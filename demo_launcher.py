#!/usr/bin/env python3
"""
Simple launcher for AI Intrusion Detection System Demo
This version doesn't require root privileges and demonstrates the system capabilities.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch the IDS demo"""
    print("🛡️  AI Intrusion Detection System - Demo Launcher")
    print("=" * 60)
    
    # Get project root directory
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    venv_python = project_root / ".venv" / "bin" / "python"
    
    # Check if virtual environment exists
    if not venv_python.exists():
        print("❌ Virtual environment not found.")
        print("Please run the installation first:")
        print("   ./install.sh")
        return 1
    
    # Check if we're in the right directory
    if not src_dir.exists():
        print("❌ Source directory not found.")
        print("Please run this script from the project root directory.")
        return 1
    
    print("📦 Starting IDS Demo (no root privileges required)")
    print("🌐 Dashboard will be available at: http://localhost:8080")
    print("📊 Simulated network traffic will be processed and analyzed")
    print("🚨 Security threats will be detected and displayed")
    print("\nPress Ctrl+C to stop the demo")
    print("=" * 60)
    
    try:
        # Change to src directory and run demo
        os.chdir(src_dir)
        subprocess.run([str(venv_python), "demo.py"])
        
    except KeyboardInterrupt:
        print("\n✅ Demo stopped by user")
        return 0
    except FileNotFoundError:
        print("❌ Python virtual environment not found")
        print("Please run: ./install.sh")
        return 1
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
