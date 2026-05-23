import sys
from pathlib import Path

if __name__ == "__main__":
    desktop_dir = Path(__file__).resolve().parent / "desktop"
    if str(desktop_dir) not in sys.path:
        sys.path.insert(0, str(desktop_dir))
    import runpy
    runpy.run_path(str(desktop_dir / "app" / "main.py"), run_name="__main__")
    raise SystemExit(0)
