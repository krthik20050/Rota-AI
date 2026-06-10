---
title: Voice Commands
---

Rota AI features an advanced **Voice Command Engine**. By speaking specific key-phrases, you can instruct the post-transcription LLM pass to execute text modifications, formatting tasks, or translations.

### Invocation Pattern
To run a command, speak the trigger phrase naturally at the end of your recording, or record a command immediately after a prior dictation.

### Standard Command Registry

| Command Trigger | Description | Example Spoken Input | Output Result |
|-----------------|-------------|----------------------|---------------|
| `"scratch that"` | Deletes the last transcribed sentence. | *"We should meet up tomorrow scratch that"* | *"We should meet up"* |
| `"make it formal"` | Rewrites the transcribed text in a professional, formal tone. | *"Hey can you send me that sheet make it formal"* | *"Could you please forward the spreadsheet to me?"* |
| `"make it casual"` | Rewrites in a relaxed, friendly tone. | *"I am unable to attend make it casual"* | *"Can't make it, sorry!"* |
| `"translate to [language]"` | Translates the dictated text. | *"Hello where is the library translate to Spanish"* | *"Hola, ¿dónde está la biblioteca?"* |
| `"bullet points"` | Converts the transcribed text into a markdown list. | *"Buy milk buy eggs clean car bullet points"* | `* Buy milk\n* Buy eggs\n* Clean car` |

### Custom Editing Commands
Because the backend uses an LLM (Gemini or Llama), you are not limited to fixed commands. You can command Rota AI to perform freeform text updates by starting your command with action verbs:

- *"Change the deadline to Friday"*
- *"Wrap this in a python try except block"*
- *"Correct my spelling but keep it short"*
- *"Make this sound like an email subject line"*
