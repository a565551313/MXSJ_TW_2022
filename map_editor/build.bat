@echo off
chcp 65001 >nul
REM ============================================================
REM  《夢想世界》地图编辑器 - Windows 打包脚本
REM  在 Windows 上执行本文件即可得到 dist\MapEditor\MapEditor.exe
REM  单文件 EXE：  set MAP_EDITOR_ONEFILE=1  然后再运行本脚本
REM ============================================================
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [错误] 找不到 python，请先安装 Python 3.10 或更新版本并加入 PATH。
    pause
    exit /b 1
)

python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
    echo [错误] 需要 Python 3.10 或更新版本。
    pause
    exit /b 1
)

if not exist .venv (
    echo [1/4] 创建虚拟环境 .venv ...
    python -m venv .venv || goto :fail
)
call .venv\Scripts\activate.bat

echo [2/4] 安装依赖 ...
python -m pip install --upgrade pip >nul || goto :fail
pip install -r requirements-dev.txt || goto :fail

echo [3/4] 运行测试 ...
python -m unittest discover -s tests -v || goto :fail

echo [4/4] PyInstaller 打包 ...
pyinstaller --noconfirm --clean map_editor.spec || goto :fail

echo.
if "%MAP_EDITOR_ONEFILE%"=="1" (
    echo 完成：dist\MapEditor.exe
) else (
    echo 完成：dist\MapEditor\MapEditor.exe
)
echo 运行时只需在界面里选择客户端根目录，程序会递归找出所有 *.map。
pause
exit /b 0

:fail
echo.
echo [失败] 见上方输出。
pause
exit /b 1
