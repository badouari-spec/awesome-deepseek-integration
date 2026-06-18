@echo off
chcp 65001 >nul
:: ═══════════════════════════════════════════════════════════════
::  AEJ CV MATCHER PRO — BUILD .EXE WINDOWS  (MODE OLLAMA LOCAL)
::  Agence Emploi Jeunes / Agence Prestige — KEITA
:: ═══════════════════════════════════════════════════════════════
::  A LANCER SUR UN PC WINDOWS (le .exe ne peut etre genere que
::  sur Windows). Double-cliquez simplement sur ce fichier.
:: ═══════════════════════════════════════════════════════════════
title AEJ CV Matcher - Construction du .exe
echo.
echo  ============================================================
echo    AEJ CV MATCHER PRO - Construction du logiciel Windows
echo    Mode 100%% LOCAL - Ollama - Aucune cle API requise
echo  ============================================================
echo.

:: 1) Verifier Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERREUR] Python introuvable.
    echo  Installez Python 3.11+ : https://www.python.org/downloads/
    echo  IMPORTANT : cochez "Add Python to PATH" pendant l'installation.
    pause & exit /b 1
)
echo  [OK] Python detecte.
echo.

:: 2) Mettre a jour pip + installer les dependances (sans Google)
echo  Installation des dependances (2-4 minutes)...
python -m pip install --upgrade pip --quiet
pip install -r requirements_local.txt --quiet
if %errorlevel% neq 0 (
    echo  [ERREUR] Echec d'installation des dependances.
    pause & exit /b 1
)
echo  [OK] Dependances installees.
echo.

:: 3) Construire le .exe via le fichier .spec
echo  Compilation du .exe en cours (3-7 minutes, ne pas fermer)...
echo.
pyinstaller AEJ_CV_Matcher.spec --noconfirm

if %errorlevel% equ 0 (
    echo.
    echo  ============================================================
    echo    BUILD REUSSI !
    echo  ============================================================
    echo.
    echo    Votre logiciel se trouve dans :
    echo        dist\AEJ_CV_Matcher\AEJ_CV_Matcher.exe
    echo.
    echo    POUR DISTRIBUER : copiez TOUT le dossier
    echo        dist\AEJ_CV_Matcher\
    echo    sur n'importe quel PC Windows (aucune installation requise).
    echo.
    echo    AVANT DE LANCER LE LOGICIEL :
    echo      1. Installez Ollama : https://ollama.com
    echo      2. Dans un terminal : ollama pull gemma3:4b
    echo         (autres modeles : llama3.2 / mistral / phi4:14b)
    echo      3. Double-cliquez sur AEJ_CV_Matcher.exe
    echo      - Pour les CV scannes : installez aussi Tesseract OCR.
    echo  ============================================================
    echo.
    explorer dist\AEJ_CV_Matcher
) else (
    echo.
    echo  [ERREUR] La compilation a echoue. Lisez les messages ci-dessus.
)
pause
