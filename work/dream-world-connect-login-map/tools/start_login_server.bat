@echo off
REM Double-click this file to start the local login server.
REM Keep this window open while you log in with the game client.

cd /d "%~dp0"

set PYCMD=python
where python >nul 2>nul
if errorlevel 1 set PYCMD=py

REM Fixed test account (must match what you type in the game)
set ACC=m123456
set PWD=111222

echo.
echo ==== Local login server ====
echo Account: %ACC%   Password: %PWD%
echo.
echo Choose a option (type a number, press Enter for 1):
echo   1 = version 1, fixed name
echo   2 = version 2, fixed name
echo   3 = version 3, fixed name
echo   4 = version 1, length-prefixed name
echo   5 = version 2, length-prefixed name
echo   6 = version 3, length-prefixed name
echo.
set /p CH=Option [1-6]: 
if "%CH%"=="" set CH=1

set VID=1
set EXTRA=
if "%CH%"=="2" set VID=2
if "%CH%"=="3" set VID=3
if "%CH%"=="4" set EXTRA=--name-lenprefix
if "%CH%"=="5" set VID=2
if "%CH%"=="5" set EXTRA=--name-lenprefix
if "%CH%"=="6" set VID=3
if "%CH%"=="6" set EXTRA=--name-lenprefix

echo.
echo Starting server: account=%ACC% vid=%VID% option=%CH%
echo Now start the game client and log in. Watch this window.
echo.

%PYCMD% login_server.py --account "%ACC%" --password "%PWD%" --send-login --vid %VID% %EXTRA%

echo.
echo Server stopped. Press any key to close.
pause >nul
