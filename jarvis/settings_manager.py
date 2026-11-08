import os
import json
from pathlib import Path
from typing import Dict, Any

SETTINGS_FILE = Path.home() / ".jarvis_prime" / "settings.json"

DEFAULT_SETTINGS = {
    "gemini_api_key": "",
    "model": "gemini-3.5-flash",
    "voice": "ru-RU-DmitryNeural",
    "speech_rate": "+5%",
    "wake_word_enabled": True,
    "hotkey": "alt+j",
    "volume": 100,
    "active_skills": {
        "video_editor": True,
        "computer_use": True,
        "vision": True,
        "media_control": True,
        "web_search": True,
        "reminders": True,
        "file_organizer": True
    }
}

class SettingsManager:
    """Управление настройками Джарвиса с сохранением в JSON"""
    @classmethod
    def load(cls) -> Dict[str, Any]:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not SETTINGS_FILE.exists():
            cls.save(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged = DEFAULT_SETTINGS.copy()
                merged.update(data)
                return merged
        except Exception:
            return DEFAULT_SETTINGS.copy()

    @classmethod
    def save(cls, settings: Dict[str, Any]):
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)

    @classmethod
    def update(cls, key: str, value: Any):
        current = cls.load()
        current[key] = value
        cls.save(current)
        return current
