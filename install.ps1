# ZipLoot AI Subtitle & Voice Dubbing Studio 1-Click Windows PowerShell Installer
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "   ZipLoot AI Subtitle Transcriber & Voice Dubbing Studio Installer" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python 3.10+ is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/ and rerun." -ForegroundColor Yellow
    Read-Host "Press Enter to exit..."
    exit
}

Write-Host "[1/3] Installing Python Dependencies..." -ForegroundColor Green
pip install -r requirements.txt

Write-Host "[2/3] Configuring System FFmpeg Executables..." -ForegroundColor Green
python install_ffmpeg_system.py

Write-Host "[3/3] Starting Application Server on http://localhost:7870 ..." -ForegroundColor Green
Start-Process "http://localhost:7870"
python -X utf8 run_app.py
