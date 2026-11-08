import asyncio
import os
import tempfile
import threading
import pygame
import edge_tts
import pyttsx3
import speech_recognition as sr
from jarvis.config import Config

class VoiceEngine:
    """Двухуровневый голосовой движок: Edge-TTS + нативный Windows SAPI5 (pyttsx3)"""
    def __init__(self):
        self.voice_name = Config.JARVIS_VOICE
        self.recognizer = sr.Recognizer()
        pygame.mixer.init()
        try:
            self.sapi = pyttsx3.init()
            self.sapi.setProperty('rate', 180)
        except Exception:
            self.sapi = None

    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> str:
        """Прослушивание микрофона с калибровкой шума"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = self.recognizer.recognize_google(audio, language="ru-RU")
                return text.strip()
        except Exception:
            return ""

    async def _async_speak_edge(self, text: str, output_path: str):
        # Настройка русского дубляжа Джарвиса (Вячеслав Баранов):
        # Глубокий, спокойный мужской тон (-3Hz), чуть замедленный темп речи (-2%)
        communicate = edge_tts.Communicate(text, "ru-RU-DmitryNeural", rate="-2%", pitch="-3Hz")
        await communicate.save(output_path)

    def speak(self, text: str):
        """Озвучивание текста: приоритет строго на русский дубляж Edge-TTS"""
        if not text:
            return

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = f.name

        success = False
        try:
            # Увеличиваем таймаут, чтобы не переключаться на старый голос Windows
            asyncio.run(asyncio.wait_for(self._async_speak_edge(text, temp_path), timeout=8.0))
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 300:
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                success = True
        except Exception as e:
            print(f"[Voice Error]: {e}")
        finally:
            if os.path.exists(temp_path):
                try:
                    pygame.mixer.music.unload()
                    os.remove(temp_path)
                except Exception:
                    pass

        # Если интернет-голос совсем не сработал
        if not success:
            print(f"[Fallback Voice]: {text}")
