---
title: Building Releases
---

Rota AI uses **PyInstaller** to compile the Python source code, Qt files, and Whisper model libraries into a single, executable native application.

---

### Windows Build & Installer Compilation

#### 1. Setup PyInstaller
Activate your virtual environment and run PyInstaller with the spec file:
```bash
pip install pyinstaller
pyinstaller RotaAI.spec
```
This outputs a standalone folder structure at `dist/RotaAI/` containing the compiled binary assets.

#### 2. Create the Setup Installer (Inno Setup)
To compile the standalone folder into a single `RotaAI-Setup.exe` wizard:
1. Install [Inno Setup 6](https://jrsoftware.org/isinfo.php).
2. Right-click `installer.iss` in the root directory and select **Compile Script**.
3. The setup executable will be written to `/dist/`.

---

### macOS Application Bundling
To create the macOS `.app` bundle:
1. Run PyInstaller on macOS:
   ```bash
   pyinstaller RotaAI-macOS.spec
   ```
2. Compress the output for distribution:
   ```bash
   cd dist
   zip -r RotaAI-macOS.zip RotaAI.app
   ```

---

### Linux AppImage Compilation
To build a portable Linux AppImage:
1. Execute the build-linux helper script:
   ```bash
   chmod +x scripts/build-linux.sh
   ./scripts/build-linux.sh
   ```
2. This script retrieves `appimagetool`, bundles Python and PortAudio libraries, gathers the desktop shortcut configurations, and writes `RotaAI-x86_64.AppImage` to the output folder.
