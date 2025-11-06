#!/usr/bin/env bash
#
# ekko installer
# Works on Linux and macOS
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
CONFIG_DIR="$HOME/.config/ekko"
REPO_URL="https://github.com/kdmarble/ekko"

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

echo -e "${GREEN}✓${NC} pip ready"

# Check for pipx, install if needed
if ! command -v pipx &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}  pipx not found, installing..."
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    export PATH="$HOME/.local/bin:$PATH"

    if ! command -v pipx &> /dev/null; then
        echo -e "${RED}Error: pipx installation failed${NC}"
        echo -e "${YELLOW}You can install manually with: python3 -m pip install --user pipx${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓${NC} pipx ready"

# Create config directory
mkdir -p "$CONFIG_DIR"

# Install ekko using pipx
echo -e "${BLUE}ℹ${NC}  Installing ekko..."

# Get the latest release tag by following the redirect
RELEASE_URL=$(curl -fsSL -o /dev/null -w "%{url_effective}" ${REPO_URL}/releases/latest)
LATEST_VERSION=$(basename "$RELEASE_URL")

if [ -z "$LATEST_VERSION" ]; then
    echo -e "${RED}Error: Could not determine latest version${NC}"
    exit 1
fi

WHEEL_URL="${REPO_URL}/releases/download/${LATEST_VERSION}/ekko-${LATEST_VERSION#v}-py3-none-any.whl"

if pipx list | grep -q "ekko"; then
    echo -e "${YELLOW}⚠${NC}  ekko is already installed, upgrading..."
    pipx upgrade ekko || pipx install --force "$WHEEL_URL"
else
    pipx install "$WHEEL_URL"
fi

echo -e "${GREEN}✓${NC} ekko installed"

# Ensure pipx bin directory is in PATH
PIPX_BIN_DIR=$(python3 -m pipx environment | grep PIPX_BIN_DIR | cut -d= -f2)
if [[ -z "$PIPX_BIN_DIR" ]]; then
    PIPX_BIN_DIR="$HOME/.local/bin"
fi

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
        echo -e "   ${BLUE}export PATH=\"$PIPX_BIN_DIR:\$PATH\"${NC}"
        ;;
esac

# Add to PATH if needed and shell RC was determined
if [ -n "$SHELL_RC" ] && [[ ":$PATH:" != *":$PIPX_BIN_DIR:"* ]]; then
    echo -e "${BLUE}ℹ${NC}  Adding $PIPX_BIN_DIR to PATH in $SHELL_RC"

    if [ "$SHELL_NAME" = "fish" ]; then
        echo "set -gx PATH $PIPX_BIN_DIR \$PATH" >> "$SHELL_RC"
    else
        echo "export PATH=\"$PIPX_BIN_DIR:\$PATH\"" >> "$SHELL_RC"
    fi

    echo -e "${GREEN}✓${NC} Shell integration complete"
fi

# Run setup wizard only if config doesn't exist
CONFIG_FILE="$CONFIG_DIR/config.json"
if [ -f "$CONFIG_FILE" ]; then
    echo -e "\n${GREEN}✓${NC} Existing configuration preserved"
    echo -e "${BLUE}ℹ${NC}  Config file: $CONFIG_FILE"
    echo -e "${BLUE}ℹ${NC}  To reconfigure, run: ${BLUE}ekko --setup${NC}"
else
    echo -e "\n${BLUE}🔧 Running configuration wizard...${NC}\n"
    ekko --setup < /dev/tty || {
        echo -e "${YELLOW}⚠${NC}  Couldn't run setup automatically"
        echo -e "${BLUE}ℹ${NC}  Run 'ekko --setup' manually after reloading your shell"
    }
fi

# Final instructions
echo -e "\n${GREEN}✅ Installation complete!${NC}\n"

if [ -n "$SHELL_RC" ]; then
    echo -e "Reload your shell:"
    echo -e "  ${BLUE}source $SHELL_RC${NC}"
    echo -e ""
fi

echo -e "Then try:"
echo -e "  ${BLUE}ekko find all files over 500MB${NC}"
echo -e "\nReconfigure anytime with:"
echo -e "  ${BLUE}ekko --setup${NC}"
