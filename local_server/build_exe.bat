@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (set "PY=python") else (set "PY=py -3")
%PY% -m venv .venv
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if errorlevel 1 goto failed
.venv\Scripts\python.exe bootstrap.py --check-only
if errorlevel 1 goto failed
set "PYTHONDONTWRITEBYTECODE=1"
.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean local_server.spec
if errorlevel 1 goto failed
echo Built dist\MXSJLocalServer\MXSJLocalServer.exe
pause
exit /b 0
:failed
echo Build failed. No success claimed.
pause
exit /b 1
