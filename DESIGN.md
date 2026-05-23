# Rota AI Design System

## Aesthetic Vision
A visual clone of Wispr Flow. Dark, minimal, premium, and native-feeling. The signature element is the recording overlay with an animated waveform that responds to voice amplitude in real time. It uses glassmorphism techniques (semi-transparent blurred backgrounds) to blend seamlessly with the user's current context.

## Color Palette
- **Background (Overlay):** `rgba(20, 20, 20, 0.85)` (Dark gray with 85% opacity, simulating a frosted glass effect).
- **Background (Settings/History):** `#1E1E1E` (Solid dark gray for standard dialogs).
- **Surface (Inputs/Cards):** `#2A2A2A`
- **Border/Divider:** `#333333`
- **Text (Primary):** `#FFFFFF` (100% white for high contrast readability).
- **Text (Secondary/Muted):** `#A0A0A0`
- **Accent (Active Recording):** `#FFFFFF` (Waveform bars are pure white against the dark glass).
- **Accent (Success/Saved):** `#4CAF50`
- **Accent (Error/Warning):** `#F44336`

## Typography
- **Font Family:** `Segoe UI Variable`, `Inter`, or system default sans-serif.
- **Sizes:**
  - **Headers:** 16pt (Settings/History Dialog titles)
  - **Primary Text:** 12pt (Transcribed text preview, buttons)
  - **Secondary Text:** 10pt (Labels, hints, timestamps)
- **Weights:** Regular (400) for body, Semi-bold (600) for headers and active states.

## Component Specs

### 1. Recording Overlay
- **Dimensions:** Frameless, approx 400px width, 100px height. Positioned near the bottom-center of the active screen, or trailing the text cursor if possible.
- **Background:** Frameless window with `Qt.WA_TranslucentBackground`. The main widget uses the glassmorphism color `rgba(20, 20, 20, 200)`.
- **Border Radius:** 16px.
- **Shadow:** Soft drop shadow (10px blur, `rgba(0,0,0,100)`).
- **Waveform Animation:**
  - 24 vertical bars.
  - Bar Width: 4px.
  - Bar Gap: 4px.
  - Minimum Height: 4px.
  - Maximum Height: 60px.
  - Color: `#FFFFFF`.
  - Animation Physics: Smooth interpolation (spring physics or low-pass filter) between the current height and the target RMS amplitude.

### 2. Settings Window
- **Layout:** Fixed size dialog (e.g., 450x500px).
- **Structure:**
  - Top header ("Rota AI Settings")
  - Tabbed or vertical list navigation (General, Audio, Hotkey, AI, About)
  - Controls: Dark-themed toggle switches, minimal dropdowns, borderless input fields with subtle bottom borders.
- **Style:** Dark mode standard (QSS applied).

### 3. Toast Notifications
- **Dimensions:** Approx 300px width, 50px height.
- **Position:** Bottom-right or top-right of the screen.
- **Background:** `#2A2A2A` with 8px border radius.
- **Animation:** Slide up/in, fade out after 3 seconds.

### 4. History Panel
- **Layout:** List view of the last 200 transcriptions.
- **Items:** Two lines per item (Timestamp in secondary text, snippet in primary text).
- **Search:** Sticky search bar at the top with a magnifying glass icon.