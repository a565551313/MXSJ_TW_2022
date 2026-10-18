"""自检并启动 PySide6 管理器；支持独立核心自检。"""

from __future__ import annotations

import importlib
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIN_PYTHON = (3, 10)
REQUIREMENTS: list[
    tuple[str, str]
] = []  # Standard library only in the current release.
MIRRORS = [
    None,
    "https://pypi.tuna.tsinghua.edu.cn/simple",
    "https://mirrors.aliyun.com/pypi/simple",
]


def find_missing(requirements=None):
    missing = []
    for module, package in REQUIREMENTS if requirements is None else requirements:
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append((module, package))
    return missing


def ensure_dependencies() -> bool:
    missing = find_missing()
    if not missing:
        return True
    check = subprocess.run(
        [sys.executable, "-m", "pip", "--version"], capture_output=True
    )
    if check.returncode:
        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=False)
    for mirror in MIRRORS:
        command = [sys.executable, "-m", "pip", "install", *[p for _, p in missing]]
        if mirror:
            command += ["--index-url", mirror]
        result = subprocess.run(command, check=False)
        # Successful installer exit is not sufficient: imports must actually work.
        if result.returncode == 0 and not find_missing():
            return True
    return not find_missing()


def log_failure(text: str) -> None:
    # Local launch diagnostics, not request/access logs. Review before sharing.
    try:
        with (HERE / "启动日志.txt").open("a", encoding="utf-8") as stream:
            stream.write(f"\n[{datetime.now(timezone.utc).isoformat()}]\n")
            stream.write(f"Python {sys.version}\n{text}\n")
    except OSError:
        print("启动日志无法写入，请检查目录权限。", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    core_only = "--core-only" in args
    args = [arg for arg in args if arg != "--core-only"]
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    if sys.version_info < MIN_PYTHON:
        print("需要 Python 3.10 或以上：https://www.python.org/downloads/")
        print("安装时请勾选 Add python.exe to PATH。")
        return 2
    try:
        if not ensure_dependencies():
            print("依赖安装失败；请检查网络或手动安装 requirements.txt。")
            return 2
        if "--check-only" in args and not core_only:
            # Installing PySide6 alone does not prove native Qt libraries exist.
            importlib.import_module("PySide6.QtWidgets")
        sys.path.insert(0, str(HERE / "src"))
        from mxsj_web_server.app import main as app_main

        # Check-only also verifies bundled/explicit configuration, with no listener.
        result = app_main(args, raise_errors=True)
        return 2 if "--check-only" in args and result else result
    except Exception:
        log_failure(traceback.format_exc())
        print("启动异常已记录到 启动日志.txt；分享前请检查并脱敏。", file=sys.stderr)
        if "--check-only" not in args and sys.stdin and sys.stdin.isatty():
            try:
                input("按回车键关闭……")
            except EOFError:
                pass
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
