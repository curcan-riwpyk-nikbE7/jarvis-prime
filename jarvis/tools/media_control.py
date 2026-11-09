import webbrowser
import pyautogui

class MediaControlSkill:
    """Скилл управления медиаплеером, музыкой и громкостью Windows"""

    @staticmethod
    def play_pause():
        """Переключает воспроизведение и паузу медиа (музыки, видео, браузера)"""
        pyautogui.press("playpause")
        return "Воспроизведение/Пауза переключено, сэр."

    @staticmethod
    def next_track():
        """Переключает на следующий музыкальный трек в любом запущенном плеере или браузере"""
        pyautogui.press("nexttrack")
        return "Включен следующий трек, сэр."

    @staticmethod
    def prev_track():
        """Переключает на предыдущий трек"""
        pyautogui.press("prevtrack")
        return "Включен предыдущий трек, сэр."

    @staticmethod
    def volume_up(steps: int = 5):
        """Увеличивает системную громкость Windows на указанное число шагов (по умолчанию 5)"""
        for _ in range(steps):
            pyautogui.press("volumeup")
        return f"Громкость увеличена (+{steps * 2}%), сэр."

    @staticmethod
    def volume_down(steps: int = 5):
        """Уменьшает системную громкость Windows на указанное число шагов (по умолчанию 5)"""
        for _ in range(steps):
            pyautogui.press("volumedown")
        return f"Громкость уменьшена (-{steps * 2}%), сэр."

    @staticmethod
    def volume_mute():
        """Полностью выключает или включает звук Windows (Mute)"""
        pyautogui.press("volumemute")
        return "Режим звука переключен (Mute), сэр."

    @staticmethod
    def stop_media():
        """Останавливает воспроизведение медиа"""
        pyautogui.press("stop")
        return "Воспроизведение остановлено, сэр."

    @staticmethod
    def play_youtube_music(query: str):
        url = f"https://music.youtube.com/search?q={query}"
        webbrowser.open(url)
        return f"Ищу «{query}» в YouTube Music, сэр."
