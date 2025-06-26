#!/usr/bin/env python3
"""
AI-IDS Desktop App System Service Installer
Creates system services for auto-start functionality
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import json
import logging

class ServiceInstaller:
    """Install and manage AI-IDS as a system service"""
    
    def __init__(self):
        self.app_name = "ai-ids"
        self.service_name = "ai-ids-service"
        self.app_path = Path(__file__).parent.resolve()
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def is_admin(self):
        """Check if running with administrator privileges"""
        try:
            if platform.system() == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.getuid() == 0
        except:
            return False
    
    def request_admin(self):
        """Request administrator privileges"""
        if platform.system() == "Windows":
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                # Re-run as admin
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                return False
        else:
            if os.getuid() != 0:
                print("🔐 Administrator privileges required")
                print("Please run with sudo:")
                print(f"sudo python3 {' '.join(sys.argv)}")
                return False
        return True
    
    def create_windows_service(self):
        """Create Windows service"""
        self.logger.info("Creating Windows service...")
        
        # Create service script
        service_script = self.app_path / f"{self.service_name}.py"
        service_content = f'''#!/usr/bin/env python3
"""
AI-IDS Windows Service
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import threading
import time
from pathlib import Path

# Add app path to sys.path
sys.path.insert(0, r"{self.app_path}")

try:
    from desktop_app.ids_desktop_app import IDSDesktopApp
except ImportError:
    IDSDesktopApp = None

class AIIDSService(win32serviceutil.ServiceFramework):
    _svc_name_ = "{self.service_name}"
    _svc_display_name_ = "AI Intrusion Detection Service"
    _svc_description_ = "AI-powered network intrusion detection and monitoring service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        self.app = None
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False
        if self.app:
            self.app.quit_application()
    
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        try:
            if IDSDesktopApp:
                self.app = IDSDesktopApp()
                # Start monitoring automatically
                threading.Thread(target=self.app.start_monitoring, daemon=True).start()
                
                # Keep service running
                while self.running:
                    time.sleep(1)
            else:
                servicemanager.LogErrorMsg("Could not import IDSDesktopApp")
                
        except Exception as e:
            servicemanager.LogErrorMsg(f"Service error: {{e}}")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AIIDSService)
'''
        
        service_script.write_text(service_content)
        
        # Install service
        try:
            subprocess.run([
                sys.executable, str(service_script), "install"
            ], check=True, capture_output=True)
            
            # Start service
            subprocess.run([
                sys.executable, str(service_script), "start"
            ], check=True, capture_output=True)
            
            self.logger.info("✅ Windows service installed and started")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install Windows service: {e}")
            return False
    
    def create_systemd_service(self):
        """Create systemd service for Linux"""
        self.logger.info("Creating systemd service...")
        
        # Get current user for user service
        username = os.getenv('USER', 'user')
        
        service_content = f'''[Unit]
Description=AI Intrusion Detection System
After=network.target
Wants=network.target

[Service]
Type=simple
User={username}
Group={username}
WorkingDirectory={self.app_path}
Environment=PATH={os.environ.get('PATH')}
Environment=PYTHONPATH={self.app_path}
ExecStart={sys.executable} {self.app_path}/desktop_app/ids_desktop_app.py --start-minimized
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
'''
        
        # Install as system service
        service_file = Path(f"/etc/systemd/system/{self.service_name}.service")
        
        try:
            service_file.write_text(service_content)
            
            # Reload systemd and enable service
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            subprocess.run(["systemctl", "enable", self.service_name], check=True)
            subprocess.run(["systemctl", "start", self.service_name], check=True)
            
            self.logger.info("✅ Systemd service installed and started")
            return True
            
        except (subprocess.CalledProcessError, PermissionError) as e:
            self.logger.error(f"Failed to install systemd service: {e}")
            
            # Try user service as fallback
            return self.create_user_systemd_service()
    
    def create_user_systemd_service(self):
        """Create user systemd service"""
        self.logger.info("Creating user systemd service...")
        
        # Create user service directory
        user_service_dir = Path.home() / ".config/systemd/user"
        user_service_dir.mkdir(parents=True, exist_ok=True)
        
        service_content = f'''[Unit]
