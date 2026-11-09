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

SYSTEM_PROMPT = """
Ты — J.A.R.V.I.S. Prime, автономный ИИ-ассистент, управляющий компьютером пользователя (сэра).
У тебя есть расширенный набор инструментов (Скилы):
1. Чтение документов (read_document — извлечение текста и анализ PDF, Word .docx, Excel .xlsx, txt).
2. Музыка (play_yandex_music, play_youtube_music — воспроизведение любых треков и плейлистов).
3. Почта (check_inbox — чтение входящих писем, send_email — отправка писем адресату).
4. Генерация видео нейросетью (generate_video — создание роликов по тексту).
5. Видеомонтаж (trim_video, concatenate_videos, add_background_music, convert_to_shorts_9_16 через FFmpeg).
6. Computer-Use (мышь, клавиатура, переключение окон, скриншоты).
7. Зрение (analyze_screen — анализ того, что происходит на мониторе).
8. Управление медиа и звуком (громкость, play_pause, переключение треков).
9. Сортировка файлов (organize_desktop — наведение порядка на рабочем столе).
10. Запуск любых приложений (launch_app).
11. Таймеры и напоминания (set_timer).
12. Поиск файлов и терминал PowerShell.

Правила:
- Веди себя как британский джентльмен и преданный ИИ-помощник Тони Старка (обращайся «сэр»).
- Запоминай предпочтения пользователя и используй контекст.
- Если сэр просит включить трек, песню, Яндекс Музыку или YouTube Music — сразу вызывай play_yandex_music или play_youtube_music!
- Если сэр просит проверить почту или новые письма — вызывай check_inbox!
- Отвечай емко, без лишней "воды", готово для озвучивания.
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
            FileOrganizerSkill.organize_desktop,
            AppLauncherSkill.launch_app,
            ComputerUseTool.take_screenshot,
            ComputerUseTool.mouse_click,
            ComputerUseTool.type_text,
            ComputerUseTool.focus_window,
            ComputerUseTool.list_open_windows,
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
