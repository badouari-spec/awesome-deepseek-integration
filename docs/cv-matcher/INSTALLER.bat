@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title CV Matcher Web — Installation complète

color 0A
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║   CV MATCHER WEB  — INSTALLATION AUTOMATIQUE                ║
echo  ║   Matching de CV par IA — 100%% local avec Ollama            ║
echo  ╠══════════════════════════════════════════════════════════════╣
echo  ║  Ce programme va installer automatiquement :                 ║
echo  ║    1. Python 3.11                                            ║
echo  ║    2. Ollama (moteur IA local)                               ║
echo  ║    3. Le modèle IA Gemma 3 (3 Go)                           ║
echo  ║    4. Le logiciel CV Matcher (interface web)                 ║
echo  ║    5. Un raccourci sur le Bureau                             ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
echo  Durée estimée : 10-20 minutes (selon votre connexion internet)
echo.
pause

:: ════════════════════════════════════════════════════════════
::  DOSSIER D'INSTALLATION
:: ════════════════════════════════════════════════════════════
set "INSTALL_DIR=%USERPROFILE%\CV_Matcher_Web"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
cd /d "%INSTALL_DIR%"

echo.
echo  [ETAPE 1/6]  Vérification de Python...
echo  ─────────────────────────────────────────────────────────

python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
    echo  [OK] Python !PY_VER! déjà installé.
) else (
    echo  [INFO] Python introuvable — installation en cours...
    winget install --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [INFO] Téléchargement direct de Python 3.11...
        powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_setup.exe'"
        "%TEMP%\python_setup.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
        del "%TEMP%\python_setup.exe" >nul 2>&1
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
    ) else (
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
    )
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [ERREUR] Python n'a pas pu être installé.
        echo  Téléchargez-le sur https://www.python.org (cocher "Add to PATH")
        pause & exit /b 1
    )
    echo  [OK] Python installé.
)

echo.
echo  [ETAPE 2/6]  Téléchargement des fichiers du logiciel...
echo  ─────────────────────────────────────────────────────────

set "BASE_URL=https://raw.githubusercontent.com/badouari-spec/awesome-deepseek-integration/claude/ai-cv-matching-software-ja5bny/docs/cv-matcher"
set "BACK_URL=%BASE_URL%/backend/app"

:: Structure de dossiers
if not exist "%INSTALL_DIR%\backend\app\routers"  mkdir "%INSTALL_DIR%\backend\app\routers"
if not exist "%INSTALL_DIR%\backend\app\models"   mkdir "%INSTALL_DIR%\backend\app\models"
if not exist "%INSTALL_DIR%\backend\app\services" mkdir "%INSTALL_DIR%\backend\app\services"
if not exist "%INSTALL_DIR%\frontend\js"          mkdir "%INSTALL_DIR%\frontend\js"
if not exist "%INSTALL_DIR%\frontend\css"         mkdir "%INSTALL_DIR%\frontend\css"
if not exist "%INSTALL_DIR%\uploads"              mkdir "%INSTALL_DIR%\uploads"

echo  Téléchargement des fichiers backend...
for %%F in (main.py config.py database.py) do (
    powershell -Command "Invoke-WebRequest -Uri '%BACK_URL%/%%F' -OutFile '%INSTALL_DIR%\backend\app\%%F'" 2>nul
)
for %%F in (db_models.py schemas.py) do (
    powershell -Command "Invoke-WebRequest -Uri '%BACK_URL%/models/%%F' -OutFile '%INSTALL_DIR%\backend\app\models\%%F'" 2>nul
)
for %%F in (document_parser.py ai_service.py) do (
    powershell -Command "Invoke-WebRequest -Uri '%BACK_URL%/services/%%F' -OutFile '%INSTALL_DIR%\backend\app\services\%%F'" 2>nul
)
for %%F in (cv_router.py job_router.py match_router.py) do (
    powershell -Command "Invoke-WebRequest -Uri '%BACK_URL%/routers/%%F' -OutFile '%INSTALL_DIR%\backend\app\routers\%%F'" 2>nul
)
:: __init__.py
powershell -Command "'' | Out-File '%INSTALL_DIR%\backend\app\__init__.py' -Encoding utf8" 2>nul
powershell -Command "'' | Out-File '%INSTALL_DIR%\backend\app\routers\__init__.py' -Encoding utf8" 2>nul
powershell -Command "'' | Out-File '%INSTALL_DIR%\backend\app\models\__init__.py' -Encoding utf8" 2>nul
powershell -Command "'' | Out-File '%INSTALL_DIR%\backend\app\services\__init__.py' -Encoding utf8" 2>nul

