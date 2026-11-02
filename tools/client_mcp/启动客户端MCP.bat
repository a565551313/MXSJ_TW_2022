@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
    echo Python 3.10+ required: https://www.python.org/downloads/ 1>&2
    echo During install tick "Add python.exe to PATH".
    pause
    exit /b 1
)
%PY% bootstrap.py %*
if errorlevel 1 (
    echo.
    echo Startup failed. Send this window and the log file to the developer.
    pause
    exit /b 1
)
exit /b 0
