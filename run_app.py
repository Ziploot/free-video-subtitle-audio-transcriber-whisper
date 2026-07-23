import os
import sys
import re
import uuid
import subprocess
import imageio_ffmpeg

# Configure FFmpeg environment path
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] = os.path.dirname(ffmpeg_exe) + os.pathsep + os.environ.get("PATH", "")

import speech_recognition as sr
import whisper
from deep_translator import GoogleTranslator
from gtts import gTTS
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder=".")

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SESSIONS = {}
WHISPER_MODELS = {}

def get_whisper_model(model_name="base"):
    if model_name not in WHISPER_MODELS:
        print(f"🧠 Loading OpenAI Whisper '{model_name}' model into memory...")
        WHISPER_MODELS[model_name] = whisper.load_model(model_name)
    return WHISPER_MODELS[model_name]

def format_srt_timestamp(seconds: float) -> str:
    if seconds is None or seconds < 0: seconds = 0.0
    millis = int((seconds - int(seconds)) * 1000)
    secs = int(seconds)
    hours = secs // 3600
    mins = (secs % 3600) // 60
    sc = secs % 60
    return f"{hours:02d}:{mins:02d}:{sc:02d},{millis:03d}"

def parse_srt_content(srt_text: str):
    segments = []
    blocks = re.split(r'\n\s*\n', srt_text.strip())
    for block in blocks:
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if len(lines) >= 3:
            time_line = lines[1]
            text = " ".join(lines[2:])
            time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', time_line)
            if time_match:
                start_str, end_str = time_match.groups()
                
                def to_sec(ts):
                    h, m, s_m = ts.split(':')
                    s, ms = s_m.split(',')
                    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0

                segments.append({
                    "start": to_sec(start_str),
                    "end": to_sec(end_str),
                    "text": text
                })
    return segments

def safe_translate(text: str, source_lang: str, target_lang: str) -> str:
    """Translates text with explicit language code mapping to prevent Banglish transliteration."""
    if not text or not text.strip():
        return text

    s = 'bn' if 'bn' in source_lang else ('en' if 'en' in source_lang else 'auto')
    t = 'bn' if 'bn' in target_lang else ('en' if 'en' in target_lang else target_lang)

    if s == t and s != 'auto':
        return text

    try:
        translated = GoogleTranslator(source=s, target=t).translate(text)
        return translated if translated else text
    except Exception as e:
        print("Translation notice:", e)
        return text

def extract_bengali_speech_google(wav_path: str):
    """Uses Google's High-Accuracy Speech Engine (bn-BD) to extract 100% perfect Bengali Unicode Script."""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    srt_entries = []
    structured_segments = []

    try:
        with sr.AudioFile(wav_path) as source:
            duration = int(source.DURATION)
            chunk_length = 5
            
            for i in range(0, duration, chunk_length):
                start_sec = i
                end_sec = min(i + chunk_length, duration)
                
                audio_data = recognizer.record(source, duration=chunk_length)
                try:
                    text = recognizer.recognize_google(audio_data, language="bn-BD")
                    if text.strip():
                        start_str = format_srt_timestamp(start_sec)
                        end_str = format_srt_timestamp(end_sec)
                        entry_idx = len(srt_entries) + 1
                        
                        srt_entries.append(f"{entry_idx}\n{start_str} --> {end_str}\n{text}\n")
                        structured_segments.append({
                            "start": start_sec,
                            "end": end_sec,
                            "text": text
                        })
                except (sr.UnknownValueError, sr.RequestError):
                    pass
    except Exception as e:
        print("Google Speech extraction notice:", e)

    return srt_entries, structured_segments

@app.route("/")
def index():
    return send_from_directory(".", "subtitle-generator.html")

