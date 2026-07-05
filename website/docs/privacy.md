---
title: Privacy & Security
---

Privacy is not an add-on; it is the core architectural principle of Rota AI. The desktop application is designed to give you complete ownership over your speech data.

---

### Key Privacy Pillars

#### 1. Zero Telemetry & Analytics
* Rota AI has **no** embedded tracking codes, analytics scripts, crash-reporting aggregators (like Sentry or Bugsnag), or analytics packages.
* The application never reports back on your usage counts, words typed, or average session times.

#### 2. Local SQLite DB Storage
* Your dictation history is stored entirely in a local SQLite file (`rota.db`).
* History stays on your hard drive. Rota AI provides no cloud synchronizations, which protects you from database leaks or server-side intrusions. You can purge your history database anytime inside the settings page.

#### 3. Encrypted Credentials
* All cloud API tokens (Groq or Gemini keys) are encrypted locally using hardware keys tied to your specific user profile (DPAPI on Windows, macOS Keychain, or Linux Secret Service via D-Bus).
* Unauthorized local apps or scripts cannot access or decrypt your credentials.

#### 4. Absolute Data Routing Control
* You choose where your voice data goes:
  - If you configure **Groq** or **Gemini**, audio files are sent over encrypted HTTPS to their APIs. You can view their developer data policies (both guarantee developer payload data is not used for model training).
  - If you configure **Ollama**, audio files are sent only to the local network port `127.0.0.1`. No voice or text data ever leaves your computer.
