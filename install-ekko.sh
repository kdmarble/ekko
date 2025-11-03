#!/usr/bin/env bash
#
# ekko installer
# Works on Linux, macOS, and WSL
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/ekko"
REPO_URL="https://raw.githubusercontent.com/kdmarble/ekko/main/ekko.py"

echo -e "${BLUE}🚀 ekko installer${NC}\n"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 found"

# Check pip
if ! python3 -m pip --version &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}  pip not found, installing..."
    python3 -m ensurepip --default-pip || {
        echo -e "${RED}Error: Could not install pip${NC}"
        exit 1
    }
fi

# Install requests if needed
if ! python3 -c "import requests" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC}  Installing requests module..."
    python3 -m pip install --user requests --quiet
fi

echo -e "${GREEN}✓${NC} Dependencies ready"

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"

# Download or copy ekko
if [ -f "ekko.py" ]; then
    echo -e "${BLUE}ℹ${NC}  Installing from local file..."
    cp ekko.py "$INSTALL_DIR/ekko"
else
    echo -e "${BLUE}ℹ${NC}  Downloading ekko..."
    if command -v curl &> /dev/null; then
        curl -fsSL "$REPO_URL" -o "$INSTALL_DIR/ekko"
    elif command -v wget &> /dev/null; then
        wget -q "$REPO_URL" -O "$INSTALL_DIR/ekko"
    else
        echo -e "${RED}Error: Neither curl nor wget found${NC}"
        exit 1
    fi
fi

chmod +x "$INSTALL_DIR/ekko"
echo -e "${GREEN}✓${NC} ekko installed to $INSTALL_DIR/ekko"

# Detect shell
SHELL_NAME=$(basename "$SHELL")
SHELL_RC=""

case "$SHELL_NAME" in
    bash)
        SHELL_RC="$HOME/.bashrc"
        ;;
    zsh)
        SHELL_RC="$HOME/.zshrc"
        ;;
    fish)
        SHELL_RC="$HOME/.config/fish/config.fish"
        ;;
    *)
        echo -e "${YELLOW}⚠${NC}  Unknown shell: $SHELL_NAME"
        echo -e "   Add this to your shell config manually:"
        echo -e "   ${BLUE}export PATH=\"$INSTALL_DIR:\$PATH\"${NC}"
        exit 0
        ;;
esac

# Add to PATH if needed
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${BLUE}ℹ${NC}  Adding $INSTALL_DIR to PATH in $SHELL_RC"
    
    if [ "$SHELL_NAME" = "fish" ]; then
        echo "set -gx PATH $INSTALL_DIR \$PATH" >> "$SHELL_RC"
    else
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_RC"
    fi
fi

echo -e "${GREEN}✓${NC} Shell integration complete"

# Run setup wizard only if config doesn't exist
CONFIG_FILE="$CONFIG_DIR/config.json"
if [ -f "$CONFIG_FILE" ]; then
    echo -e "\n${GREEN}✓${NC} Existing configuration preserved"
    echo -e "${BLUE}ℹ${NC}  Config file: $CONFIG_FILE"
    echo -e "${BLUE}ℹ${NC}  To reconfigure, run: ${BLUE}ekko --setup${NC}"
else
    echo -e "\n${BLUE}🔧 Running configuration wizard...${NC}\n"
    "$INSTALL_DIR/ekko" --setup < /dev/tty
fi

# Final instructions
echo -e "\n${GREEN}✅ Installation complete!${NC}\n"
echo -e "Reload your shell:"
echo -e "  ${BLUE}source $SHELL_RC${NC}"
echo -e "\nThen try:"
echo -e "  ${BLUE}ekko find all files over 500MB${NC}"
echo -e "\nReconfigure anytime with:"
echo -e "  ${BLUE}ekko --setup${NC}"
