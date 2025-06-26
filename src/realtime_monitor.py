#!/usr/bin/env python3
"""
Real-Time Network Packet Monitor for AI Intrusion Detection System
Captures and analyzes network packets in real-time for intrusion detection.
"""

import logging
import time
import threading
import queue
import signal
import sys
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Network and system libraries
import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.l2 import Ether
import psutil

# Data processing
import pandas as pd
import numpy as np

# Our intrusion detection model
from deploy_model import IntrusionDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('intrusion_detection.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NetworkFeatureExtractor:
    """Extract features from network packets for intrusion detection model"""
    
    def __init__(self):
        self.connection_states = {}
        self.service_map = self._create_service_map()
        self.flag_map = self._create_flag_map()
        
    def _create_service_map(self) -> Dict[int, str]:
        """Map common ports to service names"""
        return {
            20: 'ftp_data', 21: 'ftp', 22: 'ssh', 23: 'telnet',
            25: 'smtp', 53: 'domain', 80: 'http', 110: 'pop_3',
            143: 'imap4', 443: 'https', 993: 'imaps', 995: 'pop_3s',
            22: 'ssh', 161: 'snmp', 443: 'ssl', 993: 'imap4',
            135: 'loc-srv', 139: 'netbios-ssn', 445: 'microsoft-ds',
            1433: 'ms-sql-s', 3389: 'ms-wbt-server'
        }
    
    def _create_flag_map(self) -> Dict[str, int]:
        """Map TCP flags to numeric values"""
        return {
            'S': 1,    # SYN
            'A': 2,    # ACK  
            'F': 4,    # FIN
            'R': 8,    # RST
            'P': 16,   # PSH
            'U': 32,   # URG
            'E': 64,   # ECE
            'C': 128   # CWR
        }
    
    def extract_features(self, packet) -> Optional[Dict[str, Any]]:
        """Extract features from a single packet"""
        try:
            if not packet.haslayer(IP):
                return None
                
            features = {}
            ip_layer = packet[IP]
            
            # Basic connection info
            features['src_ip'] = ip_layer.src
            features['dst_ip'] = ip_layer.dst
            features['protocol_type'] = self._get_protocol_type(packet)
            
            # Duration (simplified - using timestamp)
            features['duration'] = 0
            
            # Service
            features['service'] = self._get_service(packet)
            
            # Flag
            features['flag'] = self._get_flag(packet)
            
            # Packet size features
            features['src_bytes'] = len(packet) if hasattr(packet, '__len__') else 0
            features['dst_bytes'] = 0  # Would need connection tracking for accurate value
            
            # Land attack detection
            features['land'] = 1 if ip_layer.src == ip_layer.dst else 0
            
            # Wrong fragment
            features['wrong_fragment'] = 0
            
            # Urgent packets
            features['urgent'] = self._get_urgent_count(packet)
            
            # Initialize traffic features with defaults
            traffic_features = {
                'hot': 0, 'num_failed_logins': 0, 'logged_in': 0,
                'num_compromised': 0, 'root_shell': 0, 'su_attempted': 0,
                'num_root': 0, 'num_file_creations': 0, 'num_shells': 0,
                'num_access_files': 0, 'num_outbound_cmds': 0,
                'is_host_login': 0, 'is_guest_login': 0, 'count': 1,
                'srv_count': 1, 'serror_rate': 0.0, 'srv_serror_rate': 0.0,
                'rerror_rate': 0.0, 'srv_rerror_rate': 0.0,
                'same_srv_rate': 1.0, 'diff_srv_rate': 0.0,
                'srv_diff_host_rate': 0.0, 'dst_host_count': 1,
                'dst_host_srv_count': 1, 'dst_host_same_srv_rate': 1.0,
                'dst_host_diff_srv_rate': 0.0, 'dst_host_same_src_port_rate': 0.0,
                'dst_host_srv_diff_host_rate': 0.0, 'dst_host_serror_rate': 0.0,
                'dst_host_srv_serror_rate': 0.0, 'dst_host_rerror_rate': 0.0,
                'dst_host_srv_rerror_rate': 0.0
            }
            
            features.update(traffic_features)
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None
    
    def _get_protocol_type(self, packet) -> str:
        """Get protocol type from packet"""
        if packet.haslayer(TCP):
            return 'tcp'
        elif packet.haslayer(UDP):
            return 'udp'
        elif packet.haslayer(ICMP):
            return 'icmp'
        else:
            return 'other'
    
    def _get_service(self, packet) -> str:
        """Get service name from packet"""
        if packet.haslayer(TCP):
            dst_port = packet[TCP].dport
        elif packet.haslayer(UDP):
            dst_port = packet[UDP].dport
        else:
            return 'other'
            
        return self.service_map.get(dst_port, 'other')
    
    def _get_flag(self, packet) -> str:
        """Get TCP flag from packet"""
        if packet.haslayer(TCP):
            flags = packet[TCP].flags
            if flags & 0x02:  # SYN
                return 'S0' if not (flags & 0x10) else 'S1'  # No ACK vs ACK
            elif flags & 0x01:  # FIN
                return 'SF'
            elif flags & 0x04:  # RST
                return 'REJ'
            else:
                return 'SF'
        return 'OTH'
    
    def _get_urgent_count(self, packet) -> int:
        """Get urgent packet count"""
        if packet.haslayer(TCP) and packet[TCP].flags & 0x20:  # URG flag
            return 1
        return 0

class RealTimeIDSMonitor:
    """Real-time intrusion detection system monitor"""
    
    def __init__(self, interface: str = None, model_path: str = None):
        self.interface = interface or self._get_default_interface()
        self.detector = IntrusionDetector(model_path)
        self.feature_extractor = NetworkFeatureExtractor()
        
        # Monitoring state
        self.is_running = False
        self.packet_queue = queue.Queue(maxsize=1000)
        self.detection_stats = defaultdict(int)
        self.recent_alerts = deque(maxlen=100)
        
        # Performance tracking
        self.packets_processed = 0
        self.threats_detected = 0
        self.start_time = None
        
        # Alert thresholds
        self.alert_threshold = 0.8  # Confidence threshold for alerts
        self.rate_limit = defaultdict(lambda: deque(maxlen=10))  # Rate limiting per IP
        
        logger.info(f"Initialized IDS Monitor on interface: {self.interface}")
    
    def _get_default_interface(self) -> str:
        """Get the default network interface"""
        try:
            # Get the interface with internet connectivity
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            
            for iface_name, iface_stats in stats.items():
                if iface_stats.isup and iface_name != 'lo':
                    if iface_name in addrs:
                        return iface_name
            
            return scapy.conf.iface  # Fallback to scapy default
        except Exception as e:
            logger.warning(f"Could not determine interface, using default: {e}")
            return scapy.conf.iface
    
    def packet_handler(self, packet):
        """Handle captured packets"""
        try:
            if not self.packet_queue.full():
                self.packet_queue.put(packet, block=False)
            else:
                logger.warning("Packet queue full, dropping packet")
        except Exception as e:
            logger.error(f"Error in packet handler: {e}")
    
    def process_packets(self):
        """Process packets from the queue"""
        while self.is_running:
            try:
                # Get packet from queue with timeout
                packet = self.packet_queue.get(timeout=1.0)
                
                # Extract features
                features = self.feature_extractor.extract_features(packet)
                if not features:
                    continue
                
                # Convert to model format
                feature_vector = self._prepare_features_for_model(features)
                if feature_vector is None:
                    continue
                
                # Make prediction
                result = self.detector.predict_single(feature_vector)
                
                # Update statistics
                self.packets_processed += 1
                
                # Check for threats
                if result['is_attack'] and result['confidence'] > self.alert_threshold:
                    self._handle_threat_detection(features, result, packet)
                
                # Log progress
                if self.packets_processed % 100 == 0:
                    self._log_progress()
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing packet: {e}")
    
    def _prepare_features_for_model(self, features: Dict[str, Any]) -> Optional[np.ndarray]:
        """Convert extracted features to model input format"""
        try:
            # Define the expected feature order (matching your model training)
            feature_order = [
                'duration', 'protocol_type', 'service', 'flag', 'src_bytes',
                'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
                'num_failed_logins', 'logged_in', 'num_compromised',
                'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
                'num_shells', 'num_access_files', 'num_outbound_cmds',
                'is_host_login', 'is_guest_login', 'count', 'srv_count',
                'serror_rate', 'srv_serror_rate', 'rerror_rate',
                'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
                'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
                'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
                'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate',
                'dst_host_serror_rate', 'dst_host_srv_serror_rate',
                'dst_host_rerror_rate', 'dst_host_srv_rerror_rate'
            ]
            
            # Extract values in correct order
            feature_values = []
            for feature_name in feature_order:
                value = features.get(feature_name, 0)
                
                # Handle categorical features
                if feature_name == 'protocol_type':
                    # Convert to numeric (tcp=0, udp=1, icmp=2, other=3)
                    protocol_map = {'tcp': 0, 'udp': 1, 'icmp': 2, 'other': 3}
                    value = protocol_map.get(value, 3)
                elif feature_name == 'service':
                    # Convert service to numeric (simplified)
                    service_map = {'http': 1, 'https': 2, 'ftp': 3, 'ssh': 4, 'other': 0}
                    value = service_map.get(value, 0)
                elif feature_name == 'flag':
                    # Convert flag to numeric
                    flag_map = {'SF': 0, 'S0': 1, 'REJ': 2, 'RSTR': 3, 'OTH': 4}
                    value = flag_map.get(value, 4)
                
                feature_values.append(float(value))
            
            return np.array(feature_values).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None
    
    def _handle_threat_detection(self, features: Dict[str, Any], result: Dict[str, Any], packet):
        """Handle detected threats"""
        self.threats_detected += 1
        
        # Rate limiting check
        src_ip = features.get('src_ip', 'unknown')
        now = time.time()
        self.rate_limit[src_ip].append(now)
        
        # Check if this IP is generating too many alerts
        recent_alerts = [t for t in self.rate_limit[src_ip] if now - t < 60]  # Last minute
        if len(recent_alerts) > 5:  # More than 5 alerts per minute
            logger.debug(f"Rate limiting alerts from {src_ip}")
            return
        
        # Create alert
        alert = {
            'timestamp': datetime.now().isoformat(),
            'source_ip': src_ip,
            'destination_ip': features.get('dst_ip', 'unknown'),
            'attack_type': result['prediction'],
            'confidence': result['confidence'],
            'protocol': features.get('protocol_type', 'unknown'),
            'service': features.get('service', 'unknown'),
            'packet_size': features.get('src_bytes', 0)
        }
        
        self.recent_alerts.append(alert)
        
        # Log alert
        logger.warning(
            f"🚨 THREAT DETECTED: {alert['attack_type']} from {src_ip} "
            f"(confidence: {alert['confidence']:.3f})"
        )
        
        # Save alert to file
        self._save_alert(alert)
    
    def _save_alert(self, alert: Dict[str, Any]):
        """Save alert to file"""
        try:
            with open('security_alerts.json', 'a') as f:
                f.write(json.dumps(alert) + '\n')
        except Exception as e:
            logger.error(f"Error saving alert: {e}")
    
    def _log_progress(self):
        """Log monitoring progress"""
        if self.start_time:
            runtime = time.time() - self.start_time
            pps = self.packets_processed / runtime if runtime > 0 else 0
            
            logger.info(
                f"📊 Processed: {self.packets_processed} packets, "
                f"Threats: {self.threats_detected}, "
                f"Rate: {pps:.1f} pps"
            )
    
    def start_monitoring(self):
        """Start the real-time monitoring"""
        logger.info("🚀 Starting real-time intrusion detection monitoring...")
        
        self.is_running = True
        self.start_time = time.time()
        
        # Start packet processing thread
        processing_thread = threading.Thread(target=self.process_packets, daemon=True)
        processing_thread.start()
        
        # Start packet capture
        try:
            logger.info(f"👁️  Monitoring network interface: {self.interface}")
            logger.info("Press Ctrl+C to stop monitoring...")
            
            scapy.sniff(
                iface=self.interface,
                prn=self.packet_handler,
                store=False,
                stop_filter=lambda x: not self.is_running
            )
            
        except KeyboardInterrupt:
            logger.info("🛑 Stopping monitoring...")
        except Exception as e:
            logger.error(f"Error during monitoring: {e}")
        finally:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop the monitoring"""
        self.is_running = False
        logger.info("✅ Monitoring stopped")
        
        # Print final statistics
        if self.start_time:
            runtime = time.time() - self.start_time
            logger.info(f"📈 Final Stats:")
            logger.info(f"  - Runtime: {runtime:.1f} seconds")
            logger.info(f"  - Packets processed: {self.packets_processed}")
            logger.info(f"  - Threats detected: {self.threats_detected}")
            logger.info(f"  - Average rate: {self.packets_processed/runtime:.1f} pps")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            'is_running': self.is_running,
            'interface': self.interface,
            'packets_processed': self.packets_processed,
            'threats_detected': self.threats_detected,
            'recent_alerts': list(self.recent_alerts)[-5:],  # Last 5 alerts
            'uptime': time.time() - self.start_time if self.start_time else 0
        }

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Received interrupt signal. Stopping monitoring...")
    sys.exit(0)

def main():
    """Main function to run the real-time IDS monitor"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-Time Network Intrusion Detection Monitor')
    parser.add_argument('--interface', '-i', help='Network interface to monitor')
    parser.add_argument('--model', '-m', help='Path to model file')
    parser.add_argument('--threshold', '-t', type=float, default=0.8, 
                       help='Alert confidence threshold (0.0-1.0)')
    
    args = parser.parse_args()
    
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Create and start monitor
        monitor = RealTimeIDSMonitor(
            interface=args.interface,
            model_path=args.model
        )
        
        monitor.alert_threshold = args.threshold
        monitor.start_monitoring()
        
    except Exception as e:
        logger.error(f"Failed to start monitoring: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
