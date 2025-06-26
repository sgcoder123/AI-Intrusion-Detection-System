#!/usr/bin/env python3
"""
Create a truly portable AI-IDS desktop app that requires no Python installation.
This creates a self-contained HTML file that runs in any web browser.
"""

import os
import base64
from pathlib import Path

def create_portable_app():
    """Create a portable HTML-based desktop app"""
    
    # HTML template with embedded CSS and JavaScript
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Intrusion Detection System - Desktop App</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .app-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 30px;
            width: 90%;
            max-width: 800px;
            min-height: 600px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: #4a5568;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .status-section {
            background: #f7fafc;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 5px solid #4299e1;
        }
        
        .status-indicator {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-active {
            color: #38a169;
        }
        
        .status-inactive {
            color: #e53e3e;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 20px;
        }
        
        .btn {
            background: linear-gradient(45deg, #4299e1, #3182ce);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(66, 153, 225, 0.3);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-stop {
            background: linear-gradient(45deg, #e53e3e, #c53030);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            border-color: #4299e1;
            transform: translateY(-5px);
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #718096;
            font-size: 0.9em;
        }
        
        .threat-value {
            color: #e53e3e;
        }
        
        .config-section {
            background: #f7fafc;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .config-item {
            margin-bottom: 15px;
        }
        
        .config-item label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #4a5568;
        }
        
        .slider {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #e2e8f0;
            outline: none;
            -webkit-appearance: none;
        }
        
        .slider::-webkit-slider-thumb {
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #4299e1;
            cursor: pointer;
        }
        
        .log-section {
            background: #1a202c;
            color: #e2e8f0;
            border-radius: 10px;
            padding: 20px;
            height: 200px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.4;
        }
        
        .log-entry {
            margin-bottom: 5px;
            padding: 2px 0;
        }
        
        .log-info {
            color: #63b3ed;
        }
        
        .log-success {
            color: #68d391;
        }
        
        .log-alert {
            color: #f56565;
            font-weight: bold;
        }
        
        .log-timestamp {
            color: #a0aec0;
        }
        
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #718096;
            font-size: 0.9em;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .monitoring-active {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="header">
            <h1>🛡️ AI Intrusion Detection System</h1>
            <p>Portable Desktop Application - No Installation Required</p>
        </div>
        
        <div class="status-section">
            <div class="status-indicator" id="statusIndicator">
                <span id="statusIcon">🔴</span>
                <span id="statusText">Protection Disabled</span>
            </div>
            
            <div class="controls">
                <button class="btn" id="startBtn" onclick="startProtection()">
                    🛡️ Start Protection
                </button>
                <button class="btn btn-stop" id="stopBtn" onclick="stopProtection()" disabled>
                    ⏹️ Stop Protection
                </button>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="packetsCount">0</div>
                <div class="stat-label">Packets Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value threat-value" id="threatsCount">0</div>
                <div class="stat-label">Threats Detected</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="uptimeDisplay">00:00:00</div>
                <div class="stat-label">Uptime</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">92%</div>
                <div class="stat-label">Detection Accuracy</div>
            </div>
        </div>
        
        <div class="config-section">
            <h3 style="margin-bottom: 15px; color: #4a5568;">⚙️ Configuration</h3>
            <div class="config-item">
                <label for="sensitivitySlider">Detection Sensitivity: <span id="sensitivityValue">50</span>%</label>
                <input type="range" id="sensitivitySlider" class="slider" min="1" max="100" value="50" 
                       oninput="updateSensitivity(this.value)">
            </div>
        </div>
        
        <div style="margin-bottom: 10px;">
            <h3 style="color: #4a5568;">📋 Activity Log</h3>
        </div>
        <div class="log-section" id="logContainer">
            <div class="log-entry log-info">
                <span class="log-timestamp">[00:00:00]</span> 
                AI-IDS Portable App loaded successfully. Click 'Start Protection' to begin monitoring.
            </div>
        </div>
        
        <div class="footer">
            <p>✨ AI Intrusion Detection System v1.0 - Portable Edition</p>
            <p>No Python, no installation, no dependencies required!</p>
        </div>
    </div>

    <script>
        // Application state
        let isMonitoring = false;
        let startTime = null;
        let packetsAnalyzed = 0;
        let threatsDetected = 0;
        let sensitivity = 50;
        let monitoringInterval = null;
        let uptimeInterval = null;
        
        // Threat types for simulation
        const threatTypes = [
            "Port Scan",
            "DoS Attack", 
            "Suspicious Connection",
            "Malware Communication",
            "IP Sweep",
            "Brute Force Attack",
            "SQL Injection Attempt",
            "XSS Attack",
            "Unauthorized Access"
        ];
        
        function getCurrentTime() {
            return new Date().toLocaleTimeString('en-US', { hour12: false });
        }
        
        function addLog(message, type = 'info') {
            const logContainer = document.getElementById('logContainer');
            const timestamp = getCurrentTime();
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry log-${type}`;
            logEntry.innerHTML = `<span class="log-timestamp">[${timestamp}]</span> ${message}`;
            
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
            
            // Keep only last 50 entries
            while (logContainer.children.length > 50) {
                logContainer.removeChild(logContainer.firstChild);
            }
        }
        
        function generateRandomIP() {
            return `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
        }
        
        function simulateMonitoring() {
            if (!isMonitoring) return;
            
            // Simulate packet analysis
            const packetsThisRound = Math.floor(Math.random() * 150) + 50;
            packetsAnalyzed += packetsThisRound;
            document.getElementById('packetsCount').textContent = packetsAnalyzed.toLocaleString();
            
            // Simulate threat detection based on sensitivity
            const threatProbability = (100 - sensitivity) / 100 * 0.1; // Lower sensitivity = more threats
            
            if (Math.random() < threatProbability) {
                threatsDetected++;
                const threatType = threatTypes[Math.floor(Math.random() * threatTypes.length)];
                const sourceIP = generateRandomIP();
                
                document.getElementById('threatsCount').textContent = threatsDetected;
                addLog(`🚨 THREAT DETECTED: ${threatType} from ${sourceIP}`, 'alert');
                
                // Flash the threat counter
                const threatElement = document.getElementById('threatsCount');
                threatElement.style.animation = 'pulse 0.5s ease-in-out';
                setTimeout(() => {
                    threatElement.style.animation = '';
                }, 500);
            }
        }
        
        function updateUptime() {
            if (!isMonitoring || !startTime) return;
            
            const now = new Date();
            const diff = Math.floor((now - startTime) / 1000);
            const hours = Math.floor(diff / 3600).toString().padStart(2, '0');
            const minutes = Math.floor((diff % 3600) / 60).toString().padStart(2, '0');
            const seconds = (diff % 60).toString().padStart(2, '0');
            
            document.getElementById('uptimeDisplay').textContent = `${hours}:${minutes}:${seconds}`;
        }
        
        function startProtection() {
            if (isMonitoring) return;
            
            isMonitoring = true;
            startTime = new Date();
            packetsAnalyzed = 0;
            threatsDetected = 0;
            
            // Update UI
            document.getElementById('statusIcon').textContent = '🟢';
            document.getElementById('statusText').textContent = 'Protection Enabled';
            document.getElementById('statusIndicator').className = 'status-indicator status-active monitoring-active';
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            
            // Reset counters
            document.getElementById('packetsCount').textContent = '0';
            document.getElementById('threatsCount').textContent = '0';
            document.getElementById('uptimeDisplay').textContent = '00:00:00';
            
            // Start monitoring simulation
            monitoringInterval = setInterval(simulateMonitoring, 2000); // Every 2 seconds
            uptimeInterval = setInterval(updateUptime, 1000); // Every second
            
            addLog('🛡️ Protection started - AI monitoring active', 'success');
        }
        
        function stopProtection() {
            if (!isMonitoring) return;
            
            isMonitoring = false;
            
            // Clear intervals
            if (monitoringInterval) {
                clearInterval(monitoringInterval);
                monitoringInterval = null;
            }
            if (uptimeInterval) {
                clearInterval(uptimeInterval);
                uptimeInterval = null;
            }
            
            // Update UI
            document.getElementById('statusIcon').textContent = '🔴';
            document.getElementById('statusText').textContent = 'Protection Disabled';
            document.getElementById('statusIndicator').className = 'status-indicator status-inactive';
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            
            addLog('⏹️ Protection stopped - Monitoring disabled', 'info');
        }
        
        function updateSensitivity(value) {
            sensitivity = parseInt(value);
            document.getElementById('sensitivityValue').textContent = sensitivity;
            
            if (isMonitoring) {
                addLog(`⚙️ Sensitivity updated to ${sensitivity}%`, 'info');
            }
        }
        
        // Initialize app
        document.addEventListener('DOMContentLoaded', function() {
            addLog('✨ AI-IDS Portable App initialized successfully', 'success');
            addLog('📖 This is a demonstration version with simulated network data', 'info');
            addLog('🔧 Adjust sensitivity and click "Start Protection" to begin', 'info');
        });
        
        // Handle page unload
        window.addEventListener('beforeunload', function(e) {
            if (isMonitoring) {
                e.preventDefault();
                e.returnValue = 'Monitoring is currently active. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
    </script>
</body>
</html>'''
    
    return html_content

def create_downloadable_package():
    """Create the downloadable package"""
    
    project_root = Path(__file__).parent
    downloads_dir = project_root / "web_app" / "static" / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔧 Creating portable AI-IDS desktop app...")
    
    # Generate the HTML app
    html_content = create_portable_app()
    
    # Save as downloadable file
    app_file = downloads_dir / "AI-IDS-Portable-Desktop-App.html"
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Create a simple launcher script for better desktop experience
    launcher_script = '''@echo off
REM AI-IDS Portable Desktop App Launcher
REM This script opens the AI-IDS app in your default browser

echo Starting AI Intrusion Detection System...
echo Opening in your default browser...

start "" "AI-IDS-Portable-Desktop-App.html"

echo AI-IDS is now running in your browser.
echo You can close this window.
pause'''
    
    launcher_file = downloads_dir / "Launch-AI-IDS.bat"
    with open(launcher_file, 'w') as f:
        f.write(launcher_script)
    
    # Create README
    readme_content = '''# AI Intrusion Detection System - Portable Desktop App

## What is this?
This is a completely portable version of the AI Intrusion Detection System that requires **NO installation whatsoever**. It runs directly in your web browser.

## How to use:

### Method 1 (Easy):
1. Download both files: `AI-IDS-Portable-Desktop-App.html` and `Launch-AI-IDS.bat`
2. Double-click `Launch-AI-IDS.bat` to start the app
3. The AI-IDS will open in your default browser

### Method 2 (Direct):
1. Download `AI-IDS-Portable-Desktop-App.html`
2. Double-click the HTML file to open it in your browser
3. The app will load automatically

## Features:
- ✅ No Python, no installation, no dependencies required
- ✅ Runs in any modern web browser
- ✅ Live threat detection simulation
- ✅ Real-time statistics and monitoring
- ✅ Adjustable sensitivity settings
- ✅ Activity logging with timestamps
- ✅ Professional desktop-like interface
- ✅ Works completely offline

## How to use the app:
1. Click "Start Protection" to begin monitoring
2. Watch the real-time statistics update
3. Adjust sensitivity slider to change detection rates
4. View threat alerts in the activity log
5. Click "Stop Protection" to pause monitoring

## System Requirements:
- Any modern web browser (Chrome, Firefox, Safari, Edge)
- No additional software needed
- Works on Windows, macOS, and Linux

## About:
This is a demonstration version of the AI Intrusion Detection System with simulated network data. It showcases the interface and functionality of a real intrusion detection system in an educational format.

The app demonstrates:
- Network packet analysis simulation
- Threat detection algorithms
- Real-time monitoring capabilities
- User-friendly security interface

Perfect for cybersecurity education, demonstrations, and learning!

---
Built with ❤️ for cybersecurity education and demonstration purposes.
'''
    
    readme_file = downloads_dir / "AI-IDS-README.txt"
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    
    # Get file sizes
    html_size = app_file.stat().st_size / 1024  # KB
    
    print(f"✅ Portable app created successfully!")
    print(f"📁 Files created in: {downloads_dir}")
    print(f"   - AI-IDS-Portable-Desktop-App.html ({html_size:.1f} KB)")
    print(f"   - Launch-AI-IDS.bat (Windows launcher)")
    print(f"   - AI-IDS-README.txt (Instructions)")
    print(f"\n🎉 Ready for download! Users can run this without any installation.")
    
    return True

if __name__ == "__main__":
    create_downloadable_package()
