# Building from Source

## Prerequisites

- Python 3.12 or 3.13
- Git

## Windows

### Quick Start

```bash
git clone https://github.com/krthik20050/Rota-AI.git
cd Rota-AI
run.bat
```

`run.bat` handles everything: Python detection, venv creation, dependency install, and launch.

### Build Installer (.exe)

```bash
pip install pyinstaller
pip install -r requirements.txt
pyinstaller rota-ai.spec --clean --noconfirm

# Build installer (requires Inno Setup)
# Download from https://jrsoftware.org/isdl.php
iscc installer.iss
```

Output: `installer-output/RotaAI-Setup.exe`

## Linux

### Quick Start

```bash
git clone https://github.com/krthik20050/Rota-AI.git
cd Rota-AI
bash linux/setup-linux.sh
# Log out and back in (or: newgrp input)
bash linux/run.sh
```

### Build AppImage

```bash
pip install pyinstaller
pip install -r linux/requirements-linux.txt
bash linux/build-linux.sh
```

Output: `dist/RotaAI.AppImage`

### Manual Build (without scripts)

```bash
# System dependencies (Ubuntu/Debian)
sudo apt-get install -y \
  libportaudio2 portaudio19-dev \
  libdbus-glib-1-dev libdbus-1-dev \
  at-spi2-core xvfb xdotool wl-clipboard \
  python3-pyatspi ffmpeg \
  fuse libfuse2

# Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r linux/requirements-linux.txt
pip install pyinstaller

# Build
pyinstaller rota-ai.spec --clean --noconfirm
```

## macOS

### Quick Start

```bash
git clone https://github.com/krthik20050/Rota-AI.git
cd Rota-AI
brew install portaudio
python3 -m venv .venv
source .venv/bin/activate
pip install -r macos/requirements-macos.txt
python3 desktop/app/main.py
```

### Build Downloadable .app Zip

```bash
chmod +x macos/build-macos.sh
./macos/build-macos.sh
```

Output:
- `dist/RotaAI.app`
- `dist/RotaAI-macOS.zip`

By default, local builds are ad-hoc signed. For public production downloads, set these environment variables before running the build:

```bash
export MACOS_CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"
export APPLE_ID="developer@example.com"
export APPLE_TEAM_ID="TEAMID"
export APPLE_APP_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"
./macos/build-macos.sh
```

Without Developer ID signing and notarization, macOS Gatekeeper can warn users before the app opens.

### macOS-Specific Dependencies

Some features require additional setup:

```bash
# For AXUIElement text injection (Accessibility)
# Grant Accessibility permission to Terminal/Python in:
# System Settings → Privacy & Security → Accessibility

# For hotkey capture (Input Monitoring)
# Grant Input Monitoring permission to Terminal/Python in:
# System Settings → Privacy & Security → Input Monitoring

# For first-run dependency checks and macOS platform APIs
pip install -r macos/requirements-macos.txt
```

## Release Process

Releases are automated via GitHub Actions (`.github/workflows/release.yml`).

1. Update version in `desktop/app/version.py`
2. Commit and push
3. Create a tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. GitHub Actions automatically:
   - Builds Windows installer (`.exe`)
   - Builds Linux AppImage (`.AppImage`)
   - Builds macOS `.app` bundle and `RotaAI-macOS.zip`
   - Creates a GitHub Release with all artifacts

For production macOS releases, configure these GitHub repository secrets:

- `MACOS_CODESIGN_IDENTITY`
- `APPLE_ID`
- `APPLE_TEAM_ID`
- `APPLE_APP_SPECIFIC_PASSWORD`

If these secrets are missing, CI still builds an ad-hoc signed macOS zip for testing, but it should not be treated as a frictionless public download.

## CI

Every push to `main`/`develop` and every PR triggers CI (`.github/workflows/ci.yml`):
- **Linux:** Python 3.12 + 3.13, import checks, smoke tests, unit tests
- **Windows:** Python 3.12 + 3.13, import checks, unit tests
- **macOS:** Python 3.12 + 3.13, import checks, unit tests
- **Lint:** Syntax checks, Windows-only import leak detection, security scan
