@echo off
cd /d "%~dp0"
echo Установка зависимостей...
python -m pip install -r requirements.txt >nul 2>&1
echo Запуск сервера FastAPI...
echo Откройте в браузере: http://127.0.0.1:8000
python -m uvicorn app.main:app --reload
pause
