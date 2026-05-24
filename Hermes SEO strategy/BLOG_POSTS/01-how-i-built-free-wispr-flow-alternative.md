---
title: "1. How I Built a Free Wispr Flow Alternative as a Student"
meta_title: "How I Built a Free Wispr Flow Alternative as a Student"
meta_description: "I tried Wispr Flow, loved it, ran out of free credits, and built my own. Here is the story of how Rota AI happened."
target_keyword: "wispr flow alternative"
---

# 1. How I Built a Free Wispr Flow Alternative as a Student

TL;DR: I am Karthik Krishnan, a student in Kerala. I tried Wispr Flow, loved it, could not afford $15/month, switched accounts to keep the free trial going, ran out of emails, and built my own voice dictation app. It is called Rota AI. It is free and open source.

I am not a professional developer. I study at Vidya Academy of Science and Technology. I got frustrated and decided to build something.

Here is how it happened.

## How I Found Wispr Flow

I saw Wispr Flow on YouTube nd Instagram. People were speaking into their computers nd clean text was showing up in their apps. No typing. No filler words. Just talking nd the words appeared.

I was skeptical. I thought it would be one of those things that sounds good in a video but does not actually work.

I tried it anyway.

The first time I used it, I just sat there staring at my screen. I said "hey how are you doing today" nd it typed exactly that. Clean. No "um." No "uh." Just the words I meant to say.

I used it for a whole day. Writing emails. Taking notes. Messaging friends. My fingers did not hurt at the end of the day for once.

Then the 14-day trial ended.

## The Wall

Wispr Flow costs $15 per month. The free tier gives you 2,000 words per week.

I am a student. I do not have $15 per month for a dictation tool. nd 2,000 words per week is nothing. A few emails nd you are done.

So I did what any desperate person would do. I started switching accounts. New email, new trial, another 14 days.

That worked for a while. But eventually I ran out of emails to use. nd the 2,000-word limit on the free tier was always there, waiting.

I remember sitting at my laptop at 2 AM, waiting for the cloud API limit to reset so I could keep working on my assignments. Those were wasted days. I could have been building something. Instead I was just waiting.

That is when I thought: why do not I just build my own?

## Building the First Draft

I had never built anything like this before. I did not know how voice dictation worked. I did not know what a VAD was. I did not know how to send text to other applications.

But I had Claude Code. nd Cursor. nd a lot of free time.

My first draft was terrible. Like, genuinely bad. It would record audio nd then just dump raw text with all the filler words nd mistakes. It could not tell the difference between silence nd speech. It sent text to the wrong application half the time.

I almost quit. Multiple times.

But I kept going. Feature by feature. First I got the audio recording working. Then I added voice activity detection so it would strip out silence. Then I got Whisper to transcribe the audio. Then I figured out how to clean up the text with an AI model. Then I spent two weeks just on text injection, trying to get the text to appear in the right place in different apps.

The text injection part was the hardest. Every app handles input differently. Some use standard Windows text boxes. Some use custom controls. Some are web-based. I ended up using three different methods: Windows SendInput API, clipboard paste, nd pyautogui as a fallback.

## What I Learned in College That Actually Mattered

Here is something funny. People always say engineering is useless. That you never use what you learn in class.

But in my operating systems course this semester, we learned about round robin scheduling. How the CPU gives each process a time slice nd cycles through them.

I used that. My cloud API has rate limits. Instead of sending all requests at once nd hitting the wall, I implemented a round robin approach. Cycle through different API keys, give each one a time slice, stay within limits.

I never thought I would actually use round robin in real life. But here we are.

## What Rota AI Can Do Now

After months of work, Rota AI does the thing I wanted Wispr Flow to do for free:

- Hold F9, speak, get clean text in any app
- AI transcription via Groq, Gemini, or local Ollama
- AI cleanup that removes filler words nd formats your speech
- Context awareness (knows if you are in VS Code vs Outlook vs Slack)
- Voice snippets for things you type a lot
- Works completely offline with Ollama
- Zero telemetry, no account, no cloud lock

It is not as polished as Wispr Flow. I want to be honest about that. It does not have Mac support. No mobile app. The UI is functional but not beautiful.

But it is free. nd it is mine. nd I built it.

## Why Open Source

I am putting Rota AI on GitHub for free. MIT license. Anyone can use it, modify it, build on it.

Because I think if you can build something, you should not put a payment wall in front of it. There are students like me who just want to use the tool. They should not have to switch accounts nd wait for limits to reset.

If you are someone who hit a payment wall on something you wanted to use, I get you. That is why this exists.

## What I Want to Say to Cloud Providers

One more thing. If you are a cloud API provider reading this: please let users carry forward their unused quota. If I pay for 2,000 requests per day nd I only use 500, let me use the other 1,500 the next day. I am paying for them. Do not just throw them away.

That would help people like me who are building things on a budget.

## Try It

If you are a student, or someone who just wants free voice dictation on Windows, give Rota AI a try.

https://github.com/krthik20050/Rota-AI

It is not perfect. But it works. nd it costs nothing.

---

*Built by Karthik Krishnan, a student at Vidya Academy of Science and Technology, Kerala. Still learning. Still building.*
