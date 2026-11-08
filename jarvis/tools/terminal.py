import subprocess

class TerminalTool:
    """Выполнение безопасных команд операционной системы Windows"""

    @staticmethod
    def run_cmd(command: str, timeout: int = 30) -> str:
        """Запуск команды через PowerShell"""
        try:
            res = subprocess.run(
                ["powershell", "-NoProfile", "-Command", command],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            out = res.stdout.strip()
            err = res.stderr.strip()
            if err:
                return f"[ВЫВОД]:\n{out}\n[ОШИБКИ]:\n{err}"
            return out or "Команда выполнена успешно (вывод пуст)."
        except subprocess.TimeoutExpired:
            return f"Ошибка: время ожидания выполнения команды ({timeout} сек) истекло."
        except Exception as e:
            return f"Ошибка запуска команды: {str(e)}"
