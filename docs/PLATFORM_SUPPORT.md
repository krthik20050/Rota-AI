# Platform Support

## Feature Matrix

| Feature | Windows | macOS | Linux (X11) | Linux (Wayland) |
|---------|---------|-------|-------------|-----------------|
| Audio recording | Yes | Yes (PortAudio) | Yes | Yes |
| Hotkey capture | Yes (pynput) | Yes (pynput / Quartz) | Yes (evdev) | Yes (evdev) |
| Cloud transcription | Yes | Yes | Yes | Yes |
| Local transcription (Ollama) | Yes | Yes | Yes | Yes |
| AI cleanup | Yes | Yes | Yes | Yes |
| Text injection | Yes (SendInput) | Yes (AX / Cmd+V fallback) | Yes (xdotool) | Yes (wtype/dotool) |
| Context awareness | Yes (UI Automation) | Partial (Accessibility / AX) | Yes (AT-SPI + xlib) | Partial (AT-SPI + compositor limits) |
| Background audio control | Yes (pycaw/media keys) | Partial (media key / system mute) | Partial (playerctl/pactl) | Partial (playerctl/pactl) |
| System tray | Yes | Yes | Yes | Yes |
| Recording overlay | Yes | Yes | Yes | Yes |
| Voice snippets | Yes | Yes | Yes | Yes |
| Personal dictionary | Yes | Yes | Yes | Yes |
| History (SQLite) | Yes | Yes | Yes | Yes |
| Auto-startup | Yes (registry) | Yes (launchd agent) | Yes (XDG autostart) | Yes (XDG autostart) |
| API key encryption | Yes (DPAPI) | Yes (Keychain via keyring) | Yes (Secret Service via keyring) | Yes (Secret Service via keyring) |
| PyInstaller build | Yes (.exe) | Not yet (CI import/test only) | Yes (AppImage) | Yes (AppImage) |
| Native installer | Yes (Inno Setup) | Not yet (DMG/pkg pending) | No | No |

## Windows

### Supported Versions
- Windows 10 (1903+)
- Windows 11

### Architecture
- x64 only

### Known Limitations
- Some games with anti-cheat may block hotkey capture
- UWP apps may not accept text injection via SendInput (use clipboard mode)
- Windows Sandbox is not supported

## macOS

### Supported Versions
- macOS 13 Ventura+
- Apple Silicon and Intel should work when Python and PortAudio are installed for the same architecture

### Required Permissions
- Accessibility: required for hotkey capture, app focus, and text injection
- Input Monitoring: optional but improves Quartz hotkey reliability
- Automation: may be requested when AppleScript is used for Cmd+V fallback

### Known Limitations
- There is no committed DMG/pkg packaging flow yet; macOS CI currently validates imports and tests only.
- Direct AX text insertion is app-dependent. The injector falls back to clipboard paste and then character typing.
- Sandboxed App Store apps may reject Accessibility or paste-based injection.
- Background media pause uses the macOS media key, which can toggle the active player if the app reports state poorly.
- First-run dependency installation requires Homebrew for PortAudio when running from source.

## Linux

### Supported Distributions
- Ubuntu 20.04+
- Debian 11+
- Fedora 35+
- Arch Linux / Manjaro
- Pop!_OS

### Desktop Environments
- GNOME (best supported)
- KDE Plasma
- XFCE
- Sway (Wayland)
- Hyprland (Wayland)

### Architecture
- x86_64
- aarch64 (ARM64)

### Known Limitations
- Wayland: xdotool does not work. Requires wtype, dotool, or ydotool.
- Some tiling window managers may not support the recording overlay.
- AT-SPI accessibility must be enabled for context awareness.
- Flatpak/Snap versions of apps may not accept text injection.

### Required System Packages

**Ubuntu/Debian:**
```bash
sudo apt install libportaudio2 portaudio19-dev libdbus-glib-1-dev \
  at-spi2-core xvfb xdotool wl-clipboard python3-pyatspi ffmpeg fuse libfuse2
```

**Fedora:**
```bash
sudo dnf install portaudio-devel dbus-glib-devel at-spi2-core \
  xdotool wl-clipboard python3-pyatspi ffmpeg fuse
```

**Arch:**
```bash
sudo pacman -S portaudio dbus-glib at-spi2-core xdotool wl-clipboard \
  python-pyatspi ffmpeg fuse2
```

### User Groups

For hotkey capture (evdev), your user must be in the `input` group:
```bash
sudo usermod -aG input $USER
# Log out and back in
```

For audio access, your user should be in the `audio` group:
```bash
sudo usermod -aG audio $USER
```
