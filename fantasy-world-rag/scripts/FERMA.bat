@echo off
title Ueasys - Stop
color 0C

echo ========================================
echo   Ueasys - Arresto Sistema
echo ========================================
echo.

:: Change to project directory
cd /d "%~dp0.."

:: Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERRORE: PowerShell non trovato!
    pause
    exit /b 1
)

:: Run the PowerShell stop script
powershell -ExecutionPolicy Bypass -File "%~dp0stop.ps1"

pause
