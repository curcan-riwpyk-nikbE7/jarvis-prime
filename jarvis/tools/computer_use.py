import time
import os
import pyautogui
import pygetwindow as gw
from typing import List, Optional

# Безопасность: перемещение мыши в угол экрана аварийно остановит скрипт
pyautogui.FAILSAFE = True

class ComputerUseTool:
    """
    Инструмент прямого управления рабочим столом Windows:
    мышь, клавиатура, управление окнами приложений.
    """

    @staticmethod
    def get_screen_size():
        w, h = pyautogui.size()
        return f"Разрешение экрана: {w}x{h}"

    @staticmethod
    def mouse_move(x: int, y: int, duration: float = 0.5):
        pyautogui.moveTo(x, y, duration=duration)
        return f"Курсор перемещен в точку ({x}, {y})"

    @staticmethod
    def mouse_click(x: Optional[int] = None, y: Optional[int] = None, clicks: int = 1, button: str = "left"):
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y, clicks=clicks, button=button)
        else:
            pyautogui.click(clicks=clicks, button=button)
        return f"Клик мыши ({button}, {clicks} раз) выполнен"

    @staticmethod
    def type_text(text: str, interval: float = 0.05):
        pyautogui.write(text, interval=interval)
        return f"Напечатан текст: {text}"

    @staticmethod
    def press_hotkey(*keys):
        """Нажатие комбинаций клавиш, например ('ctrl', 's') или ('alt', 'tab')"""
        pyautogui.hotkey(*keys)
        return f"Нажата комбинация: {' + '.join(keys)}"

    @staticmethod
    def take_screenshot(save_path: str = "screenshot.png") -> str:
        """Делает скриншот всего экрана и сохраняет его"""
        im = pyautogui.screenshot()
        abs_path = os.path.abspath(save_path)
        im.save(abs_path)
        return f"Скриншот экрана сохранен: {abs_path}"

    @staticmethod
    def list_open_windows() -> List[str]:
        """Возвращает список заголовков всех открытых окон"""
        titles = [w.title for w in gw.getAllWindows() if w.title.strip()]
        return titles

    @staticmethod
    def focus_window(title_keyword: str) -> str:
        """Находит окно по части названия и выводит его на передний план"""
        windows = gw.getWindowsWithTitle(title_keyword)
        if not windows:
            return f"Окно с названием '{title_keyword}' не найдено."
        win = windows[0]
        if win.isMinimized:
            win.restore()
        win.activate()
        return f"Окно '{win.title}' активировано на переднем плане."
