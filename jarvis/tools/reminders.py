import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict

class ReminderSkill:
    """Скилл умных таймеров и голосовых напоминаний"""
    active_reminders = []

    @classmethod
    def set_timer(cls, seconds: int, message: str, voice_callback=None) -> str:
        """Ставит таймер на N секунд с голосовым оповещением"""
        def timer_thread():
            time.sleep(seconds)
            reminder_text = f"Внимание, сэр! Напоминаю: {message}"
            if voice_callback:
                voice_callback(reminder_text)

        threading.Thread(target=timer_thread, daemon=True).start()
        minutes = seconds // 60
        sec_rem = seconds % 60
        time_str = f"{minutes} мин {sec_rem} сек" if minutes > 0 else f"{sec_rem} сек"
        return f"Таймер установлен на {time_str}: «{message}», сэр."
