@echo off
title Birthday Celebration — Colored ASCII Cinematic Animation ✨
echo =======================================================
echo    Birthday Celebration — Colored ASCII Animation ✨
echo =======================================================
echo.

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    echo Launching with virtual environment...
    ".venv\Scripts\python.exe" main.py
    goto end
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    echo Launching with Python Launcher...
    py -3 main.py
    goto end
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    echo Launching with system Python...
    python main.py
    goto end
)

echo [ERROR] Python not found! Please install Python 3.10+ and add it to PATH.
pause

:end
