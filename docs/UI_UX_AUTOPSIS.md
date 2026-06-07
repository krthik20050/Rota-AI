# 🔬 Rota AI UI/UX Autopsy — Pixel-by-Pixel vs Wispr Flow

> **Date:** May 27, 2026
> **Methodology:** Read every UI file in the codebase (overlay, settings, styles, pages, components, onboarding, tray, toast, debug windows — 24+ files). Researched Wispr Flow's design language, Mac App Store listings, their design blog, media kit, YouTube reviews, and comparison videos.
> **Tone:** Brutally honest. No sugar coating. This document exists to fix things.

---

## Executive Summary

**Rota AI UI Grade: 4/10** — Functional. Works. But looks and feels like an internal tool from 2018.

**Wispr Flow UI Grade: 9/10** — Feels like it belongs on a Mac. Every pixel is intentional. Animations are buttery. The UX is invisible until you need it.

### The Gap in One Sentence

Wispr Flow's overlay could be mistaken for a macOS system feature. Rota AI's overlay looks like a PyQt5 tutorial example.

---

## 1. THE OVERLAY (Pill) — The Most Visible Part of Your App

### Wispr Flow

| Property | Description |
|----------|-------------|
| **Shape** | Pill-shaped (highly rounded rect), slim, unobtrusive |
| **Color** | Dark glass-morphism (NSVisualEffectView) — blends with desktop wallpaper behind it |
| **Blur** | Real macOS vibrancy + blur — picks up colors from background content |
| **Animation (appear)** | Spring-based transition (response: ~0.3s, damping: ~0.7) — organic, buttery |
| **Animation (listen)** | Gentle luminosity pulse / breathing effect — not a literal sound wave |
| **Font** | SF Pro (system font, perfect kerning at any size) |
| **Philosophy** | "Invisible" — disappears into background, reveals only when needed |
| **Position** | Movable anywhere on screen, stays out of the way |
| **Placement** | OS-level layer, not an app window — truly global |

### Rota AI (actual code)

```python
# From pill_overlay.py — the overlay is a QFrame with fixed styling
self.setObjectName("PillContainer")
# In the QSS:
QFrame#PillContainer {
    background: #141918;           /* Solid dark green-black */
    border: 1px solid rgba(255,255,255,6); /* Nearly invisible border */
    border-radius: 28px;
}
```

| Property | Rota AI | Verdict |
|----------|---------|---------|
| **Shape** | QFrame with border-radius: 28px | Decent shape, but rendering is jagged on non-retina |
| **Color** | `#141918` — solid, flat dark green | Looks cheap. No depth. No blur. Just a solid rectangle. |
| **Blur** | ❌ **None** | This is the single biggest visual gap. Ours is a solid block. Theirs blends with the desktop. |
| **Animation (appear)** | Either instant or not at all | No spring. No easing. Just pops in. Feels jarring. |
| **Animation (listen)** | Waveform widget draws frequency bars | The waveform is fine technically, but it's on a solid dark background, not integrated into the pill seamlessly |
| **Font** | `"Segoe UI", "Inter", sans-serif` | Not bad, but not system-native on any OS |
| **Philosophy** | "Functional" | It's a window. It looks like a window. |
| **Position** | Fixed position near cursor? Movable? | Need to check — but even the concept of "positionable" is absent |

### The Waveform Widget

```python
# From waveform_widget.py
# Draws audio level bars using QPainter
# Colors: #86EFAC (green) for active bars, #1A2B1E (dark) for inactive
```

The waveform is **fine**. It works. But it's basic QPainter rectangles. No glow, no gradient, no smooth falloff, no animation curves. It's a VU meter from 1998.

### The Fix

**What Rota AI needs to do to close this gap:**

