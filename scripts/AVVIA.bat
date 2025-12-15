@echo off
title Ueasys - Avvio Completo
color 0A
setlocal EnableDelayedExpansion

echo.
echo ========================================
echo   Ueasys - Avvio Sistema
echo ========================================
echo.

:: Change to project directory
cd /d "%~dp0.."

:: ========================================
:: CONTROLLO PREREQUISITI
:: ========================================

echo [CONTROLLO] Verifica prerequisiti...
echo.

:: ----- Check Python -----
echo [1/6] Controllo Python...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo   [X] Python NON trovato!
    echo.
    echo   Devi installare Python 3.11 o superiore.
    echo   Scaricalo da: https://www.python.org/downloads/
    echo.
    echo   IMPORTANTE: Durante l'installazione, spunta
    echo   "Add Python to PATH" in basso!
    echo.
    set MISSING_PYTHON=1
    goto :CHECK_NODE
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo   [OK] Python %PYTHON_VER%

:CHECK_NODE
:: ----- Check Node.js -----
echo [2/6] Controllo Node.js...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo   [X] Node.js NON trovato!
    echo.
    echo   Devi installare Node.js 18 o superiore.
    echo   Scaricalo da: https://nodejs.org/
    echo.
    set MISSING_NODE=1
    goto :CHECK_DOCKER
)
for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VER=%%i
echo   [OK] Node.js %NODE_VER%

:CHECK_DOCKER
:: ----- Check Docker -----
echo [3/6] Controllo Docker...
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo   [X] Docker NON trovato!
    echo.
    echo   Devi installare Docker Desktop.
    echo   Scaricalo da: https://www.docker.com/products/docker-desktop/
    echo.
    set MISSING_DOCKER=1
    goto :CHECK_MISSING
)
echo   [OK] Docker trovato

:: Check if Docker is running
docker info >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo   [!] Docker non e' in esecuzione!
    echo   Avvio Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo   Attendo 30 secondi che Docker si avvii...
    timeout /t 30 /nobreak >nul
    
    :: Check again
    docker info >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo   [X] Docker non si e' avviato!
        echo   Apri Docker Desktop manualmente e riprova.
        set DOCKER_NOT_RUNNING=1
    ) else (
        echo   [OK] Docker avviato!
    )
) else (
    echo   [OK] Docker in esecuzione
)

:CHECK_MISSING
:: ----- Check if any critical component is missing -----
if defined MISSING_PYTHON (
    echo.
    echo ========================================
    echo   ERRORE: Prerequisiti mancanti!
    echo ========================================
    echo   Installa Python e riprova.
    echo.
    pause
    exit /b 1
)

if defined MISSING_NODE (
    echo.
    echo ========================================
    echo   ERRORE: Prerequisiti mancanti!
    echo ========================================
    echo   Installa Node.js e riprova.
    echo.
    pause
    exit /b 1
)

if defined MISSING_DOCKER (
    echo.
    echo ========================================
    echo   ERRORE: Prerequisiti mancanti!
    echo ========================================
    echo   Installa Docker Desktop e riprova.
    echo.
    pause
    exit /b 1
)

if defined DOCKER_NOT_RUNNING (
    echo.
    echo   Avvia Docker Desktop manualmente e riprova.
    pause
    exit /b 1
)

:: ========================================
:: CONTROLLO/INSTALLAZIONE POETRY
:: ========================================
echo [4/6] Controllo Poetry...

:: Aggiungi possibili path di Poetry al PATH corrente
set "PATH=%PATH%;%APPDATA%\Python\Scripts;%APPDATA%\Python\Python312\Scripts;%APPDATA%\Python\Python311\Scripts;%USERPROFILE%\.local\bin;%APPDATA%\pypoetry\venv\Scripts"

:: Prima prova con 'poetry --version' direttamente
poetry --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%i in ('poetry --version 2^>^&1') do set POETRY_VER=%%i
    echo   [OK] !POETRY_VER!
    goto :POETRY_OK
)

