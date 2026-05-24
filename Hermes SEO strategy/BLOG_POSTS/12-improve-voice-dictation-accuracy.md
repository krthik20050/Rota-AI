---
title: "How I Improved Voice Dictation Accuracy from 70% to 95%"
slug: improve-voice-dictation-accuracy
date: 2026-05-24
tags: [voice-dictation, speech-to-text, productivity, accuracy, tldr]
author: Karthik
keyword: improve voice dictation accuracy
---

## TL;DR

My voice dictation was garbage. 70% accuracy meant I spent more time fixing errors than typing. I almost gave up. Then I tuned four things: mic positioning, VAD threshold, personal dictionary, and model choice. Accuracy jumped to 95%. Now I dictate daily. Here's exactly what I did, with real numbers so you can replicate it.

---

## The Problem: Voice Dictation That Barely Worked

I started using voice dictation six months ago. Typing all day was wrecking my wrists. I figured speech-to-text would fix that.

It didn't. Not at first.

Out of the box, I was getting maybe 70% accuracy. That means roughly 3 out of every 10 words were wrong. "Schedule a meeting with the design team" became "schedule a eating with the sign team." Every. Single. Time.

I'd dictate a paragraph. Then spend five minutes fixing it. That's slower than typing. I almost quit after week two.

But I kept at it. And tbh, the problem wasn't the technology. It was my setup.

---

## Fix #1: Mic Positioning (70% → 78%)

This sounds dumb. But mic placement was the single biggest early win.

I was using my laptop's built-in mic. The one next to the webcam. My mouth was about two feet away. The mic was picking up keyboard noise, room echo, my cat, everything.

**What I tried first:**

- Bought a cheap $25 cardioid USB mic
- Positioned it 6 inches from my mouth, slightly off-axis (not directly in front)
- Added a basic foam windscreen

**Result:** Accuracy went from 70% to 78%. Just from mic placement.

The off-axis thing matters more than people think. You don't want to blast the mic directly. Angle it about 15-20 degrees to the side. Reduces plosives (those hard P and B sounds that distort).

**Key takeaway:** You don't need a $200 mic. But you do need the mic close to your mouth and pointed slightly off-center. YMMV depending on your room acoustics, but this alone is worth 8 points.

---

## Fix #2: VAD Threshold Tuning (78% → 85%)

VAD stands for Voice Activity Detection. It's the system that decides when you're speaking vs. when you're silent.

The default VAD threshold on most dictation software is set for "average" environments. My home office is quiet. So the threshold was too high. It was cutting off the beginnings and ends of my words.

**What I did:**

I dug into the settings and found the VAD sensitivity slider. Most apps hide this, but it's usually there if you look.

- Lowered VAD threshold from default (usually around -40dB) to about -55dB
- This made the system more sensitive to quiet speech
- Also adjusted the "silence duration" from 800ms to 500ms so it didn't cut me off between sentences

**Result:** Accuracy jumped from 78% to 85%.

The biggest improvement was with short words. "A," "the," "is," "to" — these were getting dropped constantly before. After tuning VAD, they started showing up.

**Pro tip:** If your dictation software doesn't expose VAD settings, try using something like `webrtc-vad` as a preprocessing step. It's open source and works well.

---

## Fix #3: Personal Dictionary (85% → 91%)

This was the fix I should have done first. I didn't even know most dictation systems support custom dictionaries.

I use a lot of specific terms in my work. Product names, technical jargon, people's names. The base model had never heard of half of them.

**What I built:**

I created a personal dictionary file with about 200 entries. Things like:

- Names of colleagues and clients
- Product-specific terminology
- Acronyms we use internally
- Common phrases I dictate ("let's circle back," "per my last email")

Most dictation systems let you import a custom vocabulary. On macOS it's the "Text Replacement" system. On Windows it's the "Speech Recognition" profile. On Linux with Whisper-based tools, you can pass a vocabulary file.

**Result:** Accuracy went from 85% to 91%.

The improvement was most noticeable in work contexts. Personal dictation (texts, casual notes) was already decent. But work dictation improved dramatically because the system finally knew what I was talking about.

**How to do this:**

1. Keep a running list of words your dictation gets wrong
2. After a week, you'll have 50-100 entries easily
3. Add them to your system's custom dictionary
4. Update monthly

Lowkey the highest-effort, highest-reward fix on this list.