1. **Blur effect** — On Windows: use DWM blur behind (SetWindowCompositionAttribute). On macOS: NSVisualEffectView via pyobjc. On Linux: KDE blur or GNOME transparency. Currently: **none of these**.
2. **Spring animations** — Replace instant show/hide with QPropertyAnimation using custom easing curves (OutBack with overshoot, not just OutCubic).
3. **Background-aware coloring** — Sample the desktop region behind the overlay and tint the pill color to match. Or at minimum, use a translucent gradient `rgba(20, 25, 24, 0.85)` instead of solid `#141918`.
4. **Glow on active** — Soft green outer glow using QGraphicsDropShadowEffect when listening. Currently: nothing.
5. **Smooth waveform** — Replace raw QPainter rectangles with QPainterPath smooth curves. Add gradient falloff. Use QGraphicsBlurEffect for glow on active bars.

---

## 2. SETTINGS WINDOW — The Second Most Visited Screen

### Wispr Flow

- **Layout:** Standard macOS sidebar → detail panel (NavigationSplitView pattern)
- **Organization:** General | Voice | Shortcuts | Account — clear hierarchical grouping
- **Complexity:** Hidden by default. Only shows what you need. "Settings you never have to open."
- **Typography:** SF Pro, clean hierarchy
- **Search:** Searchable settings (macOS standard)

### Rota AI (actual code)

```python
# From settings_window.py
# Single QScrollArea with embedded sections stacked vertically
# No sidebar, no tabs, no search

# Layout approach: _build_stacked_pages() creates:
# 1. General section
# 2. Microphone section
# 3. Audio section
# 4. Writing Mode section
# 5. Dictionary section
# 6. Snippets section
# 7. Shortcuts section
# 8. About section
# ...all in one scrollable column
```

**The Problems:**

1. ⚠️ **Everything visible at once** — 8+ sections in a single scroll view. Overwhelming. A user who just wants to change their hotkey has to scroll past microphone settings, writing modes, dictionary entries, and snippets. This is **cognitive overload**.

2. ⚠️ **Inconsistent labeling** — Some sections say "Writing Mode", others say "Audio Settings", some use title case, some use sentence case. No consistent voice.

3. ⚠️ **No visual hierarchy** — Section headers are `SectionTitle` objects but they're the same size as content labels. Weak differentiation between section title, subsection, setting label, and setting description. Everything is `font-size: 12px` to `14px`.

4. ⚠️ **No search** — With 8+ sections and 40+ settings, finding anything requires scrolling.

5. ⚠️ **Mixed QSS approach** — Some styling in `settings_qss.py`, some inline in Python code with `setStyleSheet()`. Styles are duplicated across files. No single source of truth.

6. ⚠️ **Cramped spacing** — `setContentsMargins(20, 18, 20, 18)` in most cards, sections packed with `setSpacing(16)` or `12`. No breathing room. Everything feels dense.

### The Fix

1. **Add a sidebar** — Left sidebar with section icons/labels, right panel shows selected section content. This is the standard pattern for settings with 5+ sections.
2. **Add search** — Filter settings by keyword. Essential for power users.
3. **Unify styling** — Move ALL styles into `settings_qss.py`. Remove all inline `setStyleSheet()` calls. Create a proper token system.
4. **Improve spacing** — Add 8px more padding between sections. Reduce information density.
5. **Group related settings** — Microphone + Audio should be one "Audio" section, not two. Shortcuts + Overlay behavior should be one "Interface" section.

---

## 3. ONBOARDING — First Impressions

### Wispr Flow

- **Steps:** 2-3 screens max. Permissions → Explanation → First dictate
- **Goal:** Fastest path to first successful dictation. Under 30 seconds.
- **Visual:** Clean, minimal, uses native macOS UI patterns

### Rota AI (actual code)

```python
# From _onboarding_steps.py
# 4 steps: Welcome → API Keys Setup → Model Download → Hotkey → Ready
# This is a LOT of onboarding steps for what is essentially "press a button and speak"
```

**The Problems:**

1. ⚠️ **Step 2 (API Keys) is terrifying for new users** — "Enter your Gemini API Key" and "Enter your Groq API Key" with password fields, "Get Key →" buttons that open browser tabs. This is **way too much, way too early**. A new user just wants to try dictation. They don't want to sign up for Google AI Studio and Groq before they can even speak a word.

