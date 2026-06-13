@echo off
title DeepSeek CV Matcher
cd /d "%~dp0"

:: ── Vérifier Python ──────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Python n'est pas installe sur ce PC.
    echo.
    echo  Telechargez Python sur : https://www.python.org/downloads/
    echo  Cochez bien "Add Python to PATH" pendant l'installation.
    echo.
    pause
    exit /b
)

:: ── Lancer l'application ─────────────────────────────────────────────────────
python run.py

:: ── Si le serveur s'arrête, attendre avant de fermer ────────────────────────
echo.
echo  Le serveur est arrêté.
pause
