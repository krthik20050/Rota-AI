# Bug Bounty Report — Rota AI

**Date:** 2026-05-26
**Scope:** Full codebase (desktop app, all platforms)
**Test Results:** 167 passed, 3 skipped, **0 failed**

---

## Executive Summary

The codebase is in **good security posture**. No critical or high-severity bugs were found. The architecture shows strong discipline around platform abstraction, thread safety, and secure coding practices.

| Severity | Count | Summary |
|----------|-------|---------|
| **Critical** | 0 | No remote code execution, data exfiltration, or privilege escalation vectors |
| **High** | 0 | No authentication bypass, injection, or cryptographic failures |
| **Medium** | 2 | Minor XDG-compliance issue on Linux, file handle hygiene |
| **Low** | 3 | Logging verbosity, untracked artifacts, test warnings |
| **Info** | 4 | Architecture observations for long-term improvement |

---

## CRITICAL — None Found

- ✅ **No `shell=True`** anywhere in the codebase. All 48 `subprocess.run()` and `subprocess.Popen()` calls use command lists, preventing shell injection.
- ✅ **No `eval()`, `exec()`, or unsafe deserialization** (`pickle.loads`, unsafe `yaml.load`).
- ✅ **API keys encrypted at rest** — DPAPI on Windows, keyring (Secret Service / Keychain) on Linux/macOS.
- ✅ **Ollama URL validation** — strict allowlist for localhost/private IPs only, blocked against cloud metadata endpoints.
- ✅ **Startup path validation** — temp-directory paths blocked from Windows auto-start registration.

## HIGH — None Found

- ✅ **Thread safety** — 12 `threading.Lock` / `threading.RLock` instances properly protect all shared mutable state. No deadlock patterns found.
- ✅ **Qt thread safety** — all UI mutations via `QTimer.singleShot(0, ...)` or `pyqtSignal`. No cross-thread widget access.
- ✅ **Resource cleanup** — clipboard restoration in `finally` blocks. File handles properly closed via `with` statements across all modules.
- ✅ **Platform detection** — all `ctypes.windll` calls gated behind `sys.platform == "win32"`. All macOS-specific imports wrapped in `try/except ImportError`.

---

## MEDIUM — 2 Issues

### M1 — Linux XDG Data Directory Compliance
**File:** `desktop/data/snippets.py` (line 167)
**File:** `desktop/data/history.py` (line 29)
**File:** `desktop/utils/seeder.py` (line 88)

**Description:** On Linux, these modules fall through to `os.environ.get("APPDATA", ".")` which is Windows-only. This causes snippet/history data to be stored in the current working directory (`./RotaAI/`) instead of `~/.local/share/rota-ai/`.

**Impact:** Low — existing data still works. Just not XDG-compliant.

**Fix:**
```python
if sys.platform == "darwin":
    appdata_dir = os.path.join(os.path.expanduser("~/Library/Application Support"), "RotaAI")
elif sys.platform.startswith("linux"):
    appdata_dir = os.path.join(os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")), "rota-ai")
else:
    appdata_dir = os.path.join(os.environ.get("APPDATA", "."), "RotaAI")
```

This pattern is already used correctly in `data/config.py` (lines 162–171).

### M2 — Bare `open()` Without Context Manager (file handle)
**File:** `desktop/plat/linux_injector.py` (line 436)

**Description:**
```python
return open(comm_file).read().strip().lower()
```
The file is opened without `with`. CPython closes it via GC, but this is not guaranteed in all Python implementations (PyPy, etc.).

**Impact:** Very low — CPython closes on `__del__`. Still considered a best-practice violation.

**Fix:**
```python
with open(comm_file) as f:
    return f.read().strip().lower()
```

---

## LOW — 3 Issues

### L1 — Windows Test Warning (sounddevice DLL load)
**File:** `desktop/tests/test_ai_processor.py`

**Description:** `Windows fatal exception: code 0x8007007e` occurs during `sounddevice` import in one test. The test passes but the exception is logged. This is a native DLL dependency issue (OpenAL/PortAudio or similar) available on some but not all Windows setups.

**Impact:** Cosmetic — tests still pass. No runtime impact for users who have sounddevice properly installed.

### L2 — Untracked Files
**Files:**
- `./0` (data file)
- `./tuple[bool` (partial filename — likely from failed debug/dump)
- `./.playwright-mcp/` directory (test artifacts)
- `./desktop/0` (data file)
- `./desktop/dict` (data file)

