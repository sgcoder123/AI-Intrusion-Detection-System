# AI-IDS Desktop Application

🛡️ **AI-powered Intrusion Detection System** - A cross-platform desktop application that provides real-time network monitoring, threat detection, and system protection.

## 🚀 Quick Start

### Download & Install

1. **Download** the appropriate package for your platform:
   - **Windows**: `AI-IDS-1.0.0-windows.zip`
   - **macOS**: `AI-IDS-1.0.0-macOS.dmg` or `AI-IDS-1.0.0-macOS.zip`
   - **Linux**: `AI-IDS-1.0.0-linux.tar.gz` or `AI-IDS-1.0.0-linux.AppImage`

2. **Extract/Install** the package
3. **Run** the application
4. **Configure** auto-start (optional)

## 📋 System Requirements

- **Python 3.7+** (for source installation)
- **2GB RAM** minimum
- **100MB disk space**
- **Administrator privileges** (for full functionality)
- **Network access** for real-time monitoring

### Platform-Specific Requirements

**Windows:**
- Windows 10/11 or Windows Server 2019+
- .NET Framework 4.7.2+ (usually pre-installed)

**macOS:**
- macOS 10.12 (Sierra) or later
- Xcode Command Line Tools (for some dependencies)

**Linux:**
- Any modern distribution (Ubuntu 18.04+, CentOS 8+, etc.)
- SystemD (for service installation)
- Network packet capture capabilities

## 🔧 Installation Methods

### Method 1: Executable Package (Recommended)

**Windows:**
```cmd
# Download AI-IDS-1.0.0-windows.zip
# Extract to desired location
# Run AI-IDS.exe
# Grant admin permissions when prompted
```

**macOS:**
```bash
# Download AI-IDS-1.0.0-macOS.dmg
# Open DMG and drag AI-IDS.app to Applications
# Or extract ZIP and run AI-IDS
```

**Linux:**
```bash
# Download AI-IDS-1.0.0-linux.tar.gz
tar -xzf AI-IDS-1.0.0-linux.tar.gz
cd AI-IDS-1.0.0
./AI-IDS

# Or use AppImage
chmod +x AI-IDS-1.0.0-linux.AppImage
./AI-IDS-1.0.0-linux.AppImage
```

### Method 2: Source Installation

```bash
# Clone the repository
git clone https://github.com/your-org/AI-Intrusion-Detection-System.git
cd AI-Intrusion-Detection-System

# Install dependencies
pip install -r requirements.txt

# Run the desktop app
python desktop_app/ids_desktop_app.py
```

### Method 3: Service Installation

For automatic startup with your system:

```bash
# Install as system service
python install_service.py install

# Check service status
python install_service.py status

# Uninstall service
python install_service.py uninstall
```

## 🎯 Features

### Core Features
- 🔍 **Real-time Network Monitoring** - Continuous packet analysis
- 🤖 **AI-Powered Detection** - Machine learning threat identification  
- 📊 **Web Dashboard** - Live statistics and alerts
- 🔔 **Alert System** - Real-time threat notifications
- 📈 **Traffic Analysis** - Network behavior monitoring

### Desktop Integration
- 🖥️ **System Tray** - Runs quietly in background
- 🚀 **Auto-Start** - Launches with system boot
- ⚙️ **GUI Configuration** - Easy settings management
- 📝 **Log Viewing** - Built-in log browser
- 🌐 **Cross-Platform** - Windows, macOS, Linux support

### Advanced Features
- 🛡️ **Threat Classification** - Multiple attack type detection
- 📊 **Performance Monitoring** - System resource tracking
- 🔧 **Configurable Thresholds** - Customizable detection sensitivity
- 💾 **Data Export** - Save alerts and statistics
- 🔒 **Secure Operation** - Encrypted configuration storage

## 🖱️ Usage

### Desktop Application

1. **Start the App**
   - Double-click the executable or desktop shortcut
   - App starts minimized in system tray

2. **System Tray Controls**
   - Right-click tray icon for menu
   - Start/Stop monitoring
   - Open dashboard
   - Show main window
   - Exit application

3. **Main Window**
   - **Status Tab**: View monitoring status and statistics
   - **Configuration Tab**: Adjust settings and enable auto-start
   - **Logs Tab**: View application logs and alerts
   - **About Tab**: Application information

4. **Web Dashboard**
   - Access at `http://localhost:8080`
   - Real-time network statistics
   - Threat detection alerts
   - Interactive charts and graphs

### Configuration

**Enable Auto-Start:**
1. Open main window (right-click tray → "Show Window")
2. Go to Configuration tab
3. Check "Start with system"
4. Click "Save Configuration"

**Adjust Detection Sensitivity:**
1. Use the "Alert Threshold" slider
2. Higher values = fewer false positives
3. Lower values = more sensitive detection

**Change Dashboard Port:**
1. Modify "Dashboard Port" field
2. Save configuration
3. Restart monitoring

## 🚨 Alerts & Monitoring

### Alert Types
- **Port Scan Detection** - Unauthorized port scanning attempts
- **IP Sweep Detection** - Network reconnaissance activities  
- **DoS Attack Detection** - Denial of service attempts
- **Suspicious Traffic** - Anomalous network patterns
- **Malware Communication** - Known malicious IP contacts

### Monitoring Modes
- **Live Mode** - Real-time packet analysis
- **Demo Mode** - Simulated threats for testing
- **Training Mode** - Model retraining capabilities

## 🛠️ Troubleshooting

### Common Issues

**Application won't start:**
- Check Python version (3.7+ required)
- Install missing dependencies: `pip install -r requirements.txt`
- Run as administrator/root
- Check antivirus software permissions

**No network monitoring:**
- Grant administrator privileges
- Check firewall settings
- Verify network interface access
- Install packet capture drivers (Windows)

**Dashboard not accessible:**
- Check if port 8080 is available
- Try different port in configuration
- Verify firewall allows local connections
- Restart monitoring service

**Auto-start not working:**
- Run installer as administrator
- Check system service status
- Verify autostart configuration
- Review system logs for errors

### Log Files

**Windows**: `%USERPROFILE%\.ai_ids\ai_ids_app.log`
**macOS**: `~/Library/Logs/ai-ids.log`
**Linux**: `~/.ai_ids/ai_ids_app.log`

### Getting Help

1. Check log files for error messages
2. Run in console mode for debugging: `python ids_desktop_app.py`
3. Visit documentation at `http://localhost:8000`
4. Submit issues on GitHub repository

## 🔧 Development

### Building from Source

```bash
# Install build dependencies
pip install pyinstaller wheel

# Build executable
./build_desktop_app.sh    # Linux/macOS
build_desktop_app.bat     # Windows

# Or use Python packager
python package_desktop_app.py
```

### Project Structure

```
AI-Intrusion-Detection-System/
├── desktop_app/
│   └── ids_desktop_app.py      # Main desktop application
├── src/
│   ├── realtime_monitor.py     # Network monitoring
│   ├── dashboard.py            # Web dashboard
│   ├── config.py               # Configuration management
│   └── ...
├── models/                     # Pre-trained ML models
├── web_app/                    # Web portal
├── build_desktop_app.sh        # Build script
├── install_service.py          # Service installer
└── requirements.txt            # Dependencies
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🔒 Security

This application handles network traffic and system integration. Please:

- Keep the application updated
- Review source code before installation
- Run with appropriate privileges only
- Report security issues responsibly

## 📞 Support

- **Documentation**: Available in web portal
- **Issues**: GitHub repository issues page
- **Email**: Contact development team
- **Community**: Join our discussion forums

---

**Made with ❤️ by the AI-IDS Team**
