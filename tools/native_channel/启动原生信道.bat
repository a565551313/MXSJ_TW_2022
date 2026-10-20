@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 bootstrap.py %*
) else (
    python bootstrap.py %*
)
if errorlevel 1 pause
