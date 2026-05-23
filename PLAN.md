# Rota AI Build Plan

## Architecture Overview
Rota AI is a single-process Python desktop application (PyQt6) that provides a global system-wide voice dictation service. It operates primarily in the background (system tray) with a frameless overlay that appears during recording.

### Core Components
1. **`core.recorder`**: Manages the microphone stream via `sounddevice` (16kHz mono). Computes RMS amplitude for the waveform animation.
2. **`core.transcriber`**: Runs `faster-whisper` (base model, int8, CPU) in a background thread to process streaming audio chunks.
3. **`core.ai_processor`**: Interfaces with the Gemini API to clean transcribed text or generate AI prompts based on specific trigger phrases.
4. **`core.injector`**: Uses `pyperclip` and `keyboard`/`pyautogui` to paste text into the active window. Detects if a text field is active (fallback: toast notification and copy to clipboard).
5. **`core.hotkey`**: Manages the global F9 hook (hold-to-record or toggle).
6. **`ui.overlay`**: A PyQt6 frameless, transparent window containing a custom widget that draws the 24-bar spring-physics waveform based on the RMS amplitude stream.
7. **`ui.tray`**: System tray icon with context menu for Settings, History, and Exit.
8. **`ui.settings_window`**: PyQt6 dialog for configuring hotkeys, API keys, and preferences.
9. **`ui.history_window`**: PyQt6 dialog displaying the last 200 transcriptions from SQLite.
10. **`data.history`**: SQLite database interface for storing transcriptions.
11. **`data.config`**: JSON configuration manager.

## Data Flow
User presses F9 -> `core.hotkey` triggers `core.recorder` -> audio stream chunks sent to `core.transcriber` -> partial transcripts emitted.
User releases F9 -> `core.recorder` stops -> final audio processed -> raw text sent to `core.ai_processor` -> cleaned text sent to `core.injector` -> text pasted.

## Edge Cases Handled
- **No Gemini API Key:** Skips AI processing, injects raw text. Warns user once via Toast.
- **Short Audio (< 0.5s):** Discarded silently.
- **No Text Field Active:** Cannot safely inject -> copies text to clipboard, shows Toast notification.
- **Long Audio (> 60s):** Auto-stops recording, processes what was captured, shows Toast.
- **Model Missing:** Downloads automatically on first run with a Toast progress indicator.
- **App Already Running:** Detects single instance (mutex/lockfile) and exits immediately.

## Test Plan
- **Unit Tests:** `test_injector.py` (mock clipboard), `test_ai_processor.py` (mock Gemini API response), `test_hotkey.py`.
- **E2E Manual QA:** Test injection in Chrome, VS Code, Notepad, Slack, and Windows Terminal.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 1 | PASS | Scope is tight and well-defined for a Windows utility. |
| Eng Review | `/plan-eng-review` | Architecture & tests | 1 | PASS | PyQt6 single-process architecture is correct for RAM targets. |
| Design Review | `/plan-design-review` | UI/UX gaps | 1 | PASS | Waveform must use QPainter for performance. |

**VERDICT:** Plan APPROVED automatically via YOLO mode parameters. Proceed to implementation.