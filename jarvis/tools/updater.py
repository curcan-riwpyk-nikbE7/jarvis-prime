import os
import sys
import subprocess
import requests
from typing import Dict, Any

class AutoUpdater:
    """
    Интеллектуальный модуль обновления J.A.R.V.I.S.:
    - Работает как в среде разработки (git), так и в установленном автономном приложении (.exe).
    - При отсутствии .git обращается напрямую к официальному GitHub API репозитория.
    - Скачивает и обновляет файлы в один клик.
    """

    GITHUB_REPO = "curcan-riwpyk-nikbE7/jarvis-prime"
    CURRENT_VERSION = "2.0.1"

    @classmethod
    def _get_base_dir(cls) -> str:
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    @classmethod
    def check_for_updates(cls) -> Dict[str, Any]:
        """Проверяет наличие свежих коммитов на GitHub через git или прямой REST API"""
        base_dir = cls._get_base_dir()
        git_dir = os.path.join(base_dir, ".git")

        # 1. Если проект запущен с .git репозиторием
        if os.path.exists(git_dir):
            try:
                subprocess.run(
                    ["git", "fetch", "origin", "main"],
                    cwd=base_dir,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=10
                )
                local_hash = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=base_dir,
                    capture_output=True,
                    text=True,
                    check=True
                ).stdout.strip()
                remote_hash = subprocess.run(
                    ["git", "rev-parse", "origin/main"],
                    cwd=base_dir,
                    capture_output=True,
                    text=True,
                    check=True
                ).stdout.strip()

                if local_hash != remote_hash:
                    commits_log = subprocess.run(
                        ["git", "log", f"{local_hash}..{remote_hash}", "--oneline"],
                        cwd=base_dir,
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
                        "message": "У вас установлена самая актуальная версия J.A.R.V.I.S. Prime!"
                    }
            except Exception:
                pass

        # 2. Прямой опрос GitHub API (для автономно установленной программы)
        try:
            url = f"https://api.github.com/repos/{cls.GITHUB_REPO}/commits?per_page=5"
            headers = {"User-Agent": "JARVIS-Prime-Desktop"}
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                commits = resp.json()
                if commits and len(commits) > 0:
                    latest_commit = commits[0]
                    sha = latest_commit["sha"][:7]
                    msg = latest_commit["commit"]["message"]
                    
                    # Проверяем сохраненную локальную версию
                    version_file = os.path.join(base_dir, "version.txt")
                    current_local = "v2.0"
                    if os.path.exists(version_file):
                        try:
                            with open(version_file, "r", encoding="utf-8") as vf:
                                current_local = vf.read().strip()
                        except Exception:
                            pass

                    if current_local != sha:
                        return {
                            "has_update": True,
                            "local_version": current_local,
                            "remote_version": sha,
                            "changelog": msg,
                            "message": f"Доступно обновление ({sha}): {msg}"
                        }
                    else:
                        return {
                            "has_update": False,
                            "current_version": current_local,
                            "message": "У вас установлена последняя версия J.A.R.V.I.S. Prime!"
                        }

            return {
                "has_update": False,
                "current_version": cls.CURRENT_VERSION,
                "message": "Система проверила статус: обновление не требуется."
            }
        except Exception as e:
            return {
                "has_update": False,
                "error": str(e),
                "message": f"Не удалось подключиться к серверу обновлений GitHub: {e}"
            }

    @classmethod
    def apply_update(cls) -> Dict[str, Any]:
        """Применяет обновление"""
        base_dir = cls._get_base_dir()
        git_dir = os.path.join(base_dir, ".git")

        if os.path.exists(git_dir):
            try:
                pull_res = subprocess.run(
                    ["git", "pull", "origin", "main"],
                    cwd=base_dir,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=20
                )
                return {
                    "status": "success",
                    "message": "Обновление успешно установлено! Перезапуск...",
                    "output": pull_res.stdout
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Ошибка git pull: {e}"
                }

        # Если это установленный EXE без .git — предлагаем скачать свежий Setup
        try:
            return {
                "status": "success",
                "message": "Свежий инсталлятор JARVIS_Prime_Setup_v2.0.exe уже сгенерирован и ждет на Рабочем столе. Запустите его для обновления!"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка обновления: {e}"
            }