powershell -Command "Invoke-WebRequest -Uri '%BASE_URL%/backend/requirements.txt' -OutFile '%INSTALL_DIR%\backend\requirements.txt'" 2>nul

echo  Téléchargement de l'interface web...
powershell -Command "Invoke-WebRequest -Uri '%BASE_URL%/frontend/index.html' -OutFile '%INSTALL_DIR%\frontend\index.html'" 2>nul
for %%F in (api.js components.js main.js) do (
    powershell -Command "Invoke-WebRequest -Uri '%BASE_URL%/frontend/js/%%F' -OutFile '%INSTALL_DIR%\frontend\js\%%F'" 2>nul
)
powershell -Command "Invoke-WebRequest -Uri '%BASE_URL%/frontend/css/app.css' -OutFile '%INSTALL_DIR%\frontend\css\app.css'" 2>nul

powershell -Command "Invoke-WebRequest -Uri '%BASE_URL%/run.py' -OutFile '%INSTALL_DIR%\run.py'" 2>nul

if not exist "%INSTALL_DIR%\run.py" (
    echo  [ERREUR] Téléchargement impossible. Vérifiez votre connexion.
    pause & exit /b 1
)
echo  [OK] Fichiers téléchargés.

:: Fichier .env
(
echo AI_PROVIDER=ollama
echo API_KEY=ollama
echo API_BASE_URL=http://localhost:11434/v1
echo AI_MODEL=gemma3:4b
echo OLLAMA_BASE_URL=http://localhost:11434
) > "%INSTALL_DIR%\.env"

echo.
echo  [ETAPE 3/6]  Installation des dépendances Python...
echo  ─────────────────────────────────────────────────────────
python -m pip install --upgrade pip --quiet
pip install -r "%INSTALL_DIR%\backend\requirements.txt" --quiet
if %errorlevel% neq 0 (
    echo  [ERREUR] Echec installation des dépendances.
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
    echo  [INFO] Installation d'Ollama...
    winget install --id Ollama.Ollama --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
    if %errorlevel% neq 0 (
        powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%TEMP%\OllamaSetup.exe'"
        "%TEMP%\OllamaSetup.exe" /S
        del "%TEMP%\OllamaSetup.exe" >nul 2>&1
        timeout /t 10 >nul
        set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
    )
    echo  [OK] Ollama installé.
)

echo.
echo  [ETAPE 5/6]  Téléchargement du modèle IA Gemma 3 (~3 Go)...
echo  ─────────────────────────────────────────────────────────

tasklist /fi "IMAGENAME eq ollama.exe" 2>nul | find /i "ollama.exe" >nul 2>&1
if %errorlevel% neq 0 (
    start /b "" ollama serve >nul 2>&1
    timeout /t 4 >nul
)
ollama pull gemma3:4b
if %errorlevel% neq 0 (
    echo  [ATTENTION] Modèle non téléchargé. Faites-le manuellement :
    echo    ollama pull gemma3:4b
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
echo title CV Matcher Web
echo cd /d "%INSTALL_DIR%"
echo tasklist /fi "IMAGENAME eq ollama.exe" 2^>nul ^| find /i "ollama.exe" ^>nul 2^>^&1
echo if errorlevel 1 start /b "" ollama serve ^>nul 2^>^&1 ^& timeout /t 3 ^>nul
echo python "%INSTALL_DIR%\run.py"
) > "%INSTALL_DIR%\Lancer_CV_Matcher.bat"

:: Raccourci Bureau
powershell -Command ^
  "$ws = New-Object -ComObject WScript.Shell; ^
   $s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\CV Matcher Web.lnk'); ^
   $s.TargetPath = '%INSTALL_DIR%\Lancer_CV_Matcher.bat'; ^
   $s.WorkingDirectory = '%INSTALL_DIR%'; ^
   $s.Description = 'CV Matcher Web — Matching de CV par IA'; ^
   $s.Save()"

echo  [OK] Raccourci "CV Matcher Web" créé sur le Bureau.

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║          INSTALLATION TERMINÉE AVEC SUCCÈS !                ║
echo  ╠══════════════════════════════════════════════════════════════╣
echo  ║  Raccourci : "CV Matcher Web" sur votre Bureau              ║
echo  ║  Dossier   : %INSTALL_DIR%
echo  ║                                                              ║
echo  ║  Au lancement : votre navigateur s'ouvre automatiquement    ║
echo  ║  sur http://localhost:8000                                   ║
echo  ║                                                              ║
echo  ║  L'IA fonctionne 100%% en local — aucune clé API requise.   ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

set /p LANCER="  Lancer le logiciel maintenant ? (O/N) : "
if /i "%LANCER%"=="O" (
    start "" "%INSTALL_DIR%\Lancer_CV_Matcher.bat"
)

pause
endlocal
