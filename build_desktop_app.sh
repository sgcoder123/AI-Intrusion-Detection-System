#!/bin/bash
# Build script for AI-IDS Desktop App
# Supports Linux, macOS, and Windows (via WSL/MSYS2)

set -e

echo "🛡️ AI-IDS Desktop App Build Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect platform
PLATFORM=$(uname -s)
ARCH=$(uname -m)

echo -e "${BLUE}Platform: $PLATFORM $ARCH${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python dependencies
install_dependencies() {
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    
    # Upgrade pip
    python3 -m pip install --upgrade pip
    
    # Install build dependencies
    python3 -m pip install pyinstaller wheel setuptools
    
    # Install app dependencies
    python3 -m pip install -r requirements.txt
    
    # Platform-specific dependencies
    if [[ "$PLATFORM" == "Darwin" ]]; then
        python3 -m pip install py2app
    elif [[ "$PLATFORM" == "Linux" ]]; then
        python3 -m pip install AppImage-builder 2>/dev/null || echo "AppImage-builder not available"
    fi
    
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Function to build executable
build_executable() {
    echo -e "${YELLOW}🔨 Building executable...${NC}"
    
    cd "$(dirname "$0")"
    
    # Create build directory
    mkdir -p build/dist
    
    # Run PyInstaller
    python3 -m PyInstaller \
        --clean \
        --onedir \
        --windowed \
        --name "AI-IDS" \
        --add-data "src:src" \
        --add-data "models:models" \
        --add-data "requirements.txt:." \
        --hidden-import sklearn \
        --hidden-import pandas \
        --hidden-import numpy \
        --hidden-import joblib \
        --hidden-import scapy \
        --hidden-import flask \
        --hidden-import threading \
        --hidden-import tkinter \
        --hidden-import pystray \
        --hidden-import PIL \
        desktop_app/ids_desktop_app.py
    
    echo -e "${GREEN}✅ Executable built${NC}"
}

# Function to create app icon
create_icon() {
    echo -e "${YELLOW}🎨 Creating application icon...${NC}"
    
    python3 -c "
import sys
sys.path.append('desktop_app')
try:
    from PIL import Image, ImageDraw, ImageFont
    
    # Create 512x512 icon
    icon = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw shield background
    shield_color = (52, 152, 219, 255)  # Blue
    draw.ellipse([50, 50, 462, 462], fill=shield_color)
    
    # Draw inner shield
    inner_color = (41, 128, 185, 255)  # Darker blue
    draw.ellipse([80, 80, 432, 432], fill=inner_color)
    
    # Draw 'AI' text
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 120)
    except:
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 120)
        except:
            font = ImageFont.load_default()
    
    text = 'AI'
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (512 - text_width) // 2
    y = (512 - text_height) // 2 - 20
    
    draw.text((x, y), text, fill='white', font=font)
    
    # Add 'IDS' subtitle
    try:
        small_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 40)
    except:
        try:
            small_font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 40)
        except:
            small_font = ImageFont.load_default()
    
    subtitle = 'IDS'
    bbox = draw.textbbox((0, 0), subtitle, font=small_font)
    sub_width = bbox[2] - bbox[0]
    sub_x = (512 - sub_width) // 2
    sub_y = y + text_height + 10
    
    draw.text((sub_x, sub_y), subtitle, fill='white', font=small_font)
    
    # Save icon in multiple formats
    icon.save('build/app_icon.png')
    
    # Create ICO for Windows
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icon.save('build/app_icon.ico', format='ICO', sizes=sizes)
    
    # Create ICNS for macOS
    icon.save('build/app_icon.icns', format='ICNS')
    
    print('✅ Icon created successfully')
    
except ImportError:
    print('⚠️ PIL not available, using default icon')
    # Create placeholder
    with open('build/app_icon.png', 'w') as f:
        f.write('')
"
    
    echo -e "${GREEN}✅ Icon created${NC}"
}

