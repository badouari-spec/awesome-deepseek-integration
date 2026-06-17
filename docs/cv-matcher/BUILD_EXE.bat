@echo off
chcp 65001 >nul
title CV Matcher Web — Build EXE

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║   CV MATCHER WEB — CONSTRUCTION DU LOGICIEL STANDALONE      ║
echo  ║   Génère : dist\CV_Matcher\CV_Matcher.exe                   ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

:: ── 1. Python ─────────────────────────────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERREUR] Python introuvable.
    echo  Installez Python 3.11+ sur https://www.python.org
    echo  IMPORTANT : cochez "Add Python to PATH"
    pause & exit /b 1
)
echo  [OK] Python détecté.
echo.

:: ── 2. Dépendances + PyInstaller ──────────────────────────────────────────────
echo  [1/3]  Installation des dépendances...
python -m pip install --upgrade pip --quiet
pip install -r backend\requirements.txt --quiet
pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo  [ERREUR] Échec installation des dépendances.
    pause & exit /b 1
)
echo  [OK] Dépendances prêtes.
echo.

:: ── 3. Build PyInstaller ──────────────────────────────────────────────────────
echo  [2/3]  Compilation du logiciel (5-10 minutes)...
echo         Ne fermez pas cette fenêtre.
echo.
pyinstaller cv_matcher.spec --noconfirm --clean

if %errorlevel% neq 0 (
    echo.
    echo  [ERREUR] La compilation a échoué. Lisez les messages ci-dessus.
    pause & exit /b 1
)

:: ── 4. Résultat ───────────────────────────────────────────────────────────────
echo.
echo  [3/3]  Nettoyage...
if exist build rmdir /s /q build >nul 2>&1
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                  BUILD RÉUSSI !                             ║
echo  ╠══════════════════════════════════════════════════════════════╣
echo  ║  Logiciel :  dist\CV_Matcher\CV_Matcher.exe                 ║
echo  ║                                                              ║
echo  ║  POUR DISTRIBUER : copiez TOUT le dossier                   ║
echo  ║      dist\CV_Matcher\                                        ║
echo  ║  sur n'importe quel PC Windows.                             ║
echo  ║                                                              ║
echo  ║  PRÉREQUIS SUR LE PC CIBLE :                                ║
echo  ║    1. Installer Ollama : https://ollama.com                  ║
echo  ║    2. Dans un terminal : ollama pull gemma3:4b               ║
echo  ║    3. Double-cliquer sur CV_Matcher.exe                      ║
echo  ║       → Le navigateur s'ouvre automatiquement               ║
echo  ║       → Aucun Python ni dépendance requis                   ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

set /p OPEN="  Ouvrir le dossier de sortie ? (O/N) : "
if /i "%OPEN%"=="O" explorer dist\CV_Matcher

pause
