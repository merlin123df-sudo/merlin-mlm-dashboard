@echo off
REM MERLIN MLM DASHBOARD - QUICK DEPLOY SCRIPT

echo.
echo ========================================
echo MERLIN MLM DASHBOARD - AUTO DEPLOY
echo ========================================
echo.

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Git not found! Download from https://git-scm.com/
    pause
    exit /b
)

echo [STEP 1] Git found - initializing repository...
cd /d "c:\Users\amjad\OneDrive\Documents\python"

REM Initialize Git if not already done
if not exist ".git" (
    git init
    echo OK - Git repository initialized
) else (
    echo OK - Git repository already exists
)

REM Configure Git
echo [STEP 2] Configuring Git...
git config user.name "Merlin User"
git config user.email "merlin@mlm.com"
echo OK - Git configured

REM Add all files
echo [STEP 3] Adding files...
git add .
echo OK - Files added

REM Commit
echo [STEP 4] Committing...
git commit -m "Merlin MLM Dashboard - Fast Version (120s cache)" 2>nul
echo OK - Changes committed

REM Check git status
git status

echo.
echo ========================================
echo NEXT STEPS (IN BROWSER):
echo ========================================
echo.
echo 1) Create GitHub Repository:
echo    Go to: https://github.com/new
echo    Name: merlin-mlm-dashboard
echo    Visibility: PUBLIC
echo.
echo 2) Push Code:
echo    Copy this command in Terminal:
echo    git push -u origin main
echo    (after adding remote origin with your GitHub URL)
echo.
echo 3) Deploy on Streamlit Cloud:
echo    Go to: https://share.streamlit.io
echo    Select your repository
echo    Click Deploy
echo.
echo 4) Live Dashboard:
echo    https://merlin-mlm-dashboard.streamlit.app
echo.
echo ========================================
echo READY FOR DEPLOYMENT!
echo ========================================
echo.
pause
