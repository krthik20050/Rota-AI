---
title: Basic Dictation
---

The core workflow of Rota AI is designed to replace keyboard typing with fast, hands-free voice dictation without breaking your active focus.

### Operation Modes

You can trigger dictation using two interaction patterns on your configured hotkey (default: `F9`):

1. **Press-and-Hold (Default)**:
   - Press and hold `F9`. Keep it held down while speaking.
   - Release the key as soon as you finish talking.
   - Recording stops immediately, and text is processed and pasted.
2. **Tap-to-Toggle**:
   - Tap `F9` once to start recording. The pill overlay appears.
   - Speak your text.
   - Tap `F9` again to stop recording.

### Recording States and UI Indicators
When recording, Rota AI displays a floating, semi-transparent overlay pill on screen. The pill changes colors to indicate the audio capture state:

- 🟩 **Green / Pulse**: Actively listening and capturing microphone inputs.
- 🟨 **Yellow**: Silero VAD has detected silence, indicating you have paused speaking.
- 🟦 **Blue**: Uploading audio buffer to transcription engine.
- ⚙️ **Spinning Wheel**: Running the post-transcription LLM cleanup pass.

### Punctuation Control
ASR models are highly proficient at auto-punctuating sentences. However, for precise formatting, speak the punctuation commands out loud:

* Say *"period"*, *"comma"*, or *"question mark"* for standard punctuation.
* Say *"new line"* or *"line break"* to insert `\n`.
* Say *"new paragraph"* to insert `\n\n`.
* Say *"open quote"* and *"close quote"* for quotation marks.
