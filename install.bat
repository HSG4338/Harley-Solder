@echo off
setlocal enabledelayedexpansion
title HARLEY SOLDER — INSTALLER

:: ============================================================
::  HARLEY SOLDER — INSTALL SCRIPT
::  Windows 10/11 — Build 0.9.1-UNSTABLE
:: ============================================================

color 0A
cls

echo.
echo  ============================================================
echo   H A R L E Y   S O L D E R   ^|^|   I N S T A L L E R
echo  ============================================================
echo   Build 0.9.1-UNSTABLE ^| Windows Setup
echo  ============================================================
echo.

timeout /t 1 /nobreak >nul

:: ── STEP 1: Check Python ──────────────────────────────────────
echo  [01/08]  Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [FAIL]  Python not found in PATH.
    echo.
    echo          Please install Python 3.10 or newer:
    echo          https://www.python.org/downloads/
    echo.
    echo          IMPORTANT: Check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK]    Python %PYVER% found.

:: Check minimum version (3.10)
for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
    set PYMAJ=%%a
    set PYMIN=%%b
)
if %PYMAJ% LSS 3 (
    echo  [FAIL]  Python 3.10+ required. Found %PYVER%.
    pause
    exit /b 1
)
if %PYMAJ% EQU 3 if %PYMIN% LSS 10 (
    echo  [WARN]  Python 3.10+ recommended. Found %PYVER%. Proceeding anyway...
)

timeout /t 1 /nobreak >nul

:: ── STEP 2: Check pip ─────────────────────────────────────────
echo  [02/08]  Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo  [FAIL]  pip not found. Attempting to install...
    python -m ensurepip --upgrade
    if errorlevel 1 (
        echo  [FAIL]  Could not install pip. Please install manually.
        pause
        exit /b 1
    )
)
echo  [OK]    pip found.

timeout /t 1 /nobreak >nul

:: ── STEP 3: Upgrade pip ───────────────────────────────────────
echo  [03/08]  Upgrading pip...
python -m pip install --upgrade pip --quiet
echo  [OK]    pip up to date.

timeout /t 1 /nobreak >nul

:: ── STEP 4: Install PyQt6 ────────────────────────────────────
echo  [04/08]  Installing PyQt6 (GUI framework)...
python -m pip install PyQt6 --quiet
if errorlevel 1 (
    echo  [FAIL]  PyQt6 installation failed.
    echo          Try manually: pip install PyQt6
    pause
    exit /b 1
)
echo  [OK]    PyQt6 installed.

timeout /t 1 /nobreak >nul

:: ── STEP 5: Optional — Pillow (asset generator) ───────────────
echo  [05/08]  Installing Pillow (eye asset generator)...
python -m pip install Pillow --quiet
if errorlevel 1 (
    echo  [WARN]  Pillow not installed. generate_assets.py will not work.
    echo          Harley will use procedural eye rendering as fallback.
) else (
    echo  [OK]    Pillow installed.
)

timeout /t 1 /nobreak >nul

:: ── STEP 6: Optional — Anthropic SDK ─────────────────────────
echo  [06/08]  Checking Anthropic SDK (optional, for live AI)...
python -c "import anthropic" >nul 2>&1
if errorlevel 1 (
    echo  [SKIP]  Anthropic SDK not installed.
    echo          To enable live Claude API:
    echo            pip install anthropic
    echo          Then set use_anthropic_api=true in config/config.json
) else (
    echo  [OK]    Anthropic SDK found.
)

timeout /t 1 /nobreak >nul

:: ── STEP 7: Create assets directory ──────────────────────────
echo  [07/08]  Checking assets directory...
if not exist "assets\eyes" (
    mkdir "assets\eyes"
    echo  [OK]    Created assets\eyes\
) else (
    echo  [OK]    assets\eyes\ exists.
)

:: Count existing assets
set ASSET_COUNT=0
for %%f in (assets\eyes\*.png assets\eyes\*.webp) do set /a ASSET_COUNT+=1

if %ASSET_COUNT% EQU 0 (
    echo  [INFO]  No eye assets found. Generating placeholders...
    python generate_assets.py
    if errorlevel 1 (
        echo  [WARN]  Asset generation failed. Procedural fallback will be used.
    ) else (
        echo  [OK]    Placeholder eye assets generated.
    )
) else (
    echo  [OK]    Found %ASSET_COUNT% existing eye asset(s^).
)

timeout /t 1 /nobreak >nul

:: ── STEP 8: Verify core modules ───────────────────────────────
echo  [08/08]  Verifying core modules...
python -c "
import sys
errors = []
modules = [
    ('main', 'main.py'),
    ('config.settings', 'config/settings.py'),
    ('communication', 'communication/__init__.py'),
    ('cli_boot.boot_sequence', 'cli_boot/boot_sequence.py'),
    ('ai_core.chat_loop', 'ai_core/chat_loop.py'),
    ('emotion_engine.emotion_state', 'emotion_engine/emotion_state.py'),
    ('ui.eye_window', 'ui/eye_window.py'),
    ('ui.eye_widget', 'ui/eye_widget.py'),
    ('ui.glitch_renderer', 'ui/glitch_renderer.py'),
    ('ui.pulse_system', 'ui/pulse_system.py'),
    ('ui.asset_manager', 'ui/asset_manager.py'),
]
for mod, path in modules:
    try:
        with open(path) as f: pass
        print(f'  OK    {path}')
    except FileNotFoundError:
        print(f'  MISS  {path}')
        errors.append(path)
if errors:
    print(f'  FAIL  {len(errors)} file(s) missing')
    sys.exit(1)
else:
    print('  OK    All core files present')
"
if errorlevel 1 (
    echo.
    echo  [FAIL]  Some files are missing. Re-extract the zip and retry.
    pause
    exit /b 1
)

:: ── DONE ──────────────────────────────────────────────────────
echo.
echo  ============================================================
echo   INSTALLATION COMPLETE
echo  ============================================================
echo.
echo   To launch Harley Solder:
echo     python main.py
echo.
echo   To run system checkup:
echo     python checkup.py
echo.
echo   To generate eye assets manually:
echo     python generate_assets.py
echo.
echo  ============================================================
echo.
set /p LAUNCH="  Launch Harley Solder now? [Y/N]: "
if /i "%LAUNCH%"=="Y" (
    echo.
    echo  Starting...
    python main.py
)

endlocal
pause
