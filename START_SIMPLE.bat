@echo off
title CyberSec Pro Dashboard - Simple Launcher
cd /d "%~dp0"

echo.
echo ================================================
echo   CYBERSEC PRO DASHBOARD - QUICK START
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking dependencies...
echo.

REM Check if data file exists
if not exist "Cybersecurity_KPI_Minimal.xlsx" (
    echo ERROR: Data file 'Cybersecurity_KPI_Minimal.xlsx' not found
    echo Please ensure the data file is in the same directory
    pause
    exit /b 1
)

REM Check if main files exist
if not exist "dashboard_optimized.py" (
    echo ERROR: dashboard_optimized.py not found
    pause
    exit /b 1
)

if not exist "api_optimized.py" (
    echo ERROR: api_optimized.py not found
    pause
    exit /b 1
)

echo All files found. Starting services...
echo.

echo [1/2] Starting API Server (this may take a moment)...
start "CyberSec API Server" cmd /k "echo Starting API Server... && python api_optimized.py"

REM Wait for API to initialize
echo Waiting for API to initialize...
timeout /t 8 /nobreak >nul

echo [2/2] Starting Dashboard...
start "CyberSec Dashboard" cmd /k "echo Starting Dashboard... && python dashboard_optimized.py"

echo.
echo ================================================
echo   SERVICES STARTING...
echo ================================================
echo.
echo Dashboard URL: http://localhost:8050
echo API Server URL: http://localhost:8001
echo.
echo Two command windows will open:
echo - One for the API Server (port 8001)
echo - One for the Dashboard (port 8050)
echo.
echo To stop the services, close both command windows.
echo.
echo Opening browser in 10 seconds...
timeout /t 10 /nobreak

REM Try to open the dashboard in default browser
start http://localhost:8050

echo.
echo Thank you for using CyberSec Pro Dashboard!
echo.
pause
