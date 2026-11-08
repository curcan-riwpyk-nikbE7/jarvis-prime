import os
import json
from google import genai
from google.genai import types

from jarvis.config import Config
from jarvis.tools.video_editor import VideoEditorTool
from jarvis.tools.computer_use import ComputerUseTool
from jarvis.tools.file_manager import FileManagerTool
from jarvis.tools.terminal import TerminalTool

SYSTEM_PROMPT = """
Ты — J.A.R.V.I.S. Prime, автономный ИИ-ассистент, управляющий компьютером пользователя (сэра).
У тебя есть реальные инструменты для выполнения задач:
1. Видеомонтаж (нарезка, склейка видео, наложение музыки через FFmpeg).
2. Computer-Use (управление мышью, клики, ввод текста, переключение окон, скриншоты экрана).
3. Поиск файлов на диске (папка Загрузки, Рабочий стол).
4. Выполнение терминальных команд PowerShell.

Правила:
- Веди себя как британский джентльмен и преданный ИИ-помощник Тони Старка (обращайся «сэр»).
- Когда сэр просит смонтировать видео или сделать что-то на компьютере, используй доступные инструменты.
- Отвечай коротко, емко, без лишних длинных монологов.
"""

class JarvisCore:
    def __init__(self):
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY не установлен в .env")

        self.client = genai.Client(api_key=api_key)

        # Регистрируем функции в Gemini Function Calling
        self.tools = [
            VideoEditorTool.trim_video,
            VideoEditorTool.concatenate_videos,
            VideoEditorTool.add_background_music,
            VideoEditorTool.convert_to_shorts_9_16,
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
        try:
            response = self.chat.send_message(user_text)
            return response.text.strip() if response.text else "Команда выполнена, сэр."
        except Exception as e:
            return f"Прошу прощения, сэр. Ошибка при выполнении задачи: {str(e)}"
