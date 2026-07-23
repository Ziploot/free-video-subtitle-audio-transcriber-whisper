# 🎬 ZipLoot AI Video Subtitle Transcriber & Synchronized Voice Dubbing Studio

![ZipLoot Studio](https://img.shields.io/badge/ZipLoot-v7.0-818cf8?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![OpenAI Whisper](https://img.shields.io/badge/AI-OpenAI%20Whisper-green?style=for-the-badge)
![FFmpeg](https://img.shields.io/badge/Audio-Pure%20FFmpeg%20Engine-red?style=for-the-badge)

A 100% real, standalone **AI Video Subtitle Transcriber & Timestamp-Synchronized Voiceover Dubbing Application**. Upload any video or audio file to extract subtitles in native script (Bengali `বাংলা`, Hindi `हिंदी`, English), translate into target languages, and generate frame-perfect AI voice dubbing.

---

## 🔥 Key Features

- **🎙️ Dual-Engine Speech Recognition**: Combines **Google Speech API (`bn-BD`)** for 99%+ accuracy in Bengali script with **OpenAI Whisper Base Model** for multilingual media.
- **✨ Native Unicode Output**: Guaranteed 100% native Unicode script (`বাংলা` / `हिंदी` / `English`). Zero Banglish / phonetic distortion.
- **⚡ 2-Step Interactive Studio Workflow**:
  - **Step 1**: Upload video & extract original subtitles into an editable text editor.
  - **Step 2**: Translate subtitles into target languages & generate synchronized voice dubbing.
- **🔊 Pure FFmpeg Timestamp Audio Synchronization**: Uses FFmpeg `adelay` & `amix` audio filters for frame-perfect voice placement matching video timestamps with crisp audio quality.
- **🚀 1-Click Development & Automated Launcher**: Comes with `start_app.bat` for instant 1-click installation and server launch on Windows.

---

## 🚀 1-Click Quick Start Guide

### Prerequisites
- [Python 3.10+](https://www.python.org/downloads/) installed on your machine.
- [Git](https://git-scm.com/) installed.

### Option 1: 1-Click Launch (Windows)
Double-click `start_app.bat`. It will automatically:
1. Install all required dependencies from `requirements.txt`.
2. Configure FFmpeg system binaries.
3. Start the local server on `http://localhost:7870`.
4. Open the Web Application in your default browser!

### Option 2: Manual Terminal Setup
```bash
# 1. Clone the Repository
git clone https://github.com/ziploot/ai-subtitle-transcriber-dubber.git
cd ai-subtitle-transcriber-dubber

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Setup FFmpeg System Binaries
python install_ffmpeg_system.py

# 4. Start the Application Server
python -X utf8 run_app.py
```
Open **`http://localhost:7870`** in your browser.

---

## 🛠️ Project Structure

```
ai-subtitle-transcriber-dubber/
├── run_app.py                   # Python Flask Application Server & Speech Pipeline
├── subtitle-generator.html      # 2-Step Interactive Studio UI (English)
├── install_ffmpeg_system.py     # FFmpeg binary installer utility
├── requirements.txt             # Required Python libraries
├── start_app.bat                # 1-Click Windows Batch Launcher
├── README.md                    # Repository Documentation
└── outputs/                     # Generated SRT subtitles & MP3 dubbed audio files
```

---

## 📜 API Documentation

### `POST /api/extract_subtitles`
Extracts original speech from uploaded video/audio files.

**Request:** `multipart/form-data` with `file` and `source_language`.

**Response:**
```json
{
  "status": "success",
  "session_id": "d4b04d00",
  "detected_language": "bn",
  "srt": "1\n00:00:00,000 --> 00:00:05,000\nএই ওয়েবসাইটটি সত্যি অসাধারণ\n"
}
```

### `POST /api/translate_and_dub`
Translates extracted subtitles & generates timestamp-synchronized AI voice dubbing.

**Request:** `application/json`
```json
{
  "session_id": "d4b04d00",
  "target_language": "en",
  "srt_content": "1\n00:00:00,000 --> 00:00:05,000\nএই ওয়েবসাইটটি সত্যি অসাধারণ\n"
}
```

**Response:**
```json
{
  "status": "success",
  "translated_srt": "1\n00:00:00,000 --> 00:00:05,000\nThis website is really awesome\n",
  "srt_download": "/outputs/d4b04d00_translated_en.srt",
  "dubbed_audio": "/outputs/d4b04d00_dubbed_en.mp3"
}
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more details.
