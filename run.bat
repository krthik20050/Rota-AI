@echo off
REM ============================================================================
REM Rota AI - Self-Updating Launcher (single file you can double-click)
REM ============================================================================
REM HOW TO USE
REM   A) Leave this file inside the repo folder — nothing to configure.
REM   B) Shortcut on Desktop: right-click this file -> Send to -> Desktop (shortcut).
REM   C) Copy this file to Desktop only: edit ROTA_REPO_OVERRIDE below (one line).
REM CLICK AGAIN while Rota runs: brings the window forward (does not start a second copy).
REM ============================================================================
setlocal enabledelayedexpansion

title Rota AI - Launcher

REM --- Configuration ---------------------------------------------------------
REM If this copy lives OUTSIDE the repo (e.g. Desktop), set your clone path here:
REM   Example:  set "ROTA_REPO_OVERRIDE=D:\projects codes\rota ai"
REM Leave empty when run.bat sits next to the app\ folder.
set "ROTA_REPO_OVERRIDE="

set "REPO_DIR=%~dp0"
if not "!ROTA_REPO_OVERRIDE!"=="" (
    set "ROTA_AI_HOME=!ROTA_REPO_OVERRIDE!"
)
if defined ROTA_AI_HOME (
    if exist "!ROTA_AI_HOME!\desktop\app\main.py" (
        set "REPO_DIR=!ROTA_AI_HOME!\"
    ) else (
        echo [WARN] ROTA_AI_HOME set but desktop\app\main.py not found:
        echo        !ROTA_AI_HOME!
        echo        Using launcher folder instead ^(!REPO_DIR!^)
    )
)

set "VENV_DIR=%REPO_DIR%.venv"
set "REQ_FILE=%REPO_DIR%requirements.txt"
set "HASH_FILE=%VENV_DIR%\.req_hash"

REM --- Move to repo root -----------------------------------------------------
pushd "%REPO_DIR%"
if not exist "desktop\app\main.py" (
    echo [ERROR] desktop\app\main.py not found in !REPO_DIR!
    echo         Edit ROTA_REPO_OVERRIDE near the top of this file ^(see REM instructions^),
    echo         or use a shortcut to run.bat inside your repo folder.
    goto :fail
)

echo.
echo ============================================
echo           R O T A   A I
echo        Self-Updating Launcher
echo ============================================
echo.

REM ============================================================================
REM 1. PREFLIGHT - Find python (try python, then py -3, then py)
REM ============================================================================
set "PY="

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY=python"
    goto :py_found
)

py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY=py -3"
    goto :py_found
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY=py"
    goto :py_found
)

echo [ERROR] Python is not installed or not in PATH.
echo         Install Python 3.10+: https://python.org/downloads
echo         IMPORTANT: Check "Add Python to PATH" during install.
goto :fail

:py_found
for /f "tokens=*" %%v in ('%PY% --version 2^>^&1') do echo       Found: %%v

where git >nul 2>&1
if %errorlevel% neq 0 (
    echo       [WARN] git not found. Skipping auto-update.
    goto :skip_pull
)

REM ============================================================================
REM 2. AUTO-UPDATE - Pull latest from current branch
REM ============================================================================
echo [1/4] Checking for updates...

set "BRANCH="
for /f "tokens=*" %%b in ('git rev-parse --abbrev-ref HEAD 2^>nul') do set "BRANCH=%%b"
if not defined BRANCH (
    echo       [WARN] Not a git repo or detached HEAD. Skipping.
    goto :skip_pull
)

git fetch origin >nul 2>&1
if %errorlevel% neq 0 (
    echo       Offline. Skipping update.
    goto :skip_pull
)

set "LOCAL_HEAD="
set "REMOTE_HEAD="
for /f "tokens=*" %%i in ('git rev-parse HEAD 2^>nul') do set "LOCAL_HEAD=%%i"
for /f "tokens=*" %%i in ('git rev-parse "origin/!BRANCH!" 2^>nul') do set "REMOTE_HEAD=%%i"

if not defined REMOTE_HEAD (
    echo       No remote tracking for !BRANCH!. Skipping.
    goto :skip_pull
)

if "!LOCAL_HEAD!"=="!REMOTE_HEAD!" (
    echo       Already up to date.
) else (
    echo       Pulling latest on !BRANCH!...
    git pull --ff-only origin !BRANCH! >nul 2>&1
    if !errorlevel! equ 0 (
        echo       Updated successfully.
    ) else (
        echo       Local changes ahead of remote — skipping update.
    )
)

