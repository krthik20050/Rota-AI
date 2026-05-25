# Development Guide

## Setup

### Windows
```bash
git clone https://github.com/krthik20050/Rota-AI.git
cd Rota-AI
run.bat  # Creates venv, installs deps, launches
```

### Linux
```bash
git clone https://github.com/krthik20050/Rota-AI.git
cd Rota-AI
bash linux/setup-linux.sh  # System deps
bash linux/run.sh          # Launch
```

## Project Structure

```
desktop/
├── app/           # Application controllers, wiring, entry point
├── ai/            # AI text processing (cleanup, prompts, utils)
├── audio/         # Audio pipeline (recording, VAD, transcription, hotkeys)
├── data/          # Data layer (config, history, snippets, dictionary)
├── injection/     # Windows text injection (SendInput, UI Automation)
├── plat/          # Platform abstraction (Linux hotkeys, injection, windows)
├── ui/            # User interface (windows, overlay, styles, pages)
├── utils/         # Shared utilities (logging, window effects)
└── tests/         # Unit tests
```

## Key Patterns

### Platform Abstraction

All platform-specific code goes through `plat/`:

```python
from plat import get_hotkey_handler, get_injector

hotkey_handler = get_hotkey_handler()  # Windows: pynput, Linux: evdev
injector = get_injector()              # Windows: SendInput, Linux: xdotool
```

**Rule:** Code outside `plat/` and `injection/` must never import platform-specific modules directly.

### Threading

- **Main thread**: Qt event loop, all UI operations
- **Hotkey thread**: Keyboard monitoring (daemon)
- **ProcessorThread**: Background transcription + AI cleanup (QThread)

**Critical rule:** No Qt widget methods from background threads. Use `QTimer.singleShot(0, fn)` to post work back to the main thread.

### Service Wiring

Services are wired in `desktop/app/service_wiring.py`. This is the composition root where all dependencies are created and connected.

### Mixin Architecture

The main app controller (`rota_app.py`) uses mixins for separation of concerns:

- `HotkeyMixin` — Hotkey registration and handling
- `RecordingStateMixin` — Recording state management
- `TranscriberMixin` — Transcription backend management
- `ProcessingPipelineMixin` — AI cleanup pipeline
- `ThreadLifecycleMixin` — Thread management
- `SignalBridges` — Qt signal/slot connections

## Adding a New Feature

1. **Identify the layer**: UI, audio, AI, data, injection, or platform?
2. **Add to the appropriate module**
3. **Wire it in `service_wiring.py`** if it is a new service
4. **Add tests in `desktop/tests/`**
5. **Update this doc** if it changes the architecture

## Adding a New Transcription Backend

1. Create a new class in `desktop/audio/transcriber.py`:
```python
class NewBackendTranscriber(BaseTranscriber):
    def transcribe(self, audio_bytes: bytes) -> str:
        # Your implementation
        pass
```

2. Register it in `desktop/app/service_wiring.py`:
```python
def _create_transcriber(self):
    if backend == "new_backend":
        return NewBackendTranscriber(config=self._config)
```

3. Add the option to settings UI in `desktop/ui/pages/`

4. Add tests in `desktop/tests/test_transcriber.py`

## Code Style

- Python 3.12+ type hints
- Docstrings for all public methods
- Keep functions small and single-purpose
- Match existing code style
- No em dashes in user-facing strings

## Commit Messages

```
type(scope): description

# Types: feat, fix, docs, refactor, test, chore
# Examples:
feat(audio): add noise reduction pre-processing
fix(ui): overlay not hiding on recording stop
docs: add platform support matrix
```

## Pull Request Workflow

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes, add tests
4. Run tests: `python -m pytest desktop/tests/ -v`
5. Commit with clear messages
6. Push and open a PR
7. CI must pass before merge
