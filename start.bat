@echo off
:: Ensure the script runs in its own directory (important when running as Admin)
cd /d "%~dp0"

echo ========================================
echo       EventViewer 2 - Startup
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python from python.org
    pause
    exit /b
)

echo [1/2] Installing/Updating dependencies...
pip install -r requirements.txt --quiet

echo [2/2] Starting application...
echo.
echo Application will open in your browser automatically.
echo Keep this window open while using the app.
echo.

python app.py

pause
