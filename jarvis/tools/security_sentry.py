import os
import time
import threading
from pathlib import Path
import cv2

class SecuritySentry:
    """
    Охранный режим (Security & Vision Sentry).
    Следит за присутствием через веб-камеру. Если кто-то появляется перед камерой
    в охранном режиме (или совершает движение):
    - Делает качественный снимок нарушителя
    - Сохраняет файл локально
    - Отправляет уведомление и фотографию владельцу в Telegram!
    """
    _is_active = False
    _sentry_thread = None
    _telegram_bridge = None
    SNAPSHOT_DIR = Path.home() / ".jarvis_security"

    @classmethod
    def set_telegram_bridge(cls, bridge):
        cls._telegram_bridge = bridge

    @classmethod
    def is_active(cls) -> bool:
        return cls._is_active

    @classmethod
    def capture_photo(cls) -> str:
        """Делает мгновенный снимок с веб-камеры и возвращает путь к файлу"""
        cls.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"sentry_{int(time.time())}.jpg"
        filepath = str(cls.SNAPSHOT_DIR / filename)

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return None

        # Пропускаем первые 3 кадра для автоэкспозиции камеры
        for _ in range(3):
            cap.read()

        ret, frame = cap.read()
        cap.release()

        if ret and frame is not None:
            cv2.imwrite(filepath, frame)
            return filepath
        return None

    @classmethod
    def arm(cls, interval_sec: int = 4) -> dict:
        """Активировать охранный режим"""
        if cls._is_active:
            return {"status": "info", "message": "Охранный режим уже включен, сэр."}

        cls._is_active = True

        def sentry_worker():
            print("[Security Sentry]: Охранный периметр активирован.")
            # Используем встроенный каскад Хаара для детекции лиц нарушителя
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            while cls._is_active:
                try:
                    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                    if not cap.isOpened():
                        cap = cv2.VideoCapture(0)

                    if cap.isOpened():
                        # Даем камере настроить баланс
                        for _ in range(2):
                            cap.read()
                        ret, frame = cap.read()
                        cap.release()

                        if ret and frame is not None:
                            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))

                            if len(faces) > 0:
                                print(f"[Security Sentry]: 🚨 Обнаружен человек перед экраном ({len(faces)} лиц)!")
                                cls.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
                                photo_path = str(cls.SNAPSHOT_DIR / f"alert_{int(time.time())}.jpg")
                                cv2.imwrite(photo_path, frame)

                                if cls._telegram_bridge and cls._telegram_bridge.is_running:
                                    alert_msg = f"🚨 ВНИМАНИЕ, СЭР!\nОбнаружено движение перед вашей станцией! Зафиксировано лицо нарушителя."
                                    cls._telegram_bridge.send_alert(alert_msg, photo_path)

                                # Задержка после детекции чтобы не спамить
                                time.sleep(15)
                except Exception as e:
                    print(f"[Security Sentry Error]: {e}")

                time.sleep(interval_sec)

        cls._sentry_thread = threading.Thread(target=sentry_worker, daemon=True)
        cls._sentry_thread.start()

        return {"status": "success", "message": "Охранный режим активирован! Веб-камера сканирует периметр на наличие людей."}

    @classmethod
    def disarm(cls) -> dict:
        """Деактивировать охранный режим"""
        cls._is_active = False
        return {"status": "success", "message": "Охранный режим отключен. Периметр в штатном режиме."}
