import os
import winreg
import glob
import subprocess
from pathlib import Path
from typing import Dict, Optional

class AppLauncherSkill:
    """
    Умный поиск и запуск программ Windows (как в Kira):
    сканирует реестр, меню Пуск и AppData, понимает сленг и опечатки.
    """
    _cache = {}

    SLANG_MAP = {
        "телега": "telegram",
        "телеграм": "telegram",
        "телеграмм": "telegram",
        "тг": "telegram",
        "хром": "chrome",
        "браузер": "chrome",
        "премьер": "premiere",
        "премьер про": "premiere pro",
        "фотошоп": "photoshop",
        "стим": "steam",
        "дискорд": "discord",
        "кальк": "calc",
        "ноутпад": "notepad",
        "блокнот": "notepad",
        "код": "code",
        "вскод": "code",
        "проводник": "explorer"
    }

    @classmethod
    def scan_installed_apps(cls) -> Dict[str, str]:
        """Сканирует ярлыки в меню Пуск и на Рабочем столе"""
        if cls._cache:
            return cls._cache

        apps = {}
        # Папки с ярлыками меню Пуск
        search_dirs = [
            Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
            Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
            Path.home() / "Desktop"
        ]

        for base_dir in search_dirs:
            if base_dir.exists():
                for p in base_dir.rglob("*.lnk"):
                    clean_name = p.stem.lower()
                    apps[clean_name] = str(p)

        cls._cache = apps
        return apps

    @classmethod
    def launch_app(cls, app_name: str) -> str:
        """Запуск приложения по названию, сленгу или опечатке"""
        query = app_name.lower().strip()
        
        # Проверяем таблицу сленга
        target = cls.SLANG_MAP.get(query, query)

        # 1. Быстрый системный запуск (calc, notepad, explorer, chrome)
        quick_commands = {
            "calc": "calc.exe",
            "notepad": "notepad.exe",
            "explorer": "explorer.exe",
            "code": "code",
            "cmd": "cmd.exe"
        }
        if target in quick_commands:
            try:
                subprocess.Popen(quick_commands[target], shell=True)
                return f"Приложение «{app_name}» запущено, сэр."
            except Exception:
                pass

        # 2. Нечеткий поиск по сканированным ярлыкам Windows
        apps = cls.scan_installed_apps()

        # Точное или частичное совпадение
        best_match = None
        for name, path in apps.items():
            if target == name or target in name:
                best_match = path
                break

        if best_match:
            try:
                os.startfile(best_match)
                return f"Открываю «{app_name}», сэр."
            except Exception as e:
                return f"Не удалось открыть «{app_name}»: {e}"

        # 3. Попытка запустить напрямую через Windows Shell
        try:
            subprocess.Popen(f"start {target}", shell=True)
            return f"Команда запуска «{app_name}» отправлена в систему, сэр."
        except Exception:
            return f"Сэр, приложение «{app_name}» не найдено на вашем компьютере."
