---
title: "13. How to Transcribe Audio Files with Whisper on Windows"
meta_title: "How to Transcribe Audio Files with Whisper on Windows"
meta_description: "Use faster-whisper on Windows to transcribe audio files locally. Step by step guide with command line examples, output formats, batch processing, and real numbers."
target_keyword: "transcribe audio whisper windows"
---

# 13. How to Transcribe Audio Files with Whisper on Windows

TL;DR: Install faster-whisper with pip, run one command, and get a transcript from any audio file. Works on Windows, runs on CPU or GPU, outputs to text or SRT. Here is the full walkthrough.

So here is the thing. Sometimes you do not want real-time dictation. Sometimes you already have a recorded audio file and you just need the transcript. Maybe it is a meeting recording. Maybe it is a voice memo. Maybe it is a podcast.

That is what this is about. Taking an audio file you already have and turning it into text. Locally on Windows. No cloud. No subscriptions. No uploading your audio to anyone.

## Why not just use a Cloud API?

Fair question. Services like OpenAI Whisper API exist. They work well. But:

1. You are uploading audio to someone else's server.
2. API costs money at scale.
3. You need internet for every file.
4. Some audio is sensitive nd you just do not want it leaving your machine.

Local transcription fixes all of that. Once it is set up, you can transcribe as many files as you want. Free. Forever. Offline.

## What is faster-whisper?

OpenAI released Whisper. It is a speech recognition model. It is open source. It is really good.

But the default Python package (openai-whisper) can be annoying to install on Windows. Dependencies, CUDA issues, all that.

faster-whisper is a reimplementation that is:
- Easier to install
- Faster at transcription (like 4x faster)
- Uses less memory
- Fully compatible with Whisper models

It is what I recommend for Windows users. It just works.

## Installation

Open a terminal. PowerShell or CMD, either works.

First, make sure you have Python 3.8+:

```
python --version
```

If you do not have Python, grab it from python.org. The Windows installer is straightforward.

Install faster-whisper:

```
pip install faster-whisper
```

That is it. No CUDA toolkit needed for CPU. If you have an ndvidia GPU, you will want CUDA installed for GPU acceleration. I will cover that below.

## Basic Transcription

Say you have a file called lecture.mp3. You want a transcript. Run:

```
whisper lecture.mp3 --model medium
```

That's it. The model downloads automatically the first time (about 1.5GB for medium). Then it transcribes. When it finishes, you get a .txt file, an .srt file, and a .json file next to your audio file.

The .txt is the plain transcript. The .srt is a subtitle file with timestamps. The .json has word-level timestamps nd metadata.

## Choosing a Model

faster-whisper supports all the standard Whisper models. Here is the breakdown:

| Model   | Size   | RAM Needed | GPU VRAM | Speed      | Accuracy |
|---------|--------|------------|----------|------------|----------|
| tiny    | 75MB   | 4GB        | 1GB      | Very Fast  | Low      |
| base    | 140MB  | 4GB        | 1GB      | Fast       | Decent   |
| small   | 250MB  | 6GB        | 2GB      | Good       | Okay     |
| medium  | 1.5GB  | 8GB        | 5GB      | Moderate   | Good     |
| large-v3| 3GB    | 12GB       | 10GB     | Slow       | Best     |

I use medium on my machine (i5 12th gen, 16GB RAM, RTX 3050). It gives the best balance of speed nd accuracy for English.

If you have a weaker machine, use small. It is honestly not that bad. Only use large if accuracy is critical nd you have a good GPU.

## Output Formats

faster-whisper supports multiple output formats. Use the --output_format flag:

```
whisper lecture.mp3 --model medium --output_format txt
```

Available formats:

- **txt** - Plain text transcript. Just the words, no timestamps.
- **srt** - Subtitle format with timestamps. Works with video players.
- **vtt** - WebVTT subtitles. Same idea as SRT, slightly different format.
- **json** - Full data including word-level timestamps, confidence scores, nd segments.
- **tsv** - Tab-separated. Good for loading into a spreadsheet.
- **all** - Generates every format. This is the default.

For most people, txt is what you want. If you need timestamps, go with srt or vtt.

## Real Numbers on My Machine

I tested this on my Dell G15. i5 12th gen, 16GB RAM, RTX 3050 4GB.

Audio file: 30 minute college lecture. MP3 format, 128kbps.

| Model  | CPU Time | GPU Time |
|--------|----------|----------|
| small  | 8 min    | 1.5 min  |
| medium | 18 min   | 3 min    |
| large  | Not tested (4GB VRAM not enough) |

GPU is with the --device cuda --compute_type int8 flags. CPU is default.

So on GPU, medium model transcribes a 30 minute file in about 3 minutes. That is pretty fast tbh.

## GPU Setup (Optional but Recommended)

If you have an ndvidia GPU, using it makes transcription way faster. Here is what you need:

1. Install CUDA Toolkit 11.8 or 12.x from ndvidia's website.
2. Install faster-whisper with CUDA support:

```
pip install faster-whisper
```

The standard pip install already includes CUDA support if CUDA is detected. You do not need a separate package.

Run with GPU:
```
whisper lecture.mp3 --model medium --device cuda --compute_type int8
```

