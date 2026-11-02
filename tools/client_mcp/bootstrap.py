"""Check dependencies and launch the stdio or loopback HTTP MCP server."""

from __future__ import annotations

import importlib
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG_PATH = HERE / "启动日志.txt"
REQUIREMENTS = [
    ("mcp.server.stdio", "mcp>=1.30.0,<2"),
    ("mcp.server.streamable_http_manager", "mcp>=1.30.0,<2"),
    ("uvicorn", "uvicorn>=0.31.1"),
    ("starlette", "starlette>=0.27"),
]
MIRRORS = [
    None,
    "https://pypi.tuna.tsinghua.edu.cn/simple",
    "https://mirrors.aliyun.com/pypi/simple",
]


def find_missing() -> list[str]:
    missing = []
    for module, package in REQUIREMENTS:
        try:
            importlib.import_module(module)
        except ImportError:
            if package not in missing:
                missing.append(package)
    return missing


def install_packages(packages: list[str]) -> bool:
    for mirror in MIRRORS:
        cmd = [sys.executable, "-m", "pip", "install", *packages]
        if mirror:
            cmd.extend(["-i", mirror])
        print(
            f"Installing dependencies from {mirror or 'default index'}", file=sys.stderr
        )
        try:
            result = subprocess.run(
                cmd, stdout=sys.stderr, stderr=sys.stderr, check=False
            )
        except OSError as exc:
            print(f"Install failed: {exc}", file=sys.stderr)
            continue
        importlib.invalidate_caches()
        if result.returncode == 0 and not find_missing():
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    check_only = "--check-only" in args
    args = [arg for arg in args if arg != "--check-only"]
    if sys.version_info < (3, 10):  # noqa: UP036
        print(
            "Python 3.10+ required: https://www.python.org/downloads/ "
            "(select Add python.exe to PATH)",
            file=sys.stderr,
        )
        return 2
    missing = find_missing()
    if missing and (check_only or not install_packages(missing)):
        print(f"Missing dependencies: {', '.join(missing)}", file=sys.stderr)
        return 2
    sys.path.insert(0, str(HERE / "src"))
    from mxsj_client_mcp.run import main as run_main

    if check_only:
        print("OK: mxsj-client-mcp environment check passed", file=sys.stderr)
        return 0
    return run_main(args)


def entrypoint() -> int:
    try:
        return main()
    except Exception:
        text = traceback.format_exc()
        try:
            with LOG_PATH.open("a", encoding="utf-8") as log:
                log.write(f"\n===== {datetime.now():%Y-%m-%d %H:%M:%S} =====\n")
                log.write(f"Python {sys.version}\n{text}\n")
        except OSError:
            pass
        print(text, file=sys.stderr)
        print(f"Startup failure log: {LOG_PATH}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(entrypoint())
