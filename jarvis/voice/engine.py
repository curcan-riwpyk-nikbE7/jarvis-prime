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
        communicate = edge_tts.Communicate(text, self.voice_name, rate="+5%", pitch="-1Hz")
        await communicate.save(output_path)

    def speak(self, text: str):
        """Озвучивание текста: сначала через чистый нейро-голос Edge-TTS, при сбое — через нативный движок Windows"""
        if not text:
            return

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = f.name

        success = False
        try:
            asyncio.run(asyncio.wait_for(self._async_speak_edge(text, temp_path), timeout=4.0))
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 500:
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                success = True
        except Exception as e:
            pass
        finally:
            if os.path.exists(temp_path):
                try:
                    pygame.mixer.music.unload()
                    os.remove(temp_path)
                except Exception:
                    pass

        # Если интернет-голос не проигрался, мгновенно говорим через нативный Windows голос
        if not success and self.sapi:
            try:
                self.sapi.say(text)
                self.sapi.runAndWait()
            except Exception:
                pass
