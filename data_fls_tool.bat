@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
title 《夢想世界》(MXSJ) data.fls / script.fls 解包解密與加密打包工具

:: 切換到腳本所在目錄
cd /d "%~dp0"

:: 自動檢測 Python 解釋器
set "PY_CMD="
where python >nul 2>nul && set "PY_CMD=python"
if not defined PY_CMD (
    where py >nul 2>nul && set "PY_CMD=py -3"
)
if not defined PY_CMD (
    where python3 >nul 2>nul && set "PY_CMD=python3"
)
if not defined PY_CMD (
    echo [錯誤] 未檢測到 Python 環境，請先安裝 Python 3 並加入 PATH！
    pause
    exit /b 1
)

:: 自動定位核心腳本 tools\decompiler\pack_and_encrypt.py
set "TOOL_SCRIPT="
if exist "%~dp0tools\decompiler\pack_and_encrypt.py" (
    set "TOOL_SCRIPT=%~dp0tools\decompiler\pack_and_encrypt.py"
) else if exist "%~dp0..\tools\decompiler\pack_and_encrypt.py" (
    set "TOOL_SCRIPT=%~dp0..\tools\decompiler\pack_and_encrypt.py"
) else (
    echo [錯誤] 找不到 tools\decompiler\pack_and_encrypt.py！
    pause
    exit /b 1
)

:MENU
cls
echo ======================================================================
echo       《夢想世界》(MXSJ) data.fls ^& script.fls 解包解密 / 加密打包工具
echo ======================================================================
echo   當前工作目錄: %CD%
echo ----------------------------------------------------------------------
echo   【data.fls  - Python 2.7 Split-Stream 引擎】
echo     [1] 解包並解密當前目錄的 data.fls   到 OUT 文件夾
echo     [2] 加密並打包 OUT 文件夾的內容     到 IN 文件夾 (IN\data.fls)
echo.
echo   【script.fls - Python 2.5 5段式XOR + 0SLF 引擎 (共 5002 個模塊)】
echo     [3] 解包並解密當前目錄的 script.fls 到 OUT 文件夾
echo     [4] 加密並打包 OUT 文件夾的內容     到 IN 文件夾 (IN\script.fls)
echo.
echo   【自檢與退出】
echo     [5] 執行往返一致性自檢 (Verify data.fls ^& script.fls)
echo     [0] 退出
echo ======================================================================
set "choice="
set /p "choice=請輸入選項編號 [1 / 2 / 3 / 4 / 5 / 0]: "

if "%choice%"=="1" goto OPT1
if "%choice%"=="2" goto OPT2
if "%choice%"=="3" goto OPT3
if "%choice%"=="4" goto OPT4
if "%choice%"=="5" goto OPT5
if "%choice%"=="0" goto END
echo.
echo [提示] 無效的選項，請重新輸入！
timeout /t 2 >nul
goto MENU

:OPT1
echo.
echo ----------------------------------------------------------------------
echo [1] 正在解包並解密 data.fls 到 OUT 文件夾...
echo ----------------------------------------------------------------------
set "FLS_FILE="
if exist "%CD%\data.fls" (
    set "FLS_FILE=%CD%\data.fls"
) else if exist "%~dp0data.fls" (
    set "FLS_FILE=%~dp0data.fls"
) else if exist "%~dp0data\data.fls" (
    set "FLS_FILE=%~dp0data\data.fls"
)

if not defined FLS_FILE (
    echo [錯誤] 在當前目錄或 data\ 目錄下均找不到 data.fls！
    pause
    goto MENU
)

%PY_CMD% "%TOOL_SCRIPT%" unpack-out --archive "%FLS_FILE%" --out-dir "%CD%\OUT"
echo.
if errorlevel 1 (
    echo [失敗] 解包或解密 data.fls 過程中發生錯誤！
) else (
    echo [完成] 已成功解包並反編譯 data.fls 到: %CD%\OUT
    echo        可直接修改 OUT 目錄下的 .py / .pyc / 資源文件，完成後選擇 [2] 打包。
)
echo.
pause
goto MENU

