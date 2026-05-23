@echo off
REM ============================================================
REM  Rota AI - Build Windows distributable
REM  Output: dist\RotaAI\RotaAI.exe  (one-dir bundle)
REM  Run from the repo root after activating the venv.
REM ============================================================
setlocal enabledelayedexpansion

set "ROOT=%~dp0"
set "VENV=%ROOT%.venv"
set "DIST=%ROOT%dist\RotaAI"

echo.
echo ============================================================
echo    Rota AI Build
echo ============================================================
echo.

REM --- Activate venv -------------------------------------------
if not exist "%VENV%\Scripts\activate.bat" (
    echo [ERROR] venv not found at %VENV%
    echo         Run run.bat first to create the venv, then re-run this.
    goto :fail
)
call "%VENV%\Scripts\activate.bat"

REM --- Install PyInstaller if missing --------------------------
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/3] Installing PyInstaller...
    pip install pyinstaller --quiet
    if !errorlevel! neq 0 goto :fail
) else (
    echo [1/3] PyInstaller already installed.
)

REM --- Build ---------------------------------------------------
echo [2/3] Building RotaAI.exe ...
echo       This may take several minutes on first build.
echo.

cd /d "%ROOT%"
pyinstaller rota-ai.spec --clean --noconfirm

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed. Check the output above.
    goto :fail
)

REM --- Report --------------------------------------------------
echo.
echo [3/3] Done.
echo.
if exist "%DIST%\RotaAI.exe" (
    echo   Output: %DIST%\RotaAI.exe
    for %%f in ("%DIST%") do echo   Size:   %%~zf bytes ^(folder^)
    echo.
    echo   To distribute: zip the entire dist\RotaAI\ folder.
    echo   Users extract it anywhere and double-click RotaAI.exe
) else (
    echo [WARN] RotaAI.exe not found in expected location.
    echo        Check dist\ folder manually.
)

REM --- Inno Setup (optional) -----------------------------------
echo.
echo Checking for Inno Setup...
set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe"       set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"

if not defined ISCC (
    echo       Inno Setup not found — skipping installer creation.
    echo       Install from: https://jrsoftware.org/isdl.php
    echo       Then re-run this script to build RotaAI-Setup.exe
    goto :done
)

echo       Building installer with Inno Setup...
if not exist "%ROOT%installer-output" mkdir "%ROOT%installer-output"
"%ISCC%" "%ROOT%installer.iss"
if !errorlevel! equ 0 (
    echo.
    echo   Installer: %ROOT%installer-output\RotaAI-Setup.exe
) else (
    echo   [WARN] Inno Setup compilation had errors.
)

goto :done
:fail
echo.
pause
exit /b 1
:done
echo ============================================================
pause
endlocal
