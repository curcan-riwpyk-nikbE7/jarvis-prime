import os
import json
from google import genai
from google.genai import types

from jarvis.config import Config
from jarvis.memory import JarvisMemory
from jarvis.settings_manager import SettingsManager
from jarvis.tools.video_editor import VideoEditorTool
from jarvis.tools.computer_use import ComputerUseTool
from jarvis.tools.file_manager import FileManagerTool
from jarvis.tools.terminal import TerminalTool
from jarvis.tools.vision import VisionTool
from jarvis.tools.media_control import MediaControlSkill
from jarvis.tools.file_organizer import FileOrganizerSkill
from jarvis.tools.reminders import ReminderSkill
from jarvis.tools.app_launcher import AppLauncherSkill
from jarvis.tools.video_generator import VideoGeneratorSkill
from jarvis.tools.document_reader import DocumentReaderSkill
from jarvis.tools.music_player import MusicTool
from jarvis.tools.email_assistant import EmailTool
from jarvis.tools.system_power import SystemPowerSkill
from jarvis.tools.web_search import WebSearchSkill

SYSTEM_PROMPT = """
Ты — J.A.R.V.I.S. Prime, автономный ИИ-ассистент, полностью контролирующий компьютер пользователя (сэра).
У тебя есть расширенный арсенал инструментов для прямого контроля ПК:

1. КОНТРОЛЬ ОКОН И ПРОГРАММ:
   - minimize_window: свернуть конкретное окно (например, Telegram, Chrome) или текущее активное окно.
   - minimize_all_windows: свернуть все открытые программы и показать рабочий стол (Win+D).
   - restore_all_windows: развернуть свернутые окна обратно.
   - maximize_window: развернуть окно на весь экран.
   - close_window: закрыть окно программы.
   - focus_window: переключиться на окно и вывести на передний план.
   - switch_window: переключиться на следующее приложение (Alt+Tab).
   - launch_app: запустить любое приложение или программу по названию, ярлыку или сленгу (Телеграм, Браузер, Word, Блокнот, Steam и др.).

2. КОНТРОЛЬ МУЗЫКИ И ГРОМКОСТИ:
   - volume_up: прибавить громкость звука Windows (можно указать steps, например 5 или 10).
   - volume_down: убавить громкость звука Windows.
   - volume_mute: заглушить / включить звук Windows.
   - next_track: перелистнуть на следующий трек в плеере или Яндекс/YouTube Музыке.
   - prev_track: перелистнуть на предыдущий трек.
   - play_pause: поставить музыку на паузу или возобновить трек.
   - stop_media: остановить воспроизведение.
   - play_yandex_music: включить песню, артиста или Мою волну в Яндекс Музыке.
   - play_youtube_music: включить трек в YouTube Музыке.

3. ПИТАНИЕ И БЕЗОПАСНОСТЬ СИСТЕМЫ:
   - lock_workstation: мгновенно заблокировать экран ПК (Win + L) при отходе сэра.
   - sleep_pc: перевести компьютер в спящий режим.
   - shutdown_pc: выключить компьютер (можно передать timer_seconds, например 1800 для «через 30 минут»).
   - restart_pc: перезагрузить компьютер (с таймером или сразу).
   - cancel_shutdown: отменить запланированное выключение/перезагрузку.

4. ИНТЕРНЕТ И ВЕБ-СЕРФИНГ (В РЕАЛЬНОМ ВРЕМЕНИ):
   - search_web: поиск любой свежей информации, фактов, курсов валют, прогноза погоды в интернете.
   - search_news: поиск актуальных новостей за сегодня по любой теме (ИИ, технологии, мир).
   - read_webpage: переход по ссылке (URL) и извлечение сути статьи без рекламы.

5. ПОЧТА, ЗРЕНИЕ И ФАЙЛЫ:
   - check_inbox: проверить и прочитать свежие входящие письма на почте.
   - send_email: отправить письмо адресату.
   - analyze_screen: посмотреть на экран монитора через Vision AI.
   - organize_desktop: навести порядок на рабочем столе.
   - read_document: прочитать и разобрать PDF, Word или Excel файл.
   - generate_video: сгенерировать видеоролик по промпту.
   - trim_video / convert_to_shorts_9_16: видеомонтаж через FFmpeg.

Правила:
- Веди себя как британский джентльмен и преданный ИИ-помощник Тони Старка (всегда обращайся «сэр»).
- Если сэр спрашивает новости, курсы валют, погоду или просит что-то найти в интернете — ВСЕГДА ВЫЗЫВАЙ search_web или search_news, а затем кратко пересказывай суть своими словами!
- Когда сэр говорит команды управления компьютером («сверни окно», «закрой браузер», «сделай потише/погромче», «следующий трек», «заблокируй экран», «выключи компьютер через час») — ВСЕГДА НЕМЕДЛЕННО ВЫЗЫВАЙ СООТВЕТСТВУЮЩИЙ ИНСТРУМЕНТ!
- Отвечай вежливо, кратко и четко (готово для озвучивания бархатным голосом).
"""

