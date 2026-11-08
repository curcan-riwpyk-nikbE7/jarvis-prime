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
