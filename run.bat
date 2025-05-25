@echo off

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Run the Gradio app
python gradio_app.py
