import os
import sys
import time
import threading
from pathlib import Path
import webview
import keyboard
import psutil

root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from jarvis.config import Config
from jarvis.voice.engine import VoiceEngine
from jarvis.core import JarvisCore
from jarvis.sound_fx import SoundFX
from jarvis.tools.telegram_bridge import TelegramBridge
from jarvis.tools.organizer import OrganizerManager
from jarvis.tools.security_sentry import SecuritySentry

class UltimateBridge:
    def __init__(self, window):
        self.window = window
        self.voice = VoiceEngine()
        self.core = None
        self.tg_bridge = None
        self._init_core()
        self._setup_hotkeys()
        self._start_wake_word()
        self._start_system_monitor()
        self._start_telegram_bridge()
        self._setup_organizer_listener()
        SoundFX.play_startup_sound()

    def _init_core(self):
        def load():
            try:
                self.core = JarvisCore()
                if self.tg_bridge:
                    self.tg_bridge.core = self.core
            except Exception as e:
                print(f"[Core Init]: {e}")
        threading.Thread(target=load, daemon=True).start()

    def _start_telegram_bridge(self):
        def start_tg():
            try:
                self.tg_bridge = TelegramBridge(self.core)
                SecuritySentry.set_telegram_bridge(self.tg_bridge)
                self.tg_bridge.start()
            except Exception as e:
                print(f"[Telegram Bridge Init]: {e}")
        threading.Thread(target=start_tg, daemon=True).start()

    def _setup_organizer_listener(self):
        def on_notify(msg):
            try:
                self.window.evaluate_js(f"addMessage('ОРГАНАЙЗЕР', '{msg}', false)")
                self.voice.speak(msg)
                if self.tg_bridge:
                    self.tg_bridge.send_notification(msg)
            except Exception:
                pass
        OrganizerManager.add_notification_listener(on_notify)
        OrganizerManager.ensure_monitor_running()

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

    def _start_system_monitor(self):
        """Реальный мониторинг CPU, RAM и Диска (как в Kira)"""
        def loop():
            while True:
                try:
                    cpu = int(psutil.cpu_percent(interval=1))
                    ram = int(psutil.virtual_memory().percent)
                    disk = int(psutil.disk_usage('C:').percent)
                    self.window.evaluate_js(f"updateSystemGauges({cpu}, {ram}, {disk})")
                except Exception:
                    pass
                time.sleep(2)
        threading.Thread(target=loop, daemon=True).start()

    def trigger_listen(self):
        def task():
            SoundFX.play_wake_sound()
            self.window.evaluate_js("setStatus('СЛУШАЮ СЭР...', true, false)")
            user_text = self.voice.listen(timeout=6, phrase_time_limit=10)
            self.window.evaluate_js("setStatus('ГОТОВ К РАБОТЕ', false, false)")

            if user_text:
                clean_text = user_text.replace("'", "\\'").replace('"', '\\"')
                self.window.evaluate_js(f"addMessage('СЭР', '{clean_text}', true)")
                self.send_command(user_text)

        threading.Thread(target=task, daemon=True).start()

    def send_command(self, prompt: str):
        def task():
            self.window.evaluate_js("setStatus('ОБРАБОТКА...', false, false)")

            if self.core:
                reply = self.core.process_request(prompt)
            else:
                reply = "Ядро Gemini пока инициализируется, сэр. Секунду."

            clean_reply = reply.replace("'", "\\'").replace('"', '\\"').replace("\n", "<br>")
            self.window.evaluate_js(f"addMessage('J.A.R.V.I.S.', '{clean_reply}', false)")
            self.window.evaluate_js("setStatus('ОТВЕЧАЮ ГОЛОСОМ...', false, true)")

            # Озвучивание настоящим дубляжом
            self.voice.speak(reply)
            self.window.evaluate_js("setStatus('ГОТОВ К РАБОТЕ', false, false)")

        threading.Thread(target=task, daemon=True).start()

    def switch_to_orb(self):
        """Переключение на легкий 3D-шар"""
        try:
            self.window.destroy()
            from jarvis.app_holo import start_holo_jarvis
            start_holo_jarvis()
        except Exception:
            pass

    def open_wizard(self):
        """Открыть мастер быстрой настройки из скриншотов"""
        wizard_path = os.path.join(os.path.dirname(__file__), "ui", "wizard.html")
        webview.create_window(
            title="J.A.R.V.I.S. Setup Wizard",
            url=wizard_path,
            width=540,
            height=620,
            background_color='#0b0816'
        )

    def complete_onboarding(self, data: dict):
        """Сохранение результатов мастера настройки"""
        from jarvis.settings_manager import SettingsManager
        current = SettingsManager.load()
        current.update(data)
        SettingsManager.save(current)
        self.window.evaluate_js(f"addMessage('СИСТЕМА', 'Мастер настройки завершен! Приятно познакомиться, {data.get('user_name', 'сэр')}.', false)")

    def get_settings(self):
        """Получить текущие настройки для отображения в UI"""
        from jarvis.settings_manager import SettingsManager
        return SettingsManager.load()

    def save_settings(self, new_settings: dict):
        from jarvis.settings_manager import SettingsManager
        current = SettingsManager.load()
        current.update(new_settings)
        SettingsManager.save(current)
        
        # Обновление параметров голоса в реальном времени
        voice_id = new_settings.get("voice")
        rate = new_settings.get("speech_rate")
        pitch = new_settings.get("speech_pitch")
        self.voice.update_voice_params(voice_name=voice_id, rate=rate, pitch=pitch)

        # Если обновлен API-ключ Gemini или модель
        if "gemini_api_key" in new_settings and new_settings["gemini_api_key"]:
            os.environ["GEMINI_API_KEY"] = new_settings["gemini_api_key"]
            try:
                from jarvis.core import JarvisCore
                self.core = JarvisCore()
            except Exception:
                pass

        # Если обновлен токен Telegram
        if "telegram_bot_token" in new_settings:
            if self.tg_bridge:
                self.tg_bridge.stop()
            self._start_telegram_bridge()

        return True

    def close_app(self):
        self.window.destroy()
        os._exit(0)


def start_ultimate_jarvis():
    html_path = os.path.join(os.path.dirname(__file__), "ui", "nexus.html")
    window = webview.create_window(
        title="J.A.R.V.I.S. PRIME — Quantum Nexus HUD",
        url=html_path,
        width=1180,
        height=740,
        frameless=True,
        easy_drag=True,
        background_color='#020409'
    )
    bridge = UltimateBridge(window)
    window.expose(
        bridge.trigger_listen,
        bridge.send_command,
        bridge.switch_to_orb,
        bridge.get_settings,
        bridge.save_settings,
        bridge.open_wizard,
        bridge.complete_onboarding,
        bridge.close_app
    )
    webview.start()

if __name__ == "__main__":
    start_ultimate_jarvis()
