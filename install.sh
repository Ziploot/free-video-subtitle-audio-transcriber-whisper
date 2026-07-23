#!/usr/bin/env bash
# ZipLoot AI Subtitle & Voice Dubbing Studio 1-Click Bash Installer (Linux & macOS)
cd "$(dirname "$0")" || exit

echo "====================================================================="
echo "   ZipLoot AI Subtitle Transcriber & Voice Dubbing Studio Installer"
echo "====================================================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed. Please install Python 3.10+."
    exit 1
fi

echo "[1/3] Installing Python Dependencies..."
pip3 install -r requirements.txt

echo "[2/3] Configuring FFmpeg..."
python3 install_ffmpeg_system.py

echo "[3/3] Launching Server on http://localhost:7870 ..."
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:7870"
elif command -v open &> /dev/null; then
    open "http://localhost:7870"
fi

python3 -X utf8 run_app.py
