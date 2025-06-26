# AI Intrusion Detection System - Getting Started Guide

## 🎯 What You Downloaded
You've downloaded the AI-IDS (AI Intrusion Detection System) - a user-friendly desktop application for network security monitoring and threat detection demonstration.

## 📦 Available Download Options

### 1. **AI-IDS Portable** (Recommended for beginners)
- **File**: `AI-IDS-Portable.zip`
- **Best for**: Users who want the easiest setup
- **Works**: With or without Python installed

### 2. **AI-IDS Desktop Package**
- **Files**: `AI-IDS-Desktop-v1.0.0.zip` or `AI-IDS-Desktop-v1.0.0.tar.gz`
- **Best for**: Users who have Python installed
- **Works**: Requires Python 3.6+

---

## 🚀 Step-by-Step Installation Guide

### Option A: Portable Version (Easiest - No Python Required)

#### Windows Users:
1. **Download** `AI-IDS-Portable.zip`
2. **Extract** the ZIP file to any folder (e.g., Desktop, Documents)
3. **Open** the extracted `AI-IDS-Portable` folder
4. **Double-click** `launch_ai_ids.bat`
5. **Wait** for the application to start (may take 10-30 seconds)

#### Mac/Linux Users:
1. **Download** `AI-IDS-Portable.zip`
2. **Extract** the ZIP file to any folder
3. **Open Terminal** and navigate to the extracted folder:
   ```bash
   cd ~/Downloads/AI-IDS-Portable
   ```
4. **Make the launcher executable**:
   ```bash
   chmod +x launch_ai_ids.sh
   ```
5. **Run the launcher**:
   ```bash
   ./launch_ai_ids.sh
   ```

### Option B: Desktop Package (Requires Python)

#### Prerequisites:
- Python 3.6 or higher installed
- pip (Python package installer)

#### Installation Steps:
1. **Download** `AI-IDS-Desktop-v1.0.0.zip`
2. **Extract** to your preferred location
3. **Open Terminal/Command Prompt** in the extracted folder
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the application**:
   ```bash
   python standalone_ids_app.py
   ```

---

## 🖥️ Using the Application

### First Launch
1. The AI-IDS window will open with a clean interface
2. You'll see the main dashboard with:
   - **Protection Status**: Currently stopped (red)
   - **Statistics**: All zeros initially
   - **Configuration**: Sensitivity slider and settings
   - **Recent Alerts**: Empty log area

### Starting Protection
1. **Click** the "🛡️ Start Protection" button
2. **Watch** the status change to "🟢 Protection Enabled"
3. **Observe** live statistics updating:
   - Packets Analyzed (simulated network traffic)
   - Threats Detected (based on AI analysis)
   - Uptime counter

### Adjusting Settings
- **Sensitivity Slider**: Lower values = more threats detected
- **Auto-start**: Check to start protection automatically
- **Recent Alerts**: View detected threats in real-time

### Stopping Protection
- **Click** "⏹️ Stop Protection" to pause monitoring
- Statistics will freeze until you restart

---

## 🔧 Troubleshooting

### Application Won't Start

#### Windows:
- **Right-click** `launch_ai_ids.bat` → "Run as administrator"
- **Check** if Windows Defender is blocking the file
- **Ensure** you extracted the full ZIP file contents

#### Mac:
- **System Preferences** → Security & Privacy → Allow the application
- **Terminal**: Try running with `python3` instead of `python`
- **Permissions**: Run `chmod +x launch_ai_ids.sh`

#### Linux:
- **Install tkinter**: `sudo apt-get install python3-tk`
- **Check Python**: `python3 --version`
- **Run directly**: `python3 ai_ids_app.py`

### Web Mode (Fallback)
If the desktop app fails, the system automatically opens a web version:
1. Your default browser will open
2. Navigate to `http://localhost:8080`
3. Use the web interface (same features)

### Common Issues:

**ERROR: "tkinter not found"**
- Install Python with tkinter support
- On Ubuntu/Debian: `sudo apt-get install python3-tk`
- On CentOS/RHEL: `sudo yum install tkinter`

**ERROR: "Module not found"**
- Run: `pip install -r requirements.txt`
- Or try: `pip3 install -r requirements.txt`

**Application freezes**
- Close and restart the application
- Check system resources (RAM/CPU)
- Try reducing sensitivity setting

---

## 🎮 Demo Mode vs Live Mode

### Demo Mode (Default)
- **Simulated** network traffic and threats
- **Safe** for testing and learning
- **No actual** network monitoring
- **Educational** purposes

### Live Mode (Advanced)
- Requires additional setup
- Real network packet analysis
- Administrative privileges needed
- For cybersecurity professionals

---

## 📱 Features Overview

### 🛡️ Protection Dashboard
- Real-time status indicator
- One-click start/stop protection
- Live threat counter
- Network packet statistics

### ⚙️ Configuration
- Adjustable sensitivity (1-100)
- Auto-start with system option
- Sound alerts toggle
- Persistent settings storage

### 📊 Monitoring
- Live threat detection
- Alert categorization
- Activity logging
- Uptime tracking

### 🔍 Threat Types Detected
- Port scans
- DDoS attempts
- Suspicious connections
- Malware communications
- IP sweeps
- Brute force attacks

---

## 🆘 Getting Help

### Built-in Help
- **Menu**: Help → Documentation
- **Tooltips**: Hover over buttons for quick help
- **Log**: Check "Recent Alerts" for status messages

### Online Resources
- **GitHub**: [Project Repository]
- **Documentation**: Check included README files
- **Issues**: Report bugs through the web interface

### Contact Support
If you encounter persistent issues:
1. **Check** the troubleshooting section above
2. **Try** the web mode fallback
3. **Note** your operating system and Python version
4. **Describe** the specific error message

---

## 🎯 Quick Start Checklist

- [ ] Downloaded and extracted AI-IDS package
- [ ] Ran the launcher script for your OS
- [ ] Application opened successfully
- [ ] Clicked "Start Protection"
- [ ] Observed live statistics updating
- [ ] Adjusted sensitivity if desired
- [ ] Ready to monitor for threats!

---

## 🔒 Privacy & Security Notes

- This is a **demonstration application** for educational purposes
- **No real** network data is transmitted externally
- **Settings** are stored locally on your computer
- **No personal** information is collected
- Safe to use on any network

---

**Congratulations! 🎉 You're now ready to use the AI Intrusion Detection System!**

For advanced features and customization, refer to the technical documentation included with your download.
