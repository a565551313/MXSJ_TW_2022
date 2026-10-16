@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title MXSJ One-click Game Loop Verification

echo ==========================================
echo   MXSJ - One-click game-loop verification
echo ==========================================
echo.
echo This runs the local prototype, exercises the real TCP flow,
echo and runs the automated test suites. No pip packages are needed.
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON=py -3"
        goto python_found
    )
)
where python >nul 2>nul
if %errorlevel%==0 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON=python"
        goto python_found
    )
)

echo [ERROR] Python 3.11 or newer was not found.
echo Install it from https://www.python.org/downloads/windows/
echo Then double-click this file again.
echo.
pause
exit /b 1

:python_found
if not exist ".venv\Scripts\python.exe" (
    echo Preparing a local Python environment...
    %PYTHON% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Could not create the Python environment.
        pause
        exit /b 1
    )
)

if not exist "server\tools\verify_game_loop.py" (
    echo [ERROR] This script must stay in the project root beside the server folder.
    pause
    exit /b 1
)

if not exist "server\data" mkdir "server\data"
echo Starting end-to-end and automated tests. Please wait...
echo.
".venv\Scripts\python.exe" "server\tools\verify_game_loop.py"
if errorlevel 1 (
    echo.
    echo RESULT: FAILED. Copy or photograph the error above and send it to ChatGPT.
) else (
    echo.
    echo RESULT: SUCCESS. The tested development flow reached the map.
)
echo.
pause
