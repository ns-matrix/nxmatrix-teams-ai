@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run setup.bat first.
  pause
  exit /b 1
)
if not exist ".env" copy ".env.example" ".env" >nul
".venv\Scripts\python.exe" check_api.py
pause
