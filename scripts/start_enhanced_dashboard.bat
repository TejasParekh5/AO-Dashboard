@echo off
echo Starting Cybersecurity KPI Dashboard with Smart Suggestion System...
echo.
echo This script will start both the suggestion API and the dashboard
echo.
echo 1. Make sure you have installed all required packages:
echo    pip install -r requirements.txt
echo.
echo 2. Starting the Smart Suggestion API...
start cmd /k "cd /d "%~dp0" && .\.venv\Scripts\python.exe suggestion_api.py"
echo.
echo 3. Starting the Enhanced Dashboard...
echo    Opening dashboard at http://127.0.0.1:8050/
echo.
timeout /t 5
start cmd /k "cd /d "%~dp0" && .\.venv\Scripts\python.exe enhanced_dashboard.py"
echo.
echo Both services are running. You can access the dashboard at:
echo http://127.0.0.1:8050/
echo.
echo Press any key to shut down both services...
pause
taskkill /F /FI "WINDOWTITLE eq *suggestion_api.py*"
taskkill /F /FI "WINDOWTITLE eq *enhanced_dashboard.py*"
