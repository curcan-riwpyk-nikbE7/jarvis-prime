@echo off
chcp 65001 >nul
echo ======================================================
echo    J.A.R.V.I.S. PRIME - Настройка окружения Windows
echo ======================================================

cd /d "%~dp0"

echo 1. Проверка Python...
python --version
if errorlevel 1 (
    echo [ОШИБКА] Python не обнаружен! Установите Python 3.10+ с python.org
    pause
    exit /b 1
)

echo 2. Создание виртуального окружения (.venv)...
python -m venv .venv
call .venv\Scripts\activate.bat

echo 3. Обновление pip и установка зависимостей...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo 4. Проверка файла конфигурации .env...
if not exist .env (
    copy .env.example .env
    echo [Инфо] Создан файл .env. Пожалуйста, откройте его и вставьте ваш GEMINI_API_KEY!
)

echo ======================================================
echo [УСПЕХ] Установка завершена! Запускайте Джарвиса через run.bat
echo ======================================================
pause