---

## Fix #4: Choosing the Right Model (91% → 95%)

This was the final piece. I had been using whatever default model came with my OS. On macOS that's Apple's built-in dictation. It's fine for casual use. But it's not optimized for my voice.

**What I tested:**

I ran the same 500-word test passage through four different dictation engines:

| Model | Accuracy | Notes |
|-------|----------|-------|
| Apple Built-in | 85% | Decent, but struggles with accent |
| Google Speech-to-Text | 88% | Better with accents, needs internet |
| Whisper Large v3 | 93% | Excellent, but slow on CPU |
| Whisper Medium + fine-tune | 95% | Best balance of speed and accuracy |

I ended up going with Whisper Medium. It runs locally on my machine (M2 MacBook), processes in about 2x real-time, and handles my accent way better than the alternatives.

The fine-tuning part is optional but fr, it made a difference. I fed it about 30 minutes of my own voice recordings with transcripts. That's it. The model learned my speech patterns and the improvement was immediate.

**If you can't fine-tune:** Just switching from your OS default to Whisper Large v3 will likely give you a 5-8% boost. It's that much better for non-standard accents.

---

## The Full Journey: 70% → 95%

Here's the progression over about three months:

| Week | Change | Accuracy |
|------|--------|----------|
| 1 | Baseline (laptop mic, default settings) | 70% |
| 3 | Added USB mic, proper positioning | 78% |
| 5 | Tuned VAD threshold | 85% |
| 8 | Built personal dictionary (200 entries) | 91% |
| 12 | Switched to Whisper Medium + fine-tune | 95% |

Each fix built on the last. None of them alone would have gotten me to daily-driver status. But together, they transformed voice dictation from a frustration into something I actually rely on.

---

## What 95% Accuracy Actually Feels Like

At 70%, dictation is a chore. You're constantly backtracking, correcting, swearing.

At 95%, it just works. I dictate blog posts, emails, meeting notes, even code comments. I still make corrections, but maybe 1-2 per paragraph instead of 5-6 per sentence.

My average dictation session is about 15 minutes. At 70% accuracy, I'd spend another 10 minutes fixing errors. At 95%, I spend maybe 2 minutes. That's 8 minutes saved per session. Multiple times a day, it adds up.

I went from "this doesn't work" to "I can't imagine going back to typing everything." That's a big shift.

---

## FAQ

**Q: What mic do you recommend for voice dictation?**

A: Any cardioid USB mic under $50 works. The Fifine K669 or the Maono AU-A04 are both solid. The key is positioning, not price. Keep it 6 inches from your mouth, slightly off-axis.

**Q: Does voice dictation work with accents?**

A: Yes, but you need the right model. Whisper handles accents better than most built-in solutions. If you have a strong accent, fine-tuning on your own voice recordings is the single best thing you can do.

**Q: How long does it take to build a useful personal dictionary?**

A: About a week of normal use. Just keep a note of every word the system gets wrong. After 7 days you'll have enough entries to make a real difference. I update mine monthly now.

**Q: Is 95% accuracy good enough for professional work?**

A: For me, yes. I still proofread everything. But the edits are minor. At 95%, you're fixing the occasional homonym or missed punctuation, not rewriting sentences.

**Q: Can I use these tips with any dictation software?**

A: Most of them are software-agnostic. Mic positioning and VAD tuning apply everywhere. Personal dictionary support varies, but most modern systems have it. Model choice depends on what you're willing to set up.

**Q: How much did all this cost?**

A: About $30 total. $25 for the mic, $5 for the foam windscreen. Whisper is free and open source. The personal dictionary is just a text file. The biggest investment was time, not money.

**Q: What's the single most impactful change?**

A: If I had to pick one: mic positioning. It's free (just move closer to your mic) and gave me the biggest single jump. But honestly, you need all four fixes to get to 95%.

---

## Final Thoughts

Voice dictation isn't magic. Out of the box, it's often mediocre. But the gap between "mediocre" and "excellent" is surprisingly small. Four changes. Three months. 25 percentage points of accuracy.

If you've tried voice dictation and gave up, I get it. I almost did too. But the tech is there. You just need to set it up right.

Start with the mic. Then tune the VAD. Build your dictionary. Pick the right model. Do those four things and you'll be dictating like a pro.

Trust me on this one.
