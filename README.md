# Rota AI — Local Voice Dictation

**Free, open-source, local-first voice dictation for Windows.**
A privacy-respecting alternative to Wispr Flow.

## ⚠️ Privacy & Security

**Rota AI does not have a server.** Everything runs on your machine.

### What stays local
- All transcription history → `%APPDATA%/RotaAI/history.db` (SQLite, plaintext)
- API keys → `%APPDATA%/RotaAI/config.json` (encrypted with Windows DPAPI)
- Personal dictionary → `%APPDATA%/RotaAI/personal_dictionary.json`
- Snippets → `%APPDATA%/RotaAI/snippets.json`

### What leaves your machine (only if you configure it)
- **Voice audio** → sent to your configured AI provider (Gemini/Groq) for transcription
- **Transcripts** → sent to your configured AI provider for text cleanup
- **Personal vocabulary** → sent to AI provider as context for better recognition

### Important notes
- **History is stored in plaintext SQLite** — anyone with file access can read it
- **No encryption at rest** for history.db (documented limitation)
- **API keys are encrypted** at rest using Windows DPAPI
- **No telemetry, no analytics, no phone-home**

## Quick Start

1. Clone this repo
2. Copy `.env.example` to `.env` and add your API keys:
   ```
   GEMINI_API_KEY=AIzaSy...
   GROQ_API_KEY=gsk_...
   ```
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python main.py`

## Getting API Keys

- **Gemini** (free tier): https://aistudio.google.com/app/apikey
- **Groq** (free tier): https://console.groq.com/keys
- **Ollama** (fully local, no key needed): https://ollama.com

## Security

See [SECURITY.md](SECURITY.md) for full security policy and known limitations.
