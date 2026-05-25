# Security Policy

## Reporting Security Issues

If you find a security vulnerability, please open a GitHub Issue with the `security` label.

## Data Privacy

**What leaves your machine:**
- Audio chunks → Groq Whisper API (if Groq key is set)
- Cleaned text → Gemini API (if Gemini key is set)
- If no cloud keys: everything runs locally via faster-whisper. Nothing leaves your machine.

**What stays local:**

| Data | Windows Path | Linux Path | macOS Path |
|------|-------------|-----------|------------|
| Config | `%APPDATA%\RotaAI\config.json` | `~/.config/rota-ai/config.json` | `~/Library/Application Support/RotaAI/config.json` |
| History | `%APPDATA%\RotaAI\history.db` | `~/.local/share/rota-ai/history.db` | `~/Library/Application Support/RotaAI/history.db` |
| Dictionary | `%APPDATA%\RotaAI\personal_dictionary.json` | `~/.local/share/rota-ai/personal_dictionary.json` | `~/Library/Application Support/RotaAI/personal_dictionary.json` |
| Sessions | `%APPDATA%\RotaAI\sessions.db` | `~/.local/share/rota-ai/sessions.db` | `~/Library/Application Support/RotaAI/sessions.db` |

**API key encryption at rest:**
- **Windows:** DPAPI (win32crypt, AES-256, current user account only)
- **Linux:** keyring (Freedesktop Secret Service / GNOME Keyring)
- **macOS:** keyring (macOS Keychain)

No Rota AI server exists. Zero telemetry.

## Security Controls (implemented)

| Control | Status |
|---------|--------|
| API keys encrypted at rest | ✅ (Windows DPAPI / Linux keyring / macOS Keychain) |
| Gemini key in HTTP header, not URL | ✅ |
| Ollama URL restricted to localhost/private networks | ✅ |
| Rate limiting on Gemini (30/min) and Groq (20/min) | ✅ |
| Injection blocked in terminal windows | ✅ |
| Prompt injection pattern detection | ✅ |
| Max transcript length (10,000 chars) | ✅ |
| Max injection length (5,000 chars) | ✅ |
| Single-instance mutex + loopback socket (127.0.0.1 only) | ✅ |
| Startup path validation | ✅ |
| LIKE injection sanitized in history search | ✅ |
| Error bodies redact 30+ char token strings | ✅ |
| Platform abstraction (no Windows imports on Linux) | ✅ |

## Known Remaining Limitations

- **History DB plaintext** — `history.db` contains all transcribed text in plaintext SQLite. Any process running as your user can read it. SQLite encryption (SQLCipher) is a future improvement.
- **Clipboard window** — During text injection, the clipboard briefly holds the injected text (~150 ms). This is unavoidable with the Ctrl+V paste method.
- **Injection scope** — Rota injects into the foreground window. Terminals are blocked, but any other app is a valid target by design.
- **Global hotkey** — Requires OS-level keyboard access (evdev on Linux, pynput on Windows, pynput + Quartz on macOS).

## Bring Your Own Keys

Rota AI does not include any API keys. You must provide your own:
- Gemini key: https://aistudio.google.com/app/apikey
- Groq key: https://console.groq.com/keys
- Or use Ollama for fully local, offline processing
