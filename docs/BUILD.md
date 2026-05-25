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
   - Creates a GitHub Release with both artifacts

## CI

Every push to `main`/`develop` and every PR triggers CI (`.github/workflows/ci.yml`):
- **Linux:** Python 3.12 + 3.13, import checks, smoke tests, unit tests
- **Windows:** Python 3.12 + 3.13, import checks, unit tests
- **Lint:** Syntax checks, Windows-only import leak detection
