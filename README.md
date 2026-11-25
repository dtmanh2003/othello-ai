# Othello AI

An Othello (Reversi) game written in Python with pygame. You play against an AI that searches moves with minimax and alpha-beta pruning (depth 4).

The folder also has the original C version of the game (`CL31_kadai4_13_DUONGMANH.c`) and a PDF report on the AI (`othello_ai_report.pdf`).

## Run

```powershell
pip install pygame numpy
python othello_pygame.py
```

On Windows you can also double-click `play_othello.bat`.

## Build an .exe

```powershell
pip install pyinstaller
pyinstaller Othello.spec
```

The executable is written to `dist/Othello.exe`.

## Files

- `othello_pygame.py`: the game (board logic, AI, sound, drawing)
- `CL31_kadai4_13_DUONGMANH.c`: the console C version
- `generate_report.py`: builds `othello_ai_report.pdf` with reportlab (needs the Noto Sans JP and MS Gothic fonts on Windows)
- `Othello.spec`: PyInstaller build settings
