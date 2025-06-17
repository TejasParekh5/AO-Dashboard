@echo off
echo Cybersecurity KPI Dashboard - FULL VERSION
echo ==========================================
echo.
echo This script will start both the ML-powered suggestion API and the enhanced dashboard
echo.
echo Starting the Suggestion API (ML-based)...
start cmd /k "cd /d "%~dp0" && python suggestion_api.py"

echo.
echo Waiting for API to initialize (5 seconds)...
timeout /t 5 /nobreak >nul

echo.
echo Starting the Enhanced Dashboard...
cd /d "%~dp0"
python enhanced_dashboard.py

echo.
echo Dashboard is now running. Access it at http://127.0.0.1:8050/ in your web browser.
echo.
pause
