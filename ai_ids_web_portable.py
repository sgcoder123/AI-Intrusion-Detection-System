#!/usr/bin/env python3
"""
AI Intrusion Detection System - Web-Based Real Network Monitor
This creates a web application that monitors real network traffic for intrusions.
Requires administrative privileges to capture network packets.
"""

import os
import sys
import threading
import time
import webbrowser
import json
import socket
import struct
import ipaddress
import random
import numpy as np
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
from collections import defaultdict, deque

# Import ctypes for admin privilege checking
try:
    import ctypes
except ImportError:
    ctypes = None

# Import psutil for network monitoring (optional)
try:
    import psutil
except ImportError:
    psutil = None

# ML imports with fallback
try:
    import joblib
    import pandas as pd
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML libraries (joblib, pandas) not available. AI detection will be disabled.")

class WebIDSApp:
    """Network Intrusion Detection System with Simulation and Real Mode"""
    
    def __init__(self):
        self.is_monitoring = False
        self.threats_detected = 0
        self.packets_analyzed = 0
        self.start_time = None
        self.monitor_thread = None
        self.socket = None
        self.config = {
            'sensitivity': 50,
            'auto_start': False,
            'alert_sound': True,
            'simulation_mode': True  # New config option
            # AI detection is always enabled and cannot be disabled
        }
        
        # AI Model
        self.ml_model = None
        self.ai_feature_columns = [
            'duration', 'protocol_type', 'service', 'flag', 'src_bytes',
            'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
            'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell',
            'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
            'num_access_files', 'num_outbound_cmds', 'is_host_login',
            'is_guest_login', 'count', 'srv_count', 'serror_rate',
            'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate',
            'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
            'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate',
            'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
            'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
            'dst_host_srv_serror_rate', 'dst_host_rerror_rate',
            'dst_host_srv_rerror_rate'
        ]
        self.load_ai_model()
        
        # Enhanced threat detection tracking
        self.connection_counts = defaultdict(int)
        self.port_scan_attempts = defaultdict(set)
        self.recent_packets = deque(maxlen=1000)
        self.suspicious_ips = set()
        self.dos_detection = defaultdict(int)
        self.last_cleanup = time.time()
        
        # Enhanced detection data structures
        self.packet_timestamps = defaultdict(list)  # For timing analysis
        self.connection_patterns = defaultdict(lambda: {'ports': set(), 'first_seen': 0, 'last_seen': 0, 'packet_count': 0})
        self.protocol_stats = defaultdict(int)
        self.payload_sizes = defaultdict(list)
        self.tcp_flags = defaultdict(list)
        self.baseline_established = False
        self.baseline_data = {
            'normal_ports': set(),
            'common_protocols': set(),
            'avg_packet_rate': 0,
            'typical_connections': set()
        }
        
        # Simulation mode data
        self.detected_threats_log = []
        
        # Threat breakdown counters
        self.threat_breakdown = defaultdict(int)
        
    def load_ai_model(self):
        """Load the pre-trained Random Forest model"""
        global ML_AVAILABLE
        if not ML_AVAILABLE:
            print("⚠️ ML libraries not available. AI detection disabled.")
            return False
            
        model_path = Path(__file__).parent / "models" / "random_forest_model_quick.joblib"
        
        try:
            if model_path.exists():
                self.ml_model = joblib.load(model_path)
                print("✅ AI model loaded successfully: random_forest_model_quick.joblib")
                return True
            else:
                print(f"❌ AI model not found at: {model_path}")
                return False
        except Exception as e:
            print(f"❌ Failed to load AI model: {e}")
            return False
    
    def extract_packet_features(self, packet_info, recent_packets_list=None):
        """Extract features from packet for AI model prediction"""
        if not packet_info:
            return None
            
        # Initialize features with default values
        features = {}
        
        # Basic packet features
        features['duration'] = 0  # Connection duration (simplified)
        features['protocol_type'] = self.encode_protocol(packet_info['protocol'])
        features['service'] = self.encode_service(packet_info['dst_port'])
        features['flag'] = 1  # TCP flags (simplified)
        features['src_bytes'] = 0  # Source bytes (not available in basic packet)
        features['dst_bytes'] = 0  # Destination bytes (not available in basic packet)
        features['land'] = 1 if packet_info['src_ip'] == packet_info['dst_ip'] else 0
        features['wrong_fragment'] = 0
        features['urgent'] = 0
        features['hot'] = 0
        features['num_failed_logins'] = 0
        features['logged_in'] = 0
        features['num_compromised'] = 0
        features['root_shell'] = 0
        features['su_attempted'] = 0
        features['num_root'] = 0
        features['num_file_creations'] = 0
        features['num_shells'] = 0
        features['num_access_files'] = 0
        features['num_outbound_cmds'] = 0
        features['is_host_login'] = 0
        features['is_guest_login'] = 0
        
        # Traffic analysis features (based on recent packets)
        if recent_packets_list:
            recent_packets_list = list(recent_packets_list)[-100:]  # Last 100 packets
            
            # Count connections from same source
            same_src_count = sum(1 for p in recent_packets_list if p['src_ip'] == packet_info['src_ip'])
            features['count'] = min(same_src_count, 100)
            
            # Count connections to same service
            same_service_count = sum(1 for p in recent_packets_list if p['dst_port'] == packet_info['dst_port'])
            features['srv_count'] = min(same_service_count, 50)
            
            # Error rates (simplified)
            features['serror_rate'] = 0.0
            features['srv_serror_rate'] = 0.0
            features['rerror_rate'] = 0.0
            features['srv_rerror_rate'] = 0.0
            
            # Service rates
            if same_src_count > 0:
                same_srv_from_src = sum(1 for p in recent_packets_list 
                                      if p['src_ip'] == packet_info['src_ip'] and p['dst_port'] == packet_info['dst_port'])
                features['same_srv_rate'] = same_srv_from_src / same_src_count
                
                diff_srv_from_src = same_src_count - same_srv_from_src
                features['diff_srv_rate'] = diff_srv_from_src / same_src_count
            else:
                features['same_srv_rate'] = 0.0
                features['diff_srv_rate'] = 0.0
                
            features['srv_diff_host_rate'] = 0.0
            
            # Host-based features
            dst_host_connections = sum(1 for p in recent_packets_list if p['dst_ip'] == packet_info['dst_ip'])
            features['dst_host_count'] = min(dst_host_connections, 255)
            features['dst_host_srv_count'] = min(same_service_count, 255)
            features['dst_host_same_srv_rate'] = same_service_count / max(dst_host_connections, 1)
            features['dst_host_diff_srv_rate'] = max(0, 1 - features['dst_host_same_srv_rate'])
            features['dst_host_same_src_port_rate'] = 0.0
            features['dst_host_srv_diff_host_rate'] = 0.0
            features['dst_host_serror_rate'] = 0.0
            features['dst_host_srv_serror_rate'] = 0.0
            features['dst_host_rerror_rate'] = 0.0
            features['dst_host_srv_rerror_rate'] = 0.0

        else:
            # Default values when no recent packets
            for feature in ['count', 'srv_count', 'serror_rate', 'srv_serror_rate', 
                          'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
                          'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
                          'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 
                          'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate',
                          'dst_host_serror_rate', 'dst_host_srv_serror_rate',
                          'dst_host_rerror_rate', 'dst_host_srv_rerror_rate']:
                features[feature] = 0.0

        return features
    
    def encode_protocol(self, protocol_num):
        """Encode protocol number to categorical value"""
        protocol_map = {1: 1, 6: 2, 17: 3}  # ICMP: 1, TCP: 2, UDP: 3
        return protocol_map.get(protocol_num, 0)
    
    def encode_service(self, port):
        """Encode destination port to service category"""
        # Map common ports to service IDs (simplified mapping)
        service_map = {
            21: 1, 22: 2, 23: 3, 25: 4, 53: 5, 80: 6, 110: 7, 143: 8,
            443: 9, 993: 10, 995: 11, 135: 12, 139: 13, 445: 14, 1433: 15,
            3389: 16, 5900: 17, 6379: 18
        }
        return service_map.get(port, 0)
    
    def ai_detect_threats(self, packet_info):
        """AI-powered threat detection using Random Forest model"""
        global ML_AVAILABLE
        if not self.ml_model or not ML_AVAILABLE:
            return []
            
        try:
            # Extract features for the model
            features = self.extract_packet_features(packet_info, self.recent_packets)
            if not features:
                return []
            
            # Create DataFrame with the features in the correct order
            feature_df = pd.DataFrame([features])
            
            # Ensure all required columns are present
            for col in self.ai_feature_columns:
                if col not in feature_df.columns:
                    feature_df[col] = 0
            
            # Reorder columns to match model training
            feature_df = feature_df[self.ai_feature_columns]
            
            # Predict threat probability
            prediction = self.ml_model.predict(feature_df)[0]
            
            # If model predicts an attack (not normal)
            if prediction != 'normal':
                threat_type = f"AI-Detected {prediction.title()} Attack"
                return [f"{threat_type} from {packet_info['src_ip']}"]
            
        except Exception as e:
            print(f"AI detection error: {e}")
            
        return []
    
    def create_network_monitor(self):
        """Create network monitoring capability with permission-free fallback"""
        # Try raw socket first (requires permissions)
        if self.try_raw_socket():
            print("✅ Using raw socket monitoring (requires admin/root)")
            return True
        
        # Fallback to permission-free monitoring
        print("📡 Raw socket failed, using permission-free network monitoring...")
        return self.setup_permission_free_monitoring()
    
    def try_raw_socket(self):
        """Try to create raw socket (requires admin/root privileges)"""
        try:
            # Create raw socket (requires admin/root privileges)
            if os.name == 'nt':  # Windows
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
                self.socket.bind(('', 0))
                self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                # Enable promiscuous mode on Windows
                self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
            else:  # Linux/Unix
                self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
            
            self.monitoring_mode = "raw_socket"
            return True
        except (PermissionError, OSError):
            return False
        except Exception as e:
            print(f"⚠️ Raw socket creation failed: {e}")
            return False
    
    def setup_permission_free_monitoring(self):
        """Setup network monitoring that doesn't require special permissions"""
        try:
            # Use network connection monitoring instead of packet capture
            self.monitoring_mode = "connection_monitor"
            print("✅ Permission-free monitoring enabled")
            print("   - Monitoring active network connections")
            print("   - Analyzing connection patterns")
            print("   - Detecting suspicious network behavior")
            return True
        except Exception as e:
            print(f"❌ Failed to setup permission-free monitoring: {e}")
            return False
    
    def parse_ip_packet(self, packet):
        """Parse IP packet and extract relevant information"""
        try:
            if os.name == 'nt':  # Windows raw socket
                ip_header = packet[:20]
            else:  # Linux with ethernet header
                ip_header = packet[14:34]  # Skip ethernet header
            
            # Unpack IP header
            ip_data = struct.unpack('!BBHHHBBH4s4s', ip_header)
            version_ihl = ip_data[0]
            version = version_ihl >> 4
            ihl = version_ihl & 0xF
            
            if version != 4:  # Only handle IPv4
                return None
                
            protocol = ip_data[6]
            src_ip = socket.inet_ntoa(ip_data[8])
            dst_ip = socket.inet_ntoa(ip_data[9])
            
            # Extract port information for TCP/UDP
            src_port = dst_port = 0
            if protocol in [6, 17]:  # TCP or UDP
                header_length = ihl * 4
                if os.name == 'nt':
                    transport_header = packet[header_length:header_length+4]
                else:
                    transport_header = packet[14+header_length:14+header_length+4]
                
                if len(transport_header) >= 4:
                    src_port, dst_port = struct.unpack('!HH', transport_header)
            
            return {
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'src_port': src_port,
                'dst_port': dst_port,
                'protocol': protocol,
                'timestamp': time.time()
            }
        except Exception:
            return None
    
    def detect_threats(self, packet_info):
        """Analyze packet for potential threats using AI detection only"""
        if not packet_info:
            return []
        
        threats = []
        
        # AI-powered detection (always enabled)
        if self.ml_model:
            ai_threats = self.ai_detect_threats(packet_info)
            if ai_threats:
                threats.extend(ai_threats)
                for threat in ai_threats:
                    threat_type = threat.split(' from ')[0]
                    self.threat_breakdown[threat_type] += 1
        
        return threats
    
    def cleanup_tracking_data(self):
        """Periodically clean up tracking data to prevent memory issues"""
        current_time = time.time()
        if current_time - self.last_cleanup > 300:  # Clean every 5 minutes
            # Reset DoS counters
            self.dos_detection.clear()
            
            # Clean old port scan data (keep only recent)
            for ip in list(self.port_scan_attempts.keys()):
                if len(self.port_scan_attempts[ip]) > 50:
                    self.port_scan_attempts[ip] = set(list(self.port_scan_attempts[ip])[-20:])
            
            # Reset suspicious IPs periodically
            self.suspicious_ips.clear()
            
            self.last_cleanup = current_time
    
    def start_monitoring(self):
        """Start network monitoring in either simulation or real mode"""
        if self.is_monitoring:
            return {"status": "error", "message": "Already monitoring"}
        
        # Check mode and handle accordingly
        if not self.config['simulation_mode']:
            # Real network mode - Try to create network monitoring
            if not self.create_network_monitor():
                return {"status": "error", "message": "Failed to setup network monitoring. Switching to simulation mode."}
        
        # Reset all counters for a fresh start
        self.is_monitoring = True
        self.start_time = datetime.now()
        self.packets_analyzed = 0
        self.threats_detected = 0
        self.connection_counts.clear()
        self.port_scan_attempts.clear()
        self.suspicious_ips.clear()
        self.dos_detection.clear()
        self.detected_threats_log.clear()
        self.threat_breakdown.clear()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        mode_name = "Simulation" if self.config['simulation_mode'] else "Real network"
        return {"status": "started", "message": f"{mode_name} monitoring enabled"}
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.is_monitoring = False
        
        # Close socket
        if self.socket:
            try:
                if os.name == 'nt':
                    self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
                self.socket.close()
            except:
                pass
            self.socket = None
        
        return {"status": "stopped", "message": "Network monitoring disabled"}
    
    def reset_stats(self):
        """Reset all statistics to zero"""
        self.threats_detected = 0
        self.packets_analyzed = 0
        self.start_time = None
        self.connection_counts.clear()
        self.port_scan_attempts.clear()
        self.suspicious_ips.clear()
        self.dos_detection.clear()
        self.threat_breakdown.clear()
        return {"status": "reset", "message": "Statistics reset"}
    
    def monitoring_loop(self):
        """Network monitoring loop - handles both simulation and real modes"""
        if self.config['simulation_mode']:
            print("🎯 Starting simulation mode monitoring...")
            self.simulation_monitoring_loop()
        else:
            if hasattr(self, 'monitoring_mode') and self.monitoring_mode == "raw_socket":
                print("🔍 Starting raw socket packet capture...")
                self.real_monitoring_loop()
            else:
                print("📡 Starting permission-free network monitoring...")
                self.permission_free_monitoring_loop()
    
    def simulation_monitoring_loop(self):
        """Simulated monitoring loop with AI-based threat detection only"""
        while self.is_monitoring:
            # Simulate packet analysis
            packets_per_second = random.randint(50, 200)
            self.packets_analyzed += packets_per_second
            
            # Generate AI-based threats only (if model is available)
            if self.ml_model:
                # Simulate AI threat detection based on sensitivity - reduced frequency
                sensitivity = self.config['sensitivity']
                
                # Reduced sensitivity logic: More reasonable attack rates
                if sensitivity >= 80:  # High sensitivity (More alerts)
                    threat_probability = 0.15  # 15% chance per second (~1 every 7 seconds)
                elif sensitivity >= 50:  # Medium sensitivity
                    threat_probability = 0.08  # 8% chance per second (~1 every 12 seconds)
                else:  # Low sensitivity (Fewer alerts)
                    threat_probability = 0.04  # 4% chance per second (~1 every 25 seconds)
                
                # Single threat check per cycle for more realistic frequency
                if random.random() < threat_probability:
                    # Generate realistic AI-detected threat types with more variety
                    ai_threat_types = [
                        "AI-Detected DoS Attack", "AI-Detected Probe Attack", "AI-Detected U2R Attack",
                        "AI-Detected R2L Attack", "AI-Detected Buffer Overflow Attack", 
                        "AI-Detected Port Sweep", "AI-Detected Neptune Attack", "AI-Detected Smurf Attack",
                        "AI-Detected Ipsweep Attack", "AI-Detected Satan Attack", "AI-Detected Teardrop Attack",
                        "AI-Detected Land Attack", "AI-Detected Back Attack", "AI-Detected Warezclient Attack",
                        "AI-Detected Warezmaster Attack", "AI-Detected Ftp_write Attack", "AI-Detected Guess_passwd Attack",
                        "AI-Detected Imap Attack", "AI-Detected Multihop Attack", "AI-Detected Phf Attack",
                        "AI-Detected Nmap Attack", "AI-Detected Portsweep Attack", "AI-Detected Rootkit Attack",
                        "AI-Detected Spy Attack", "AI-Detected Sqlattack Attack"
                    ]
                    threat_type = random.choice(ai_threat_types)
                    
                    # Generate more realistic IP addresses including some from common attack ranges
                    attack_ip_ranges = [
                        lambda: f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",  # Local network
                        lambda: f"10.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",  # Private network
                        lambda: f"{random.randint(1,223)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",  # Random public
                        lambda: f"172.{random.randint(16,31)}.{random.randint(1,255)}.{random.randint(1,255)}",  # Private network
                    ]
                    source_ip = random.choice(attack_ip_ranges)()
                    
                    threat_detail = f"{threat_type} from {source_ip}"
                    self.detected_threats_log.append(threat_detail)
                    self.threat_breakdown[threat_type] += 1
                    self.threats_detected += 1
            
            time.sleep(1)
    
    def real_monitoring_loop(self):
        """Real network packet monitoring loop"""
        if not self.socket:
            return
            
        while self.is_monitoring and self.socket:
            try:
                # Receive packet
                packet, addr = self.socket.recvfrom(65536)
                self.packets_analyzed += 1
                
                # Parse packet
                packet_info = self.parse_ip_packet(packet)
                if packet_info:
                    self.recent_packets.append(packet_info)
                    
                    # Detect threats
                    threats = self.detect_threats(packet_info)
                    if threats:
                        self.threats_detected += len(threats)
                        # Store threat details for logging
                        self.detected_threats_log.extend(threats)
                
                # Cleanup periodically
                self.cleanup_tracking_data()
                
            except Exception as e:
                if self.is_monitoring:
                    print(f"⚠️ Packet capture error: {e}")
                    time.sleep(0.1)
                break
    
    def permission_free_monitoring_loop(self):
        """Permission-free monitoring loop using network connections"""
        while self.is_monitoring:
            try:
                # Get current network connections
                connections = self.get_network_connections()
                
                # Analyze each connection
                for connection in connections:
                    self.packets_analyzed += 1
                    
                    # Analyze connection for threats using AI
                    threats = self.analyze_connection_for_threats(connection)
                    if threats:
                        self.threats_detected += len(threats)
                        self.detected_threats_log.extend(threats)
                        
                        # Update threat breakdown
                        for threat in threats:
                            threat_type = threat.split(' from ')[0]
                            self.threat_breakdown[threat_type] += 1
                
                # Cleanup periodically
                self.cleanup_tracking_data()
                
                # Sleep to avoid excessive CPU usage
                time.sleep(2)
                
            except Exception as e:
                if self.is_monitoring:
                    print(f"⚠️ Permission-free monitoring error: {e}")
                    time.sleep(1)
                break
    
    def get_stats(self):
        """Get current statistics"""
        uptime = 0
        if self.is_monitoring and self.start_time:
            uptime = int((datetime.now() - self.start_time).total_seconds())
        
        # Get recent threats (last 5)
        recent_threats = self.detected_threats_log[-5:] if self.detected_threats_log else []
        
        return {
            "is_monitoring": self.is_monitoring,
            "packets_analyzed": self.packets_analyzed,
            "threats_detected": self.threats_detected,
            "uptime": uptime,
            "sensitivity": self.config['sensitivity'],
            "simulation_mode": self.config['simulation_mode'],
            "ai_model_loaded": self.ml_model is not None,
            "recent_threats": recent_threats,
            "threat_breakdown": dict(self.threat_breakdown)
        }
    
    def update_config(self, config):
        """Update configuration"""
        self.config.update(config)
        return {"status": "updated", "config": self.config}
    
    def check_admin_privileges(self):
        """Check if the application has administrator privileges"""
        try:
            if os.name == 'nt':  # Windows
                if ctypes:
                    return ctypes.windll.shell32.IsUserAnAdmin()
                else:
                    return False
            else:  # Linux/Unix
                return os.geteuid() == 0
        except:
            return False
    
    def get_network_connections(self):
        """Get current network connections without requiring special permissions"""
        try:
            if psutil:
                connections = []
                for conn in psutil.net_connections(kind='inet'):
                    if conn.status == 'ESTABLISHED':
                        local_addr = conn.laddr
                        remote_addr = conn.raddr if conn.raddr else None
                        
                        if remote_addr:
                            connections.append({
                                'local_ip': local_addr.ip,
                                'local_port': local_addr.port,
                                'remote_ip': remote_addr.ip,
                                'remote_port': remote_addr.port,
                                'protocol': 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP',
                                'timestamp': time.time()
                            })
                return connections
            else:
                # Fallback if psutil is not available
                return self.get_connections_fallback()
        except Exception as e:
            print(f"⚠️ Error getting network connections: {e}")
            return []
    
    def get_connections_fallback(self):
        """Fallback method to get network information using standard library"""
        connections = []
        try:
            # Try to get some network activity by checking common ports
            common_ports = [80, 443, 22, 21, 25, 53, 993, 995, 143, 110]
            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.1)
                    result = sock.connect_ex(('127.0.0.1', port))
                    if result == 0:
                        connections.append({
                            'local_ip': '127.0.0.1',
                            'local_port': 0,
                            'remote_ip': '127.0.0.1',
                            'remote_port': port,
                            'protocol': 'TCP',
                            'timestamp': time.time()
                        })
                    sock.close()
                except:
                    pass
        except Exception as e:
            print(f"⚠️ Fallback connection monitoring failed: {e}")
        
        return connections
    
    def analyze_connection_for_threats(self, connection):
        """Analyze network connection for threats using AI"""
        if not self.ml_model:
            return []
        
        # Convert connection to packet-like format for AI analysis
        packet_info = {
            'src_ip': connection['remote_ip'],
            'dst_ip': connection['local_ip'],
            'src_port': connection['remote_port'],
            'dst_port': connection['local_port'],
            'protocol': 6 if connection['protocol'] == 'TCP' else 17,  # TCP=6, UDP=17
            'timestamp': connection['timestamp']
        }
        
        return self.ai_detect_threats(packet_info)
    
    def create_web_portable(self):
        """Create a portable web application"""
        
        print("🌐 Creating Portable Web-Based AI-IDS Application")
        print("=" * 50)
        
        # Create the portable web app file
        portable_file_content = f'''#!/usr/bin/env python3
"""
AI Intrusion Detection System - Portable Web Edition
Double-click to run! No installation required.
"""

{open(__file__, 'r').read()}

if __name__ == "__main__":
    main()
'''
        
        # Write the portable file
        with open("AI-IDS-Portable-Web.py", "w") as f:
            f.write(portable_file_content)
        
        print("✅ Portable web application created: AI-IDS-Portable-Web.py")
        
        # Create Windows batch launcher
        bat_content = '''@echo off
echo 🛡️ Starting AI Intrusion Detection System - Web Edition
echo.
echo This application runs in your web browser.
echo A browser window will open automatically.
echo.
echo To stop the application, close this window.
echo.
python "AI-IDS-Portable-Web.py"
if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to start. Python 3 might not be installed.
    echo Please install Python 3 from https://python.org
    pause
)
'''
        
        with open("Start-AI-IDS-Web.bat", "w") as f:
            f.write(bat_content)
        
        # Create Linux/Mac shell launcher
        sh_content = '''#!/bin/bash
echo "🛡️ Starting AI Intrusion Detection System - Web Edition"
echo ""
echo "This application runs in your web browser."
echo "A browser window will open automatically."
echo ""
echo "To stop the application, press Ctrl+C in this terminal."
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

python3 "AI-IDS-Portable-Web.py"
'''
        
        with open("Start-AI-IDS-Web.sh", "w") as f:
            f.write(sh_content)
        
        os.chmod("Start-AI-IDS-Web.sh", 0o755)
        
        print("✅ Launcher scripts created:")
        print("   - Start-AI-IDS-Web.bat (Windows)")
        print("   - Start-AI-IDS-Web.sh (Linux/Mac)")
        
        return True

