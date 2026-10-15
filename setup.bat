@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo ============================================
echo       NX MATRIX AI - SETUP AND LAUNCHER
echo ============================================
echo.

if not exist "pyproject.toml" (
  echo ERROR: Run this script from the project root.
  pause
  exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python was not found. Install Python 3.12 or later and enable Add Python to PATH.
  pause
  exit /b 1
)

echo [1/4] Creating virtual environment if needed...
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 goto :error
)

echo [2/4] Upgrading pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error

echo [3/4] Installing project dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo [4/4] Preparing .env configuration...
if not exist ".env" (
  copy ".env.example" ".env" >nul
  if errorlevel 1 goto :error
  echo Created .env from .env.example. Edit it if needed.
) else (
  echo Existing .env preserved.
)

:menu
echo.
echo ================ NX MATRIX AI ================
echo 1. Run bot locally
echo 2. Test LLM API configuration
echo 3. Check configuration and dependencies
echo 4. Start Microsoft Dev Tunnel
echo 5. Edit .env in Notepad
echo 6. Exit
echo ==============================================
choice /c 123456 /n /m "Choose 1-6: "
if errorlevel 6 goto :end
if errorlevel 5 goto :edit
if errorlevel 4 goto :tunnel
if errorlevel 3 goto :check
if errorlevel 2 goto :test
if errorlevel 1 goto :run

:run
echo Starting NX Matrix AI on port %BOT_PORT%. Leave this window open; use Ctrl+C to stop the bot.
".venv\Scripts\python.exe" src\main.py
echo Bot process stopped.
goto :menu

:test
".venv\Scripts\python.exe" check_api.py
if errorlevel 1 echo LLM API test failed. Review the message above.
pause
goto :menu

:check
echo Python:
".venv\Scripts\python.exe" --version
echo Dependency check:
".venv\Scripts\python.exe" -m pip check
echo LLM connectivity check:
".venv\Scripts\python.exe" check_api.py
pause
goto :menu

:tunnel
call run_tunnel.bat
goto :menu

:edit
if not exist ".env" copy ".env.example" ".env" >nul
notepad ".env"
goto :menu

:error
echo.
echo ERROR: Setup failed. Check the error above and retry setup.bat.
pause
exit /b 1

:end
echo Exiting setup.
exit /b 0
