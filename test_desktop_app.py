#!/usr/bin/env python3
"""
Desktop App Test Script
Verifies functionality of the AI-IDS desktop application
"""

import sys
import os
import time
import threading
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        # Test GUI libraries
        import tkinter as tk
        print("✅ tkinter - GUI framework")
    except ImportError:
        print("❌ tkinter - not available")
    
    try:
        import pystray
        print("✅ pystray - system tray")
    except ImportError:
        print("⚠️ pystray - not available (system tray disabled)")
    
    try:
        from PIL import Image
        print("✅ PIL - image processing")
    except ImportError:
        print("⚠️ PIL - not available (icons disabled)")
    
    # Test IDS modules
    try:
        from src.config import IDSConfig
        print("✅ IDSConfig - configuration")
    except ImportError as e:
        print(f"❌ IDSConfig - {e}")
    
    try:
        from src.realtime_monitor import RealTimeIDSMonitor
        print("✅ RealTimeIDSMonitor - monitoring")
    except ImportError as e:
        print("⚠️ RealTimeIDSMonitor - not available")
    
    try:
        from src.dashboard import IDSDashboard
        print("✅ IDSDashboard - web interface")
    except ImportError as e:
        print("⚠️ IDSDashboard - not available")
    
    print()

def test_desktop_app_creation():
    """Test desktop app instantiation"""
    print("🖥️ Testing desktop app creation...")
    
    try:
        sys.path.append('desktop_app')
        from desktop_app.ids_desktop_app import IDSDesktopApp
        
        app = IDSDesktopApp()
        print("✅ Desktop app created successfully")
        
        # Test configuration
        if hasattr(app, 'config') and app.config:
            print("✅ Configuration loaded")
        else:
            print("⚠️ Configuration not available")
        
        # Test logging
        if hasattr(app, 'logger'):
            app.logger.info("Test log message")
            print("✅ Logging system working")
        
        return app
        
    except Exception as e:
        print(f"❌ Desktop app creation failed: {e}")
        return None

def test_autostart_detection():
    """Test autostart functionality detection"""
    print("🚀 Testing autostart detection...")
    
    try:
        from desktop_app.ids_desktop_app import IDSDesktopApp
        app = IDSDesktopApp()
        
        if hasattr(app, 'is_autostart_enabled'):
            is_enabled = app.is_autostart_enabled()
            print(f"✅ Autostart detection: {'Enabled' if is_enabled else 'Disabled'}")
        else:
            print("⚠️ Autostart detection not available")
            
    except Exception as e:
        print(f"❌ Autostart detection failed: {e}")

def test_gui_creation():
    """Test GUI creation (headless safe)"""
    print("🎨 Testing GUI creation...")
    
    try:
        import tkinter as tk
        
        # Test if display is available
        try:
            root = tk.Tk()
            root.withdraw()  # Hide window
            print("✅ GUI framework available")
            root.destroy()
        except tk.TclError:
            print("⚠️ No display available (headless mode)")
            
    except ImportError:
        print("❌ tkinter not available")

def test_model_loading():
    """Test ML model loading"""
    print("🤖 Testing model loading...")
    
    models_dir = Path("models")
    if not models_dir.exists():
        print("⚠️ Models directory not found")
        return
    
    model_files = list(models_dir.glob("*.joblib"))
    if model_files:
        print(f"✅ Found {len(model_files)} model files")
        for model in model_files:
            print(f"   📄 {model.name}")
    else:
        print("⚠️ No model files found")
    
    # Test model loading
    try:
        import joblib
        for model_file in model_files[:1]:  # Test first model only
            model = joblib.load(model_file)
            print(f"✅ Model loaded: {model_file.name}")
            break
    except Exception as e:
        print(f"❌ Model loading failed: {e}")

def test_web_dashboard():
    """Test web dashboard startup"""
    print("🌐 Testing web dashboard...")
    
    try:
        from src.dashboard import IDSDashboard
        
        # Create dashboard instance
        dashboard = IDSDashboard()
        print("✅ Dashboard instance created")
        
        # Test in background thread (won't actually start server in test)
        print("⚠️ Dashboard server test skipped (would bind to port)")
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")

def test_configuration():
    """Test configuration system"""
    print("⚙️ Testing configuration...")
    
    try:
        from src.config import IDSConfig
        
        config = IDSConfig()
        print("✅ Configuration instance created")
        
        # Test some default values
        port = config.get('monitoring.dashboard_port', 8080)
        threshold = config.get('detection.confidence_threshold', 0.8)
        
        print(f"✅ Dashboard port: {port}")
        print(f"✅ Detection threshold: {threshold}")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

def test_service_installation():
    """Test service installation capabilities"""
    print("🔧 Testing service installation...")
    
    try:
        from install_service import ServiceInstaller
        
        installer = ServiceInstaller()
        print("✅ Service installer created")
        
        # Test admin detection (safe to run)
        is_admin = installer.is_admin()
        print(f"✅ Admin privileges: {'Yes' if is_admin else 'No'}")
        
        # Test service status check (safe)
        status = installer.check_service_status()
        print(f"✅ Service status check: {'Running' if status else 'Stopped'}")
        
    except Exception as e:
        print(f"❌ Service test failed: {e}")

def run_quick_demo():
    """Run a quick demo of key functionality"""
    print("🎮 Running quick demo...")
    
    try:
        from desktop_app.ids_desktop_app import IDSDesktopApp
        
        app = IDSDesktopApp()
        
        # Simulate some statistics
        app.stats['packets_processed'] = 1000
        app.stats['threats_detected'] = 5
        
        print("✅ Demo app created with sample stats")
        print(f"   📊 Packets: {app.stats['packets_processed']}")
        print(f"   🚨 Threats: {app.stats['threats_detected']}")
        
        # Test alert system
        app.add_alert("Test alert: Demo threat detected")
        print("✅ Alert system tested")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def main():
    """Run all tests"""
    print("🛡️ AI-IDS Desktop App Test Suite")
    print("=" * 40)
    print()
    
    # Run tests
    test_imports()
    test_desktop_app_creation()
    test_autostart_detection()
    test_gui_creation()
    test_model_loading()
    test_web_dashboard()
    test_configuration()
    test_service_installation()
    run_quick_demo()
    
    print()
    print("🎉 Test suite completed!")
    print()
    print("💡 Next steps:")
    print("   1. Run: python desktop_app/ids_desktop_app.py")
    print("   2. Or build: ./build_desktop_app.sh")
    print("   3. Or package: python package_desktop_app.py")
    print("   4. Or install service: python install_service.py install")

if __name__ == "__main__":
    main()
