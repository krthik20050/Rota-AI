# Architecture Improvement Recommendations

Based on a comprehensive audit of the Rota AI codebase, here are recommendations organized by impact and effort.

---

## High Impact / Low Effort (Quick Wins)

### 1. Add a `--version` CLI flag

**File:** `desktop/app/main.py`
**Effort:** 5 minutes

The argparse parser already exists (for `--hotkey-backend`). Add `--version` to print the version string and exit. This is standard CLI hygiene and helps users and CI scripts verify which build is installed.

```python
parser.add_argument("--version", action="store_true", help="Print version and exit")
if args.version:
    from app.version import __version__
    print(f"Rota AI v{__version__}")
    sys.exit(0)
```

### 2. Use Specific Exception Types (Low-hanging fruit)

**Files:** Multiple, especially `plat/linux_*.py` and `injection/`
**Effort:** Medium across ~30 files, but can be done incrementally

The codebase has ~250 `except Exception:` blocks. While many are legitimate (defensive programming in a system-level app), some should be tightened. **Focus on the platform modules first:**

```python
# Current (too broad)
except Exception:
    logger.exception("clipboard_copy_error")

# Better
except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
    logger.warning("clipboard_cmd_timeout")
except PermissionError:
    logger.error("clipboard_permission_denied")
except OSError as e:
    logger.error("clipboard_os_error", error=str(e))
```

**Prioritize** the platform modules (`plat/`, `audio/`) over UI code, where broad `except` is more acceptable (`show_crash_dialog` fallbacks, etc.).

### 3. Add `pyproject.toml` for CLI Entry Point

**Effort:** 15 minutes

Replace the `main.py` entry point with a proper `pyproject.toml` `[project.scripts]` entry so the app can be launched as `rota` after `pip install`:

```toml
[project.scripts]
rota = "app.main:run"
```

---

## Medium Impact / Medium Effort

### 4. Injector Module Global State → Class-Based State

**Files:** `desktop/plat/linux_injector.py`, `desktop/plat/macos_injector.py`, `desktop/injection/injector.py`
**Effort:** 1-2 hours

**Problem:** The injectors use module-level globals for undo state:

```python
# linux_injector.py
global _last_undo_content, _last_injected_text
global _last_injected_field_info, _last_injected_window, _last_injected_correlation_id
```

Six `global` declarations. These leak across recording sessions and make testing impossible without monkeypatching.

**Solution:** Wrap undo state in a dataclass, attach it to the `TextInjector` instance:

```python
@dataclass
class InjectorState:
    undo_content: str | None = None
    injected_text: str | None = None
    field_info: dict | None = None
    correlation_id: str | None = None

class TextInjector:
    def __init__(self):
        self._state = InjectorState()
```

This makes state per-instance, testable, and doesn't leak between sessions.

### 5. Reduce Circular / Implicit Imports

**Files:** `desktop/app/main.py`, `desktop/app/controller.py`, `desktop/app/rota_app.py`
**Effort:** 1-2 hours

**Problem:** `controller.py` imports `RotaApp` and many other symbols that are re-exported for `main.py`. This creates a large "barrel import" that makes dependency tracing difficult.

```python
# controller.py — barrel import
from app.controller import (
    RotaApp,
    configure_logging,
    logger,
    try_acquire_instance_listener,
    wake_existing_instance,
)
```

**Solution:** Move CLI parsing, logging config, and instance listener into their own small modules. Keep `controller.py` lean.

### 6. Config Manager → Data Class + Validation

**File:** `desktop/data/config.py`
**Effort:** 1-2 hours

**Problem:** The config manager uses raw string keys everywhere (`self.config.get("model_size", "base")`). No type safety, no autocomplete, no default-value documentation.

**Solution:** Define a typed config dataclass with defaults and validation:

```python
@dataclass
class AppConfig:
    hotkey: str = "f9"
    hotkey_mode: str = "toggle"
    model_size: str = "base"
    cpu_threads: int = 0
    ai_provider: str = "gemini"
    ai_enabled: bool = True
    history_days: int = 30
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:1b"
    # ... etc
```

The config manager reads/writes JSON but returns strongly-typed `AppConfig`. This eliminates `str()` casts, `bool()` casts, and potential `None` crashes throughout the codebase.

---

## High Impact / High Effort (Architecture)

### 7. Plugin-Based Platform Module Registry

**Files:** `desktop/plat/__init__.py` + all platform modules
**Effort:** 3-4 hours

**Problem:** Platform selection is a chain of `if-elif` statements:

```python
def get_hotkey_handler():
    if IS_LINUX: from plat.linux_hotkey import HotkeyHandler
    elif IS_MACOS: from plat.macos_hotkey import HotkeyHandler
    else: from audio.hotkey import HotkeyHandler
```

Adding a new platform (e.g. FreeBSD, ChromeOS) or replacing a backend requires editing this file. It also makes tests harder — you have to use sys.platform patching.

**Solution:** Use a registry pattern:

