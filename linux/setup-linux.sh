#!/usr/bin/env bash
# ============================================================================
# Rota AI -- Linux Desktop Setup Script
# ============================================================================
# Run this on a fresh Ubuntu/Debian/Fedora/Arch Linux desktop.
# It installs all system and Python dependencies needed for the Linux port.
#
# Usage:  bash setup-linux.sh
# ============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "============================================"
echo "    R O T A   A I  --  Linux Setup"
echo "============================================"
echo ""

# --- Detect distro ---
DISTRO=""
PKG_INSTALL=""
if [ -f /etc/os-release ]; then
    . /etc/os-release
    case "$ID" in
        ubuntu|debian|linuxmint|pop)
            DISTRO="debian"
            PKG_INSTALL="sudo apt-get install -y"
            ;;
        fedora)
            DISTRO="fedora"
            PKG_INSTALL="sudo dnf install -y"
            ;;
        arch|manjaro|endeavouros)
            DISTRO="arch"
            PKG_INSTALL="sudo pacman -S --noconfirm"
            ;;
        *)
            echo -e "${YELLOW}[WARN] Unknown distro: $ID. Trying Debian-style packages.${NC}"
            DISTRO="debian"
            PKG_INSTALL="sudo apt-get install -y"
            ;;
    esac
fi

echo -e "${BLUE}Detected: $DISTRO${NC}"
echo ""

# --- Check sudo ---
if ! sudo -n true 2>/dev/null; then
    echo -e "${YELLOW}This script needs sudo privileges to install system packages.${NC}"
    echo "You may be prompted for your password."
    echo ""
fi

# ============================================================================
# 1. SYSTEM PACKAGES
# ============================================================================
echo -e "${GREEN}[1/6] Installing system packages...${NC}"

if [ "$DISTRO" = "debian" ]; then
    sudo apt-get update -qq
    $PKG_INSTALL \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        libportaudio2 \
        portaudio19-dev \
        libdbus-glib-1-dev \
        libdbus-1-dev \
        at-spi2-core \
        python3-pyatspi \
        gnome-keyring \
        libsecret-1-dev \
        wl-clipboard \
        xdotool \
        xclip \
        dbus-x11 \
        libayatana-appindicator3-1 \
        gir1.2-appindicator3-0.1 \
        ffmpeg \
        git

elif [ "$DISTRO" = "fedora" ]; then
    $PKG_INSTALL \
        python3 \
        python3-pip \
        python3-devel \
        portaudio-devel \
        dbus-glib-devel \
        at-spi2-core \
        python3-pyatspi \
        gnome-keyring \
        libsecret-devel \
        wl-clipboard \
        xdotool \
        xclip \
        dbus-x11 \
        ffmpeg \
        git

elif [ "$DISTRO" = "arch" ]; then
    $PKG_INSTALL \
        python \
        python-pip \
        portaudio \
        dbus-glib \
        at-spi2-core \
        python-pyatspi \
        gnome-keyring \
        libsecret \
        wl-clipboard \
        xdotool \
        xclip \
        dbus \
        ffmpeg \
        git
fi

echo -e "${GREEN}  System packages installed.${NC}"
echo ""

# ============================================================================
# 2. ADD USER TO REQUIRED GROUPS
# ============================================================================
echo -e "${GREEN}[2/6] Configuring user groups...${NC}"

# 'input' group -- needed for evdev keyboard access (no root required)
_NEEDS_RELOGIN=false
if ! groups | grep -q '\binput\b'; then
    sudo usermod -aG input "$USER"
    _NEEDS_RELOGIN=true
    echo -e "${YELLOW}  Added '$USER' to 'input' group.${NC}"
else
    echo "  User already in 'input' group."
fi

# 'audio' group -- needed for audio device access
if ! groups | grep -q '\baudio\b'; then
    sudo usermod -aG audio "$USER"
    echo -e "${YELLOW}  Added '$USER' to 'audio' group.${NC}"
else
    echo "  User already in 'audio' group."
fi

echo ""

# ============================================================================
# 3. UINPUT ACCESS (for ydotool / uinput-based injection)
# ============================================================================
echo -e "${GREEN}[3/6] Configuring uinput access...${NC}"