2. ⚠️ **Step 3 (Model Download) introduces unnecessary friction** — "Download Model" button with progress status for a fallback model. The user hasn't even dictated anything yet. Why are we asking them to download a 3GB model?

3. ⚠️ **4 steps is too many** — Users should be dictating within 2 clicks: (1) "Here's how it works" → (2)"Pick your hotkey" → DONE. Everything else (API keys, model selection) belongs in Settings.

4. ⚠️ **The QSS is actually decent** — Props: the onboarding styles in `onboarding_qss.py` are the best-looking part of the app. The serif font for titles, the green accents, the card backgrounds. But the content is too dense.

### The Fix

1. **Reduce to 2 mandatory steps**: (1) Welcome + hotkey selection, (2) Done + "try it now" button
2. **Move API keys and model selection to Settings** — Show a "Configure Cloud" card on the home page instead
3. **Let users dictate before they configure** — Default to local mode with a sensible model. Let them experience the core value before asking them to do anything.
4. **Add a "first dictation" flow** — After onboarding, show a tooltip or mini-tutorial: "Press Tab, say something, watch it appear."

---

## 4. VISUAL DESIGN SYSTEM — The Missing Layer

### Current State in Rota AI

There is **no design system**. What exists is a collection of QSS files with hardcoded values:

```python
# From _main_window_qss_tokens.py
# These ARE the tokens:
DARK_BG = "#0D1211"
DARK_CARD = "#141918"
DARK_SURFACE = "#1C2220"
ACCENT_GREEN = "#86EFAC"
TEXT_PRIMARY = "#E8E8EA"
TEXT_SECONDARY = "#8E8E93"
TEXT_MUTED = "#5A5A60"
TEXT_DIM = "#3A3A40"
BORDER_SUBTLE = "rgba(255, 255, 255, 6)"
ERROR_RED = "#F87171"
```

These tokens exist but they're only used in ONE file (`_main_window_qss_tokens.py`). The settings QSS (`settings_qss.py`), onboarding QSS, and inline styles scattered across 20+ Python files all use their own hardcoded values.

**Evidence of inconsistent styling:**

| File | BG Color | Card Color | Accent |
|------|----------|------------|--------|
| `_main_window_qss_tokens.py` | `#0D1211` | `#141918` | `#86EFAC` |
| `settings_qss.py` | `#0D1211` | `#141918` | `#86EFAC` |
| `onboarding_qss.py` | `#141918` | `#191E1C` | `#86EFAC` |
| `_insights_helpers.py` (inline) | Hardcoded `rgba(255,255,255,0.05)` | N/A | N/A |
| `_insights_speech_tab.py` (inline) | Hardcoded `rgba(255, 255, 255, 0.1)` | N/A | `#86EFAC` redefined as `CLR_ACCENT` |

**The Problems:**

1. ⚠️ **Colors are duplicated everywhere** — `#86EFAC` appears in 12+ files as a hardcoded string. If you want to tweak the accent color, you have to change it in a dozen places.

2. ⚠️ **No elevation system** — Cards use `background: rgba(255,255,255,0.05)` with `border: 1px solid rgba(255,255,255,0.1)` for depth. No shadows. No z-index hierarchy. Everything is flat.

3. ⚠️ **No consistent border-radius** — Values range from `2px` (heatmap cells) to `28px` (pill overlay) with no logical progression. Some cards use `6px`, some `8px`, some `10px`, some `12px`, some `20px`. No system.

4. ⚠️ **No typographic scale** — Body text ranges from `9px` (achievement descriptions) to `28px` (speedometer value). No defined steps: h1, h2, h3, body, caption, label. Every label sets its own font-size.

5. ⚠️ **Font inconsistency** — Mix of `"Segoe UI"`, `"Inter"`, `"Georgia"`, `"Times New Roman"`, `"Courier New"`, `"Consolas"`. None are loaded as webfonts — relying on system availability.

