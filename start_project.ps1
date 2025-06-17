# PowerShell script to start the Cybersecurity Dashboard with API
Write-Host "Cybersecurity KPI Dashboard Startup Script" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Get the script directory
$ScriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Set-Location $ScriptDir

# Check if virtual environment exists
$VenvPath = "$ScriptDir\.venv\Scripts\python.exe"
if (-not (Test-Path $VenvPath)) {
    Write-Host "ERROR: Virtual environment not found at .venv" -ForegroundColor Red
    Write-Host "Please run the setup script first." -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting Suggestion API..." -ForegroundColor Green
# Start the API in a new PowerShell window
$APIJob = Start-Process powershell -ArgumentList "-Command", "cd '$ScriptDir'; & '$VenvPath' suggestion_api.py" -WindowStyle Normal -PassThru

# Wait for API to start
Write-Host "Waiting for API to initialize (5 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test if API is running
try {
    $Response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -Method GET -TimeoutSec 5
    Write-Host "API is running successfully!" -ForegroundColor Green
} catch {
    Write-Host "WARNING: API might not be ready yet. Dashboard will show errors until API starts." -ForegroundColor Yellow
}

Write-Host "Starting Dashboard..." -ForegroundColor Green
Write-Host "Dashboard will be available at: http://127.0.0.1:8050/" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop both services" -ForegroundColor Yellow

# Start the dashboard (this will block until stopped)
try {
    & $VenvPath enhanced_dashboard.py
} finally {
    # Clean up: stop the API process when dashboard stops
    if ($APIJob -and !$APIJob.HasExited) {
        Write-Host "Stopping API..." -ForegroundColor Yellow
        Stop-Process -Id $APIJob.Id -Force -ErrorAction SilentlyContinue
    }
}
