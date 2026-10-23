@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "PYTHONPATH=src"
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
    echo [ERROR] Python 3.10+ not found.
    pause
    exit /b 1
)
%PY% repair_runtimes.py
set "RESULT=%ERRORLEVEL%"
echo.
pause
exit /b %RESULT%
