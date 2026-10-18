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
%PY% -m venv .venv
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if errorlevel 1 goto failed
.venv\Scripts\python.exe bootstrap.py --check-only
if errorlevel 1 goto failed
set "PYTHONPATH=%CD%\src"
set "PYTHONDONTWRITEBYTECODE=1"
.venv\Scripts\python.exe -m ruff check .
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m unittest discover -s tests -v
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean web_server.spec
if errorlevel 1 goto failed
if "%WEB_SERVER_ONEFILE%"=="1" (
    echo Built dist\MXSJWebServer.exe
) else (
    echo Built dist\MXSJWebServer\MXSJWebServer.exe
)
pause
exit /b 0
:failed
echo Build failed. No success claimed.
pause
exit /b 1
