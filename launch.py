#!/usr/bin/env python3
"""
Master Launcher for AI Intrusion Detection System
Provides easy access to all system features and components.
"""

import sys
import os
import subprocess
from pathlib import Path

def print_banner():
    """Print system banner"""
    print("🛡️" + "=" * 60 + "🛡️")
    print("     AI INTRUSION DETECTION SYSTEM - MASTER LAUNCHER")
    print("🛡️" + "=" * 60 + "🛡️")
    print()

def print_menu():
    """Print main menu options"""
    print("📋 Available Options:")
    print()
    print("   1. 🖥️  Desktop App      - Cross-platform desktop application")
    print("   2. 🎮 Demo Mode         - Try the system without root privileges")
    print("   3. 🛡️  Live Protection  - Real network monitoring (requires sudo)")
    print("   4. 🌐 Download Portal   - Web portal for distributing the system")
    print("   5. ⚙️  Configuration    - Edit system configuration")
    print("   6. 📚 Documentation     - View documentation and guides")
    print("   7. 🔧 Installation      - Run full system installation")
    print("   8. 🔨 Build & Package   - Build desktop app packages")
    print("   9. ❓ Help & Support    - Get help and troubleshooting info")
    print("  10. 🚪 Exit              - Exit launcher")
    print()

def get_paths():
    """Get important file paths"""
    project_root = Path(__file__).parent
    return {
        'project_root': project_root,
        'src_dir': project_root / 'src',
        'web_app_dir': project_root / 'web_app',
        'venv_python': project_root / '.venv' / 'bin' / 'python',
        'config_file': project_root / 'src' / 'ids_config.yaml'
    }

def check_environment():
    """Check if environment is properly set up"""
    paths = get_paths()
    
    if not paths['venv_python'].exists():
        print("❌ Virtual environment not found!")
        print("   Please run the installation first:")
        print("   ./install.sh")
        return False
    
    if not paths['src_dir'].exists():
        print("❌ Source directory not found!")
        return False
    
    return True

def launch_demo():
    """Launch demo mode"""
    paths = get_paths()
    print("🎮 Starting Demo Mode...")
    print("   - No root privileges required")
    print("   - Simulated network traffic")
    print("   - Web dashboard at: http://localhost:8080")
    print()
    
    try:
        subprocess.run([str(paths['venv_python']), 'demo_launcher.py'])
    except KeyboardInterrupt:
        print("\n✅ Demo stopped")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def launch_live_protection():
    """Launch live protection mode"""
    print("🛡️  Starting Live Protection Mode...")
    print("   ⚠️  This requires root/administrator privileges")
    print("   - Real network packet monitoring")
    print("   - Live threat detection")
    print("   - Web dashboard at: http://localhost:8080")
    print()
    
    confirm = input("Continue with live monitoring? (requires sudo) [y/N]: ")
    if confirm.lower() != 'y':
        return
    
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['start_monitoring.bat'], shell=True)
        else:  # Linux/macOS
            subprocess.run(['sudo', './start_monitoring.sh'])
    except KeyboardInterrupt:
        print("\n✅ Live protection stopped")
    except Exception as e:
        print(f"❌ Live protection failed: {e}")

def launch_download_portal():
    """Launch download portal"""
    paths = get_paths()
    print("🌐 Starting Download Portal...")
    print("   - Web portal at: http://localhost:5000")
    print("   - Users can download the system")
    print("   - Includes documentation and demo")
    print()
    
    try:
        os.chdir(paths['web_app_dir'])
        subprocess.run([str(paths['venv_python']), 'launch_portal.py'])
    except KeyboardInterrupt:
        print("\n✅ Download portal stopped")
    except Exception as e:
        print(f"❌ Download portal failed: {e}")

def edit_configuration():
    """Edit system configuration"""
    paths = get_paths()
    config_file = paths['config_file']
    
    print("⚙️  Configuration Management")
    print(f"   Config file: {config_file}")
    print()
    
    if not config_file.exists():
        print("   Creating default configuration...")
        try:
            os.chdir(paths['src_dir'])
            subprocess.run([
                str(paths['venv_python']), '-c',
                'from config import IDSConfig; IDSConfig().save_config()'
            ])
            print("   ✅ Default configuration created")
        except Exception as e:
            print(f"   ❌ Failed to create config: {e}")
            return
    
    print("   Configuration options:")
    print("   1. View current configuration")
    print("   2. Edit with default editor")
    print("   3. Reset to defaults")
    print("   4. Back to main menu")
    
    choice = input("\n   Your choice [1-4]: ").strip()
    
    if choice == '1':
        try:
            with open(config_file, 'r') as f:
                print("\n" + "=" * 50)
                print(f.read())
                print("=" * 50)
        except Exception as e:
            print(f"❌ Failed to read config: {e}")
    
    elif choice == '2':
        try:
            editor = os.environ.get('EDITOR', 'nano')
            subprocess.run([editor, str(config_file)])
        except Exception as e:
            print(f"❌ Failed to open editor: {e}")
    
    elif choice == '3':
        confirm = input("Reset configuration to defaults? [y/N]: ")
        if confirm.lower() == 'y':
            try:
                os.chdir(paths['src_dir'])
                subprocess.run([
                    str(paths['venv_python']), '-c',
                    'from config import IDSConfig; c = IDSConfig(); c.config = c.DEFAULT_CONFIG.copy(); c.save_config()'
                ])
                print("✅ Configuration reset to defaults")
            except Exception as e:
                print(f"❌ Failed to reset config: {e}")

