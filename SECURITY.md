# Security Policy

## Reporting Security Issues
If you find a security vulnerability, please open a GitHub Issue with the `security` label.

## Data Privacy

**What leaves your machine:**
- Audio chunks → Groq Whisper API (if Groq key is set)
- Cleaned text → Gemini API (if Gemini key is set)
- If no cloud keys: everything runs locally via faster-whisper. Nothing leaves your machine.

**What stays local:**
- Transcription history: `%APPDATA%/RotaAI/history.db` (SQLite, plaintext)
- API keys: `%APPDATA%/RotaAI/config.json` — **encrypted at rest via Windows DPAPI** (AES-256, current user account only)
- Personal dictionary: `%APPDATA%/RotaAI/personal_dictionary.json`
- No Rota AI server exists. Zero telemetry.

## Security Controls (implemented)

| Control | Status |
|---------|--------|
| API keys encrypted at rest (Windows DPAPI) | ✅ |
| Gemini key in HTTP header, not URL | ✅ |
| Ollama URL restricted to localhost/private networks | ✅ |
| Rate limiting on Gemini (30/min) and Groq (20/min) | ✅ |
| Injection blocked in terminal windows | ✅ |
| Prompt injection pattern detection | ✅ |
| Max transcript length (10,000 chars) | ✅ |
| Max injection length (5,000 chars) | ✅ |
| Single-instance mutex + loopback socket (127.0.0.1 only) | ✅ |
| Windows registry startup path validation | ✅ |
| LIKE injection sanitized in history search | ✅ |
| Error bodies redact 30+ char token strings | ✅ |

## Known Remaining Limitations

- **History DB plaintext** — `history.db` contains all transcribed text in plaintext SQLite. Any process running as your Windows user can read it. SQLite encryption (SQLCipher) is a future improvement.
- **Clipboard window** — During text injection, the clipboard briefly holds the injected text (~150 ms). This is unavoidable with the Ctrl+V paste method.
- **Injection scope** — Rota injects into the foreground window. Terminals are blocked, but any other app is a valid target by design.
- **Global hotkey** — Requires OS-level keyboard access.

## Bring Your Own Keys
Rota AI does not include any API keys. You must provide your own:
- Gemini key: https://aistudio.google.com/app/apikey
- Groq key: https://console.groq.com/keys
- Or use Ollama for fully local, offline processing
