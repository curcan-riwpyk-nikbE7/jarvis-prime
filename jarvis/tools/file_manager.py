import os
import glob
from pathlib import Path
from typing import List

class FileManagerTool:
    """Инструмент для поиска и управления файлами на диске"""

    @staticmethod
    def find_files(directory: str, pattern: str = "*.*", recursive: bool = True) -> List[str]:
        """Поиск файлов по шаблону (например '*.mp4', '*.mov')"""
        if not os.path.exists(directory):
            return [f"Директория {directory} не найдена."]
        
        search_path = os.path.join(directory, "**" if recursive else "", pattern)
        files = glob.glob(search_path, recursive=recursive)
        return files[:50]  # Ограничение до первых 50 файлов

    @staticmethod
    def get_downloads_folder() -> str:
        return str(Path.home() / "Downloads")

    @staticmethod
    def get_desktop_folder() -> str:
        return str(Path.home() / "Desktop")
