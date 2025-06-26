@echo off
echo 🛡️ Starting AI Intrusion Detection System - Web Edition
echo.
echo This application runs in your web browser.
echo A browser window will open automatically.
echo.
echo To stop the application, close this window.
echo.
python "AI-IDS-Portable-Web.py"
if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to start. Python 3 might not be installed.
    echo Please install Python 3 from https://python.org
    pause
)
