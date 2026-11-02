@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY goto :fail
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" || goto :fail
if not exist ".venv\Scripts\python.exe" %PY% -m venv .venv || goto :fail
set "VPY=.venv\Scripts\python.exe"
"%VPY%" -m pip install ".[dev]" pyinstaller || goto :fail
"%VPY%" -m pytest tests || goto :fail
"%VPY%" -m PyInstaller --noconfirm --clean client_mcp.spec || goto :fail
if "%CLIENT_MCP_ONEFILE%"=="1" echo Done: dist\ClientMCP.exe
if not "%CLIENT_MCP_ONEFILE%"=="1" echo Done: dist\ClientMCP\ClientMCP.exe
pause
exit /b 0
:fail
echo [FAILED] Build step failed. Check output above.
pause
exit /b 1
