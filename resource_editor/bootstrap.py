#!/usr/bin/env python3
"""资源编辑器一键启动：环境自检 → 缺依赖自动安装 → 打开界面。

用法（在本目录下）：

* Windows 双击 ``启动编辑器.bat``（它会调用本脚本）；
* 或手动运行 ``python bootstrap.py [资源包或目录路径]``；
* 只检查环境不打开界面：``python bootstrap.py --check-only``。

任何启动异常都会写入同目录的 ``启动日志.txt``，并停在窗口里
显示原因，不会一闪而过——把日志内容发给开发者即可定位问题。
"""
from __future__ import annotations

import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG_PATH = HERE / "启动日志.txt"
MIN_PYTHON = (3, 10)

# (导入名, pip 安装名)：缺哪个装哪个
REQUIREMENTS = [
    ("PySide6", "PySide6>=6.4"),
    ("PIL", "Pillow>=9.0"),
]

# 依次尝试的下载源：None=官方源，后面是国内镜像（官方慢/连不上时兜底）
MIRRORS: list[tuple[str | None, str]] = [
    (None, "官方源"),
    ("https://pypi.tuna.tsinghua.edu.cn/simple", "清华镜像"),
    ("https://mirrors.aliyun.com/pypi/simple", "阿里云镜像"),
]


def _say(message: str = "") -> None:
    print(message, flush=True)


def find_missing(
    requirements: list[tuple[str, str]] | None = None,
) -> list[tuple[str, str]]:
    """返回当前环境缺失的 (导入名, pip 名) 列表。"""
    missing = []
    for import_name, pip_name in (requirements or REQUIREMENTS):
        try:
            __import__(import_name)
        except ImportError:
            missing.append((import_name, pip_name))
    return missing


def install_packages(pip_names: list[str]) -> bool:
    """逐个下载源尝试安装，装完复检；全部成功返回 True。"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                       check=True, capture_output=True)
    except (subprocess.CalledProcessError, OSError):
        _say("pip 不可用，尝试用 ensurepip 修复…")
        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"])
    for url, label in MIRRORS:
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade",
               *pip_names]
        if url:
            cmd += ["-i", url]
        _say(f"正在安装 {'、'.join(pip_names)}（{label}）…")
        result = subprocess.run(cmd)
        if result.returncode == 0 and not find_missing():
            return True
        _say(f"该下载源未成功（返回码 {result.returncode}），换下一个源重试…")
    return not find_missing()


def ensure_dependencies() -> bool:
    """检查并补齐运行依赖。"""
    missing = find_missing()
    if not missing:
        _say("依赖检查通过：PySide6、Pillow 均已安装。")
        return True
    names = "、".join(import_name for import_name, _ in missing)
    _say(f"检测到缺少依赖：{names}，现在自动安装（只需这一次）…")
    if install_packages([pip_name for _imp, pip_name in missing]):
        _say("依赖安装完成。")
        return True
    _say("")
    _say("自动安装失败。可能原因：没有网络，或公司/校园网拦截。")
    _say("可手动在命令行执行下面这行再重试：")
    _say(f"    {sys.executable} -m pip install "
         + " ".join(pip_name for _imp, pip_name in missing))
    return False


def _log_failure(exc_text: str) -> None:
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n===== {datetime.now():%Y-%m-%d %H:%M:%S} =====\n")
            f.write(f"Python {sys.version}\n{exc_text}\n")
    except OSError:
        pass


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    check_only = "--check-only" in args
    args = [a for a in args if a != "--check-only"]

    _say("MXSJ 资源编辑器 · 启动自检")
    _say(f"Python {sys.version.split()[0]}：{sys.executable}")
    if sys.version_info < MIN_PYTHON:
        _say(f"Python 版本过低：需要 {MIN_PYTHON[0]}.{MIN_PYTHON[1]} 以上，"
             f"当前是 {sys.version.split()[0]}。")
        _say("请到 https://www.python.org/downloads/ 安装新版 Python，"
             "安装时勾选 “Add python.exe to PATH”。")
        return 2
    if not ensure_dependencies():
        return 2
    if check_only:
        _say("环境已就绪，可以打开编辑器。")
        return 0

    sys.path.insert(0, str(HERE / "src"))
    from resource_editor.app import main as app_main

    _say("正在打开编辑器界面…")
    return app_main([str(HERE / "bootstrap.py"), *args])


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        text = traceback.format_exc()
        _log_failure(text)
        _say("")
        _say("启动失败，错误详情已写入日志文件：")
        _say(f"    {LOG_PATH}")
        _say("把这个日志文件发给开发者即可。详情如下：")
        _say(text)
        if sys.stdin is not None and sys.stdin.isatty():
            try:
                input("按回车键关闭窗口…")
            except EOFError:
                pass
        raise SystemExit(1) from None
