# Fantasy World RAG - Stop Script for Windows
# Run this in PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fantasy World RAG - Arresto Sistema" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Arresto container Docker..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "[2/2] Pulizia processi..." -ForegroundColor Yellow

# Kill any uvicorn processes
$uvicornProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn*" }
if ($uvicornProcesses) {
    $uvicornProcesses | Stop-Process -Force
    Write-Host "  Backend fermato." -ForegroundColor Green
}

# Kill any node processes related to vite
$viteProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*vite*" }
if ($viteProcesses) {
    $viteProcesses | Stop-Process -Force
    Write-Host "  Frontend fermato." -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Sistema Arrestato!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tutti i servizi sono stati fermati." -ForegroundColor Green
Write-Host ""
Write-Host "Per riavviare: .\scripts\start.ps1" -ForegroundColor Yellow
Write-Host ""
