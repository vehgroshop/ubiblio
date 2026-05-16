@echo off
REM Double-clickable launcher for Anna's Boekenpaleis.
REM Starts docker compose (dev), waits for the app, and runs the named
REM cloudflared tunnel "boekenpaleis" (boekenpaleis.sejoost.nl).

setlocal
set "REPO=%~dp0.."
pushd "%REPO%"
title Anna's Boekenpaleis
powershell -NoProfile -ExecutionPolicy Bypass -File "%REPO%\scripts\tunnel.ps1" -Named boekenpaleis
set "ERR=%ERRORLEVEL%"
popd
if not "%ERR%"=="0" (
    echo.
    echo Launch exited with code %ERR%. Press any key to close.
    pause >nul
)
endlocal
