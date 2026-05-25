#!/usr/bin/env bash
# ============================================================================
# Rota AI -- macOS Build Script
# ============================================================================
# Builds dist/RotaAI.app and dist/RotaAI-macOS.zip.
#
# Optional production signing/notarization is controlled by environment:
#   MACOS_CODESIGN_IDENTITY="Developer ID Application: ..."
#   APPLE_ID="developer@example.com"
#   APPLE_TEAM_ID="TEAMID1234"
#   APPLE_APP_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"
# ============================================================================

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${REPO_DIR}/dist"
APP_PATH="${DIST_DIR}/RotaAI.app"
ZIP_PATH="${DIST_DIR}/RotaAI-macOS.zip"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "${REPO_DIR}"

echo -e "${GREEN}[1/5] Checking macOS build prerequisites...${NC}"
if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "macos/build-macos.sh must be run on macOS."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required."
    exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is required for PortAudio. Install from https://brew.sh"
    exit 1
fi

if ! brew list portaudio >/dev/null 2>&1; then
    echo -e "${YELLOW}PortAudio missing; installing with Homebrew...${NC}"
    brew install portaudio
fi

echo -e "${GREEN}[2/5] Preparing Python environment...${NC}"
if [[ "${CI:-}" == "true" ]]; then
    # In CI, deps are pre-installed by the workflow — skip venv
    echo "CI environment: using pre-installed Python environment"
else
    if [[ ! -d ".venv" ]]; then
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    python -m pip install --upgrade pip setuptools wheel
    pip install -r macos/requirements-macos.txt
    pip install pyinstaller
fi

echo -e "${GREEN}[3/5] Building .app with PyInstaller...${NC}"
rm -rf build "${DIST_DIR}/RotaAI" "${APP_PATH}" "${ZIP_PATH}"
export PYTHONPATH="${REPO_DIR}/desktop:${PYTHONPATH:-}"
pyinstaller rota-ai.spec --clean --noconfirm

if [[ ! -d "${APP_PATH}" ]]; then
    echo "Expected app bundle not found: ${APP_PATH}"
    exit 1
fi

echo -e "${GREEN}[4/5] Signing app bundle...${NC}"
if [[ -n "${MACOS_CODESIGN_IDENTITY:-}" ]]; then
    codesign --force --deep --options runtime --timestamp \
        --entitlements macos/entitlements.plist \
        --sign "${MACOS_CODESIGN_IDENTITY}" "${APP_PATH}"
else
    echo -e "${YELLOW}MACOS_CODESIGN_IDENTITY not set; applying ad-hoc signature.${NC}"
    codesign --force --deep --entitlements macos/entitlements.plist --sign - "${APP_PATH}"
fi
codesign --verify --deep --strict "${APP_PATH}"

echo -e "${GREEN}[5/5] Creating downloadable zip...${NC}"
ditto -c -k --keepParent "${APP_PATH}" "${ZIP_PATH}"

if [[ -n "${APPLE_ID:-}" && -n "${APPLE_TEAM_ID:-}" && -n "${APPLE_APP_SPECIFIC_PASSWORD:-}" ]]; then
    echo -e "${GREEN}Submitting for Apple notarization...${NC}"
    xcrun notarytool submit "${ZIP_PATH}" \
        --apple-id "${APPLE_ID}" \
        --team-id "${APPLE_TEAM_ID}" \
        --password "${APPLE_APP_SPECIFIC_PASSWORD}" \
        --wait
    xcrun stapler staple "${APP_PATH}"
    ditto -c -k --keepParent "${APP_PATH}" "${ZIP_PATH}"
else
    echo -e "${YELLOW}Notarization skipped; set Apple notarization env vars for public production releases.${NC}"
fi

echo ""
echo -e "${GREEN}Build complete:${NC} ${ZIP_PATH}"
