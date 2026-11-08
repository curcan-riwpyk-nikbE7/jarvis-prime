import os
import io
import pyautogui
from PIL import Image
from google import genai
from google.genai import types
from jarvis.config import Config

class VisionTool:
    """Модуль зрения Джарвиса: анализ экрана через мультимодальную Gemini"""

    @staticmethod
    def analyze_screen(prompt: str = "Что сейчас происходит на экране? Опиши интерфейс, ошибки или открытые программы.") -> str:
        try:
            screenshot = pyautogui.screenshot()
            
            # Сжимаем скриншот для быстрой отправки
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='JPEG', quality=80)
            img_bytes = img_byte_arr.getvalue()

            client = genai.Client(api_key=Config.GEMINI_API_KEY)
            
            response = client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                    prompt
                ]
            )
            return response.text.strip() if response.text else "Изображение проанализировано, деталей не обнаружено."
        except Exception as e:
            return f"Ошибка анализа экрана: {str(e)}"
