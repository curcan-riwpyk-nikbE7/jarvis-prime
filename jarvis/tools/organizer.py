import os
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from jarvis.sound_fx import SoundFX

class OrganizerManager:
    """
    Умный органайзер: Календарь, Заметки, Напоминания и Будильники.
    Хранит заметки и задачи в JSON, поддерживает таймеры и оповещения в отдельном потоке.
    """
    DATA_FILE = Path.home() / ".jarvis_organizer.json"
    _listeners = []
    _active_timers = []
    _monitor_thread = None
    _running = False

    @classmethod
    def _load_data(cls) -> dict:
        if not cls.DATA_FILE.exists():
            default = {"notes": [], "reminders": [], "alarms": []}
            cls._save_data(default)
            return default
        try:
            with open(cls.DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"notes": [], "reminders": [], "alarms": []}

    @classmethod
    def _save_data(cls, data: dict):
        with open(cls.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # 1. ЗАМЕТКИ
    @classmethod
    def add_note(cls, text: str, category: str = "Общее") -> dict:
        data = cls._load_data()
        note = {
            "id": int(time.time()),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "category": category,
            "text": text
        }
        data.setdefault("notes", []).append(note)
        cls._save_data(data)
        return {"status": "success", "message": f"Заметка сохранена: «{text}»", "note": note}

    @classmethod
    def list_notes(cls) -> list:
        data = cls._load_data()
        return data.get("notes", [])

    # 2. НАПОМИНАНИЯ
    @classmethod
    def add_reminder(cls, text: str, delay_minutes: float = None, exact_time_str: str = None) -> dict:
        """
        Создает напоминание либо через delay_minutes, либо в точное время HH:MM.
        """
        now = datetime.now()
        target_time = None

        if delay_minutes is not None and delay_minutes > 0:
            target_time = now + timedelta(minutes=delay_minutes)
        elif exact_time_str:
            # Парсим HH:MM
            try:
                parts = [int(p) for p in exact_time_str.strip().split(":")]
                target_time = now.replace(hour=parts[0], minute=parts[1], second=0, microsecond=0)
                if target_time <= now:
                    target_time += timedelta(days=1)
            except Exception:
                target_time = now + timedelta(minutes=10)
        else:
            target_time = now + timedelta(minutes=15)

        data = cls._load_data()
        reminder = {
            "id": int(time.time()),
            "target_time": target_time.strftime("%Y-%m-%d %H:%M:%S"),
            "target_timestamp": target_time.timestamp(),
            "text": text,
            "completed": False
        }
        data.setdefault("reminders", []).append(reminder)
        cls._save_data(data)
        cls.ensure_monitor_running()

        return {
            "status": "success",
            "message": f"Напоминание установлено на {target_time.strftime('%H:%M')}: «{text}»",
            "reminder": reminder
        }

    # 3. БУДИЛЬНИКИ
    @classmethod
    def set_alarm(cls, time_str: str, label: str = "Будильник") -> dict:
        return cls.add_reminder(text=label, exact_time_str=time_str)

    @classmethod
    def list_pending(cls) -> list:
        data = cls._load_data()
        now_ts = time.time()
        return [r for r in data.get("reminders", []) if not r.get("completed") and r.get("target_timestamp", 0) > now_ts]

    @classmethod
    def add_notification_listener(cls, callback):
        if callback not in cls._listeners:
            cls._listeners.append(callback)

    @classmethod
    def ensure_monitor_running(cls):
        if cls._running:
            return
        cls._running = True

        def monitor_loop():
            while cls._running:
                now_ts = time.time()
                data = cls._load_data()
                changed = False
                for r in data.get("reminders", []):
                    if not r.get("completed") and now_ts >= r.get("target_timestamp", 0):
                        r["completed"] = True
                        changed = True
                        msg = f"⏰ Сэр! Напоминаю: {r.get('text', '')}"
                        SoundFX.play_notification_sound()
                        for cb in cls._listeners:
                            try:
                                cb(msg)
                            except Exception:
                                pass
                if changed:
                    cls._save_data(data)
                time.sleep(3)

        cls._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        cls._monitor_thread.start()
