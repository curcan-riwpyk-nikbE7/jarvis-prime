import os
import threading
from PIL import Image
import pystray
from jarvis.sound_fx import SoundFX

class TrayManager:
    """
    Менеджер системного трея (возле часов Windows) как в Luxify Assistant:
    - Сворачивает Джарвиса в фоновый режим.
    - Оставляет активным Wake Word («Джарвис») и горячую клавишу (Alt+J).
    - Разворачивает окно в один клик.
    - Имеет удобное контекстное меню.
    """

    _instance = None

    def __init__(self, window, trigger_listen_callback):
        self.window = window
        self.trigger_listen_callback = trigger_listen_callback
        self.icon = None
        self._thread = None

    @classmethod
    def setup_tray(cls, window, trigger_listen_callback, icon_path: str = None):
        if cls._instance is None:
            cls._instance = TrayManager(window, trigger_listen_callback)
            cls._instance._start_tray(icon_path)
        return cls._instance

    def _start_tray(self, icon_path: str = None):
        def run():
            try:
                if icon_path and os.path.exists(icon_path):
                    image = Image.open(icon_path)
                else:
                    # Резервный значок
                    image = Image.new('RGB', (64, 64), color=(0, 240, 255))

                menu = pystray.Menu(
                    pystray.MenuItem("Показать J.A.R.V.I.S.", self.show_window, default=True),
                    pystray.MenuItem("Слушать (Alt+J)", self.on_listen_click),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("Свернуть в трей", self.hide_window),
                    pystray.MenuItem("Выход", self.exit_app)
                )

                self.icon = pystray.Icon("JARVIS", image, "J.A.R.V.I.S. Prime", menu)
                self.icon.run()
            except Exception as e:
                print(f"[Tray Error]: {e}")

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def show_window(self, icon=None, item=None):
        try:
            self.window.restore()
            self.window.show()
            SoundFX.play_wake_sound()
        except Exception:
            pass

    def hide_window(self, icon=None, item=None):
        try:
            self.window.hide()
        except Exception:
            pass

    def on_listen_click(self, icon=None, item=None):
        self.show_window()
        if self.trigger_listen_callback:
            self.trigger_listen_callback()

    def exit_app(self, icon=None, item=None):
        try:
            if self.icon:
                self.icon.stop()
            self.window.destroy()
            os._exit(0)
        except Exception:
            os._exit(0)
