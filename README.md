<div align="center">

# Rota AI

### Free, open source voice dictation for Windows. Speak in any app. No subscriptions. No cloud lock. No typing.

[![GitHub Release](https://img.shields.io/github/v/release/krthik20050/Rota-AI?style=for-the-badge&color=black)](https://github.com/krthik20050/Rota-AI/releases)
[![GitHub Stars](https://img.shields.io/github/stars/krthik20050/Rota-AI?style=for-the-badge&color=yellow)](https://github.com/krthik20050/Rota-AI/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/krthik20050/Rota-AI?style=for-the-badge&color=blue)](https://github.com/krthik20050/Rota-AI/network/members)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white&style=flat-square)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-41CD52?logo=qt&logoColor=white&style=flat-square)](https://www.riverbankcomputing.com/software/pyqt/)
[![Whisper](https://img.shields.io/badge/Faster--Whisper-STT-FF6F00?logo=openai&logoColor=white&style=flat-square)](https://github.com/SYSTRAN/faster-whisper)

<sup>Rota AI is a free alternative to Wispr Flow. Open source voice dictation software for Windows. Speak into any application. AI cleans up your speech, removes filler words, formats text, and injects it wherever your cursor is. Local offline transcription via Ollama. Cloud transcription via Groq and Gemini. Privacy first with encrypted API key storage and local SQLite history. The best free voice to text app for Windows. The best Wispr Flow alternative. The best open source speech recognition desktop app. Voice typing. Voice input. Dictation software. Speech to text. Text to voice. Voice commands. Voice control. Hands free typing. AI dictation. AI transcription. Local AI. Offline AI. Private AI voice.</sup>

</div>

---

## How It Started

I am student nd when I first tried Wispr Flow. I was honestly amazed. The way it just understood what I was saying, cleaned it up, and dropped it into whatever app I was using. It felt like the future.

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
7. [Performance vs Wispr Flow](#performance-vs-wispr-flow)
8. [Supported Models](#supported-models)
9. [FAQ](#faq)
10. [Known Issues](#known-issues)
11. [Contributing](#contributing)
12. [Star History](#star-history)
13. [License](#license)

---

## What Rota AI Does

Rota AI sits on your Windows desktop. You hold a hotkey (F9 by default). You speak. Rota records your voice, transcribes it, cleans it up with AI, and types the result into whatever app your cursor is in.

That is it. No switching apps. No copy pasting. No subscription. No account. No internet required if you go local.

It works in VS Code, Slack, Notion, Gmail, Word, Discord, your browser, your terminal, any app with a text field.

---

## Quick Start

```bash
git clone https://github.com/krthik20050/Rota-AI.git
cd Rota-AI
run.bat
```

`run.bat` handles everything:
- Finds Python 3.10 or newer on your system
- Creates a virtual environment
- Installs all dependencies
- Pulls the latest code from GitHub on every launch
- Launches Rota AI

The first time you run it, Rota walks you through onboarding. You pick your transcription backend. Cloud API key or local AI. You are ready to go in under two minutes.

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

> **AI Text Cleanup**
> Rota does not dump raw transcription into your app. It understands what you said and cleans it up like a human would. Removes "um", "uh", "like", "you know". Resolves self corrections like "the price is 200 dollars... no wait, 300". Handles false starts and stutters. Converts spoken punctuation ("comma", "period", "new paragraph") into actual characters and formatting.

> **Auto Formatting**
> When you list steps, Rota creates a numbered list. When you list items, it creates bullet points. When you shift topics, it adds paragraph breaks. It detects whether you are being formal, casual, or technical and adjusts the tone of the output to match.

> **Context Awareness**
> Rota detects which app you are in using Windows UI Automation. It preserves camelCase and snake_case in VS Code. It uses formal tone in Outlook. It keeps things short and punchy in Slack. It reads the existing text in the field before injecting so it never overwrites what you already wrote.

> **Voice Snippets**
> Set up voice shortcuts for text you use often. Say "insert email" and your full email signature appears. Say "insert address" and your address is pasted. Stop typing the same things fifty times a day.

> **Personal Dictionary**
> Rota learns your vocabulary over time. Technical terms, project names, people names, company jargon. The more you use it, the better it gets at transcribing your specific words. You can also add terms manually.

> **Productivity Analytics**
> Track your words per minute, clarity scores, and session history. See how much time you are saving compared to typing. All stored locally in SQLite.

> **Dark Mode UI**
> Pure black dark theme inspired by Apple design language. Floating pill overlay with audio reactive waveform that shows when you are recording. System tray access. Acrylic blur effects on Windows 11. Every pixel is custom styled.

> **Privacy First**
> API keys are encrypted with Windows DPAPI, tied to your Windows user account. Transcription history is stored in local SQLite, no cloud sync. No telemetry. No analytics sent anywhere. No servers. No account required. Rota AI does not phone home. Period.

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
│    Latency: ~150ms for short phrases (measured on RTX 3060)         │
│    Free tier: 20 RPM, 2,000 RPD                                      │
│                                                                      │
│  [Gemini Cloud]                                                      │
│    Whisper via Gemini API                                            │
│    Latency: ~250ms for short phrases                                 │
│    Free tier: generous rate limits                                   │
│                                                                      │
│  [Local Ollama]                                                      │
│    Faster Whisper with CTranslate2 backend                          │
│    int8 quantization, runs on CPU or GPU                            │
│    Model options: tiny, base, small, medium, large v3, turbo        │
│    No internet required after model download                         │
│    RTX 3060 GPU: large v3 at 0.28x RTF (3.6x realtime)              │
│    CPU only (i5): small at 0.19x RTF (5.4x realtime)                │
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

## Performance vs Wispr Flow

> [!WARNING]
> All Rota AI benchmarks below were measured on a Dell G15 laptop: Intel i5 12th gen, 16GB RAM, NVIDIA RTX 3060 6GB GPU. Your results will vary based on your hardware and chosen model.

### Rota AI Benchmarks (RTX 3060 6GB, int8 quantization)

| Metric | Groq Cloud | Gemini Cloud | Local GPU (small, int8) | Local GPU (large v3 turbo, int8) | Local GPU (large v3, int8) |
|---|---|---|---|---|---|
| Transcription latency | ~150ms | ~250ms | ~300ms | ~250ms | ~500ms |
| AI cleanup latency | ~200ms | ~300ms | ~400ms | ~400ms | ~400ms |
| Total end to end | ~350ms | ~550ms | ~700ms | ~650ms | ~900ms |
| Real time factor | N/A (cloud) | N/A (cloud) | 0.068x (15x RT) | 0.050x (20x RT) | 0.279x (3.6x RT) |
| Works offline | No | No | Yes | Yes | Yes |
| Cost | Free tier | Free tier | Free | Free | Free |
| Model size | Cloud | Cloud | 480 MB | ~1.5 GB | ~3.1 GB |
| VRAM usage | N/A | N/A | ~0.9 GB | ~1.5 GB | ~3.0 GB |

### Rota AI Benchmarks (CPU only, i5 int8)

| Metric | Local CPU (base, int8) | Local CPU (small, int8) |
|---|---|---|
| Transcription latency | ~400ms | ~600ms |
| AI cleanup latency | ~500ms | ~500ms |
| Total end to end | ~900ms | ~1.1s |
| Real time factor | 0.042x (24x RT) | 0.068x (15x RT) |

### Comparison with Wispr Flow

| Metric | Wispr Flow (Pro) | Rota AI (Groq) | Rota AI (Local GPU small) | Rota AI (Local GPU large turbo) |
|---|---|---|---|---|
| Price | $15/month | Free | Free | Free |
| Free tier | 2,000 words/week | 2,000 requests/day | Unlimited | Unlimited |
| Works on Windows | Yes | Yes | Yes | Yes |
| Works on Mac | Yes | Not yet | Not yet | Not yet |
| Works on iPhone/Android | Yes | No | No | No |
| Offline mode | No | No | Yes (Ollama) | Yes (Ollama) |
| AI cleanup pass | Yes | Yes | Yes | Yes |
| Auto formatting | Yes | Yes | Yes | Yes |
| Context awareness | Yes | Yes | Yes | Yes |
| Voice snippets | Yes | Yes | Yes | Yes |
| Personal dictionary (syncs across devices) | Yes | Yes (local only) | Yes (local only) | Yes (local only) |
| Encrypted key storage | Unknown | Yes (DPAPI) | Yes (DPAPI) | Yes (DPAPI) |
| Telemetry / analytics sent to cloud | Yes (cloud based) | No | No | No |
| Open source | No | Yes (MIT) | Yes (MIT) | Yes (MIT) |
| Account required | Yes | No | No | No |

Wispr Flow is a polished product with cross device sync, mobile apps, and Mac support. Rota AI on Groq is faster for end to end latency. Rota AI local mode is the only option that works 100% offline with no cloud dependency. Rota AI is the only option where you can read every line of code and verify what it does with your data.

---

## Supported Models

### Transcription Models (Faster Whisper, local mode)

| Model | Parameters | Disk Size | VRAM (int8) | CPU RAM (int8) | RTF on RTX 3060 | RTF on i5 CPU |
|---|---|---|---|---|---|---|
| tiny | 39M | 75 MB | ~400 MB | ~300 MB | 0.037x (27x RT) | ~0.09x (11x RT) |
| base | 74M | 140 MB | ~600 MB | ~500 MB | 0.042x (24x RT) | ~0.12x (8.7x RT) |
| small | 244M | 480 MB | ~900 MB | ~1.5 GB | 0.068x (15x RT) | ~0.19x (5.4x RT) |
| medium | 769M | 1.5 GB | ~1.5 GB | ~2.5 GB | 0.136x (7.4x RT) | ~0.39x (2.6x RT) |
| large v2 | 1550M | 3.1 GB | ~2.9 GB | ~4 GB | 0.211x (4.7x RT) | ~0.50x (2x RT) |
| large v3 | 1550M | 3.1 GB | ~3.0 GB | ~5 GB | 0.279x (3.6x RT) | ~0.64x (1.6x RT) |
| large v3 turbo | 809M | 1.5 GB | ~1.5 GB | ~2.5 GB | 0.050x (20x RT) | ~0.26x (3.9x RT) |

> [!TIP]
> For a Dell G15 with RTX 3060 6GB, **large v3 turbo at int8** is the best balance. RTF of 0.050 means 20x realtime. 1.5GB VRAM usage. Leaves plenty of headroom. For CPU only, **base or small** are the only models that transcribe faster than realtime.

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

### What is the difference between Rota AI and Wispr Flow?

Wispr Flow is a polished commercial product at $15/month after a 14 day trial. It works on Mac, Windows, iPhone, and Android with cross device sync.

Rota AI is free and open source. Currently Windows only. Everything is local by design, no account needed. What Rota AI has that Wispr Flow does not: fully local offline mode, encrypted API key storage via Windows DPAPI, zero telemetry, no account required, and you can audit every single line of code.

### Can I use Rota AI without an internet connection?

Yes. Install Ollama, download a Whisper model, and Rota AI works 100% offline. No API keys, no accounts, no internet. Your voice data never leaves your computer. This is something Wispr Flow cannot do.

### Where are my API keys stored?

Encrypted with Windows DPAPI using pywin32. The encryption is tied to your Windows user account. Even if someone copies your config file, they cannot decrypt your keys without your Windows login. Rota AI has no servers. Your keys are only sent to the API provider you chose (Groq or Gemini) during transcription requests.

### Does it work in any app?

If the app has a text field and accepts keyboard input, Rota AI works in it. VS Code, Cursor, Slack, Discord, Notion, Obsidian, Gmail, Outlook, Word, Excel, your browser, your terminal, Steam chat, everything. The text injection layer uses multiple methods (SendInput, clipboard paste, UI Automation) to handle even stubborn applications.

### How accurate is the transcription?

Whisper base gives roughly 92-95% word accuracy on clear English speech. Small gives 94-97%. Large v3 turbo gives 96-98%. The AI cleanup pass fixes many remaining errors, especially filler words and self corrections. For technical terms, add them to your personal dictionary and Rota learns them over time.

### What languages are supported?

Whisper supports 99+ languages for transcription. The AI cleanup pass currently works best in English. Transcription in other languages works great. AI cleanup for other languages is on the roadmap.

### Does it work on Mac or Linux?

Not yet. Windows 10 and 11 only for now. macOS and Linux are planned. The core pipeline is platform agnostic but the text injection and context detection layers use Windows specific APIs (SendInput, UI Automation, DPAPI) that need platform specific implementations.

### How much disk space do I need?

The Rota AI application itself is about 25 MB. Dependencies (PyQt6, torch, etc.) are about 500 MB. Then the model you choose:
- Whisper base: 140 MB
- Whisper small: 480 MB
- Whisper large v3 turbo: 1.5 GB
- Whisper large v3: 3.1 GB
- Silero VAD: 2 MB
- AI cleanup model (Ollama): 1-5 GB depending on what you pick

### What are the minimum system requirements?

- Windows 10 or 11
- Python 3.10+
- 4 GB RAM minimum (8 GB recommended)
- Microphone (built in or external)
- For local transcription: 8 GB RAM for base/small, 16 GB for medium/large
- For GPU transcription: NVIDIA GPU with 4+ GB VRAM (GTX 1650 or better)
- For CPU only transcription: any modern quad core processor

### Can I use my own fine tuned Whisper model?

Yes. Rota AI supports loading custom model paths. Point it to your fine tuned model in settings and it will use it for transcription.

### What Python version do I need?

Python 3.10 or newer. `run.bat` auto detects your Python installation. If you have multiple versions, it picks the newest one.

### I found a bug. Where do I report it?

Open an issue on GitHub. I read every single issue and try to respond quickly. Include your Windows version, Python version, chosen backend, and steps to reproduce.

---

## Known Issues

> [!WARNING]
> **Windows only**: Rota AI currently only supports Windows 10 and 11. macOS and Linux versions are planned. The README will be updated when they are available.

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
