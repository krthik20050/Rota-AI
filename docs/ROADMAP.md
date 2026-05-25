# Roadmap

## Current Status

Rota AI is functional on Windows and Linux. Core pipeline works: record, transcribe, clean up, inject. Cloud backends (Groq, Gemini) and local backend (Ollama) both supported.

## Short Term (Next 1-3 Months)

### Features
- [ ] macOS port (need a Mac developer or CI with macOS runner)
- [ ] Audio file transcription (drag and drop audio files)
- [ ] Custom AI cleanup prompts (user-defined prompts)
- [ ] Multi-language UI (the app itself, not just transcription)
- [ ] Plugin system for custom text processors

### Quality
- [ ] Reduce transcription latency (currently 1-3 seconds)
- [ ] Better handling of accented English
- [ ] Improved VAD for noisy environments
- [ ] More injection methods for stubborn apps

### Documentation
- [ ] Video tutorials (YouTube)
- [ ] API documentation for plugin system
- [ ] Translation guide for contributors

## Medium Term (3-6 Months)

### Features
- [ ] Mobile companion app (Android first)
- [ ] Cross-device sync (optional, encrypted)
- [ ] Team/enterprise features (admin panel, usage analytics)
- [ ] Voice commands (not just dictation, but "open VS Code", "send message")
- [ ] Integration with more editors (JetBrains, Neovim)

### Platform
- [ ] Flatpak distribution for Linux
- [ ] Snap package
- [ ] Windows Store distribution
- [ ] Homebrew for macOS (when ported)

## Long Term (6-12 Months)

### Vision
- [ ] Real-time streaming transcription (word-by-word as you speak)
- [ ] On-device small model (no Ollama needed, built-in)
- [ ] Voice profiles (learn your voice, vocabulary, style over time)
- [ ] Collaborative features (shared snippets, team dictionaries)
- [ ] Accessibility features (voice control of the OS, not just text input)

### Ecosystem
- [ ] Plugin marketplace
- [ ] Third-party integrations (Zapier, IFTTT, etc.)
- [ ] Enterprise support tier (optional, paid, for sustainability)

## How to Influence the Roadmap

1. Open a GitHub Issue with the `enhancement` label
2. Describe the use case, not just the feature
3. Explain who would benefit and how often
4. If you can build it, say so. PRs are always welcome.

## Completed

See [FIXES.md](../FIXES.md) for a detailed log of completed work.
