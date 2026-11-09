import os
import subprocess
from typing import Dict, Any

class AutoUpdater:
    """
    Модуль автономного автообновления J.A.R.V.I.S. прямо из GitHub репозитория.
    Позволяет:
    - Проверить наличие новых коммитов / обновлений (git fetch, git status)
    - Установить обновление в один клик (git pull origin main)
    - Обновить зависимости (pip install -r requirements.txt)
    - Перезапустить приложение с сохранением настроек
    """

    REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    @classmethod
    def check_for_updates(cls) -> Dict[str, Any]:
        """Проверяет наличие свежих коммитов на GitHub"""
        try:
            # git fetch
            subprocess.run(
                ["git", "fetch", "origin", "main"],
                cwd=cls.REPO_DIR,
                capture_output=True,
                text=True,
                check=True
            )

            # Получаем локальный и удаленный хэши
            local_hash = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=cls.REPO_DIR,
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()

            remote_hash = subprocess.run(
                ["git", "rev-parse", "origin/main"],
                cwd=cls.REPO_DIR,
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()

            if local_hash != remote_hash:
                # Получаем список коммитов
                commits_log = subprocess.run(
                    ["git", "log", f"{local_hash}..{remote_hash}", "--oneline"],
                    cwd=cls.REPO_DIR,
                    capture_output=True,
                    text=True
                ).stdout.strip()

                return {
                    "has_update": True,
                    "local_version": local_hash[:7],
                    "remote_version": remote_hash[:7],
                    "changelog": commits_log or "Новые системные исправления и оптимизация.",
                    "message": f"Доступно обновление ({remote_hash[:7]})."
                }
            else:
                return {
                    "has_update": False,
                    "current_version": local_hash[:7],
                    "message": "У вас установлена последняя версия J.A.R.V.I.S. Prime!"
                }
        except Exception as e:
            return {
                "has_update": False,
                "error": str(e),
                "message": f"Ошибка проверки обновлений: {e}"
            }

    @classmethod
    def apply_update(cls) -> Dict[str, Any]:
        """Выполняет git pull и обновляет зависимости"""
        try:
            pull_res = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=cls.REPO_DIR,
                capture_output=True,
                text=True,
                check=True
            )

            # Обновляем зависимости при необходимости
            req_file = os.path.join(cls.REPO_DIR, "requirements.txt")
            if os.path.exists(req_file):
                subprocess.run(
                    [r"C:\Users\KINGSAID\AppData\Local\Programs\Python\Python312\python.exe", "-m", "pip", "install", "-r", req_file],
                    cwd=cls.REPO_DIR,
                    capture_output=True,
                    text=True
                )

            return {
                "status": "success",
                "message": "Обновление успешно загружено и установлено! Перезапуск...",
                "output": pull_res.stdout
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка при установке обновления: {e}"
            }