The int8 compute type uses less VRAM. On my 4GB RTX 3050, medium works with int8 but not with float16. If you have more VRAM, try float16 or float32 for slightly better accuracy.

If CUDA is not detected, faster-whisper falls back to CPU automatically. No error, just slower.

## Batch Processing Meeting Recordings

Here is where this actually gets useful in practice. I had a folder with like 20 meeting recordings from a college project. All MP3 files. I needed transcripts of all of them.

Doing them one by one would be annoying. So I made a batch script.

On Windows, save this as batch_transcribe.bat:

```batch
@echo off
set MODEL=medium
set FORMAT=srt

for %%f in (*.mp3 *.wav *.m4a *.flac) do (
    echo Transcribing %%f...
    whisper "%%f" --model %MODEL% --output_format %FORMAT% --language en
    echo Done: %%f
)

echo All files processed.
pause
```

Drop that script in your folder with audio files. Double click it. It loops through every audio file nd transcribes it. Just let it run.

For Linux or WSL users, here is the bash version:

```bash
#!/bin/bash
MODEL="medium"
FORMAT="srt"

for f in *.mp3 *.wav *.m4a *.flac; do
  [ -f "$f" ] || continue
  echo "Transcribing $f..."
  whisper "$f" --model "$MODEL" --output_format "$FORMAT" --language en
done

echo "All files processed."
```

I had about 15 files totaling roughly 8 hours of audio. Using medium model on GPU, the whole batch took about 45 minutes. Went to ndmade a sandwich, came back, all done. Fr, that is the dream workflow.

## Specifying Language

Whisper auto-detects language. But if you know the language, specifying it speeds things up nd improves accuracy:

```
whisper lecture.mp3 --model medium --language en
```

Supported languages include en, es, fr, de, hi, ta, zh, ja, ko, nd a bunch more. If the language code does not work, try the full name like "English" or "Tamil."

## My Actual Use Case: College Lectures

Lowkey this is why I started doing this.

I take a lot of notes during lectures. But sometimes I miss things. The professor says something important while I am still writing the previous point. Or my hand hurts. Or I zone out. We all zone out sometimes.

So I started recording lectures on my phone. Just audio. Then every weekend I batch transcribe them all. Now I have a text file for every lecture. I can search through them. Copy quotes. Review before exams nd I am not scrambling through messy handwritten notes.

The accuracy is surprisingly good. Even with professors who have accents. The medium model handles Indian English dialects pretty well. YMMV depending on accent, background noise, nd recording quality.

Pro tip: place your recording device closer to the speaker. Even a cheap phone recording from 3 feet away is way better than from 15 feet away. The cleaner the audio, the better the transcript.

## Dealing with Imperfect Transcripts

Let me be real. Local Whisper is not perfect. You will get some errors:

- Technical terms might get garbled. "Kubernetes" might come out as "coober netease." Fun.
- Names nd proper nouns are hit or miss.
- If there is background noise, accuracy drops.
- Overlapping speech is hard. If two people talk at once, Whisper gets confused.

For my lecture transcripts, I estimate about 95% accuracy with clean audio on medium model. That is enough to be useful. I just skim through nd fix the obvious mistakes. Way faster than typing everything from scratch.

If you need higher accuracy, use the large model. But you will need the GPU VRAM for it.

## Other Flags Worth Knowing

Here are some flags I use regularly:

```
--task translate
```
Transcribes nd translates to English. Useful if your audio is in another language.

```
--beam_size 5
```
Higher beam size = slightly better accuracy but slower. Default is 5. You can try 1 for faster results.

```
--vad_filter True
```
Voice Activity Detection. Removes silence from processing. Speeds things up on files with lots of pauses.

```
--output_dir ./transcripts/
```
Saves all output files to a specific folder instead of next to the audio file.

## FAQ

**Which Whisper model should I use on Windows?**
Medium for the best balance of speed nd accuracy if your machine can handle it. Small if you have limited RAM (8GB). Tiny only if you need speed nd accuracy does not matter much.

**Does faster-whisper work on Windows 10?**
Yes. Works on Windows 10 nd 11. As long as you have Python 3.8+, you are good.

**Can I transcribe video files?**
Whisper works on audio, not video. But you can extract the audio first with ffmpeg:
```
ffmpeg -i video.mp4 -vn -acodec mp3 audio.mp3
```
Then transcribe the audio file.

**Does it work for languages other than English?**
Yes. Whisper supports 90+ languages. Specify with --language Tamil, --language Hindi, etc. Accuracy varies by language. English is the best. Some lower-resource languages are worse.

**My GPU only has 4GB VRAM. Can I use it?**
Yes. Use --compute_type int8. It is designed for lower VRAM. Medium model works. Large does not.

**How is this different from Rota AI?**
Rota AI is for real-time voice dictation. You speak, text appears instantly. This guide is for when you already have recorded audio files nd need transcripts. They solve different problems. I use both.

**Is faster-whisper free?**
Completely free. It is open source. No API keys, no accounts, no limits.

**What audio formats are supported?**
MP3, WAV, M4A, FLAC, OGG, nd most common audio formats. Anything ffmpeg can decode, Whisper can transcribe.

---

*Written by Karthik Krishnan. I transcribe all my college lectures with faster-whisper so I can stop pretending I focus for 90 minutes straight. It works weirdly well.*
