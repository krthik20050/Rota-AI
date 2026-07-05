---
title: Offline Mode
---

Rota AI can be configured to run completely offline with zero telemetry and zero network calls, guaranteeing absolute data privacy.

---

### Step-by-Step Offline Setup

#### 1. Install Ollama
Download and run the installer for your platform from [ollama.com](https://ollama.com).

#### 2. Download Whisper Models
Open a terminal (Command Prompt, PowerShell, or bash) and pull the Whisper model sizes you wish to use:
```bash
# Pull Whisper Small (480MB weights - fast, balanced accuracy)
ollama pull whisper-small

# Pull Whisper Large (3.1GB weights - highly accurate, requires GPU)
ollama pull whisper-large
```

#### 3. Download LLM Clean-up Models (Optional)
If you want local AI cleanup, download a lightweight LLM such as Llama 3.2 1B or 3B:
```bash
ollama pull llama3.2:3b
```

#### 4. Configure Rota AI Settings
1. Open Rota AI **Settings > Transcription**.
2. Set the **Backend** dropdown to `Ollama`.
3. Set the **Model** to matching name, e.g., `whisper-small`.
4. (Optional) Go to **Settings > AI Cleanup**, select `Ollama` as the cleanup processor, and input the model name `llama3.2:3b`.
5. Save changes.

---

### Offline vs Cloud Performance

| Feature | Cloud (Groq/Gemini) | Local (Ollama) |
|---------|--------------------|----------------|
| **Data Privacy** | Subject to API privacy policies | 100% Private (No data leaves RAM/Disk) |
| **Transcription Latency** | ~300ms - 800ms | ~1.5s - 6.0s (Hardware dependent) |
| **GPU Requirement** | None (Runs on any machine) | Highly recommended (NVIDIA/Apple Unified Memory) |
| **Offline Support** | No (Fails without internet) | Yes (Fully functional air-gapped) |