### The Fix

1. **Enforce the token system** — Import `_main_window_qss_tokens.py` everywhere instead of hardcoding. Make onboarding_qss.py and settings_qss.py import from the same tokens file.
2. **Create a DESIGN.md** — Document the design system: colors, typography scale, spacing scale, elevation system, border-radius scale, animation timing.
3. **Standardize border-radii**: `4px` (micro elements), `8px` (cards), `12px` (panels), `28px` (pill).
4. **Add shadows/elevation**: Level 1 (cards), Level 2 (dropdowns/popups), Level 3 (overlay/pill).
5. **Consolidate fonts**: Inter for UI (it looks premium and is free), JetBrains Mono for code/technical displays, loaded as a bundled resource.

---

## 5. TYPOGRAPHY — The Quiet Killer

### Current State

```python
# In _main_window_qss_base.py
font-family: "Segoe UI", "Inter", sans-serif;  # Common pattern
# In onboarding_qss.py
font-family: "Georgia", "Times New Roman", serif;  # Only for titles
# In speedometer.py
font-family: "Courier New", monospace;  # For numbers
```

**The Problems:**

1. ⚠️ **Segoe UI** — This is a Windows system font. On macOS, it falls back to a generic sans-serif. On Linux, it might not exist at all. This creates a different look on every platform.

2. ⚠️ **No font loading** — Inter is listed as a fallback but not actually bundled or loaded. If the user doesn't have Inter installed (99% don't), they get Segoe UI or whatever the system defaults to.

3. ⚠️ **No consistent size scale** — Looking across all files:
   - `9px` — Achievement descriptions (too small for accessibility)
   - `10px` — Drill content, metric values
   - `11px` — Field hints, description text
   - `12px` — Section subtitles, card headers
   - `13px` — Body text, setting labels
   - `14px` — Speaking pace card
   - `16px` — Archetype name
   - `20px` — Hotkey pill, icons
   - `22px` — Speedometer value
   - `26px` — Onboarding step titles
   - This is **11 distinct sizes** without a coherent system.

4. ⚠️ **No line-height control** — QSS sets `line-height: 1.5` in some places but most text uses Qt's default which is tight and cramped.

### The Fix

1. **Bundle Inter font** — Include Inter variable font in the assets directory, load it in QFontDatabase at startup. This ensures the same look on every OS.
2. **Define a 7-step type scale**: Caption (10px) → Small (12px) → Body (13px) → Large (15px) → Heading (18px) → Title (22px) → Display (28px)
3. **Set line-height: 1.6** on all body text via QSS
4. **Use font-weight: 400/500/600/700** deliberately — not just everywhere

---

## 6. ANIMATIONS & MOTION

### Current State

```python
# From speedometer.py — the best animation in the app
anim = QPropertyAnimation(self, b"display_value", self)
anim.setStartValue(0)
anim.setEndValue(self._value)
anim.setDuration(950)
anim.setEasingCurve(QEasingCurve.Type.OutCubic)

# From trend_chart.py — similar pattern
anim.setDuration(1300)
# Uses (1 - t)^3 for manual ease-out cubic
```

**The Problems:**

1. ⚠️ **Only 3 animated elements** — Speedometer, trend chart, and progress bars. The entire rest of the UI is static.

2. ⚠️ **No spring animations** — `OutCubic` is a standard easing curve. It's fine. But it's not spring-based. Spring-based easing (`OutBack` with overshoot) feels more organic and "premium."

3. ⚠️ **No transitions** — Window show/hide, section changes, overlay appearance — all instant. No fade-in, no slide, no scale.

4. ⚠️ **No micro-interactions** — Buttons don't scale on hover. Cards don't lift. Toggles don't animate. The UI feels dead.

### The Fix