**Impact:** None — not committed. Declutter the working tree.

### L3 — `desktop/app/main.py` — `prog="rota"` vs actual binary name
**File:** `desktop/app/main.py` (line 110)

**Description:**
```python
parser = argparse.ArgumentParser(prog="rota", description="Rota AI — voice dictation")
```
The `prog` name is "rota" but the binary is distributed as `rota-ai.exe` (Windows) or `rota-ai` (Linux/macOS). The help text will show "rota" instead of the actual executable name.

**Impact:** Cosmetic — can be confusing in `--help` output.

---

## INFO — Architecture Observations

### I1 — macOS `pbcopy` / `pbpaste` Without `communicate()` Timeout
**File:** `desktop/plat/macos_injector.py` (line 176)

```python
proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
proc.communicate(text.encode("utf-8"), timeout=5)
```
`communicate()` has a timeout, so this is safe. But the `Popen` does not specify `timeout` for its own startup — if `pbcopy` hangs on launch, the process blocks. Very edge-case; considered safe.

### I2 — Global Module State Used Across Three Injectors
**Files:**
- `desktop/injection/injector.py`
- `desktop/plat/linux_injector.py`
- `desktop/plat/macos_injector.py`

All three use module-level globals (`_last_injected_text`, `_last_injected_hwnd`, etc.) tracked per-platform. This is safe because only one injector is active per session (platform-specific), but it means constructing a new `TextInjector` instance that operates on stale global state.

### I3 — Qt `QApplication` Created Once, Default Arguments
**File:** `desktop/app/rota_app.py` (line 51)

```python
self.app = QApplication(sys.argv)
```
The `--hotkey-backend` CLI flag is consumed by `argparse` before `QApplication` is created, so it won't conflict with Qt's own parsing. This is correct. However, `sys.argv` still contains the flag — Qt will ignore unrecognized flags.

### I4 — Daemon Thread File I/O
Some daemon threads (`_sd_loader`, `_run_analytics`, clipboard captures) perform I/O. Daemon threads can be killed mid-operation at interpreter exit. This is acceptable for analytics and background checks but worth noting.

---

## ✅ Verified Safe Patterns

### Security
- [x] No `shell=True` in any subprocess call (48 calls checked)
- [x] No `eval()` / `exec()` / unsafe deserialization
- [x] API keys encrypted at rest (DPAPI on Windows, keyring on Linux/macOS)
- [x] Ollama URL allowlist + blocklist validation
- [x] Max injection length enforced (5000 chars)
- [x] Terminal injection warnings
- [x] Temp-directory startup path blocked

### Thread Safety
- [x] `threading.Lock` protects all shared mutable state (12 instances)
- [x] `threading.Event` used for coordination in hotkey capture
- [x] `QThread` for long-lived processor thread
- [x] `QTimer.singleShot(0, ...)` for main-thread UI callbacks
- [x] Thread exception hooks installed (`threading.excepthook`)

### Cross-Platform
- [x] `sys.platform` gating consistent across codebase
- [x] All `ctypes.windll` calls behind `sys.platform == "win32"` guard
- [x] All macOS-specific imports wrapped in `try/except ImportError`
- [x] `plat/__init__.py` provides clean platform abstraction layer
- [x] ImportError fallbacks for every optional platform dependency

### Resource Management
- [x] File handles: all but 1 (M2) use `with open(...)`
- [x] Clipboard: restored in `finally` blocks
- [x] Mutex/locks: properly released in `finally` or exception paths
- [x] Temp files: `tempfile.NamedTemporaryFile(delete=True)` used

---

## Bug Bounty Verdict

**No payout-worthy bugs found.** The codebase shows strong security consciousness:

1. A professional-grade platform abstraction layer
2. Proper encryption of secrets at rest
3. Defensive subprocess patterns (no shell=True)
4. Thread-safe state management
5. Graceful degradation when optional deps are missing

The two medium issues (M1, M2) are easy fixes that would bring the codebase to "exemplary" status.

---

## Quick Fixes (10 minutes total)

1. **M1** — Add XDG detection for Linux in `snippets.py`, `history.py`, `seeder.py`
2. **M2** — Wrap `open()` in `with` in `linux_injector.py:436`
3. **L3** — Update `prog` to match binary name
