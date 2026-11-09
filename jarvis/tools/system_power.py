import os
import subprocess
from typing import Optional

class SystemPowerSkill:
    """
    Скилл управления питанием, блокировкой и состоянием системы Windows.
    Поддерживает: выключение, перезагрузку, таймер выключения, отмену таймера,
    блокировку экрана (Win+L) и переход в режим сна.
    """

    @staticmethod
    def lock_workstation() -> str:
        """Мгновенно блокирует экран компьютера (Win + L) для защиты рабочего места"""
        try:
            # Вызов LockWorkStation из user32.dll
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
            return "Рабочая станция заблокирована, сэр. Безопасность обеспечена."
        except Exception as e:
            return f"Не удалось заблокировать экран: {e}"

    @staticmethod
    def sleep_pc() -> str:
        """Переводит компьютер в режим сна (энергосбережение)"""
        try:
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
            return "Перевожу систему в режим энергосбережения и сна, сэр."
        except Exception as e:
            return f"Не удалось отправить систему в сон: {e}"

    @staticmethod
    def shutdown_pc(timer_seconds: int = 0) -> str:
        """
        Выключает компьютер.
        timer_seconds: задержка в секундах (например, 1800 для 30 минут).
        Если 0 — выключает через 10 секунд с предупреждением.
        """
        try:
            sec = max(0, timer_seconds)
            if sec > 0:
                mins = round(sec / 60, 1)
                subprocess.run(["shutdown", "/s", "/t", str(sec)], check=True)
                return f"Инициализирован протокол выключения питания. Компьютер выключится через {mins} мин. (секунд: {sec}), сэр."
            else:
                subprocess.run(["shutdown", "/s", "/t", "10"], check=True)
                return "Инициализировано завершение работы системы. Выключение произойдет через 10 секунд, сэр."
        except Exception as e:
            return f"Ошибка при выключении питания: {e}"

    @staticmethod
    def restart_pc(timer_seconds: int = 0) -> str:
        """
        Перезагружает компьютер.
        timer_seconds: задержка перед перезагрузкой.
        """
        try:
            sec = max(0, timer_seconds)
            if sec > 0:
                mins = round(sec / 60, 1)
                subprocess.run(["shutdown", "/r", "/t", str(sec)], check=True)
                return f"Инициализирована перезагрузка системы через {mins} мин. ({sec} сек), сэр."
            else:
                subprocess.run(["shutdown", "/r", "/t", "10"], check=True)
                return "Инициализирована перезагрузка системы. Перезагрузка начнется через 10 секунд, сэр."
        except Exception as e:
            return f"Ошибка при перезагрузке: {e}"

    @staticmethod
    def cancel_shutdown() -> str:
        """Отменяет запланированное выключение или перезагрузку компьютера"""
        try:
            subprocess.run(["shutdown", "/a"], check=True)
            return "Запланированное выключение системы успешно отменено, сэр."
        except Exception as e:
            return f"Не удалось отменить выключение (возможно, таймер не был установлен): {e}"
