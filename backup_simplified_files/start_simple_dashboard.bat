@echo off
echo Starting Cybersecurity KPI Dashboard with Simple Suggestion System...
echo.
echo This script will start both the simplified suggestion API and the dashboard
echo.
echo 1. Make sure you have installed all required packages (except sentence-transformers):
echo    pip install dash dash-bootstrap-components plotly pandas numpy fastapi uvicorn openpyxl requests
echo.
echo 2. Starting the Simple Suggestion API...
start cmd /k "cd /d "%~dp0" && python simple_suggestion_api.py"
echo.
echo 3. Starting the Enhanced Dashboard...
echo    Opening dashboard at http://127.0.0.1:8050/
echo.
timeout /t 5
start cmd /k "cd /d "%~dp0" && python enhanced_dashboard.py"
echo.
echo Both services are running. You can access the dashboard at:
echo http://127.0.0.1:8050/
echo.
echo Press any key to shut down both services...
pause
taskkill /F /FI "WINDOWTITLE eq *simple_suggestion_api.py*"
taskkill /F /FI "WINDOWTITLE eq *enhanced_dashboard.py*"
