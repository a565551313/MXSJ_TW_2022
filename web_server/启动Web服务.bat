@echo off
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    set "PY=py -3"
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Python 3.10+ required: https://www.python.org/downloads/
        echo Enable Add python.exe to PATH during installation.
        pause
        exit /b 2
    )
    set "PY=python"
)
%PY% bootstrap.py %*
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" pause
exit /b %RESULT%
