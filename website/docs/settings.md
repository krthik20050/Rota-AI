---
title: Settings Reference
---

This section documents all configuration options available in the Rota AI configuration database. These settings are persisted locally in `config.json`.

---

### Audio Settings
Configure the parameters for sound capture and silent space stripping.

* **Input Device**: The active system microphone. Choosing "Default System Device" dynamically tracks OS settings.
* **Sample Rate**: Locked to `16000 Hz` (Whisper models are trained strictly on 16kHz mono audio).
* **VAD Sensitivity**: The sensitivity threshold for the Silero Voice Activity Detector.
  - Range: `0.1` (very sensitive) to `0.9` (ignores quiet talking). Default is `0.5`.
* **VAD Padding (ms)**: The duration of padding silence to keep before and after a speech chunk is detected. Keeps speech boundaries from clipping. Default is `300ms`.

---

### Transcription & Models
Configure the speech-to-text engines.

* **Backend**: Choice between `Groq`, `Gemini`, or `Ollama`.
* **Model Size**:
  - Cloud: Defaults to `whisper-large-v3-turbo`.
  - Local (Ollama): Choice between `whisper-base`, `whisper-small`, or `whisper-large`.
* **Primary Language**: Explicitly set the language ISO code (e.g., `en`, `es`, `fr`, `de`) to skip the ASR language detection phase, shaving ~200ms off transcription latency.

---

### Injection & Paste Options
Controls how processed text is returned to the operating system.

* **Injection Method**:
  - `Direct Input`: Simulates hardware keyboard presses. Safe for all apps but slow for large texts.
  - `Clipboard Paste`: Copies the text to the clipboard and sends a virtual `Ctrl+V` (or `Cmd+V`) hotkey. Virtually instant.
  - `Auto`: Uses Direct Input for less than 200 characters and Clipboard Paste for larger inputs.
* **Injection Delay (ms)**: Pause interval between key events. If letters appear scrambled or skipped in laggy applications (like remote desktops), increase this to `10ms`.
