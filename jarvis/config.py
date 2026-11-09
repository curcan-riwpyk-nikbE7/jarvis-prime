import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def get_base_dir() -> str:
    """Возвращает базовую директорию проекта, корректно работая как в скриптах, так и в скомпилированном exe."""
    if getattr(sys, 'frozen', False):
        # Если запущено из PyInstaller exe
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass and os.path.exists(os.path.join(meipass, 'jarvis', 'ui')):
            return meipass
        exe_dir = os.path.dirname(sys.executable)
        if os.path.exists(os.path.join(exe_dir, '_internal', 'jarvis', 'ui')):
            return os.path.join(exe_dir, '_internal')
        if os.path.exists(os.path.join(exe_dir, 'jarvis', 'ui')):
            return exe_dir
        return exe_dir
    # Если запущен обычный python скрипт
    return str(Path(__file__).resolve().parent.parent)

def get_ui_path(filename: str = "nexus.html") -> str:
    """Находит абсолютный путь к UI-файлу в любых условиях развертывания."""
    base = get_base_dir()
    candidates = [
        os.path.join(base, "jarvis", "ui", filename),
        os.path.join(base, "_internal", "jarvis", "ui", filename),
        os.path.join(base, "ui", filename),
        os.path.join(os.path.dirname(__file__), "ui", filename),
    ]
    for p in candidates:
        if os.path.exists(p):
            return os.path.abspath(p)
    return os.path.abspath(candidates[0])

load_dotenv()

class Config:
    PROJECT_ROOT = get_base_dir()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    JARVIS_VOICE = os.getenv("JARVIS_VOICE", "ru-RU-DmitryNeural")
    DEFAULT_INPUT_MODE = os.getenv("DEFAULT_INPUT_MODE", "voice")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID", "")

