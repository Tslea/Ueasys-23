# Fantasy World RAG - Start Script for Windows
# Run this in PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fantasy World RAG - Avvio Sistema" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "ERRORE: File .env non trovato!" -ForegroundColor Red
    Write-Host "Esegui prima: .\scripts\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Check Docker
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRORE: Docker non e' in esecuzione!" -ForegroundColor Red
    Write-Host "Apri Docker Desktop e aspetta che si avvii." -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/4] Avvio database con Docker..." -ForegroundColor Green
docker-compose up -d

Write-Host ""
Write-Host "[2/4] Attendo che i database siano pronti..." -ForegroundColor Green
Start-Sleep -Seconds 10

# Check if database migration is needed
Write-Host ""
Write-Host "[3/4] Controllo migrazioni database..." -ForegroundColor Green
poetry run alembic upgrade head 2>&1 | Out-Null
Write-Host "  Database pronto!" -ForegroundColor Green

Write-Host ""
Write-Host "[4/4] Avvio servizi..." -ForegroundColor Green
Write-Host ""

# Create a helper script to start backend
$backendScript = @'
Write-Host "Backend avviato su http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Premi CTRL+C per fermare" -ForegroundColor Yellow
Write-Host ""
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
'@

# Create a helper script to start frontend
$frontendScript = @'
Write-Host "Frontend avviato su http://localhost:5173" -ForegroundColor Green
Write-Host "Premi CTRL+C per fermare" -ForegroundColor Yellow
Write-Host ""
cd frontend
npm run dev
'@

# Save scripts temporarily
$backendScript | Out-File -FilePath "$env:TEMP\start-backend.ps1" -Encoding UTF8
$frontendScript | Out-File -FilePath "$env:TEMP\start-frontend.ps1" -Encoding UTF8

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-File", "$env:TEMP\start-backend.ps1" -WorkingDirectory (Get-Location)

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-File", "$env:TEMP\start-frontend.ps1" -WorkingDirectory (Get-Location)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Sistema Avviato!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Servizi in esecuzione:" -ForegroundColor White
Write-Host "  - PostgreSQL:  localhost:5432" -ForegroundColor Gray
Write-Host "  - Redis:       localhost:6379" -ForegroundColor Gray
Write-Host "  - Qdrant:      localhost:6333" -ForegroundColor Gray
Write-Host "  - Backend:     http://localhost:8000" -ForegroundColor Green
Write-Host "  - Frontend:    http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Apri il browser su: http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "Per fermare tutto:" -ForegroundColor White
Write-Host "  1. Chiudi le finestre Backend e Frontend" -ForegroundColor Gray
Write-Host "  2. Esegui: docker-compose down" -ForegroundColor Gray
Write-Host ""

# Open browser
Start-Process "http://localhost:5173"
