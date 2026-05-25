#!/usr/bin/env bash
# ============================================================================
# Rota AI - Linux Launcher
# ============================================================================
# Handles: venv setup, dependency sync, desktop file, launch
# Usage:   ./run.sh
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${REPO_DIR}/.venv"
REQ_FILE="${SCRIPT_DIR}/requirements-linux.txt"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "============================================"
echo "          R O T A   A I"
echo "          Linux Launcher"
echo "============================================"
echo ""

# --- 0. Check 'input' group membership (required for evdev hotkey access) ---
if ! groups | grep -qw "input"; then
    # User is not in 'input' group at all
    echo -e "${RED}[ERROR] Your user is not in the 'input' group.${NC}"
    echo ""
    echo "  Rota AI needs read access to /dev/input/event* to detect hotkeys."
    echo "  Fix:"
    echo "    sudo usermod -aG input \$USER"
    echo "    then log out and back in."
    echo ""
    echo "  If you just ran setup-linux.sh, the group was added but your"
    echo "  current session doesn't see it yet. Two options:"
    echo "    1. Log out and log back in (permanent fix)."
    echo "    2. Run this instead for the current session only:"
    echo "       newgrp input"
    echo ""
    echo "  After 'newgrp input', re-run this script in the new shell."
    exit 1
fi

# --- 1. Check Python ---
PY=""
if command -v python3 &>/dev/null; then
    PY="python3"
elif command -v python &>/dev/null; then
    PY="python"
else
    echo -e "${RED}[ERROR] Python 3 not found.${NC}"
    echo "  sudo apt install python3 python3-pip python3-venv"
    exit 1
fi
echo "  Found: $($PY --version 2>&1)"

# --- 2. Virtual environment ---
if [ ! -d "${VENV_DIR}" ]; then
    echo "  Creating virtual environment..."
    $PY -m venv "${VENV_DIR}"
fi
source "${VENV_DIR}/bin/activate"

# --- 3. Dependencies ---
if [ -f "${REQ_FILE}" ]; then
    echo "  Installing Python dependencies..."
    if ! pip install -r "${REQ_FILE}" --disable-pip-version-check 2>&1; then
        echo -e "${RED}  [ERROR] Dependency installation failed.${NC}"
        echo "  Try manually: pip install -r ${REQ_FILE}"
        echo "  If system packages are missing, run: bash ${SCRIPT_DIR}/setup-linux.sh"
        exit 1
    fi
    echo -e "${GREEN}  Dependencies installed.${NC}"
else
    echo -e "${YELLOW}  [WARN] ${REQ_FILE} not found — skipping dependency check.${NC}"
fi

# --- 4. Desktop file ---
DESKTOP_FILE_DIR="${HOME}/.local/share/applications"
mkdir -p "${DESKTOP_FILE_DIR}"
cat > "${DESKTOP_FILE_DIR}/rota-ai.desktop" << DESKTOP
[Desktop Entry]
Type=Application
Name=Rota AI
Comment=Open source voice dictation for Linux
Exec=${REPO_DIR}/linux/run.sh
Icon=${REPO_DIR}/desktop/assets/icon.svg
Terminal=false
Categories=Utility;Accessibility;
DESKTOP

# --- 5. Launch ---
echo ""
echo "  Launching Rota AI..."
echo "  Config: ~/.config/rota-ai/config.json"
echo ""

export PYTHONPATH="${REPO_DIR}/desktop:${PYTHONPATH:-}"

exec python3 -u "${REPO_DIR}/desktop/app/main.py" "$@"
