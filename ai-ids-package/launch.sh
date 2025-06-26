#!/bin/bash
echo "🛡️ Starting AI Intrusion Detection System..."
echo "Checking Python installation..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ and try again."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not available. Please install pip and try again."
    exit 1
fi

echo "✅ Python found. Installing dependencies..."

# Install requirements
pip3 install -r requirements.txt --user

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo "🚀 Starting AI-IDS..."
    python3 ai_ids_app.py
else
    echo "❌ Failed to install dependencies. Please check your internet connection."
    exit 1
fi
