---
title: "How to Set Up a Free Groq API Key for Voice Dictation"
slug: set-up-groq-api-free
date: 2026-05-24
tags: [groq, api-key, voice-dictation, whisper, free]
---

# How to Set Up a Free Groq API Key for Voice Dictation

## TL;DR

Groq gives you free access to Whisper Large v3 for transcription. The free tier is generous enough for daily use. Setup takes like 5 minutes. You don't even need a credit card. Just sign up, grab your key, nd paste it into Rota AI. Done.

---

## Why Groq?

Ok so there are a bunch of providers out there for speech-to-text. But here is why I keep coming back to Groq.

**Speed.** Like honestly it's absurd how fast Groq is. They use these LPUs (Language Processing Units) nd the inference is near-instant. You talk, you get text back. Barely any latency.

**Free tier.** The free tier is actually usable. Not one of those "try it for 11 minutes nd pay us forever" situations. You get enough requests per day for regular voice dictation without spending a dime.

**Whisper Large v3.** This is the best open source transcription model out there right now. Groq runs it. For free. That's kind of a big deal.

**No credit card required.** This one matters. A lot of providers want your card upfront just to try things. Groq doesn't. Sign up with your email nd you're in.

Tbh if you are building anything with voice input nd you don't want to deal with complex setup, Groq is the move.

---

## Step by Step: Get Your Free Groq API Key

Here is exactly how to do it.

### Step 1: Go to console.groq.com

Open your browser nd head to [console.groq.com](https://console.groq.com). That's the GroqCloud console. This is where everything lives.

### Step 2: Sign Up

Click "Sign Up" in the top right. You can use your email or sign in with Google. Takes maybe 30 seconds. No credit card. No hoops.

### Step 3: Create an API Key

Once you are in the dashboard:

1. Click on **API Keys** in the left sidebar
2. Click **Create API Key**
3. Give it a name. Something like "Rota AI" or "voice dictation" so you remember what it's for
4. Click **Submit**

You'll see a key that starts with `gsk_`. That's your key.

### Step 4: Copy the Key

Click the copy button next to the key. Or highlight it nd copy manually. Either way, get it on your clipboard.

**Important:** This is the only time you'll see the full key in the dashboard. If you lose it, you'll need to create a new one. So don't close the tab yet.

### Step 5: Paste Into Rota AI

Now open Rota AI:

1. Go to **Settings**
2. Find the **API Keys** section
3. Paste your Groq key into the Groq field
4. Save

That's it. Rota AI will now use Groq's Whisper Large v3 for all your voice dictation. Fast, free, accurate.

---

## Rate Limits nd How Round Robin Helps

Ok so the free tier does have limits. Here is the deal.

Groq's free tier gives you a certain number of requests per minute nd per day. The exact numbers change sometimes so check their docs for the current limits. But for most people doing voice dictation throughout the day, you won't hit them.

But what if you do? Or what if you are using Rota AI heavily for long recordings?

That's where **round robin** comes in. Rota AI supports multiple API keys for the same provider. So you can:

1. Create a second Groq account with a different email
2. Get another API key
3. Add it to Rota AI

Rota AI will rotate between the two keys automatically. Effectively doubling your rate limits. Lowkey genius if you ask me.

YMMV depending on how much you use it. But for most people, one key is plenty.

---

## Troubleshooting

Ran into issues? Here are the common ones.

### "Invalid API Key"

This usually means one of three things:

- You copied the key wrong. Try copying it again from the Groq dashboard
- The key was regenerated or deleted. Check the console to make sure it still exists
- There's a trailing space when you pasted it. Delete the field nd paste again carefully

### "Network Error" or Timeout

- Check your internet connection first. Obvious but worth saying
- Groq's API might be having a moment. Check [status.groq.com](https://status.groq.com)
- If you are on a corporate VPN, it might be blocking the request. Try without VPN

### "Model Not Available"

Sometimes Groq rotates which models are available on the free tier. If Whisper Large v3 is temporarily unavailable:

- Wait a few minutes nd try again
- Check Groq's Discord or status page for announcements
- As a fallback, you can switch to the Gemini API (see below)

### Transcription Quality Issues

If the transcription isn't accurate:

- Make sure you are speaking clearly. Whisper is good but it's not magic
- Background noise messes things up. Try a quieter environment
- Check your microphone input levels in your OS settings

---

## Alternative: Gemini API Key Setup

If Groq isn't working for you, or you just want a backup, Google's Gemini API is another solid option.

The Gemini API also has a free tier. Here is the quick version:

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Click **Get API Key**
4. Create a new key
5. Paste it into Rota AI's settings under the Gemini field

Gemini's free tier is also pretty generous. And since it's Google, the transcription quality is competitive. Having both Groq nd Gemini keys configured means Rota AI can fall back automatically if one provider has issues.

Fr, I recommend setting up both. Takes an extra 3 minutes nd you'll thank yourself later.

---

## FAQ

**Is Groq really free?**
Yes. The free tier is real nd it doesn't require a credit card. There are paid tiers if you need more capacity but the free one is enough for most people.

**How many transcriptions can I do per day on the free tier?**
It depends on the current rate limits. Check Groq's docs for the latest numbers. For typical voice dictation use (a few minutes at a time, several times a day), you'll be fine.

**Do I need to know coding to set this up?**
No. If you can copy nd paste, you can set this up. The whole process is clicking buttons in a dashboard.

**Can I use the same Groq key for multiple apps?**
Technically yes. But if you hit rate limits, it'll affect all apps using that key. For Rota AI alone, one key is plenty.

**What happens if I lose my API key?**
Just create a new one in the Groq dashboard. Delete the old one from Rota AI, paste the new one in. Takes 30 seconds.

**Is my voice data stored by Groq?**
Check Groq's privacy policy for the official answer. But generally, API providers don't store your data permanently. Still, if you are transcribing sensitive stuff, it's worth reading the fine print.

**Can I use this for languages other than English?**
Yes. Whisper Large v3 supports a ton of languages. Groq runs the full model so you get multilingual support on the free tier.

---

That's the whole thing. Get your free Groq key, plug it into Rota AI, nd start dictating. It's fast, it's free, nd it just works.

If you run into anything weird, drop a comment or check the troubleshooting section above. Happy transcribing.
