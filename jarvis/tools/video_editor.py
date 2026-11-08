import os
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional

class VideoEditorTool:
    """
    Инструмент профессионального видеомонтажа через системный FFmpeg.
    Поддерживает: нарезку, объединение, извлечение аудио, конвертацию разрешения,
    наложение фоновой музыки.
    """

    @staticmethod
    def is_ffmpeg_installed() -> bool:
        return shutil.which("ffmpeg") is not None

    @classmethod
    def trim_video(cls, input_path: str, output_path: str, start_time: str, duration: Optional[str] = None) -> str:
        """
        Обрезает видео.
        start_time: '00:00:10' (часы:минуты:секунды) или секунды ('10')
        duration: длительность фрагмента в секундах
        """
        if not os.path.exists(input_path):
            return f"Ошибка: файл {input_path} не найден."

        cmd = ["ffmpeg", "-y", "-ss", str(start_time), "-i", input_path]
        if duration:
            cmd.extend(["-t", str(duration)])
        cmd.extend(["-c", "copy", output_path])

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f"Видео успешно обрезано и сохранено: {output_path}"
        except subprocess.CalledProcessError as e:
            return f"Ошибка FFmpeg при нарезке: {e.stderr.decode('utf-8', errors='ignore')}"

    @classmethod
    def concatenate_videos(cls, video_paths: List[str], output_path: str) -> str:
        """Склеивает список видеофайлов в один финальный ролик"""
        if not video_paths:
            return "Ошибка: не переданы видеофайлы для склейки."

        for p in video_paths:
            if not os.path.exists(p):
                return f"Ошибка: файл {p} не найден."

        list_file = Path("temp_concat_list.txt")
        try:
            with open(list_file, "w", encoding="utf-8") as f:
                for path in video_paths:
                    abs_path = os.path.abspath(path).replace("\\", "/")
                    f.write(f"file '{abs_path}'\n")

            cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(list_file), "-c", "copy", output_path
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f"Видео успешно объединены в файл: {output_path}"
        except subprocess.CalledProcessError as e:
            return f"Ошибка склейки видео: {e.stderr.decode('utf-8', errors='ignore')}"
        finally:
            if list_file.exists():
                list_file.unlink()

    @classmethod
    def add_background_music(cls, video_path: str, music_path: str, output_path: str, music_volume: float = 0.2) -> str:
        """
        Накладывает фоновую музыку на видео с уменьшенной громкостью,
        сохраняя оригинальную речь.
        """
        if not os.path.exists(video_path) or not os.path.exists(music_path):
            return "Ошибка: видеофайл или музыкальный файл не найдены."

        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", music_path,
            "-filter_complex",
            f"[1:a]volume={music_volume}[music];[0:a][music]amix=inputs=2:duration=first[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            output_path
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f"Музыка успешно наложена: {output_path}"
        except subprocess.CalledProcessError as e:
            return f"Ошибка наложения музыки: {e.stderr.decode('utf-8', errors='ignore')}"

    @classmethod
    def convert_to_shorts_9_16(cls, input_path: str, output_path: str) -> str:
        """Конвертирует стандартное горизонтальное видео 16:9 в вертикальный формат 9:16 (Shorts/Reels)"""
        if not os.path.exists(input_path):
            return f"Ошибка: файл {input_path} не найден."

        # Размытый фон + центральное видео для вертикального формата
        filter_str = (
            "[0:v]scale=ih*16/9:-1,boxblur=luma_radius=min(h\\,w)/20:luma_power=1:chroma_radius=min(h\\,w)/20:chroma_power=1[bg];"
            "[0:v]scale=-1:1080[ov];"
            "[bg]crop=1080:1920[bg_cropped];"
            "[bg_cropped][ov]overlay=(W-w)/2:(H-h)/2"
        )
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", filter_str,
            "-c:a", "copy",
            output_path
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f"Видео успешно переведено в формат Shorts (9:16): {output_path}"
        except subprocess.CalledProcessError as e:
            return f"Ошибка конвертации в Shorts: {e.stderr.decode('utf-8', errors='ignore')}"
