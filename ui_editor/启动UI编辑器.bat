@echo off
chcp 65001 >nul
cd /d "%~dp0"
title MXSJ UI Editor
where py >nul 2>&1
if %errorlevel%==0 goto use_py
where python >nul 2>&1
if %errorlevel%==0 goto use_python
echo.
echo [ERROR] Python was not found on this computer.
echo Please install Python 3.10 or newer from https://www.python.org/downloads/
echo IMPORTANT: tick "Add python.exe to PATH" during installation.
echo.
pause
exit /b 1

:use_py
py -3 bootstrap.py %*
if %errorlevel% neq 0 echo [ERROR] Startup failed. See messages above / startup log.
goto done

:use_python
python bootstrap.py %*
if %errorlevel% neq 0 echo [ERROR] Startup failed. See messages above / startup log.
goto done

:done
echo.
pause
