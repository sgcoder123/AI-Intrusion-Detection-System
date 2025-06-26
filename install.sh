#!/bin/bash
# Installation script for AI Intrusion Detection System

set -e  # Exit on any error

echo "🛡️  AI Intrusion Detection System - Installation Script"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root for packet capture
check_permissions() {
    print_status "Checking permissions..."
    
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. This is not recommended for regular use."
        print_warning "Consider using sudo only when needed for packet capture."
    else
        print_status "Running as non-root user. You may need sudo for packet capture."
    fi
}

# Check Python version
check_python() {
    print_status "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
        print_success "Python $python_version found"
        
        # Check if version is >= 3.8
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python version is compatible"
        else
            print_error "Python 3.8+ is required. Found: $python_version"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8 or later."
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        print_status "Detected Ubuntu/Debian system"
        sudo apt-get update
        sudo apt-get install -y python3-dev python3-pip libpcap-dev build-essential
        print_success "System dependencies installed"
    elif command -v yum &> /dev/null; then
        # RHEL/CentOS
        print_status "Detected RHEL/CentOS system"
        sudo yum install -y python3-devel python3-pip libpcap-devel gcc
        print_success "System dependencies installed"
    elif command -v brew &> /dev/null; then
        # macOS
        print_status "Detected macOS system"
        brew install libpcap
        print_success "System dependencies installed"
    else
        print_warning "Could not detect package manager. Please install:"
        print_warning "- Python development headers"
        print_warning "- libpcap development library"
        print_warning "- C compiler (gcc)"
    fi
}

# Create virtual environment
create_venv() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Make sure we're in virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate
    fi
    
    # Install requirements
    pip install -r requirements.txt
    print_success "Python dependencies installed"
}

# Setup configuration
setup_config() {
    print_status "Setting up configuration..."
    
    cd src
    if [ ! -f "ids_config.yaml" ]; then
        python3 -c "from config import IDSConfig; IDSConfig().save_config()"
        print_success "Default configuration created: src/ids_config.yaml"
    else
        print_status "Configuration file already exists"
    fi
    cd ..
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    # Make sure we're in virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate
    fi
    
    cd src
    
    # Test model loading
    if python3 -c "from deploy_model import IntrusionDetector; IntrusionDetector()" 2>/dev/null; then
        print_success "Model loading test passed"
    else
        print_error "Model loading test failed"
        return 1
    fi
    
    # Test configuration
    if python3 -c "from config import IDSConfig; IDSConfig()" 2>/dev/null; then
        print_success "Configuration test passed"
    else
        print_error "Configuration test failed"
        return 1
    fi
    
    cd ..
    print_success "Installation test completed successfully"
}

# Create launcher scripts
create_launchers() {
    print_status "Creating launcher scripts..."
    
    # Create start script
    cat > start_ids.sh << 'EOF'
#!/bin/bash
# Start AI Intrusion Detection System

cd "$(dirname "$0")"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Start IDS
cd src
python3 ids_main.py "$@"
EOF

    chmod +x start_ids.sh
    
    # Create monitoring script (requires sudo for packet capture)
    cat > start_ids_monitor.sh << 'EOF'
#!/bin/bash
# Start AI Intrusion Detection System with packet monitoring (requires sudo)

cd "$(dirname "$0")"

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
    echo "Packet capture requires root privileges. Restarting with sudo..."
    sudo "$0" "$@"
    exit $?
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Start IDS with packet monitoring
cd src
python3 ids_main.py "$@"
EOF

    chmod +x start_ids_monitor.sh
    
    print_success "Launcher scripts created:"
    print_success "  - start_ids.sh (dashboard only)"
    print_success "  - start_ids_monitor.sh (full monitoring with sudo)"
}

# Main installation process
main() {
    echo
    print_status "Starting installation process..."
    echo
    
    check_permissions
    check_python
    install_system_deps
    create_venv
    install_python_deps
    setup_config
    test_installation
    create_launchers
    
    echo
    print_success "Installation completed successfully!"
    echo
    echo "📋 Next steps:"
    echo "  1. Review configuration: src/ids_config.yaml"
    echo "  2. Start dashboard only: ./start_ids.sh"
    echo "  3. Start full monitoring: ./start_ids_monitor.sh"
    echo "  4. Access dashboard: http://localhost:8080"
    echo
    echo "🔒 For packet capture, you need root privileges:"
    echo "  sudo ./start_ids_monitor.sh"
    echo
    echo "📚 For more information, see README.md"
    echo
}

# Run installation
main