:: Se non funziona, prova con 'python -m poetry'
python -m poetry --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%i in ('python -m poetry --version 2^>^&1') do set POETRY_VER=%%i
    echo   [OK] !POETRY_VER! (via python -m)
    :: Usa python -m poetry per il resto dello script
    set "POETRY_CMD=python -m poetry"
    goto :POETRY_OK
)

:: Poetry non trovato, installiamo
echo   [!] Poetry non trovato. Installazione in corso...
echo.

:: Install Poetry using pip
python -m pip install poetry >nul 2>nul

:: Riprova dopo installazione
python -m poetry --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%i in ('python -m poetry --version 2^>^&1') do set POETRY_VER=%%i
    echo   [OK] !POETRY_VER! installato
    set "POETRY_CMD=python -m poetry"
    goto :POETRY_OK
)

:: Ultimo tentativo con installer ufficiale
echo   Tentativo con installer ufficiale...
powershell -Command "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -" 2>nul

:: Ricarica PATH
set "PATH=%PATH%;%APPDATA%\pypoetry\venv\Scripts"

poetry --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Poetry installato!
    goto :POETRY_OK
)

python -m poetry --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Poetry installato!
    set "POETRY_CMD=python -m poetry"
    goto :POETRY_OK
)

echo   [X] Installazione Poetry fallita!
echo   Prova ad aprire un nuovo terminale e riavviare questo script.
echo   Oppure esegui: pip install poetry
pause
exit /b 1

:POETRY_OK
:: Imposta comando poetry di default se non ancora impostato
if not defined POETRY_CMD set "POETRY_CMD=poetry"

:: ========================================
:: CONTROLLO/INSTALLAZIONE DIPENDENZE PYTHON
:: ========================================
echo [5/6] Controllo dipendenze Python...

