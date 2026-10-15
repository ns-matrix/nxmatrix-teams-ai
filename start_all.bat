@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title NX Matrix AI - Local Launcher

echo.
echo =====================================================
echo          NX MATRIX AI - ONE CLICK LAUNCHER
echo =====================================================
echo This starts the local bot only. It does NOT open a
echo public tunnel or expose Ollama to the internet.
echo.

if not exist "pyproject.toml" (
  echo ERROR: Run this script from the repository root.
  pause
  exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python 3.12 or later was not found on PATH.
  echo Install Python and enable "Add Python to PATH".
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  python -m venv .venv
  if errorlevel 1 goto :error
)

echo Installing/verifying dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

if not exist ".env" (
  copy ".env.example" ".env" >nul
  if errorlevel 1 goto :error
  echo.
  echo Created .env. Open it and set API_BASE_URL, API_KEY,
  echo API_MODEL and Teams authentication settings first.
  notepad ".env"
  echo Save .env, close Notepad, then rerun start_all.bat.
  pause
  exit /b 0
)

echo.
echo Select the mode for this launch:
echo 1. Local Agents Playground / emulator (localhost only)
echo 2. Authenticated Teams bot (registered credentials required)
echo 3. Run API connectivity test only
echo 4. Run Python tests only
echo 5. Exit
choice /c 12345 /n /m "Choose 1-5: "
if errorlevel 5 goto :end
if errorlevel 4 goto :tests
if errorlevel 3 goto :apitest
if errorlevel 2 goto :authenticated
if errorlevel 1 goto :local

:local
echo.
echo LOCAL MODE: the authentication bypass is set only for the
echo child process launched by this script. Keep the bot local.
echo Do not start a public tunnel in this mode.
start "NX Matrix AI - Local Bot" /D "%~dp0" cmd /k "set DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS=true && .venv\Scripts\python.exe src\main.py"
goto :openplayground

:authenticated
echo.
echo Starting with credentials configured in .env.
echo If credentials are missing, the bot will exit safely.
start "NX Matrix AI - Authenticated Bot" /D "%~dp0" cmd /k "set DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS= && .venv\Scripts\python.exe src\main.py"
goto :openplayground

:openplayground
timeout /t 2 /nobreak >nul
start "" "%~dp0docs\index.html"
start "" "https://learn.microsoft.com/microsoftteams/platform/"
echo.
echo Bot terminal opened in a separate window.
echo Local messaging endpoint: http://localhost:3978/api/messages
echo Use Microsoft 365 Agents Playground to send messages.
echo Keep the bot window open; stop it with Ctrl+C.
echo.
pause
goto :end

:apitest
".venv\Scripts\python.exe" check_api.py
pause
goto :end

:tests
".venv\Scripts\python.exe" -m compileall -q src check_api.py tests
if errorlevel 1 goto :error
".venv\Scripts\python.exe" -m unittest discover -s tests -v
if errorlevel 1 goto :error
".venv\Scripts\python.exe" -m pip check
pause
goto :end

:error
echo.
echo ERROR: A setup or command step failed. Read the error above.
pause
exit /b 1

:end
exit /b 0
