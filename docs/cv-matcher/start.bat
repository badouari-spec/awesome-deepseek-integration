@echo off
title CV Matcher — IA Locale
cd /d "%~dp0"

echo.
echo  ╔═══════════════════════════════════════╗
echo  ║   CV Matcher — Matching de CV par IA  ║
echo  ║   Mode 100%% local avec Ollama         ║
echo  ╚═══════════════════════════════════════╝
echo.

:: ── Vérifier Python ──────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  Python n'est pas installe.
    echo  Telechargez-le sur : https://www.python.org/downloads/
    echo  Cochez "Add Python to PATH" lors de l'installation.
    echo.
    pause
    exit /b
)

:: ── Lancer l'application ─────────────────────────────────────────────────────
python run.py

echo.
echo  Le serveur s'est arrete.
pause
