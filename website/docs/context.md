---
title: Context Awareness
---

Rota AI features intelligent **Context Awareness**. The application constantly tracks which desktop window has active keyboard focus and passes this context metadata (e.g., application class, executable name, window title) to the LLM cleanup layer.

The LLM adapts its formatting instructions to match the target environment.

---

### App-Specific Formatting Rules

#### 1. Software Development (VS Code, Cursor, Terminal, JetBrains)
When a code editor or terminal is in focus, the cleanup pass prioritizes programming formatting:
* Preserves programming casing: `camelCase`, `snake_case`, `kebab-case`.
* Formats code keywords correctly (e.g., typing `try except`, `async await`, `import statements`).
* Prevents auto-capitalization at the start of lines to avoid syntax errors.
* Keeps technical commands like `git checkout -b main` in raw monospace formatting.

#### 2. Chat and Messaging (Slack, Discord, Teams, Telegram)
When a chat application is in focus:
* Keeps formatting relaxed and conversational.
* Uses appropriate contractions (`don't`, `can't`, `it's`).
* Employs inline markdown for emphasis (`*italic*`, `**bold**`).
* Strips formal email greetings and signatures.

#### 3. Professional Writing (Word, Outlook, Notion, Gmail)
When a word processor or email client is in focus:
* Automatically adds formal greetings or closings if dictated.
* Uses formal punctuation, capitalization, and complete sentences.
* Expands common abbreviations.

---

### Privacy & Security Note
Window detection is performed entirely **locally** on your device. The active window detection code queries standard OS-level accessibility APIs:
- **Windows**: `GetForegroundWindow` and UI Automation APIs.
- **macOS**: `NSWorkspace.shared.frontmostApplication` and `AXUIElement` APIs.
- **Linux**: AT-SPI / `xdotool` window querying APIs.

*Only the name of the application and the title of the window are sent to your configured transcription/LLM backend during the cleaning call.*
