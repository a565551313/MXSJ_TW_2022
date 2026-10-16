@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
if exist ".venv\Scripts\python.exe" goto ready
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -m venv .venv
  if errorlevel 1 goto fail
  goto ready
)
where python >nul 2>&1
if errorlevel 1 goto fail
python -m venv .venv
if errorlevel 1 goto fail
:ready
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if errorlevel 1 goto fail
.venv\Scripts\python.exe bootstrap.py --check-only
if errorlevel 1 goto fail
set PYTHONPATH=%CD%\src
set QT_QPA_PLATFORM=offscreen
set MXSJ_MANUAL_REQUIRE_GUI=1
.venv\Scripts\python.exe -m unittest discover -s tests -v
if errorlevel 1 goto fail
set QT_QPA_PLATFORM=
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean script_manual.spec
if errorlevel 1 goto fail
if "%MXSJ_MANUAL_ONEFILE%"=="1" (
  echo Built: dist\MXSJScriptManual.exe
) else (
  echo Built: dist\MXSJScriptManual\MXSJScriptManual.exe
)
pause
exit /b 0
:fail
echo Build failed. Python 3.10+ and network access are required.
pause
exit /b 2
