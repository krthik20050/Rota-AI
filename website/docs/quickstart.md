---
title: Quickstart
---

Start dictating with Rota AI in less than 2 minutes by following this step-by-step setup guide.

### Step 1: Initial Launch
When you open Rota AI for the first time, you will be greeted by the **Onboarding Wizard**. This wizard configures the application essentials:
1. **Choose a Backend**: Select your starting transcription processor.
   - **Groq** is the fastest and highly recommended if you have an active internet connection.
   - **Ollama** runs entirely local but requires downloading models.
2. **Setup your API Key**: If using Groq or Gemini, copy-paste your free API Key.
3. **Select Microphone**: Choose your input audio source. Click **Test Mic** to speak and see the audio levels peak.
4. **Choose Hotkey**: By default, the recording key is bound to `F9`.

### Step 2: The Core Workflow
Now that Rota AI is running, it will sit silently in your OS system tray (bottom-right on Windows/Linux, top-bar on macOS).

1. **Focus a Text Area**: Click inside any application where you want to write text (e.g., Slack, Notepad, VS Code, or an email).
2. **Press F9**:
   - A modern, glowing visual indicator (recording pill) will appear on screen.
   - The application will immediately begin capturing audio from your microphone.
3. **Speak Naturally**: Say what you want written. You do not need to pause or pronounce robotically. You can say punctuation explicitly (e.g., *"Let's plan for Monday comma and write the code period"*).
4. **Press F9 Again**:
   - The recording will stop.
   - Rota AI processes the speech in the background, applies your LLM cleanup settings, and types the output directly at your cursor location.

### Tips for Perfect Dictation
* **Punctuation Commands**: Say *"new line"* to start a new line, or *"new paragraph"* to create a double-space separation.
* **Volume**: Keep a natural speaking volume. You don't need to speak directly into the microphone capsule.
* **Canceling**: If you make a mistake and want to abort the current recording without typing it, hit the `Escape` key on your keyboard while recording is active.
