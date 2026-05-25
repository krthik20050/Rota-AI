# Contributing to Rota AI

## Getting Started

### Windows

```bash
git clone https://github.com/krthik20050/Rota-AI.git
cd Rota-AI
run.bat
```

### macOS

```bash
git clone https://github.com/krthik20050/Rota-AI.git
cd Rota-AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 desktop/app/main.py
```

**macOS permissions required:**
- **Microphone** — System Settings → Privacy & Security → Microphone → add Terminal
- **Accessibility** — System Settings → Privacy & Security → Accessibility → add Terminal
- **Input Monitoring** — System Settings → Privacy & Security → Input Monitoring → add Terminal

Restart Terminal after granting permissions.

### Linux (Ubuntu/Debian/Fedora/Arch)

```bash
git clone https://github.com/krthik20050/Rota-AI.git
cd Rota-AI
bash linux/setup-linux.sh    # one-time system deps
# Log out and back in (or run: newgrp input)
bash linux/run.sh
```

**Manual setup (without setup-linux.sh):**

```bash
# Install system deps (Ubuntu/Debian)
sudo apt-get install -y python3 python3-pip python3-venv \
  libportaudio2 portaudio19-dev libdbus-glib-1-dev \
  at-spi2-core xvfb xdotool wl-clipboard \
  python3-pyatspi ffmpeg

# Add yourself to input group for evdev hotkey access
sudo usermod -aG input $USER
# Log out and back in, or: newgrp input

# Create venv and install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r linux/requirements-linux.txt

# Run
export QT_QPA_PLATFORM=offscreen  # only if running headless
python3 desktop/app/main.py
```

## Running the App (after setup)

```bash
# Windows
run.bat

# Linux
bash linux/run.sh

# Or directly
python3 desktop/app/main.py
```

## Running Tests

```bash
cd desktop
python -m pytest tests/ -v
```

On Linux CI, tests run automatically via GitHub Actions. See `.github/workflows/ci.yml`.

## API Keys

Copy `.env.example` to `.env` and fill in your keys. **Never commit `.env` or `config.json`** — both are gitignored.

```bash
cp .env.example .env
# Edit .env with your keys
```

## Platform Abstraction Rules

**Critical:** Code outside `plat/` and `injection/` must never import Windows-specific modules directly.

✅ **Correct:**
```python
from plat import get_injector
Injector = get_injector()
injector = Injector()
```

❌ **Wrong:**
```python
from injection.injector import TextInjector  # Windows-only!
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full platform abstraction pattern.

## Pull Request Workflow

1. Fork and create a branch: `git checkout -b fix/your-fix`
2. Keep changes focused — one fix or feature per PR
3. Run tests before submitting: `cd desktop && python -m pytest tests/ -v`
4. Reference any related issue in the PR description
5. PRs to `main` trigger CI automatically (Linux + Windows builds)

## Code Style

- Python — follow PEP 8, keep files under 500 lines
- No debug prints or `console.log` left in commits
- Validate input at system boundaries
- Prefer editing existing files over creating new ones
- Cross-platform code must work on both Windows and Linux

## Security Issues

**Do not** open a public issue for security vulnerabilities. Email directly or use GitHub's private security advisory feature. See [SECURITY.md](SECURITY.md) for the full policy.

## Project Structure

```
desktop/              # Main source
├── app/              # Controllers, service wiring, main window
├── ai/               # AI text processing (cleanup, prompts)
├── audio/            # Recording, transcription, VAD, Windows hotkey
├── data/             # Config, history, snippets
├── injection/        # Windows-only: text injection, field detection
├── plat/             # Cross-platform abstraction layer
│   ├── __init__.py   # Platform routing (import this, not platform modules)
│   ├── linux_*       # Linux-specific implementations
│   └── linux/        # Linux build scripts
├── ui/               # Onboarding, settings, overlay, tray
├── utils/            # Logging, seeding, window effects
└── tests/            # Unit tests
```