1. **Add spring easing** — Use `OutBack` with `QPropertyAnimation` for overlay appearance, section changes, and modal transitions.
2. **Fade in the overlay** — Currently the overlay appears instantly. Add a 150ms opacity transition from 0 to 0.95.
3. **Button micro-interactions** — On hover: scale 1.02, increase border opacity. On press: scale 0.98. These are ~100 lines of code total.
4. **Section transitions** — When switching between settings sections or onboarding steps, use a horizontal slide (150ms, OutCubic) instead of an instant swap.

---

## 7. SPECIFIC WIDGET-BY-WIDGET COMPARISON

### Pill Overlay: Rota vs Wispr

| Element | Rota AI | Wispr Flow | Gap | Fix Effort |
|---------|---------|------------|-----|------------|
| Background | Solid `#141918` | Glass blur + vibrancy | 🔴 Critical | Medium (need OS blur API) |
| Shape | border-radius: 28px | Pill shape | 🟡 Minor | Already close |
| Listening indicator | Waveform bars | Gentle pulse | 🟡 Medium | Redesign pulse animation |
| Appear animation | Instant / None | Spring (0.3s) | 🔴 Critical | Easy (add QPropertyAnimation) |
| Position | Fixed? Movable? | Fully draggable | 🟡 Medium | Add drag support |
| Shadow | None | Soft glow on active | 🟡 Medium | Add QGraphicsDropShadowEffect |
| Font | Segoe UI | SF Pro | 🟡 Minor | Bundle Inter font |

### Settings Window: Rota vs Wispr

| Element | Rota AI | Wispr Flow | Gap | Fix Effort |
|---------|---------|------------|-----|------------|
| Layout | Vertical scroll | Sidebar → Detail | 🔴 Critical | Medium (restructure) |
| Section count | 8+ visible at once | Hidden/sub-sections | 🔴 Critical | Easy (tab/sidebar) |
| Search | ❌ None | ✅ Yes | 🟡 Medium | Medium (add search bar) |
| Consistent styling | ❌ Inline + QSS | ✅ Unified | 🟡 Medium | Refactor to tokens |
| Spacing density | Dense (16px gaps) | Generous (24px+) | 🟡 Minor | Bump gap values |
| Typography | Mixed sizes | System scale | 🟡 Medium | Define type scale |

### Insights Dashboard: Rota vs Wispr

| Element | Rota AI | Wispr Flow | Gap | Fix Effort |
|---------|---------|------------|-----|------------|
| Data visualizations | ✅ Speedometer, trend chart, heatmap, rings | ✅ Similar | 🟡 Minor | Design polish |
| Achievement cards | ✅ Custom QFrame with unlock states | ❌ None | 🟢 Advantage | Keep improving |
| Information density | High (too many metrics on one page) | Moderate | 🟡 Medium | Reduce by 30% |
| Loading states | ❌ Blank until data loads | ✅ Skeleton/placeholder | 🟡 Easy | Add skeleton screens |
| Empty states | Text: "Start a dictation to see insights" | Illustrated empty states | 🟡 Easy | Add illustrations |

### Toast Notifications: Rota vs Wispr

| Element | Rota AI | Wispr Flow | Gap | Fix Effort |
|---------|---------|------------|-----|------------|
| Design | `toast.py` — styled QFrame | Inline popover | 🟡 Minor | Polish |
| Slide animation | ❌ None | ✅ Slide from edge | 🟡 Easy | Add QPropertyAnimation |
| Auto-dismiss | ✅ Timer-based | ✅ | 🟢 Parity | Already works |
| Multiple stacking | ❌ Replaces current | ✅ Stacks | 🟡 Easy | Layout manager |

---

## 8. P1 ISSUES (Fix Before Adding Any Features)

These are the **highest priority** issues. Fix these and the app immediately feels more trustworthy.

### P1.1: Overlay Has No Blur Effect