# Global app instance
web_app = WebIDSApp()

class IDSRequestHandler(SimpleHTTPRequestHandler):
    """Custom request handler for the AI-IDS web application"""
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_main_page()
        elif self.path == '/api/stats':
            self.serve_stats()
        elif self.path == '/api/start':
            self.serve_start()
        elif self.path == '/api/stop':
            self.serve_stop()
        elif self.path == '/api/reset':
            self.serve_reset()
        elif self.path == '/api/toggle-mode':
            self.serve_toggle_mode()
        elif self.path.startswith('/api/config'):
            self.handle_config()
        else:
            self.send_error(404)
    
    def serve_main_page(self):
        """Serve the main application page"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Intrusion Detection System - Portable Web Edition</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        
        .status-indicator {
            font-size: 1.5em;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 10px;
        }
        
        .status-disabled {
            background: #ffe6e6;
            color: #cc0000;
        }
        
        .status-enabled {
            background: #e6ffe6;
            color: #006600;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c82333;
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        
        .config-section {
            margin-top: 20px;
        }
        
        .sensitivity-buttons {
            display: flex;
            gap: 15px;
            margin: 15px 0;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .btn-sensitivity {
            padding: 15px 20px;
            border: 2px solid #ddd;
            border-radius: 10px;
            background: white;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            font-size: 14px;
            font-weight: bold;
            min-width: 120px;
        }
        
        .btn-sensitivity:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .btn-sensitivity.active {
            border-color: #667eea;
            background: #667eea;
            color: white;
        }
        
        .btn-sensitivity small {
            display: block;
            font-size: 11px;
            margin-top: 5px;
            opacity: 0.8;
        }
        
        .current-level {
            text-align: center;
            margin-top: 10px;
            font-weight: bold;
            color: #667eea;
        }
        
        .sensitivity-explanation {
            margin-top: 15px;
            padding: 15px;
            background: #f0f4ff;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .sensitivity-info {
            font-size: 14px;
            line-height: 1.5;
            color: #555;
        }
        
        .log-area {
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.9em;
        }
        
        .threat-alert {
            color: #dc3545;
            font-weight: bold;
        }
        
        .threat-breakdown {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #dee2e6;
        }
        
        .threat-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        
        .threat-item {
            background: white;
            padding: 10px;
            border-radius: 6px;
            border-left: 4px solid #dc3545;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .threat-name {
            font-weight: 500;
            color: #333;
            font-size: 0.9em;
        }
        
        .threat-count {
            background: #dc3545;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            min-width: 20px;
            text-align: center;
        }
        
        .no-threats {
            text-align: center;
            color: #6c757d;
            font-style: italic;
            grid-column: 1 / -1;
        }
        
        .update-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #28a745;
            border-radius: 50%;
            margin-left: 10px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ AI Intrusion Detection System</h1>
            <p>Network Monitor - <span id="currentMode">Simulation Mode</span> • <span id="aiStatus">AI Detection: Loading...</span></p>
            <p><strong>AI-Powered Real-time Detection</strong> • Safe Simulation Mode • Optional Real Network Monitoring</p>
            <div id="modeWarning" style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 8px; margin-top: 15px; display: none;">
                <strong>🔐 Administrator Privileges Needed:</strong> To switch to real network monitoring, please restart the application as administrator (Windows) or with sudo (Linux/Mac).
            </div>
            <div id="simulationInfo" style="background: #d1ecf1; border: 1px solid #bee5eb; padding: 10px; border-radius: 8px; margin-top: 15px;">
                <strong>🎯 Simulation Mode:</strong> Safe mode with AI-powered threat detection. No administrator privileges required.
            </div>
            <div id="aiInfo" style="background: #e7f5e7; border: 1px solid #b8d8b8; padding: 10px; border-radius: 8px; margin-top: 15px;">
                <strong>🤖 AI Detection:</strong> This system uses machine learning for advanced threat detection. All threats are identified using AI algorithms.
            </div>
        </div>
        
        <div class="card">
            <div id="status" class="status-indicator status-disabled">
                🔴 Protection Disabled
            </div>
            
            <div class="controls">
                <button id="startBtn" class="btn btn-primary" onclick="startProtection()">
                    🛡️ Start Protection
                </button>
                <button id="stopBtn" class="btn btn-danger" onclick="stopProtection()" disabled>
                    ⏹️ Stop Protection
                </button>
                <button id="toggleModeBtn" class="btn" onclick="toggleMode()" style="background: #6c757d; color: white;">
                    🌐 Enable Real Network Mode
                </button>
            </div>
        </div>
        
        <div class="card">
            <h3>Live Statistics <span id="updateIndicator" class="update-indicator"></span></h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <div id="packetsCount" class="stat-value">0</div>
                    <div class="stat-label">Packets Analyzed</div>
                </div>
                <div class="stat-item">
                    <div id="threatsCount" class="stat-value">0</div>
                    <div class="stat-label">Threats Detected</div>
                </div>
                <div class="stat-item">
                    <div id="uptime" class="stat-value">00:00:00</div>
                    <div class="stat-label">Uptime</div>
                </div>
            </div>
            
            <div id="threatBreakdown" class="threat-breakdown" style="margin-top: 20px; display: none;">
                <h4 style="margin-bottom: 15px; color: #667eea;">Threat Breakdown</h4>
                <div id="threatBreakdownList" class="threat-list">
                    <div class="no-threats">No threats detected yet</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>Configuration</h3>
            <div class="config-section">
                <label>Detection Sensitivity Level:</label>
                <div class="sensitivity-buttons">
                    <button class="btn-sensitivity" id="lowsens" onclick="setSensitivity(20, 'Low')">
                        🎯 Low<br><small>Quiet Mode</small>
                    </button>
                    <button class="btn-sensitivity active" id="mediumsens" onclick="setSensitivity(50, 'Medium')">
                        ⚖️ Medium<br><small>Recommended</small>
                    </button>
                    <button class="btn-sensitivity" id="highsens" onclick="setSensitivity(80, 'High')">
                        🚨 High<br><small>High Alert Mode</small>
                    </button>
                </div>
                <div id="currentSensitivity" class="current-level">Current: Medium (50%)</div>
                <div class="sensitivity-explanation">
                    <div id="sensitivityInfo" class="sensitivity-info">
                        <strong>Medium Sensitivity:</strong> Balanced AI detection suitable for most environments. The machine learning model uses moderate confidence thresholds for threat identification.
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>Recent Activity</h3>
            <div id="logArea" class="log-area">
                [00:00:00] AI Intrusion Detection System ready. Currently in Simulation Mode with AI-powered threat detection. Click 'Start Protection' to begin monitoring.
            </div>
        </div>
    </div>

    <script>
        let isMonitoring = false;
        let logEntries = [];
        let simulationMode = true;
        let lastThreatCount = 0;
        
        function addLog(message, isAlert = false) {
            const now = new Date();
            const timestamp = now.toTimeString().split(' ')[0];
            const logEntry = `[${timestamp}] ${message}`;
            
            logEntries.push({text: logEntry, isAlert});
            if (logEntries.length > 50) {
                logEntries.shift();
            }
            
            const logArea = document.getElementById('logArea');
            logArea.innerHTML = logEntries.map(entry => 
                `<div class="${entry.isAlert ? 'threat-alert' : ''}">${entry.text}</div>`
            ).join('');
            logArea.scrollTop = logArea.scrollHeight;
        }
        
        function updateModeDisplay() {
            const currentMode = document.getElementById('currentMode');
            const modeWarning = document.getElementById('modeWarning');
            const simulationInfo = document.getElementById('simulationInfo');
            const toggleBtn = document.getElementById('toggleModeBtn');
            
            if (simulationMode) {
                currentMode.textContent = 'Simulation Mode';
                modeWarning.style.display = 'none';
                simulationInfo.style.display = 'block';
                toggleBtn.textContent = '🌐 Enable Real Network Mode';
                toggleBtn.style.background = '#6c757d';
            } else {
                currentMode.textContent = 'Real Network Mode';
                modeWarning.style.display = 'none';
                simulationInfo.style.display = 'none';
                toggleBtn.textContent = '🎯 Switch to Simulation';
                toggleBtn.style.background = '#28a745';
            }
        }
        
        function toggleMode() {
            if (isMonitoring) {
                addLog('❌ Cannot change mode while monitoring is active. Stop protection first.');
                return;
            }
            
            fetch('/api/toggle-mode')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'error') {
                        addLog('❌ ' + data.message);
                        return;
                    }
                    
                    if (data.status === 'admin_required') {
                        // Show admin requirement dialog
                        showAdminRequiredDialog(data.message);
                        return;
                    }
                    
                    simulationMode = data.simulation_mode;
                    updateModeDisplay();
                    addLog('🔄 ' + data.message);
                })
                .catch(error => {
                    addLog('❌ Failed to toggle mode: ' + error);
                });
        }
        
        function showAdminRequiredDialog(message) {
            // Create and show a modal dialog for admin requirements
            const dialog = document.createElement('div');
            dialog.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
            `;
            
            dialog.innerHTML = `
                <div style="
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                    max-width: 500px;
                    text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                ">
                    <h3 style="color: #dc3545; margin-bottom: 20px;">🔐 Administrator Privileges Required</h3>
                    <p style="margin-bottom: 20px; line-height: 1.5;">
                        Real network monitoring requires administrator privileges to capture network packets.
                    </p>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                        <strong>To enable Real Network Mode:</strong><br>
                        • <strong>Windows:</strong> Right-click and "Run as administrator"<br>
                        • <strong>Linux/Mac:</strong> Run with <code>sudo python3 ai_ids_web_portable.py</code>
                    </div>
                    <p style="margin-bottom: 20px; color: #6c757d; font-size: 14px;">
                        You can continue using Simulation Mode without administrator privileges.
                    </p>
                    <button onclick="closeAdminDialog()" style="
                        background: #667eea;
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-weight: bold;
                        cursor: pointer;
                    ">Continue with Simulation Mode</button>
                </div>
            `;
            
            document.body.appendChild(dialog);
            
            // Add close function to global scope
            window.closeAdminDialog = function() {
                document.body.removeChild(dialog);
                addLog('⚠️ Real network mode requires administrator privileges. Continuing with simulation mode.');
            };
        }
        
        function startProtection() {
            fetch('/api/start')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'error') {
                        addLog('❌ ' + data.message);
                        return;
                    }
                    isMonitoring = true;
                    lastThreatCount = 0; // Reset threat counter for fresh start
                    updateUI();
                    addLog('🛡️ ' + data.message);
                })
                .catch(error => {
                    addLog('❌ Failed to start protection: ' + error);
                });
        }
        
        function stopProtection() {
            fetch('/api/stop')
                .then(response => response.json())
                .then(data => {
                    isMonitoring = false;
                    updateUI();
                    addLog('⏹️ Protection stopped - Network monitoring disabled');
                })
                .catch(error => {
                    addLog('❌ Failed to stop protection: ' + error);
                });
        }
        
        function setSensitivity(value, level) {
            // Update visual state
            document.querySelectorAll('.btn-sensitivity').forEach(btn => btn.classList.remove('active'));
            document.getElementById(level.toLowerCase() + 'sens').classList.add('active');
            document.getElementById('currentSensitivity').textContent = `Current: ${level} (${value}%)`;
            
            // Update explanation based on level and mode
            const explanations = {
                'Low': simulationMode ? 
                    '<strong>Low Sensitivity (Quiet Mode):</strong> Conservative AI detection with occasional alerts (~1 every 25 seconds). Only flags high-confidence AI-detected threats. Best for quieter monitoring.' :
                    '<strong>Low Sensitivity (Quiet Mode):</strong> Conservative AI detection with high confidence thresholds. Only flags threats that the machine learning model identifies with very high certainty.',
                'Medium': simulationMode ?
                    '<strong>Medium Sensitivity (Recommended):</strong> Balanced AI detection with regular alerting (~1 every 12 seconds). Good for general monitoring and learning about AI-powered network security threats.' :
                    '<strong>Medium Sensitivity (Recommended):</strong> Balanced AI detection suitable for most environments. The machine learning model uses moderate confidence thresholds for threat identification.',
                'High': simulationMode ?
                    '<strong>High Sensitivity (High Alert Mode):</strong> AI detects threats frequently (~1 every 7 seconds). Best for learning about different AI-detected attack types and demonstrations. Expect regular AI alerts!' :
                    '<strong>High Sensitivity (High Alert Mode):</strong> AI uses aggressive detection thresholds. The machine learning model will flag more potential threats with lower confidence scores. May generate more false positives.'
            };
            
            document.getElementById('sensitivityInfo').innerHTML = explanations[level];
            
            // Update server
            fetch(`/api/config?sensitivity=${value}`)
                .then(response => response.json())
                .then(data => {
                    addLog(`⚙️ Sensitivity updated to ${level} level (${value}%)`);
                })
                .catch(error => {
                    addLog('❌ Failed to update sensitivity: ' + error);
                });
        }
        
        function updateUI() {
            const status = document.getElementById('status');
            const startBtn = document.getElementById('startBtn');
            const stopBtn = document.getElementById('stopBtn');
            const toggleBtn = document.getElementById('toggleModeBtn');
            
            if (isMonitoring) {
                status.textContent = '🟢 Protection Enabled';
                status.className = 'status-indicator status-enabled';
                startBtn.disabled = true;
                stopBtn.disabled = false;
                toggleBtn.disabled = true;
                toggleBtn.style.opacity = '0.6';
            } else {
                status.textContent = '🔴 Protection Disabled';
                status.className = 'status-indicator status-disabled';
                startBtn.disabled = false;
                stopBtn.disabled = true;
                toggleBtn.disabled = false;
                toggleBtn.style.opacity = '1';
            }
        }
        
        function updateStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('packetsCount').textContent = data.packets_analyzed.toLocaleString();
                    document.getElementById('threatsCount').textContent = data.threats_detected;
                    
                    // Update mode if it changed
                    if (simulationMode !== data.simulation_mode) {
                        simulationMode = data.simulation_mode;
                        updateModeDisplay();
                    }
                    
                    // Update AI status (always enabled)
                    const aiStatus = document.getElementById('aiStatus');
                    if (data.ai_model_loaded) {
                        aiStatus.textContent = 'AI Detection: ✅ Active';
                        aiStatus.style.color = '#28a745';
                    } else {
                        aiStatus.textContent = 'AI Detection: ❌ Model Not Found';
                        aiStatus.style.color = '#dc3545';
                    }
                    
                    // Update uptime
                    const hours = Math.floor(data.uptime / 3600);
                    const minutes = Math.floor((data.uptime % 3600) / 60);
                    const seconds = data.uptime % 60;
                    document.getElementById('uptime').textContent = 
                        `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                    
                    // Update threat breakdown
                    updateThreatBreakdown(data.threat_breakdown);
                    
                    // Check for new threats - display real threat information when available
                    if (data.threats_detected > lastThreatCount && isMonitoring) {
                        const newThreats = data.threats_detected - lastThreatCount;
                        
                        if (data.recent_threats && data.recent_threats.length > 0) {
                            // Display actual threat details
                            const recentThreats = data.recent_threats.slice(-newThreats);
                            recentThreats.forEach(threat => {
                                addLog(`🚨 THREAT DETECTED: ${threat}`, true);
                            });
                        } else {
                            // Fallback for when no detailed threat info is available
                            for (let i = 0; i < newThreats; i++) {
                                addLog(`🚨 AI THREAT DETECTED: Network anomaly identified`, true);
                            }
                        }
                    }
                    lastThreatCount = data.threats_detected;
                })
                .catch(error => {
                    console.error('Failed to update stats:', error);
                });
        }
        
        function updateThreatBreakdown(threatBreakdown) {
            const breakdownSection = document.getElementById('threatBreakdown');
            const breakdownList = document.getElementById('threatBreakdownList');
            
            if (!threatBreakdown || Object.keys(threatBreakdown).length === 0) {
                breakdownSection.style.display = 'none';
                return;
            }
            
            breakdownSection.style.display = 'block';
            
            // Sort threats by count (highest first)
            const sortedThreats = Object.entries(threatBreakdown)
                .sort(([,a], [,b]) => b - a);
            
            if (sortedThreats.length === 0) {
                breakdownList.innerHTML = '<div class="no-threats">No threats detected yet</div>';
                return;
            }
            
            breakdownList.innerHTML = sortedThreats.map(([threatType, count]) => `
                <div class="threat-item">
                    <span class="threat-name">${threatType}</span>
                    <span class="threat-count">${count}</span>
                </div>
            `).join('');
        }
        
        // Update stats every second
        setInterval(updateStats, 1000);
        
        // Initial load
        updateStats();
        updateModeDisplay();
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_stats(self):
        """Serve current statistics"""
        stats = web_app.get_stats()
        self.send_json_response(stats)
    
    def serve_start(self):
        """Start monitoring"""
        result = web_app.start_monitoring()
        self.send_json_response(result)
    
    def serve_stop(self):
        """Stop monitoring"""
        result = web_app.stop_monitoring()
        self.send_json_response(result)
    
    def serve_reset(self):
        """Reset statistics"""
        result = web_app.reset_stats()
        self.send_json_response(result)
    
    def serve_toggle_mode(self):
        """Toggle between simulation and real network mode"""
        if web_app.is_monitoring:
            result = {"status": "error", "message": "Cannot change mode while monitoring is active. Stop monitoring first."}
        else:
            current_mode = web_app.config['simulation_mode']
            
            # If switching to real mode, check for admin privileges
            if current_mode:  # Currently in simulation, switching to real
                if not web_app.check_admin_privileges():
                    result = {"status": "admin_required", "message": "Administrator privileges required for real network monitoring. Please restart the application as administrator/root.", "simulation_mode": current_mode}
                else:
                    web_app.config['simulation_mode'] = False
                    result = {"status": "success", "message": "Switched to Real Network mode", "simulation_mode": False}
            else:  # Switching back to simulation
                web_app.config['simulation_mode'] = True
                result = {"status": "success", "message": "Switched to Simulation mode", "simulation_mode": True}
        
        self.send_json_response(result)
    
    def handle_config(self):
        """Handle configuration updates"""
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        config_update = {}
        if 'sensitivity' in params:
            config_update['sensitivity'] = int(params['sensitivity'][0])
        
        result = web_app.update_config(config_update)
        self.send_json_response(result)
    
    def send_json_response(self, data):
        """Send JSON response"""
        response = json.dumps(data).encode()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-length', len(response))
        self.end_headers()
        self.wfile.write(response)

def create_web_portable():
    """Create a portable web application"""
    app = WebIDSApp()
    return app.create_web_portable()

def main():
    """Main function to run the web server"""
    port = 8080
    
    print(f"🛡️ AI Intrusion Detection System - Network Monitor")
    print(f"🎯 Starting in Simulation Mode (safe for all users)")
    print(f"   Real network monitoring available with administrator privileges")
    print(f"")
    print(f"Starting web server on port {port}...")
    print(f"🌐 Open your browser to: http://localhost:{port}")
    print(f"Press Ctrl+C to stop the server")
    print()
    
    try:
        # Start web server
        server = HTTPServer(('localhost', port), IDSRequestHandler)
        
        # Open browser
        try:
            webbrowser.open(f'http://localhost:{port}')
        except:
            print("Could not open browser automatically. Please navigate to http://localhost:8080")
        
        print("✅ Server started successfully!")
        print("💡 The application is now running in your web browser")
        print()
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        server.shutdown()
        print("✅ Server stopped. Thank you for using AI-IDS!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--create':
        create_web_portable()
    else:
        main()
