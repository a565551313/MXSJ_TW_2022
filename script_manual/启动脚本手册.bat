@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
where py >nul 2>&1
if not errorlevel 1 (
  py -3 bootstrap.py %*
  if errorlevel 1 goto fail
  exit /b 0
)
where python >nul 2>&1
if not errorlevel 1 (
  python bootstrap.py %*
  if errorlevel 1 goto fail
  exit /b 0
)
echo Python 3.10+ required. Install from https://www.python.org/downloads/
pause
exit /b 2
:fail
pause
exit /b 2
