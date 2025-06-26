#!/usr/bin/env python3
"""
Integrated Real-Time Intrusion Detection System
Combines packet monitoring, threat detection, and web dashboard.
"""

import sys
import time
import threading
import argparse
import signal
import logging
from pathlib import Path

# Add Flask to requirements
import subprocess
import os

# Import our modules
from realtime_monitor import RealTimeIDSMonitor
from dashboard import IDSDashboard
from config import IDSConfig

logger = logging.getLogger(__name__)

class IntegratedIDS:
    """Integrated IDS with monitoring and dashboard"""
    
    def __init__(self, config_file: str = 'ids_config.yaml'):
        self.config = IDSConfig(config_file)
        self.monitor = None
        self.dashboard = None
        self.dashboard_thread = None
        self.is_running = False
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get('logging.level', 'INFO'))
        log_file = self.config.get('logging.file', 'intrusion_detection.log')
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def install_dependencies(self):
        """Install required dependencies"""
        try:
            # Check if Flask is installed
            import flask
            logger.info("✅ Flask already installed")
        except ImportError:
            logger.info("📦 Installing Flask...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask', 'pyyaml'])
            logger.info("✅ Flask installed successfully")
    
    def start_dashboard(self):
        """Start the web dashboard in a separate thread"""
        if self.config.get('monitoring.enable_web_dashboard', True):
            host = self.config.get('monitoring.dashboard_host', '127.0.0.1')
            port = self.config.get('monitoring.dashboard_port', 8080)
            
            self.dashboard = IDSDashboard(host=host, port=port)
            
            def run_dashboard():
                try:
                    self.dashboard.start()
                except Exception as e:
                    logger.error(f"Dashboard error: {e}")
            
            self.dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
            self.dashboard_thread.start()
            
            # Give dashboard time to start
            time.sleep(2)
            logger.info(f"🌐 Dashboard available at http://{host}:{port}")
    
    def start_monitoring(self):
        """Start the packet monitoring"""
        # Get configuration
        interface = self.config.get('network.interface')
        if interface == 'auto':
            interface = None
        
        model_path = self.config.get('detection.model_path')
        if not os.path.isabs(model_path):
            # Make path relative to project root
            project_root = Path(__file__).parent.parent
            model_path = project_root / model_path
        
        # Create monitor
        self.monitor = RealTimeIDSMonitor(
            interface=interface,
            model_path=str(model_path)
        )
        
        # Configure monitor
        self.monitor.alert_threshold = self.config.get('detection.confidence_threshold', 0.8)
        
        # Setup dashboard integration
        if self.dashboard:
            self._setup_dashboard_integration()
        
        # Start monitoring
        logger.info("🚀 Starting integrated IDS system...")
        self.is_running = True
        
        try:
            self.monitor.start_monitoring()
        except KeyboardInterrupt:
            logger.info("🛑 Received interrupt signal")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
        finally:
            self.stop()
    
    def _setup_dashboard_integration(self):
        """Setup integration between monitor and dashboard"""
        original_handle_threat = self.monitor._handle_threat_detection
        original_log_progress = self.monitor._log_progress
        
        def enhanced_handle_threat(features, result, packet):
            # Call original method
            original_handle_threat(features, result, packet)
            
            # Update dashboard
            if self.dashboard:
                alert = {
                    'timestamp': time.time(),
                    'source_ip': features.get('src_ip', 'unknown'),
                    'destination_ip': features.get('dst_ip', 'unknown'),
                    'attack_type': result['prediction'],
                    'confidence': result['confidence'],
                    'protocol': features.get('protocol_type', 'unknown'),
                    'service': features.get('service', 'unknown'),
                    'packet_size': features.get('src_bytes', 0)
                }
                self.dashboard.add_alert(alert)
        
        def enhanced_log_progress():
            # Call original method
            original_log_progress()
            
            # Update dashboard stats
            if self.dashboard and self.monitor.start_time:
                runtime = time.time() - self.monitor.start_time
                current_rate = self.monitor.packets_processed / runtime if runtime > 0 else 0
                
                stats = {
                    'packets_processed': self.monitor.packets_processed,
                    'threats_detected': self.monitor.threats_detected,
                    'is_running': self.monitor.is_running,
                    'current_rate': current_rate
                }
                self.dashboard.update_stats(stats)
        
        # Replace methods
        self.monitor._handle_threat_detection = enhanced_handle_threat
        self.monitor._log_progress = enhanced_log_progress
    
    def stop(self):
        """Stop the IDS system"""
        self.is_running = False
        if self.monitor:
            self.monitor.stop_monitoring()
        logger.info("✅ IDS system stopped")
    
    def get_status(self):
        """Get system status"""
        status = {
            'is_running': self.is_running,
            'config_file': self.config.config_file,
            'dashboard_enabled': self.config.get('monitoring.enable_web_dashboard', True)
        }
        
        if self.monitor:
            status.update(self.monitor.get_status())
        
        return status

def signal_handler(signum, frame, ids_system):
    """Handle graceful shutdown"""
    print("\n🛑 Shutting down IDS system...")
    ids_system.stop()
    sys.exit(0)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Integrated AI Intrusion Detection System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Start with default config
  %(prog)s -i eth0 -t 0.9          # Monitor eth0 with 90%% confidence threshold
  %(prog)s --no-dashboard          # Run without web dashboard
  %(prog)s --dashboard-port 9000   # Use custom dashboard port
        """
    )
    
    parser.add_argument('--interface', '-i', 
                       help='Network interface to monitor (auto-detect if not specified)')
    parser.add_argument('--model', '-m', 
                       help='Path to model file (uses config default if not specified)')
    parser.add_argument('--threshold', '-t', type=float, 
                       help='Alert confidence threshold (0.0-1.0)')
    parser.add_argument('--config', '-c', default='ids_config.yaml',
                       help='Configuration file path')
    parser.add_argument('--dashboard-port', type=int,
                       help='Web dashboard port')
    parser.add_argument('--no-dashboard', action='store_true',
                       help='Disable web dashboard')
    parser.add_argument('--status', action='store_true',
                       help='Show system status and exit')
    
    args = parser.parse_args()
    
    try:
        # Create IDS system
        ids = IntegratedIDS(args.config)
        
        # Setup signal handler
        signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, ids))
        
        # Setup logging
        ids.setup_logging()
        
        # Update config from command line args
        ids.config.update_from_args(args)
        
        if args.no_dashboard:
            ids.config.set('monitoring.enable_web_dashboard', False)
        
        if args.dashboard_port:
            ids.config.set('monitoring.dashboard_port', args.dashboard_port)
        
        # Install dependencies
        ids.install_dependencies()
        
        # Show status if requested
        if args.status:
            status = ids.get_status()
            print("📊 IDS System Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
            return
        
        # Show startup info
        print("🛡️  AI Intrusion Detection System")
        print("=" * 50)
        print(f"📁 Config file: {ids.config.config_file}")
        print(f"🔧 Model: {ids.config.get('detection.model_path')}")
        print(f"🎯 Threshold: {ids.config.get('detection.confidence_threshold')}")
        print(f"🌐 Dashboard: {'Enabled' if ids.config.get('monitoring.enable_web_dashboard') else 'Disabled'}")
        print("=" * 50)
        
        # Start dashboard
        if ids.config.get('monitoring.enable_web_dashboard', True):
            ids.start_dashboard()
        
        # Start monitoring
        ids.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start IDS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