:OPT2
echo.
echo ----------------------------------------------------------------------
echo [2] 正在加密並打包 OUT 文件夾到 IN 文件夾 (IN\data.fls)...
echo ----------------------------------------------------------------------
if not exist "%CD%\OUT" (
    echo [錯誤] 找不到 "%CD%\OUT" 文件夾，請先執行 [1] 解包 data.fls！
    pause
    goto MENU
)

%PY_CMD% "%TOOL_SCRIPT%" pack-in --out-dir "%CD%\OUT" --in-dir "%CD%\IN"
echo.
if errorlevel 1 (
    echo [失敗] 加密或打包 data.fls 過程中發生錯誤！
) else (
    echo [完成] 已成功加密並打包生成: %CD%\IN\data.fls
)
echo.
pause
goto MENU

:OPT3
echo.
echo ----------------------------------------------------------------------
echo [3] 準備解包並解密 script.fls 到 OUT 文件夾...
echo ----------------------------------------------------------------------
set "SFLS_FILE="
if exist "%CD%\script.fls" (
    set "SFLS_FILE=%CD%\script.fls"
) else if exist "%~dp0script.fls" (
    set "SFLS_FILE=%~dp0script.fls"
) else if exist "%~dp0data\script.fls" (
    set "SFLS_FILE=%~dp0data\script.fls"
)

if not defined SFLS_FILE (
    echo [錯誤] 在當前目錄或 data\ 目錄下均找不到 script.fls！
    pause
    goto MENU
)

echo [提示] script.fls 共有 5002 個腳本模塊：
echo        - 輸入路徑關鍵字（如 login、netserver、equipitemdata）或編號（如 516、17）可秒級解包指定模塊
echo        - 直接按 Enter 留空則解包並反編譯全部 5002 個模塊
set "flt="
set /p "flt=請輸入篩選關鍵字/編號（直接按 Enter 解包全部）: "

if defined flt (
    %PY_CMD% "%TOOL_SCRIPT%" unpack-script-out --archive "%SFLS_FILE%" --out-dir "%CD%\OUT" --entry "%flt%"
) else (
    %PY_CMD% "%TOOL_SCRIPT%" unpack-script-out --archive "%SFLS_FILE%" --out-dir "%CD%\OUT"
)
echo.
if errorlevel 1 (
    echo [失敗] 解包或解密 script.fls 過程中發生錯誤！
) else (
    echo [完成] 已成功解包並反編譯 script.fls 到: %CD%\OUT\script\
    echo        可直接修改 OUT\script\ 下的 .py 或 .pyc 文件，完成後選擇 [4] 加密打包。
)
echo.
pause
goto MENU

:OPT4
echo.
echo ----------------------------------------------------------------------
echo [4] 正在 5段式XOR 加密並打包 OUT 文件夾到 IN 文件夾 (IN\script.fls)...
echo ----------------------------------------------------------------------
if not exist "%CD%\OUT" (
    echo [錯誤] 找不到 "%CD%\OUT" 文件夾，請先執行 [3] 解包 script.fls！
    pause
    goto MENU
)

%PY_CMD% "%TOOL_SCRIPT%" pack-script-in --out-dir "%CD%\OUT" --in-dir "%CD%\IN"
echo.
if errorlevel 1 (
    echo [失敗] 加密或打包 script.fls 過程中發生錯誤！
) else (
    echo [完成] 已成功加密並打包生成: %CD%\IN\script.fls
)
echo.
pause
goto MENU

:OPT5
echo.
echo ----------------------------------------------------------------------
echo [5] 正在執行往返一致性自檢 (data.fls ^& script.fls)...
echo ----------------------------------------------------------------------
%PY_CMD% "%TOOL_SCRIPT%" verify
echo.
pause
goto MENU

:END
endlocal
exit /b 0
