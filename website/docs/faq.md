---
title: Frequently Asked Questions
---

Here are answers to the most common questions regarding Rota AI.

---

### Is Rota AI really free?
Yes. Rota AI is fully open-source under the permissive **MIT License**. There are no premium features, no subscription paywalls, and no hidden charges.

---

### Do I need a credit card or cloud account to get started?
No. You do not need any credit card or Rota account. If you choose a cloud backend like Groq or Gemini, you will need to sign up for their developer console platforms to generate a free API key.

---

### Can I dictate in languages other than English?
Yes. Rota AI supports multi-language transcription:
* Under **Groq** and **Gemini**, Whisper supports over 99 languages (including Spanish, French, German, Mandarin, Portuguese, Hindi, etc.).
* Under **Ollama**, make sure you pull a multi-language model version (like `whisper-small` or `whisper-large`).

---

### Does Rota AI run inside fullscreen games or software?
It depends on how the software renders:
* In borderless windowed or windowed applications, the floating recording overlay pill displays correctly.
* In exclusive fullscreen mode (like some 3D video games), the OS graphics layer blocks external application overlays from drawing on top. Dictation will still capture audio and inject text, but you won't see the visual recording indicator.
