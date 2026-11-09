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
    def minimize_window(title_keyword: Optional[str] = None) -> str:
        """Сворачивает окно приложения по названию или активное окно, если не указано"""
        try:
            if title_keyword:
                windows = gw.getWindowsWithTitle(title_keyword)
                if not windows:
                    return f"Окно с названием '{title_keyword}' не найдено, сэр."
                win = windows[0]
                win.minimize()
                return f"Окно «{win.title}» свернуто, сэр."
            else:
                active = gw.getActiveWindow()
                if active:
                    active.minimize()
                    return f"Окно «{active.title}» свернуто, сэр."
                pyautogui.hotkey('win', 'down')
                return "Активное окно свернуто, сэр."
        except Exception as e:
            return f"Не удалось свернуть окно: {e}"

    @staticmethod
    def minimize_all_windows() -> str:
        """Сворачивает все открытые окна (показывает рабочий стол Win+D)"""
        pyautogui.hotkey('win', 'd')
        return "Все окна свернуты, рабочий стол открыт, сэр."

    @staticmethod
    def restore_all_windows() -> str:
        """Восстанавливает свернутые окна (повторный Win+D)"""
        pyautogui.hotkey('win', 'd')
        return "Окна восстановлены, сэр."

    @staticmethod
    def maximize_window(title_keyword: Optional[str] = None) -> str:
        """Разворачивает окно на весь экран"""
        try:
            if title_keyword:
                windows = gw.getWindowsWithTitle(title_keyword)
                if not windows:
                    return f"Окно с названием '{title_keyword}' не найдено, сэр."
                win = windows[0]
                win.maximize()
                win.activate()
                return f"Окно «{win.title}» развернуто на весь экран, сэр."
            else:
                active = gw.getActiveWindow()
                if active:
                    active.maximize()
                    return f"Окно «{active.title}» развернуто на весь экран, сэр."
                pyautogui.hotkey('win', 'up')
                return "Окно развернуто, сэр."
        except Exception as e:
            return f"Не удалось развернуть окно: {e}"

    @staticmethod
    def close_window(title_keyword: Optional[str] = None) -> str:
        """Закрывает окно приложения по названию или активное окно (Alt+F4)"""
        try:
            if title_keyword:
                windows = gw.getWindowsWithTitle(title_keyword)
                if not windows:
                    return f"Окно '{title_keyword}' не найдено, сэр."
                win = windows[0]
                win.close()
                return f"Окно «{win.title}» закрыто, сэр."
            else:
                pyautogui.hotkey('alt', 'f4')
                return "Окно закрыто, сэр."
        except Exception as e:
            return f"Не удалось закрыть окно: {e}"

    @staticmethod
    def switch_window() -> str:
        """Переключается на следующее приложение (Alt+Tab)"""
        pyautogui.hotkey('alt', 'tab')
        return "Переключился на следующее окно, сэр."

    @staticmethod
    def focus_window(title_keyword: str) -> str:
        """Находит окно по части названия и выводит его на передний план"""
        windows = gw.getWindowsWithTitle(title_keyword)
        if not windows:
            return f"Окно с названием '{title_keyword}' не найдено, сэр."
        win = windows[0]
        if win.isMinimized:
            win.restore()
        win.activate()
        return f"Окно '{win.title}' активировано на переднем плане, сэр."
