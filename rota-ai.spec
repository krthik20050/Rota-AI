# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Rota AI
# Build: pyinstaller rota-ai.spec

import sys
from pathlib import Path

ROOT = Path(SPECPATH)
DESKTOP = ROOT / "desktop"

block_cipher = None

a = Analysis(
    [str(ROOT / "desktop" / "app" / "main.py")],
    pathex=[str(DESKTOP)],
    binaries=[],
    datas=[
        # Desktop sub-packages
        (str(DESKTOP / "ai"),        "ai"),
        (str(DESKTOP / "audio"),     "audio"),
        (str(DESKTOP / "data"),      "data"),
        (str(DESKTOP / "injection"), "injection"),
        (str(DESKTOP / "services"),  "services"),
        (str(DESKTOP / "ui"),        "ui"),
        (str(DESKTOP / "utils"),     "utils"),
        (str(DESKTOP / "assets"),    "assets"),
        # .env template (user fills in API keys)
        (str(ROOT / ".env.example") if (ROOT / ".env.example").exists() else str(ROOT / "requirements.txt"), "."),
    ],
    hiddenimports=[
        # pynput / keyboard system hooks
        "pynput.keyboard._win32",
        "pynput.mouse._win32",
        "pynput._util.win32",
        "keyboard",
        # PyQt6 essentials
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.QtMultimedia",
        # sounddevice
        "sounddevice",
        "_sounddevice_data",
        # pywin32
        "win32api",
        "win32con",
        "win32gui",
        "win32process",
        "pywintypes",
        # torch
        "torch",
        "torch.nn",
        "torch.jit",
        # faster-whisper / ctranslate2
        "faster_whisper",
        "ctranslate2",
        # audio / misc
        "pydub",
        "pyperclip",
        "pyautogui",
        "structlog",
        "noisereduce",
        "dotenv",
        "groq",
        "psutil",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude CUDA to keep size manageable (CPU-only build)
        "torch.cuda",
        "torch.backends.cuda",
        "torch.backends.cudnn",
        # Dev / test only
        "pytest",
        "IPython",
        "notebook",
        "matplotlib",
        # Large unused stdlib
        "tkinter",
        "unittest",
        "xml.etree",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="RotaAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no console window for end users
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(DESKTOP / "assets" / "icon.ico"),
    version_file=None,
    uac_admin=False,        # don't force UAC — most features work without admin
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="RotaAI",
)
