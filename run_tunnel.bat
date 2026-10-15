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
echo This creates a public tunnel to port 3978.
echo Keep the Python bot running in a separate terminal.
echo Use only for development. Stop with Ctrl+C when finished.
echo.
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
echo Tunnel command failed. Review the error above.
pause
exit /b 1
