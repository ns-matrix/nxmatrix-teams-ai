@echo off
setlocal EnableExtensions
cd /d "%~dp0"
where devtunnel >nul 2>nul
if errorlevel 1 (
  echo Microsoft Dev Tunnels CLI not found.
  echo Install with: winget install Microsoft.devtunnel
  pause
  exit /b 1
)
if not exist ".env" (
  echo ERROR: .env is missing. Run setup.bat first.
  pause
  exit /b 1
)
findstr /I /R /C:"^[ ]*DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS[ ]*=[ ]*true[ ]*$" ".env" >nul
if not errorlevel 1 (
  echo ERROR: Unauthenticated local mode is enabled in .env.
  echo Comment out DANGEROUSLY_ALLOW_UNAUTHENTICATED_REQUESTS before using a public tunnel.
  pause
  exit /b 1
)
findstr /R /C:"^CLIENT_ID=.[^ ]*" ".env" >nul
if errorlevel 1 goto :missing_credentials
findstr /R /C:"^CLIENT_SECRET=.[^ ]*" ".env" >nul
if errorlevel 1 goto :missing_credentials
findstr /R /C:"^TENANT_ID=.[^ ]*" ".env" >nul
if errorlevel 1 goto :missing_credentials
set "BOT_PORT=3978"
for /f "tokens=1,* delims==" %%A in ('findstr /B /I "BOT_PORT=" ".env"') do set "BOT_PORT=%%B"
echo Start the bot in a separate terminal before hosting this tunnel.
echo This tunnel is for temporary development only; treat its URL as public.
echo Forwarding port %BOT_PORT%. Do not expose the Ollama port 11434.
echo If a new tunnel URL is generated, update the registered messaging endpoint.
devtunnel user login
if errorlevel 1 goto :error
devtunnel create --allow-anonymous
if errorlevel 1 goto :error
devtunnel port create -p %BOT_PORT%
if errorlevel 1 goto :error
devtunnel host
pause
exit /b 0
:missing_credentials
echo ERROR: Public tunneling requires CLIENT_ID, CLIENT_SECRET, and TENANT_ID in .env.
echo Configure a registered Teams bot first. Local emulator mode must not be exposed.
pause
exit /b 1
:error
echo Tunnel command failed. Check the error above.
pause
exit /b 1
