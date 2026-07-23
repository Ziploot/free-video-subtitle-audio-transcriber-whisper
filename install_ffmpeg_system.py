import os
import shutil
import sys

import imageio_ffmpeg
ffmpeg_src = imageio_ffmpeg.get_ffmpeg_exe()
print("Source FFmpeg:", ffmpeg_src)

python_dir = os.path.dirname(sys.executable)
scripts_dir = os.path.join(python_dir, "Scripts")

target_python_ffmpeg = os.path.join(python_dir, "ffmpeg.exe")
target_scripts_ffmpeg = os.path.join(scripts_dir, "ffmpeg.exe")

shutil.copyfile(ffmpeg_src, target_python_ffmpeg)
print("Copied to Python dir:", target_python_ffmpeg)

shutil.copyfile(ffmpeg_src, target_scripts_ffmpeg)
print("Copied to Python Scripts dir:", target_scripts_ffmpeg)
