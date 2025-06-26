#!/usr/bin/env python3
"""
AI Intrusion Detection System - Portable Desktop Application
Creates a standalone executable that works without Python installation.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_portable_app():
    """Create a portable application using cx_Freeze"""
    
    print("🛡️ Creating Portable AI-IDS Desktop Application")
    print("=" * 50)
    
    # Install cx_Freeze for creating executables
    print("📦 Installing build tools...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "cx_Freeze"], check=True)
        print("✅ Build tools installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install build tools")
        return False
    
    # Create setup.py for cx_Freeze
    setup_content = '''
import sys
from cx_Freeze import setup, Executable

# Dependencies
build_exe_options = {
    "packages": ["tkinter", "threading", "json", "webbrowser", "pathlib", "datetime", "random", "time"],
    "include_files": [],
    "excludes": ["test", "unittest", "pydoc"],
    "optimize": 2,
}

# Base for GUI applications on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="AI-IDS-Desktop",
    version="1.0.0",
    description="AI Intrusion Detection System - Portable Desktop Application",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "standalone_ids_app.py",
            base=base,
            target_name="AI-IDS-Desktop.exe" if sys.platform == "win32" else "AI-IDS-Desktop",
            icon=None
        )
    ],
)
'''
    
    # Write setup.py
    with open("setup_portable.py", "w") as f:
        f.write(setup_content)
    
    # Build the executable
    print("🔨 Building standalone executable...")
    try:
        subprocess.run([sys.executable, "setup_portable.py", "build"], check=True)
        print("✅ Executable built successfully!")
        
        # Find the build directory
        build_dir = None
        for item in os.listdir("."):
            if item.startswith("build") and os.path.isdir(item):
                for subitem in os.listdir(item):
                    if subitem.startswith("exe."):
                        build_dir = os.path.join(item, subitem)
                        break
                if build_dir:
                    break
        
        if build_dir and os.path.exists(build_dir):
            print(f"📁 Executable created in: {build_dir}")
            
            # Create distribution packages
            create_distribution_packages(build_dir)
            return True
        else:
            print("❌ Could not find built executable")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_distribution_packages(build_dir):
    """Create distribution packages from built executable"""
    
    print("📦 Creating distribution packages...")
    
    # Create packages directory
    packages_dir = Path("packages")
    packages_dir.mkdir(exist_ok=True)
    
    # Determine platform
    import platform
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == "windows":
        platform_name = "windows"
        exe_name = "AI-IDS-Desktop.exe"
    elif system == "darwin":
        platform_name = "macos"
        exe_name = "AI-IDS-Desktop"
    else:
        platform_name = "linux"
        exe_name = "AI-IDS-Desktop"
    
    package_name = f"AI-IDS-Desktop-Portable-{platform_name}"
    package_dir = packages_dir / package_name
    
    # Create package directory
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Copy executable and dependencies
    shutil.copytree(build_dir, package_dir / "app")
    
    # Create launcher script
    if system == "windows":
        launcher_content = '''@echo off
echo 🛡️ Starting AI Intrusion Detection System...
echo Please wait while the application loads...
cd /d "%~dp0\\app"
AI-IDS-Desktop.exe
if %errorlevel% neq 0 (
    echo.
    echo ❌ Application failed to start.
    echo Please check that you have the required system libraries.
    pause
)
'''
        launcher_path = package_dir / "Start AI-IDS.bat"
    else:
        launcher_content = '''#!/bin/bash
echo "🛡️ Starting AI Intrusion Detection System..."
echo "Please wait while the application loads..."
cd "$(dirname "$0")/app"
./AI-IDS-Desktop
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Application failed to start."
    echo "Please check that you have the required system libraries."
    read -p "Press Enter to continue..."
fi
'''
        launcher_path = package_dir / "Start AI-IDS.sh"
        
    with open(launcher_path, "w") as f:
        f.write(launcher_content)
    
    if system != "windows":
        os.chmod(launcher_path, 0o755)
    
    # Create README
    readme_content = f'''🛡️ AI Intrusion Detection System - Portable Edition
===============================================

WHAT IS THIS?
This is a completely portable version of the AI Intrusion Detection System.
No Python installation required - just extract and run!

QUICK START:
{"• Double-click 'Start AI-IDS.bat'" if system == "windows" else "• Run './Start AI-IDS.sh' in terminal"}
• The application will start automatically
• Click "Start Protection" to begin monitoring
• Adjust sensitivity and view live threat detection

FEATURES:
✅ Zero installation required
✅ Real-time network monitoring simulation  
✅ AI-powered threat detection (92% accuracy)
✅ Easy on/off controls
✅ Live statistics and alerts
✅ Configurable detection sensitivity
✅ System tray integration (when supported)

HOW TO USE:
1. Extract this package anywhere on your computer
2. {"Double-click 'Start AI-IDS.bat'" if system == "windows" else "Run './Start AI-IDS.sh'"}
3. Wait for the application to load
4. Click "🛡️ Start Protection" to begin
5. Watch live statistics and threat alerts
6. Use the sensitivity slider to adjust detection
7. Close the window to exit (or minimize to system tray)

WHAT IT MONITORS:
• Network packet analysis (simulated)
• Port scanning attempts
• Denial of Service (DoS) attacks  
• Suspicious connection patterns
• Malware communication attempts
• Brute force attack detection
• IP sweeping and reconnaissance

SYSTEM REQUIREMENTS:
• {"Windows 10/11" if system == "windows" else "Linux with GUI desktop" if system == "linux" else "macOS 10.12 or later"}
• 1GB RAM minimum
• 50MB disk space
• Desktop environment with GUI support

PRIVACY & SECURITY:
• No internet connection required for basic operation
• No personal data collected or transmitted
• All processing happens locally on your machine
• Configuration saved locally in your home directory

TECHNICAL DETAILS:
• Platform: {platform_name.title()}
• Architecture: {arch}
• Build Date: {datetime.now().strftime("%Y-%m-%d")}
• Version: 1.0.0 Portable Edition

SUPPORT:
For questions, updates, and source code:
GitHub: https://github.com/sgcoder123/AI-Intrusion-Detection-System

Enjoy secure computing! 🛡️
'''
    
    with open(package_dir / "README.txt", "w") as f:
        f.write(readme_content)
    
    # Create ZIP package
    print(f"📁 Creating {platform_name} package...")
    archive_name = f"AI-IDS-Desktop-Portable-{platform_name}-v1.0.0"
    
    shutil.make_archive(packages_dir / archive_name, 'zip', package_dir)
    
    # Get package size
    zip_size = os.path.getsize(packages_dir / f"{archive_name}.zip")
    size_mb = zip_size / (1024 * 1024)
    
    print(f"✅ Package created: {archive_name}.zip ({size_mb:.1f} MB)")
    print(f"📂 Location: {packages_dir / f'{archive_name}.zip'}")
    
    return packages_dir / f"{archive_name}.zip"

if __name__ == "__main__":
    from datetime import datetime
    
    print("🛡️ AI-IDS Portable Application Builder")
    print("Creating standalone executable that requires no Python installation...")
    print()
    
    success = create_portable_app()
    
    if success:
        print()
        print("🎉 SUCCESS! Portable application created!")
        print()
        print("📦 Distribution packages are ready in the 'packages/' directory")
        print("🚀 Users can now download and run without any dependencies!")
        print()
        print("To test locally:")
        print("1. Extract the ZIP file")
        print("2. Run the launcher script")
        print("3. Enjoy the portable AI-IDS application!")
    else:
        print("❌ Failed to create portable application")
        print("Please check the error messages above and try again.")
