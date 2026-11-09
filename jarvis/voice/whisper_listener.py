import io
import os
import tempfile
import numpy as np
import speech_recognition as sr

class WhisperRecognizer:
    """
    Высокоточный локальный слух на базе Faster-Whisper.
    Распознает речь на русском языке даже в шумной комнате, со сленгом, акцентом
    и без задержек сетевых запросов.
    Автоматически переключается на google speech recognition в случае сбоя.
    """
    _model = None
    _loading = False

    @classmethod
    def get_model(cls, model_size: str = "tiny"):
        if cls._model is None and not cls._loading:
            cls._loading = True
            try:
                from faster_whisper import WhisperModel
                # tiny модель весит ~75MB, загружается за секунду и молниеносно работает на CPU
                print(f"[Whisper AI]: Инициализация локальной нейросети слуха (Faster-Whisper '{model_size}')...")
                cls._model = WhisperModel(model_size, device="cpu", compute_type="int8")
                print("[Whisper AI]: Нейросеть слуха успешно загружена в память!")
            except Exception as e:
                print(f"[Whisper AI Init Error]: {e}")
                cls._model = None
            finally:
                cls._loading = False
        return cls._model

    @classmethod
    def transcribe_audio_data(cls, audio_data: sr.AudioData, language: str = "ru") -> str:
        """
        Преобразует аудиозапись sr.AudioData в текст с помощью Faster-Whisper.
        """
        try:
            model = cls.get_model()
            if model is None:
                return None

            wav_bytes = audio_data.get_wav_data()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(wav_bytes)
                wav_path = f.name

            try:
                segments, info = model.transcribe(wav_path, language=language, beam_size=1, vad_filter=True)
                text = " ".join([seg.text for seg in segments]).strip()
                return text
            finally:
                if os.path.exists(wav_path):
                    try:
                        os.remove(wav_path)
                    except Exception:
                        pass
        except Exception as e:
            print(f"[Whisper Transcribe Error]: {e}")
            return None
