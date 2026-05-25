# Troubleshooting

## Linux

### "Cannot access keyboard devices" / Hotkey doesn't work

**Symptom:** Rota starts but pressing F9 (or your hotkey) does nothing.

**Cause:** Your user is not in the `input` group, or the group change hasn't taken effect yet.

**Fix (try in order):**

```bash
# Option 1: Quick fix for current session (no logout needed)
newgrp input
# Then launch Rota from the same terminal:
bash linux/run.sh

# Option 2: Permanent fix (requires logout)
sudo usermod -aG input $USER
# Log out and log back in, then:
bash linux/run.sh

# Option 3: Verify you're in the group
groups | grep input
# Should show: ... audio input ...
```

### "No keyboard devices found" even after joining input group

**Symptom:** Error says no keyboards were found.

**Fix:**

```bash
# Check if /dev/input/event* exists
ls /dev/input/event*

# Check permissions
ls -la /dev/input/event*
# Should show: crw-rw---- 1 root input ...

# Verify your groups
id | grep input

# If you just joined input, you need to re-login or run:
newgrp input
```

### App crashes on startup with Qt/display errors

**Symptom:** `qt.qpa.plugin: Could not load the Qt platform plugin`

**Fix:**

```bash
# Install missing Qt system libraries
sudo apt-get install -y \
  libxcb-xinerama0 libxkbcommon0 libegl1 libgl1 \
  libfontconfig1 libdbus-1-3 libx11-xcb1 libxcb-glx0 \
  libxcb-keysyms1 libxcb-image0 libxcb-shm0 libxcb-icccm4 \
  libxcb-sync1 libxcb-xfixes0 libxcb-shape0 libxcb-randr0 \
  libxcb-render-util0

# If running on a headless server, use offscreen mode:
export QT_QPA_PLATFORM=offscreen
bash linux/run.sh
```

### "PermissionError: [Errno 13] Permission denied: /dev/input/event0"

**Cause:** The `input` group exists but your current session doesn't have it yet.

**Fix:**

```bash
# Immediate fix without logout:
newgrp input

# Or check if the group was actually added:
cat /etc/group | grep input
# Should show: input:x:107:yourusername
```

### Text injection doesn't work (Wayland)

**Symptom:** Transcription works but text doesn't appear in the target app.

**Cause:** On Wayland, xdotool doesn't work. Rota needs `wtype`, `dotool`, or `ydotool`.

**Fix:**

```bash
# Install one of these:
sudo apt install xdotool        # X11 only
# OR for Wayland:
pip install wtype               # or build from source
# OR:
sudo apt install dotool         # works on both X11 and Wayland

# Verify which session type you're running:
echo $XDG_SESSION_TYPE
# x11 → xdotool works
# wayland → need wtype/dotool/ydotool
```

### AppImage doesn't start

**Symptom:** `AppImage` won't execute or shows FUSE errors.

**Fix:**

```bash
# Make it executable
chmod +x RotaAI.AppImage

# If FUSE is not available, extract and run:
./RotaAI.AppImage --appimage-extract
./squashfs-root/AppRun
```

### Audio recording doesn't work

**Symptom:** No audio captured when speaking.

**Fix:**

```bash
# Check if microphone is detected
pactl list sources short
# or: arecord -l

# Check if PortAudio is installed
python3 -c "import sounddevice; print(sounddevice.query_devices())"

# Install PortAudio if missing:
sudo apt install libportaudio2 portaudio19-dev
```

### "ModuleNotFoundError: No module named 'evdev'"

**Fix:**

```bash
pip install evdev
# or:
pip install -r linux/requirements-linux.txt
```

## Windows

### Rota doesn't start / binary not found error

**Symptom:** `run.bat` says Python is not found.

**Fix:**

```powershell
# Install Python 3.12+ from https://python.org
# Make sure to check "Add Python to PATH" during installation
# Then run run.bat again
```

### Hotkey doesn't register

**Symptom:** F9 does nothing.

**Fix:**
- Another app may be blocking the hotkey. Try changing it in onboarding.
- Check if Rota has keyboard permissions in Windows Settings → Privacy → Keyboard
- Try running as Administrator

### Antivirus flags RotaAI.exe

**Symptom:** Windows Defender or antivirus quarantines the built executable.

**Fix:** This is a false positive common with PyInstaller-packaged Python apps. Add an exclusion in your antivirus, or build from source:
```
git clone https://github.com/krthik20050/Rota-AI.git
cd Rota-AI
run.bat
```

### "pywin32 not found" error

**Fix:**

```powershell
pip install pywin32
```
