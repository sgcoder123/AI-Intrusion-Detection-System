#!/usr/bin/env python3
"""
Demo script for AI Intrusion Detection System Real-Time Monitoring
Shows how the system would work without requiring root privileges.
"""

import sys
import time
import random
import threading
from datetime import datetime
import json

# Add src to path
sys.path.append('.')

from deploy_model import IntrusionDetector
from dashboard import IDSDashboard

class IDSDemo:
    """Demo of the IDS system with simulated network data"""
    
    def __init__(self):
        print("🛡️  AI Intrusion Detection System - Demo Mode")
        print("=" * 60)
        
        # Load the model
        print("📦 Loading trained model...")
        self.detector = IntrusionDetector()
        info = self.detector.get_model_info()
        print(f"✅ Model loaded: {info['model_type']} with {info['n_features']} features")
        
        # Initialize dashboard
        print("🌐 Starting web dashboard...")
        self.dashboard = IDSDashboard(host='127.0.0.1', port=8080)
        
        # Stats
        self.packets_processed = 0
        self.threats_detected = 0
        self.start_time = datetime.now()
        
        # Sample attack types for demo
        self.attack_types = [
            'normal', 'normal', 'normal', 'normal', 'normal',  # Most traffic is normal
            'ipsweep', 'portsweep', 'satan', 'nmap', 'back',
            'neptune', 'smurf', 'teardrop', 'pod', 'land'
        ]
        
    def generate_sample_features(self) -> list:
        """Generate realistic network features for demo"""
        # These are sample features that match the model's expected input
        features = [
            random.uniform(0, 100),      # duration
            random.choice([0, 1, 2]),    # protocol_type (tcp, udp, icmp)
            random.choice([0, 1, 2, 3]), # service
            random.choice([0, 1, 2, 3]), # flag
            random.randint(0, 65535),    # src_bytes
            random.randint(0, 65535),    # dst_bytes
            random.choice([0, 1]),       # land
            0,                           # wrong_fragment
            random.randint(0, 3),        # urgent
            random.randint(0, 100),      # hot
            random.randint(0, 5),        # num_failed_logins
            random.choice([0, 1]),       # logged_in
            random.randint(0, 10),       # num_compromised
            random.choice([0, 1]),       # root_shell
            random.choice([0, 1]),       # su_attempted
            random.randint(0, 5),        # num_root
            random.randint(0, 10),       # num_file_creations
            random.randint(0, 5),        # num_shells
            random.randint(0, 10),       # num_access_files
            random.randint(0, 5),        # num_outbound_cmds
            random.choice([0, 1]),       # is_host_login
            random.choice([0, 1]),       # is_guest_login
            random.randint(1, 500),      # count
            random.randint(1, 500),      # srv_count
            random.uniform(0, 1),        # serror_rate
            random.uniform(0, 1),        # srv_serror_rate
            random.uniform(0, 1),        # rerror_rate
            random.uniform(0, 1),        # srv_rerror_rate
            random.uniform(0, 1),        # same_srv_rate
            random.uniform(0, 1),        # diff_srv_rate
            random.uniform(0, 1),        # srv_diff_host_rate
            random.randint(1, 255),      # dst_host_count
            random.randint(1, 255),      # dst_host_srv_count
            random.uniform(0, 1),        # dst_host_same_srv_rate
            random.uniform(0, 1),        # dst_host_diff_srv_rate
            random.uniform(0, 1),        # dst_host_same_src_port_rate
            random.uniform(0, 1),        # dst_host_srv_diff_host_rate
            random.uniform(0, 1),        # dst_host_serror_rate
            random.uniform(0, 1),        # dst_host_srv_serror_rate
            random.uniform(0, 1),        # dst_host_rerror_rate
            random.uniform(0, 1),        # dst_host_srv_rerror_rate
        ]
        return features
    
    def simulate_packet_processing(self):
        """Simulate processing network packets"""
        print("📡 Starting packet simulation...")
        
        while True:
            try:
                # Generate sample network features
                features = self.generate_sample_features()
                
                # Make prediction
                result = self.detector.predict_single(features)
                
                # Update stats
                self.packets_processed += 1
                
                # Check for threats
                if result['is_attack'] and result['confidence'] > 0.8:
                    self.threats_detected += 1
                    
                    # Create alert for dashboard
                    alert = {
                        'timestamp': datetime.now().isoformat(),
                        'source_ip': f"192.168.1.{random.randint(1, 254)}",
                        'destination_ip': f"10.0.0.{random.randint(1, 254)}",
                        'attack_type': result['prediction'],
                        'confidence': result['confidence'],
                        'protocol': random.choice(['tcp', 'udp', 'icmp']),
                        'service': random.choice(['http', 'https', 'ssh', 'ftp']),
                        'packet_size': random.randint(64, 1500)
                    }
                    
                    self.dashboard.add_alert(alert)
                    
                    print(f"🚨 THREAT DETECTED: {alert['attack_type']} from {alert['source_ip']} "
                          f"(confidence: {alert['confidence']:.3f})")
                
                # Update dashboard stats
                runtime = (datetime.now() - self.start_time).total_seconds()
                current_rate = self.packets_processed / runtime if runtime > 0 else 0
                
                stats = {
                    'packets_processed': self.packets_processed,
                    'threats_detected': self.threats_detected,
                    'is_running': True,
                    'current_rate': current_rate
                }
                self.dashboard.update_stats(stats)
                
                # Log progress
                if self.packets_processed % 50 == 0:
                    print(f"📊 Processed: {self.packets_processed} packets, "
                          f"Threats: {self.threats_detected}, "
                          f"Rate: {current_rate:.1f} pps")
                
                # Simulate packet arrival rate
                time.sleep(random.uniform(0.1, 0.5))
                
            except KeyboardInterrupt:
                print("\n🛑 Demo stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in demo: {e}")
                time.sleep(1)
    
    def start_dashboard_thread(self):
        """Start dashboard in background thread"""
        def run_dashboard():
            try:
                self.dashboard.start()
            except Exception as e:
                print(f"Dashboard error: {e}")
        
        dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        dashboard_thread.start()
        
        # Give dashboard time to start
        time.sleep(2)
        print(f"✅ Dashboard available at: http://127.0.0.1:8080")
    
    def run_demo(self):
        """Run the complete demo"""
        try:
            # Start dashboard
            self.start_dashboard_thread()
            
            print("\n📋 Demo Information:")
            print("  - This demo simulates network packet processing")
            print("  - Random network features are generated and classified")
            print("  - Threats are detected based on the trained ML model")
            print("  - View real-time results at: http://127.0.0.1:8080")
            print("  - Press Ctrl+C to stop the demo")
            print("\n" + "=" * 60)
            
            # Start packet simulation
            self.simulate_packet_processing()
            
        except KeyboardInterrupt:
            print("\n✅ Demo completed successfully!")
        except Exception as e:
            print(f"❌ Demo failed: {e}")

def main():
    """Main demo function"""
    try:
        demo = IDSDemo()
        demo.run_demo()
    except Exception as e:
        print(f"Failed to start demo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