Description=AI Intrusion Detection System (User)
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
WorkingDirectory={self.app_path}
Environment=PATH={os.environ.get('PATH')}
Environment=PYTHONPATH={self.app_path}
Environment=DISPLAY={os.environ.get('DISPLAY', ':0')}
ExecStart={sys.executable} {self.app_path}/desktop_app/ids_desktop_app.py --start-minimized
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
'''
        
        service_file = user_service_dir / f"{self.service_name}.service"
        
        try:
            service_file.write_text(service_content)
            
            # Enable and start user service
            subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
            subprocess.run(["systemctl", "--user", "enable", self.service_name], check=True)
            subprocess.run(["systemctl", "--user", "start", self.service_name], check=True)
            
            # Enable lingering for user services to start at boot
            subprocess.run(["loginctl", "enable-linger", os.getenv('USER')], check=False)
            
            self.logger.info("✅ User systemd service installed and started")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install user systemd service: {e}")
            return False
    
    def create_launchd_service(self):
        """Create launchd service for macOS"""
        self.logger.info("Creating launchd service...")
        
        # Use LaunchAgents for user-level service
        launch_agents_dir = Path.home() / "Library/LaunchAgents"
        launch_agents_dir.mkdir(exist_ok=True)
        
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ai-ids.service</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{self.app_path}/desktop_app/ids_desktop_app.py</string>
        <string>--start-minimized</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{self.app_path}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{Path.home()}/Library/Logs/ai-ids.log</string>
    <key>StandardErrorPath</key>
    <string>{Path.home()}/Library/Logs/ai-ids-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>{os.environ.get('PATH')}</string>
        <key>PYTHONPATH</key>
        <string>{self.app_path}</string>
    </dict>
</dict>
</plist>'''
        
        plist_file = launch_agents_dir / "com.ai-ids.service.plist"
        
        try:
            plist_file.write_text(plist_content)
            
            # Load and start service
            subprocess.run(["launchctl", "load", str(plist_file)], check=True)
            subprocess.run(["launchctl", "start", "com.ai-ids.service"], check=True)
            
            self.logger.info("✅ Launchd service installed and started")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install launchd service: {e}")
            return False
    
    def install_service(self):
        """Install platform-appropriate service"""
        system = platform.system()
        
        if system == "Windows":
            return self.create_windows_service()
        elif system == "Linux":
            return self.create_systemd_service()
        elif system == "Darwin":
            return self.create_launchd_service()
        else:
            self.logger.error(f"Unsupported platform: {system}")
            return False
    
    def uninstall_service(self):
        """Uninstall service"""
        system = platform.system()
        
        try:
            if system == "Windows":
                service_script = self.app_path / f"{self.service_name}.py"
                if service_script.exists():
                    subprocess.run([sys.executable, str(service_script), "remove"], check=True)
                    service_script.unlink()
                
            elif system == "Linux":
                # Try system service first
                try:
                    subprocess.run(["systemctl", "stop", self.service_name], check=True)
                    subprocess.run(["systemctl", "disable", self.service_name], check=True)
                    Path(f"/etc/systemd/system/{self.service_name}.service").unlink(missing_ok=True)
                except:
                    # Try user service
                    subprocess.run(["systemctl", "--user", "stop", self.service_name], check=False)
                    subprocess.run(["systemctl", "--user", "disable", self.service_name], check=False)
                    user_service = Path.home() / f".config/systemd/user/{self.service_name}.service"
                    user_service.unlink(missing_ok=True)
                
                subprocess.run(["systemctl", "daemon-reload"], check=False)
                subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
                
            elif system == "Darwin":
                plist_file = Path.home() / "Library/LaunchAgents/com.ai-ids.service.plist"
                if plist_file.exists():
                    subprocess.run(["launchctl", "unload", str(plist_file)], check=False)
                    plist_file.unlink()
            
            self.logger.info("✅ Service uninstalled")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall service: {e}")
            return False
    
    def check_service_status(self):
        """Check service status"""
        system = platform.system()
        
        try:
            if system == "Windows":
                result = subprocess.run([
                    "sc", "query", self.service_name
                ], capture_output=True, text=True)
                return "RUNNING" in result.stdout
                
            elif system == "Linux":
                # Check system service first
                result = subprocess.run([
                    "systemctl", "is-active", self.service_name
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    return "active" in result.stdout
                
                # Check user service
                result = subprocess.run([
                    "systemctl", "--user", "is-active", self.service_name
                ], capture_output=True, text=True)
                return "active" in result.stdout
                
            elif system == "Darwin":
                result = subprocess.run([
                    "launchctl", "list", "com.ai-ids.service"
                ], capture_output=True, text=True)
                return result.returncode == 0
                
        except Exception as e:
            self.logger.error(f"Failed to check service status: {e}")
        
        return False

def main():
    """Main installer function"""
    print("🛡️ AI-IDS Service Installer")
    print("=" * 30)
    
    installer = ServiceInstaller()
    
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        
        if action == "install":
            if not installer.request_admin():
                sys.exit(1)
            
            print("📦 Installing AI-IDS service...")
            if installer.install_service():
                print("✅ Service installed successfully!")
                print("🚀 AI-IDS will now start automatically with your system")
            else:
                print("❌ Service installation failed")
                sys.exit(1)
                
        elif action == "uninstall":
            if not installer.request_admin():
                sys.exit(1)
                
            print("🗑️ Uninstalling AI-IDS service...")
            if installer.uninstall_service():
                print("✅ Service uninstalled successfully!")
            else:
                print("❌ Service uninstall failed")
                sys.exit(1)
                
        elif action == "status":
            status = installer.check_service_status()
            print(f"Service status: {'🟢 Running' if status else '🔴 Stopped'}")
            
        else:
            print(f"Unknown action: {action}")
            sys.exit(1)
    
    else:
        print("Usage:")
        print(f"  {sys.argv[0]} install   - Install service")
        print(f"  {sys.argv[0]} uninstall - Uninstall service")
        print(f"  {sys.argv[0]} status    - Check service status")

if __name__ == "__main__":
    main()
