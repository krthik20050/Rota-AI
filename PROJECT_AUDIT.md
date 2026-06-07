# ROTA AI — COMPLETE PROJECT AUDIT

> **Date:** June 6, 2026 | **Auditor:** Deep codebase + GitHub + Website analysis

---

## PART 1: CODEBASE AUDIT

### Architecture Overview

The codebase is **well-structured** with clear separation of concerns:

```
desktop/
├── app/           — Core logic (controller, mixins, services)
│   ├── rota_app.py              (755 lines — main app orchestrator)
│   ├── controller.py            (re-exports public API)
│   ├── hotkey_mixin.py          (global hotkey handling)
│   ├── recording_state_mixin.py (state machine)
│   ├── processing_pipeline_mixin.py
│   ├── transcriber_mixin.py
│   ├── thread_lifecycle_mixin.py
│   ├── signal_bridges.py
│   ├── health_check.py
│   └── service_wiring.py
├── audio/         — Audio pipeline
│   ├── recorder.py              (sounddevice-based recording)
│   ├── transcriber.py           (Groq + local whisper)
│   └── vad.py                   (voice activity detection)
├── ui/            — All UI components
│   ├── main_window.py           (353 lines — sidebar + content stack)
│   ├── onboarding.py            (339 lines — 5-step wizard)
│   ├── settings_window.py       (354 lines — scroll settings)
│   ├── tray.py                  (97 lines — system tray)
│   ├── toast.py                 (150 lines — pill notifications)
│   ├── pages/                   — Home, Insights, Dictionary, Snippets
│   ├── overlay/                 — Pill overlay + waveform
│   └── components/              — Charts, heatmaps, history items
├── data/          — Config, database
├── injection/     — Text injection
├── plat/          — Platform-specific (Windows, macOS, Linux)
└── tests/         — Test files
```

### What EXISTS (Done)

| Feature | Status | Notes |
|---|---|---|
| Core pipeline (record → transcribe → inject) | DONE | Working |
| Global hotkey (F9) | DONE | pynput-based |
| System tray | DONE | Custom styled dark menu |
| Onboarding wizard | DONE | 5 steps: Welcome, API Keys, Model, Hotkey, Ready |
| Settings window | DONE | Scroll-based, multiple sections |
| Toast notifications | DONE | Pill-shaped, custom painted |
| Pill overlay | DONE | Floating recording indicator |
| Waveform widget | DONE | Custom QPainter |
| AI text cleanup | DONE | Gemini/Groq-based |
| Local whisper fallback | DONE | faster-whisper |
| Cloud transcription | DONE | Groq whisper-large-v3-turbo |
| Text injection | DONE | Windows UI Automation |
| History tracking | DONE | SQLite-based |
| Insights/analytics page | DONE | Stats, charts, heatmaps |
| Dictionary/personal words | DONE | |
| Snippets | DONE | |
| Crash detection | DONE | Flag file on crash |
| Error dialog | DONE | QMessageBox with GitHub link |
| Instance guard | DONE | Single-instance via socket |
| macOS port | IN PROGRESS | Platform files exist |
| Linux support | IN PROGRESS | Platform files exist |
| PyInstaller packaging | DONE | .exe exists |
| Dark theme | DONE | Custom QSS stylesheets |
| Auto-updater | PARTIAL | Check for updates exists |
| Logging | DONE | structlog + file logging |

### What's MISSING or NEEDS WORK

#### UI/UX Issues (Specific, Actionable)

1. **No audio level meter in main window**
   - The pill overlay has a waveform, but the main window has no visual mic level indicator
   - Users need to SEE the app is hearing them at all times
   - Fix: Add a small level meter widget to the home page status area

2. **No streaming transcription display**
   - Results appear only after full transcription completes
   - Users expect to see text appearing in real-time
   - Fix: Show partial/interim results as they arrive from Groq

3. **Settings window is scroll-based, not sidebar-based**
   - Current: Single scroll area with all settings
   - Better: Sidebar + stacked panel (like macOS System Settings)
   - This is a UX polish item, not critical

4. **No "copy to clipboard" visual feedback**
   - After transcription, text is injected but no confirmation it was copied
   - Fix: Show a brief "Copied!" toast or status bar message

5. **Onboarding requires API keys upfront**
   - Step 1 is API Keys — this blocks users who just want to try local mode
   - Fix: Make API keys optional, offer "Skip" to local-only mode

6. **No first-run mic test**
   - Onboarding has API keys and model download but no mic check
   - Fix: Add a "Test your microphone" step with level meter

