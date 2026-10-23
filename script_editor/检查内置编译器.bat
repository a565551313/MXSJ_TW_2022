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
%PY% -m script_editor.runtime_cli audit --root .
set "RESULT=%ERRORLEVEL%"
echo.
if not "%RESULT%"=="0" echo [FAILED] Keep this error text. Do not replace runtimes with game DLLs.
if not "%RESULT%"=="0" echo [HINT] If it says runtime file SHA256 mismatch, double-click the repair bat in this folder.
pause
exit /b %RESULT%
