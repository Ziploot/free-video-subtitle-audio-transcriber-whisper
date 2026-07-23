@echo off
TITLE ZipLoot AI Subtitle Transcriber ^& Voice Dubber Studio
echo =====================================================================
echo    ZipLoot AI Subtitle Transcriber ^& Voice Dubbing Studio
echo =====================================================================
echo.
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not added to PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b
)

echo [2/3] Installing dependencies from requirements.txt...
pip install -r requirements.txt
python install_ffmpeg_system.py

echo.
echo [3/3] Starting Local Server on http://localhost:7870 ...
echo.
start "" "http://localhost:7870"
python -X utf8 run_app.py

pause
