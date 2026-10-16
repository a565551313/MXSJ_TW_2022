@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

title MXSJ Development Game Server
echo ==========================================
echo   MXSJ game server - local development
echo ==========================================
echo.
echo This is a local development prototype only.
echo It is NOT compatible with the original game client.
echo Do not expose this port to the public Internet.
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 --version >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON=py -3"
        goto python_found
    )
)

where python >nul 2>nul
if %errorlevel%==0 (
    python --version
    set "PYTHON=python"
    goto python_found
)

echo [ERROR] Python 3.11 or newer was not found.
echo Please install Python from https://www.python.org/downloads/windows/
echo During installation, enable "Add Python to PATH", then double-click this file again.
echo.
pause
exit /b 1

:python_found
if not exist ".venv\Scripts\python.exe" (
    echo [1/2] Creating a local Python environment...
    %PYTHON% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Could not create the Python environment.
        echo Please confirm Python 3.11 or newer is installed.
        pause
        exit /b 1
    )
)

if not exist "server\data" mkdir "server\data"
set "PYTHONPATH=%CD%\server\src"
set "PYTHONDONTWRITEBYTECODE=1"

echo [2/2] Starting server...
echo Address: 127.0.0.1:8765
echo Keep this window open while using the server.
echo To stop the server, close this window or press Ctrl+C.
echo.
".venv\Scripts\python.exe" -m mxsj_server.bootstrap.game_server --database "server\data\game-loop.sqlite3"
echo.
echo The server has stopped.
pause
