---
title: Voice Snippets
---

Voice snippets allow you to bind long, complex blocks of text to a spoken trigger word. During the post-transcription cleaning pass, Rota AI will look for these trigger words and immediately replace them with the expanded text.

### How to Create a Snippet

1. Open Rota AI **Settings** and navigate to the **Snippets** tab.
2. Click **Add Snippet**.
3. Fill in the fields:
   - **Trigger Phrase**: The word or short phrase you will speak (e.g., `"my signature"`). Keep triggers distinct and easy for Whisper to hear.
   - **Expansion Text**: The raw text that should be pasted (supports newlines and formatting).
4. Click **Save**.

### Examples of Useful Snippets

| Spoken Trigger | Expanded Output |
|----------------|-----------------|
| `"insert code header"` | `#!/usr/bin/env python3\n# -*- coding: utf-8 -*-` |
| `"my address"` | `Flat 4B, Emerald Heights, Bangalore, 560001` |
| `"insert react component"` | `import React from 'react';\n\nexport default function Component() {\n  return <div>Component</div>;\n}` |

### Configuration Rules
* **Trigger Prefixes**: By default, Rota AI watches for trigger words preceded by a command prefix like `"insert"` or `"paste"` (e.g., saying *"insert email"* instead of just *"email"*). This prevents accidental expansions during normal dictation. You can customize or disable this prefix in the Settings menu.
* **Storage**: Snippets are stored locally inside the application's SQLite database (`snippets` table) and are loaded into memory on startup for zero-latency lookup.
