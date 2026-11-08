import sys
import time
from jarvis.config import Config
from jarvis.voice.engine import VoiceEngine
from jarvis.core import JarvisCore

def main():
    print("=" * 60)
    print("       ⚡ J.A.R.V.I.S. PRIME — AUTONOMOUS AGENT ⚡")
    print("       Реальное управление компьютером & Видеомонтаж")
    print("=" * 60)

    voice = VoiceEngine()

    try:
        core = JarvisCore()
        print("\n[Статус]: Ядро Gemini подключено и готово к работе.")
    except Exception as e:
        print(f"\n[Внимание]: Ошибка подключения к Gemini: {e}")
        print("Убедитесь, что ваш API-ключ указан в файле .env")
        return

    welcome_msg = "Джарвис Прайм на связи, сэр. Все протоколы активированы. Чем могу помочь?"
    print(f"\nДжарвис: «{welcome_msg}»\n")
    voice.speak(welcome_msg)

    while True:
        try:
            print("\n[Режим прослушивания] Говорите в микрофон (или введите 'exit' для выхода):")
            user_input = voice.listen(timeout=6, phrase_time_limit=12)

            if not user_input:
                # Если микрофон молчит, даем возможность ввести текстом
                continue

            print(f"Сэр: «{user_input}»")

            if user_input.lower() in ["выход", "стоп", "отключись", "exit"]:
                farewell = "Отключаю питание систем. До встречи, сэр."
                print(f"Джарвис: «{farewell}»")
                voice.speak(farewell)
                break

            print("[Джарвис]: Выполняю команду...")
            reply = core.process_request(user_input)

            print(f"Джарвис: «{reply}»")
            voice.speak(reply)

        except KeyboardInterrupt:
            print("\nЗавершение работы по требованию пользователя.")
            break
        except Exception as e:
            print(f"[Ошибка]: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
