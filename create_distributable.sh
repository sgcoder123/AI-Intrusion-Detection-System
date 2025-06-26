#!/bin/bash

# Simple AI-IDS Package Creator
# Creates a distributable package that users can download and run

echo "🛡️ Creating AI-IDS Distributable Package"
echo "=========================================="

# Create package directory
mkdir -p ai-ids-package
cd ai-ids-package

# Copy the standalone app
cp ../standalone_ids_app.py ./ai_ids_app.py

# Create requirements file
cat > requirements.txt << 'EOF'
tkinter
pillow>=8.0.0
pystray>=0.19.0
EOF

# Create launcher script for Linux/Mac
cat > launch.sh << 'EOF'
#!/bin/bash
echo "🛡️ Starting AI Intrusion Detection System..."
echo "Checking Python installation..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ and try again."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not available. Please install pip and try again."
    exit 1
fi

echo "✅ Python found. Installing dependencies..."

# Install requirements
pip3 install -r requirements.txt --user

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo "🚀 Starting AI-IDS..."
    python3 ai_ids_app.py
else
    echo "❌ Failed to install dependencies. Please check your internet connection."
    exit 1
fi
EOF

# Create launcher script for Windows
cat > launch.bat << 'EOF'
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
EOF

# Create README
cat > README.txt << 'EOF'
🛡️ AI Intrusion Detection System - Desktop Application
======================================================

WHAT IS THIS?
This is a real-time network intrusion detection system powered by AI.
It monitors your network traffic and alerts you to potential security threats.

FEATURES:
✅ Real-time network monitoring
✅ AI-powered threat detection (92% accuracy)  
✅ Easy on/off controls
✅ System tray integration
✅ Live statistics dashboard
✅ Configurable detection sensitivity
✅ Cross-platform support (Windows, macOS, Linux)

QUICK START:
1. For Windows: Double-click "launch.bat"
2. For Linux/Mac: Run "./launch.sh" in terminal
3. Grant permissions when prompted
4. Click "Start Protection" to begin monitoring
5. View live stats and threats in the application window

SYSTEM REQUIREMENTS:
- Python 3.7 or higher
- 2GB RAM minimum
- Network access for threat detection
- Administrator privileges recommended

USAGE:
- The application will start with a simple GUI interface
- Click "Start Protection" to begin monitoring network traffic
- The system will analyze packets in real-time and detect threats
- Adjust sensitivity slider to control detection thresholds
- Enable "Start with system" for automatic protection
- Access web dashboard for detailed statistics

THREAT DETECTION:
The system detects various types of network attacks including:
- Port scans and network reconnaissance
- Denial of Service (DoS) attacks
- Malware communication attempts
- Suspicious connection patterns
- Brute force attacks
- IP sweeping and probing

PRIVACY & SECURITY:
- No personal data is collected or transmitted
- All processing happens locally on your machine
- Only network metadata is analyzed (no content)
- Configuration is stored locally in your home directory

SUPPORT:
For help, documentation, and updates:
GitHub: https://github.com/sgcoder123/AI-Intrusion-Detection-System

TROUBLESHOOTING:
- If Python is not found, install Python 3.7+ from python.org
- If dependencies fail to install, check your internet connection
- If you get permission errors, run as administrator
- For GUI issues, ensure you have a desktop environment

Enjoy secure computing! 🛡️
EOF

# Create version info
cat > VERSION.txt << 'EOF'
AI-IDS Desktop Application v1.0.0
Build Date: June 26, 2025
Python Requirements: 3.7+
License: MIT
EOF

chmod +x launch.sh

cd ..

# Create ZIP package
echo "📦 Creating downloadable package..."
zip -r AI-IDS-Desktop-v1.0.0.zip ai-ids-package/

# Create TAR.GZ for Linux
tar -czf AI-IDS-Desktop-v1.0.0.tar.gz ai-ids-package/

echo "✅ Packages created successfully!"
echo ""
echo "📦 Distribution packages:"
echo "   - AI-IDS-Desktop-v1.0.0.zip (Windows/Universal)"
echo "   - AI-IDS-Desktop-v1.0.0.tar.gz (Linux/Unix)"
echo ""
echo "Package contents:"
ls -la ai-ids-package/
echo ""
echo "Package sizes:"
ls -lh AI-IDS-Desktop-v1.0.0.*
echo ""
echo "🚀 Ready for web distribution!"
