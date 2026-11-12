@echo off
cd /d "%~dp0"
where ffmpeg >nul 2>nul
if errorlevel 1 (echo FFmpeg not found in PATH. Install FFmpeg and add bin to PATH.& pause & exit /b 1)
where ffprobe >nul 2>nul
if errorlevel 1 (echo FFprobe not found. It is normally included with FFmpeg.& pause & exit /b 1)
python helper.py
pause
