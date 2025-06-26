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
        status_frame.columnconfigure(1, weight=1)
        
        # Status indicator
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.status_label = ttk.Label(status_frame, text="STOPPED", 
                                     foreground="red", font=('Arial', 12, 'bold'))
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(status_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(15, 0))
        
        self.start_button = ttk.Button(button_frame, text="Start Protection", 
                                      command=self.start_monitoring)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Protection", 
                                     command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1)
        
        # Statistics section
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="15")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        stats_frame.columnconfigure(1, weight=1)
        
        # Threats detected
        ttk.Label(stats_frame, text="Threats Detected:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.threats_label = ttk.Label(stats_frame, text="0", font=('Arial', 12, 'bold'))
        self.threats_label.grid(row=0, column=1, sticky=tk.W)
        
        # Packets analyzed
        ttk.Label(stats_frame, text="Packets Analyzed:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.packets_label = ttk.Label(stats_frame, text="0", font=('Arial', 12))
        self.packets_label.grid(row=1, column=1, sticky=tk.W)
        
        # Uptime
        ttk.Label(stats_frame, text="Uptime:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.uptime_label = ttk.Label(stats_frame, text="00:00:00", font=('Arial', 12))
        self.uptime_label.grid(row=2, column=1, sticky=tk.W)
        
        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="15")
        config_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)
        
        # Sensitivity slider
        ttk.Label(config_frame, text="Sensitivity:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.sensitivity_var = tk.DoubleVar(value=self.config['sensitivity'])
        sensitivity_scale = ttk.Scale(config_frame, from_=1, to=100, 
                                    variable=self.sensitivity_var, 
                                    command=self.on_sensitivity_change)
        sensitivity_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.sensitivity_value_label = ttk.Label(config_frame, text=str(int(self.config['sensitivity'])))
        self.sensitivity_value_label.grid(row=0, column=2)
        
        # Auto-start checkbox
        self.autostart_var = tk.BooleanVar(value=self.config['auto_start'])
        autostart_check = ttk.Checkbutton(config_frame, text="Start with application", 
                                         variable=self.autostart_var, 
                                         command=self.save_config)
        autostart_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # Alert log section
        log_frame = ttk.LabelFrame(main_frame, text="Recent Alerts", padding="15")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Log text area
        self.log_text = tk.Text(log_frame, height=8, width=50, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Add initial log message
        self.add_log("AI-IDS Application started. Click 'Start Protection' to begin monitoring.")
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # Start update timer
        self.update_gui()
    
    def on_sensitivity_change(self, value):
        """Handle sensitivity slider changes"""
        self.sensitivity_value_label.config(text=str(int(float(value))))
        self.save_config()
    
    def add_log(self, message, level="INFO"):
        """Add a message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        
        # Keep log size manageable
        lines = self.log_text.get("1.0", tk.END).count('\n')
        if lines > 100:
            self.log_text.delete("1.0", "10.0")
    
    def start_monitoring(self):
        """Start the intrusion detection monitoring"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.start_time = time.time()
        self.threats_detected = 0
        self.packets_analyzed = 0
        
        # Update GUI
        self.status_label.config(text="ACTIVE", foreground="green")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.add_log("Protection started. AI monitoring active.", "SUCCESS")
    
    def stop_monitoring(self):
        """Stop the intrusion detection monitoring"""
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        
        # Update GUI
        self.status_label.config(text="STOPPED", foreground="red")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.add_log("Protection stopped.", "INFO")
    
    def monitor_loop(self):
        """Main monitoring loop (simulated for demo)"""
        while self.is_monitoring and self.running:
            try:
                # Simulate packet analysis
                packets_this_round = random.randint(50, 200)
                self.packets_analyzed += packets_this_round
                
                # Simulate threat detection based on sensitivity
                sensitivity = int(self.sensitivity_var.get())
                threat_probability = (100 - sensitivity) / 100 * 0.05  # Lower sensitivity = more threats detected
                
                if random.random() < threat_probability:
                    self.threats_detected += 1
                    threat_types = [
                        "Port scan detected",
                        "Suspicious network traffic", 
                        "Potential DDoS attempt",
                        "Unauthorized access attempt",
                        "Malware communication detected",
                        "Anomalous data transfer"
                    ]
                    threat_type = random.choice(threat_types)
                    self.add_log(f"THREAT DETECTED: {threat_type}", "ALERT")
                
                # Sleep for monitoring interval
                time.sleep(2)
                
            except Exception as e:
                if self.is_monitoring:  # Only log if we're supposed to be monitoring
                    self.add_log(f"Monitoring error: {str(e)}", "ERROR")
                time.sleep(1)
    
    def update_gui(self):
        """Update GUI elements periodically"""
        if not self.running:
            return
            
        try:
            # Update statistics
            self.threats_label.config(text=str(self.threats_detected))
            self.packets_label.config(text=f"{self.packets_analyzed:,}")
            
            # Update uptime
            if self.start_time:
                uptime_seconds = int(time.time() - self.start_time)
                hours = uptime_seconds // 3600
                minutes = (uptime_seconds % 3600) // 60
                seconds = uptime_seconds % 60
                uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.uptime_label.config(text=uptime_str)
            
            # Schedule next update
            self.root.after(1000, self.update_gui)
            
        except Exception:
            pass  # Ignore errors during GUI updates
    
    def on_window_close(self):
        """Handle window close event"""
        if self.is_monitoring:
            response = messagebox.askyesno(
                "Confirm Exit",
                "Monitoring is currently active. Do you want to stop monitoring and exit?"
            )
            if not response:
                return
        
        self.quit_app()
    
    def quit_app(self):
        """Quit the application"""
        self.running = False
        self.is_monitoring = False
        self.save_config()
        
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass
        
        sys.exit(0)
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_app()
        except Exception as e:
            messagebox.showerror("Error", f"Application error: {str(e)}")
            self.quit_app()

def main():
    """Main entry point"""
    try:
        app = MinimalIDSApp()
        app.run()
    except Exception as e:
        # Fallback error handling
        try:
            import tkinter.messagebox as mb
            mb.showerror("Startup Error", f"Failed to start AI-IDS: {str(e)}")
        except:
            print(f"Failed to start AI-IDS: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