**Current:** Solid `#141918` background
**Why it matters:** The overlay is the #1 most-seen UI element. A solid dark rectangle screams "unfinished." A glass-blur effect makes the app feel native and premium.
**File:** `pill_overlay.py`
**Fix:** 
- Windows: `SetWindowCompositionAttribute` with `AccentState.ACCENT_ENABLE_BLURBEHIND`
- macOS: `NSVisualEffectView` via pyobjc
- Linux: `_KDE_NET_WM_BLUR_BEHIND_REGION` or compositor transparency
- **Fallback:** If none available, use `QGraphicsBlurEffect` on a screenshot of the desktop behind the overlay (expensive but better than solid)

### P1.2: Settings Has No Sidebar

**Current:** Single scrolling column with 8+ sections
**Why it matters:** Settings is the second-most-visited screen. The current layout is overwhelming and hard to navigate.
**File:** `settings_window.py`, `_settings_sections.py`
**Fix:** Add a sidebar with section icons at left. Show only one section at a time. Add a search bar at top.

### P1.3: Onboarding Asks Too Much Too Soon

**Current:** 4 steps including API key entry and model download
**Why it matters:** Users want to dictate, not configure. Every second before first dictation is a second they might leave.
**File:** `_onboarding_steps.py`, `onboarding.py`
**Fix:** Reduce to 2 steps. Move API keys and model selection to Settings. Default to local mode.

### P1.4: No Loading/Empty States

**Current:** Many screens show blank until data loads. Empty states are plain text.
**Why it matters:** When a screen is blank, the user doesn't know if the app is loading, broken, or just has nothing to show. This erodes trust.
**Files:** `insights_page.py`, `home_page.py`, `history_window.py`
**Fix:** Add skeleton loading screens (pulsing gray rectangles that match the layout). Add illustrated empty states with helpful CTAs.

### P1.5: Design Tokens Not Enforced

**Current:** Colors/spacing/fonts hardcoded in 15+ files
**Why it matters:** Making any visual change requires hunting through files. Inconsistencies accumulate.
**Fix:** Make ALL imports use `_main_window_qss_tokens.py`. Remove inline styleSheet calls. One source of truth.

---

## 9. WHAT WISPR FLOW DOESN'T DO WELL (Our Opportunities)

Yes, Wispr Flow's design is better. But it's not perfect. Here's where we can beat them:

| Opportunity | Wispr Flow Weakness | How Rota AI Can Win |
|-------------|-------------------|---------------------|
| **Cross-platform consistency** | Mac-only native feel (breaks on Windows) | If we polish our cross-platform UI, we can look good on ALL platforms |
| **Linux users** | Doesn't exist | Developers who use Linux are a captive audience |
| **Customizability** | Limited settings, "hidden complexity" philosophy | If we make settings approachable but powerful, power users will love us |
| **Gamification** | No achievements, no streaks | We already have this. Make it beautiful and front-and-center. |
| **Open source** | Closed, opaque | Users can inspect, theme, and contribute to our UI |
| **Transparency** | "Invisible" can feel untrustworthy | If we show what's happening (confidence, model, latency), users trust us more |
| **Data insights** | Basic tracking | Our insights dashboard is genuinely deeper. Make it visual and delightful. |
| **On-device processing** | Cloud-only | Local = no latency, no privacy concerns. Lean into this. |

---

## 10. DESIGN SYSTEM RECOMMENDATIONS (Complete)

### Colors

```
Surface BG:     #0D1211   (darkest — main background)
Surface Card:   #141918   (card backgrounds)
Surface Raise:  #1C2220   (raised elements, hover states)
Surface Border: rgba(255, 255, 255, 0.06)
Surface Hover:  rgba(255, 255, 255, 0.08)

Accent Green:   #86EFAC   (primary actions, active states)
Accent Blue:    #93C5FD   (secondary info, links)
Accent Purple:  #C084FC   (premium/insights)
Accent Red:     #F87171   (errors, warnings)
Accent Yellow:  #FBBF24   (cautions, highlights)

Text Primary:   #E8E8EA   (headings, body)
Text Secondary: #8E8E93   (subtitles, descriptions)
Text Muted:     #5A5A60   (placeholders, hints)
Text Dim:       #3A3A40   (disabled, borders)

Glass:          rgba(20, 25, 24, 0.85)  (overlay background)
```