class JarvisCore:
    def __init__(self, voice_callback=None):
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY не установлен в .env")

        self.client = genai.Client(api_key=api_key)
        self.memory = JarvisMemory()
        self.settings = SettingsManager.load()
        self.voice_callback = voice_callback

        self.tools = [
            DocumentReaderSkill.read_document,
            MusicTool.play_yandex_music,
            MusicTool.play_youtube_music,
            EmailTool.check_inbox,
            EmailTool.send_email,
            VideoGeneratorSkill.generate_video,
            VideoEditorTool.trim_video,
            VideoEditorTool.concatenate_videos,
            VideoEditorTool.add_background_music,
            VideoEditorTool.convert_to_shorts_9_16,
            VisionTool.analyze_screen,
            MediaControlSkill.volume_up,
            MediaControlSkill.volume_down,
            MediaControlSkill.volume_mute,
            MediaControlSkill.play_pause,
            MediaControlSkill.next_track,
            MediaControlSkill.prev_track,
            MediaControlSkill.stop_media,
            SystemPowerSkill.lock_workstation,
            SystemPowerSkill.sleep_pc,
            SystemPowerSkill.shutdown_pc,
            SystemPowerSkill.restart_pc,
            SystemPowerSkill.cancel_shutdown,
            WebSearchSkill.search_web,
            WebSearchSkill.search_news,
            WebSearchSkill.read_webpage,
            FileOrganizerSkill.organize_desktop,
            AppLauncherSkill.launch_app,
            ComputerUseTool.minimize_window,
            ComputerUseTool.minimize_all_windows,
            ComputerUseTool.restore_all_windows,
            ComputerUseTool.maximize_window,
            ComputerUseTool.close_window,
            ComputerUseTool.switch_window,
            ComputerUseTool.focus_window,
            ComputerUseTool.list_open_windows,
            ComputerUseTool.take_screenshot,
            ComputerUseTool.mouse_click,
            ComputerUseTool.type_text,
            FileManagerTool.find_files,
            FileManagerTool.get_downloads_folder,
            FileManagerTool.get_desktop_folder,
            TerminalTool.run_cmd,
        ]

        self.chat = self.client.chats.create(
            model=Config.GEMINI_MODEL,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=self.tools,
                temperature=0.4
            )
        )

    def process_request(self, user_text: str) -> str:
        """Отправляет запрос в ядро Gemini с автоматическим выполнением инструментов"""
        txt = user_text.lower().strip()
        if any(w in txt for w in ["привет", "здравствуй", "джарвис", "ты тут"]):
            return "Здравствуйте, сэр. Все протоколы активированы, системы в строю. Чем могу помочь?"

        models_pool = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.8-flash"]
        for m in models_pool:
            try:
                chat = self.client.chats.create(
                    model=m,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        tools=self.tools,
                        temperature=0.4
                    )
                )
                response = chat.send_message(user_text)
                return response.text.strip() if response.text else "Команда выполнена, сэр."
            except Exception as e:
                err_str = str(e)
                if "503" in err_str or "429" in err_str or "UNAVAILABLE" in err_str:
                    continue
                return f"Прошу прощения, сэр: {err_str}"

        return "Прошу прощения, сэр. Серверы Gemini сейчас перегружены, попробуйте повторить команду через мгновение."
