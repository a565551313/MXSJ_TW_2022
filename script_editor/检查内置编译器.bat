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
if "%RESULT%"=="0" goto done
echo.
echo [INFO] Bytes may have been rewritten by Git; checking and repairing ...
%PY% repair_runtimes.py
echo.
echo [INFO] Re-checking ...
%PY% -m script_editor.runtime_cli audit --root .
set "RESULT=%ERRORLEVEL%"
:done
echo.
if not "%RESULT%"=="0" echo [FAILED] Keep this error text. Do not replace runtimes with game DLLs.
if not "%RESULT%"=="0" echo [HINT] Send the last 10 lines to the maintainer; do not delete files.
pause
exit /b %RESULT%
