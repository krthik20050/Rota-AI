#!/usr/bin/env bash
# ============================================================================
# Rota AI - Linux Launcher
# ============================================================================
# Handles: venv setup, dependency sync, config dir creation, launch
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="${REPO_DIR}/.venv-linux"
REQ_FILE="${REPO_DIR}/requirements-linux.txt"

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

# --- 1. Check Python ---
PY=""
if command -v python3 &>/dev/null; then
    PY="python3"
elif command -v python &>/dev/null; then
    PY="python"
else
    echo -e "${RED}[ERROR] Python 3 not found. Install it with:${NC}"
    echo "  sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$($PY --version 2>&1)
echo "  Found: ${PYTHON_VERSION}"

# --- 2. Virtual environment ---
if [ ! -d "${VENV_DIR}" ]; then
    echo "  Creating virtual environment..."
    $PY -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

# --- 3. Dependencies ---
if [ -f "${REQ_FILE}" ]; then
    pip install -r "${REQ_FILE}" -q --disable-pip-version-check 2>/dev/null || true
fi

# --- 4. Desktop file for PATH integration (optional) ---
DESKTOP_FILE_DIR="${HOME}/.local/share/applications"
mkdir -p "${DESKTOP_FILE_DIR}"
cat > "${DESKTOP_FILE_DIR}/rota-ai.desktop" << DESKTOP
[Desktop Entry]
Type=Application
Name=Rota AI
Comment=Voice dictation for Linux
Exec=${REPO_DIR}/run.sh
Icon=${REPO_DIR}/desktop/assets/icon.svg
Terminal=false
Categories=Utility;Accessibility;
DESKTOP

# --- 5. Launch ---
echo ""
echo "  Launching Rota AI..."
echo "  Config: ~/.config/rota-ai/config.json"
echo ""

export PYTHONPATH="${SCRIPT_DIR}:\${PYTHONPATH:-}"

exec python3 -u "${SCRIPT_DIR}/app/main.py" "$@"
