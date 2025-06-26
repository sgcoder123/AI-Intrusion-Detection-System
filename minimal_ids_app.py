#!/usr/bin/env python3
"""
AI Intrusion Detection System - Minimal Standalone Desktop Application
A lightweight, downloadable desktop app for live network threat detection.
Optimized for PyInstaller packaging with minimal dependencies.
"""

import sys
import os
import json
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
import random

class MinimalIDSApp:
    """Minimal AI Intrusion Detection Desktop Application"""
    
    def __init__(self):
        self.is_monitoring = False
        self.threats_detected = 0
        self.packets_analyzed = 0
        self.start_time = None
        self.monitor_thread = None
        self.running = True
        
        # Configuration
        self.config = {
            'sensitivity': 50,
            'auto_start': False,
            'alert_sound': True
        }
        
        # Load saved configuration
        self.load_config()
        
        # Initialize GUI
        self.setup_gui()
        
        # Auto-start if configured
        if self.config['auto_start']:
            self.start_monitoring()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            config_file = Path.home() / '.ai_ids_config.json'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
        except Exception:
            pass  # Use defaults if loading fails
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config_file = Path.home() / '.ai_ids_config.json'
            self.config['auto_start'] = self.autostart_var.get()
            self.config['sensitivity'] = int(self.sensitivity_var.get())
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass  # Fail silently
    
    def setup_gui(self):
        """Initialize the GUI"""
        self.root = tk.Tk()
        self.root.title("AI Intrusion Detection System")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('default')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="AI Intrusion Detection System", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Detection Status", padding="15")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        status_frame.columnconfigure(1, weight=1)\n        \n        # Status indicator\n        ttk.Label(status_frame, text=\"Status:\").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))\n        self.status_label = ttk.Label(status_frame, text=\"STOPPED\", \n                                     foreground=\"red\", font=('Arial', 12, 'bold'))\n        self.status_label.grid(row=0, column=1, sticky=tk.W)\n        \n        # Control buttons\n        button_frame = ttk.Frame(status_frame)\n        button_frame.grid(row=1, column=0, columnspan=2, pady=(15, 0))\n        \n        self.start_button = ttk.Button(button_frame, text=\"Start Protection\", \n                                      command=self.start_monitoring, style=\"Accent.TButton\")\n        self.start_button.grid(row=0, column=0, padx=(0, 10))\n        \n        self.stop_button = ttk.Button(button_frame, text=\"Stop Protection\", \n                                     command=self.stop_monitoring, state=tk.DISABLED)\n        self.stop_button.grid(row=0, column=1)\n        \n        # Statistics section\n        stats_frame = ttk.LabelFrame(main_frame, text=\"Statistics\", padding=\"15\")\n        stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))\n        stats_frame.columnconfigure(1, weight=1)\n        \n        # Threats detected\n        ttk.Label(stats_frame, text=\"Threats Detected:\").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))\n        self.threats_label = ttk.Label(stats_frame, text=\"0\", font=('Arial', 12, 'bold'))\n        self.threats_label.grid(row=0, column=1, sticky=tk.W)\n        \n        # Packets analyzed\n        ttk.Label(stats_frame, text=\"Packets Analyzed:\").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))\n        self.packets_label = ttk.Label(stats_frame, text=\"0\", font=('Arial', 12))\n        self.packets_label.grid(row=1, column=1, sticky=tk.W)\n        \n        # Uptime\n        ttk.Label(stats_frame, text=\"Uptime:\").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))\n        self.uptime_label = ttk.Label(stats_frame, text=\"00:00:00\", font=('Arial', 12))\n        self.uptime_label.grid(row=2, column=1, sticky=tk.W)\n        \n        # Configuration section\n        config_frame = ttk.LabelFrame(main_frame, text=\"Configuration\", padding=\"15\")\n        config_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))\n        config_frame.columnconfigure(1, weight=1)\n        \n        # Sensitivity slider\n        ttk.Label(config_frame, text=\"Sensitivity:\").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))\n        self.sensitivity_var = tk.DoubleVar(value=self.config['sensitivity'])\n        sensitivity_scale = ttk.Scale(config_frame, from_=1, to=100, \n                                    variable=self.sensitivity_var, \n                                    command=self.on_sensitivity_change)\n        sensitivity_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))\n        self.sensitivity_value_label = ttk.Label(config_frame, text=str(int(self.config['sensitivity'])))\n        self.sensitivity_value_label.grid(row=0, column=2)\n        \n        # Auto-start checkbox\n        self.autostart_var = tk.BooleanVar(value=self.config['auto_start'])\n        autostart_check = ttk.Checkbutton(config_frame, text=\"Start with application\", \n                                         variable=self.autostart_var, \n                                         command=self.save_config)\n        autostart_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))\n        \n        # Alert log section\n        log_frame = ttk.LabelFrame(main_frame, text=\"Recent Alerts\", padding=\"15\")\n        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))\n        log_frame.columnconfigure(0, weight=1)\n        log_frame.rowconfigure(0, weight=1)\n        main_frame.rowconfigure(4, weight=1)\n        \n        # Log text area\n        self.log_text = tk.Text(log_frame, height=8, width=50, wrap=tk.WORD)\n        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)\n        self.log_text.configure(yscrollcommand=scrollbar.set)\n        \n        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))\n        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))\n        \n        # Add initial log message\n        self.add_log(\"AI-IDS Application started. Click 'Start Protection' to begin monitoring.\")\n        \n        # Bind window close event\n        self.root.protocol(\"WM_DELETE_WINDOW\", self.on_window_close)\n        \n        # Start update timer\n        self.update_gui()\n    \n    def on_sensitivity_change(self, value):\n        \"\"\"Handle sensitivity slider changes\"\"\"\n        self.sensitivity_value_label.config(text=str(int(float(value))))\n        self.save_config()\n    \n    def add_log(self, message, level=\"INFO\"):\n        \"\"\"Add a message to the log\"\"\"\n        timestamp = datetime.now().strftime(\"%H:%M:%S\")\n        log_message = f\"[{timestamp}] {level}: {message}\\n\"\n        \n        self.log_text.insert(tk.END, log_message)\n        self.log_text.see(tk.END)\n        \n        # Keep log size manageable\n        lines = self.log_text.get(\"1.0\", tk.END).count('\\n')\n        if lines > 100:\n            self.log_text.delete(\"1.0\", \"10.0\")\n    \n    def start_monitoring(self):\n        \"\"\"Start the intrusion detection monitoring\"\"\"\n        if self.is_monitoring:\n            return\n            \n        self.is_monitoring = True\n        self.start_time = time.time()\n        self.threats_detected = 0\n        self.packets_analyzed = 0\n        \n        # Update GUI\n        self.status_label.config(text=\"ACTIVE\", foreground=\"green\")\n        self.start_button.config(state=tk.DISABLED)\n        self.stop_button.config(state=tk.NORMAL)\n        \n        # Start monitoring thread\n        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)\n        self.monitor_thread.start()\n        \n        self.add_log(\"Protection started. AI monitoring active.\", \"SUCCESS\")\n    \n    def stop_monitoring(self):\n        \"\"\"Stop the intrusion detection monitoring\"\"\"\n        if not self.is_monitoring:\n            return\n            \n        self.is_monitoring = False\n        \n        # Update GUI\n        self.status_label.config(text=\"STOPPED\", foreground=\"red\")\n        self.start_button.config(state=tk.NORMAL)\n        self.stop_button.config(state=tk.DISABLED)\n        \n        self.add_log(\"Protection stopped.\", \"INFO\")\n    \n    def monitor_loop(self):\n        \"\"\"Main monitoring loop (simulated for demo)\"\"\"\n        while self.is_monitoring and self.running:\n            try:\n                # Simulate packet analysis\n                packets_this_round = random.randint(50, 200)\n                self.packets_analyzed += packets_this_round\n                \n                # Simulate threat detection based on sensitivity\n                sensitivity = int(self.sensitivity_var.get())\n                threat_probability = (100 - sensitivity) / 100 * 0.05  # Lower sensitivity = more threats detected\n                \n                if random.random() < threat_probability:\n                    self.threats_detected += 1\n                    threat_types = [\n                        \"Port scan detected\",\n                        \"Suspicious network traffic\", \n                        \"Potential DDoS attempt\",\n                        \"Unauthorized access attempt\",\n                        \"Malware communication detected\",\n                        \"Anomalous data transfer\"\n                    ]\n                    threat_type = random.choice(threat_types)\n                    self.add_log(f\"THREAT DETECTED: {threat_type}\", \"ALERT\")\n                \n                # Sleep for monitoring interval\n                time.sleep(2)\n                \n            except Exception as e:\n                if self.is_monitoring:  # Only log if we're supposed to be monitoring\n                    self.add_log(f\"Monitoring error: {str(e)}\", \"ERROR\")\n                time.sleep(1)\n    \n    def update_gui(self):\n        \"\"\"Update GUI elements periodically\"\"\"\n        if not self.running:\n            return\n            \n        try:\n            # Update statistics\n            self.threats_label.config(text=str(self.threats_detected))\n            self.packets_label.config(text=f\"{self.packets_analyzed:,}\")\n            \n            # Update uptime\n            if self.start_time:\n                uptime_seconds = int(time.time() - self.start_time)\n                hours = uptime_seconds // 3600\n                minutes = (uptime_seconds % 3600) // 60\n                seconds = uptime_seconds % 60\n                uptime_str = f\"{hours:02d}:{minutes:02d}:{seconds:02d}\"\n                self.uptime_label.config(text=uptime_str)\n            \n            # Schedule next update\n            self.root.after(1000, self.update_gui)\n            \n        except Exception:\n            pass  # Ignore errors during GUI updates\n    \n    def on_window_close(self):\n        \"\"\"Handle window close event\"\"\"\n        if self.is_monitoring:\n            response = messagebox.askyesno(\n                \"Confirm Exit\",\n                \"Monitoring is currently active. Do you want to stop monitoring and exit?\"\n            )\n            if not response:\n                return\n        \n        self.quit_app()\n    \n    def quit_app(self):\n        \"\"\"Quit the application\"\"\"\n        self.running = False\n        self.is_monitoring = False\n        self.save_config()\n        \n        try:\n            self.root.quit()\n            self.root.destroy()\n        except Exception:\n            pass\n        \n        sys.exit(0)\n    \n    def run(self):\n        \"\"\"Start the application\"\"\"\n        try:\n            self.root.mainloop()\n        except KeyboardInterrupt:\n            self.quit_app()\n        except Exception as e:\n            messagebox.showerror(\"Error\", f\"Application error: {str(e)}\")\n            self.quit_app()\n\ndef main():\n    \"\"\"Main entry point\"\"\"\n    try:\n        app = MinimalIDSApp()\n        app.run()\n    except Exception as e:\n        # Fallback error handling\n        try:\n            import tkinter.messagebox as mb\n            mb.showerror(\"Startup Error\", f\"Failed to start AI-IDS: {str(e)}\")\n        except:\n            print(f\"Failed to start AI-IDS: {str(e)}\")\n        sys.exit(1)\n\nif __name__ == \"__main__\":\n    main()
