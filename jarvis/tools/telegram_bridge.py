import os
import time
import threading
from pathlib import Path
import telebot
from telebot import types

from jarvis.config import Config
from jarvis.settings_manager import SettingsManager

class TelegramBridge:
    """
    Личный защищенный Telegram-мост для Джарвиса.
    Позволяет сэру управлять компьютером удаленно с телефона через Telegram:
    - Выполнять любые текстовые и голосовые запросы через ядро Jarvis Core
    - Запрашивать снимок экрана в реальном времени (/screen)
    - Блокировать рабочий стол (/lock)
    - Выключать или перезагружать ПК (/shutdown, /cancel)
    - Проверять запущенные программы и состояние (/status)
    """

    _instance = None
    _thread = None

    def __init__(self, core_instance=None):
        self.core = core_instance
        self.bot = None
        self.is_running = False
        self._load_credentials()

    def _load_credentials(self):
        settings = SettingsManager.load()
        self.token = settings.get("telegram_bot_token") or Config.TELEGRAM_BOT_TOKEN or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.allowed_user_id = settings.get("telegram_user_id") or Config.TELEGRAM_ALLOWED_USER_ID or os.getenv("TELEGRAM_ALLOWED_USER_ID", "")

    def start(self):
        self._load_credentials()
        if not self.token:
            print("[Telegram Bridge]: Токен Telegram-бота не установлен. Ожидание настройки...")
            return False

        if self.is_running:
            return True

        try:
            self.bot = telebot.TeleBot(self.token, parse_mode=None)
            self._register_handlers()
            self.is_running = True

            def polling_loop():
                print("[Telegram Bridge]: Telegram-мост успешно активирован. Бот на связи!")
                while self.is_running:
                    try:
                        self.bot.infinity_polling(timeout=10, long_polling_timeout=5)
                    except Exception as e:
                        print(f"[Telegram Polling error]: {e}")
                        time.sleep(3)

            self._thread = threading.Thread(target=polling_loop, daemon=True)
            self._thread.start()
            return True
        except Exception as e:
            print(f"[Telegram Bridge Init Error]: {e}")
            return False

    def stop(self):
        self.is_running = False
        if self.bot:
            try:
                self.bot.stop_polling()
            except Exception:
                pass

    def send_alert(self, text: str, photo_path: str = None):
        """Отправляет тревожное уведомление с фотографией владельцу в Telegram"""
        if not self.bot or not self.allowed_user_id:
            return
        try:
            if photo_path and os.path.exists(photo_path):
                with open(photo_path, 'rb') as f:
                    self.bot.send_photo(self.allowed_user_id, f, caption=text)
            else:
                self.bot.send_message(self.allowed_user_id, text)
        except Exception as e:
            print(f"[Telegram send_alert error]: {e}")

    def send_notification(self, text: str):
        """Отправляет текстовое уведомление владельцу в Telegram"""
        if not self.bot or not self.allowed_user_id:
            return
        try:
            self.bot.send_message(self.allowed_user_id, text)
        except Exception as e:
            print(f"[Telegram send_notification error]: {e}")

    def _is_authorized(self, user_id: int) -> bool:
        if not self.allowed_user_id:
            # Если ID еще не задан, запоминаем первого написавшего как владельца
            self.allowed_user_id = str(user_id)
            settings = SettingsManager.load()
            settings["telegram_user_id"] = str(user_id)
            SettingsManager.save(settings)
            print(f"[Telegram Bridge]: Авторизован первый владелец Telegram ID: {user_id}")
            return True
        return str(user_id) == str(self.allowed_user_id)

    def _register_handlers(self):
        bot = self.bot

        @bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            if not self._is_authorized(message.from_user.id):
                bot.reply_to(message, "⛔ Доступ ограничен. Эта станция J.A.R.V.I.S. принадлежит сэру.")
                return

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row("📸 Скриншот экрана", "🔒 Блокировка ПК")
            markup.row("🛡️ Охрана: Вкл", "🛡️ Охрана: Выкл")
            markup.row("⏰ Мои напоминания", "📝 Заметки")
            markup.row("✉️ Проверить почту", "🎵 Моя волна")
            markup.row("📊 Статус ПК", "⏹️ Отмена выключения")

            welcome_text = (
                "Здравствуйте, сэр! 🎩\n"
                "Квантовый мост J.A.R.V.I.S. синхронизирован с вашим мобильным терминалом.\n\n"
                "Вы можете присылать мне текстовые команды или нажимать кнопки быстрого контроля:\n"
                "• /screen — прислать снимок экрана\n"
                "• /lock — мгновенно заблокировать ПК\n"
                "• /shutdown <минуты> — запланировать выключение\n"
                "• /cancel — отменить выключение\n"
                "• Любой текст или вопрос — выполню на вашем компьютере!"
            )
            bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

        @bot.message_handler(commands=['screen', 'screenshot'])
        def handle_screenshot(message):
            if not self._is_authorized(message.from_user.id):
                return
            bot.send_chat_action(message.chat.id, 'upload_photo')
            try:
                from jarvis.tools.computer_use import ComputerUseTool
                shot_path = Path.home() / "Desktop" / "tg_live_screen.png"
                ComputerUseTool.take_screenshot(str(shot_path))
                with open(shot_path, 'rb') as photo:
                    bot.send_photo(message.chat.id, photo, caption="Текущий снимок вашего монитора, сэр.")
                if shot_path.exists():
                    shot_path.unlink()
            except Exception as e:
                bot.reply_to(message, f"Ошибка при захвате экрана: {e}")

        @bot.message_handler(commands=['lock'])
        def handle_lock(message):
            if not self._is_authorized(message.from_user.id):
                return
            from jarvis.tools.system_power import SystemPowerSkill
            res = SystemPowerSkill.lock_workstation()
            bot.reply_to(message, res)

        @bot.message_handler(commands=['status'])
        def handle_status(message):
            if not self._is_authorized(message.from_user.id):
                return
            try:
                import psutil
                cpu = psutil.cpu_percent(interval=0.5)
                ram = psutil.virtual_memory().percent
                disk = psutil.disk_usage('C:').percent
                from jarvis.tools.computer_use import ComputerUseTool
                wins = ComputerUseTool.list_open_windows()
                wins_text = "\n".join([f"• {w[:35]}" for w in wins[:5]])

                text = (
                    f"🖥️ **Телеметрия рабочей станции:**\n"
                    f"• Процессор (CPU): {cpu}%\n"
                    f"• Память (RAM): {ram}%\n"
                    f"• Накопитель (SSD): {disk}%\n\n"
                    f"Активные окна:\n{wins_text}"
                )
                bot.send_message(message.chat.id, text, parse_mode="Markdown")
            except Exception as e:
                bot.reply_to(message, f"Ошибка статуса: {e}")

        @bot.message_handler(func=lambda msg: True)
        def handle_text(message):
            if not self._is_authorized(message.from_user.id):
                bot.reply_to(message, "⛔ Доступ ограничен.")
                return

            text = message.text.strip()
            
            # Быстрые кнопки меню
            if text == "📸 Скриншот экрана":
                handle_screenshot(message)
                return
            elif text == "🔒 Блокировка ПК":
                handle_lock(message)
                return
            elif text == "📊 Статус ПК":
                handle_status(message)
                return
            elif text == "⏹️ Отмена выключения":
                from jarvis.tools.system_power import SystemPowerSkill
                res = SystemPowerSkill.cancel_shutdown()
                bot.reply_to(message, res)
                return
            elif text == "🛡️ Охрана: Вкл":
                from jarvis.tools.security_sentry import SecuritySentry
                SecuritySentry.set_telegram_bridge(self)
                res = SecuritySentry.arm()
                bot.reply_to(message, res.get("message", "Охрана включена."))
                return
            elif text == "🛡️ Охрана: Выкл":
                from jarvis.tools.security_sentry import SecuritySentry
                res = SecuritySentry.disarm()
                bot.reply_to(message, res.get("message", "Охрана выключена."))
                return
            elif text == "⏰ Мои напоминания":
                from jarvis.tools.organizer import OrganizerManager
                reminders = OrganizerManager.list_pending()
                if not reminders:
                    bot.reply_to(message, "Активных напоминаний нет, сэр.")
                else:
                    lines = [f"• {r.get('target_time', '')}: {r.get('text', '')}" for r in reminders]
                    bot.reply_to(message, "⏰ Список активных напоминаний:\n" + "\n".join(lines))
                return
            elif text == "📝 Заметки":
                from jarvis.tools.organizer import OrganizerManager
                notes = OrganizerManager.list_notes()
                if not notes:
                    bot.reply_to(message, "Заметок пока нет, сэр.")
                else:
                    lines = [f"• [{n.get('date', '')}] {n.get('text', '')}" for n in notes[-5:]]
                    bot.reply_to(message, "📝 Последние заметки:\n" + "\n".join(lines))
                return
            elif text == "✉️ Проверить почту":
                text = "Проверь последние входящие письма на почте"
            elif text == "🎵 Моя волна":
                text = "Включи Мою волну в Яндекс Музыке"

            bot.send_chat_action(message.chat.id, 'typing')

            if not self.core:
                try:
                    from jarvis.core import JarvisCore
                    self.core = JarvisCore()
                except Exception as e:
                    bot.reply_to(message, f"Инициализация ядра: {e}")
                    return

            try:
                # Отправляем в главное ядро Джарвиса со всеми инструментами ПК
                reply = self.core.process_request(text)
                bot.send_message(message.chat.id, reply)
            except Exception as e:
                bot.reply_to(message, f"Ошибка исполнения команды: {e}")