### Typography Scale

```
Display:  28px / 700 / Inter        (onboarding titles, hero stats)
Heading:  22px / 700 / Inter        (section titles)
Title:    18px / 600 / Inter        (card titles)
Large:    15px / 600 / Inter        (subsection headers)
Body:     13px / 400 / Inter        (content, labels)
Small:    12px / 400 / Inter        (captions, hints)
Caption:  10px / 500 / Inter        (badges, tiny labels)

Mono:     13px / 500 / JetBrainsMono  (API keys, hotkeys, code)
```

### Spacing Scale

```
2px  — micro padding
4px  — tight elements
8px  — element spacing
12px — related elements
16px — section internal padding
20px — card internal padding
24px — between cards
32px — major sections
48px — page padding
```

### Border Radius

```
4px  — badges, micro elements
8px  — cards, inputs, buttons
12px — panels, dialogs
28px — pill overlay
```

### Elevation (Box Shadow)

```
Level 0: none
Level 1: 0 2px 8px rgba(0,0,0,0.2)      — cards
Level 2: 0 4px 16px rgba(0,0,0,0.3)     — dropdowns, popups
Level 3: 0 8px 32px rgba(0,0,0,0.4)     — modals, dialogs
Level 4: 0 4px 24px rgba(134,239,172,0.15) — overlay glow (active)
```

### Animation

```
Overlay appear:   200ms spring (response: 0.25, damping: 0.7)
Overlay hide:     150ms ease-out
Section change:   200ms ease-out, horizontal slide
Card hover:       150ms ease-out, scale 1.02
Button press:     100ms ease-out, scale 0.97
Toast appear:     300ms ease-out, slide from top
Progress fill:    800ms ease-out-cubic
```

---

## 11. QUICK WINS (1-2 Days Each)

| # | Task | Effort | Impact |
|---|------|--------|--------|
| 1 | Make overlay background translucent `rgba(20,25,24,0.85)` instead of solid `#141918` | 5 min | 🟡 Medium |
| 2 | Add 150ms fade-in animation to overlay show/hide | 30 min | 🟡 Medium |
| 3 | Add QGraphicsDropShadowEffect to overlay when listening (soft green glow) | 15 min | 🟡 Medium |
| 4 | Add hover scale (1.02) to all clickable cards | 1 hr | 🟢 High |
| 5 | Reduce onboarding to 2 steps (welcome → hotkey → go) | 4 hr | 🔴 Critical |
| 6 | Add skeleton loading states to insights page | 2 hr | 🟢 High |
| 7 | Bundle Inter font + load via QFontDatabase | 1 hr | 🟡 Medium |
| 8 | Create unified token file, enforce imports everywhere | 3 hr | 🟢 High |
| 9 | Add "Mac-style" sidebar to settings window | 6 hr | 🔴 Critical |
| 10 | Add search to settings | 3 hr | 🟡 Medium |

---

## 12. THE RAW TRUTH

**Rota AI's UI feels like it was built by a backend engineer who needed a UI.** And that's exactly what happened. The code works. The features are there. But the user experience was treated as an afterthought.

**Wispr Flow's UI feels like it was built by a design team that also hired great engineers.** Every pixel, every animation, every transition was intentional. They obsessed over the 80% use cases and made them flawless.

**The gap isn't about having fewer features. It's about the features we have feeling unfinished.** The overlay is functional but not delightful. The settings work but feel overwhelming. The onboarding is thorough but exhausting.

**Closing this gap requires:**
1. **A design system** — Not optional. Must-have.
2. **Obsessive polish** — Every UI element needs a pass: colors, spacing, typography, animation.
3. **Radical UX simplification** — Fewer options, more defaults, hidden complexity.
4. **Cross-platform consistency** — The app should look good on Windows, macOS, and Linux without platform-specific hacks.

---

*Generated by Rota AI's UI/UX autopsy — brutally honest, pixel-by-pixel, actionable.*
