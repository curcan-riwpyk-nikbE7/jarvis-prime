import webbrowser
import pyautogui

class MediaControlSkill:
    """Скилл управления медиаплеером, музыкой и громкостью Windows"""

    @staticmethod
    def play_pause():
        pyautogui.press("playpause")
        return "Воспроизведение/Пауза переключено, сэр."

    @staticmethod
    def next_track():
        pyautogui.press("nexttrack")
        return "Следующий трек, сэр."

    @staticmethod
    def prev_track():
        pyautogui.press("prevtrack")
        return "Предыдущий трек, сэр."

    @staticmethod
    def volume_up(steps: int = 5):
        for _ in range(steps):
            pyautogui.press("volumeup")
        return "Громкость увеличена, сэр."

    @staticmethod
    def volume_down(steps: int = 5):
        for _ in range(steps):
            pyautogui.press("volumedown")
        return "Громкость уменьшена, сэр."

    @staticmethod
    def volume_mute():
        pyautogui.press("volumemute")
        return "Звук отключен, сэр."

    @staticmethod
    def play_youtube_music(query: str):
        url = f"https://music.youtube.com/search?q={query}"
        webbrowser.open(url)
        return f"Ищу «{query}» в YouTube Music, сэр."
