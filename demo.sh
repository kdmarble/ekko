#!/usr/bin/env bash
#
# Demo script - Test ekko without installing
#

set -e

echo "🎬 ekko Demo"
echo ""
echo "This script will:"
echo "1. Check dependencies"
echo "2. Run ekko locally without installation"
echo "3. Show you how it works"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi
echo "✓ Python 3 found"

# Check pip and requests
if ! python3 -c "import requests" 2>/dev/null; then
    echo "⚠️  Installing requests module..."
    python3 -m pip install requests --user --quiet
fi
echo "✓ Dependencies ready"
echo ""

# Make executable
chmod +x ekko.py

# Check if configured
if [ ! -f "$HOME/.config/ekko/config.json" ]; then
    echo "🔧 First time setup - running configuration wizard..."
    echo ""
    ./ekko.py --setup
else
    echo "✓ Already configured"
fi

echo ""
echo "🚀 Demo Mode - Try these examples:"
echo ""
echo "  ./ekko.py find all files over 500MB"
echo "  ./ekko.py show disk usage sorted by size"
echo "  ./ekko.py compress this folder"
echo ""
echo "Or run your own:"
read -p "Your prompt: " prompt

if [ -n "$prompt" ]; then
    ./ekko.py $prompt
else
    echo "No prompt provided. Run: ./ekko.py <your prompt>"
fi

echo ""
echo "---"
echo "💡 To install permanently, run: bash install-ekko.sh"