# Create udev rule for uinput access without root
if [ -f /etc/udev/rules.d/99-uinput.rules ]; then
    echo "  uinput udev rule already exists."
else
    echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | sudo tee /etc/udev/rules.d/99-uinput.rules > /dev/null
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    echo -e "${YELLOW}  Created /etc/udev/rules.d/99-uinput.rules. Log out and back in.${NC}"
fi

echo ""

# ============================================================================
# 4. PYTHON VIRTUAL ENVIRONMENT
# ============================================================================
echo -e "${GREEN}[4/6] Setting up Python virtual environment...${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"
    echo "  Created .venv/"
else
    echo "  .venv/ already exists."
fi

source "${VENV_DIR}/bin/activate"
pip install --upgrade pip setuptools wheel -q
echo "  pip upgraded."

echo ""

# ============================================================================
# 5. PYTHON DEPENDENCIES
# ============================================================================
echo -e "${GREEN}[5/6] Installing Python dependencies...${NC}"

PIP_REQ="${SCRIPT_DIR}/requirements.txt"
PIP_REQ_LINUX="${SCRIPT_DIR}/linux/requirements-linux.txt"

if [ -f "${PIP_REQ_LINUX}" ]; then
    pip install -r "${PIP_REQ_LINUX}" -q 2>&1 | tail -3
elif [ -f "${PIP_REQ}" ]; then
    pip install -r "${PIP_REQ}" -q 2>&1 | tail -3
fi

echo "  Python packages installed."
echo ""

# ============================================================================
# 6. VERIFY
# ============================================================================
echo -e "${GREEN}[6/6] Verification...${NC}"
echo ""

source "${VENV_DIR}/bin/activate"
cd "${SCRIPT_DIR}"
python3 -c "
import sys
sys.path.insert(0, 'desktop')

# Core
import PyQt6
print(f'  PyQt6: {PyQt6.QtCore.PYQT_VERSION_STR}')

import sounddevice
print(f'  sounddevice: OK')

import faster_whisper
print(f'  faster-whisper: OK')

import torch
print(f'  torch: {torch.__version__} (CUDA: {torch.cuda.is_available()})')

# Linux backends
import evdev
print(f'  evdev: OK')

import keyring
print(f'  keyring: {keyring.get_keyring()}')

try:
    import pyatspi
    print(f'  pyatspi: OK')
except ImportError:
    print(f'  pyatspi: NOT INSTALLED (run: sudo apt install python3-pyatspi)')

# Tools
import shutil
for tool in ['wl-copy', 'xdotool', 'xclip', 'ffmpeg']:
    if shutil.which(tool):
        print(f'  {tool}: OK')
    else:
        print(f'  {tool}: NOT FOUND')

# Platform layer
from plat import get_hotkey_handler, get_injector
HotkeyHandler = get_hotkey_handler()
TextInjector = get_injector()
print(f'  plat.HotkeyHandler: {HotkeyHandler.__name__}')
print(f'  plat.TextInjector: {TextInjector.__name__}')
" 2>&1

# ============================================================================
# FINAL: Relogin warning (shown last so it isn't buried)
# ============================================================================
if [ "${_NEEDS_RELOGIN}" = "true" ]; then
    echo ""
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ACTION REQUIRED — READ BEFORE LAUNCHING ROTA AI        ║${NC}"
    echo -e "${RED}╠══════════════════════════════════════════════════════════╣${NC}"
    echo -e "${RED}║  Your user was added to the 'input' group, but your     ║${NC}"
    echo -e "${RED}║  CURRENT SESSION does not see this change yet.           ║${NC}"
    echo -e "${RED}║                                                          ║${NC}"
    echo -e "${RED}║  Hotkeys WILL NOT WORK until you do one of:             ║${NC}"
    echo -e "${RED}║                                                          ║${NC}"
    echo -e "${RED}║  Option 1 (permanent):  Log out and log back in.         ║${NC}"
    echo -e "${RED}║                                                          ║${NC}"
    echo -e "${RED}║  Option 2 (this session only):                           ║${NC}"
    echo -e "${RED}║    newgrp input                                          ║${NC}"
    echo -e "${RED}║    (then re-run ./linux/run.sh in the new shell)         ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
fi
