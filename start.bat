@echo off
:: Ensure the script runs in its own directory
cd /d "%~dp0"

:: 0. Check for Administrator privileges and elevate if needed
net sessions >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] High privileges required. Elevating...
    powershell -Command "Start-Process '%~0' -Verb RunAs"
    exit /b
)

echo ========================================
echo       EventViewer Pro - Startup
echo ========================================
echo.

set "INSTALLED_ANY=0"

:: 1. Check winget
winget --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] winget not found! 
    echo Please install "App Installer" from Microsoft Store.
    pause
    exit /b
)

:: 2. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Python not found. Searching via winget...
    winget search --id Python.Python.3.12 --source winget
    echo.
    echo [INFO] Installing Python 3.12...
    winget install --id Python.Python.3.12 --source winget --accept-package-agreements --accept-source-agreements
    echo.
    set "INSTALLED_ANY=1"
)

:: 3. Check npm (Node.js)
call npm -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Node.js/npm not found. Searching via winget...
    winget search --id OpenJS.NodeJS.LTS --source winget
    echo.
    echo [INFO] Installing Node.js LTS...
    winget install --id OpenJS.NodeJS.LTS --source winget --accept-package-agreements --accept-source-agreements
    echo.
    set "INSTALLED_ANY=1"
)

:: If something was installed, we MUST restart to refresh PATH for pip/npm calls
if "%INSTALLED_ANY%"=="1" (
    echo [SUCCESS] Installation process finished!
    echo.
    echo IMPORTANT: Please RESTART this script to apply environment changes.
    pause
    exit /b
)

:START_APP
echo [1/2] Installing/Updating Python dependencies...
call pip install -r requirements.txt --quiet

:: 4. Build frontend if dist folder is missing
if not exist "frontend\dist" (
    echo [INFO] Frontend build not found. Starting build process...
    cd frontend
    call npm install
    call npm run build
    cd ..
)

echo [2/2] Starting application...
echo.
echo Application will open in your browser automatically.
echo Keep this window open while using the app.
echo.

python app.py
pause
