# Architecture

## Overview

Rota AI is a cross-platform desktop voice dictation app built with Python, PyQt6, and faster-whisper. It records your voice, transcribes it (via cloud API or local model), cleans up the text with AI, and injects it into whatever app you're using.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| UI Framework | PyQt6 (Qt 6) |
| Language | Python 3.12+] |
| Audio Capture | sounddevice (PortAudio) |
| Voice Activity Detection | Silero VAD v6 |
| Transcription (primary) | Groq Whisper API (cloud) |
| Transcription (fallback) | faster-whisper (local, CTranslate2) |
| AI Cleanup | Gemini API / Groq Llama / Ollama |
|| Text Injection (Windows) | keybd_event (Ctrl+V paste) |
|| Text Injection (Linux) | xdotool / wtype / dotool + clipboard |
|| Text Injection (macOS) | AXUIElement + NSPasteboard + AppleScript Cmd+V |
|| Hotkey Capture (Windows) | pynput |
|| Hotkey Capture (Linux) | evdev |
|| Hotkey Capture (macOS) | pynput + Quartz CGEventTap |
|| Config Storage | JSON file (encrypted at rest) |
|| Secret Storage (Windows) | DPAPI (win32crypt) |
|| Secret Storage (Linux) | keyring (Secret Service / GNOME Keyring) |
|| Secret Storage (macOS) | keyring (macOS Keychain) |
|| Packaging (Windows) | PyInstaller + Inno Setup |
|| Packaging (Linux) | PyInstaller + AppImage |
|| Packaging (macOS) | PyInstaller + .app bundle |

## Project Structure

```
Rota-AI/
├── .github/workflows/        # CI/CD (GitHub Actions)
│   ├── ci.yml                # Runs on every push/PR (Linux + Windows)
│   └── release.yml           # Builds releases on tag push
├── desktop/                  # Main application source
│   ├── app/                  # Application controllers and wiring
│   │   ├── main.py           # Entry point
│   │   ├── rota_app.py       # Main app controller (mixins)
│   │   ├── service_wiring.py # Dependency injection / service setup
│   │   ├── controller.py     # App initialization
│   │   ├── health_check.py   # Startup health checks
│   │   ├── instance_guard.py # Single-instance mutex
│   │   ├── logging_config.py # Structured logging setup
│   │   ├── processor_thread.py # Background transcription threads
│   │   └── version.py        # Version string
│   ├── ai/                   # AI text processing
│   │   ├── ai_processor.py   # AI cleanup pipeline
│   │   ├── prompts.py        # LLM prompt templates
│   │   ├── text_utils.py     # Text normalization
│   │   └── ...
│   ├── audio/                # Audio pipeline
│   │   ├── recorder.py       # PortAudio recording
│   │   ├── transcriber.py    # Whisper transcription (Groq + local fallback)
│   │   ├── vad.py            # Voice activity detection (Silero)
│   │   └── hotkey.py         # Windows hotkey handler (pynput)
│   ├── data/                 # Data layer
│   │   ├── config.py         # Config manager (OS-appropriate paths)
│   │   ├── history.py        # Transcription history (SQLite)
│   │   └── snippets.py       # Voice-triggered text expansion
│   ├── injection/            # Windows-only text injection
│   │   ├── injector.py       # Windows text injector (keybd_event)
│   │   ├── field_detector.py # Windows UI Automation
│   │   └── ...
│   ├── plat/                 # Platform abstraction layer
│   │   ├── __init__.py       # Platform detection and routing
│   │   ├── linux_hotkey.py   # Linux hotkey (evdev)
│   │   ├── linux_injector.py # Linux text injection (xdotool/wtype)
│   │   ├── linux_window.py   # Linux window detection (AT-SPI + xlib)
│   │   ├── linux_secrets.py  # Linux keyring storage
│   │   └── linux_startup.py  # Linux XDG autostart
│   ├── ui/                   # User interface
│   │   ├── onboarding.py     # Onboarding wizard
│   │   ├── main_window.py    # Main dashboard
│   │   ├── settings_window.py
│   │   ├── history_window.py
│   │   ├── tray.py           # System tray icon
│   │   ├── overlay/          # Recording pill overlay
│   │   ├── pages/            # Settings pages
│   │   └── styles/           # QSS stylesheets
│   ├── utils/                # Shared utilities
│   │   ├── log.py            # Structured logger
│   │   ├── seeder.py         # Mock data seeder
│   │   └── window_effects.py # Window blur (Windows) / no-op (Linux)
│   └── tests/                # Unit tests
├── linux/                    # Linux-specific scripts
│   ├── setup-linux.sh        # One-time system setup
│   ├── run.sh                # Linux launcher
│   ├── build-linux.sh        # AppImage build script
│   └── requirements-linux.txt
├── assets/                   # Icons, images
├── requirements.txt          # Windows Python dependencies
├── run.bat                   # Windows launcher
└── rota-ai.spec              # PyInstaller spec
```

## Platform Abstraction

The `plat/` module is the key to cross-platform support. All platform-specific code lives behind a common interface:

```
plat/__init__.py
├── get_hotkey_handler()  → Windows: audio.hotkey.HotkeyHandler (pynput)
│                           Linux:   plat.linux_hotkey.HotkeyHandler (evdev)
│                           macOS:   plat.macos_hotkey.HotkeyHandler (pynput + Quartz)
├── get_injector()        → Windows: injection.injector.TextInjector (keybd_event)
│                           Linux:   plat.linux_injector.TextInjector (xdotool)
│                           macOS:   plat.macos_injector.TextInjector (AXUIElement)
├── get_window_detector() → Windows: injection.field_detector
│                           Linux:   plat.linux_window (AT-SPI + xlib)
│                           macOS:   plat.macos_window (AXUIElement + NSWorkspace)
└── ...

**Rule:** Code outside `plat/`, `injection/`, and `plat/macos_*` must never import platform-specific modules directly. Always go through `plat/`.
**Rule:** Code outside `plat/` and `injection/` must never import Windows-specific modules directly. Always go through `plat/`.

## Audio Pipeline

```
Hotkey pressed
  → AudioRecorder.start() [sounddevice, 16kHz mono]
    → Silero VAD strips silence in real-time
      → On stop: full audio buffer sent to AudioTranscriber
        → Primary: Groq Whisper API (cloud, whisper-large-v3-turbo)
        → Fallback: faster-whisper (local, CTranslate2 int8)
          → AI cleanup pass (Gemini / Groq Llama / Ollama)
            → TextInjector.inject() → clipboard + Ctrl+V
```

## Threading Model

- **Main thread:** Qt event loop, all UI operations
- **Hotkey thread:** evdev/pynput keyboard monitoring (daemon)
- **TranscriberLoadThread:** Background model loading (QThread)
- **ProcessorThread:** Background transcription + AI cleanup (QThread)

**Critical rule:** No Qt widget methods may be called from background threads. Use `QTimer.singleShot(0, fn)` to post work back to the main thread.

## Configuration

| Platform | Config Path | Data Path |
|----------|------------|-----------|
| Windows | `%APPDATA%\RotaAI\config.json` | `%APPDATA%\RotaAI\` |
| Linux | `~/.config/rota-ai/config.json` | `~/.local/share/rota-ai/` |
| macOS | `~/Library/Application Support/RotaAI/config.json` | `~/Library/Application Support/RotaAI/` |

API keys are encrypted at rest:
- **Windows:** DPAPI (win32crypt, AES-256, user-bound)
- **Linux:** keyring (Freedesktop Secret Service / GNOME Keyring)
- **macOS:** keyring (macOS Keychain)