@app.route("/outputs/<path:filename>")
def serve_output(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
        
    if filename.endswith(".mp3"):
        return send_from_directory(UPLOAD_FOLDER, filename, mimetype="audio/mpeg")
    elif filename.endswith(".srt"):
        return send_from_directory(UPLOAD_FOLDER, filename, mimetype="text/plain")
    return send_from_directory(UPLOAD_FOLDER, filename)

# STEP 1: Extract Original Subtitles
@app.route("/api/extract_subtitles", methods=["POST"])
def extract_subtitles():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    src_lang = request.form.get("source_language", "auto")

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    session_id = str(uuid.uuid4())[:8]
    filename = f"{session_id}_{file.filename}"
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    wav_path = os.path.join(UPLOAD_FOLDER, f"{session_id}_16k.wav")

    print(f"🎬 [Step 1] Extracting Subtitles from: '{filename}' | Language: '{src_lang}'")

    srt_entries = []
    structured_segments = []
    detected_lang = src_lang

    try:
        cmd = [ffmpeg_exe, "-i", input_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav_path, "-y"]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        if src_lang in ["bn", "auto"]:
            print("🎙️ Running Google High-Accuracy Speech Engine (bn-BD) for 100% Perfect Bengali Script...")
            srt_entries, structured_segments = extract_bengali_speech_google(wav_path)
            if srt_entries:
                detected_lang = "bn"

        if not srt_entries:
            print("🧠 Running OpenAI Whisper Neural Engine...")
            model = get_whisper_model("base")
            options = {"task": "transcribe"}
            if src_lang and src_lang != "auto":
                options["language"] = src_lang

            result = model.transcribe(wav_path, **options)
            detected_lang = result.get("language", src_lang if src_lang != "auto" else "en")
            segments = result.get("segments", [])

            for idx, seg in enumerate(segments, start=1):
                raw_text = seg["text"].strip()
                if not raw_text:
                    continue

                start_sec = seg["start"]
                end_sec = seg["end"]

                start_str = format_srt_timestamp(start_sec)
                end_str = format_srt_timestamp(end_sec)
                
                srt_entries.append(f"{idx}\n{start_str} --> {end_str}\n{raw_text}\n")
                structured_segments.append({
                    "start": start_sec,
                    "end": end_sec,
                    "text": raw_text
                })

    except Exception as e:
        print("Extract subtitles exception:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(wav_path):
            try: os.remove(wav_path)
            except: pass

    srt_content = "\n".join(srt_entries) if srt_entries else "1\n00:00:00,000 --> 00:00:05,000\nNo speech detected in this media."

    SESSIONS[session_id] = {
        "input_path": input_path,
        "detected_lang": detected_lang,
        "segments": structured_segments,
        "srt_content": srt_content
    }

    return jsonify({
        "status": "success",
        "session_id": session_id,
        "detected_language": detected_lang,
        "srt": srt_content
    })

# STEP 2: Translate Subtitles & Generate Synchronized AI Voice Dubbing via Pure FFmpeg Filter Assembly
@app.route("/api/translate_and_dub", methods=["POST"])
def translate_and_dub():
    data = request.get_json(force=True)
    session_id = data.get("session_id")
    target_lang = data.get("target_language", "bn")
    edited_srt = data.get("srt_content")

    if not session_id or session_id not in SESSIONS:
        return jsonify({"error": "Invalid or expired session. Please re-upload media."}), 400

    session = SESSIONS[session_id]
    input_path = session["input_path"]
    detected_src_lang = session["detected_lang"]

    print(f"🎙️ [Step 2] Translating & Dubbing Session: '{session_id}' -> Target Language: '{target_lang}'")

    if edited_srt:
        segments = parse_srt_content(edited_srt)
    else:
        segments = session["segments"]

    srt_entries = []
    translated_segments = []

    for idx, seg in enumerate(segments, start=1):
        text = seg["text"].strip()
        start_sec = seg["start"]
        end_sec = seg["end"]

        translated_text = safe_translate(text, detected_src_lang, target_lang)

        start_str = format_srt_timestamp(start_sec)
        end_str = format_srt_timestamp(end_sec)
        
        srt_entries.append(f"{idx}\n{start_str} --> {end_str}\n{translated_text}\n")
        translated_segments.append({
            "start": start_sec,
            "end": end_sec,
            "text": translated_text
        })

    translated_srt_content = "\n".join(srt_entries)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    srt_filename = f"{base_name}_translated_{target_lang}.srt"
    srt_path = os.path.join(UPLOAD_FOLDER, srt_filename)

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(translated_srt_content)

    dub_audio_filename = f"{base_name}_dubbed_{target_lang}.mp3"
    dub_audio_path = os.path.join(UPLOAD_FOLDER, dub_audio_filename)
    dubbed_audio_url = None

    if translated_segments:
        temp_seg_files = []
        try:
            print(f"🎙️ Assembling Crisp Timestamp-Synchronized Voiceover in '{target_lang}' via Pure FFmpeg...")
            
            ffmpeg_cmd = [ffmpeg_exe]
            filter_inputs = []
            filter_outputs = []

            for i, seg_info in enumerate(translated_segments):
                text_to_speak = seg_info["text"]
                start_ms = int(seg_info["start"] * 1000)
                
                temp_seg_file = os.path.join(UPLOAD_FOLDER, f"temp_seg_{session_id}_{i}.mp3")
                temp_seg_files.append(temp_seg_file)

                tts = gTTS(text=text_to_speak, lang=target_lang, slow=False)
                tts.save(temp_seg_file)

                ffmpeg_cmd.extend(["-i", temp_seg_file])
                filter_inputs.append(f"[{i}:a]adelay={start_ms}|{start_ms}[a{i}]")
                filter_outputs.append(f"[a{i}]")

            # Combine all delayed audio streams into master audio using FFmpeg amix filter
            filter_str = ";".join(filter_inputs) + ";" + "".join(filter_outputs) + f"amix=inputs={len(translated_segments)}:duration=longest[out]"
            
            ffmpeg_cmd.extend([
                "-filter_complex", filter_str,
                "-map", "[out]",
                "-c:a", "libmp3lame",
                "-q:a", "2",
                dub_audio_path,
                "-y"
            ])

            subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            dubbed_audio_url = f"/outputs/{dub_audio_filename}"
            print("✅ Pure FFmpeg Master Synchronized Audio Created:", dub_audio_path)

        except Exception as dub_err:
            print("FFmpeg Dubbing Assembly Error:", dub_err)
        finally:
            for f_tmp in temp_seg_files:
                if os.path.exists(f_tmp):
                    try: os.remove(f_tmp)
                    except: pass

    return jsonify({
        "status": "success",
        "translated_srt": translated_srt_content,
        "srt_download": f"/outputs/{srt_filename}",
        "dubbed_audio": dubbed_audio_url
    })

if __name__ == "__main__":
    port = 7870
    print(f"ZipLoot Pure FFmpeg Timestamp-Synchronized Subtitle & Dubbing Engine running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
