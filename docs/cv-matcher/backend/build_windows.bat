@echo off
setlocal enabledelayedexpansion
title DeepSeek CV Matcher - Build

echo.
echo  ===================================================
echo   DeepSeek CV Matcher  ^|  Windows Build Script
echo  ===================================================
echo.

:: ── Check Python ─────────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found.
    echo          Install Python 3.11+ from https://python.org
    echo          Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version') do set PY_VER=%%v
echo  Python %PY_VER% found.
echo.

:: ── Create virtual environment ────────────────────────────────────────────────
if not exist .venv (
    echo  [1/5] Creating virtual environment...
    python -m venv .venv
) else (
    echo  [1/5] Virtual environment already exists.
)

call .venv\Scripts\activate.bat

:: ── Install dependencies ──────────────────────────────────────────────────────
echo.
echo  [2/5] Installing dependencies (this may take a few minutes)...
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet
echo       Done.

:: ── Clean previous build ──────────────────────────────────────────────────────
echo.
echo  [3/5] Cleaning previous build...
if exist dist   rmdir /s /q dist
if exist build  rmdir /s /q build
echo       Done.

:: ── Run PyInstaller ───────────────────────────────────────────────────────────
echo.
echo  [4/5] Building executable with PyInstaller...
pyinstaller cv_matcher.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo  [ERROR] PyInstaller failed. See errors above.
    pause
    exit /b 1
)

:: ── Post-build setup ──────────────────────────────────────────────────────────
echo.
echo  [5/5] Finalizing output...

:: Copy .env template next to the .exe
copy ..\  .env.example  dist\CVMatcher\.env.example >nul 2>&1
copy ..\.env.example  dist\CVMatcher\.env.example >nul 2>&1

:: Create empty uploads folder
if not exist dist\CVMatcher\uploads mkdir dist\CVMatcher\uploads

:: Create a starter .env if it doesn't exist
if not exist dist\CVMatcher\.env (
    echo DEEPSEEK_API_KEY=sk-your-key-here  > dist\CVMatcher\.env
    echo DEEPSEEK_MODEL=deepseek-chat       >> dist\CVMatcher\.env
)

:: Create a launch shortcut batch (optional helper)
echo @echo off                                     > dist\CVMatcher\Start CVMatcher.bat
echo start "" "%%~dp0CVMatcher.exe"               >> dist\CVMatcher\Start CVMatcher.bat

:: ── Summary ───────────────────────────────────────────────────────────────────
echo.
if exist dist\CVMatcher\CVMatcher.exe (
    echo  ===================================================
    echo   BUILD SUCCESSFUL!
    echo  ===================================================
    echo.
    echo   Output folder : dist\CVMatcher\
    echo   Executable    : dist\CVMatcher\CVMatcher.exe
    echo.
    echo   BEFORE RUNNING:
    echo   1. Open  dist\CVMatcher\.env
    echo   2. Replace  sk-your-key-here  with your DeepSeek API key
    echo      Get one at: https://platform.deepseek.com
    echo.
    echo   OR enter the API key directly in the app window after launch.
    echo.
    echo   TO DISTRIBUTE: zip the entire  dist\CVMatcher\  folder.
    echo  ===================================================
) else (
    echo  [ERROR] Build failed — CVMatcher.exe not found.
)

echo.
pause
endlocal
