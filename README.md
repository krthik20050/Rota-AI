<div align="center">

# Rota AI

### Free, open source voice dictation for Windows, macOS, and Linux. Speak in any app. No subscriptions. No cloud lock. No typing.

[![GitHub Release](https://img.shields.io/github/v/release/krthik20050/Rota-AI?style=for-the-badge&color=black)](https://github.com/krthik20050/Rota-AI/releases)
[![GitHub Stars](https://img.shields.io/github/stars/krthik20050/Rota-AI?style=for-the-badge&color=yellow)](https://github.com/krthik20050/Rota-AI/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/krthik20050/Rota-AI?style=for-the-badge&color=blue)](https://github.com/krthik20050/Rota-AI/network/members)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/krthik20050?style=for-the-badge&color=ea4aaa&logo=github-sponsors)](https://github.com/sponsors/krthik20050)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5E5B?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/karthik)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white&style=flat-square)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-41CD52?logo=qt&logoColor=white&style=flat-square)](https://www.riverbankcomputing.com/software/pyqt/)
[![Whisper](https://img.shields.io/badge/Faster--Whisper-STT-FF6F00?logo=openai&logoColor=white&style=flat-square)](https://github.com/SYSTRAN/faster-whisper)

<sup>Rota AI is a free alternative to Wispr Flow. Open source voice dictation software for Windows. Speak into any application. AI cleans up your speech, removes filler words, formats text, and injects it wherever your cursor is. Local offline transcription via Ollama. Cloud transcription via Groq and Gemini. Privacy first with encrypted API key storage and local SQLite history. The best free voice to text app for Windows. The best Wispr Flow alternative. The best open source speech recognition desktop app. Voice typing. Voice input. Dictation software. Speech to text. Text to voice. Voice commands. Voice control. Hands free typing. AI dictation. AI transcription. Local AI. Offline AI. Private AI voice.</sup>

</div>

---

## How It Started

I am a student nd when I first tried Wispr Flow. I was honestly amazed. The way it just understood what I was saying, cleaned it up, and dropped it into whatever app I was using. It felt like the future.

Then my 14 day free trial ended.

I could not go back to typing. My fingers felt slow. Everything felt slow.

So I started thinking. Why can't I build something like this myself? How hard could it be?

It turned out to be very hard.

I spent months learning how voice dictation actually works under the hood. I reverse engineered how Wispr Flow processes audio, how it does its AI cleanup, how it detects what app you are in, how it injects text. I learned about speech recognition models, voice activity detection, prompt engineering for LLMs, Windows UI Automation, global hotkey hooks, text injection methods. Things I never thought I would need to know as a student.

I used a lot of system architecture design patterns to make this work. The pipeline had to be fast. The UI had to stay responsive while audio was being processed. The AI cleanup had to feel instant. The text injection had to work in every app, from VS Code to Outlook to Slack.

Special thanks to Claude Code and Cursor for helping me through this journey. They helped me debug issues I was stuck on for days, helped me understand how to structure the codebase, and helped me get through the hard parts when I wanted to give up.

This project taught me more about real software engineering than any course ever did.

And now I am giving it to the open source community. Free. For everyone. Bring your own API keys, or go fully local with Ollama. Use it, test it, break it, build features on top of it. I would love that.

If you are a student like I am, I hope this inspires you to build things too. You do not need a big team or but need a bit of money or funding. You just need curiosity and stubbornness.

---

## Table of Contents

1. [What Rota AI Does](#what-rota-ai-does)
2. [Quick Start](#quick-start)
3. [Choose Your Backend: Cloud API or Local AI](#choose-your-backend-cloud-api-or-local-ai)
4. [Features](#features)
5. [How It Works: Architecture and Pipeline](#how-it-works-architecture-and-pipeline)
6. [Repository Structure](#repository-structure)
7. [How Close Are We to Wispr Flow?](#how-close-are-we-to-wispr-flow)
8. [Supported Models](#supported-models)
9. [FAQ](#faq)
10. [Known Issues](#known-issues)
11. [Contributing](#contributing)
12. [Documentation](#documentation)
13. [Star History](#star-history)
14. [License](#license)

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Project structure, platform abstraction, threading model |
| [docs/BUILD.md](docs/BUILD.md) | How to build from source on Windows and Linux |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues and fixes for both platforms |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute, dev setup, PR workflow |
| [SECURITY.md](SECURITY.md) | Security policy, data privacy, encryption details |
| [FIXES.md](FIXES.md) | Detailed bug fix log |

---

## What Rota AI Does

Rota AI sits on your desktop (Windows, macOS, and Linux). You hold a hotkey (F9 by default). You speak. Rota records your voice, transcribes it, cleans it up with AI, and types the result into whatever app your cursor is in.

That is it. No switching apps. No copy pasting. No subscription. No account. No internet required if you go local.

It works in VS Code, Slack, Notion, Gmail, Word, Discord, your browser, your terminal, any app with a text field.

---

## Quick Start

### Windows

```bash
git clone https://github.com/krthik20050/Rota-AI.git
cd Rota-AI
run.bat
```

`run.bat` handles everything: finds Python, creates a virtual environment, installs dependencies, pulls latest code, and launches Rota AI.

### macOS

```bash
git clone https://github.com/krthik20050/Rota-AI.git
cd Rota-AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

On first run, Rota will prompt you to grant system permissions. Three are required:

1. **Microphone** — for audio recording
2. **Accessibility** — for hotkey capture and text injection
3. **Input Monitoring** — for reliable global hotkeys (Quartz CGEventTap)

To grant permissions: System Settings → Privacy & Security → [permission name] → add Terminal (or your Python interpreter) → toggle on. You may need to restart the app after granting.

> **Note:** macOS depends on `pyobjc` for system integration. Installing with `pip install -r requirements.txt` handles this automatically. If you see import errors for `AppKit`, `ApplicationServices`, or `Quartz`, run `pip install -r requirements.txt` again.

> **Note:** The app must be launched from Terminal (not Finder) for permission prompts to work correctly. You can also run it from VS Code's integrated terminal.

### Linux

```bash
git clone https://github.com/krthik20050/Rota-AI.git
cd Rota-AI
bash linux/setup-linux.sh   # one time: installs system deps + adds you to input group
# log out and back in (or run: newgrp input)
bash linux/run.sh
```

`setup-linux.sh` installs system packages (PortAudio, xdotool, evdev, etc.) and adds your user to the `input` group so evdev can read keyboard events. The group change requires a re-login — or run `newgrp input` in your terminal for an immediate fix without logging out.

**Or download the AppImage** (no Python or git needed):

```bash
chmod +x RotaAI.AppImage
./RotaAI.AppImage
```

The first time you run it, Rota walks you through onboarding. You pick your transcription backend. Cloud API key or local AI. You are ready in under two minutes.

---

## Choose Your Backend: Cloud API or Local AI

> [!NOTE]
> During onboarding, you choose how Rota AI transcribes your voice. You can change this anytime in settings. Both paths are free. Pick what works for you.

### Path A: Bring Your Own API Key (Cloud Transcription)

Create a `.env` file in the project root:

```env
GROQ_API_KEY=gsk_your_key_here
GEMINI_API_KEY=AIza_your_key_here
```

**Groq** gives you the fastest cloud transcription. Their free tier includes Whisper Large v3 at 20 requests per minute and 2,000 requests per day. No credit card needed. Sign up at [console.groq.com/keys](https://console.groq.com/keys).

**Gemini** from Google also has a free tier. Gemini 2.5 Flash and 2.5 Pro are both free with rate limits. No credit card needed. Sign up at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).

Both work great. Groq is faster for transcription. Gemini is more generous with rate limits. You can switch between them in settings anytime.

### Path B: Go Fully Local with Ollama (No Internet, No API Keys)

If you want zero cloud dependency, install [Ollama](https://ollama.com) and run a local model. Rota AI uses it for 100% offline transcription. Your voice never leaves your machine. No API keys. No accounts. No internet. Ever.

### AI Cleanup Pass

Regardless of which transcription backend you pick, Rota AI runs a second AI pass to clean up your text. This is what removes filler words, formats lists, adjusts tone, and makes your speech feel human. For this cleanup pass, you can use:

- **Groq Llama 3.1 8B** (free tier: 30 RPM, 14,400 RPD) for fast cleanup
- **Gemini 2.5 Flash** (free tier, generous limits) for quality cleanup
- **Ollama local model** for fully offline cleanup

Transcription backend and cleanup backend are picked independently during onboarding.

---

## Features

<table>
<tr>
<td width="50%">

### 🧠 AI Text Cleanup

Rota does not dump raw transcription into your app. It **understands what you said** and cleans it up like a human would:

- Removes filler words ("um", "uh", "like", "you know")
- Resolves self corrections ("the price is 200... no wait, 300")
- Handles false starts and stutters
- Converts spoken punctuation into real characters ("comma" → ,)
- Fixes grammar while keeping **your** voice

<table>
<tr>
<td width="50%">

### 📝 Auto Formatting

Rota listens for structure in your speech and formats accordingly:

- **Sequential steps** → numbered lists
- **Parallel items** → bullet points
- **Topic shifts** → paragraph breaks
- **Tone detection** → adjusts output (formal for email, casual for chat, technical for code)

You do not have to say "make this a list". Rota just knows.

</td>
</tr>
</table>

### 🎯 Context Awareness

Rota detects which app you are in before injecting text:

- **VS Code / Cursor** → preserves camelCase, snake_case, CLI commands
- **Outlook / Gmail** → uses formal professional tone
- **Slack / Discord** → keeps it short and casual
- **Browser / Notes** → natural prose

It also **reads the existing text** in the field before injecting, so it never overwrites what you already wrote.

### 🔊 Smart Audio Pipeline

The audio processing chain is designed for accuracy and speed:

- **16kHz mono PCM** capture via PortAudio (sounddevice)
- **Silero VAD v6** strips silence before transcription (2MB model, <1ms per chunk)
- **Dual pass architecture** for short phrases, raw transcription is used directly to save latency
- Configurable VAD threshold, padding, and minimum speech duration

### 🧩 Voice Snippets

Stop typing the same things over and over:

- Say **"insert email"** → your full email signature appears
- Say **"insert address"** → your full address is pasted
- Say **"insert phone"** → your number appears
- Create unlimited custom triggers in settings

Perfect for support replies, calendar links, intro emails, code templates, anything you type more than twice.

### 📖 Personal Dictionary

Rota learns your vocabulary automatically:

- Technical terms, project names, people names, company jargon
- Learns from every correction you make post-injection
- Manual add option for terms you want it to learn immediately
- Stored locally in SQLite, never sent anywhere

### 📊 Productivity Analytics

Track your speaking productivity over time:

- **Words per minute** in real time
- **Clarity score** based on filler word ratio
- **Session history** with full transcription records
- All computed and stored **locally** in SQLite

### 🎨 Desktop Grade UI

Built with PyQt6, every pixel is custom styled:

- **Pure black dark theme** inspired by Apple design language
- **Floating pill overlay** with audio reactive 7-bar waveform
- **System tray** access with one click show/hide
- **Acrylic blur** effects using native Windows compositor (Windows 11 only)
- Dockable, frameless, always-on-top overlay
- Dedicated **onboarding flow** for first time setup

### 🔐 Privacy by Design

Everything about Rota AI is built around keeping your data yours:

- **API keys encrypted** — Windows DPAPI on Windows, system keyring on Linux
- **Transcription history** in local SQLite, no cloud sync
- **Zero telemetry**, no analytics, no phone calls home
- **No servers**, no account, no signup required
- **Full source code** available, audit every line
- Works **100% offline** with Ollama, no internet ever needed

</td>
</tr>
</table>

### 💉 Text Injection Engine

Getting text into applications is harder than it sounds. Rota uses multiple injection methods:

**Windows:**
- **Primary**: Windows SendInput API for keystroke simulation
- **Large text**: Clipboard paste via pyperclip + Ctrl+V
- **Fallback**: pyautogui for stubborn applications
- **Field reader**: Windows UI Automation (IUIAutomationTextPattern) reads existing text before injection
- **Verification**: confirms injection was successful

**Linux:**
- **Primary**: Clipboard paste via xclip/wl-clipboard + Ctrl+V (xdotool or wtype)
- **Focus restore**: xdotool windowactivate before paste
- **Field reader**: AT-SPI (python-xlib) for reading existing text

Works in every app that accepts keyboard input: VS Code, Cursor, Slack, Discord, Notion, Obsidian, Gmail, Outlook, Word, Excel, browsers, terminals, everything.

### ⌨️ Global Hotkeys

Control Rota AI without touching your mouse:

- **F9** (default): push to talk, hold and release
- **Escape**: cancel current session
- **Configurable**: rebind any key in settings

Global hooks via pynput work at the system level, so hotkeys work regardless of which app is focused.

### 🔄 Auto Updating

`run.bat` auto-pulls the latest code from GitHub on every launch. You always run the newest version without thinking about it. No manual updates, no package manager, no prompts. Just double click and you are on the latest.

---

## How It Works: Architecture and Pipeline

Rota AI uses a 7 stage pipeline. Each stage runs on its own thread so the UI never freezes, even while audio is being processed.

### The Pipeline

```
┌──────────────────────────────────────────────────────────────────────┐
│                        STAGE 1: AUDIO CAPTURE                        │
│                                                                      │
│  Microphone input at 16kHz mono PCM                                  │
│  sounddevice library with low latency stream                         │
│  Real time RMS amplitude for waveform visualization                  │
│  PyQt6 signal/slot for thread safe UI updates                       │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  STAGE 2: VOICE ACTIVITY DETECTION                   │
│                                                                      │
│  Silero VAD v6 with ONNX Runtime backend                            │
│  Model size: 2 MB                                                    │
│  ROC-AUC: 0.97 on multi-domain validation (best in class VAD)       │
│  Processing: <1ms per 31ms audio chunk on a single CPU thread        │
│  Strips leading and trailing silence from audio                      │
│  Configurable: padding duration, min speech duration, threshold      │
│  Output: clean audio chunk with only speech content                  │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     STAGE 3: TRANSCRIPTION                           │
│                                                                      │
│  Backend is user configured (picked during onboarding):              │
│                                                                      │
│  [Groq Cloud]                                                        │
│    Whisper Large v3 via Groq API                                    │
│    Free tier: 20 RPM, 2,000 RPD                                      │
│                                                                      │
│  [Gemini Cloud]                                                      │
│    Whisper via Gemini API                                            │
│    Free tier: generous rate limits                                   │
│                                                                      │
│  [Local Ollama]                                                      │
│    Faster Whisper with CTranslate2 backend                          │
│    int8 quantization, runs on CPU or GPU                            │
│    Model options: tiny, base, small, medium, large v3, turbo        │
│    No internet required after model download                         │
│    On RTX 3050: small at 0.07x RTF, turbo at 0.05x RTF             │
│    On CPU only (i5): base at 0.12x RTF                              │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    STAGE 4: AI CLEANUP PASS                          │
│                                                                      │
│  LLM based text processing (second pass after transcription)         │
│                                                                      │
│  What it does:                                                       │
│    Removes filler words and disfluencies                             │
│    Resolves self corrections ("no wait, I meant...")                 │
│    Converts spoken punctuation to characters                         │
│    Formats numbers, dates, currency from spoken form                 │
│    Detects sequential content and creates numbered lists             │
│    Detects parallel items and creates bullet lists                   │
│    Adds paragraph breaks at topic shift boundaries                  │
│    Adjusts register: formal, casual, technical                       │
│    Preserves technical terms and camelCase                           │
│                                                                      │
│  For short phrases (under 5 words), this stage is skipped            │
│  entirely to save latency. Raw transcription is injected directly.   │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    STAGE 5: CONTEXT DETECTION                        │
│                                                                      │
│  Windows UI Automation COM interface                                │
│  Reads active window title and process name                          │
│  Classifies context: code editor, email, chat, notes, browser, other │
│  Reads existing field text using IUIAutomationTextPattern            │
│  Falls back to WM_GETTEXT for classic Win32 controls                │
│  Injection strategy adapts to detected context                       │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     STAGE 6: TEXT INJECTION                          │
│                                                                      │
│  Primary: Windows SendInput API for keystroke simulation             │
│  Large text (>200 chars): clipboard paste via pyperclip + Ctrl+V    │
│  Fallback: pyautogui for stubborn applications                       │
│  pywin32 for focused field interaction                              │
│  Field reader verifies injection was successful                      │
│  Works in any app that accepts keyboard input                        │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      STAGE 7: PERSISTENCE                            │
│                                                                      │
│  SQLite database for all local storage                                │
│    Sessions, transcriptions, snippets, dictionary, analytics         │
│    ACID transactions, indexed queries, partial updates               │
│    Single file, no server, no setup                                  │
│                                                                      │
│  Encrypted config via Windows DPAPI (pywin32)                       │
│    API keys encrypted to current Windows user account                │
│    Not readable by other users or if file is copied                  │
│                                                                      │
│  Analytics computed locally: WPM, clarity score, session duration    │
│  No data leaves the machine. No telemetry. No cloud.                 │
└──────────────────────────────────────────────────────────────────────┘
```

### Why This Architecture

**Threading model**: Each pipeline stage runs on a dedicated QThread. The Qt main thread handles UI only. This means the overlay, waveform display, settings panel, and history view stay smooth and responsive even while audio is being processed, transcribed, and cleaned up simultaneously.

**VAD before transcription**: Silero VAD strips silence before sending audio to the transcription engine. This reduces transcription time, reduces API costs for cloud mode, and improves accuracy because the model does not waste tokens processing silence.

**Two pass design**: Stage 3 transcribes. Stage 4 cleans up. This separation means you can use a fast model for transcription and a smarter model for cleanup. It also means the cleanup pass can be skipped for short phrases where it is not needed, keeping latency low.

**Context detection**: Most dictation apps blindly paste text. Rota reads the active window, classifies the context, and adapts its output. This is the difference between a raw transcription tool and something that feels genuinely smart.

**SQLite over JSON**: Session history, dictionary entries, snippets, and analytics are stored in SQLite. SQLite provides ACID transactions, indexed queries, and partial updates. JSON files would require loading everything into memory for every single operation and offer no data integrity guarantees.

**DPAPI for secrets**: API keys are encrypted with Windows Data Protection API, bound to your Windows user account. Even if someone copies your config file, they cannot read your keys without your Windows login credentials.

---

## Repository Structure

```
Rota-AI/
├── desktop/                          # Main application
│   ├── ai/                          # AI processing layer
│   │   ├── ai_processor.py          # LLM cleanup pass orchestration
│   │   ├── prompts.py               # System prompts and formatting rules
│   │   └── text_utils.py            # Text preprocessing utilities
│   ├── audio/                       # Audio capture and processing
│   │   ├── recorder.py              # Microphone capture via sounddevice
│   │   ├── transcriber.py           # Faster Whisper transcription
│   │   ├── recording_session.py     # Session state management
│   │   ├── hotkey.py                # Global hotkey hooks (pynput)
│   │   └── vad.py                   # Silero VAD integration
│   ├── app/                         # Application lifecycle
│   │   ├── main.py                  # Entry point
│   │   ├── rota_app.py              # QApplication setup
│   │   ├── health_check.py          # Startup diagnostics
│   │   └── hotkey_mixin.py          # Hotkey mixin for main window
│   ├── data/                        # Persistence layer
│   │   └── config_manager.py        # DPAPI encrypted config, SQLite sessions
│   ├── injection/                   # Text injection layer
│   │   ├── injector.py              # SendInput and clipboard injection
│   │   └── field_reader.py          # UI Automation field text reader
│   ├── services/                    # Background services
│   │   ├── session_store.py         # SQLite session persistence
│   │   └── enhanced_insights.py     # Analytics computation
│   ├── ui/                          # User interface
│   │   ├── main_window.py           # Main application window
│   │   ├── settings_window.py       # Settings panel
│   │   ├── onboarding.py            # First run onboarding flow
│   │   ├── components/              # Reusable UI components
│   │   ├── overlay/                 # Floating pill overlay
│   │   │   ├── pill_overlay.py      # Overlay widget
│   │   │   ├── waveform_widget.py   # Audio reactive waveform
│   │   │   └── animation_utils.py   # Easing and animation functions
│   │   ├── pages/                   # Tab pages
│   │   │   ├── home_page.py         # Dashboard
│   │   │   └── insights_page.py     # Analytics page
│   │   └── styles/                  # QSS styling system
│   ├── utils/                       # Utility helpers
│   │   └── native_blur.py           # Windows Acrylic blur (pywin32)
│   └── tests/                       # Test suite
│       ├── test_ai_processor.py     # AI cleanup tests
│       └── test_session_store.py    # Persistence tests
├── main.py                          # Root entry point
├── run.bat                          # One click launcher (auto setup + update)
├── requirements.txt                 # Python dependencies
└── LICENSE                          # MIT License
```

---

## How Close Are We to Wispr Flow?

> [!NOTE]
> I have a Dell G15 with an Intel i5 13th gen (i5-13450HX), 16GB RAM, and an NVIDIA RTX 3050 6GB Laptop GPU. All Rota AI numbers below are from my own testing on this machine. I do not have a Mac so I cannot test Wispr Flow locally. Wispr Flow data comes from their website and user reports. Where I am not sure, I say so.

### The Honest Comparison

| | Wispr Flow (Pro) | SuperWhisper (Pro) | Rota AI (Groq) | Rota AI (Local GPU) |
|---|---|---|---|---|
| **Price** | $15/month | $8.49/month | Free | Free |
| **Free tier** | 2,000 words/week | Unlimited basic models | 2,000 requests/day | Unlimited |
| **Open source** | No | No | Yes (MIT) | Yes (MIT) |
| **Offline mode** | No | Yes | No | Yes (Ollama) |
- **Platforms** | Mac, Windows, iOS, Android | Mac, Windows, iOS | Windows, macOS, Linux | Windows, macOS, Linux |
| **Account required** | Yes | Yes | No | No |
| **AI cleanup / auto editing** | Yes | Yes (multiple modes) | Yes | Yes |
| **Context awareness** | Yes | Yes (reads screen) | Yes (detects active app) | Yes (detects active app) |
| **Voice snippets** | Yes | Yes | Yes | Yes |
| **Personal dictionary** | Yes (syncs across devices) | Yes (syncs across devices) | Yes (local only) | Yes (local only) |
| **Encrypted key storage** | Not disclosed | Not disclosed | Yes (Windows DPAPI) | Yes (Windows DPAPI) |
| **Telemetry sent to cloud** | Yes (cloud based product) | Not fully disclosed | No | No |
| **Custom modes / prompts** | No | Yes (fully custom) | Configurable prompts | Configurable prompts |
| **File transcription** | No | Yes (audio and video) | No | No |
| **Cross device sync** | Yes | Yes | No | No |

### What Wispr Flow Does Better

Wispr Flow is a polished product. It has Mac, iPhone, and Android apps. Your dictionary and snippets sync across all your devices. It has been in development for years and raised $81 million. The UX is refined. The onboarding is smooth. If you want a commercial product with cross platform support and you are willing to pay $15/month, Wispr Flow is the better choice.

### What SuperWhisper Does Better

SuperWhisper costs $8.49/month (cheaper than Wispr Flow). It works on Mac, Windows, and iOS. It supports offline mode. It has more AI modes than Rota AI: Super Mode (reads screen context), Voice Mode, Message Mode, Email Mode, Note Mode, Meeting Mode, and fully custom modes. It can transcribe audio and video files. It has been used by people like Andrej Karpathy and the CEOs of Vercel and Tiny. If you want a cheap, polished, cross platform dictation app with lots of modes, SuperWhisper is a strong option.

### What Rota AI Does Better

Rota AI is free. Not free tier. Free. There is no account, no subscription, no credit card. It is open source so you can read every line of code and verify what it does with your data. API keys are encrypted with Windows DPAPI. There is zero telemetry, nothing sent to any server. It works 100% offline with Ollama and no cloud dependency.

On my RTX 3050 6GB, Rota AI with Groq cloud transcription feels faster than Wispr Flow for short phrases. For local transcription, RTX 3050 handles Whisper small at int8 comfortably with about 300ms transcription latency. Large v3 turbo fits in the 6GB VRAM at int8. I recommend small or base for RTX 3050 users.

### The Gap

I am honest about what Rota AI is missing compared to Wispr Flow and SuperWhisper:

- No mobile app. iPhone and Android are not supported.
- No cross device sync. Dictionary and snippets stay local.
- No file transcription. You cannot feed it an audio or video file and get a transcript.
- No screen reading. SuperWhisper can read what is on your screen for context. Rota AI only detects which app you are in.
- The AI cleanup pass is good but Wispr Flow has had years of prompt engineering and it shows.
- macOS support is new and still being tested. Report issues on GitHub.

I am working on closing these gaps. But I would rather be honest about where things are than make claims I cannot back up.

---

## Supported Models

### Transcription Models (Faster Whisper, local mode)

| Model | Parameters | Disk Size | VRAM (int8) | CPU RAM (int8) | RTF on RTX 3050 | RTF on i5 CPU |
|---|---|---|---|---|---|---|
| tiny | 39M | 75 MB | ~400 MB | ~300 MB | 0.04x (25x RT) | ~0.09x (11x RT) |
| base | 74M | 140 MB | ~600 MB | ~500 MB | 0.05x (20x RT) | ~0.12x (8.7x RT) |
| small | 244M | 480 MB | ~900 MB | ~1.5 GB | 0.07x (14x RT) | ~0.19x (5.4x RT) |
| medium | 769M | 1.5 GB | ~1.5 GB | ~2.5 GB | 0.14x (7x RT) | ~0.39x (2.6x RT) |
| large v3 turbo | 809M | 1.5 GB | ~1.5 GB | ~2.5 GB | 0.05x (20x RT) | ~0.26x (3.9x RT) |
| large v3 | 1550M | 3.1 GB | ~3.0 GB | ~5 GB | ~0.75x (1.3x RT) | ~0.64x (1.6x RT) |

> [!TIP]
> For a Dell G15 with RTX 3050 6GB, **small or large v3 turbo at int8** is the best balance. Large v3 also fits in 6GB VRAM. For CPU only, **base or small** are the only models that transcribe faster than realtime.

### AI Cleanup Models

| Model | Provider | Parameters | Context Window | Free Tier |
|---|---|---|---|---|
| Llama 3.1 8B instant | Groq | 8B | 128K | 30 RPM, 14,400 RPD |
| Llama 3.3 70B versatile | Groq | 70B | 128K | 30 RPM, 1,000 RPD |
| Gemini 2.5 Gemini 2.5 Flash | Google | Undisclosed | 1M | Generous |
| Gemini 2.5 Flash Lite | Google | Undisclosed | 1M | Generous |
| Any local GGUF model | Ollama | Varies | Varies | Unlimited |

---

## FAQ

### Is Rota AI really free?

Yes. Completely. The software is MIT licensed open source. Groq and Gemini both have free tiers that are enough for daily use. Ollama is 100% free with no limits. There is no pro plan, no premium tier, no feature lock, no credit card ever needed.

---

### What is the difference between Rota AI and Wispr Flow?

Wispr Flow is a polished commercial product at $15/month after a 14 day trial. It works on Mac, Windows, iPhone, and Android with cross device sync. It has been in development for years.

Rota AI is free and open source. Currently Windows only. Everything is local by design, no account needed. What Rota AI has that Wispr Flow does not: fully local offline mode, encrypted API key storage via Windows DPAPI, zero telemetry, no account required, and you can audit every single line of code.

---

### Can I use Rota AI without an internet connection?

Yes. Install Ollama, download a Whisper model, and Rota AI works 100% offline. No API keys, no accounts, no internet. Your voice data never leaves your computer. This is something Wispr Flow cannot do.

---

### Where are my API keys stored?

Encrypted with Windows DPAPI using pywin32. The encryption is tied to your Windows user account. Even if someone copies your config file, they cannot decrypt your keys without your Windows login. Rota AI has no servers. Your keys are only sent to the API provider you chose (Groq or Gemini) during transcription requests.

---

### Does it work in any app?

If the app has a text field and accepts keyboard input, Rota AI works in it. VS Code, Cursor, Slack, Discord, Notion, Obsidian, Gmail, Outlook, Word, Excel, your browser, your terminal, Steam chat, everything. The text injection layer uses multiple methods (SendInput, clipboard paste, UI Automation) to handle even stubborn applications.

---

### How accurate is the transcription?

Whisper base gives roughly 92-95% word accuracy on clear English speech. Small gives 94-97%. Large v3 turbo gives 96-98%. The AI cleanup pass fixes many remaining errors, especially filler words and self corrections. For technical terms, add them to your personal dictionary and Rota learns them over time.

---

### What languages are supported?

Whisper supports 99+ languages for transcription. The AI cleanup pass currently works best in English. Transcription in other languages works great. AI cleanup for other languages is something I want to add.

---

### Does it work on Mac or Linux?

Windows 10/11, macOS 12+, and Linux are all supported.

**Windows:** Run `run.bat` or `python main.py`. No additional setup needed.

**macOS:** Run `python main.py` after installing dependencies. Three permissions are required (Microphone, Accessibility, Input Monitoring). See [Quick Start → macOS](#macos) for details.

**Linux:** Run `bash linux/run.sh` or use the AppImage. User must be in the `input` group for hotkey detection.

---

### How much disk space do I need?

The Rota AI application itself is about 25 MB. Dependencies (PyQt6, torch, etc.) are about 500 MB. Then the model you choose:
- Whisper base: 140 MB
- Whisper small: 480 MB
- Whisper large v3 turbo: 1.5 GB
- Whisper large v3: 3.1 GB
- Silero VAD: 2 MB
- AI cleanup model (Ollama): 1-5 GB depending on what you pick

---

### What are the minimum system requirements?

**Windows:** Windows 10 or 11, Python 3.10+

**Linux:** Ubuntu 20.04+, Fedora 36+, Arch (or any distro with evdev + X11/Wayland). Python 3.10+. User must be in the `input` group for hotkey detection.

**Both platforms:**
- 4 GB RAM minimum (8 GB recommended)
- Microphone (built in or external)
- For local transcription: 8 GB RAM for base/small, 16 GB for medium/large
- For GPU transcription: NVIDIA GPU with 6+ GB VRAM recommended (RTX 3050 or better)
- For CPU only transcription: any modern quad core processor

---

### Can I use my own fine tuned Whisper model?

Yes. Rota AI supports loading custom model paths. Point it to your fine tuned model in settings and it will use it for transcription.

---

### What Python version do I need?

Python 3.10 or newer. `run.bat` auto detects your Python installation. If you have multiple versions, it picks the newest one.

---

### I found a bug. Where do I report it?

Open an issue on GitHub. I read every single issue and try to respond quickly. Include your Windows version, Python version, chosen backend, and steps to reproduce.

---

## Known Issues

> [!WARNING]
> **Platform support**: Rota AI supports Windows 10/11 and Linux (AppImage). macOS support is planned.

> [!NOTE]
> **Linux — media pause not supported**: On Windows, Rota pauses system audio (Spotify, YouTube, etc.) while recording. On Linux this feature is a no-op. PipeWire/PulseAudio integration is planned.

> [!CAUTION]
> **Linux — keyboard freeze on hard crash**: Rota uses evdev to read keyboard events, which requires holding a file descriptor to `/dev/input/event*`. If the app crashes hard (SIGSEGV or force kill), the keyboard may become unresponsive until the process is fully terminated. This is an inherent limitation of evdev, not fixable in Python. Killing the Rota process (`killall python`) restores normal keyboard operation immediately.

> [!NOTE]
> **Linux — input group required**: The hotkey system requires your user to be in the `input` group. Run `bash linux/setup-linux.sh` once. The change takes effect at next login, or immediately via `newgrp input`.

> [!NOTE]
> **First run model download**: The first time you use a local model, it downloads from Hugging Face. base is 140 MB, small is 480 MB, large v3 is 3.1 GB. This is a one time download. Files are cached and reused.

> [!NOTE]
> **PortAudio**: Audio recording requires PortAudio. `run.bat` handles this automatically on most systems. If you install manually on a minimal Windows install, you may need to install PortAudio separately.

> [!CAUTION]
> **Antivirus false positives**: Some antivirus software flags Rota AI because it uses global hotkeys and injects text into other applications. These are expected behaviors for any dictation app. The code is fully open source. You can verify exactly what it does.

> [!NOTE]
> **DPI scaling**: On monitors with non 100% DPI scaling, some UI elements may render at the wrong size. This is a known Qt6 issue and being worked on.

---

## Contributing

Rota AI is a community project. I built it as a student and I want it to stay open and welcoming.

**Bug reports**: Open an issue. Tell me what happened, what you expected, and how to reproduce it. Include your hardware specs and chosen backend.

**Feature requests**: Open a discussion. I want to hear what you want to build.

**Code contributions**: Fork the repo, make your changes, open a pull request. Keep PRs focused on one thing. Run the tests before submitting.

```bash
git clone https://github.com/YOUR_USERNAME/Rota-AI.git
cd Rota-AI
run.bat

# Run tests
cd desktop
python -m pytest tests/ -v
```

**Testing**: Try Rota AI on your machine with your microphone and your apps. Tell me what works and what does not. Different hardware, different microphones, different Windows versions. Every test helps make this better.

**Documentation**: If something in this README is confusing, wrong, or missing, fix it and open a PR. The README is the first thing people see and I want it to be great.

---

## Star History

If Rota AI is useful to you, a star on GitHub helps other people find it. It takes two seconds and it means a lot to me.

[![Star History Chart](https://api.star-history.com/svg?repos=krthik20050/Rota-AI&type=Date)](https://star-history.com/#krthik20050/Rota-AI&Date)

---

## License

MIT License. Use it however you want. Commercial use, personal use, modify it, redistribute it. Just keep the LICENSE file.

---

<div align="center">

Built by [Karthik Krishnan](https://www.linkedin.com/in/karthik-krishnan-/). A student who wanted to build a Wispr Flow alternative and learned more from this project than from any course.

[Issues](https://github.com/krthik20050/Rota-AI/issues) | [Discussions](https://github.com/krthik20050/Rota-AI/discussions)

Rota AI is not affiliated with Wispr Flow. This is an independent open source project.
</div>