:: Check if virtual environment exists
if not exist ".venv" (
    echo   [!] Ambiente virtuale non trovato. Creazione in corso...
    echo   (Questo puo' richiedere qualche minuto...)
    %POETRY_CMD% install --no-interaction
    if %ERRORLEVEL% NEQ 0 (
        echo   [X] Errore nell'installazione dipendenze Python!
        pause
        exit /b 1
    )
    echo   [OK] Dipendenze Python installate!
) else (
    echo   [OK] Ambiente virtuale esistente
    :: Run poetry install silently to catch any updates
    %POETRY_CMD% install --no-interaction >nul 2>nul
)

:: ========================================
:: CONTROLLO/INSTALLAZIONE DIPENDENZE FRONTEND
:: ========================================
echo [6/6] Controllo dipendenze Frontend...

if not exist "frontend\node_modules" (
    echo   [!] Moduli Node non trovati. Installazione in corso...
    echo   (Questo puo' richiedere qualche minuto...)
    cd frontend
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo   [X] Errore nell'installazione dipendenze Frontend!
        cd ..
        pause
        exit /b 1
    )
    cd ..
    echo   [OK] Dipendenze Frontend installate!
) else (
    echo   [OK] Moduli Node esistenti
)

:: ========================================
:: CONTROLLO FILE .ENV
:: ========================================
echo.
echo [CONFIGURAZIONE] Controllo file .env...

:: Use PowerShell to check for .env file (more reliable than batch 'if exist')
powershell -Command "Test-Path '.env'" | findstr "True" >nul
if %ERRORLEVEL% EQU 0 (
    echo   [OK] File .env presente
    goto :ENV_OK
)

:: .env non esiste, controlla .env.example
powershell -Command "Test-Path '.env.example'" | findstr "True" >nul
if %ERRORLEVEL% EQU 0 (
    echo   [!] File .env non trovato. Creazione da template...
    copy .env.example .env >nul
    echo   [OK] File .env creato!
    echo.
    echo   ========================================
    echo   ATTENZIONE: Configura le API Key!
    echo   ========================================
    echo   Apri il file .env e inserisci:
    echo   - GROK_API_KEY (da console.x.ai)
    echo   - DEEPSEEK_API_KEY (da platform.deepseek.com)
    echo.
    echo   IMPORTANTE: Apri il file .env e inserisci le tue API key,
    echo   poi rilancia questo script.
    echo.
    pause
    exit /b 0
) else (
    echo   [X] File .env.example non trovato!
    pause
    exit /b 1
)

:ENV_OK

:: ========================================
:: AVVIO SERVIZI
:: ========================================
echo.
echo ========================================
echo   Avvio Servizi
echo ========================================
echo.

:: Start Docker containers (only databases, not the API)
echo [1/4] Avvio database Docker...
docker compose up -d postgres redis qdrant
if %ERRORLEVEL% NEQ 0 (
    echo   [X] Errore avvio Docker containers!
    pause
    exit /b 1
)
echo   [OK] Database avviati (PostgreSQL, Redis, Qdrant)

:: Wait for databases to be ready
echo [2/4] Attendo che i database siano pronti...
timeout /t 8 /nobreak >nul
echo   [OK] Database pronti

:: Run migrations
echo [3/4] Controllo migrazioni database...
%POETRY_CMD% run alembic upgrade head >nul 2>nul
echo   [OK] Database aggiornato

:: Start backend and frontend
echo [4/4] Avvio Backend e Frontend...
echo.

:: Create temp scripts for new windows
echo @echo off > "%TEMP%\fwr_backend.bat"
echo title Ueasys - Backend >> "%TEMP%\fwr_backend.bat"
echo color 0A >> "%TEMP%\fwr_backend.bat"
echo cd /d "%CD%" >> "%TEMP%\fwr_backend.bat"
echo echo. >> "%TEMP%\fwr_backend.bat"
echo echo ======================================== >> "%TEMP%\fwr_backend.bat"
echo echo   Backend - http://localhost:8000 >> "%TEMP%\fwr_backend.bat"
echo echo   API Docs - http://localhost:8000/docs >> "%TEMP%\fwr_backend.bat"
echo echo ======================================== >> "%TEMP%\fwr_backend.bat"
echo echo. >> "%TEMP%\fwr_backend.bat"
echo echo Premi CTRL+C per fermare >> "%TEMP%\fwr_backend.bat"
echo echo. >> "%TEMP%\fwr_backend.bat"
echo %POETRY_CMD% run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 >> "%TEMP%\fwr_backend.bat"
echo pause >> "%TEMP%\fwr_backend.bat"

echo @echo off > "%TEMP%\fwr_frontend.bat"
echo title Ueasys - Frontend >> "%TEMP%\fwr_frontend.bat"
echo color 0B >> "%TEMP%\fwr_frontend.bat"
echo cd /d "%CD%\frontend" >> "%TEMP%\fwr_frontend.bat"
echo echo. >> "%TEMP%\fwr_frontend.bat"
echo echo ======================================== >> "%TEMP%\fwr_frontend.bat"
echo echo   Frontend - http://localhost:5173 >> "%TEMP%\fwr_frontend.bat"
echo echo ======================================== >> "%TEMP%\fwr_frontend.bat"
echo echo. >> "%TEMP%\fwr_frontend.bat"
echo echo Premi CTRL+C per fermare >> "%TEMP%\fwr_frontend.bat"
echo echo. >> "%TEMP%\fwr_frontend.bat"
echo npm run dev >> "%TEMP%\fwr_frontend.bat"
echo pause >> "%TEMP%\fwr_frontend.bat"

:: Start backend
start "" "%TEMP%\fwr_backend.bat"

:: Wait for backend to start
timeout /t 4 /nobreak >nul

:: Start frontend
start "" "%TEMP%\fwr_frontend.bat"

:: Wait a bit then open browser
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   Sistema Avviato con Successo!
echo ========================================
echo.
echo   Servizi attivi:
echo   - PostgreSQL:  localhost:5432
echo   - Redis:       localhost:6379
echo   - Qdrant:      localhost:6333
echo   - Backend:     http://localhost:8000
echo   - Frontend:    http://localhost:5173
echo.
echo   Apertura browser...
echo.

:: Open browser
start "" "http://localhost:5173"

echo   Per fermare tutto:
echo   1. Chiudi le finestre Backend e Frontend
echo   2. Esegui FERMA.bat oppure: docker-compose down
echo.
echo   Premi un tasto per chiudere questa finestra...
pause >nul
