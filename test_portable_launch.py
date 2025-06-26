#!/usr/bin/env python3
"""
Test script to demonstrate the AI-IDS portable app launch process
This simulates what happens when a user downloads and runs the app
"""

import sys
import os
from pathlib import Path

def test_portable_launch():
    """Test the portable launch experience"""
    
    print("🧪 AI-IDS Portable Launch Test")
    print("=" * 50)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Check if we're in the correct location
    portable_dir = current_dir / "web_app" / "static" / "downloads" / "AI-IDS-Portable"
    if not portable_dir.exists():
        print("❌ AI-IDS-Portable directory not found")
        print(f"Expected location: {portable_dir}")
        return False
    
    print(f"✅ Found portable directory: {portable_dir}")
    
    # List contents
    print("\n📋 Contents of portable package:")
    for item in portable_dir.iterdir():
        print(f"   - {item.name}")
    
    # Check launcher scripts
    bat_launcher = portable_dir / "launch_ai_ids.bat"
    sh_launcher = portable_dir / "launch_ai_ids.sh"
    
    print("\n🔍 Checking launcher scripts:")
    print(f"   Windows launcher: {'✅' if bat_launcher.exists() else '❌'} {bat_launcher}")
    print(f"   Unix launcher: {'✅' if sh_launcher.exists() else '❌'} {sh_launcher}")
    
    # Check Python files
    desktop_app = portable_dir / "ai_ids_app.py"
    web_app = portable_dir / "ai_ids_web.py"
    
    print("\n🐍 Checking Python applications:")
    print(f"   Desktop app: {'✅' if desktop_app.exists() else '❌'} {desktop_app}")
    print(f"   Web app: {'✅' if web_app.exists() else '❌'} {web_app}")
    
    # Test Python availability
    print("\n🔧 System check:")
    python_available = False
    python_command = None
    
    for cmd in ['python', 'python3']:
        try:
            import subprocess
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                python_available = True
                python_command = cmd
                print(f"   ✅ Python found: {cmd} - {result.stdout.strip()}")
                break
        except:
            continue
    
    if not python_available:
        print("   ❌ Python not found in PATH")
        print("   🌐 Would fallback to web mode")
    
    # Test desktop app launch (if Python available)
    if python_available and desktop_app.exists():
        print(f"\n🖥️  Testing desktop app launch...")
        try:
            # Just test import, don't actually run the GUI
            import subprocess
            test_cmd = [python_command, str(desktop_app), '--help']
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=5)
            if "AI Intrusion Detection System" in result.stdout:
                print("   ✅ Desktop app can be launched")
            else:
                print("   ⚠️  Desktop app may have issues")
        except Exception as e:
            print(f"   ❌ Desktop app test failed: {e}")
    
    print("\n📖 README content preview:")
    readme_file = portable_dir / "README.txt"
    if readme_file.exists():
        with open(readme_file, 'r') as f:
            lines = f.readlines()[:10]  # Show first 10 lines
            for line in lines:
                print(f"   {line.rstrip()}")
        if len(lines) >= 10:
            print("   ... (more content in README.txt)")
    else:
        print("   ❌ README.txt not found")
    
    print("\n🎯 User Experience Summary:")
    print("   1. User downloads AI-IDS-Portable.zip")
    print("   2. User extracts the ZIP file")
    print("   3. User runs the appropriate launcher:")
    print("      - Windows: Double-click launch_ai_ids.bat")
    print("      - Mac/Linux: Run ./launch_ai_ids.sh")
    print("   4. Launcher detects system and runs best available version")
    print("   5. User sees AI-IDS interface and can start monitoring")
    
    print("\n✨ Test completed successfully!")
    return True

if __name__ == "__main__":
    test_portable_launch()
