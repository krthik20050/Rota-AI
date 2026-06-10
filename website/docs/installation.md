---
title: Installation
---

Rota AI is distributed as a lightweight desktop application with native builds for Windows, macOS, and Linux. No cloud accounts, registration, or subscriptions are required to run the application.

### Windows Installation

1. **Download**: Obtain the latest executable setup (`RotaAI-Setup.exe`) from the official website or [GitHub Releases](https://github.com/krthik20050/Rota-AI/releases).
2. **Execution**: Double-click `RotaAI-Setup.exe`.
3. **SmartScreen Warning**: Because the installer is signed with a self-generated developer certificate, Windows SmartScreen may display a warning:
   - Click **"More Info"**.
   - Click **"Run anyway"**.
4. **Setup Process**: The installer will install Rota AI directly into your local user directory:
   ```
   %LOCALAPPDATA%\Programs\RotaAI\
   ```
   *Note: Administrator privileges are not required for this installation path.*
5. **Autostart**: The installer will register Rota AI in your Startup registry key:
   ```
   HKCU\Software\Microsoft\Windows\CurrentVersion\Run
   ```
6. **Microphone Permissions**: Windows 10/11 requires permission for desktop applications to access your microphone. If transcription fails on launch, verify this in:
   - *Settings > Privacy & security > Microphone* (Ensure "Let desktop apps access your microphone" is toggled ON).

### macOS Installation

1. **Download**: Download the Apple Silicon or Intel variant (`RotaAI-macOS.zip` / `RotaAI-macOS-x64.zip`).
2. **Decompress**: Double-click the ZIP archive to extract `RotaAI.app`.
3. **Move to Applications**: Drag `RotaAI.app` to your `/Applications` directory.
4. **Gatekeeper Bypass (First Run)**: Because the app is not currently signed and notarized via an active Apple Developer ID program, double-clicking it normally will show a warning: *"RotaAI.app is damaged and can’t be opened."* or *"macOS cannot verify the developer..."*
   - To bypass, **Right-click / Control-click** on `RotaAI.app` in the Applications folder and choose **Open**.
   - In the security dialog that appears, click **Open**. macOS will cache this exception.
5. **System Permissions**: Rota AI requires two system permissions to function:
   - **Accessibility**: Needed to intercept the global hotkey (F9) and inject text into the active app.
   - **Microphone**: Needed to capture the audio stream.
   *Both prompts will appear on launch. If missed, enable them manually under System Settings > Privacy & Security.*

### Linux Installation

1. **Download**: Download the portable AppImage: `RotaAI.AppImage`.
2. **Permit Execution**: Open a terminal and grant execution rights:
   ```bash
   chmod +x RotaAI.AppImage
   ```
3. **Execute**: Double-click the file or run it via terminal:
   ```bash
   ./RotaAI.AppImage
   ```
4. **Integration**: If you want system-wide desktop integration (.desktop shortcut):
   - Move the AppImage to `~/.local/bin/` or `/usr/local/bin/`.
   - Create a desktop entry at `~/.local/share/applications/rota-ai.desktop` pointing to the AppImage path.
5. **Wayland Support**: For Wayland compositors (GNOME, Sway, Hyprland), ensure `wtype` or `dotool` is installed on your host system:
   ```bash
   # Ubuntu/Debian
   sudo apt install wtype

   # Fedora
   sudo dnf install wtype

   # Arch Linux
   sudo pacman -S wtype
   ```
