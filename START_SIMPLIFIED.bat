@echo off
title CyberSec Pro Dashboard - Simplified (No API Required)
cd /d "%~dp0"

echo.
echo ========================================================
echo   CYBERSEC PRO DASHBOARD - SIMPLIFIED VERSION
echo ========================================================
echo   ✅ No API server required
echo   📊 Direct model integration  
echo   🚀 Single process startup
echo ========================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found. Checking requirements...

REM Check if data file exists
if not exist "Cybersecurity_KPI_Minimal.xlsx" (
    echo ❌ ERROR: Data file 'Cybersecurity_KPI_Minimal.xlsx' not found
    echo Please ensure the data file is in the same directory
    pause
    exit /b 1
)

REM Check if main files exist
if not exist "dashboard_simplified.py" (
    echo ❌ ERROR: dashboard_simplified.py not found
    pause
    exit /b 1
)

if not exist "model_integration.py" (
    echo ❌ ERROR: model_integration.py not found
    pause
    exit /b 1
)

echo ✅ All files found. Starting dashboard...
echo.

echo 🧠 Loading AI model (this may take a moment)...
echo 📊 Starting dashboard with integrated AI features...
echo.

REM Start the simplified dashboard
python dashboard_simplified.py

echo.
echo Dashboard session ended.
pause
