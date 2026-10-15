from __future__ import annotations

import importlib
import importlib.metadata
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIN_PYTHON = (3, 10)
REQUIREMENTS = [("PySide6", "PySide6==6.10.3"), ("jsonschema", "jsonschema==4.25.1")]
MIRRORS = [
    None,
    "https://pypi.tuna.tsinghua.edu.cn/simple",
    "https://mirrors.aliyun.com/pypi/simple",
]


def missing_dependencies():
    missing = []
    for module, pin in REQUIREMENTS:
        try:
            importlib.import_module(module)
            if importlib.metadata.version(module) != pin.split("==")[1]:
                missing.append(pin)
        except (ImportError, importlib.metadata.PackageNotFoundError):
            missing.append(pin)
    return missing


def ensure_dependencies():
    missing = missing_dependencies()
    if not missing:
        return True
    result = subprocess.run([sys.executable, "-m", "pip", "--version"], check=False)
    if result.returncode:
        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)
    for mirror in MIRRORS:
        command = [sys.executable, "-m", "pip", "install", *missing]
        if mirror:
            command += ["--index-url", mirror]
        print(f"补装依赖：{'、'.join(missing)}；源：{mirror or '官方'}", flush=True)
        if subprocess.run(command, check=False).returncode == 0:
            importlib.invalidate_caches()
            if not missing_dependencies():
                return True
    return False


def log_failure(detail):
    try:
        with (HERE / "启动日志.txt").open("a", encoding="utf-8") as stream:
            stream.write(
                f"\n{datetime.now().isoformat()}\nPython {sys.version}\n{detail}\n"
            )
    except OSError:
        pass


def main(argv=None):
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    args = list(sys.argv[1:] if argv is None else argv)
    check_only = "--check-only" in args
    args = [value for value in args if value != "--check-only"]
    if sys.version_info < MIN_PYTHON:
        print(
            "需要Python ≥ 3.10；https://www.python.org/downloads/；请勾选Add to PATH。"
        )
        return 2
    try:
        if not ensure_dependencies():
            raise RuntimeError("依赖安装失败；请查看pip错误。不要忽略Python版本冲突。")
        importlib.import_module("PySide6.QtWidgets")
        sys.path.insert(0, str(HERE / "src"))
        if check_only:
            from mxsj_manual.core.catalog import load_catalog

            catalog = load_catalog(HERE)
            print(
                f"依赖/手册结构自检通过：{catalog.coverage()}；不代表Windows或游戏验收。"
            )
            return 0
        from mxsj_manual.app import main as application_main

        return application_main(args)
    except Exception:
        detail = traceback.format_exc()
        log_failure(detail)
        print(detail)
        print(f"启动失败，完整日志：{HERE / '启动日志.txt'}")
        if not check_only and sys.stdin is not None and sys.stdin.isatty():
            input("按回车退出…")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
