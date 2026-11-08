import asyncio
import os
import tempfile
import pygame
import edge_tts
import speech_recognition as sr
from jarvis.config import Config

class VoiceEngine:
    """Голосовой движок Джарвиса: микрофон и естественная нейро-озвучка"""
    def __init__(self):
        self.voice_name = Config.JARVIS_VOICE
        self.recognizer = sr.Recognizer()
        pygame.mixer.init()

    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> str:
        """Прослушивание микрофона с калибровкой шума"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = self.recognizer.recognize_google(audio, language="ru-RU")
                return text.strip()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            return ""

    async def _async_speak(self, text: str, output_path: str):
        communicate = edge_tts.Communicate(text, self.voice_name, rate="+5%", pitch="-1Hz")
        await communicate.save(output_path)

    def speak(self, text: str):
        """Озвучивание текста голосом Джарвиса"""
        if not text:
            return

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = f.name

        try:
            asyncio.run(asyncio.wait_for(self._async_speak(text, temp_path), timeout=8.0))
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"[Голос]: {text}")
        finally:
            if os.path.exists(temp_path):
                try:
                    pygame.mixer.music.unload()
                    os.remove(temp_path)
                except Exception:
                    pass
