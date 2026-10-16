@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
:newlog
set "LOG=%CD%\windows_test_%RANDOM%_%RANDOM%.log"
if exist "%LOG%" goto newlog
echo Windows manual self-check > "%LOG%"
ver >> "%LOG%"
echo Log: "%LOG%"
if exist ".venv\Scripts\python.exe" goto ready
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -m venv .venv >> "%LOG%" 2>&1
  if errorlevel 1 goto fail
  goto ready
)
where python >nul 2>&1
if errorlevel 1 goto fail
python -m venv .venv >> "%LOG%" 2>&1
if errorlevel 1 goto fail
:ready
.venv\Scripts\python.exe --version >> "%LOG%" 2>&1
echo Installing test dependencies. Details are being written to the log.
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt >> "%LOG%" 2>&1
if not errorlevel 1 goto deps_ok
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple >> "%LOG%" 2>&1
if not errorlevel 1 goto deps_ok
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt --index-url https://mirrors.aliyun.com/pypi/simple >> "%LOG%" 2>&1
if errorlevel 1 goto fail
:deps_ok
.venv\Scripts\python.exe bootstrap.py --check-only >> "%LOG%" 2>&1
if errorlevel 1 goto fail
echo Running all gates with GUI tests required. Please wait.
.venv\Scripts\python.exe check_manual.py --require-gui >> "%LOG%" 2>&1
if errorlevel 1 goto fail
echo AUTOMATED_CHECKS_PASSED >> "%LOG%"
type "%LOG%"
echo Now follow WINDOWS_TEST.md and launch the manual for visual checks.
echo Keep this log: "%LOG%"
pause
exit /b 0
:fail
echo SELF_CHECK_FAILED >> "%LOG%"
type "%LOG%"
echo Check failed. Python 3.10+ (64-bit), venv and network access are required.
echo Keep this log: "%LOG%"
pause
exit /b 2
