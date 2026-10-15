#!/usr/bin/env python3
"""脚本编辑器一键启动：环境自检 → 缺依赖自动安装 → 打开界面。

用法（在本目录下）：

* Windows 双击 ``启动脚本编辑器.bat``（它会调用本脚本）；
* 或手动运行 ``python bootstrap.py ``；
* 只检查环境不打开界面：``python bootstrap.py --check-only``。

任何启动异常都会写入同目录的 ``启动日志.txt`` 并在窗口里显示
原因，不会一闪而过——把日志内容发给开发者即可定位问题。
"""

from __future__ import annotations

import importlib.metadata
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG_PATH = HERE / "启动日志.txt"
MIN_PYTHON = (3, 10)
MAX_PYTHON = (3, 15)
sys.path.insert(0, str(HERE / "src"))
from script_editor import GUI_VERSION  # noqa: E402 - bootstrap local source path
from script_editor.recovery_dependencies import (  # noqa: E402
    RECOVERY_REQUIREMENTS,
    RECOVERY_VERSIONS,
    SOURCE_SHA256,
    checked_recovery_source,
    installed_recovery_source_matches,
)

GUI_REQUIREMENTS = [("PySide6", f"PySide6=={GUI_VERSION}")]
REQUIREMENTS = GUI_REQUIREMENTS + RECOVERY_REQUIREMENTS

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
    for import_name, pip_name in REQUIREMENTS if requirements is None else requirements:
        try:
            if import_name != "PySide6":
                distribution = import_name.replace("_", "-")
                if importlib.metadata.version(distribution) != RECOVERY_VERSIONS[
                    import_name
                ] or (
                    import_name == "uncompyle6"
                    and not installed_recovery_source_matches()
                ):
                    missing.append((import_name, pip_name))
                continue
            module = __import__(import_name)
            if import_name == "PySide6" and module.__version__ != GUI_VERSION:
                missing.append((import_name, pip_name))
        except (ImportError, importlib.metadata.PackageNotFoundError):
            missing.append((import_name, pip_name))
    return missing


def install_packages(pip_names: list[str], requirements=None) -> bool:
    """逐个下载源尝试安装，装完复检；全部成功返回 True。"""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"], check=True, capture_output=True
        )
    except (subprocess.CalledProcessError, OSError):
        _say("pip 不可用，尝试用 ensurepip 修复…")
        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"])
    for url, label in MIRRORS:
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", *pip_names]
        if url:
            cmd += ["-i", url]
        _say(f"正在安装 {'、'.join(pip_names)}（{label}）…")
        result = subprocess.run(cmd)
        if result.returncode == 0 and not find_missing(requirements):
            return True
        _say(f"该下载源未成功（返回码 {result.returncode}），换下一个源重试…")
    return not find_missing(requirements)


def ensure_dependencies() -> bool:
    """Qt is required to open; recovery installation failure never hides the GUI."""
    missing_gui = find_missing(GUI_REQUIREMENTS)
    if missing_gui and not install_packages(
        [p for _, p in missing_gui], GUI_REQUIREMENTS
    ):
        _say(
            "Qt安装失败，无法打开界面；请查看pip具体错误（可能为版本/依赖/网络问题）。"
        )
        return False
    missing = find_missing(RECOVERY_REQUIREMENTS)
    if not missing:
        _say("依赖检查通过：Qt及独立恢复引擎已就绪。")
        return True
    _say(
        "正在安装支持当前Python的恢复引擎；使用包内固定提交源码，不使用旧版xdis6.1.8。"
    )
    try:
        source = checked_recovery_source(HERE)
        # Install the complete consistent set together, not a partially upgraded engine.
        pins = [source.as_uri() + "#sha256=" + SOURCE_SHA256] + [
            p for name, p in RECOVERY_REQUIREMENTS if name != "uncompyle6"
        ]
        if install_packages(pins, RECOVERY_REQUIREMENTS):
            _say("恢复引擎安装完成。")
            return True
    except (OSError, ValueError) as exc:
        _say(str(exc))
    _say("恢复引擎未就绪，仍打开已有编辑器界面；包内恢复可能暂不可用。")
    _say(
        "请保留上面的具体错误；版本冲突不是换镜像就能解决，也不要强制忽略Python版本限制。"
    )
    return True


def _log_failure(exc_text: str) -> None:
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n===== {datetime.now():%Y-%m-%d %H:%M:%S} =====\n")
            f.write(f"Python {sys.version}\n{exc_text}\n")
    except OSError:
        pass


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    install_only = "--install-only" in args
    check_only = "--check-only" in args
    args = [a for a in args if a not in {"--check-only", "--install-only"}]

    _say("MXSJ 脚本编辑器 · 启动自检")
    _say(f"Python {sys.version.split()[0]}：{sys.executable}")
    if not MIN_PYTHON <= sys.version_info < MAX_PYTHON:
        _say(
            f"Python版本不在支持范围：需要3.10至3.14，当前是 {sys.version.split()[0]}。"
        )
        _say(
            "请到 https://www.python.org/downloads/ 安装Python 3.10—3.14，"
            "安装时勾选 “Add python.exe to PATH”。"
        )
        return 2
    if not ensure_dependencies():
        return 2
    if install_only:
        return 2 if find_missing(RECOVERY_REQUIREMENTS) else 0
    try:
        __import__("PySide6.QtWidgets")
    except (ImportError, importlib.metadata.PackageNotFoundError):
        _log_failure(traceback.format_exc())
        _say("PySide6已安装但QtWidgets加载失败（系统动态库可能缺失）。")
        _say(f"详情见 {LOG_PATH}；不反复安装Python包掩盖系统库问题。")
        return 2
    if check_only:
        if find_missing(RECOVERY_REQUIREMENTS):
            _say("完整自检失败：恢复引擎未就绪；普通启动仍可打开界面。")
            return 2
        from script_editor.core.compiler.distribution import audit_runtimes

        try:
            report = audit_runtimes(HERE, execute=True)
        except (OSError, ValueError) as exc:
            _say(f"内置编译器检查未通过：{exc}")
            _log_failure(traceback.format_exc())
            return 2
        for compiler in report["compilers"]:
            _say(
                f"通过：{compiler['vm']} / CPython {compiler['version']} / "
                f"{compiler['bits']}bit；仅编译和marshal回读，未执行目标模块。"
            )
        _say("GUI加载及双编译器完整自检通过；不代表客户端加载/业务验收。")
        return 0

    from script_editor.app import main as app_main

    _say("正在打开编辑器界面…")
    return app_main(args)


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
        _say("把日志内容发给开发者即可定位问题。")
        raise SystemExit(1) from None
