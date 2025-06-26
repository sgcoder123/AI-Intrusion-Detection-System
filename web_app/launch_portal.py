#!/usr/bin/env python3
"""
Launcher for AI IDS Download Portal Web Application
"""

import sys
import os
import subprocess
from pathlib import Path

def install_requirements():
    """Install web app requirements"""
    try:
        # Get the virtual environment Python
        project_root = Path(__file__).parent.parent
        venv_python = project_root / ".venv" / "bin" / "python"
        
        if not venv_python.exists():
            print("❌ Virtual environment not found. Please run the main installation first:")
            print("   ./install.sh")
            return False
        
        # Install web app requirements
        web_app_dir = Path(__file__).parent
        requirements_file = web_app_dir / "requirements.txt"
        
        if requirements_file.exists():
            print("📦 Installing web application dependencies...")
            subprocess.check_call([
                str(venv_python), "-m", "pip", "install", "-r", str(requirements_file)
            ])
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def main():
    """Launch the web application"""
    print("🌐 AI IDS Download Portal")
    print("=" * 40)
    
    # Install requirements
    if not install_requirements():
        return 1
    
    # Get paths
    project_root = Path(__file__).parent.parent
    venv_python = project_root / ".venv" / "bin" / "python"
    web_app_dir = Path(__file__).parent
    app_file = web_app_dir / "app.py"
    
    # Change to web app directory
    os.chdir(web_app_dir)
    
    print("🚀 Starting web application...")
    print("📊 Download portal will be available at: http://localhost:5000")
    print("📁 Users can download the IDS system from the web interface")
    print("\nPress Ctrl+C to stop the web application")
    print("=" * 40)
    
    try:
        # Run the web application
        subprocess.run([str(venv_python), str(app_file)])
        
    except KeyboardInterrupt:
        print("\n✅ Web application stopped")
        return 0
    except FileNotFoundError:
        print("❌ Python virtual environment not found")
        print("Please run the main installation: ./install.sh")
        return 1
    except Exception as e:
        print(f"❌ Error running web application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
