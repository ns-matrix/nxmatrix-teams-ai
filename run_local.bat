@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run setup.bat first.
  pause
  exit /b 1
)
if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo Created .env. Review it before continuing.
)
echo Starting NX Matrix AI on port 3978...
".venv\Scripts\python.exe" src\main.py
pause
