@echo off
echo Cybersecurity KPI Dashboard - Git Push Helper
echo =============================================
echo.
echo This script will help push your project to GitHub
echo Repository: https://github.com/TejasParekh5/AO-Dashboard.git
echo.

REM Check if Git is installed
git --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed or not in your PATH.
    echo Please install Git from https://git-scm.com/downloads
    echo.
    pause
    exit /b 1
)

REM Check if the directory is already a git repository
if not exist .git (
    echo Initializing new Git repository...
    git init
    if %errorlevel% neq 0 (
        echo ERROR: Failed to initialize Git repository.
        pause
        exit /b 1
    )
) else (
    echo Git repository already exists.
)

REM Create .gitignore file if it doesn't exist
if not exist .gitignore (
    echo Creating .gitignore file...
    (
        echo # Python generated files
        echo __pycache__/
        echo *.py[cod]
        echo *$py.class
        echo *.so
        echo .Python
        echo env/
        echo build/
        echo develop-eggs/
        echo dist/
        echo downloads/
        echo eggs/
        echo .eggs/
        echo lib/
        echo lib64/
        echo parts/
        echo sdist/
        echo var/
        echo *.egg-info/
        echo .installed.cfg
        echo *.egg
        echo.
        echo # Virtual environment
        echo .venv/
        echo venv/
        echo ENV/
        echo.
        echo # ML models directory (may be large)
        echo # models/
        echo.
        echo # IDE files
        echo .idea/
        echo .vscode/
        echo *.swp
        echo *.swo
        echo.
        echo # OS specific files
        echo .DS_Store
        echo Thumbs.db
        echo.
        echo # Excel temp files
        echo ~$*.xlsx
        echo.
        echo # Backup files
        echo backup_simplified_files/
    ) > .gitignore
)

REM Add remote if it doesn't exist
git remote -v | findstr "origin" > nul
if %errorlevel% neq 0 (
    echo Adding GitHub repository as remote...
    git remote add origin https://github.com/TejasParekh5/AO-Dashboard.git
) else (
    echo Remote already exists.
)

REM Add all files
echo.
echo Adding all files to Git...
git add .
if %errorlevel% neq 0 (
    echo ERROR: Failed to add files to Git.
    pause
    exit /b 1
)

REM Commit changes
echo.
echo Committing changes...
git commit -m "Initial commit of Cybersecurity KPI Dashboard"
if %errorlevel% neq 0 (
    echo.
    echo NOTE: No changes to commit or commit failed.
    echo If you've already committed, this is fine.
    echo.
)

REM Push to GitHub
echo.
echo Pushing to GitHub repository...
echo This may prompt for your GitHub credentials.
echo.
git push -u origin master
if %errorlevel% neq 0 (
    echo.
    echo Trying with 'main' branch instead of 'master'...
    git push -u origin main
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to push to GitHub.
        echo Possible reasons:
        echo - You need to authenticate with GitHub
        echo - The repository already has content that needs to be pulled first
        echo - Branch name issues (master vs main)
        echo.
        echo Try running these commands manually if needed:
        echo git pull origin master --allow-unrelated-histories
        echo git push -u origin master
        echo.
        echo OR:
        echo git branch -M main
        echo git pull origin main --allow-unrelated-histories
        echo git push -u origin main
        echo.
    )
)

echo.
echo Process completed.
echo Visit your repository at: https://github.com/TejasParekh5/AO-Dashboard
echo.
pause
