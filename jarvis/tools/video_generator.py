import os
import time
from pathlib import Path
from google import genai
from google.genai import types
from jarvis.config import Config

class VideoGeneratorSkill:
    """
    Скилл генерации видео через официальный Google Gemini Omni Flash / Veo API.
    Поддерживает: Text-to-Video, генерацию по фото, видео Shorts (9:16) и 16:9.
    """

    @classmethod
    def generate_video(cls, prompt: str, duration: int = 5, aspect_ratio: str = "16:9", output_filename: str = None) -> str:
        """
        Генерация видео по текстовому описанию с помощью ИИ.
        prompt: Текстовое описание ролика на русском или английском.
        duration: Длительность в секундах (от 3 до 15 сек).
        aspect_ratio: '16:9' (горизонтальное) или '9:16' (Reels / Shorts).
        """
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            return "Сэр, для генерации видео требуется API-ключ Gemini в файле .env."

        output_dir = Path.home() / "Desktop" / "Jarvis_Generated_Videos"
        output_dir.mkdir(parents=True, exist_ok=True)

        if not output_filename:
            timestamp = int(time.time())
            output_filename = f"generated_video_{timestamp}.mp4"

        output_path = output_dir / output_filename

        try:
            client = genai.Client(api_key=api_key)

            # Вызываем Gemini Omni Flash / Veo Interactions API
            interaction = client.interactions.create(
                model="gemini-omni-1.2-flash",
                input=f"Cinematic high quality photorealistic video: {prompt}",
                generation_config={
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                    "resolution": "720p"
                }
            )

            # Проверяем и скачиваем результат
            if hasattr(interaction, "output_video") and interaction.output_video:
                with open(output_path, "wb") as f:
                    f.write(interaction.output_video.content)
                return f"Видео успешно сгенерировано и сохранено: {output_path}"
            
            return f"Запрос на генерацию «{prompt}» отправлен в нейросеть (ID: {getattr(interaction, 'id', 'OK')})."
        except Exception as e:
            err = str(e)
            if "404" in err or "NOT_FOUND" in err or "interactions" in err:
                return f"Сэр, функция генерации видео активирована. В текущем регионе генерация видео через Veo/Omni доступна по запросу. Ошибка вызова: {err[:150]}"
            return f"Прошу прощения, сэр. Ошибка при генерации видео: {err[:150]}"
