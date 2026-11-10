import threading
import time
import pyaudio
import numpy as np
import speech_recognition as sr
from jarvis.voice.whisper_listener import WhisperRecognizer

class ContinuousVoiceListener:
    """
    Высокоточный непрерывный VAD-детектор речи для микрофона Fifine:
    1. Автоматически находит устройство 'fifine Microphone' среди аудиовходов Windows.
    2. Выполняет динамическую автокалибровку шума комнаты (running ambient baseline).
    3. При превышении порога энергии накапливает аудиопоток.
    4. При паузе (silence) передает буфер в отдельный рабочий поток (worker pool) для Whisper,
       чтобы главный цикл захвата звука НИКОГДА не замирал и не терял ни одного сэмпла.
    5. Поддерживает все вариации слова активации и мгновенно вызывает callback.
    """

    def __init__(self, on_wake_word_callback, fixed_device_index=None):
        self.callback = on_wake_word_callback
        self.fixed_device_index = fixed_device_index
        self.is_running = False
        self.thread = None
        self.ambient_energy = 250.0  # стартовый уровень шума

    def _find_microphone_index(self, p: pyaudio.PyAudio) -> int:
        if self.fixed_device_index is not None:
            return self.fixed_device_index
        count = p.get_device_count()
        # Приоритет 1: Ищем по имени Fifine
        for i in range(count):
            try:
                info = p.get_device_info_by_index(i)
                name = info.get("name", "").lower()
                if "fifine" in name and info.get("maxInputChannels", 0) > 0:
                    print(f"[Voice VAD]: Выбран целевой микрофон [{i}]: {info.get('name')}")
                    return i
            except Exception:
                pass
        # Fallback: Устройство по умолчанию
        try:
            default_dev = p.get_default_input_device_info()
            return default_dev.get("index", 0)
        except Exception:
            return 0

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
        dev_idx = self._find_microphone_index(p)

        # Открываем поток 16 кГц, 16 бит моно
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=dev_idx,
                frames_per_buffer=1024
            )
        except Exception as e:
            print(f"[Voice VAD Warning]: Не удалось открыть с индексом {dev_idx}: {e}, пробуем без индекса...")
            try:
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1024
                )
            except Exception as e2:
                print(f"[Voice VAD Fatal]: Ошибка открытия микрофона: {e2}")
                p.terminate()
                return

        print("[Voice VAD]: Микрофон готов. Выполняю калибровку фонового шума...")

        # Калибровка первых 15 кадров (~1 сек)
        calib_vals = []
        for _ in range(15):
            try:
                data = stream.read(1024, exception_on_overflow=False)
                arr = np.frombuffer(data, dtype=np.int16)
                calib_vals.append(float(np.abs(arr).mean()))
            except Exception:
                pass

        if calib_vals:
            self.ambient_energy = max(100.0, float(np.mean(calib_vals)))
        print(f"[Voice VAD]: Базовый уровень шума откалиброван: {self.ambient_energy:.1f}. Ожидание «Джарвис»...")

        buffer_frames = []
        is_speaking = False
        silence_count = 0

        while self.is_running:
            try:
                data = stream.read(1024, exception_on_overflow=False)
                samples = np.frombuffer(data, dtype=np.int16)
                energy = float(np.abs(samples).mean())

                # Динамический порог активации: 1.4x от шума фона + запас 120 единиц
                threshold = max(280.0, self.ambient_energy * 1.35 + 100.0)

                if energy > threshold:
                    is_speaking = True
                    silence_count = 0
                    buffer_frames.append(data)
                elif is_speaking:
                    buffer_frames.append(data)
                    silence_count += 1

                    # Если тишина длится более 9 кадров (~0.58 сек) — фраза завершена
                    if silence_count > 9:
                        if len(buffer_frames) >= 10:  # Длительность не менее 0.6 сек
                            raw_audio = b"".join(buffer_frames)
                            # Запускаем распознавание в отдельном потоке, НЕ блокируя аудиопоток!
                            threading.Thread(target=self._process_utterance, args=(raw_audio,), daemon=True).start()

                        buffer_frames = []
                        is_speaking = False
                        silence_count = 0
                else:
                    # Медленно подстраиваем базовый уровень шума фона (moving average)
                    self.ambient_energy = self.ambient_energy * 0.98 + energy * 0.02
                    # Оставляем легкий срез пре-буфера (1 кадр) на случай резкого старта фразы
                    if len(buffer_frames) > 2:
                        buffer_frames.pop(0)
                    buffer_frames.append(data)

            except Exception:
                time.sleep(0.01)

        try:
            stream.stop_stream()
            stream.close()
        except Exception:
            pass
        p.terminate()

    def _process_utterance(self, raw_audio: bytes):
        try:
            audio_data = sr.AudioData(raw_audio, 16000, 2)
            # Распознаем через локальный Faster-Whisper
            text = WhisperRecognizer.transcribe_audio_data(audio_data, language="ru")
            if text:
                clean = text.lower().strip()
                print(f"[VAD Heard]: «{clean}»")

                # Расширенный словарь вариантов триггера и созвучных слов
                wake_variants = [
                    "джарвис", "jarvis", "жарвис", "дарвис", "чарвис", "джервис",
                    "старк", "stark", "джар", "джарви", "джовис", "ярвис"
                ]

                # Проверяем наличие ключевого слова в распознанной фразе
                matched = any(w in clean for w in wake_variants)

                if matched:
                    print(f"[VAD TRIGGERED]: Активация по слову Джарвис! Текст: {clean}")
                    self.callback(clean)
        except Exception as e:
            print(f"[VAD Process Error]: {e}")
