#!/usr/bin/env bash
# ============================================================================
# Rota AI -- Linux AppImage Build Script
# ============================================================================
# Builds a PyInstaller-based AppImage for Linux distribution.
# Prerequisites: PyInstaller, appimagetool, system libs (see setup-linux.sh)
# ============================================================================

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${REPO_DIR}/build-linux"
DIST_DIR="${REPO_DIR}/dist"
APP_DIR="${BUILD_DIR}/AppDir"
VENV_DIR="${REPO_DIR}/.venv"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}[1/5] Preparing build directory...${NC}"
rm -rf "${BUILD_DIR}" "${DIST_DIR}"
mkdir -p "${APP_DIR}/usr/bin" "${APP_DIR}/usr/lib" "${APP_DIR}/usr/share/applications" "${APP_DIR}/usr/share/icons/hicolor/256x256/apps"

echo -e "${GREEN}[2/5] Building with PyInstaller...${NC}"
cd "${REPO_DIR}"
if [ -f "${VENV_DIR}/bin/activate" ]; then
    source "${VENV_DIR}/bin/activate"
fi
export PYTHONPATH="${REPO_DIR}/desktop:${PYTHONPATH:-}"

pyinstaller \
    --clean \
    --noconfirm \
    --onedir \
    --name "RotaAI" \
    --distpath "${APP_DIR}/usr/bin" \
    --add-data "desktop/assets:assets" \
    --hidden-import=evdev \
    --hidden-import=keyring \
    --hidden-import=structlog \
    --hidden-import=PyQt6.sip \
    desktop/app/main.py

echo -e "${GREEN}[3/5] Creating AppImage metadata...${NC}"

# .desktop file
cat > "${APP_DIR}/usr/share/applications/rota-ai.desktop" << 'DESKTOP'
[Desktop Entry]
Type=Application
Name=Rota AI
Comment=Open source voice dictation
Exec=RotaAI
Icon=rota-ai
Terminal=false
Categories=Utility;Accessibility;
Keywords=voice;dictation;accessibility;transcription;
DESKTOP

# AppRun script
cat > "${APP_DIR}/AppRun" << 'APPRUN'
#!/bin/bash
SELF_DIR="$(dirname "$(readlink -f "$0")")"
export PATH="${SELF_DIR}/usr/bin/RotaAI:${PATH}"
export PYTHONPATH="${SELF_DIR}/usr/bin/RotaAI:${PYTHONPATH:-}"
exec "${SELF_DIR}/usr/bin/RotaAI/RotaAI" "$@"
APPRUN
chmod +x "${APP_DIR}/AppRun"

# Icon (copy from assets if exists, otherwise use placeholder)
if [ -f "${REPO_DIR}/desktop/assets/icon.svg" ]; then
    cp "${REPO_DIR}/desktop/assets/icon.svg" "${APP_DIR}/usr/share/icons/hicolor/256x256/apps/rota-ai.svg"
    cp "${REPO_DIR}/desktop/assets/icon.svg" "${APP_DIR}/rota-ai.svg"
else
    # Create a minimal SVG icon
    cat > "${APP_DIR}/rota-ai.svg" << 'ICON'
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256">
  <rect width="256" height="256" rx="32" fill="#0e0e12"/>
  <text x="128" y="160" font-family="monospace" font-size="120" fill="#e4f222" text-anchor="middle" font-weight="bold">R</text>
</svg>
ICON
    cp "${APP_DIR}/rota-ai.svg" "${APP_DIR}/usr/share/icons/hicolor/256x256/apps/rota-ai.svg"
fi

echo -e "${GREEN}[4/5] Downloading appimagetool...${NC}"
if ! command -v appimagetool &>/dev/null; then
    ARCH=$(uname -m)
    # Validate arch is one of the known values before using in URL
    case "${ARCH}" in
        x86_64|aarch64|armhf) ;;
        *) echo -e "${RED}Unsupported architecture: ${ARCH}${NC}" && exit 1 ;;
    esac
    curl -fsSL -o /tmp/appimagetool \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage"
    chmod +x /tmp/appimagetool
    APPIMAGETOOL="/tmp/appimagetool"
else
    APPIMAGETOOL="appimagetool"
fi

echo -e "${GREEN}[5/5] Building AppImage...${NC}"
cd "${DIST_DIR}"
ARCH=$(uname -m) "${APPIMAGETOOL}" "${APP_DIR}" "RotaAI-${ARCH}.AppImage"

# Rename to standard name
mv "RotaAI-${ARCH}.AppImage" "RotaAI.AppImage"

echo ""
echo -e "${GREEN}Build complete!${NC}"
ls -lh "${DIST_DIR}/RotaAI.AppImage"
