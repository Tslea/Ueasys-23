@echo off
title Ueasys - Setup
color 0B

echo ========================================
echo   Ueasys - Setup Wizard
echo ========================================
echo.

:: Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERRORE: PowerShell non trovato!
    pause
    exit /b 1
)

:: Run the PowerShell setup script
powershell -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

pause
