# Testing

## Running Tests

### All Tests
```bash
# From project root
python -m pytest desktop/tests/ -v

# With coverage
python -m pytest desktop/tests/ -v --cov=desktop --cov-report=html
```

### Platform-Specific Tests
```bash
# Linux
python -m pytest desktop/tests/ -v -k "linux"

# Windows
python -m pytest desktop/tests/ -k "windows"
```

### Single Test File
```bash
python -m pytest desktop/tests/test_ai_processor.py -v
```

## Test Structure

```
desktop/tests/
├── test_ai_processor.py          # AI cleanup pipeline tests
├── test_ai_processor_advanced.py # Edge cases and prompt injection
├── test_auto_improvement.py      # Text improvement tests
├── test_cleanup.py               # Text cleanup/normalization
├── test_controller_stop_flow.py  # Recording stop behavior
├── test_enhanced_insights.py     # Insights/analytics tests
├── test_instance_guard.py        # Single-instance mutex tests
├── test_personal_dictionary.py   # Dictionary management
├── test_rate_limiter.py          # API rate limiter tests
├── test_session_store.py         # Session/history storage
├── test_snippets.py              # Voice snippets tests
└── test_text_utils.py            # Text normalization utilities
```

## What Is Tested

### Audio Pipeline
- Recording start/stop/cancel
- VAD threshold behavior
- Audio buffer management
- Sample rate validation

### Transcription
- Groq API integration (mocked)
- Ollama local model integration (mocked)
- Fallback chain: Groq → Gemini → Ollama
- Language detection
- Error handling for network failures

### AI Cleanup
- Filler word removal
- Punctuation restoration
- Context-aware formatting
- Prompt injection prevention
- Tone adjustment (formal/casual/none)

### Text Injection
- SendInput method (Windows)
- Clipboard paste method
- xdotool method (Linux X11)
- Large text threshold behavior
- Injection delay

### Data Layer
- Config read/write/migration
- History storage and retrieval
- Snippet CRUD operations
- Personal dictionary management
- API key encryption/decryption

## Writing Tests

### Test Naming
```python
def test_<what>_<condition>_<expected>():
    pass

# Examples:
def test_cleanup_removes_filler_words():
    pass

def test_injection_fallback_to_clipboard_on_sendinput_failure():
    pass
```

### Mocking External APIs

Always mock external API calls:

```python
from unittest.mock import patch, MagicMock

@patch("ai.ai_processor.GroqClient")
def test_transcription_uses_groq(mock_groq):
    mock_groq.return_value.transcribe.return_value = "hello world"
    result = transcribe_audio(b"fake_audio")
    assert result == "hello world"
```

### Platform-Specific Tests

Skip tests that do not apply to the current platform:

```python
import pytest
import sys

@pytest.mark.skipif(sys.platform != "linux", reason="Linux-only test")
def test_evdev_hotkey_detection():
    pass

@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
def test_dpapi_encryption():
    pass
```

## CI Testing

Tests run automatically on every push and PR via GitHub Actions:

- **Linux**: Python 3.12, 3.13 on ubuntu-24.04
- **Windows**: Python 3.12, 3.13 on windows-latest
- **Lint**: Syntax checks, import leak detection

See `.github/workflows/ci.yml` for details.

## Manual Testing Checklist

Before releasing, verify:

- [ ] Hotkey starts/stops recording
- [ ] Transcription appears in target app
- [ ] AI cleanup removes filler words
- [ ] Context awareness works in VS Code
- [ ] Context awareness works in Slack
- [ ] Snippets trigger correctly
- [ ] Personal dictionary corrections apply
- [ ] History stores and retrieves entries
- [ ] Settings persist across restarts
- [ ] Ollama local mode works offline
- [ ] Groq cloud mode works with API key
- [ ] Backend fallback works (Groq fails → Ollama)
- [ ] System tray icon appears and responds
- [ ] Recording overlay shows during recording
- [ ] Single-instance guard prevents second launch
