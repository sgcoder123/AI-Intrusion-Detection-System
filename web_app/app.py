#!/usr/bin/env python3
"""
Web Application for AI Intrusion Detection System Download Portal
Allows users to download and install the IDS system for live protection.
"""

from flask import Flask, render_template, send_file, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
import os
import json
import zipfile
import tempfile
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
import sqlite3
from functools import wraps

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')
app.secret_key = 'ids_download_portal_secret_key_2025'
CORS(app)

# Configuration
DOWNLOAD_DIR = Path(__file__).parent.parent
DATABASE_FILE = 'downloads.db'
ALLOWED_PLATFORMS = ['windows', 'linux', 'macos']

class DownloadPortal:
    """Main download portal application"""
    
    def __init__(self):
        self.init_database()
        self.setup_routes()
        
    def init_database(self):
        """Initialize SQLite database for tracking downloads"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Create downloads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT,
                user_agent TEXT,
                platform TEXT,
                download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                email TEXT,
                organization TEXT
            )
        ''')
        
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                rating INTEGER,
                comments TEXT,
                submit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @app.route('/')
        def index():
            """Main download portal page"""
            stats = self.get_download_stats()
            return render_template('index.html', stats=stats)
        
        @app.route('/download')
        def download_page():
            """Download page with platform selection"""
            return render_template('download.html')
        
        @app.route('/api/download/<platform>')
        def download_package(platform):
            """Generate and serve download package"""
            if platform not in ALLOWED_PLATFORMS:
                return jsonify({'error': 'Invalid platform'}), 400
            
            try:
                # Get user info from form
                email = request.args.get('email', '')
                organization = request.args.get('organization', '')
                
                # Map platform to actual files
                downloads_dir = Path(__file__).parent / 'static' / 'downloads'
                
                if platform == 'windows':
                    filename = 'AI-IDS-Desktop-v1.0.0.zip'
                    file_path = downloads_dir / filename
                elif platform == 'linux':
                    filename = 'AI-IDS-Desktop-v1.0.0.tar.gz'  
                    file_path = downloads_dir / filename
                elif platform == 'macos':
                    filename = 'AI-IDS-Desktop-v1.0.0.zip'  # Universal package
                    file_path = downloads_dir / filename
                else:
                    return jsonify({'error': 'Invalid platform'}), 400
                
                # Check if file exists
                if not file_path.exists():
                    logger.error(f"Download file not found: {file_path}")
                    return jsonify({'error': 'Download file not available'}), 404
                
                # Log download
                self.log_download(request.remote_addr, request.user_agent.string, 
                                platform, email, organization)
                
                # Serve file
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=filename
                )
                
            except Exception as e:
                logger.error(f"Download error: {e}")
                return jsonify({'error': 'Download failed'}), 500
        
        @app.route('/install/<platform>')
        def installation_guide(platform):
            """Installation guide for specific platform"""
            if platform not in ALLOWED_PLATFORMS:
                return redirect(url_for('index'))
            
            return render_template(f'install_{platform}.html', platform=platform)
        
        @app.route('/documentation')
        def documentation():
            """Documentation page"""
            return render_template('documentation.html')
        
        @app.route('/getting-started')
        def getting_started():
            """Getting started guide"""
            # Read the getting started markdown file and convert to HTML
            try:
                getting_started_path = Path(__file__).parent.parent / 'GETTING_STARTED.md'
                with open(getting_started_path, 'r') as f:
                    content = f.read()
                # Simple markdown to HTML conversion for display
                # Replace headers and basic formatting
                html_content = content.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
                html_content = html_content.replace('## ', '<h2>').replace('\n', '</h2>\n')
                html_content = html_content.replace('### ', '<h3>').replace('\n', '</h3>\n')
                html_content = html_content.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
                html_content = html_content.replace('`', '<code>', 1).replace('`', '</code>', 1)
                html_content = html_content.replace('\n\n', '</p><p>')
                html_content = '<p>' + html_content + '</p>'
                return render_template('getting_started.html', content=html_content)
            except Exception as e:
                return f"<h1>Getting Started Guide</h1><p>Error loading guide: {e}</p>"
        
        @app.route('/support')
        def support():
            """Support and troubleshooting page"""
            return render_template('support.html')
        
        @app.route('/api/feedback', methods=['POST'])
        def submit_feedback():
            """Submit user feedback"""
            try:
                data = request.get_json()
                email = data.get('email', '')
                rating = data.get('rating', 0)
                comments = data.get('comments', '')
                
                conn = sqlite3.connect(DATABASE_FILE)
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO feedback (email, rating, comments) VALUES (?, ?, ?)',
                    (email, rating, comments)
                )
                conn.commit()
                conn.close()
                
                return jsonify({'success': True})
                
            except Exception as e:
                logger.error(f"Feedback error: {e}")
                return jsonify({'error': 'Failed to submit feedback'}), 500
        
        @app.route('/api/stats')
        def get_stats_api():
            """Get download statistics API"""
            stats = self.get_download_stats()
            return jsonify(stats)
        
        @app.route('/demo')
        def live_demo():
            """Live demo page"""
            return render_template('demo.html')
        
        @app.route('/admin')
        def admin_dashboard():
            """Admin dashboard (basic)"""
            if not session.get('admin'):
                return redirect(url_for('admin_login'))
            
            stats = self.get_detailed_stats()
            return render_template('admin.html', stats=stats)
        
        @app.route('/admin/login', methods=['GET', 'POST'])
        def admin_login():
            """Admin login"""
            if request.method == 'POST':
                password = request.form.get('password')
                if password == 'admin123':  # Simple password for demo
                    session['admin'] = True
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Invalid password')
            
            return render_template('admin_login.html')
        
        @app.route('/download/<package_name>')
        def download_direct(package_name):
            """Direct download for specific packages"""
            try:
                downloads_dir = Path(__file__).parent / 'static' / 'downloads'
                
                # Security check - only allow specific packages
                allowed_packages = [
                    'AI-IDS-Portable.zip',
                    'AI-IDS-Desktop.zip',
                    'AI-IDS-Web.zip'
                ]
                
                if package_name not in allowed_packages:
                    logger.warning(f"Unauthorized download attempt: {package_name}")
                    return jsonify({'error': 'Package not found'}), 404
                
                file_path = downloads_dir / package_name
                
                # Check if file exists
                if not file_path.exists():
                    logger.error(f"Download file not found: {file_path}")
                    return jsonify({'error': 'Download file not available'}), 404
                
                # Get user info from session/args
                email = request.args.get('email', session.get('user_email', ''))
                organization = request.args.get('organization', session.get('user_org', ''))
                
                # Determine package type for logging
                if 'Portable' in package_name:
                    package_type = 'portable'
                elif 'Desktop' in package_name:
                    package_type = 'desktop'
                elif 'Web' in package_name:
                    package_type = 'web'
                else:
                    package_type = 'unknown'
                
                # Log download
                self.log_download(request.remote_addr, request.user_agent.string, 
                                package_type, email, organization)
                
                # Serve file
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=package_name
                )
                
            except Exception as e:
                logger.error(f"Direct download error: {e}")
                return jsonify({'error': 'Download failed'}), 500
        
        @app.route('/download/desktop')
        def download_desktop():
            """Download desktop application package"""
            return redirect('/download/AI-IDS-Desktop.zip')
        
        @app.route('/download/web')
        def download_web():
            """Download web application package"""
            return redirect('/download/AI-IDS-Web.zip')
        
        @app.route('/download/portable-app')
        def download_portable_app():
            """Download the portable HTML app"""
            try:
                downloads_dir = Path(app.static_folder) / 'downloads'
                app_file = downloads_dir / 'AI-IDS-Portable-Desktop-App.html'
                
                if not app_file.exists():
                    logger.error(f"Portable app file not found: {app_file}")
                    return "Portable app not available", 404
                
                # Log download
                self.log_download(request.remote_addr, request.user_agent.string, 
                                'portable', None, None)
                
                return send_file(
                    app_file,
                    as_attachment=True,
                    download_name='AI-IDS-Portable-Desktop-App.html'
                )
            except Exception as e:
                logger.error(f"Portable app download error: {e}")
                return "Download failed", 500
        
        @app.route('/download/launcher')
        def download_launcher():
            """Download the Windows launcher for the portable app"""
            try:
                downloads_dir = Path(app.static_folder) / 'downloads'
                launcher_file = downloads_dir / 'Launch-AI-IDS.bat'
                
                if not launcher_file.exists():
                    logger.error(f"Launcher file not found: {launcher_file}")
                    return "Launcher not available", 404
                
                # Log download
                self.log_download(request.remote_addr, request.user_agent.string, 
                                'launcher', None, None)
                
                return send_file(
                    launcher_file,
                    as_attachment=True,
                    download_name='Launch-AI-IDS.bat'
                )
            except Exception as e:
                logger.error(f"Launcher download error: {e}")
                return "Download failed", 500
        
        @app.route('/api/download-stats')
        def download_stats():
            """Get download statistics"""
            try:
                conn = sqlite3.connect(DATABASE_FILE)
                cursor = conn.cursor()
                
                # Get total downloads
                cursor.execute('SELECT COUNT(*) FROM downloads')
                total_downloads = cursor.fetchone()[0]
                
                # Get downloads by platform
                cursor.execute('''
                    SELECT platform, COUNT(*) as count 
                    FROM downloads 
                    GROUP BY platform 
                    ORDER BY count DESC
                ''')
                by_platform = dict(cursor.fetchall())
                
                # Get recent downloads (last 30 days)
                thirty_days_ago = datetime.now() - timedelta(days=30)
                cursor.execute('''
                    SELECT COUNT(*) FROM downloads 
                    WHERE download_time > ?
                ''', (thirty_days_ago.isoformat(),))
                recent_downloads = cursor.fetchone()[0]
                
                conn.close()
                
                return jsonify({
                    'total_downloads': total_downloads,
                    'by_platform': by_platform,
                    'recent_downloads': recent_downloads
                })
                
            except Exception as e:
                logger.error(f"Stats error: {e}")
                return jsonify({'error': 'Could not fetch stats'}), 500
    
    def create_download_package(self, platform):
        """Create platform-specific download package"""
        temp_dir = tempfile.mkdtemp()
        package_path = os.path.join(temp_dir, f'ai-ids-{platform}.zip')
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all necessary files
            base_path = DOWNLOAD_DIR
            
            # Core files
            core_files = [
                'requirements.txt',
                'README.md',
                'REALTIME_README.md',
                'setup.py'
            ]
            
            for file in core_files:
                file_path = base_path / file
                if file_path.exists():
                    zipf.write(file_path, file)
            
            # Source code
            src_dir = base_path / 'src'
            if src_dir.exists():
                for root, dirs, files in os.walk(src_dir):
                    for file in files:
                        if file.endswith(('.py', '.yaml')):
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(base_path)
                            zipf.write(file_path, arcname)
            
            # Models (if they exist)
            models_dir = base_path / 'models'
            if models_dir.exists():
                for model_file in models_dir.glob('*.joblib'):
                    arcname = model_file.relative_to(base_path)
                    zipf.write(model_file, arcname)
            
            # Platform-specific installation script
            install_script = self.get_platform_install_script(platform)
            zipf.writestr(f'install.{self.get_script_extension(platform)}', install_script)
            
            # Quick start guide
            quick_start = self.get_platform_quick_start(platform)
            zipf.writestr('QUICK_START.md', quick_start)
            
            # License and documentation
            license_text = self.get_license_text()
            zipf.writestr('LICENSE', license_text)
        
        return package_path
    
    def get_platform_install_script(self, platform):
        """Get platform-specific installation script"""
        if platform == 'linux':
            return '''#!/bin/bash
# AI Intrusion Detection System - Linux Installation
set -e

echo "🛡️  AI Intrusion Detection System - Linux Installer"
echo "=================================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get install -y libpcap-dev build-essential

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "📋 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up configuration
echo "⚙️  Setting up configuration..."
cd src
python3 -c "from config import IDSConfig; IDSConfig().save_config()"
cd ..

# Create launcher scripts
cat > start_ids.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
cd src
python3 ids_main.py "$@"
EOF
chmod +x start_ids.sh

cat > start_monitoring.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
if [[ $EUID -ne 0 ]]; then
    echo "Packet capture requires root privileges. Restarting with sudo..."
    sudo "$0" "$@"
    exit $?
fi
source venv/bin/activate
cd src
python3 ids_main.py "$@"
EOF
chmod +x start_monitoring.sh

echo "✅ Installation complete!"
echo ""
echo "🚀 To start:"
echo "  Dashboard only: ./start_ids.sh"
echo "  Full monitoring: sudo ./start_monitoring.sh"
echo "  Web interface: http://localhost:8080"
'''
        
        elif platform == 'windows':
            return '''@echo off
REM AI Intrusion Detection System - Windows Installation
echo 🛡️  AI Intrusion Detection System - Windows Installer
echo ==================================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo 🐍 Setting up Python environment...
python -m venv venv
call venv\\Scripts\\activate.bat

REM Install requirements
echo 📋 Installing Python packages...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Set up configuration
echo ⚙️  Setting up configuration...
cd src
python -c "from config import IDSConfig; IDSConfig().save_config()"
cd ..

REM Create launcher scripts
echo @echo off > start_ids.bat
echo cd /d "%~dp0" >> start_ids.bat
echo call venv\\Scripts\\activate.bat >> start_ids.bat
echo cd src >> start_ids.bat
echo python ids_main.py %* >> start_ids.bat

echo @echo off > start_monitoring.bat
echo cd /d "%~dp0" >> start_monitoring.bat
echo call venv\\Scripts\\activate.bat >> start_monitoring.bat
echo cd src >> start_monitoring.bat
echo python ids_main.py %* >> start_monitoring.bat

echo ✅ Installation complete!
echo.
echo 🚀 To start:
echo   Dashboard only: start_ids.bat
echo   Full monitoring: start_monitoring.bat (run as Administrator)
echo   Web interface: http://localhost:8080
pause
'''
        
        elif platform == 'macos':
            return '''#!/bin/bash
# AI Intrusion Detection System - macOS Installation
set -e

echo "🛡️  AI Intrusion Detection System - macOS Installer"
echo "================================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Installing via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
if command -v brew &> /dev/null; then
    brew install libpcap
fi

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "📋 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up configuration
echo "⚙️  Setting up configuration..."
cd src
python3 -c "from config import IDSConfig; IDSConfig().save_config()"
cd ..

# Create launcher scripts
cat > start_ids.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
cd src
python3 ids_main.py "$@"
EOF
chmod +x start_ids.sh

cat > start_monitoring.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
if [[ $EUID -ne 0 ]]; then
    echo "Packet capture requires root privileges. Restarting with sudo..."
    sudo "$0" "$@"
    exit $?
fi
source venv/bin/activate
cd src
python3 ids_main.py "$@"
EOF
chmod +x start_monitoring.sh

echo "✅ Installation complete!"
echo ""
echo "🚀 To start:"
echo "  Dashboard only: ./start_ids.sh"
echo "  Full monitoring: sudo ./start_monitoring.sh"
echo "  Web interface: http://localhost:8080"
'''
    
    def get_script_extension(self, platform):
        """Get script file extension for platform"""
        return 'bat' if platform == 'windows' else 'sh'
    
    def get_platform_quick_start(self, platform):
        """Get platform-specific quick start guide"""
        return f'''# AI Intrusion Detection System - Quick Start ({platform.title()})

## Installation

1. Extract the downloaded ZIP file
2. Run the installation script:
   - Linux/macOS: `chmod +x install.sh && ./install.sh`
   - Windows: Double-click `install.bat` or run in Command Prompt

## Starting the System

### Dashboard Only (No root/admin required)
- Linux/macOS: `./start_ids.sh`
- Windows: Double-click `start_ids.bat`

### Full Real-Time Monitoring (Requires root/admin)
- Linux/macOS: `sudo ./start_monitoring.sh`
- Windows: Right-click `start_monitoring.bat` → "Run as Administrator"

## Accessing the Web Interface

Open your browser and go to: http://localhost:8080

## Features

✅ Real-time network packet analysis
✅ AI-powered threat detection
✅ Web-based monitoring dashboard
✅ 20+ attack type detection
✅ Low false positive rate
✅ Customizable alert thresholds

## Support

- Documentation: See README.md files
- Issues: Check the support documentation
- Configuration: Edit `src/ids_config.yaml`

## System Requirements

- Python 3.8 or later
- 2GB+ RAM recommended
- Network interface access
- Admin/root privileges for packet capture

Enjoy your AI-powered network protection! 🛡️
'''
    
    def get_license_text(self):
        """Get license text"""
        return '''MIT License

Copyright (c) 2025 AI Intrusion Detection System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
    
    def log_download(self, ip_address, user_agent, platform, email, organization):
        """Log download to database"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO downloads (ip_address, user_agent, platform, email, organization) VALUES (?, ?, ?, ?, ?)',
                (ip_address, user_agent, platform, email, organization)
            )
            conn.commit()
            conn.close()
            logger.info(f"Download logged: {platform} from {ip_address}")
        except Exception as e:
            logger.error(f"Failed to log download: {e}")
    
    def get_download_stats(self):
        """Get basic download statistics"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            # Total downloads
            cursor.execute('SELECT COUNT(*) FROM downloads')
            total_downloads = cursor.fetchone()[0]
            
            # Downloads by platform
            cursor.execute('SELECT platform, COUNT(*) FROM downloads GROUP BY platform')
            platform_stats = dict(cursor.fetchall())
            
            # Recent downloads (last 24 hours)
            cursor.execute(
                'SELECT COUNT(*) FROM downloads WHERE download_time > datetime("now", "-1 day")'
            )
            recent_downloads = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_downloads': total_downloads,
                'platform_stats': platform_stats,
                'recent_downloads': recent_downloads
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'total_downloads': 0, 'platform_stats': {}, 'recent_downloads': 0}
    
    def get_detailed_stats(self):
        """Get detailed statistics for admin"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            # Download trends
            cursor.execute('''
                SELECT DATE(download_time) as date, COUNT(*) as count 
                FROM downloads 
                WHERE download_time > datetime("now", "-30 days")
                GROUP BY DATE(download_time) 
                ORDER BY date
            ''')
            daily_downloads = cursor.fetchall()
            
            # Top organizations
            cursor.execute('''
                SELECT organization, COUNT(*) as count 
                FROM downloads 
                WHERE organization != "" 
                GROUP BY organization 
                ORDER BY count DESC 
                LIMIT 10
            ''')
            top_orgs = cursor.fetchall()
            
            # Recent feedback
            cursor.execute('''
                SELECT email, rating, comments, submit_time 
                FROM feedback 
                ORDER BY submit_time DESC 
                LIMIT 20
            ''')
            recent_feedback = cursor.fetchall()
            
            conn.close()
            
            basic_stats = self.get_download_stats()
            
            return {
                **basic_stats,
                'daily_downloads': daily_downloads,
                'top_organizations': top_orgs,
                'recent_feedback': recent_feedback
            }
        except Exception as e:
            logger.error(f"Failed to get detailed stats: {e}")
            return self.get_download_stats()

# Initialize the portal
portal = DownloadPortal()

def main():
    """Run the web application"""
    print("🌐 Starting AI IDS Download Portal...")
    print("📊 Dashboard available at: http://localhost:5000")
    print("💾 Download packages will be generated on-demand")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
