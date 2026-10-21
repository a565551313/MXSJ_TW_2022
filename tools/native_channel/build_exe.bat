@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist .venv\Scripts\python.exe goto ready
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -m venv .venv
) else (
    python -m venv .venv
)
if errorlevel 1 goto fail
:ready
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m unittest discover -s tests
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean native_channel.spec
if errorlevel 1 goto fail
echo Built dist\MXSJNativeChannel\MXSJNativeChannel.exe
pause
exit /b 0
:fail
echo Build failed. See output above.
pause
exit /b 1
