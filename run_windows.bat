@echo off
title Text to Voice PRO - Setup
echo =========================================
echo   Text to Voice PRO — Multi-Language
echo =========================================
echo.
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found. Download from https://python.org
    pause & exit /b 1
)
echo Installing dependencies...
pip install gtts pygame-ce -q
echo.
echo Launching app...
python text_to_voice_pro.py
pause
