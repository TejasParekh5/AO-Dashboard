# Setting up Git Repository for Cybersecurity KPI Dashboard
Write-Host "======================================================"
Write-Host "     Setting up Git Repository for Cybersecurity KPI Dashboard"
Write-Host "======================================================"
Write-Host ""

# Step 1: Initialize Git repository
Write-Host "Step 1: Initializing Git repository..."
git init
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error initializing Git repository." -ForegroundColor Red
    exit
}
Write-Host "Git repository initialized successfully." -ForegroundColor Green
Write-Host ""

# Step 2: Add all files to Git
Write-Host "Step 2: Adding all files to Git..."
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error adding files to Git." -ForegroundColor Red
    exit
}
Write-Host "Files added successfully." -ForegroundColor Green
Write-Host ""

# Step 3: Make initial commit
Write-Host "Step 3: Making initial commit..."
git commit -m "Initial commit of Cybersecurity KPI Dashboard"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error making initial commit." -ForegroundColor Red
    exit
}
Write-Host "Initial commit created successfully." -ForegroundColor Green
Write-Host ""

# Instructions for next steps
Write-Host "======================================================"
Write-Host "Now you need to create a repository on GitHub, GitLab, or another Git hosting service."
Write-Host ""
Write-Host "After creating the repository, run the following commands:" -ForegroundColor Yellow
Write-Host ""
Write-Host "git remote add origin YOUR_REPOSITORY_URL" -ForegroundColor Cyan
Write-Host "git push -u origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "For example:" -ForegroundColor Yellow
Write-Host "git remote add origin https://github.com/yourusername/cybersecurity-kpi-dashboard.git" -ForegroundColor Cyan
Write-Host "git push -u origin main" -ForegroundColor Cyan
Write-Host "======================================================"

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
