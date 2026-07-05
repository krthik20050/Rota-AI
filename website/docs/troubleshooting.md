---
title: Troubleshooting
---

This guide helps you diagnose and resolve common issues encountered while running Rota AI.

---

### Issue 1: Nothing happens when I press F9

#### Windows Diagnostics
1. Check your system tray. Verify that the Rota AI icon is visible (or check your Task Manager to make sure `app/main.py` or `RotaAI.exe` is active).
2. Verify that your microphone is set as the active device and is not hardware-muted.
3. Check permissions under *Settings > Privacy & security > Microphone* and ensure desktop apps are allowed.
4. Try running Rota AI as **Administrator** (UAC blocks input events in elevated applications).

#### macOS Diagnostics
1. Open *System Settings > Privacy & Security > Accessibility*.
2. Turn RotaAI off and back on.
3. Verify the same settings under *Privacy & Security > Microphone*.

---

### Issue 2: Text is scrambled or typed out-of-order
If you notice that output text is missing letters, capitalization is random, or sentences are mixed up:
1. Open **Settings > Injection**.
2. Increase the **Injection Delay** from `0ms` to `10ms` or `20ms`. (Some slow-rendering applications or remote desktops cannot keep up with rapid simulated hardware keyboard entries).
3. If letters are still missing, toggle the **Injection Method** strictly to **Clipboard Paste**.

---

### Issue 3: Local transcription is extremely slow (using Ollama)
If a 5-second voice recording takes more than 10 seconds to transcribe:
* **Check GPU Acceleration**: Ensure Ollama is running using your dedicated GPU (NVIDIA CUDA or Apple Silicon Unified Memory) rather than falling back to CPU cores.
* **Decrease Model Size**: If you pulled `whisper-large` on a low-spec laptop, it will lag. Run `ollama pull whisper-small` and switch your model setting to `whisper-small` for a 4x latency improvement.
