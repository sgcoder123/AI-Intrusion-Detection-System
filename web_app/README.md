# 🌐 AI IDS Download Portal

## Overview

This web application provides a user-friendly portal for downloading and installing the AI Intrusion Detection System. Users can:

- **Download platform-specific packages** (Windows, Linux, macOS)
- **View system documentation** and installation guides  
- **Try a live demo** of the intrusion detection system
- **Access support** and troubleshooting resources
- **Track download statistics** and user feedback

## 🚀 Quick Start

### Launch the Web Portal

```bash
# From the project root directory
cd web_app
python3 launch_portal.py
```

The portal will be available at: **http://localhost:5000**

### Features

✅ **Platform-Specific Downloads** - Automatically packages the IDS system for Windows, Linux, and macOS  
✅ **Installation Scripts** - Includes automated installers for each platform  
✅ **Live Demo** - Interactive demonstration of threat detection capabilities  
✅ **Documentation Portal** - Complete guides and API reference  
✅ **Download Analytics** - Track downloads and user engagement  
✅ **User Feedback** - Collect ratings and comments from users  

## 📦 Download Packages

The web portal generates downloadable packages containing:

### Core Components
- Complete source code with real-time monitoring
- Pre-trained machine learning models (92% accuracy)
- Web dashboard for monitoring and alerts
- Configuration files and documentation

### Platform-Specific Installers
- **Linux**: Bash script with apt/yum package management
- **Windows**: Batch script with pip installation  
- **macOS**: Bash script with Homebrew integration

### Included Files
```
ai-ids-platform-YYYYMMDD.zip
├── src/                     # Source code
├── models/                  # ML models (.joblib files)
├── requirements.txt         # Python dependencies
├── install.sh/.bat          # Platform installer
├── start_ids.sh/.bat        # Dashboard launcher
├── start_monitoring.sh/.bat # Full monitoring launcher
├── QUICK_START.md           # Platform-specific guide
├── README.md                # Complete documentation
└── LICENSE                  # MIT license
```

## 🎮 Live Demo

The portal includes an interactive demo showing:

- **Real-time packet processing** simulation
- **Threat detection** with various attack types
- **Live statistics** and monitoring dashboard
- **Alert generation** and management

Access the demo at: `http://localhost:5000/demo`

## 📊 Analytics Dashboard

Track portal usage with built-in analytics:

- **Download counts** by platform and time period
- **User demographics** and organization tracking
- **Feedback ratings** and comments
- **Popular features** and documentation sections

Admin access: `http://localhost:5000/admin` (password: `admin123`)

## 🔧 Configuration

### Web App Settings

The portal can be configured by modifying `app.py`:

```python
# Server configuration
HOST = '0.0.0.0'          # Bind to all interfaces
PORT = 5000               # Default port
DEBUG = True              # Enable debug mode

# Database
DATABASE_FILE = 'downloads.db'  # SQLite database

# Platforms
ALLOWED_PLATFORMS = ['windows', 'linux', 'macos']
```

### Customization Options

- **Branding**: Modify HTML templates in `templates/`
- **Styling**: Update CSS in template `<style>` sections
- **Features**: Add new endpoints in `app.py`
- **Analytics**: Extend database schema for more tracking

## 🛠️ Development

### File Structure
```
web_app/
├── app.py                   # Main Flask application
├── launch_portal.py         # Launcher script
├── requirements.txt         # Web app dependencies
├── downloads.db            # SQLite database (auto-created)
└── templates/              # HTML templates
    ├── index.html          # Homepage
    ├── download.html       # Download page
    ├── demo.html           # Live demo
    ├── documentation.html  # Docs portal
    └── admin.html          # Analytics dashboard
```

### Adding New Features

1. **New Download Options**: Add platforms to `ALLOWED_PLATFORMS`
2. **Custom Installers**: Modify `get_platform_install_script()`
3. **Enhanced Analytics**: Extend database schema and API endpoints
4. **UI Improvements**: Update HTML templates and CSS

### API Endpoints

The portal exposes several REST API endpoints:

- `GET /api/download/<platform>` - Download package
- `GET /api/stats` - Download statistics  
- `POST /api/feedback` - Submit user feedback
- `GET /api/chart_data` - Analytics data

## 🔒 Security Considerations

### Download Security
- Packages are generated on-demand with fresh timestamps
- File integrity can be verified with checksums
- Downloads are logged with IP and user agent tracking

### Admin Access
- Simple password protection for analytics dashboard
- Consider implementing proper authentication for production
- Database contains no sensitive user information

### Privacy
- Only basic analytics are collected (IP, platform, timestamp)
- Email addresses are optional and used only for updates
- No personal data is required for downloads

## 🚀 Deployment

### Production Deployment

For production use, consider:

1. **WSGI Server**: Use Gunicorn or uWSGI instead of Flask dev server
2. **Reverse Proxy**: Nginx or Apache for static files and SSL
3. **Database**: PostgreSQL or MySQL for better performance
4. **CDN**: CloudFlare or AWS CloudFront for global distribution
5. **Monitoring**: Application monitoring and error tracking

### Example Production Setup

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With SSL and reverse proxy
# Configure Nginx to proxy to http://localhost:5000
```

### Environment Variables

```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
export DATABASE_URL=postgresql://user:pass@localhost/idsportal
```

## 📈 Usage Analytics

The portal tracks several metrics:

### Download Metrics
- Total downloads across all platforms
- Platform distribution (Windows vs Linux vs macOS)
- Geographic distribution (by IP)
- Download trends over time

### User Engagement
- Page views and session duration
- Feature usage (demo, documentation, support)
- User feedback and ratings
- Conversion rates (visitors to downloads)

### System Performance
- Package generation time
- Download completion rates
- Error rates and types
- Server response times

## 🆘 Support

### Common Issues

**Port Already in Use**
```bash
# Check what's using port 5000
lsof -i :5000

# Use different port
export PORT=5001
python3 launch_portal.py
```

**Package Generation Fails**
- Ensure all required files exist in parent directory
- Check file permissions and disk space
- Verify Python virtual environment is properly set up

**Database Errors**
- Database is auto-created on first run
- Check write permissions in web_app directory
- Delete `downloads.db` to reset database

### Getting Help

1. Check the main project documentation
2. Review log files for error details
3. Open an issue on the project repository
4. Contact support through the web portal

## 📄 License

This web portal is part of the AI Intrusion Detection System and is licensed under the MIT License. See the main project LICENSE file for details.

## 🤝 Contributing

Contributions to improve the download portal are welcome! Areas for enhancement:

- **UI/UX improvements** - Better responsive design and user experience
- **Additional platforms** - Support for more operating systems
- **Enhanced analytics** - More detailed usage tracking and reporting  
- **Security features** - User authentication and access control
- **Performance optimization** - Caching and CDN integration

Please follow the main project's contribution guidelines when submitting changes.
