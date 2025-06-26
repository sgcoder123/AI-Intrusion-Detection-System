# 🛡️ Real-Time Network Intrusion Detection System

## Overview

This AI-powered intrusion detection system now includes **real-time network packet monitoring** capabilities. It captures and analyzes network traffic in real-time, detecting potential security threats using your trained machine learning model.

## 🚀 Quick Start

### 1. Installation

Run the automated installation script:

```bash
chmod +x install.sh
./install.sh
```

This will:
- Install system dependencies
- Create a Python virtual environment  
- Install required Python packages
- Set up configuration files
- Create launcher scripts

### 2. Start Monitoring

**Option A: Dashboard Only (No Root Required)**
```bash
./start_ids.sh
```

**Option B: Full Real-Time Monitoring (Requires Root)**
```bash
sudo ./start_ids_monitor.sh
```

### 3. Access Dashboard

Open your browser and go to:
```
http://localhost:8080
```

## 🔧 Configuration

The system uses a YAML configuration file located at `src/ids_config.yaml`. Key settings include:

```yaml
network:
  interface: 'auto'  # Network interface to monitor
  
detection:
  model_path: 'models/random_forest_model_tuned.joblib'
  confidence_threshold: 0.8  # Alert threshold (0.0-1.0)
  
monitoring:
  enable_web_dashboard: true
  dashboard_port: 8080
  dashboard_host: '127.0.0.1'

alerts:
  log_file: 'security_alerts.json'
  enable_email: false  # Email notifications (configure SMTP)
```

## 🌐 Web Dashboard Features

The included web dashboard provides:

- **Real-time statistics**: Packets processed, threats detected, detection rate
- **Live threat alerts**: Recent security incidents with details
- **Threat visualization**: Charts showing attack types and detection trends  
- **System status**: Interface monitoring and uptime tracking
- **Responsive design**: Works on desktop and mobile devices

## 🔍 Detection Capabilities

The system monitors and analyzes:

### Network Traffic
- **Incoming packets**: From router/internet to your device
- **Outgoing packets**: From your device to external networks
- **All protocols**: TCP, UDP, ICMP traffic analysis
- **Port scanning detection**: Unusual connection patterns

### Attack Types Detected
Based on your trained model, the system can identify:

- DoS/DDoS attacks
- Port scans and reconnaissance
- Malware communication
- Unauthorized access attempts
- Data exfiltration patterns
- Network intrusions
- And 20+ other attack categories

## 💻 Command Line Usage

### Basic Usage
```bash
# Start with default settings
sudo python3 src/ids_main.py

# Monitor specific interface
sudo python3 src/ids_main.py --interface eth0

# Set custom confidence threshold
sudo python3 src/ids_main.py --threshold 0.9

# Disable dashboard
sudo python3 src/ids_main.py --no-dashboard

# Custom dashboard port
sudo python3 src/ids_main.py --dashboard-port 9000
```

### Advanced Options
```bash
# Use custom config file
sudo python3 src/ids_main.py --config my_config.yaml

# Use different model
sudo python3 src/ids_main.py --model path/to/model.joblib

# Show system status
python3 src/ids_main.py --status
```

## 📊 Real-Time Features

### Packet Processing Pipeline
1. **Packet Capture**: Using Scapy for real-time packet sniffing
2. **Feature Extraction**: Convert packets to 41 ML features
3. **Threat Detection**: ML model classification in real-time
4. **Alert Generation**: Immediate threat notifications
5. **Dashboard Updates**: Live statistics and visualizations

### Performance Optimizations
- **Multi-threaded processing**: Separate threads for capture and analysis
- **Queue management**: Buffered packet processing to prevent drops
- **Rate limiting**: Prevents alert spam from the same source
- **Efficient feature extraction**: Optimized for low-latency processing

## 🔒 Security Considerations

### Root Privileges
Packet capture requires root privileges. The system:
- Only requests sudo when needed for packet capture
- Runs analysis in user space when possible
- Includes permission checking and warnings

### Network Interface Access
- Automatically detects the best interface to monitor
- Supports manual interface selection
- Works with Ethernet, Wi-Fi, and virtual interfaces

### Privacy Protection
- Only analyzes packet headers and metadata
- Does not store or log packet contents
- Respects local network privacy requirements

## 📁 File Structure

```
AI-Intrusion-Detection-System/
├── src/
│   ├── ids_main.py           # Main integrated system
│   ├── realtime_monitor.py   # Real-time packet monitoring
│   ├── dashboard.py          # Web dashboard
│   ├── config.py            # Configuration management
│   ├── deploy_model.py      # Model deployment (existing)
│   └── ids_config.yaml      # Configuration file
├── models/                  # Trained ML models
├── data/                   # Training/validation data
├── install.sh              # Installation script
├── start_ids.sh           # Dashboard launcher
├── start_ids_monitor.sh   # Full monitoring launcher
└── requirements.txt       # Dependencies
```

## 🚨 Alert System

### Alert Types
- **High Confidence Threats**: Immediate alerts for high-probability attacks
- **Rate-Limited Alerts**: Prevents spam from repeated threats
- **Detailed Information**: Source IP, attack type, confidence level

### Alert Destinations
- **Web Dashboard**: Real-time visual alerts
- **Log Files**: JSON-formatted alert logs
- **Console Output**: Terminal notifications
- **Email Notifications**: Optional SMTP alerts (configurable)

## 🔧 Troubleshooting

### Common Issues

**Permission Denied**
```bash
# Ensure you're running with sudo for packet capture
sudo ./start_ids_monitor.sh
```

**No Network Interface Found**
```bash
# List available interfaces
ip link show

# Specify interface manually
sudo python3 src/ids_main.py --interface eth0
```

**Model Loading Error**
```bash
# Check if model file exists
ls -la models/

# Test model loading
python3 -c "from src.deploy_model import IntrusionDetector; IntrusionDetector()"
```

**Dashboard Not Loading**
```bash
# Check if port is available
netstat -tlnp | grep 8080

# Use different port
python3 src/ids_main.py --dashboard-port 9000
```

### Log Files
- **Application logs**: `intrusion_detection.log`
- **Security alerts**: `security_alerts.json`
- **Configuration**: `src/ids_config.yaml`

## 🎯 Performance Tuning

### For High Traffic Networks
```yaml
network:
  buffer_size: 2000  # Increase packet buffer

detection:
  confidence_threshold: 0.9  # Reduce false positives
  
monitoring:
  stats_update_interval: 10  # Reduce dashboard updates
```

### For Low Resource Systems
```yaml
network:
  buffer_size: 500  # Reduce memory usage

monitoring:
  enable_web_dashboard: false  # Disable dashboard
```

## 📚 Technical Details

### Feature Extraction
The system extracts 41 network features from each packet:
- Connection duration and byte counts
- Protocol type and service identification  
- TCP flags and connection states
- Traffic analysis features
- Host-based statistics

### Machine Learning Integration
- Uses your pre-trained Random Forest model
- Real-time inference on extracted features
- Confidence-based alerting
- Multi-class attack type classification

### Network Monitoring
- Supports promiscuous and non-promiscuous modes
- Cross-platform compatibility (Linux, macOS, Windows)
- Interface auto-detection and manual selection
- Efficient packet filtering and processing

## 🤝 Contributing

Contributions are welcome! Please see the main project README for contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review log files for error details
3. Open an issue on the project repository
4. Include configuration and log information when reporting bugs
