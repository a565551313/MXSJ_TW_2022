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
    pause
    exit /b 1
)
%PY% check_package.py %*
echo.
pause
exit /b 0
