#!/bin/bash
echo "🛡️ Starting AI Intrusion Detection System - Web Edition"
echo ""
echo "This application runs in your web browser."
echo "A browser window will open automatically."
echo ""
echo "To stop the application, press Ctrl+C in this terminal."
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

python3 "AI-IDS-Portable-Web.py"
