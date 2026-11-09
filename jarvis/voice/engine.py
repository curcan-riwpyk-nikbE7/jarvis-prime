import asyncio
import os
import tempfile
import threading
import pygame
import edge_tts
import pyttsx3
import speech_recognition as sr
from jarvis.config import Config
from jarvis.voice.whisper_listener import WhisperRecognizer

class VoiceEngine:
    """Двухуровневый голосовой движок: Edge-TTS + нативный Windows SAPI5 (pyttsx3)"""
    def __init__(self):
        self.voice_name = Config.JARVIS_VOICE
        self.rate = "-2%"
        self.pitch = "-3Hz"
        self.recognizer = sr.Recognizer()
        pygame.mixer.init()
        try:
            self.sapi = pyttsx3.init()
            self.sapi.setProperty('rate', 180)
        except Exception:
            self.sapi = None

    def update_voice_params(self, voice_name=None, rate=None, pitch=None):
        if voice_name:
            self.voice_name = voice_name
        if rate is not None:
            self.rate = rate
        if pitch is not None:
            self.pitch = pitch

    def listen(self, timeout: int = 5, phrase_time_limit: int = 10, use_whisper: bool = True) -> str:
        """Прослушивание микрофона с локальным Whisper AI или Google fallback"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
                # Приоритет 1: Сверхточный локальный слух Whisper AI
                if use_whisper:
                    whisper_text = WhisperRecognizer.transcribe_audio_data(audio, language="ru")
                    if whisper_text:
                        return whisper_text

                # Fallback: Google Speech Recognition
                text = self.recognizer.recognize_google(audio, language="ru-RU")
                return text.strip()
        except Exception:
            return ""

    def _clean_text_for_speech(self, text: str) -> str:
        """Очищает текст от markdown, кавычек, ссылок и спецсимволов для гарантированного синтеза речи"""
        import re
        t = re.sub(r'<[^>]+>', ' ', text)
        t = re.sub(r'[`*#_«»\"]', ' ', t)
        t = re.sub(r'[(){}\[\]]', ' ', t)
        t = re.sub(r'(\d+):(\d+)', r'\1 на \2', t)
        t = t.replace('/', ' ').replace('\\', ' ').replace('_', ' ')
        t = re.sub(r'\s+', ' ', t).strip()
        return t

    async def _async_speak_edge(self, text: str, output_path: str, voice_override: str = None):
        v = voice_override or self.voice_name
        # Для максимальной стабильности на стороне серверов Microsoft не передаем крайние pitch/rate
        communicate = edge_tts.Communicate(text, v)
        await communicate.save(output_path)

    def speak(self, text: str):
        """Озвучивание текста: приоритет на нейронный русский голос Edge-TTS (без робота Windows)"""
        if not text:
            return

        clean_text = self._clean_text_for_speech(text)
        if not clean_text:
            return

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = f.name

        success = False
        # Кандидаты нейросетевых голосов строго на чистом русском языке:
        # 1. Русский мужской дубляж Баранова (Dmitry)
        # 2. Русский женский дубляж F.R.I.D.A.Y. (Svetlana)
        voice_candidates = [
            "ru-RU-DmitryNeural",
            "ru-RU-SvetlanaNeural"
        ]

        for voice_candidate in voice_candidates:
            try:
                asyncio.run(asyncio.wait_for(self._async_speak_edge(clean_text, temp_path, voice_candidate), timeout=5.0))
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 300:
                    pygame.mixer.music.load(temp_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    success = True
                    break
            except Exception:
                pass

        # 2. Если Edge-TTS не ответил из-за сети — используем естественный Google Neural TTS (gTTS), а НЕ старого робота Windows!
        if not success:
            try:
                from gtts import gTTS
                tts = gTTS(clean_text, lang='ru')
                tts.save(temp_path)
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 300:
                    pygame.mixer.music.load(temp_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    success = True
            except Exception as e:
                print(f"[gTTS Fallback Error]: {e}")

        # Удаляем временный файл
        if os.path.exists(temp_path):
            try:
                pygame.mixer.music.unload()
                os.remove(temp_path)
            except Exception:
                pass
