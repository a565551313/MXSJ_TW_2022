@echo off
REM Double-click this file to start the local login server.
REM It asks for the account and password, then starts login_server.py.
REM Keep this window open while you log in with the game client.

cd /d "%~dp0"

set PYCMD=python
where python >nul 2>nul
if errorlevel 1 set PYCMD=py

echo.
echo ==== Local login server ====
echo Type the SAME account and password you will type in the game.
echo.
set /p ACC=Account (e.g. max123456): 
set /p PWD=Password (e.g. 12345678): 

echo.
echo Version number to send: 1, 2 or 3 (press Enter for 1)
set /p VID=Version [1]: 
if "%VID%"=="" set VID=1
echo Role name format: 1 = fixed 16 bytes, 2 = length-prefixed (press Enter for 1)
set /p NF=Format [1]: 
set EXTRA=
if "%NF%"=="2" set EXTRA=--name-lenprefix

echo.
echo Starting server with account [%ACC%] vid=%VID% format=%NF% ...
echo Now start the game client and log in. Watch this window.
echo.

%PYCMD% login_server.py --account "%ACC%" --password "%PWD%" --send-login --vid %VID% %EXTRA%

echo.
echo Server stopped. Press any key to close.
pause >nul
