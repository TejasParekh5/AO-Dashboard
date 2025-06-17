@echo off
echo ======================================================
echo     Setting up Git Repository for Cybersecurity KPI Dashboard
echo ======================================================
echo.

echo Step 1: Initializing Git repository...
git init
if %errorlevel% neq 0 (
    echo Error initializing Git repository.
    goto error
)
echo Git repository initialized successfully.
echo.

echo Step 2: Adding all files to Git...
git add .
if %errorlevel% neq 0 (
    echo Error adding files to Git.
    goto error
)
echo Files added successfully.
echo.

echo Step 3: Making initial commit...
git commit -m "Initial commit of Cybersecurity KPI Dashboard"
if %errorlevel% neq 0 (
    echo Error making initial commit.
    goto error
)
echo Initial commit created successfully.
echo.

echo ======================================================
echo Now you need to create a repository on GitHub, GitLab, or another Git hosting service.
echo.
echo After creating the repository, run the following commands:
echo.
echo git remote add origin YOUR_REPOSITORY_URL
echo git push -u origin main
echo.
echo For example:
echo git remote add origin https://github.com/yourusername/cybersecurity-kpi-dashboard.git
echo git push -u origin main
echo ======================================================
echo.
goto end

:error
echo.
echo An error occurred during the Git setup process.
echo Please check the error message above and try again.

:end
pause
