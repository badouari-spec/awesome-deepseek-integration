@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title AEJ CV Matcher PRO — Installation complète

color 0A
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║   AEJ CV MATCHER PRO  v2.0  — INSTALLATION AUTOMATIQUE      ║
echo  ║   Agence Emploi Jeunes / Agence Prestige — Abidjan           ║
echo  ╠══════════════════════════════════════════════════════════════╣
echo  ║  Ce programme va installer automatiquement :                 ║
echo  ║    1. Python 3.11                                            ║
echo  ║    2. Ollama (moteur IA local)                               ║
echo  ║    3. Le modèle IA Gemma 3 (3 Go)                           ║
echo  ║    4. Le logiciel AEJ CV Matcher PRO                         ║
echo  ║    5. Un raccourci sur le Bureau                             ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  Durée estimée : 10-20 minutes (selon votre connexion internet)
echo.
pause

:: ════════════════════════════════════════════════════════════
::  DOSSIER D'INSTALLATION
:: ════════════════════════════════════════════════════════════
set "INSTALL_DIR=%USERPROFILE%\AEJ_CV_Matcher"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
cd /d "%INSTALL_DIR%"

echo.
echo  [ETAPE 1/6]  Verification de Python...
echo  ─────────────────────────────────────────────────────────

python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
    echo  [OK] Python !PY_VER! déjà installé.
) else (
    echo  [INFO] Python introuvable — téléchargement en cours...
    echo         Cela peut prendre 2-3 minutes.
    echo.

    :: Télécharger Python via winget (Windows 10/11)
    winget install --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
    if %errorlevel% equ 0 (
        echo  [OK] Python installé via winget.
        :: Rafraîchir PATH
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
    ) else (
        :: Fallback : téléchargement direct
        echo  [INFO] Téléchargement direct de Python 3.11...
        powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_setup.exe'"
        if not exist "%TEMP%\python_setup.exe" (
            echo  [ERREUR] Impossible de télécharger Python.
            echo  Téléchargez-le manuellement : https://www.python.org/downloads/
            echo  Cochez "Add Python to PATH" puis relancez ce programme.
            pause & exit /b 1
        )
        echo  [INFO] Installation de Python (fenêtre peut s'ouvrir)...
        "%TEMP%\python_setup.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
        del "%TEMP%\python_setup.exe" >nul 2>&1
        :: Rafraîchir PATH
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
        for /f "usebackq delims=" %%i in (`python -c "import sys; print(sys.executable)"`) do set PY_EXE=%%i
    )

    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [ERREUR] Python n'a pas pu être installé.
        echo  Veuillez le télécharger manuellement sur https://www.python.org
        pause & exit /b 1
    )
    echo  [OK] Python installé avec succès.
)

echo.
echo  [ETAPE 2/6]  Téléchargement des fichiers du logiciel...
echo  ─────────────────────────────────────────────────────────

set "REPO_URL=https://raw.githubusercontent.com/badouari-spec/awesome-deepseek-integration/claude/ai-cv-matching-software-ja5bny/docs/aej-cv-matcher"

:: Télécharger les fichiers principaux
echo  Téléchargement de AEJ_CV_Matcher.py...
powershell -Command "Invoke-WebRequest -Uri '%REPO_URL%/AEJ_CV_Matcher.py' -OutFile '%INSTALL_DIR%\AEJ_CV_Matcher.py'" 2>nul
if not exist "%INSTALL_DIR%\AEJ_CV_Matcher.py" (
    echo  [ERREUR] Impossible de télécharger les fichiers du logiciel.
    echo  Vérifiez votre connexion internet.
    pause & exit /b 1
)

echo  Téléchargement de requirements_local.txt...
powershell -Command "Invoke-WebRequest -Uri '%REPO_URL%/requirements_local.txt' -OutFile '%INSTALL_DIR%\requirements_local.txt'" 2>nul

echo  Téléchargement de config_aej_matcher.json...
powershell -Command "Invoke-WebRequest -Uri '%REPO_URL%/config_aej_matcher.json' -OutFile '%INSTALL_DIR%\config_aej_matcher.json'" 2>nul

echo  [OK] Fichiers téléchargés dans : %INSTALL_DIR%

echo.
echo  [ETAPE 3/6]  Installation des dépendances Python...
echo  ─────────────────────────────────────────────────────────
echo  (2-5 minutes selon votre connexion)

python -m pip install --upgrade pip --quiet
pip install -r requirements_local.txt --quiet
if %errorlevel% neq 0 (
    echo  [ERREUR] Echec de l'installation des dépendances.
    echo  Vérifiez votre connexion internet et relancez.
    pause & exit /b 1
)
echo  [OK] Dépendances installées.

