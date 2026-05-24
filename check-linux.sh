#!/usr/bin/env bash
# Quick health check for Linux port -- run AFTER setup-linux.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/.venv/bin/activate"

python3 -c "
import sys
sys.path.insert(0, '${SCRIPT_DIR}/desktop')

from plat import get_hotkey_handler, get_injector, get_window_detector, get_field_reader, get_app_detector

print('=== Rota AI Linux Health Check ===')
print()

# --- Imports ---
print('[Imports]')
HotkeyHandler = get_hotkey_handler()
TextInjector = get_injector()
wd = get_window_detector()
print(f'  HotkeyHandler: {HotkeyHandler.__module__}.{HotkeyHandler.__name__}')
print(f'  TextInjector:  {TextInjector.__module__}.{TextInjector.__name__}')
print(f'  WindowDetect:  {wd.__name__}')
print()

# --- Config ---
from data.config import ConfigManager, _IS_LINUX
print('[Config]')
print(f'  IS_LINUX: {_IS_LINUX}')
tmp = '/tmp/rota-ai-test-config.json'
cfg = ConfigManager(config_path=tmp)
print(f'  Config path: {cfg.config_path}')
print(f'  Config dir exists: {__import__(\"os\").path.exists(__import__(\"os\").path.dirname(cfg.config_path))}')
print()

# --- Secrets ---
from plat.linux_secrets import encrypt_secret, decrypt_secret
enc = encrypt_secret('test')
dec = decrypt_secret(enc)
print('[Secrets]')
print(f'  encrypt: {enc}')
print(f'  decrypt: {dec}')
print()

# --- Startup ---
from plat.linux_startup import register_startup, unregister_startup, is_startup_enabled
register_startup('/usr/bin/python3')
print('[Startup]')
print(f'  registered: {is_startup_enabled()}')
unregister_startup()
print(f'  unregistered: {not is_startup_enabled()}')
print()

# --- Session detection ---
from plat.linux_injector import detect_session_type
session = detect_session_type()
print('[Session]')
print(f'  Type: {session.value}')
print(f'  WAYLAND_DISPLAY: {__import__(\"os\").environ.get(\"WAYLAND_DISPLAY\", \"(not set)\")}')
print(f'  XDG_SESSION_TYPE: {__import__(\"os\").environ.get(\"XDG_SESSION_TYPE\", \"(not set)\")}')
print(f'  DISPLAY: {__import__(\"os\").environ.get(\"DISPLAY\", \"(not set)\")}')
print()

# --- Tools ---
import shutil
print('[Tools]')
for tool in ['wl-copy', 'wl-paste', 'xdotool', 'xclip', 'ydotool', 'wtype', 'dotool', 'ffmpeg']:
    found = shutil.which(tool)
    status = 'OK' if found else 'NOT FOUND'
    print(f'  {tool}: {status}')
print()

# --- evdev ---
print('[evdev]')
try:
    import evdev
    devices = evdev.list_devices()
    keyboards = [d for d in devices if evdev.ecodes.EV_KEY in evdev.InputDevice(d).capabilities()]
    print(f'  Input devices: {len(devices)}')
    print(f'  Keyboards: {len(keyboards)}')
except Exception as e:
    print(f'  evdev error: {e}')
print()

# --- AT-SPI ---
print('[AT-SPI]')
try:
    import pyatspi
    desktop = pyatspi.Registry.getDesktop(0)
    print(f'  AT-SPI available: True')
    print(f'  Desktop apps: {desktop.childCount}')
except Exception as e:
    print(f'  AT-SPI available: False ({e})')
print()

print('=== Health Check Complete ===')
" 2>&1
