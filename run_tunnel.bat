@echo off
setlocal
cd /d "%~dp0"
where devtunnel >nul 2>nul
if errorlevel 1 (
  echo Microsoft Dev Tunnels CLI not found.
  echo Install with: winget install Microsoft.devtunnel
  pause
  exit /b 1
)
echo Start the bot in a separate terminal before hosting this tunnel.
echo This uses anonymous tunnel access for temporary development only.
echo Do not expose the Ollama port 11434.
devtunnel user login
if errorlevel 1 goto :error
devtunnel create --allow-anonymous
if errorlevel 1 goto :error
devtunnel port create -p 3978
if errorlevel 1 goto :error
devtunnel host
pause
exit /b 0
:error
echo Tunnel command failed. Check the error above.
pause
exit /b 1
