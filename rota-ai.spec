# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Rota AI
# Build: pyinstaller rota-ai.spec

import sys
import re
from pathlib import Path

ROOT = Path(SPECPATH)
DESKTOP = ROOT / "desktop"
VERSION_FILE = DESKTOP / "app" / "version.py"
IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")

APP_VERSION = "1.0.0"
if VERSION_FILE.exists():
    match = re.search(
        r'__version__\s*=\s*["\']([^"\']+)["\']',
        VERSION_FILE.read_text(encoding="utf-8"),
    )
    if match:
        APP_VERSION = match.group(1)

common_hiddenimports = [
    # PyQt6 essentials
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
    "PyQt6.QtMultimedia",
    # sounddevice
    "sounddevice",
    "_sounddevice_data",
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
    # Dynamic platform factory imports
    "plat",
]

platform_hiddenimports = []
if IS_WINDOWS:
    platform_hiddenimports = [
        # pynput / keyboard system hooks
        "pynput.keyboard._win32",
        "pynput.mouse._win32",
        "pynput._util.win32",
        "keyboard",
        # pywin32
        "win32api",
        "win32con",
        "win32gui",
        "win32process",
        "pywintypes",
    ]
elif IS_MACOS:
    platform_hiddenimports = [
        "pynput.keyboard._darwin",
        "pynput.mouse._darwin",
        "pynput._util.darwin",
        "AppKit",
        "ApplicationServices",
        "Quartz",
        "objc",
        "keyring",
        "plat.macos_hotkey",
        "plat.macos_injector",
        "plat.macos_instance_guard",
        "plat.macos_setup",
        "plat.macos_startup",
        "plat.macos_window",
    ]
elif IS_LINUX:
    platform_hiddenimports = [
        "evdev",
        "keyring",
        "Xlib",
        "plat.linux_hotkey",
        "plat.linux_injector",
        "plat.linux_secrets",
        "plat.linux_startup",
        "plat.linux_window",
    ]

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
        (str(DESKTOP / "plat"),      "plat"),
        (str(DESKTOP / "services"),  "services"),
        (str(DESKTOP / "ui"),        "ui"),
        (str(DESKTOP / "utils"),     "utils"),
        (str(DESKTOP / "assets"),    "assets"),
        # .env template (user fills in API keys)
        (str(ROOT / ".env.example") if (ROOT / ".env.example").exists() else str(ROOT / "requirements.txt"), "."),
    ],
    hiddenimports=common_hiddenimports + platform_hiddenimports,
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
    icon=str(DESKTOP / "assets" / "icon.ico") if IS_WINDOWS else None,
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

if IS_MACOS:
    app = BUNDLE(
        coll,
        name="RotaAI.app",
        icon=str(DESKTOP / "assets" / "icon.icns")
        if (DESKTOP / "assets" / "icon.icns").exists()
        else None,
        bundle_identifier="com.rotaai.app",
        info_plist={
            "CFBundleName": "Rota AI",
            "CFBundleDisplayName": "Rota AI",
            "CFBundleShortVersionString": APP_VERSION,
            "CFBundleVersion": APP_VERSION,
            "NSMicrophoneUsageDescription": "Rota AI records microphone audio for dictation.",
            "NSAppleEventsUsageDescription": "Rota AI uses Apple Events to paste dictated text into the active app.",
            "NSHumanReadableCopyright": "Copyright Rota AI contributors",
            "LSMinimumSystemVersion": "13.0",
        },
    )
