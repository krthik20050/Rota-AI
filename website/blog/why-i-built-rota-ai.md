---
title: "Why I Built Rota AI"
date: "2026-05-25"
description: "I was a student who tried Wispr Flow, loved it, couldn't afford it, and decided to build a free open source alternative. This is that story."
tags: ["open source", "voice dictation", "story"]
---

## The 14-Day Free Trial That Started Everything

I am a student. When I first tried Wispr Flow, I was honestly amazed.

The way it just understood what I was saying, cleaned it up, and dropped it into whatever app I was using. It felt like the future. Typing felt slow by comparison. My fingers felt inefficient. After a week of using it, going back to a keyboard felt like a downgrade.

Then my 14-day free trial ended.

I could not go back to typing. My fingers felt slow. Everything felt slow.

So I started thinking. Why can't I build something like this myself? How hard could it be?

It turned out to be very hard.

## What I Had to Learn

I spent months learning how voice dictation actually works under the hood. Things I never expected to need to know as a student:

- How speech recognition models process audio at the signal level
- How Voice Activity Detection strips silence before transcription
- How to inject text into any application on Windows without breaking anything
- How Windows UI Automation works and why it exists
- How to build a pipeline where every stage runs on its own thread so the UI never freezes
- How to encrypt API keys with Windows DPAPI so they cannot be stolen even if someone copies your config file

I reverse engineered how Wispr Flow processes audio, how it does AI cleanup, how it detects what app you are in, how it injects text. I read source code. I read research papers. I built things, broke them, rebuilt them.

This project taught me more about real software engineering than any course ever did.

## What Rota AI Does

Rota AI sits on your desktop. You hold a hotkey. You speak. Rota records your voice, transcribes it using Whisper, runs an AI cleanup pass to remove filler words and fix grammar, then types the result into whatever app your cursor is in.

No switching apps. No copy pasting. No subscription. No account. No internet required if you go fully local with Ollama.

It works in VS Code, Slack, Notion, Gmail, Word, Discord, your browser, your terminal. Any app with a text field.

The stack: Python, PyQt6, Faster Whisper, Silero VAD, Groq, Gemini, SQLite. The UI is pure black, custom styled, floating pill overlay with an audio-reactive waveform. Every pixel is intentional.

## The Technical Architecture

The pipeline has 7 stages, each on its own thread:

**Stage 1 - Audio capture**: 16kHz mono PCM via PortAudio. Real-time RMS for waveform visualization.

**Stage 2 - Voice activity detection**: Silero VAD v6 strips leading and trailing silence before anything goes to the transcription engine. 2MB model, under 1ms per chunk. This saves API credits and improves accuracy.

**Stage 3 - Transcription**: Your choice of Groq Whisper (cloud, free tier), Gemini (cloud, free tier), or local Faster Whisper via Ollama (no internet ever needed).

**Stage 4 - AI cleanup**: A second LLM pass removes filler words, resolves self-corrections, formats lists, adjusts tone. Skipped entirely for phrases under 5 words to keep latency low.

**Stage 5 - Context detection**: Reads the active window title and process name. Classifies context: code editor, email, chat, notes. Adapts output accordingly. VS Code gets camelCase preserved. Slack gets casual tone. Outlook gets formal.

**Stage 6 - Text injection**: Multiple methods. SendInput API for short text. Clipboard + Ctrl+V for longer passages. Fallback to pyautogui for stubborn apps.

**Stage 7 - Persistence**: SQLite for session history, snippets, personal dictionary, analytics. DPAPI-encrypted config for API keys.

## Why Free and Open Source

Wispr Flow costs $15 per month. SuperWhisper costs $8.49 per month. Both are great products. But not everyone can afford a subscription for a tool like this.

I am a student. Many people who would benefit from voice dictation are students, writers, developers, people with accessibility needs. People for whom $15 per month is not a small amount.

Rota AI is MIT licensed. Free. No account. No credit card. No subscription. Bring your own API keys (Groq and Gemini both have free tiers that handle daily use), or go fully local with Ollama.

The code is all on GitHub. Every line. You can audit exactly what it does with your voice data. The answer is nothing. It goes to the transcription service you chose and nowhere else.

## What is Next

The Windows version is solid. Linux support via AppImage is in testing. macOS is planned.

There is more to build: screen context reading (like SuperWhisper's Super Mode), file transcription, cross-device sync, mobile. But the core product works well right now and I am proud of it.

If you are a student and this inspires you to build something, do it. You do not need a big team. You do not need funding. You need curiosity and the stubbornness to keep going when things break, which they will, constantly.

---

**Rota AI is free and open source.** [GitHub](https://github.com/krthik20050/Rota-AI) - star it if it is useful to you. It helps others find it.
