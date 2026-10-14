@echo off
chcp 65001 >nul
REM ------------------------------------------------------------
REM  MXSJ Script Editor - one-click EXE build (Windows only)
REM
REM  Result:          dist\MXSJScriptEditor\MXSJScriptEditor.exe
REM  Steps: check Python -> .venv -> requirements-dev.txt -> unittest
REM         -> pyinstaller script_editor.spec
REM  This file is ASCII on purpose; all Chinese text lives in Python.
REM ------------------------------------------------------------
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
    echo [ERROR] Python 3.10+ not found.
    echo         Install it from https://www.python.org/downloads/
    echo         and tick "Add python.exe to PATH" in the installer.
    pause
    exit /b 1
)
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
    echo [ERROR] Python 3.10 or newer is required.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [1/4] Creating virtual environment .venv ...
    %PY% -m venv .venv || goto :fail
) else (
    echo [1/4] Reusing virtual environment .venv
)
set "VPY=.venv\Scripts\python.exe"

echo [2/4] Installing dependencies from requirements-dev.txt ...
REM pip self-upgrade is best effort (offline / locked-down machines must not fail here)
"%VPY%" -m pip install --upgrade pip >nul 2>nul
"%VPY%" -m pip install -r requirements-dev.txt || goto :fail

echo [3/4] Running unit tests ...
set "PYTHONPATH=src"
set "QT_QPA_PLATFORM=offscreen"
"%VPY%" -m unittest discover -s tests || goto :fail
set "PYTHONPATH="
set "QT_QPA_PLATFORM="

echo [4/4] Building with PyInstaller ...
"%VPY%" -m PyInstaller --noconfirm --clean script_editor.spec || goto :fail

if not exist "dist\MXSJScriptEditor\runtimes" mkdir "dist\MXSJScriptEditor\runtimes"
copy /y "runtimes\manifest.json" "dist\MXSJScriptEditor\runtimes\manifest.json" >nul || goto :fail
echo.
REM no %CD% inside the parentheses: a ")" in the folder name would break cmd parsing
echo Done: dist\MXSJScriptEditor\MXSJScriptEditor.exe
echo NOTE: compiler manifest is empty; native package GUI build is disabled.
echo Double-click the EXE to check it opens a window; see README for the manual checklist.
pause
exit /b 0

:fail
echo.
echo [FAILED] A step above returned an error. Nothing usable was built.
pause
exit /b 1