echo.
echo  [ETAPE 4/6]  Vérification / Installation d'Ollama...
echo  ─────────────────────────────────────────────────────────

ollama --version >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Ollama déjà installé.
) else (
    echo  [INFO] Ollama introuvable — téléchargement en cours (~150 Mo)...

    :: Essayer winget d'abord
    winget install --id Ollama.Ollama --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
    if %errorlevel% neq 0 (
        :: Fallback : téléchargement direct
        echo  [INFO] Téléchargement direct d'Ollama...
        powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%TEMP%\OllamaSetup.exe'"
        if not exist "%TEMP%\OllamaSetup.exe" (
            echo  [ERREUR] Impossible de télécharger Ollama.
            echo  Téléchargez-le manuellement sur https://ollama.com
            echo  puis relancez ce programme.
            pause & exit /b 1
        )
        "%TEMP%\OllamaSetup.exe" /S
        del "%TEMP%\OllamaSetup.exe" >nul 2>&1
        :: Attendre que l'installation se termine
        timeout /t 10 >nul
        set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
    )

    ollama --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [ATTENTION] Ollama installé — un redémarrage peut être nécessaire.
        echo  Après redémarrage, relancez ce programme pour finir l'installation.
    ) else (
        echo  [OK] Ollama installé avec succès.
    )
)

echo.
echo  [ETAPE 5/6]  Téléchargement du modèle IA (Gemma 3 — ~3 Go)...
echo  ─────────────────────────────────────────────────────────
echo  Cette étape peut prendre 5 à 15 minutes selon votre connexion.
echo  Ne pas fermer cette fenêtre.
echo.

:: Lancer ollama serve en arrière-plan si pas déjà lancé
tasklist /fi "IMAGENAME eq ollama.exe" 2>nul | find /i "ollama.exe" >nul 2>&1
if %errorlevel% neq 0 (
    start /b "" ollama serve >nul 2>&1
    timeout /t 4 >nul
)

ollama pull gemma3:4b
if %errorlevel% neq 0 (
    echo.
    echo  [ATTENTION] Le téléchargement du modèle a échoué.
    echo  Vous pouvez le télécharger manuellement plus tard :
    echo    1. Ouvrir un terminal
    echo    2. Taper : ollama pull gemma3:4b
    echo.
) else (
    echo  [OK] Modèle Gemma 3 prêt.
)

echo.
echo  [ETAPE 6/6]  Création du raccourci Bureau...
echo  ─────────────────────────────────────────────────────────

:: Créer le lanceur
(
echo @echo off
echo chcp 65001 ^>nul
echo title AEJ CV Matcher PRO
echo cd /d "%INSTALL_DIR%"
echo tasklist /fi "IMAGENAME eq ollama.exe" 2^>nul ^| find /i "ollama.exe" ^>nul 2^>^&1
echo if errorlevel 1 start /b "" ollama serve ^>nul 2^>^&1 ^& timeout /t 3 ^>nul
echo python "%INSTALL_DIR%\AEJ_CV_Matcher.py"
) > "%INSTALL_DIR%\Lancer_AEJ_CV_Matcher.bat"

:: Créer raccourci bureau via PowerShell
powershell -Command ^
  "$ws = New-Object -ComObject WScript.Shell; ^
   $s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\AEJ CV Matcher PRO.lnk'); ^
   $s.TargetPath = '%INSTALL_DIR%\Lancer_AEJ_CV_Matcher.bat'; ^
   $s.WorkingDirectory = '%INSTALL_DIR%'; ^
   $s.Description = 'AEJ CV Matcher PRO — Agence Emploi Jeunes'; ^
   $s.Save()"

echo  [OK] Raccourci créé sur le Bureau.

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║          INSTALLATION TERMINÉE AVEC SUCCÈS !                ║
echo  ╠══════════════════════════════════════════════════════════════╣
echo  ║  Le logiciel est installé dans :                            ║
echo  ║    %INSTALL_DIR%
echo  ║                                                              ║
echo  ║  Pour lancer le logiciel :                                   ║
echo  ║    → Double-cliquer sur "AEJ CV Matcher PRO" sur le Bureau  ║
echo  ║                                                              ║
echo  ║  L'IA fonctionne 100%% en local — aucune clé API requise.   ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

set /p LANCER="  Lancer le logiciel maintenant ? (O/N) : "
if /i "%LANCER%"=="O" (
    start "" "%INSTALL_DIR%\Lancer_AEJ_CV_Matcher.bat"
)

pause
endlocal
