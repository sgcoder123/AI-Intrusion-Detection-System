@echo off
echo 🛡️ Starting AI Intrusion Detection System...
echo Checking Python installation...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3 is not installed. Please install Python 3.7+ and try again.
    pause
    exit /b 1
)

echo ✅ Python found. Installing dependencies...

REM Install requirements
pip install -r requirements.txt --user

if %errorlevel% equ 0 (
    echo ✅ Dependencies installed successfully!
    echo 🚀 Starting AI-IDS...
    python ai_ids_app.py
) else (
    echo ❌ Failed to install dependencies. Please check your internet connection.
    pause
    exit /b 1
)
