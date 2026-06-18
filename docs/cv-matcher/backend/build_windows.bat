@echo off
setlocal enabledelayedexpansion
title CV Matcher — Compilation Windows (.exe)
color 0A

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   CV Matcher — Build Windows EXE (Mode IA Locale)   ║
echo  ╚══════════════════════════════════════════════════════╝
echo.
echo  Ce logiciel fonctionne 100%% en local avec Ollama.
echo  Aucune cle API requise. Vos donnees ne quittent jamais votre PC.
echo.

:: ── Vérification Python ──────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] Python introuvable.
    echo           Installez Python 3.11+ depuis https://python.org
    echo           Cochez "Add Python to PATH" pendant l'installation.
    echo.
    pause & exit /b 1
)
for /f "tokens=2" %%v in ('python --version') do set PY_VER=%%v
echo  [OK] Python %PY_VER% detecte.
echo.

:: ── Environnement virtuel ────────────────────────────────────────────────────
if not exist .venv (
    echo  [1/5] Creation de l'environnement virtuel...
    python -m venv .venv
) else (
    echo  [1/5] Environnement virtuel existant.
)
call .venv\Scripts\activate.bat

:: ── Installation des dependances ────────────────────────────────────────────
echo.
echo  [2/5] Installation des dependances Python (~2-3 minutes)...
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet
echo       OK.

:: ── Nettoyage ────────────────────────────────────────────────────────────────
echo.
echo  [3/5] Nettoyage de l'ancien build...
if exist dist  rmdir /s /q dist
if exist build rmdir /s /q build
echo       OK.

:: ── Compilation PyInstaller ──────────────────────────────────────────────────
echo.
echo  [4/5] Compilation de l'executable (5-10 minutes)...
pyinstaller cv_matcher.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo  [ERREUR] La compilation a echoue. Verifiez les erreurs ci-dessus.
    pause & exit /b 1
)

:: ── Post-traitement ──────────────────────────────────────────────────────────
echo.
echo  [5/5] Finalisation...

:: Dossier uploads
if not exist dist\CVMatcher\uploads mkdir dist\CVMatcher\uploads

:: Fichier .env par defaut (mode Ollama local)
if not exist dist\CVMatcher\.env (
    echo AI_PROVIDER=ollama                          > dist\CVMatcher\.env
    echo API_KEY=ollama                             >> dist\CVMatcher\.env
    echo API_BASE_URL=http://localhost:11434/v1     >> dist\CVMatcher\.env
    echo AI_MODEL=gemma3:4b                         >> dist\CVMatcher\.env
    echo OLLAMA_BASE_URL=http://localhost:11434     >> dist\CVMatcher\.env
)

:: Raccourci batch de lancement
echo @echo off                                        > "dist\CVMatcher\Lancer CV Matcher.bat"
echo start "" "%%~dp0CVMatcher.exe"                  >> "dist\CVMatcher\Lancer CV Matcher.bat"

:: ── Resultat ─────────────────────────────────────────────────────────────────
echo.
if exist dist\CVMatcher\CVMatcher.exe (
    echo  ╔══════════════════════════════════════════════════════╗
    echo  ║              BUILD TERMINE AVEC SUCCES !             ║
    echo  ╠══════════════════════════════════════════════════════╣
    echo  ║  Executable : dist\CVMatcher\CVMatcher.exe           ║
    echo  ╠══════════════════════════════════════════════════════╣
    echo  ║  AVANT DE LANCER L'APPLICATION :                     ║
    echo  ║                                                      ║
    echo  ║  1) Installez Ollama : https://ollama.com            ║
    echo  ║  2) Ouvrez un terminal et tapez :                    ║
    echo  ║       ollama pull gemma3:4b                          ║
    echo  ║     (ou llama3.2 / mistral / phi4 / qwen2.5)        ║
    echo  ║  3) Double-cliquez sur CVMatcher.exe                 ║
    echo  ║                                                      ║
    echo  ║  DISTRIBUER : zippez tout le dossier dist\CVMatcher\ ║
    echo  ╚══════════════════════════════════════════════════════╝
) else (
    echo  [ERREUR] CVMatcher.exe non trouve — build echoue.
)

echo.
pause
endlocal
