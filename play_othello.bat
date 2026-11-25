@echo off
cd /d "%~dp0"
python othello_pygame.py
if errorlevel 1 (
    echo.
    echo [ERROR] Something went wrong. Make sure Python and pygame are installed.
    echo Run: pip install pygame numpy
    pause
)
