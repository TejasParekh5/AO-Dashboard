# ====================================================================
# CYBERSEC PRO DASHBOARD - COMPLETE STARTUP SCRIPT
# ====================================================================

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🚀 CYBERSEC PRO DASHBOARD - INTELLIGENT STARTUP" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Cyan

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $listener = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners()
        return $listener | Where-Object { $_.Port -eq $Port }
    }
    catch {
        return $false
    }
}

# Function to kill process on port
function Stop-ProcessOnPort {
    param([int]$Port)
    try {
        $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object OwningProcess
        foreach ($process in $processes) {
            Stop-Process -Id $process.OwningProcess -Force -ErrorAction SilentlyContinue
            Write-Host "   ✅ Stopped process on port $Port" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "   ⚠️  Could not stop process on port $Port" -ForegroundColor Yellow
    }
}

# Check Python installation
Write-Host "🔍 Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
    pause
    exit 1
}

# Check if in correct directory
Write-Host "📁 Verifying directory structure..." -ForegroundColor Cyan
$requiredFiles = @(
    "dashboard_optimized.py",
    "api_optimized.py", 
    "requirements.txt",
    "Cybersecurity_KPI_Minimal.xlsx"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ Found: $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Missing: $file" -ForegroundColor Red
        if ($file -eq "api_optimized.py") {
            Write-Host "   💡 Falling back to suggestion_api.py" -ForegroundColor Yellow
        }
    }
}

# Install/Update dependencies
Write-Host "📦 Checking Python dependencies..." -ForegroundColor Cyan
try {
    pip install -r requirements.txt --quiet --upgrade
    Write-Host "   ✅ Dependencies installed/updated" -ForegroundColor Green
}
catch {
    Write-Host "   ⚠️  Some dependencies may have issues" -ForegroundColor Yellow
}

# Check and start API server
Write-Host "🔧 Managing API Server..." -ForegroundColor Cyan
$apiPort = 8000
$dashboardPort = 8050

# Stop existing processes
if (Test-Port $apiPort) {
    Write-Host "   🔄 Stopping existing API server on port $apiPort..." -ForegroundColor Yellow
    Stop-ProcessOnPort $apiPort
    Start-Sleep -Seconds 2
}

if (Test-Port $dashboardPort) {
    Write-Host "   🔄 Stopping existing dashboard on port $dashboardPort..." -ForegroundColor Yellow
    Stop-ProcessOnPort $dashboardPort
    Start-Sleep -Seconds 2
}

# Start API server
Write-Host "   🚀 Starting API server..." -ForegroundColor Cyan
$apiFile = if (Test-Path "api_optimized.py") { "api_optimized.py" } else { "suggestion_api.py" }

$apiProcess = Start-Process python -ArgumentList $apiFile -WindowStyle Hidden -PassThru
if ($apiProcess) {
    Write-Host "   ✅ API server started (PID: $($apiProcess.Id))" -ForegroundColor Green
    
    # Wait for API to be ready
    Write-Host "   ⏳ Waiting for API to be ready..." -ForegroundColor Yellow
    $maxRetries = 30
    $retries = 0
    
    do {
        Start-Sleep -Seconds 1
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "   ✅ API server is ready!" -ForegroundColor Green
                break
            }
        }
        catch {
            $retries++
        }
    } while ($retries -lt $maxRetries)
    
    if ($retries -ge $maxRetries) {
        Write-Host "   ⚠️  API server may not be fully ready, but continuing..." -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ Failed to start API server" -ForegroundColor Red
}

# Start Dashboard
Write-Host "🖥️  Starting Enhanced Dashboard..." -ForegroundColor Cyan
$dashboardFile = if (Test-Path "dashboard_optimized.py") { "dashboard_optimized.py" } else { "enhanced_dashboard.py" }

Write-Host "   📊 Using: $dashboardFile" -ForegroundColor Cyan
Write-Host "   🌐 Dashboard will be available at: http://localhost:8050" -ForegroundColor Green
Write-Host "   🤖 API endpoints available at: http://localhost:8000" -ForegroundColor Green
Write-Host "" -ForegroundColor White
Write-Host "🎯 FEATURES ENABLED:" -ForegroundColor Yellow
Write-Host "   ✨ Modern responsive UI" -ForegroundColor White
Write-Host "   📈 Real-time analytics" -ForegroundColor White
Write-Host "   🧠 AI-powered insights" -ForegroundColor White
Write-Host "   💬 Interactive chatbot" -ForegroundColor White
Write-Host "   📊 Advanced visualizations" -ForegroundColor White
Write-Host "   📤 Export functionality" -ForegroundColor White
Write-Host "   🔄 Auto-refresh capabilities" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🎉 LAUNCHING DASHBOARD..." -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan

try {
    # Start dashboard in foreground so we can see output
    python $dashboardFile
}
catch {
    Write-Host "❌ Error starting dashboard: $_" -ForegroundColor Red
    Write-Host "" -ForegroundColor White
    Write-Host "🔧 TROUBLESHOOTING TIPS:" -ForegroundColor Yellow
    Write-Host "   1. Check if port 8050 is available" -ForegroundColor White
    Write-Host "   2. Ensure Python dependencies are installed" -ForegroundColor White
    Write-Host "   3. Verify Excel file exists" -ForegroundColor White
    Write-Host "   4. Check API server logs" -ForegroundColor White
    Write-Host "   5. Try running as administrator" -ForegroundColor White
}
finally {
    Write-Host "" -ForegroundColor White
    Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
    if ($apiProcess -and !$apiProcess.HasExited) {
        Write-Host "   🔄 Stopping API server..." -ForegroundColor Yellow
        Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "   ✅ Cleanup complete" -ForegroundColor Green
    Write-Host "" -ForegroundColor White
    Write-Host "👋 Thank you for using CyberSec Pro Dashboard!" -ForegroundColor Cyan
    pause
}
