import math
import random
import threading
import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from jarvis.config import Config
from jarvis.voice.engine import VoiceEngine
from jarvis.core import JarvisCore
from jarvis.tools.video_editor import VideoEditorTool
from jarvis.tools.computer_use import ComputerUseTool
from jarvis.tools.file_manager import FileManagerTool

class JarvisStudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S. PRIME — Studio Command Center")
        self.root.geometry("1100x700")
        self.root.minsize(950, 600)

        self.voice = VoiceEngine()
        self.core = None
        self.is_listening = False
        self.is_speaking = False
        self.angle = 0

        self._setup_style()
        self._build_ui()
        self._init_brain()
        self._animate_hud()

    def _setup_style(self):
        self.style = tb.Style(theme="superhero")

    def _build_ui(self):
        # Главный контейнер на две колонки
        self.main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#0d1117", sashwidth=4)
        self.main_pane.pack(fill=tk.BOTH, expand=True)

        # ЛЕВАЯ КОЛОНКА: HUD, Статус, Голосовое ядро
        self.left_frame = tk.Frame(self.main_pane, bg="#090d16", width=460)
        self.main_pane.add(self.left_frame)

        # ПРАВАЯ КОЛОНКА: Панель управления, Студия монтажа, Логи ReAct
        self.right_frame = tk.Frame(self.main_pane, bg="#0d1117")
        self.main_pane.add(self.right_frame)

        self._build_left_hud()
        self._build_right_studio()

    def _build_left_hud(self):
        # Заголовок
        lbl_brand = tk.Label(
            self.left_frame, text="⚡ J . A . R . V . I . S   P R I M E",
            font=("Consolas", 18, "bold"), fg="#00f0ff", bg="#090d16"
        )
        lbl_brand.pack(pady=(20, 2))

        lbl_desc = tk.Label(
            self.left_frame, text="AUTONOMOUS COMPUTER-USE & STUDIO AGENT",
            font=("Consolas", 8), fg="#00838f", bg="#090d16"
        )
        lbl_desc.pack(pady=(0, 10))

        # Холст HUD Реактора
        self.canvas = tk.Canvas(self.left_frame, width=380, height=280, bg="#090d16", highlightthickness=0)
        self.canvas.pack(pady=5)

        # Статусная плашка
        self.lbl_status = tk.Label(
            self.left_frame, text="SYSTEM INITIALIZING...",
            font=("Consolas", 11, "bold"), fg="#00f0ff", bg="#090d16"
        )
        self.lbl_status.pack(pady=5)

        # Кнопка голосовой активации
        self.btn_mic = tb.Button(
            self.left_frame,
            text="🎙️ АКТИВИРОВАТЬ МИКРОФОН",
            bootstyle="info-outline",
            command=self.toggle_voice_listen
        )
        self.btn_mic.pack(pady=15, ipadx=15, ipady=5)

        # Индикатор устройств
        sys_box = tk.LabelFrame(self.left_frame, text=" Статус модулей ", font=("Consolas", 9), fg="#80d8ff", bg="#090d16", padx=10, pady=10)
        sys_box.pack(fill=tk.X, padx=25, pady=10)

        tk.Label(sys_box, text="● Модуль видеомонтажа (FFmpeg): ГОТОВ", font=("Consolas", 8), fg="#00e676", bg="#090d16").pack(anchor="w")
        tk.Label(sys_box, text="● Модуль Computer-Use (Мышь/Окна): ГОТОВ", font=("Consolas", 8), fg="#00e676", bg="#090d16").pack(anchor="w")
        tk.Label(sys_box, text="● Голосовой синтез (Neural TTS): ГОТОВ", font=("Consolas", 8), fg="#00e676", bg="#090d16").pack(anchor="w")

    def _build_right_studio(self):
        notebook = tb.Notebook(self.right_frame, bootstyle="info")
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Вкладка 1: Диалог и Выполнение задач
        tab_chat = tk.Frame(notebook, bg="#161b22")
        notebook.add(tab_chat, text="  💬 Диалог с Джарвисом  ")

        self.chat_display = tk.Text(tab_chat, bg="#0d1117", fg="#c9d1d9", font=("Segoe UI", 10), wrap=tk.WORD, borderwidth=0)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Нижняя строка ввода текста
        input_frame = tk.Frame(tab_chat, bg="#161b22")
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.entry_cmd = tb.Entry(input_frame, font=("Segoe UI", 10))
        self.entry_cmd.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry_cmd.bind("<Return>", lambda e: self.send_text_command())

        btn_send = tb.Button(input_frame, text="Отправить", bootstyle="info", command=self.send_text_command)
        btn_send.pack(side=tk.RIGHT)

        # Вкладка 2: Панель Видеомонтажа
        tab_studio = tk.Frame(notebook, bg="#161b22", padx=15, pady=15)
        notebook.add(tab_studio, text="  🎬 Студия Монтажа  ")

        tk.Label(tab_studio, text="БЫСТРЫЕ ОПЕРАЦИИ С ВИДЕО", font=("Consolas", 12, "bold"), fg="#00f0ff", bg="#161b22").pack(anchor="w", pady=(0, 10))

        # Кнопки быстрых действий студии
        ops = [
            ("✂️ Нарезать первые 30 сек", "Обрежь первые 30 секунд у видео"),
            ("📱 Конвертировать в формат Shorts/Reels (9:16)", "Переведи горизонтальное видео в вертикальный формат Shorts"),
            ("🎵 Наложить фоновую музыку", "Наложи фоновую музыку на видео с тихим звуком"),
            ("📸 Сделать скриншот экрана", "Сделай скриншот экрана и сохрани"),
            ("🔍 Найти видеофайлы в папке Загрузки", "Найди все видеофайлы в папке Загрузки")
        ]
        for title, prompt in ops:
            btn = tb.Button(tab_studio, text=title, bootstyle="secondary-outline", command=lambda p=prompt: self.execute_prompt(p))
            btn.pack(fill=tk.X, pady=4)

    def _init_brain(self):
        def load():
            try:
                self.core = JarvisCore()
                self.root.after(0, lambda: self.set_status("СИСТЕМЫ В СТРОЮ // ГОТОВ К РАБОТЕ", "#00f0ff"))
                self.root.after(0, lambda: self.append_chat("Джарвис", "Все протоколы активированы, сэр. Я готов к работе."))
            except Exception as e:
                self.root.after(0, lambda: self.set_status("ОШИБКА ПОДКЛЮЧЕНИЯ", "#ff5252"))
                self.root.after(0, lambda: self.append_chat("Система", f"Ошибка: {e}"))
        threading.Thread(target=load, daemon=True).start()

    def set_status(self, text, color="#00f0ff"):
        self.lbl_status.config(text=text, fg=color)

    def append_chat(self, author, message):
        self.chat_display.insert(tk.END, f"[{author}]: ", "bold")
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.see(tk.END)

    def send_text_command(self):
        text = self.entry_cmd.get().strip()
        if text:
            self.entry_cmd.delete(0, tk.END)
            self.execute_prompt(text)

    def execute_prompt(self, prompt):
        self.append_chat("Сэр", prompt)
        self.set_status("ОБРАБОТКА КОМАНДЫ...", "#ff9100")

        def run_task():
            if self.core:
                reply = self.core.process_request(prompt)
            else:
                reply = "Ядро Gemini пока инициализируется, сэр. Секунду."

            self.root.after(0, lambda: self.append_chat("Джарвис", reply))
            self.root.after(0, lambda: self.set_status("СИСТЕМЫ В СТРОЮ // ОЖИДАНИЕ", "#00f0ff"))

            # Озвучка ответа
            self.is_speaking = True
            self.voice.speak(reply)
            self.is_speaking = False

        threading.Thread(target=run_task, daemon=True).start()

    def toggle_voice_listen(self):
        if self.is_listening:
            return

        def listen_task():
            self.is_listening = True
            self.root.after(0, lambda: self.set_status("СЛУШАЮ ВАС, СЭР...", "#ffd600"))
            self.root.after(0, lambda: self.btn_mic.configure(bootstyle="warning"))

            text = self.voice.listen(timeout=6, phrase_time_limit=10)

            self.is_listening = False
            self.root.after(0, lambda: self.btn_mic.configure(bootstyle="info-outline"))

            if text:
                self.root.after(0, lambda: self.execute_prompt(text))
            else:
                self.root.after(0, lambda: self.set_status("СИСТЕМЫ В СТРОЮ // ОЖИДАНИЕ", "#00f0ff"))

        threading.Thread(target=listen_task, daemon=True).start()

    def _animate_hud(self):
        self.canvas.delete("all")
        cx, cy = 190, 140

        color = "#00f0ff" if not self.is_speaking else "#ff9100"
        if self.is_listening:
            color = "#ffd600"

        # Внешнее вращающееся кольцо с метками
        num_ticks = 32
        for i in range(num_ticks):
            rad = math.radians(i * (360 / num_ticks) + self.angle)
            r1 = 100
            r2 = 110 if i % 4 == 0 else 105
            x1 = cx + r1 * math.cos(rad)
            y1 = cy + r1 * math.sin(rad)
            x2 = cx + r2 * math.cos(rad)
            y2 = cy + r2 * math.sin(rad)
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2 if i % 4 == 0 else 1)

        # Вращающиеся дуги
        self.canvas.create_arc(cx - 85, cy - 85, cx + 85, cy + 85, start=-self.angle * 2, extent=130, outline=color, width=3, style=tk.ARC)
        self.canvas.create_arc(cx - 85, cy - 85, cx + 85, cy + 85, start=-self.angle * 2 + 180, extent=70, outline=color, width=3, style=tk.ARC)

        # Пульсирующее ядро
        pulse = 4 * math.sin(math.radians(self.angle * 6))
        core_r = 40 + (pulse if not self.is_speaking else random.randint(5, 15))
        self.canvas.create_oval(cx - core_r, cy - core_r, cx + core_r, cy + core_r, outline=color, width=2)

        # Спектрограмма звука в центре
        for i in range(9):
            bx = cx - 24 + (i * 6)
            h = random.randint(3, 20) if (self.is_speaking or self.is_listening) else int(4 + 3 * math.sin(math.radians(self.angle * 10 + i * 40)))
            self.canvas.create_line(bx, cy - h, bx, cy + h, fill="#ffffff", width=2)

        self.angle = (self.angle + (4 if self.is_speaking else 1.5)) % 360
        self.root.after(30, self._animate_hud)

def start_gui():
    root = tb.Window(themename="superhero")
    app = JarvisStudioApp(root)
    root.mainloop()

if __name__ == "__main__":
    start_gui()
