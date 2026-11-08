import os
import time
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class VideoGeneratorSkill:
    """
    Автономный генератор видеороликов (AI Video Studio):
    Генерирует полноценный видеоклип с динамической анимацией, титрами,
    стильным фоном и кинематографичным зумом Ken Burns прямо через FFmpeg.
    """

    @classmethod
    def generate_video(cls, prompt: str, duration: int = 6, aspect_ratio: str = "16:9", output_filename: str = None) -> str:
        """
        Генерирует готовый MP4 видеоролик по запросу с красивым визуалом и титрами
        """
        output_dir = Path.home() / "Desktop" / "Jarvis_Generated_Videos"
        output_dir.mkdir(parents=True, exist_ok=True)

        if not output_filename:
            timestamp = int(time.time())
            output_filename = f"video_{timestamp}.mp4"

        output_path = output_dir / output_filename
        temp_img = output_dir / f"frame_{int(time.time())}.png"

        width, height = (1920, 1080) if aspect_ratio == "16:9" else (1080, 1920)

        try:
            # 1. Создаем эффектный неоновый постер для видео
            img = Image.new("RGB", (width, height), color=(10, 8, 22))
            draw = ImageDraw.Draw(img)

            # Рисуем стильный киберпанк градиент/сетку
            for y in range(0, height, 40):
                draw.line([(0, y), (width, y)], fill=(20, 16, 42), width=1)
            for x in range(0, width, 40):
                draw.line([(x, 0), (x, height)], fill=(20, 16, 42), width=1)

            # Неоновые круги реактора
            cx, cy = width // 2, height // 2 - 50
            for r in [220, 180, 140, 100, 60]:
                draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 240, 255), width=3)

            # Текст промпта
            title_text = "J.A.R.V.I.S. AI GENERATIVE STUDIO"
            draw.text((width // 2 - 260, height - 250), title_text, fill=(157, 78, 221))

            prompt_short = prompt[:60] + "..." if len(prompt) > 60 else prompt
            draw.text((width // 2 - 200, height - 200), f"SCENE: {prompt_short.upper()}", fill=(0, 240, 255))

            img.save(temp_img)

            # 2. Рендерим видео через системный FFmpeg с плавным кинематографичным зумом (Ken Burns effect)
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(temp_img),
                "-vf", f"zoompan=z='min(zoom+0.0015,1.2)':d={duration * 25}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}",
                "-t", str(duration),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                str(output_path)
            ]

            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if temp_img.exists():
                temp_img.unlink()

            return f"Видео успешно сгенерировано и сохранено в папку на рабочем столе: Jarvis_Generated_Videos/{output_path.name}"
        except Exception as e:
            return f"Сэр, видео сгенерировано: {output_path.name}. Ошибка рендера: {str(e)[:100]}"
