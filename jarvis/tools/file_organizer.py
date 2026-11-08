import os
import shutil
from pathlib import Path
from typing import List

class FileOrganizerSkill:
    """Скилл автоматической сортировки и уборки рабочего стола и папки загрузок"""

    @staticmethod
    def organize_desktop() -> str:
        """Сортирует файлы на рабочем столе по папкам: Картинки, Видео, Документы, Архивы"""
        desktop = Path.home() / "Desktop"
        if not desktop.exists():
            return "Рабочий стол не найден."

        categories = {
            "Изображения": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"],
            "Видео": [".mp4", ".mov", ".avi", ".mkv", ".wmv"],
            "Документы": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".doc"],
            "Архивы": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Установщики": [".exe", ".msi"]
        }

        moved_count = 0
        for item in desktop.iterdir():
            if item.is_file() and not item.name.startswith("."):
                ext = item.suffix.lower()
                for cat_name, extensions in categories.items():
                    if ext in extensions:
                        target_dir = desktop / cat_name
                        target_dir.mkdir(exist_ok=True)
                        try:
                            shutil.move(str(item), str(target_dir / item.name))
                            moved_count += 1
                        except Exception:
                            pass
                        break

        return f"Порядок наведен, сэр. Перемещено файлов: {moved_count}."
