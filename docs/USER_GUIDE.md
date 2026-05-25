# User Guide

## Getting Started

### First Launch

When you first open Rota AI, the onboarding wizard will walk you through:

1. **Choose your transcription backend** — Cloud (Groq/Gemini) or Local (Ollama)
2. **Set your hotkey** — Default is F9. Pick whatever feels comfortable.
3. **Test your microphone** — Speak a sentence and verify the transcription looks right.
4. **You are done.** Close onboarding and start dictating.

### Basic Workflow

1. Click in any text field (VS Code, Slack, browser, whatever)
2. Press F9 (or your chosen hotkey)
3. Speak naturally. Say punctuation out loud: "comma", "period", "new paragraph"
4. Press F9 again to stop
5. Your cleaned-up text appears in the app

That is it. No switching windows. No copy-paste.

## Hotkeys

| Action | Default Key | Configurable |
|--------|-------------|-------------|
| Start/Stop Recording | F9 | Yes |
| Cancel Recording | Escape | Yes |
| Toggle Overlay | F8 | Yes |

Change hotkeys in Settings > Hotkeys. Press your desired key combination and hit Save.

## Transcription Backends

### Cloud (Recommended for Speed)

**Groq** (default)
- Fastest option. Whisper Large v3 Turbo.
- Free tier: generous daily limits
- Requires API key from console.groq.com
- Your audio goes to Groq's servers

**Gemini**
- Google's speech recognition
- Good accuracy, especially for accented English
- Requires API key from aistudio.google.com

### Local (Recommended for Privacy)

**Ollama**
- Runs entirely on your machine
- No internet needed after model download
- Requires Ollama installed (ollama.com)
- Model sizes: Small (250MB), Medium (500MB), Large (1.5GB)
- 8GB RAM minimum for Small, 16GB recommended for Medium

Switch backends in Settings > Transcription > Backend.

## AI Cleanup

After transcription, Rota AI runs a second AI pass to:

- Remove filler words ("um", "uh", "like", "you know")
- Fix grammar and punctuation
- Resolve self-corrections ("I went to the — no, I drove to the store")
- Format based on context (code editor vs email vs chat)

### Cleanup Modes

| Mode | Behavior |
|------|----------|
| Formal | Proper punctuation, no contractions, complete sentences |
| Casual | Relaxed punctuation, contractions allowed, conversational |
| None | Raw transcription, no cleanup |

Change mode in Settings > AI Cleanup > Tone.

### Context Awareness

Rota AI detects which app you are in and adjusts:

- **VS Code / Code editors**: Preserves camelCase, snake_case, CLI commands
- **Email clients**: Formal tone, proper greetings
- **Chat apps (Slack, Discord)**: Casual tone, shorter sentences
- **Browsers**: Adapts to the specific site

Disable in Settings > AI Cleanup > Context Awareness.

## Voice Snippets

Snippets let you insert frequently used text by speaking a trigger phrase.

### Setup

1. Go to Settings > Snippets
2. Add a trigger prefix (default: "insert")
3. Add snippets: trigger phrase → full text

### Example

| Trigger | Output |
|---------|--------|
| insert email | karthik@example.com |
| insert address | 123 Main St, Kerala, India |
| insert signature | Best regards, Karthik |
| insert code header | #!/usr/bin/env python3 |

To use: say "insert email" and the full email appears.

## Personal Dictionary

Add words that Whisper consistently gets wrong:

1. Go to Settings > Dictionary
2. Add the word and its correct spelling
3. Whisper will use your dictionary for future transcriptions

Useful for: technical terms, names, jargon, non-English words.

## Text Injection

Rota AI uses different methods to insert text into apps:

| Method | When Used |
|--------|-----------|
| SendInput (Windows) | Default. Works in most apps. |
| Clipboard Paste | Fallback for stubborn apps. |
| xdotool (Linux/X11) | Default on Linux X11 sessions. |
| wtype/dotool (Linux/Wayland) | Default on Linux Wayland sessions. |

If text is not appearing in a specific app:
1. Go to Settings > Injection
2. Switch to "Clipboard" method
3. Increase injection delay to 10-20ms

## Settings Reference

### Audio Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Sample Rate | 16kHz | Do not change. Whisper expects this. |
| VAD Threshold | 0.5 | Lower = more sensitive. Higher = less sensitive. |
| Padding | 300ms | Silence kept before/after speech. Increase if words get cut off. |

### Transcription Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Backend | Groq | Cloud (Groq/Gemini) or Local (Ollama) |
| Model | whisper-large-v3-turbo | Cloud model or local model size |
| Language | English | Primary language for transcription |

### Injection Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Method | Auto | Auto-detect best injection method |
| Large Text Threshold | 200 chars | Above this, uses clipboard paste |
| Injection Delay | 0ms | Increase if text appears garbled |

## System Tray

Rota AI runs in the system tray. Right-click the icon for:

- **Show/Hide** — Toggle the main window
- **Start/Stop** — Toggle recording
- **Settings** — Open settings window
- **Quit** — Close the app

## History

All transcriptions are stored locally in SQLite. View them in the History window.

- Search by date or content
- Copy any previous transcription
- Delete individual entries or clear all

History stays on your machine. Nothing is sent to any server.

## Keyboard-Only Workflow

For maximum efficiency:

1. `F9` — Start recording
2. Speak your text
3. `F9` — Stop recording
4. Text appears in the active app
5. `Ctrl+Z` — Undo if something went wrong

No mouse needed. Ever.
