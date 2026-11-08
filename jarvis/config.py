import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    JARVIS_VOICE = os.getenv("JARVIS_VOICE", "ru-RU-DmitryNeural")
    DEFAULT_INPUT_MODE = os.getenv("DEFAULT_INPUT_MODE", "voice")