def show_documentation():
    """Show documentation options"""
    print("📚 Documentation & Guides")
    print()
    print("   Available documentation:")
    print("   1. Main README.md - Complete system overview")
    print("   2. REALTIME_README.md - Real-time monitoring guide")
    print("   3. IMPLEMENTATION_COMPLETE.md - Implementation summary")
    print("   4. web_app/README.md - Download portal guide")
    print("   5. Online documentation via web portal")
    print("   6. Back to main menu")
    
    choice = input("\n   Your choice [1-6]: ").strip()
    
    docs = {
        '1': 'README.md',
        '2': 'REALTIME_README.md', 
        '3': 'IMPLEMENTATION_COMPLETE.md',
        '4': 'web_app/README.md'
    }
    
    if choice in docs:
        doc_file = Path(__file__).parent / docs[choice]
        if doc_file.exists():
            try:
                pager = os.environ.get('PAGER', 'less')
                subprocess.run([pager, str(doc_file)])
            except:
                # Fallback to cat
                subprocess.run(['cat', str(doc_file)])
        else:
            print(f"❌ Documentation file not found: {docs[choice]}")
    
    elif choice == '5':
        print("🌐 Starting documentation portal...")
        launch_download_portal()

def run_installation():
    """Run system installation"""
    install_script = Path(__file__).parent / 'install.sh'
    
    if install_script.exists():
        print("🔧 Running system installation...")
        try:
            subprocess.run(['bash', str(install_script)])
        except Exception as e:
            print(f"❌ Installation failed: {e}")
    else:
        print("❌ Installation script not found: install.sh")

def show_help():
    """Show help and support information"""
    print("❓ Help & Support")
    print()
    print("📋 Quick Troubleshooting:")
    print("   • Virtual environment issues: Run ./install.sh")
    print("   • Permission errors: Use sudo for live monitoring")
    print("   • Port conflicts: Check if ports 8080/5000 are free")
    print("   • Model loading errors: Verify models/ directory exists")
    print()
    print("📁 Important Files:")
    print("   • Configuration: src/ids_config.yaml")
    print("   • Logs: intrusion_detection.log")
    print("   • Alerts: security_alerts.json")
    print()
    print("🔧 Common Commands:")
    print("   • Check status: python3 src/ids_main.py --status")
    print("   • Test model: python3 src/deploy_model.py")
    print("   • List interfaces: ip link show (Linux)")
    print()
    print("🌐 Web Interfaces:")
    print("   • Monitoring Dashboard: http://localhost:8080")
    print("   • Download Portal: http://localhost:5000")
    print()
    print("📚 For more help, see the documentation or visit the web portal.")

def launch_desktop_app():
    """Launch desktop application"""
    paths = get_paths()
    print("🖥️ Starting Desktop Application...")
    print("   - Cross-platform AI-IDS desktop app")
    print("   - System tray integration")
    print("   - Real-time monitoring and dashboard")
    print("   - Auto-start capability")
    print()
    
    try:
        desktop_app_path = paths['project_root'] / 'desktop_app' / 'ids_desktop_app.py'
        if desktop_app_path.exists():
            subprocess.run([str(paths['venv_python']), str(desktop_app_path)])
        else:
            print("❌ Desktop app not found!")
            print("   Try building it first with option 8")
    except KeyboardInterrupt:
        print("\n✅ Desktop app stopped")
    except Exception as e:
        print(f"❌ Desktop app failed: {e}")
        print("   This might be due to missing display in headless environment")
        print("   Try the build option instead")

def main():
    """Main launcher function"""
    print_banner()
    
    if not check_environment():
        print("\n🔧 Would you like to run the installation now? [y/N]: ", end="")
        if input().lower() == 'y':
            run_installation()
        return
    
    while True:
        print_menu()
        choice = input("Select an option [1-10]: ").strip()
        print()
        
        if choice == '1':
            launch_desktop_app()
        elif choice == '2':
            launch_demo()
        elif choice == '3':
            launch_live_protection()
        elif choice == '4':
            launch_download_portal()
        elif choice == '5':
            edit_configuration()
        elif choice == '6':
            show_documentation()
        elif choice == '7':
            run_installation()
        elif choice == '8':
            paths = get_paths()
            print("🔨 Building and packaging the desktop app...")
            print("   1. Test desktop app components")
            print("   2. Build executable packages")
            print("   3. Package for distribution")
            print("   4. Install as system service")
            print("   5. Back to main menu")
            
            build_choice = input("\n   Build option [1-5]: ").strip()
            
            if build_choice == '1':
                print("🧪 Testing desktop app...")
                subprocess.run([str(paths['venv_python']), 'test_desktop_app.py'])
            elif build_choice == '2':
                print("🔨 Building executable...")
                if sys.platform.startswith('win'):
                    subprocess.run(['build_desktop_app.bat'])
                else:
                    subprocess.run(['./build_desktop_app.sh'])
            elif build_choice == '3':
                print("📦 Packaging for distribution...")
                subprocess.run([str(paths['venv_python']), 'package_desktop_app.py'])
            elif build_choice == '4':
                print("🔧 Installing system service...")
                subprocess.run([str(paths['venv_python']), 'install_service.py', 'install'])
            elif build_choice == '5':
                pass  # Back to main menu
            else:
                print("❌ Invalid build option")
        elif choice == '9':
            show_help()
        elif choice == '10':
            print("🚪 Exiting AI IDS Launcher. Stay secure! 🛡️")
            break
        else:
            print("❌ Invalid choice. Please select 1-10.")
        
        if choice != '10':
            input("\nPress Enter to continue...")
            print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Launcher interrupted. Goodbye! 👋")
    except Exception as e:
        print(f"\n❌ Launcher error: {e}")
        sys.exit(1)
