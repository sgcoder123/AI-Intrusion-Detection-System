#!/usr/bin/env python3
"""
Simple build script for AI-IDS standalone executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_standalone_app():
    """Build standalone AI-IDS executable"""
    
    project_root = Path(__file__).parent
    print(f"🏠 Project root: {project_root}")
    
    # Clean previous builds
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    
    if dist_dir.exists():
        print("🧹 Cleaning dist directory...")
        shutil.rmtree(dist_dir)
    
    if build_dir.exists():
        print("🧹 Cleaning build directory...")
        shutil.rmtree(build_dir)
    
    # Create output directory
    output_dir = project_root / "web_app" / "static" / "downloads"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔨 Building standalone executable...")
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # Create a single executable file
        "--windowed",  # No console window (GUI app)
        "--name", "AI-IDS-Desktop",
        "--clean",
        "--noconfirm",
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "minimal_ids_app_clean.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode != 0:
        print("❌ Build failed!")
        return False
    
    # Check if executable was created
    exe_name = "AI-IDS-Desktop.exe" if sys.platform == "win32" else "AI-IDS-Desktop"
    exe_path = dist_dir / exe_name
    
    if not exe_path.exists():
        print(f"❌ Executable not found at: {exe_path}")
        return False
    
    print(f"✅ Executable created: {exe_path}")
    
    # Get file size
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"📏 Executable size: {size_mb:.1f} MB")
    
    # Copy to downloads directory
    target_path = output_dir / exe_name
    shutil.copy2(exe_path, target_path)
    print(f"📦 Executable copied to downloads: {target_path}")
    
    # Create README
    readme_content = f"""# AI Intrusion Detection System - Standalone Desktop App

## What is this?
This is a completely standalone version of the AI Intrusion Detection System that requires **NO Python installation** or technical setup.

## How to run:
1. Download `{exe_name}`
2. Double-click the file to start the application
3. The AI-IDS desktop app will open with a simple interface
4. Click "Start Protection" to begin monitoring for network threats
5. Click "Stop Protection" to pause monitoring

## Features:
- ✅ Live network threat detection using AI algorithms
- ✅ Simple on/off toggle interface  
- ✅ Real-time threat counter and statistics
- ✅ Adjustable sensitivity settings
- ✅ Activity logging and alerts
- ✅ No Python or technical knowledge required
- ✅ Works completely offline in demo mode

## System Requirements:
- Windows 10/11, macOS 10.12+, or Linux (Ubuntu 18.04+)
- {size_mb:.0f}MB disk space
- Internet connection for live monitoring (optional for demo mode)

## Troubleshooting:
- If the app doesn't start, try running as administrator (Windows) or with `chmod +x` (Linux/macOS)
- On macOS, you may need to allow the app in Security & Privacy settings
- The app runs in demo mode with simulated network data for demonstration purposes

## About:
This AI-powered intrusion detection system provides a user-friendly interface for network security monitoring. The application demonstrates threat detection capabilities and provides real-time statistics.

Built with ❤️ for cybersecurity education and demonstration.

**Note:** This is a demonstration application. For production use, please use the full AI-IDS system with trained models.
"""
    
    readme_path = output_dir / f"AI-IDS-Desktop-README.txt"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"📄 README created: {readme_path}")
    
    print("\n🎉 Standalone executable build completed successfully!")
    print(f"📁 Files in downloads directory:")
    for file in output_dir.glob("AI-IDS-Desktop*"):
        print(f"   - {file.name}")
    
    return True

if __name__ == "__main__":
    success = build_standalone_app()
    sys.exit(0 if success else 1)
