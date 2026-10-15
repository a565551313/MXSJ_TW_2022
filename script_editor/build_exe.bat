@echo off
chcp 65001 >nul
REM Windows onedir release: both audited x86 standard runtimes are mandatory.
REM This builds the editor only; it never creates/distributes game packages.
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
    echo [ERROR] Python 3.10+ not found.
    pause
    exit /b 1
)
%PY% -c "import sys; sys.exit(0 if (3, 10) <= sys.version_info < (3, 15) else 1)"
if errorlevel 1 (
    echo [ERROR] Python 3.10 through 3.14 is required.
    pause
    exit /b 1
)
set "PYTHONPATH=src"
echo [1/5] Auditing both standard Windows runtimes before any build ...
%PY% -m script_editor.runtime_cli audit --root . || goto :fail

if not exist ".venv\Scripts\python.exe" (
    echo [2/5] Creating virtual environment .venv ...
    %PY% -m venv .venv || goto :fail
) else (
    echo [2/5] Reusing virtual environment .venv
)
set "VPY=.venv\Scripts\python.exe"
echo [3/5] Installing dependencies and running strict release checks ...
"%VPY%" -m pip install --upgrade pip >nul 2>nul
"%VPY%" -m pip install -r requirements-dev.txt || goto :fail
REM GUI/compiler skips are fatal; only explicitly opt-in game-material tests may skip.
"%VPY%" -m script_editor.release_checks --root . || goto :fail

echo [4/5] Building with PyInstaller ...
"%VPY%" -m PyInstaller --noconfirm --clean script_editor.spec || goto :fail
"%VPY%" -m PyInstaller --noconfirm --clean recovery_worker.spec || goto :fail
"%VPY%" stage_recovery.py --destination "dist\MXSJScriptEditor" || goto :fail
echo [5/5] Copying exact runtime inventories and rechecking staged bytes ...
"%VPY%" -m script_editor.runtime_cli stage --root . --destination "dist\MXSJScriptEditor" > "dist\MXSJScriptEditor\runtime-audit.json" || goto :fail
"%VPY%" -m script_editor.catalog_cli stage --root . --destination "dist\MXSJScriptEditor" || goto :fail
set "PYTHONPATH="
echo.
echo Built: dist\MXSJScriptEditor\MXSJScriptEditor.exe
echo Runtime compile/marshal checks passed. GUI EXE and game acceptance still need manual tests.
pause
exit /b 0

:fail
echo.
echo [FAILED] Release blocked. Do not distribute partial or stale build output.
echo Both genuine standard x86 runtimes, their licenses and file hashes are required.
pause
exit /b 1
