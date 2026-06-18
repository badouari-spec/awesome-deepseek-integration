@echo off
chcp 65001 >nul
title AEJ CV Matcher PRO — IA Locale
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║   AEJ CV MATCHER PRO  v2.0  — ÉDITION PRESTIGE          ║
echo  ║   Agence Emploi Jeunes / Agence Prestige — Abidjan       ║
echo  ║   Mode 100%% local — Ollama — Aucune clé API requise      ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

:: ── Vérifier Python ───────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] Python introuvable.
    echo  Téléchargez Python 3.11+ sur : https://www.python.org/downloads/
    echo  IMPORTANT : cochez "Add Python to PATH" lors de l'installation.
    echo.
    pause
    exit /b 1
)

:: ── Vérifier Ollama ───────────────────────────────────────────────
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo  [ATTENTION] Ollama ne semble pas lancé.
    echo.
    echo  Assurez-vous que :
    echo    1. Ollama est installé  : https://ollama.com
    echo    2. Ollama est en cours  : lancez "ollama serve" dans un terminal
    echo    3. Un modèle est chargé : ollama pull gemma3:4b
    echo.
    echo  Le logiciel va quand même démarrer — configurez Ollama depuis
    echo  l'onglet "Configuration" puis cliquez "Tester".
    echo.
    timeout /t 4 >nul
)

:: ── Installer les dépendances (1ère fois seulement) ───────────────
if not exist ".installed" (
    echo  [1/2] Installation des dépendances Python (~2 minutes, une seule fois)...
    python -m pip install --upgrade pip --quiet
    pip install -r requirements_local.txt --quiet
    if errorlevel 1 (
        echo  [ERREUR] Echec installation. Verifiez votre connexion internet.
        pause & exit /b 1
    )
    echo. > .installed
    echo  [OK] Installation terminée.
    echo.
)

:: ── Lancer l'application ──────────────────────────────────────────
echo  [2/2] Lancement du logiciel...
echo.
python AEJ_CV_Matcher.py

echo.
echo  Le logiciel s'est fermé.
pause
