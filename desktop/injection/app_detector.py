import ctypes
import ctypes.wintypes
from dataclasses import dataclass

from utils.log import get_logger

logger = get_logger(__name__)

try:
    import psutil
except ImportError:
    psutil = None
    logger.warning("psutil not available; process detection disabled")


@dataclass
class AppContext:
    app_name: str = ""
    process_name: str = ""
    category: str = "other"
    tone: str = "neutral"


# lowercase stem (no .exe) → category
_PROCESS_CATEGORY: dict[str, str] = {
    # Browsers
    "chrome": "browser",
    "firefox": "browser",
    "msedge": "browser",
    "brave": "browser",
    "opera": "browser",
    "vivaldi": "browser",
    "iexplore": "browser",
    # Editors / IDEs
    "code": "editor",
    "cursor": "editor",
    "sublime_text": "editor",
    "notepad++": "editor",
    "atom": "editor",
    "notepad": "editor",
    "wordpad": "editor",
    "nvim": "editor",
    "vim": "editor",
    "emacs": "editor",
    "pycharm64": "editor",
    "idea64": "editor",
    "clion64": "editor",
    "webstorm64": "editor",
    # Terminals
    "cmd": "terminal",
    "powershell": "terminal",
    "pwsh": "terminal",
    "wt": "terminal",
    "bash": "terminal",
    "mintty": "terminal",
    "conhost": "terminal",
    "alacritty": "terminal",
    "windowsterminal": "terminal",
    # Chat / Comms
    "slack": "chat",
    "discord": "chat",
    "teams": "chat",
    "telegram": "chat",
    "signal": "chat",
    "zoom": "chat",
    "skype": "chat",
    "mattermost": "chat",
    "whatsapp": "chat",
    # Email
    "outlook": "email",
    "thunderbird": "email",
    "postbox": "email",
    "mailbird": "email",
    # Office
    "winword": "office",
    "excel": "office",
    "powerpnt": "office",
    "onenote": "office",
    # Notes
    "obsidian": "notes",
    "notion": "notes",
    "logseq": "notes",
    "evernote": "notes",
    # Media
    "vlc": "media",
    "spotify": "media",
    "mpv": "media",
}

# category → dictation tone hint
_CATEGORY_TONE: dict[str, str] = {
    "browser": "neutral",
    "editor": "technical",
    "terminal": "technical",
    "chat": "casual",
    "email": "formal",
    "office": "formal",
    "notes": "neutral",
    "media": "neutral",
    "other": "neutral",
}


def _get_window_title(hwnd: int) -> str:
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value


def _get_pid(hwnd: int) -> int | None:
    pid = ctypes.wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value if pid.value else None


def _process_name_from_pid(pid: int) -> str:
    if psutil is None:
        return ""
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return ""


def _classify(process_name: str) -> tuple[str, str]:
    stem = process_name.lower().removesuffix(".exe")
    category = _PROCESS_CATEGORY.get(stem, "other")
    tone = _CATEGORY_TONE.get(category, "neutral")
    return category, tone


def get_active_app() -> AppContext:
    """
    Returns AppContext for the current foreground window.
    Never raises — returns empty AppContext on any failure.
    """
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return AppContext()

        app_name = _get_window_title(hwnd)
        pid = _get_pid(hwnd)
        process_name = _process_name_from_pid(pid) if pid else ""
        category, tone = _classify(process_name)

        logger.debug(
            "active_app_detected",
            extra={
                "app_name": app_name,
                "process_name": process_name,
                "category": category,
                "tone": tone,
            },
        )
        return AppContext(
            app_name=app_name,
            process_name=process_name,
            category=category,
            tone=tone,
        )
    except Exception:
        logger.warning("active_app_detection_failed", exc_info=True)
        return AppContext()


if __name__ == "__main__":
    import time

    print("Detecting active window every 2 seconds. Switch windows to test.")
    for _ in range(5):
        ctx = get_active_app()
        print(
            f"  app_name={ctx.app_name!r:40s} "
            f"process={ctx.process_name!r:20s} "
            f"category={ctx.category:12s} "
            f"tone={ctx.tone}"
        )
        time.sleep(2)
