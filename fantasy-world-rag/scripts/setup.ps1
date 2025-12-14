# Fantasy World RAG - Quick Start Script for Windows
# Run this in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fantasy World RAG - Setup Wizard" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ATTENZIONE: Esegui questo script come Amministratore!" -ForegroundColor Red
    Write-Host "Tasto destro su PowerShell > Esegui come amministratore" -ForegroundColor Yellow
    exit 1
}

# Function to check if command exists
function Test-Command($command) {
    try {
        Get-Command $command -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Function to pause
function Pause-Script {
    Write-Host ""
    Write-Host "Premi un tasto per continuare..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Step 1: Check Python
Write-Host "[1/7] Controllo Python..." -ForegroundColor Green
if (Test-Command "python") {
    $pythonVersion = python --version 2>&1
    Write-Host "  OK: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  MANCANTE: Python non trovato!" -ForegroundColor Red
    Write-Host "  Scarica da: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  IMPORTANTE: Spunta 'Add Python to PATH' durante l'installazione!" -ForegroundColor Yellow
    Pause-Script
}

# Step 2: Check Node.js
Write-Host "[2/7] Controllo Node.js..." -ForegroundColor Green
if (Test-Command "node") {
    $nodeVersion = node --version 2>&1
    Write-Host "  OK: Node.js $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "  MANCANTE: Node.js non trovato!" -ForegroundColor Red
    Write-Host "  Scarica da: https://nodejs.org/" -ForegroundColor Yellow
    Pause-Script
}

# Step 3: Check Docker
Write-Host "[3/7] Controllo Docker..." -ForegroundColor Green
if (Test-Command "docker") {
    $dockerVersion = docker --version 2>&1
    Write-Host "  OK: $dockerVersion" -ForegroundColor Green
    
    # Check if Docker is running
    $dockerRunning = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ATTENZIONE: Docker non e' in esecuzione!" -ForegroundColor Yellow
        Write-Host "  Apri Docker Desktop e aspetta che si avvii." -ForegroundColor Yellow
    }
} else {
    Write-Host "  MANCANTE: Docker non trovato!" -ForegroundColor Red
    Write-Host "  Scarica da: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Pause-Script
}

# Step 4: Check/Install Poetry
Write-Host "[4/7] Controllo Poetry..." -ForegroundColor Green
if (Test-Command "poetry") {
    $poetryVersion = poetry --version 2>&1
    Write-Host "  OK: $poetryVersion" -ForegroundColor Green
} else {
    Write-Host "  Poetry non trovato. Installazione in corso..." -ForegroundColor Yellow
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    
    # Add to PATH for current session
    $env:Path += ";$env:APPDATA\Python\Scripts"
    
    Write-Host "  Poetry installato!" -ForegroundColor Green
    Write-Host "  NOTA: Potresti dover riavviare il terminale." -ForegroundColor Yellow
}

# Step 5: Install Python dependencies
Write-Host "[5/7] Installazione dipendenze Python..." -ForegroundColor Green
if (Test-Path "pyproject.toml") {
    poetry install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Dipendenze Python installate!" -ForegroundColor Green
    } else {
        Write-Host "  ERRORE nell'installazione. Controlla i messaggi sopra." -ForegroundColor Red
    }
} else {
    Write-Host "  ERRORE: pyproject.toml non trovato!" -ForegroundColor Red
    Write-Host "  Assicurati di essere nella cartella del progetto." -ForegroundColor Yellow
}

# Step 6: Install Frontend dependencies
Write-Host "[6/7] Installazione dipendenze Frontend..." -ForegroundColor Green
if (Test-Path "frontend/package.json") {
    Push-Location frontend
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Dipendenze Frontend installate!" -ForegroundColor Green
    } else {
        Write-Host "  ERRORE nell'installazione frontend." -ForegroundColor Red
    }
    Pop-Location
} else {
    Write-Host "  ERRORE: frontend/package.json non trovato!" -ForegroundColor Red
}

# Step 7: Setup .env file
Write-Host "[7/7] Configurazione file .env..." -ForegroundColor Green
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "  File .env creato da .env.example" -ForegroundColor Green
        Write-Host ""
        Write-Host "  IMPORTANTE: Modifica il file .env con le tue API key!" -ForegroundColor Yellow
        Write-Host "  - GROK_API_KEY: ottienila da https://console.x.ai" -ForegroundColor Yellow
        Write-Host "  - DEEPSEEK_API_KEY: ottienila da https://platform.deepseek.com" -ForegroundColor Yellow
    } else {
        Write-Host "  ERRORE: .env.example non trovato!" -ForegroundColor Red
    }
} else {
    Write-Host "  File .env gia' esistente." -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup completato!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Prossimi passi:" -ForegroundColor White
Write-Host "1. Modifica il file .env con le tue API key" -ForegroundColor Yellow
Write-Host "2. Avvia Docker Desktop (se non e' gia' aperto)" -ForegroundColor Yellow
Write-Host "3. Esegui: .\scripts\start.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Oppure avvia manualmente:" -ForegroundColor White
Write-Host "  docker-compose up -d" -ForegroundColor Gray
Write-Host "  poetry run uvicorn src.main:app --reload --port 8000" -ForegroundColor Gray
Write-Host "  cd frontend; npm run dev" -ForegroundColor Gray
Write-Host ""
