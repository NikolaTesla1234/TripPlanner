@echo off
cd /d "%~dp0"
echo Запуск веб-версии (Билд 6, Flask)...
echo Откройте в браузере: http://127.0.0.1:5000
python -m pip install -r ..\requirements.txt >nul 2>&1
python app.py
pause
