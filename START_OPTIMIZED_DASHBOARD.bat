@echo off
title CyberSec Pro Dashboard - Optimized Launcher

echo.
echo ================================================
echo   CYBERSEC PRO DASHBOARD - QUICK START
echo ================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo WARNING: Not running as administrator
    echo Some features may be limited
    echo.
)

echo Starting optimized dashboard with PowerShell...
echo.

REM Execute the PowerShell script
powershell.exe -ExecutionPolicy Bypass -File "scripts\start_optimized_dashboard.ps1"

if %errorLevel% neq 0 (
    echo.
    echo ERROR: Failed to start dashboard
    echo.
    echo Troubleshooting:
    echo 1. Right-click and "Run as administrator"
    echo 2. Check if Python is installed
    echo 3. Ensure all files are present
    echo.
    pause
)

echo.
echo Dashboard session ended.
pause