:skip_pull

REM ============================================================================
REM 3. VIRTUAL ENVIRONMENT
REM ============================================================================
echo [2/4] Setting up virtual environment...

REM If venv dir exists but activate.bat is missing, it's broken. Nuke it.
if exist "%VENV_DIR%" (
    if not exist "%VENV_DIR%\Scripts\activate.bat" (
        echo       Broken venv detected. Removing...
        rmdir /s /q "%VENV_DIR%" 2>nul
    )
)

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo       Creating virtual environment...
    %PY% -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo.
        echo [ERROR] Failed to create virtual environment.
        echo.
        echo Diagnostic info:
        %PY% --version
        %PY% -m ensurepip --version 2>nul
        if !errorlevel! neq 0 (
            echo       ensurepip is missing. Try reinstalling Python with
            echo       the "pip" option checked, or run:
            echo         %PY% -m ensurepip --upgrade
        )
        echo.
        echo You can also try manually:
        echo   %PY% -m venv "%VENV_DIR%"
        goto :fail
    )
    echo       Done.
) else (
    echo       Using existing venv.
)

call "%VENV_DIR%\Scripts\activate.bat"

REM WHY: After activate, PATH prefers venv -- but %PY% may still be "py -3", which
REM      uses the global launcher and IGNORES the venv. That yields missing deps
REM      and instant exit. Always run the venv interpreter explicitly.
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
if not exist "%VENV_PYTHON%" (
    echo.
    echo [ERROR] venv python.exe missing at:
    echo         %VENV_PYTHON%
    echo         Remove "%VENV_DIR%" and run this launcher again.
    goto :fail
)

REM ============================================================================
REM 4. DEPENDENCY SYNC
REM ============================================================================
echo [3/4] Syncing dependencies...

if not exist "%REQ_FILE%" (
    echo       [WARN] requirements.txt not found.
    goto :launch
)

call :check_deps
goto :launch

REM --- Subroutine: check and install deps ------------------------------------
:check_deps
set "REQ_HASH="
for /f "skip=1 delims=" %%h in ('certutil -hashfile "%REQ_FILE%" MD5 2^>nul') do (
    if not defined REQ_HASH set "REQ_HASH=%%h"
)
set "CACHED_HASH="
if exist "%HASH_FILE%" set /p CACHED_HASH=<"%HASH_FILE%"

if "!REQ_HASH!"=="!CACHED_HASH!" (
    echo       Dependencies unchanged. Skipping.
    goto :eof
)

echo       Installing dependencies (this may take a minute)...
pip install -r "%REQ_FILE%" --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo       [WARN] pip install had errors. App may not work correctly.
    goto :eof
)
echo !REQ_HASH!>"%HASH_FILE%"
echo       Done.
goto :eof

REM ============================================================================
REM 5. LAUNCH
REM ============================================================================
:launch
echo [4/4] Launching Rota AI...
echo.

REM WHY: PYTHONPATH must include desktop/ so package imports resolve
REM      (from audio.x, from ai.x, from injection.x, from ui.x, etc.)
set "PYTHONPATH=%REPO_DIR%desktop;%PYTHONPATH%"

REM --- Single-instance check (runs SYNCHRONOUSLY so this CMD window keeps ---
REM     foreground focus when AllowSetForegroundWindow is called, ensuring  ---
REM     the running instance can actually call SetForegroundWindow later).  ---
echo       Checking for existing instance...
"%VENV_PYTHON%" -c "import sys,socket,ctypes;s=socket.socket();s.settimeout(1.0);s.connect(('127.0.0.1',47201));ctypes.windll.user32.AllowSetForegroundWindow(0xFFFFFFFF);s.sendall(b'ROTA_WAKE_MAIN\n');s.shutdown(2);s.close()" 2>nul
if %errorlevel% equ 0 (
    echo       Rota is already running ^(window brought forward^).
    echo       If the window does not appear, check the system tray.
    echo.
    echo =============================================
    goto :done
)

echo       Rota is starting. This launcher will close automatically.
echo       If the app window does not appear, check the system tray.
echo       Logs: %APPDATA%\RotaAI\rota.log
echo.
echo =============================================

REM WHY: "start """ launches Python as a detached process so this CMD window
REM      can exit immediately. The Qt window then appears in the foreground
REM      without the CMD console sitting on top of it.
start "" "%VENV_PYTHON%" -u "%REPO_DIR%desktop\app\main.py"

:done
popd
endlocal
exit /b 0

:fail
echo.
popd
pause
endlocal
