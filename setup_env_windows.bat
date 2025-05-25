@echo off

REM Create and activate a Python virtual environment
python -m venv .venv
call .venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt

REM Install ffmpeg via pip (or you can manually add ffmpeg.exe to PATH if preferred)
pip install imageio[ffmpeg]

REM OpenCV dependency for GUI backends
pip install opencv-python-headless

REM Download checkpoints using HuggingFace CLI
huggingface-cli download ByteDance/LatentSync-1.5 whisper/tiny.pt --local-dir checkpoints
huggingface-cli download ByteDance/LatentSync-1.5 latentsync_unet.pt --local-dir checkpoints
