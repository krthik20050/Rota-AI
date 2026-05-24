---
title: "10. How to Dictate Text Into Any Windows Application"
meta_title: "How to Dictate Text Into Any Windows Application"
meta_description: "Rota AI can inject dictation into VS Code, Outlook, Slack, Notepad, browsers, and more. Here is how text injection works and how to switch between methods."
target_keyword: "dictate text windows app"
---

# 10. How to Dictate Text Into Any Windows Application

TL;DR: Rota AI can send dictation to virtually any Windows app. VS Code, Outlook, Slack, Notepad, browsers. Here is how injection works.

I spent two weeks on this part of Rota AI. Two weeks just trying to get text to show up in the right place. It was the single hardest problem I solved.

Here is why.

## The Problem: Every App Handles Text Input Differently

You would think typing text into an app is a solved problem. Like, every app has a text box. Just put the text there. Done.

Nah.

VS Code uses a custom editor built on Electron. Slack is also Electron but handles input differently. Outlook uses its own thing. Browsers? Depends on the browser. Depends on the website. Some sites use contenteditable divs. Some use actual input fields. Some use both.

So when Rota AI finishes transcribing your speech and cleaning it up, it has a string of text that needs to land in whatever app you are using. And every app wants it delivered differently.

I ended up building three separate injection methods.

## Method 1: SendInput API (Works for Most Apps)

This is the default. SendInput is a Windows API that simulates actual keyboard input. It sends keystrokes at the OS level, so the target app thinks you are typing.

Most apps handle this fine. Notepad, Word, VS Code, browsers, most desktop apps. If an app has a standard text field, SendInput just works.

This is the fastest method too. Text appears character by character, almost instantly.

The downside: some apps do not process standard keyboard events properly. Electron apps sometimes eat the input. Custom controls might ignore it entirely. That is when you need method 2.

## Method 2: Clipboard Paste (The Reliable One)

Here is how this works. Rota AI copies your text to the clipboard, then sends Ctrl+V to the target app. The app pastes the text like you hit paste yourself.

This works for almost everything. Apps that ignore simulated keystrokes usually respect clipboard paste because it comes through a different Windows message path.

The tradeoff: it overwrites whatever was in your clipboard. If you had something copied, it is gone. I added a clipboard restore feature that puts your old clipboard content back after injection. But it is not perfect. YMMV.

Also, clipboard paste is slightly slower than SendInput. You might notice a tiny delay. Like, a fraction of a second. Most people do not notice.

## Method 3: pyautogui Fallback (The Last Resort)

For the rare apps that reject both SendInput and clipboard paste, there is pyautogui. This one actually moves your mouse cursor and clicks on the text field, then types the text.

It is the slowest method. It is also the most invasive because it takes control of your mouse for a moment. But it works when nothing else does.

I have only needed this for a couple of weird apps. Some old enterprise software. A few custom internal tools people have told me about. For 95% of users, you will never touch this.

## How to Switch Methods in Settings

Open Rota AI. Go to Settings > Text Injection. You will see three options:

- **SendInput** (default)
- **Clipboard Paste**
- **pyautogui**

Pick one. Hit save. Done.

You can also set per-app injection methods. So if SendInput works for everything except Slack, you can set Slack to use clipboard while everything else stays on SendInput. That is what I do personally.

## The Large Text Threshold

Here is something I added after getting frustrated with long dictations.

When you dictate something short, like a sentence or two, SendInput works great. But when you dictate a paragraph, sending it character by character through SendInput can cause issues. Some apps start lagging. Characters get dropped. The text comes out garbled.

So I added a threshold. By default, it is set at 200 characters. Anything longer than that automatically uses clipboard paste instead of SendInput. Clipboard handles large text better because it is one operation instead of hundreds of keystrokes.

You can change this threshold in settings. If you have a fast machine, you might bump it up. If you are on older hardware, lower it.

## Injection Delay: Fixing Garbled Text

Sometimes text comes out wrong. Letters missing. Words jumbled. This usually happens when the target app is slow to process input.

There is a setting called Injection Delay. It adds a small pause between keystrokes (for SendInput) or before the paste operation. Default is 0ms. If you get garbled text, try setting it to 50ms. If that is not enough, go to 100ms.

I keep mine at 30ms. Fixes the occasional garble without adding noticeable delay.

## Apps I Have Tested

Here is the list. These all work with Rota AI dictation:

| App | Method | Notes |
|-----|--------|-------|
| VS Code | SendInput | Works out of the box |
| Slack | Clipboard | SendInput sometimes drops chars |
| Discord | SendInput | Works fine |
| Outlook | Clipboard | SendInput is unreliable in compose window |
| Chrome | SendInput | Works on most sites |
| Edge | SendInput | Same as Chrome |
| Notepad | SendInput | Perfect, always works |
| Word | SendInput | Works, formatting stays intact |

I tested these on Windows 11. Windows 10 should be the same but I have not verified every app.

If your app is not on this list, try SendInput first. If that does not work, switch to clipboard. If that fails too, pyautogui will probably save you.

## FAQ

**Can I dictate into any Windows app?**
Almost any app that accepts text input. If you can type in it with a keyboard, Rota AI can probably dictate into it.

**Which injection method should I use?**
Start with SendInput. If text does not appear or comes out garbled, switch to clipboard. Use pyautogui only as a last resort.

**Does clipboard paste overwrite my clipboard?**
Yes. Rota AI tries to restore your old clipboard content after injection but it is not 100% reliable. If you have something important copied, save it before dictating.

**Why is my text garbled in some apps?**
The app is processing input too slowly. Increase the Injection Delay setting. Start at 50ms and adjust from there.

**Can I set different injection methods for different apps?**
Yes. Go to Settings > Text Injection > Per-App Rules. Set your preferred method for each app.

**Does this work with non-English text?**
SendInput handles Unicode but some apps do not. Clipboard paste is more reliable for non-English characters. If you are dictating in another language, try clipboard first.

**What if none of the three methods work?**
That is rare. Like, I have seen it maybe twice. If it happens, open a GitHub issue with the app name and I will look into it.

---

*Written by Karthik Krishnik. I spent two weeks on text injection so you do not have to think about it. Just press F9 and talk.*