# Function to create Linux package
create_linux_package() {
    echo -e "${YELLOW}🐧 Creating Linux package...${NC}"
    
    APP_DIR="build/AI-IDS.AppDir"
    mkdir -p "$APP_DIR/usr/bin"
    mkdir -p "$APP_DIR/usr/share/applications"
    mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"
    
    # Copy executable
    cp -r dist/AI-IDS/* "$APP_DIR/usr/bin/"
    
    # Create desktop file
    cat > "$APP_DIR/AI-IDS.desktop" << EOF
[Desktop Entry]
Type=Application
Name=AI Intrusion Detection System
Exec=AI-IDS
Icon=ai-ids
Comment=AI-powered network intrusion detection system
Categories=Security;Network;System;
StartupNotify=true
X-GNOME-Autostart-enabled=true
EOF
    
    # Copy icon
    cp build/app_icon.png "$APP_DIR/usr/share/icons/hicolor/256x256/apps/ai-ids.png"
    cp build/app_icon.png "$APP_DIR/ai-ids.png"
    
    # Create symlinks
    ln -sf usr/bin/AI-IDS "$APP_DIR/AppRun"
    ln -sf AI-IDS.desktop "$APP_DIR/"
    
    # Create tar.gz package
    cd build
    tar -czf "../dist/AI-IDS-1.0.0-linux-$ARCH.tar.gz" AI-IDS.AppDir
    cd ..
    
    # Try to create AppImage if tool is available
    if command_exists appimage-tool; then
        appimage-tool "$APP_DIR" "dist/AI-IDS-1.0.0-linux-$ARCH.AppImage"
    fi
    
    echo -e "${GREEN}✅ Linux package created${NC}"
}

# Function to create macOS package
create_macos_package() {
    echo -e "${YELLOW}🍎 Creating macOS package...${NC}"
    
    APP_NAME="AI-IDS.app"
    APP_DIR="build/$APP_NAME"
    CONTENTS_DIR="$APP_DIR/Contents"
    MACOS_DIR="$CONTENTS_DIR/MacOS"
    RESOURCES_DIR="$CONTENTS_DIR/Resources"
    
    # Create app bundle structure
    mkdir -p "$MACOS_DIR"
    mkdir -p "$RESOURCES_DIR"
    
    # Copy executable
    cp -r dist/AI-IDS/* "$MACOS_DIR/"
    
    # Create Info.plist
    cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>AI-IDS</string>
    <key>CFBundleIdentifier</key>
    <string>com.ai-ids.desktop</string>
    <key>CFBundleName</key>
    <string>AI-IDS</string>
    <key>CFBundleDisplayName</key>
    <string>AI Intrusion Detection System</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>AIFS</string>
    <key>CFBundleIconFile</key>
    <string>app_icon.icns</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
</dict>
</plist>
EOF
    
    # Copy icon
    cp build/app_icon.icns "$RESOURCES_DIR/"
    
    # Make executable
    chmod +x "$MACOS_DIR/AI-IDS"
    
    # Create DMG
    if command_exists hdiutil; then
        hdiutil create -volname "AI-IDS" -srcfolder "$APP_DIR" -ov -format UDZO "dist/AI-IDS-1.0.0-macOS.dmg"
    else
        # Create ZIP as fallback
        cd build
        zip -r "../dist/AI-IDS-1.0.0-macOS.zip" "$APP_NAME"
        cd ..
    fi
    
    echo -e "${GREEN}✅ macOS package created${NC}"
}

# Function to create Windows package
create_windows_package() {
    echo -e "${YELLOW}🪟 Creating Windows package...${NC}"
    
    # Create ZIP package
    cd build
    zip -r "../dist/AI-IDS-1.0.0-windows.zip" dist/AI-IDS
    cd ..
    
    echo -e "${GREEN}✅ Windows package created${NC}"
}

# Function to create installer
create_installer() {
    echo -e "${YELLOW}📦 Creating installer...${NC}"
    
    cat > "dist/install.py" << 'EOF'
#!/usr/bin/env python3
"""
AI-IDS Desktop App Quick Installer
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def main():
    print("🛡️ AI-IDS Desktop App Installer")
    print("=" * 35)
    
    system = platform.system()
    
    if system == "Windows":
        print("📥 Extract AI-IDS-1.0.0-windows.zip")
        print("🏃 Run AI-IDS.exe")
    elif system == "Darwin":
        print("📥 Open AI-IDS-1.0.0-macOS.dmg") 
        print("🏃 Drag AI-IDS.app to Applications")
    else:
        print("📥 Extract AI-IDS-1.0.0-linux.tar.gz")
        print("🏃 Run: ./AI-IDS.AppDir/AppRun")
    
    print("\n✨ Features:")
    print("• Real-time network monitoring")
    print("• AI threat detection")
    print("• System tray integration") 
    print("• Auto-start capability")
    print("• Web dashboard")
    
    print("\n🔗 After installation:")
    print("• Check system tray for AI-IDS icon")
    print("• Right-click for options")
    print("• Enable 'Start with system' in settings")
    print("• Access dashboard at http://localhost:8080")

if __name__ == "__main__":
    main()
EOF
    
    chmod +x "dist/install.py"
    
    echo -e "${GREEN}✅ Installer created${NC}"
}

# Main build process
main() {
    echo -e "${BLUE}Starting build process...${NC}"
    
    # Check Python
    if ! command_exists python3; then
        echo -e "${RED}❌ Python 3 is required${NC}"
        exit 1
    fi
    
    # Install dependencies
    install_dependencies
    
    # Create icon
    create_icon
    
    # Build executable
    build_executable
    
    # Create dist directory
    mkdir -p dist
    
    # Create platform-specific packages
    case "$PLATFORM" in
        "Linux")
            create_linux_package
            ;;
        "Darwin")
            create_macos_package
            ;;
        "MINGW"*|"CYGWIN"*|"MSYS"*)
            create_windows_package
            ;;
        *)
            echo -e "${YELLOW}⚠️ Unknown platform, creating generic package${NC}"
            cd build
            tar -czf "../dist/AI-IDS-1.0.0-generic.tar.gz" dist/AI-IDS
            cd ..
            ;;
    esac
    
    # Create installer
    create_installer
    
    echo -e "${GREEN}🎉 Build completed successfully!${NC}"
    echo -e "${BLUE}Packages created in ./dist/${NC}"
    
    # List created files
    echo -e "${YELLOW}📦 Available packages:${NC}"
    ls -la dist/
}

# Run main function
main "$@"
