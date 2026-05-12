@echo off
REM Merlin MLM Dashboard - Streamlit Cloud Deployment Script for Windows

echo.
echo ========================================
echo Merlin MLM Dashboard - Deployment Setup
echo ========================================
echo.

REM Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [X] Git is not installed. Please install from https://git-scm.com
    pause
    exit /b 1
)

echo [OK] Git is installed
echo.

REM Initialize git if needed
if not exist .git (
    echo Initializing git repository...
    git init
    git config user.name "MLM Dashboard Dev"
    git config user.email "dev@merlin-mlm.local"
    echo [OK] Git initialized
) else (
    echo [OK] Git repository already initialized
)

echo.
echo Checking required files...
echo.

REM Check required files
setlocal enabledelayedexpansion
set "missing_count=0"

for %%F in (
    "app.py"
    "ml_engine.py"
    "pipeline.py"
    "requirements.txt"
    "README.md"
    ".gitignore"
    ".streamlit\config.toml"
) do (
    if exist %%F (
        echo [OK] %%F
    ) else (
        echo [X] %%F ^(MISSING^)
        set /a missing_count+=1
    )
)

echo.

if %missing_count% equ 0 (
    echo [OK] All required files are present!
) else (
    echo [X] %missing_count% file(s) missing. Please create them first.
    pause
    exit /b 1
)

echo.
echo Checking Python dependencies...

python -m pip install -r requirements.txt --quiet --dry-run >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] All dependencies can be installed
) else (
    echo [?] Some dependencies may have issues
)

echo.
echo Checking database...

if exist "processed_db\warehouse.db" (
    for %%A in ("processed_db\warehouse.db") do (
        set "size=%%~zA"
    )
    set /a size_mb=size/1024/1024
    echo [OK] Database exists ^(~!size_mb! MB^)
) else (
    echo [?] Database not found. It will be created on first run.
)

echo.
echo ========================================
echo Ready to Deploy!
echo ========================================
echo.
echo Next steps:
echo 1. Create repository on GitHub: https://github.com/new
echo 2. Run: git add . ^&^& git commit -m "Initial commit"
echo 3. Run: git remote add origin https://github.com/USERNAME/repo.git
echo 4. Run: git push -u origin main
echo 5. Go to https://share.streamlit.io and deploy!
echo.
echo For detailed instructions, see DEPLOYMENT.md
echo.
pause
