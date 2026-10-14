@echo off
chcp 65001 >nul
REM ------------------------------------------------------------
REM  MXSJ UI Editor - one-click EXE build (Windows only)
REM
REM  Result:          dist\UIEditor\UIEditor.exe
REM  Single-file EXE: set UI_EDITOR_ONEFILE=1   (then run this script again)
REM  Steps: check Python -> .venv -> requirements-dev.txt -> unittest
REM         -> pyinstaller ui_editor.spec
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
"%VPY%" -m PyInstaller --noconfirm --clean ui_editor.spec || goto :fail

echo.
REM no %CD% inside the parentheses: a ")" in the folder name would break cmd parsing
if "%UI_EDITOR_ONEFILE%"=="1" echo Done: dist\UIEditor.exe
if not "%UI_EDITOR_ONEFILE%"=="1" echo Done: dist\UIEditor\UIEditor.exe
echo Double-click the EXE to check it opens a window; see README for the manual checklist.
pause
exit /b 0

:fail
echo.
echo [FAILED] A step above returned an error. Nothing usable was built.
pause
exit /b 1
