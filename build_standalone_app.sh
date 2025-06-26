#!/bin/bash

# AI-IDS Desktop App Builder
# Creates standalone executable packages for distribution

echo "🛡️ Building AI Intrusion Detection System Desktop Application"
echo "================================================================"

# Create build directory
mkdir -p build/packages
cd build

echo "📦 Creating standalone executable..."

# Build executable with PyInstaller
pyinstaller \
    --onefile \
    --windowed \
    --name "AI-IDS-Desktop" \
    --icon=../src/icon.ico \
    --add-data "../models:models" \
    --add-data "../data:data" \
    --hidden-import tkinter \
    --hidden-import PIL \
    --hidden-import pystray \
    ../standalone_ids_app.py

if [ $? -eq 0 ]; then
    echo "✅ Executable built successfully!"
    
    # Create distribution packages
    echo "📦 Creating distribution packages..."
    
    # Linux package
    echo "Creating Linux package..."
    mkdir -p packages/AI-IDS-Linux
    cp dist/AI-IDS-Desktop packages/AI-IDS-Linux/
    cp ../README.md packages/AI-IDS-Linux/
    cp ../requirements.txt packages/AI-IDS-Linux/
    
    # Create launcher script
    cat > packages/AI-IDS-Linux/launch.sh << 'EOF'
#!/bin/bash
echo "🛡️ Starting AI Intrusion Detection System..."
cd "$(dirname "$0")"
./AI-IDS-Desktop
EOF
    chmod +x packages/AI-IDS-Linux/launch.sh
    
    # Create installation guide
    cat > packages/AI-IDS-Linux/INSTALL.txt << 'EOF'
AI Intrusion Detection System - Installation Guide

QUICK START:
1. Extract this package to your desired location
2. Run: ./launch.sh
3. Grant permissions when prompted
4. Enjoy real-time network protection!

FEATURES:
- Real-time network monitoring
- AI-powered threat detection (92% accuracy)
- System tray integration
- Easy on/off controls
- Live statistics dashboard
- Configurable detection sensitivity

REQUIREMENTS:
- Linux with GUI desktop environment
- 2GB RAM minimum
- Network access
- Administrator privileges for full functionality

SUPPORT:
For help and documentation, visit:
https://github.com/sgcoder123/AI-Intrusion-Detection-System
EOF
    
    # Package Linux version
    cd packages
    tar -czf AI-IDS-1.0.0-linux.tar.gz AI-IDS-Linux/
    echo "✅ Linux package created: AI-IDS-1.0.0-linux.tar.gz"
    
    # Create AppImage version (simplified)
    mkdir -p AI-IDS.AppDir/usr/bin
    cp AI-IDS-Linux/AI-IDS-Desktop AI-IDS.AppDir/usr/bin/
    
    cat > AI-IDS.AppDir/AppRun << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/usr/bin"
./AI-IDS-Desktop
EOF
    chmod +x AI-IDS.AppDir/AppRun
    
    cat > AI-IDS.AppDir/ai-ids.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=AI Intrusion Detection System
Exec=AppRun
Icon=ai-ids
Comment=Real-time network threat detection
Categories=Security;Network;
EOF
    
    # Create simple icon (text-based)
    cat > AI-IDS.AppDir/ai-ids.png << 'EOF'
# Simple placeholder icon - would be replaced with actual icon file
EOF
    
    echo "✅ AppImage structure created"
    
    cd ..
    
    # Calculate file sizes
    linux_size=$(du -h packages/AI-IDS-1.0.0-linux.tar.gz | cut -f1)
    
    echo ""
    echo "📊 Build Summary:"
    echo "=================="
    echo "✅ Executable: dist/AI-IDS-Desktop"
    echo "✅ Linux Package: packages/AI-IDS-1.0.0-linux.tar.gz ($linux_size)"
    echo "✅ AppImage Ready: packages/AI-IDS.AppDir/"
    echo ""
    echo "🚀 Ready for distribution!"
    echo ""
    echo "To test the executable:"
    echo "  ./dist/AI-IDS-Desktop"
    echo ""
    echo "To test the Linux package:"
    echo "  cd packages && tar -xzf AI-IDS-1.0.0-linux.tar.gz"
    echo "  cd AI-IDS-Linux && ./launch.sh"
    
else
    echo "❌ Build failed!"
    exit 1
fi
