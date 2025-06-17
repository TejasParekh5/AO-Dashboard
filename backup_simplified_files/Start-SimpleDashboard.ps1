# Start Cybersecurity KPI Dashboard with Simple Suggestion System
Write-Host "Starting Cybersecurity KPI Dashboard with Simple Suggestion System..." -ForegroundColor Cyan
Write-Host 
Write-Host "This script will start both the simplified suggestion API and the dashboard"
Write-Host 

Write-Host "1. Make sure you have installed all required packages (except sentence-transformers):" -ForegroundColor Yellow
Write-Host "   pip install -r simple_requirements.txt"
Write-Host "   or"
Write-Host "   pip install dash dash-bootstrap-components plotly pandas numpy fastapi uvicorn openpyxl requests"
Write-Host 

Write-Host "2. Starting the Simple Suggestion API..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python simple_suggestion_api.py"
Write-Host 

Write-Host "3. Starting the Enhanced Dashboard..." -ForegroundColor Green
Write-Host "   Opening dashboard at http://127.0.0.1:8050/"
Write-Host 

Start-Sleep -Seconds 5
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python enhanced_dashboard.py"
Write-Host 

Write-Host "Both services are running. You can access the dashboard at:" -ForegroundColor Cyan
Write-Host "http://127.0.0.1:8050/" -ForegroundColor Cyan
Write-Host 

Write-Host "Press any key to shut down both services..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Get-Process | Where-Object { $_.MainWindowTitle -like "*simple_suggestion_api.py*" } | Stop-Process -Force
Get-Process | Where-Object { $_.MainWindowTitle -like "*enhanced_dashboard.py*" } | Stop-Process -Force
