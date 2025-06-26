@echo off
REM Build script for AI-IDS Desktop App on Windows
REM Requires Python 3.7+ and pip

echo 🛡️ AI-IDS Desktop App Build Script (Windows)
echo ===============================================

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Create build directory
if not exist "build" mkdir build
if not exist "dist" mkdir dist

echo 📦 Installing dependencies...

REM Upgrade pip
python -m pip install --upgrade pip

REM Install build tools
python -m pip install pyinstaller wheel setuptools

REM Install app dependencies
python -m pip install -r requirements.txt

REM Windows-specific dependencies
python -m pip install pywin32

echo ✅ Dependencies installed

echo 🎨 Creating application icon...

REM Create icon using Python
python -c "
try:
    from PIL import Image, ImageDraw, ImageFont
    
    # Create 256x256 icon
    icon = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw shield
    shield_color = (52, 152, 219, 255)
    draw.ellipse([20, 20, 236, 236], fill=shield_color)
    
    # Draw 'AI' text
    try:
        font = ImageFont.truetype('arial.ttf', 80)
    except:
        font = ImageFont.load_default()
    
    text = 'AI'
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (256 - text_width) // 2
    y = (256 - text_height) // 2 - 10
    
    draw.text((x, y), text, fill='white', font=font)
    
    # Save icon
    icon.save('build/app_icon.png')
    icon.save('build/app_icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    
    print('✅ Icon created')
    
except ImportError:
    print('⚠️ PIL not available, creating placeholder')
    with open('build/app_icon.ico', 'w') as f:
        pass
"

echo 🔨 Building executable...

REM Build with PyInstaller
python -m PyInstaller ^
    --clean ^
    --onedir ^
    --windowed ^
    --name "AI-IDS" ^
    --icon "build/app_icon.ico" ^
    --add-data "src;src" ^
    --add-data "models;models" ^
    --add-data "requirements.txt;." ^
    --hidden-import sklearn ^
    --hidden-import pandas ^
    --hidden-import numpy ^
    --hidden-import joblib ^
    --hidden-import scapy ^
    --hidden-import flask ^
    --hidden-import threading ^
    --hidden-import tkinter ^
    --hidden-import pystray ^
    --hidden-import PIL ^
    --hidden-import winreg ^
    desktop_app/ids_desktop_app.py

if errorlevel 1 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo ✅ Executable built

echo 📦 Creating Windows package...

REM Create ZIP package
cd build
powershell -Command "Compress-Archive -Path '../dist/AI-IDS' -DestinationPath '../dist/AI-IDS-1.0.0-windows.zip' -Force"
cd ..

echo 🔧 Creating installer script...

REM Create simple installer
echo @echo off > dist/install.bat
echo echo 🛡️ AI-IDS Desktop App Installer >> dist/install.bat
echo echo ================================= >> dist/install.bat
echo echo. >> dist/install.bat
echo echo 📥 Extract AI-IDS-1.0.0-windows.zip >> dist/install.bat
echo echo 🏃 Run AI-IDS.exe >> dist/install.bat
echo echo. >> dist/install.bat
echo echo ✨ Features: >> dist/install.bat
echo echo • Real-time network monitoring >> dist/install.bat
echo echo • AI threat detection >> dist/install.bat
echo echo • System tray integration >> dist/install.bat
echo echo • Auto-start capability >> dist/install.bat
echo echo • Web dashboard >> dist/install.bat
echo echo. >> dist/install.bat
echo echo 🔗 After installation: >> dist/install.bat
echo echo • Grant admin permissions when prompted >> dist/install.bat
echo echo • Check system tray for AI-IDS icon >> dist/install.bat
echo echo • Right-click for options >> dist/install.bat
echo echo • Enable 'Start with system' in settings >> dist/install.bat
echo echo • Access dashboard at http://localhost:8080 >> dist/install.bat
echo pause >> dist/install.bat

REM Create README
echo AI-IDS Desktop App v1.0.0 > dist/README.txt
echo ============================== >> dist/README.txt
echo. >> dist/README.txt
echo Installation: >> dist/README.txt
echo 1. Extract AI-IDS-1.0.0-windows.zip >> dist/README.txt
echo 2. Run AI-IDS.exe >> dist/README.txt
echo 3. Grant administrator permissions >> dist/README.txt
echo 4. App starts minimized in system tray >> dist/README.txt
echo. >> dist/README.txt
echo Features: >> dist/README.txt
echo • Real-time network monitoring >> dist/README.txt
echo • AI-powered threat detection >> dist/README.txt
echo • Web dashboard interface >> dist/README.txt
echo • System tray integration >> dist/README.txt
echo • Auto-start with Windows >> dist/README.txt
echo. >> dist/README.txt
echo Usage: >> dist/README.txt
echo • Right-click tray icon for controls >> dist/README.txt
echo • Open dashboard to view statistics >> dist/README.txt
echo • Configure auto-start in settings >> dist/README.txt
echo • View logs and alerts in GUI >> dist/README.txt

echo 🎉 Build completed successfully!
echo.
echo 📦 Packages created in ./dist/
dir dist

echo.
echo 🚀 To distribute:
echo 1. Share AI-IDS-1.0.0-windows.zip
echo 2. Users extract and run AI-IDS.exe
echo 3. App will start in system tray

pause
