---
title: Platform Abstraction
---

Rota AI features a robust cross-platform codebase. Platform-specific API calls (like writing to the Windows registry vs. macOS plist, or capturing keys on Linux wayland vs. Windows DLLs) are completely abstract behind a common interface in the `plat/` module.

Code outside the `plat/` directory is 100% OS-agnostic.

---

### The Abstraction Gateway (`plat/__init__.py`)
On startup, the system imports `sys.platform` and exposes factory functions that dynamically import and return the appropriate OS-specific classes.

```python
import sys

IS_LINUX = sys.platform.startswith("linux")
IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

def get_hotkey_handler():
    if IS_LINUX:
        from plat.linux_hotkey import HotkeyHandler
        return HotkeyHandler
    elif IS_MACOS:
        from plat.macos_hotkey import HotkeyHandler
        return HotkeyHandler
    else:
        from audio.hotkey import HotkeyHandler
        return HotkeyHandler
```

---

### Platform Implementation Map

| System API | Windows (`win32`) | macOS (`darwin`) | Linux (`linux`) |
|------------|-------------------|------------------|-----------------|
| **Hotkey Capture** | Low-Level Hook (`WH_KEYBOARD_LL` via `pynput`) | Quartz CGEventTap (`CoreGraphics` wrapper) | `/dev/input/*` event monitoring (`evdev` library) |
| **Active App Query** | Win32 API (`GetForegroundWindow` + UI Automation) | Cocoa API (`NSWorkspace` + `AXUIElement`) | X11/Wayland API (`xdotool` / AT-SPI hooks) |
| **Text Injection** | Win32 virtual keyboard driver events (`SendInput`) | Accessibility API writes or macOS Clipboard paste | `wtype` (Wayland) / `xdotool` (X11) / Clipboard paste |
| **Credential Storage** | Data Protection API (`win32crypt` DPAPI) | Apple Keychain Service (`keyring` module) | Secret Service / GNOME Keyring (`keyring` module) |
| **Auto-Startup** | Registry key `Run` under `HKCU` | LaunchAgent plist (`~/Library/LaunchAgents/`) | XDG Autostart shortcut (`~/.config/autostart/`) |
| **Single-Instance** | Win32 Named Mutex | POSIX file lock (`fcntl`) | POSIX socket-bind binding |
