import os
import re
import threading
from pathlib import Path
import yt_dlp

class MediaDownloader:
    """
    Модуль загрузки медиа (YouTube, Rutube, VK, TikTok, Vimeo и др.)
    с авто-сохранением на Рабочий стол или в папку Downloads пользователя.
    """
    DEFAULT_DOWNLOAD_DIR = str(Path.home() / "Downloads")

    @classmethod
    def get_output_path(cls, custom_dir: str = None) -> str:
        target = custom_dir or cls.DEFAULT_DOWNLOAD_DIR
        os.makedirs(target, exist_ok=True)
        return target

    @classmethod
    def download(cls, url: str, extract_audio_only: bool = False, custom_dir: str = None) -> dict:
        """
        Синхронно или в отдельном потоке загружает ролик или извлекает MP3.
        """
        output_dir = cls.get_output_path(custom_dir)
        outtmpl = os.path.join(output_dir, "%(title)s.%(ext)s")

        ydl_opts = {
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }

        if extract_audio_only:
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            })
        else:
            ydl_opts.update({
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "Медиафайл")
                ext = "mp3" if extract_audio_only else info.get("ext", "mp4")
                filename = f"{title}.{ext}"
                filepath = os.path.join(output_dir, filename)
                
                return {
                    "status": "success",
                    "title": title,
                    "filepath": filepath,
                    "duration": info.get("duration", 0),
                    "channel": info.get("uploader", "Неизвестен"),
                    "message": f"Файл «{title}» успешно загружен в {output_dir}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка загрузки медиа: {str(e)}"
            }

    @classmethod
    def download_async(cls, url: str, extract_audio_only: bool = False, on_complete=None):
        def worker():
            res = cls.download(url, extract_audio_only)
            if on_complete:
                on_complete(res)
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
