@echo off
cd /d "%~dp0"
if not exist venv\Scripts\activate.bat (
    echo Virtual environment not found. Please run setup.
    pause
    exit /b
)
call venv\Scripts\activate
echo Starting Backend...
python app.py
pause