7. **No keyboard shortcut display in main window**
   - Users have to remember F9 — no visual reminder
   - Fix: Show current hotkey in status bar or home page

8. **No transcription history search**
   - History list exists but no search/filter
   - Fix: Add a search bar above the history list

9. **No export functionality**
   - Can't export history to txt/csv
   - Fix: Add export button to history window

10. **No punctuation auto-insertion toggle in settings**
    - AI cleanup handles this but no user control
    - Fix: Add toggle in settings

11. **Tray icon doesn't change state**
    - Same icon for idle/recording/processing
    - Fix: Different icon or badge for each state

12. **No "Start with Windows" toggle**
    - Common expectation for desktop apps
    - Fix: Add toggle in settings + registry/startup folder integration

13. **No update notification**
    - Auto-updater exists but no visual prompt
    - Fix: Show toast when update is available

14. **No in-app feedback button**
    - Users have to go to GitHub to report issues
    - Fix: Add "Report Issue" button that opens pre-filled GitHub issue

15. **Font inconsistency**
    - Mix of Segoe UI, Inter, and system fonts
    - Fix: Standardize on one font family

#### Code Quality Issues

1. **PySide6 vs PyQt6 inconsistency**
   - Some files import PySide6 (main.py line 50), others PyQt6
   - This is a potential compatibility issue
   - Fix: Standardize on one (PyQt6 since that's the project standard)

2. **Hardcoded colors in multiple files**
   - Colors defined in multiple QSS files and Python files
   - Fix: Centralize color definitions in one place

3. **No type hints in UI files**
   - Mix of typed and untyped code
   - Fix: Add type hints for consistency

4. **Test coverage is minimal**
   - Only 4 test files for a 50-file codebase
   - Fix: Add tests for critical paths (recording, transcription, injection)

5. **No CI/CD**
   - No GitHub Actions for automated builds
   - Fix: Add workflow to build .exe on push

---

## PART 2: GITHUB AUDIT

### What EXISTS

| Item | Status |
|---|---|
| README with badges | DONE |
| "How It Started" story | DONE |
| Quick Start guide | DONE |
| Architecture docs | DONE |
| Build docs | DONE |
| Troubleshooting docs | DONE |
| Contributing guide | DONE |
| Security policy | DONE |
| MIT License | DONE |
| .gitignore | DONE |
| Releases with .exe | DONE |
| SEO keywords in README | DONE |
| Star history chart | DONE |
| FAQ section | DONE |
| Known Issues section | DONE |

### What's MISSING

1. **No GIF demo in README**
   - Static screenshots only — a GIF of the app in action would dramatically increase conversions
   - Fix: Record a 15-second demo and embed in README

2. **No CONTRIBUTING.md setup instructions**
   - Has contributing guide but no step-by-step dev environment setup
   - Fix: Add "Setting up dev environment" section

3. **No issue templates**
   - Missing `.github/ISSUE_TEMPLATE/` directory
   - Fix: Add bug_report.md and feature_request.md templates

4. **No PR template**
   - Missing `.github/PULL_REQUEST_TEMPLATE.md`
   - Fix: Add PR template

5. **No GitHub Discussions enabled**
   - Fix: Enable in repo settings

6. **No CODE_OF_CONDUCT.md**
   - Listed in docs table but may not exist
   - Fix: Add standard code of conduct

7. **No roadmap**
   - Users can't see what's planned
   - Fix: Add ROADMAP.md or GitHub Projects

8. **No GitHub Actions CI**
   - No automated builds or tests
   - Fix: Add workflow for build + test

9. **No release automation**
   - Manual release process
   - Fix: Add GitHub Action to build .exe on tag push

10. **No "good first issue" labels**
    - Hard for new contributors to find entry points
    - Fix: Label 3-5 beginner-friendly issues

11. **No GitHub Sponsors setup**
    - Badge exists but may not be configured
    - Fix: Enable GitHub Sponsors

12. **README has typos**
    - "I am a student nd" (missing 'a')
    - "but need a bit of money" (should be "don't need")
    - Fix: Proofread and fix

---

## PART 3: WEBSITE AUDIT

### Current State
- Website was at `website/index.html` but file is **gone** (only node_modules remain)
- Domain `rota.software` is registered and pointed to Vercel
- Vercel deployment exists but shows .vercel.app domain

### What Needs to Be Done

1. **Recreate the website**
   - The static HTML file was deleted
   - Fix: Rebuild the landing page (use the strategy.html as reference for design)

2. **Connect rota.software to Vercel**
   - DNS records need to be added in name.com
   - A record: @ → 76.76.21.21
   - CNAME: www → cname.vercel-dns.com

3. **Website content needed:**
   - Hero with value proposition
   - Download button (links to GitHub releases)
   - Feature cards
   - Screenshots/GIF of app
   - Privacy promise
   - FAQ section
   - Link to GitHub

---

## PART 4: PRIORITIZED ACTION LIST

### DO NOW (Before Any Marketing)

| # | Task | Effort | Impact |
|---|---|---|---|
| 1 | Fix README typos | 5 min | High |
| 2 | Add GIF demo to README | 30 min | Very High |
| 3 | Create issue templates | 15 min | Medium |
| 4 | Add CODE_OF_CONDUCT.md | 10 min | Low |
| 5 | Recreate website landing page | 2-4 hours | Very High |
| 6 | Connect rota.software DNS | 10 min | High |
| 7 | Add "good first issue" labels | 10 min | Medium |
| 8 | Enable GitHub Discussions | 5 min | Medium |

### DO NEXT (First 30 Days)

| # | Task | Effort | Impact |
|---|---|---|---|
| 9 | Add audio level meter to main window | 2-4 hours | High |
| 10 | Add streaming transcription display | 4-8 hours | Very High |
| 11 | Add mic test to onboarding | 1-2 hours | High |
| 12 | Add "Start with Windows" toggle | 1-2 hours | Medium |
| 13 | Add copy-to-clipboard feedback | 30 min | Medium |
| 14 | Add hotkey display in main window | 30 min | Medium |
| 15 | Add update notification toast | 1-2 hours | Medium |
| 16 | Add in-app feedback button | 1 hour | Medium |
| 17 | Standardize PyQt6 imports | 1 hour | Low |
| 18 | Centralize color definitions | 2 hours | Low |
| 19 | Add GitHub Actions CI | 2-4 hours | Medium |
| 20 | Add ROADMAP.md | 1 hour | Medium |

### DO LATER (Before 500 Users)

| # | Task | Effort | Impact |
|---|---|---|---|
| 21 | Redesign settings to sidebar layout | 4-8 hours | Medium |
| 22 | Add history search | 2-4 hours | Medium |
| 23 | Add export functionality | 2-4 hours | Medium |
| 24 | Add state-aware tray icon | 1-2 hours | Low |
| 25 | Add punctuation toggle | 1 hour | Low |
| 26 | Improve test coverage | 8-16 hours | Medium |
| 27 | Add release automation | 2-4 hours | Medium |

---

## PART 5: SOCIAL MEDIA RECOMMENDATION

**Don't create separate social accounts for Rota AI.** You're right — use your personal accounts instead.

### Recommended Approach

1. **Personal Twitter/X** — Post about Rota AI using your existing account
   - Build in public: share development journey, milestones, lessons
   - Use hashtags: #buildinpublic #opensource #python #voicetyping
   - Tag relevant accounts: @GroqInc, @OpenRouterAI

2. **Personal LinkedIn** — Write about the project from your perspective
   - "How I built a free open-source alternative to Wispr Flow as a student"
   - This performs extremely well on LinkedIn (personal story + technical)

3. **Reddit** — No account needed beyond your personal one
   - Post in r/Python, r/opensource, r/selfhosted, r/voicecoding
   - Be genuine, not promotional

4. **No Discord server yet** — Wait until you have 50+ active users
   - Start with GitHub Discussions for community

5. **No TikTok/Instagram** — Not worth the effort for a developer tool
   - Focus on text-based platforms where your audience lives

### Content Ideas for Personal Accounts

- "Day 1: I'm building a free open-source voice dictation app"
- "How I reverse-engineered Wispr Flow's text injection"
- "Week 4: Got my first 50 users. Here's what I learned."
- "Why I chose Groq over OpenAI for transcription"
- "How a student built a Wispr Flow alternative with Python"
- "Month 3: 500 users. Here's my $0 marketing breakdown"

---

## SUMMARY

**The codebase is solid.** The architecture is clean, the feature set is impressive, and the packaging works. The main gaps are:

1. **UI/UX polish** — Audio level meter, streaming transcription, mic test
2. **GitHub hygiene** — Issue templates, GIF demo, fix typos
3. **Website** — Needs to be recreated and connected to rota.software
4. **Social** — Use personal accounts, don't create brand accounts

**You're about 70% ready for launch.** The remaining 30% is polish and distribution infrastructure. Focus on the "DO NOW" list first, then start posting on Reddit and Twitter.
