#!/usr/bin/env python3
"""
Web Dashboard for Real-Time Intrusion Detection System
Provides a simple web interface to monitor the IDS status and alerts.
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict, deque

# Web framework
from flask import Flask, render_template, jsonify, request
import logging

# Disable Flask's default logging for cleaner output
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class IDSDashboard:
    """Web dashboard for IDS monitoring"""
    
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.app.secret_key = 'ids_dashboard_secret_key'
        
        # Dashboard data
        self.stats = {
            'start_time': datetime.now(),
            'packets_processed': 0,
            'threats_detected': 0,
            'is_running': False,
            'current_rate': 0.0
        }
        
        self.alerts = deque(maxlen=1000)  # Store last 1000 alerts
        self.recent_stats = deque(maxlen=60)  # Store last 60 stats updates
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return render_template('dashboard.html')
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get current statistics"""
            uptime = (datetime.now() - self.stats['start_time']).total_seconds()
            
            return jsonify({
                'uptime': uptime,
                'packets_processed': self.stats['packets_processed'],
                'threats_detected': self.stats['threats_detected'],
                'is_running': self.stats['is_running'],
                'current_rate': self.stats['current_rate'],
                'alerts_count': len(self.alerts)
            })
        
        @self.app.route('/api/alerts')
        def get_alerts():
            """Get recent alerts"""
            limit = request.args.get('limit', 50, type=int)
            recent_alerts = list(self.alerts)[-limit:]
            return jsonify(recent_alerts)
        
        @self.app.route('/api/chart_data')
        def get_chart_data():
            """Get data for charts"""
            # Threat types distribution
            threat_types = defaultdict(int)
            for alert in self.alerts:
                threat_types[alert.get('attack_type', 'unknown')] += 1
            
            # Timeline data (alerts per minute)
            timeline = defaultdict(int)
            now = datetime.now()
            for alert in self.alerts:
                try:
                    alert_time = datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00'))
                    minute_key = alert_time.strftime('%H:%M')
                    timeline[minute_key] += 1
                except:
                    continue
            
            return jsonify({
                'threat_types': dict(threat_types),
                'timeline': dict(timeline),
                'rate_history': list(self.recent_stats)
            })
        
        @self.app.route('/api/network_info')
        def get_network_info():
            """Get network interface information"""
            import psutil
            
            interfaces = []
            for iface_name, iface_stats in psutil.net_if_stats().items():
                if iface_stats.isup and iface_name != 'lo':
                    addrs = psutil.net_if_addrs().get(iface_name, [])
                    ip_addresses = [addr.address for addr in addrs if addr.family == 2]  # IPv4
                    
                    interfaces.append({
                        'name': iface_name,
                        'is_up': iface_stats.isup,
                        'speed': iface_stats.speed,
                        'ip_addresses': ip_addresses
                    })
            
            return jsonify(interfaces)
    
    def update_stats(self, monitor_stats: Dict[str, Any]):
        """Update dashboard statistics"""
        self.stats.update({
            'packets_processed': monitor_stats.get('packets_processed', 0),
            'threats_detected': monitor_stats.get('threats_detected', 0),
            'is_running': monitor_stats.get('is_running', False),
            'current_rate': monitor_stats.get('current_rate', 0.0)
        })
        
        # Store for rate history
        self.recent_stats.append({
            'timestamp': time.time(),
            'rate': monitor_stats.get('current_rate', 0.0),
            'threats': monitor_stats.get('threats_detected', 0)
        })
    
    def add_alert(self, alert: Dict[str, Any]):
        """Add new alert to dashboard"""
        self.alerts.append(alert)
    
    def start(self):
        """Start the dashboard server"""
        # Create templates directory and files if they don't exist
        self._create_template_files()
        
        print(f"🌐 Starting IDS Dashboard at http://{self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=False, threaded=True)
    
    def _create_template_files(self):
        """Create HTML template files"""
        import os
        
        templates_dir = 'templates'
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        
        # Create dashboard.html
        dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Intrusion Detection System - Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
        .stat-value { font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }
        .stat-label { color: #666; font-size: 1.1em; }
        .running { color: #4CAF50; }
        .stopped { color: #f44336; }
        .charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .chart-container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .alerts-section { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .alert-item { padding: 15px; border-left: 4px solid #f44336; margin-bottom: 10px; background: #fff3f3; border-radius: 5px; }
        .alert-time { font-size: 0.9em; color: #666; }
        .alert-details { margin-top: 5px; }
        .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        .status-running { background: #4CAF50; animation: pulse 1.5s infinite; }
        .status-stopped { background: #f44336; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        @media (max-width: 768px) { .charts-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ AI Intrusion Detection System</h1>
            <p>Real-time network security monitoring and threat detection</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="status">
                    <span class="status-indicator" id="status-indicator"></span>
                    <span id="status-text">Loading...</span>
                </div>
                <div class="stat-label">System Status</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="packets-processed">0</div>
                <div class="stat-label">Packets Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="threats-detected">0</div>
                <div class="stat-label">Threats Detected</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="current-rate">0.0</div>
                <div class="stat-label">Current Rate (pps)</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-container">
                <h3>Threat Types Distribution</h3>
                <canvas id="threatTypesChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>Detection Rate Over Time</h3>
                <canvas id="rateChart"></canvas>
            </div>
        </div>
        
        <div class="alerts-section">
            <h3>Recent Security Alerts</h3>
            <div id="alerts-container">
                <p>No alerts yet...</p>
            </div>
        </div>
    </div>

    <script>
        // Dashboard JavaScript
        let threatTypesChart, rateChart;
        
        // Initialize charts
        function initCharts() {
            const ctx1 = document.getElementById('threatTypesChart').getContext('2d');
            threatTypesChart = new Chart(ctx1, {
                type: 'doughnut',
                data: { labels: [], datasets: [{ data: [], backgroundColor: ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0'] }] },
                options: { responsive: true, maintainAspectRatio: false }
            });
            
            const ctx2 = document.getElementById('rateChart').getContext('2d');
            rateChart = new Chart(ctx2, {
                type: 'line',
                data: { labels: [], datasets: [{ label: 'Packet Rate', data: [], borderColor: '#36a2eb', fill: false }] },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
            });
        }
        
        // Update dashboard data
        function updateDashboard() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('packets-processed').textContent = data.packets_processed.toLocaleString();
                    document.getElementById('threats-detected').textContent = data.threats_detected.toLocaleString();
                    document.getElementById('current-rate').textContent = data.current_rate.toFixed(1);
                    
                    const statusIndicator = document.getElementById('status-indicator');
                    const statusText = document.getElementById('status-text');
                    if (data.is_running) {
                        statusIndicator.className = 'status-indicator status-running';
                        statusText.textContent = 'Running';
                        statusText.className = 'running';
                    } else {
                        statusIndicator.className = 'status-indicator status-stopped';
                        statusText.textContent = 'Stopped';
                        statusText.className = 'stopped';
                    }
                });
            
            fetch('/api/alerts?limit=10')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('alerts-container');
                    if (data.length === 0) {
                        container.innerHTML = '<p>No alerts yet...</p>';
                    } else {
                        container.innerHTML = data.reverse().map(alert => `
                            <div class="alert-item">
                                <div class="alert-time">${new Date(alert.timestamp).toLocaleString()}</div>
                                <div class="alert-details">
                                    <strong>${alert.attack_type}</strong> from ${alert.source_ip} 
                                    (confidence: ${(alert.confidence * 100).toFixed(1)}%)
                                </div>
                            </div>
                        `).join('');
                    }
                });
            
            fetch('/api/chart_data')
                .then(response => response.json())
                .then(data => {
                    // Update threat types chart
                    threatTypesChart.data.labels = Object.keys(data.threat_types);
                    threatTypesChart.data.datasets[0].data = Object.values(data.threat_types);
                    threatTypesChart.update();
                    
                    // Update rate chart
                    const rateHistory = data.rate_history.slice(-20); // Last 20 points
                    rateChart.data.labels = rateHistory.map((_, i) => i);
                    rateChart.data.datasets[0].data = rateHistory.map(h => h.rate);
                    rateChart.update();
                });
        }
        
        // Initialize
        initCharts();
        updateDashboard();
        setInterval(updateDashboard, 5000); // Update every 5 seconds
    </script>
</body>
</html>'''
        
        with open(os.path.join(templates_dir, 'dashboard.html'), 'w') as f:
            f.write(dashboard_html)

def main():
    """Start the dashboard server"""
    dashboard = IDSDashboard()
    dashboard.start()

if __name__ == "__main__":
    main()