```python
# plat/__init__.py
_handlers: dict[str, type] = {}

def register_platform(platform: str, handler: type) -> None:
    _handlers[platform] = handler

def get_hotkey_handler() -> type:
    key = "linux" if IS_LINUX else ("macos" if IS_MACOS else "windows")
    return _handlers.get(key) or _handlers["windows"]

# Each platform module registers itself at import time:
# plat/linux_hotkey.py → at module level: register_platform("linux", HotkeyHandler)
```

This enables:
- **Testability:** `register_platform("linux", MockHandler)` in tests
- **Extensibility:** Third-party backends could register
- **Lazy loading:** Only import what's needed

### 8. Processing Pipeline → State Machine

**Files:** `desktop/app/recording_state_mixin.py`, `desktop/app/processing_pipeline_mixin.py`
**Effort:** 4-6 hours

**Problem:** The recording state machine is implicit — state transitions are scattered across mixins with manual `self._set_state()` calls. Invalid transitions are possible (and some are guarded with if-checks scattered around).

| Current State | Event | Next State | Guard |
|--------------|-------|-----------|-------|
| IDLE | hotkey_start | LISTENING | Must not be processing |
| LISTENING | hotkey_stop | PROCESSING | Must be recording |
| PROCESSING | complete | IDLE | Must have result |
| ERROR | recovery | IDLE | Must not be recording |

**Solution:** Use a formal state machine library (`transitions` or a simple 40-line state machine):

```python
class RecordingStateMachine:
    transitions = [
        ("start_recording", RecordingState.IDLE, RecordingState.LISTENING),
        ("stop_recording", RecordingState.LISTENING, RecordingState.PROCESSING),
        ("finish_processing", RecordingState.PROCESSING, RecordingState.IDLE),
        ("error", ["LISTENING", "PROCESSING"], RecordingState.ERROR),
        ("recover", RecordingState.ERROR, RecordingState.IDLE),
    ]
```

This eliminates race conditions, makes invalid transitions crash during development (not silently), and makes the state flow visible at a glance.

### 9. Coverage Gaps — Targeted Test Additions

**Files:** `desktop/tests/` (missing coverage in several areas)
**Effort:** 2-3 hours

| Module | Existing Tests | Missing |
|--------|---------------|---------|
| `plat/linux_hotkey.py` | Platform compat (basic) | `start_listening()` modes (hold/toggle), extra hotkey dispatch, modifier-only chords |
| `plat/linux_injector.py` | None | Clipboard copy, xdotool/wtype injection, undo |
| `plat/linux_window.py` | None | Focused field detection, active window detection |
| `injection/injector.py` | None | All injector behavior |
| `injection/field_detector.py` | None | All field detection |
| `audio/transcriber.py` | AI processor tests (partial) | Groq/local switching, error recovery, VAD integration |
| `audio/recorder.py` | None | Start/stop lifecycle, audio level signals |
| `ui/` | None | All UI components (hard with Qt, but integration tests possible) |

The highest ROI: `linux_injector.py` and `linux_window.py` tests since they're platform-critical and entirely uncovered.

### 10. Thread Safety Audit

**Effort:** 2-3 hours (analysis only)

The threading model is solid (QThread for processing, threading.Thread for hotkey listeners), but the locks are used inconsistently:

| Lock | Module | Used Consistently? |
|------|--------|-------------------|
| `self._state_lock` (RLock) | rota_app.py | ✅ Yes |
| `self._lock` | linux_hotkey.py | ✅ Yes |
| `self._lock` | linux_portal.py | ✅ Yes |
| `self._lock` | macos_hotkey.py | ✅ Yes |
| `self._write_lock` | history.py | ✅ Yes |
| `self._write_lock` | session_store.py | ✅ Yes |
| `self._state_lock` | transcriber.py | ✅ Yes |
| `_sd_lock` (module-level) | recorder.py | ⚠️ Module-level, only for init |
| `_lock` (module-level) | vad.py | ✅ Yes, for model singleton |
| `self._lock` | rate_limiter.py | ✅ Yes |

**Verdict:** Lock usage is actually quite good. The main concern is the module-level `global` state in injectors (covered in #4 above).

---

## Summary Priority Matrix

| # | Improvement | Impact | Effort | Priority |
|---|-------------|--------|--------|----------|
| 1 | `--version` flag | Low | 5 min | 🟢 Quick |
| 2 | Platform exception narrowing | Medium | Incremental | 🟢 Quick |
| 3 | `pyproject.toml` entry point | Medium | 15 min | 🟢 Quick |
| 4 | Injector state → class-based | High | 1-2 hrs | 🟡 Medium |
| 5 | Reduce barrel imports | Medium | 1-2 hrs | 🟡 Medium |
| 6 | Typed config dataclass | High | 1-2 hrs | 🟡 Medium |
| 7 | Plugin platform registry | High | 3-4 hrs | 🔴 Investment |
| 8 | Formal state machine | High | 4-6 hrs | 🔴 Investment |
| 9 | Test coverage gaps | High | 2-3 hrs | 🟡 Medium |
| 10 | Thread safety audit | Medium | 2-3 hrs | 🟡 Medium |

**Recommendation:** Start with #4 (injector state) and #6 (typed config) — they provide the most immediate benefit for reliability and developer experience.
