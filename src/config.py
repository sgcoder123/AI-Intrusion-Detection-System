#!/usr/bin/env python3
"""
Configuration file for AI Intrusion Detection System
"""

import yaml
import os
from typing import Dict, Any

class IDSConfig:
    """Configuration manager for IDS"""
    
    DEFAULT_CONFIG = {
        'network': {
            'interface': 'auto',  # 'auto' for auto-detection
            'promiscuous_mode': False,
            'buffer_size': 1000,
        },
        'detection': {
            'model_path': 'models/random_forest_model_tuned.joblib',
            'confidence_threshold': 0.8,
            'rate_limit_window': 60,  # seconds
            'rate_limit_max': 5,  # max alerts per window per IP
        },
        'alerts': {
            'log_file': 'security_alerts.json',
            'enable_email': False,
            'email_smtp': 'smtp.gmail.com',
            'email_port': 587,
            'email_user': '',
            'email_password': '',
            'email_recipients': [],
            'enable_webhook': False,
            'webhook_url': '',
        },
        'logging': {
            'level': 'INFO',
            'file': 'intrusion_detection.log',
            'max_size_mb': 10,
            'backup_count': 5,
        },
        'monitoring': {
            'enable_web_dashboard': True,
            'dashboard_port': 8080,
            'dashboard_host': '127.0.0.1',
            'stats_update_interval': 5,  # seconds
        }
    }
    
    def __init__(self, config_file: str = 'ids_config.yaml'):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = yaml.safe_load(f)
                # Merge with defaults for missing keys
                return self._merge_configs(self.DEFAULT_CONFIG, config)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        config = config or self.config
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key_path: str, default=None):
        """Get config value using dot notation (e.g., 'network.interface')"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value):
        """Set config value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def update_from_args(self, args):
        """Update config from command line arguments"""
        if hasattr(args, 'interface') and args.interface:
            self.set('network.interface', args.interface)
        
        if hasattr(args, 'model') and args.model:
            self.set('detection.model_path', args.model)
        
        if hasattr(args, 'threshold') and args.threshold is not None:
            self.set('detection.confidence_threshold', args.threshold)
        
        if hasattr(args, 'dashboard_port') and args.dashboard_port:
            self.set('monitoring.dashboard_port', args.dashboard_port)

# Create default config instance
config = IDSConfig()
