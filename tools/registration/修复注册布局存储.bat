@echo off
chcp 65001 >nul
set "PYTHONUTF8=1"
if "%~1"=="" goto usage
where py >nul 2>nul
if errorlevel 1 goto try_python
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
if errorlevel 1 goto try_python
goto run_py
:try_python
where python >nul 2>nul
if errorlevel 1 goto no_python
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
if errorlevel 1 goto no_python
goto run_python
:run_py
py -3 "%~dp0repair_interface_layouts.py" "%~f1" >"%~dp0repair_log.txt" 2>&1
set "RESULT=%ERRORLEVEL%"
goto result
:run_python
python "%~dp0repair_interface_layouts.py" "%~f1" >"%~dp0repair_log.txt" 2>&1
set "RESULT=%ERRORLEVEL%"
goto result
:result
type "%~dp0repair_log.txt"
echo.
echo Input was NOT written. Read repair_log.txt before using any NEW output.
echo This is NOT a complete native-game acceptance test.
pause
exit /b %RESULT%
:usage
echo Close the TEST game copy first.
echo Drag its CURRENT interface.fls onto this BAT file.
echo A NEW interface_native_fixed.fls is created only when a storage fix is needed.
echo Never operate on the original installation. Existing outputs are refused.
pause
exit /b 2
:no_python
echo Python 3.10 or newer is required. No third-party modules are needed.
echo Use the Python installation already used by the resource editor.
pause
exit /b 2
