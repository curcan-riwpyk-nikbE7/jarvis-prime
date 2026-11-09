import threading
import time
import pyaudio
import numpy as np
import speech_recognition as sr
from jarvis.voice.whisper_listener import WhisperRecognizer

class ContinuousVoiceListener:
    """
    Непрерывный высокоскоростной детектор речи (Continuous VAD Listener).
    - Читает микрофон в непрерывном потоке PyAudio без блокировок SpeechRecognition.
    - Мгновенно улавливает начало речи по всплеску энергии микрофона (VAD).
    - Накапливает аудио-фрагмент (~2-3 сек) и передает в локальный Faster-Whisper.
    - При обнаружении слова «джарвис» / «jarvis» мгновенно вызывает callback.
    """

    def __init__(self, on_wake_word_callback, energy_threshold=180):
        self.callback = on_wake_word_callback
        self.energy_threshold = energy_threshold
        self.is_running = False
        self.thread = None

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        print("[Voice VAD]: Непрерывный слушатель микрофона активирован!")

    def stop(self):
        self.is_running = False

    def _listen_loop(self):
        p = pyaudio.PyAudio()
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024
            )
        except Exception as e:
            print(f"[Voice VAD Error]: Не удалось открыть аудиопоток: {e}")
            p.terminate()
            return

        print("[Voice VAD]: Микрофон готов. Ожидание вызова «Джарвис»...")

        buffer_frames = []
        is_speaking = False
        silence_count = 0

        while self.is_running:
            try:
                data = stream.read(1024, exception_on_overflow=False)
                samples = np.frombuffer(data, dtype=np.int16)
                energy = int(np.abs(samples).mean())

                if energy > self.energy_threshold:
                    is_speaking = True
                    silence_count = 0
                    buffer_frames.append(data)
                elif is_speaking:
                    buffer_frames.append(data)
                    silence_count += 1

                    # Если после речи 0.6 сек тишины — фраза закончена, анализируем
                    if silence_count > 10:
                        if len(buffer_frames) > 12:  # не менее 0.7 сек
                            raw_audio = b"".join(buffer_frames)
                            self._process_utterance(raw_audio)
                        buffer_frames = []
                        is_speaking = False
                        silence_count = 0
            except Exception as e:
                time.sleep(0.05)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def _process_utterance(self, raw_audio: bytes):
        try:
            audio_data = sr.AudioData(raw_audio, 16000, 2)
            # Распознаем через локальный Faster-Whisper
            text = WhisperRecognizer.transcribe_audio_data(audio_data, language="ru")
            if text:
                clean = text.lower().strip()
                print(f"[VAD Heard]: «{clean}»")
                wake_variants = ["джарвис", "jarvis", "жарвис", "дарвис", "чарвис", "старк"]
                if any(w in clean for w in wake_variants):
                    print(f"[VAD TRIGGERED]: Активация по слову Джарвис! Текст: {clean}")
                    self.callback(clean)
        except Exception as e:
            print(f"[VAD Process Error]: {e}")
