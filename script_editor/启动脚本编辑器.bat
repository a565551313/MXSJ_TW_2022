@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
    echo [ERROR] Install Python 3.10+ with PATH enabled.
    pause
    exit /b 1
)
%PY% bootstrap.py %*
if errorlevel 1 pause
