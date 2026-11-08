import os
import sys
import threading
from pathlib import Path
import webview
import keyboard

root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from jarvis.config import Config
from jarvis.voice.engine import VoiceEngine
from jarvis.core import JarvisCore
from jarvis.sound_fx import SoundFX

class HoloBridge:
    def __init__(self, window):
        self.window = window
        self.voice = VoiceEngine()
        self.core = None
        self._init_core()
        self._setup_hotkeys()
        self._start_wake_word()
        SoundFX.play_startup_sound()

    def _init_core(self):
        def load():
            try:
                self.core = JarvisCore()
            except Exception as e:
                print(f"[Bridge] Ошибка инициализации: {e}")
        threading.Thread(target=load, daemon=True).start()

    def _setup_hotkeys(self):
        try:
            keyboard.add_hotkey("alt+j", self.trigger_listen)
        except Exception:
            pass

    def _start_wake_word(self):
        def loop():
            while True:
                try:
                    heard = self.voice.listen(timeout=3, phrase_time_limit=4)
                    if heard and any(w in heard.lower() for w in ["джарвис", "jarvis"]):
                        self.trigger_listen()
                except Exception:
                    pass
        threading.Thread(target=loop, daemon=True).start()

    def trigger_listen(self):
        def task():
            SoundFX.play_wake_sound()
            self.window.evaluate_js("setStatus('СЛУШАЮ ВАС, СЭР...', true, false)")
            user_text = self.voice.listen(timeout=6, phrase_time_limit=10)
            self.window.evaluate_js("setStatus('HOLO-3D CORE // READY', false, false)")

            if user_text:
                clean_text = user_text.replace("'", "\\'").replace('"', '\\"')
                self.window.evaluate_js(f"setHoloMessage('«{clean_text}»', false)")
                self.send_command(user_text)

        threading.Thread(target=task, daemon=True).start()

    def send_command(self, prompt: str):
        def task():
            self.window.evaluate_js("setStatus('ОБРАБОТКА КОМАНДЫ...', false, false)")

            if self.core:
                reply = self.core.process_request(prompt)
            else:
                reply = "Ядро Gemini пока загружается, сэр. Секунду."

            clean_reply = reply.replace("'", "\\'").replace('"', '\\"').replace("\n", "<br>")
            self.window.evaluate_js(f"setHoloMessage('{clean_reply}', true)")
            self.window.evaluate_js("setStatus('ОТВЕЧАЮ ГОЛОСОМ...', false, true)")

            # Озвучивание
            self.voice.speak(reply)
            self.window.evaluate_js("setStatus('HOLO-3D CORE // READY', false, false)")
            self.window.evaluate_js(f"setHoloMessage('{clean_reply}', false)")

        threading.Thread(target=task, daemon=True).start()

    def minimize_app(self):
        self.window.minimize()

    def close_app(self):
        self.window.destroy()
        os._exit(0)


def start_holo_jarvis():
    html_path = os.path.join(os.path.dirname(__file__), "ui", "holo.html")
    
    # Создаем безрамочное окно с поддержкой прозрачности
    window = webview.create_window(
        title="J.A.R.V.I.S. Holo-Sphere",
        url=html_path,
        width=1000,
        height=700,
        frameless=True,          # БЕЗ СИСТЕМНОЙ РАМКИ WINDOWS
        easy_drag=True,          # Перетаскивание кликом
        on_top=True,             # Парит поверх всех окон
        transparent=True,        # Прозрачный фон
        background_color='#030811'
    )
    bridge = HoloBridge(window)
    window.expose(bridge.trigger_listen, bridge.send_command, bridge.minimize_app, bridge.close_app)
    webview.start()

if __name__ == "__main__":
    start_holo_jarvis()
