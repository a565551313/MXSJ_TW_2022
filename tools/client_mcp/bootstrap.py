"""一键启动客户端 MCP：环境自检 → 自动补依赖 → 自动生成配置 → 启动服务。

用户只需要双击同目录的 ``启动客户端MCP.bat``，不需要输入任何命令：

* 自动检查 Python 版本与依赖，缺什么装什么（官方源失败自动换清华 / 阿里云）；
* 自动生成访问令牌并保存在 ``runtime/http_token.txt``；
* 自动挑选空闲端口，写进 ``runtime/http_port.txt``；
* 自动查找客户端探针报告 ``mxsj_probe_report.txt``；
* 自动生成编程工具可直接导入的 MCP 配置 ``runtime/mcp_client_config.json``；
* 窗口里显示接入地址、配置路径和报告状态，关闭窗口即停止服务。

任何启动异常都会写入同目录的 ``启动日志.txt``，用户只需把日志发回来。
``--check-only`` 只做自检并返回退出码 0 / 2，供 Linux 沙箱与 CI 使用。
"""

from __future__ import annotations

import importlib
import json
import secrets
import socket
import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
LOG_PATH = HERE / "启动日志.txt"
RUNTIME_DIR = HERE / "runtime"
TOKEN_PATH = RUNTIME_DIR / "http_token.txt"
PORT_PATH = RUNTIME_DIR / "http_port.txt"
CONFIG_PATH = RUNTIME_DIR / "mcp_client_config.json"
REPORT_NAME = "mxsj_probe_report.txt"
DEFAULT_PORT = 8765
PORT_SCAN = 20
# The resident probe rewrites its report every second, so a gap this long means
# the client closed (or never started the timer).  Generous on purpose: loading
# a map or a long GC pause must not be mistaken for "closed".
STALE_SECONDS = 15.0
MIN_PYTHON = (3, 10)
LOW_LEVEL_MODULES = ("mcp.server.stdio", "mcp.server.streamable_http_manager")

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


def _say(message: str = "") -> None:
    print(message, flush=True)


def find_missing() -> list[str]:
    """Return the pip names of requirements that cannot be imported."""
    missing = []
    for module, package in REQUIREMENTS:
        try:
            importlib.import_module(module)
        except ImportError:
            if package not in missing:
                missing.append(package)
    return missing


def install_packages(packages: list[str]) -> bool:
    """Try every mirror; only report success after the import recheck passes."""
    for mirror in MIRRORS:
        cmd = [sys.executable, "-m", "pip", "install", *packages]
        if mirror:
            cmd.extend(["-i", mirror])
        print(f"正在安装依赖（{mirror or '官方源'}）…", file=sys.stderr, flush=True)
        try:
            result = subprocess.run(
                cmd, stdout=sys.stderr, stderr=sys.stderr, check=False
            )
        except OSError as exc:
            print(f"安装失败：{exc}", file=sys.stderr, flush=True)
            continue
        importlib.invalidate_caches()
        if result.returncode == 0 and not find_missing():
            return True
        print("该下载源未成功，换下一个源重试…", file=sys.stderr, flush=True)
    return False


def load_or_create_token(path: Path | None = None) -> str:
    """Reuse a saved token, or create and persist a new random one."""
    target = Path(path) if path is not None else TOKEN_PATH
    try:
        existing = target.read_text(encoding="utf-8").strip()
    except OSError:
        existing = ""
    if len(existing) >= 16:
        return existing
    token = secrets.token_urlsafe(32)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(token + "\n", encoding="utf-8", newline="\n")
    try:
        target.chmod(0o600)
    except OSError:
        pass
    return token


def port_is_free(port: int, host: str = "127.0.0.1") -> bool:
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        probe.bind((host, port))
    except OSError:
        return False
    finally:
        probe.close()
    return True


def pick_port(preferred: int = DEFAULT_PORT, host: str = "127.0.0.1") -> int:
    """Return the first free port at or after ``preferred``."""
    for candidate in range(preferred, preferred + PORT_SCAN):
        if port_is_free(candidate, host):
            return candidate
    raise OSError(f"{preferred}-{preferred + PORT_SCAN - 1} 端口都被占用")


def report_search_dirs() -> list[Path]:
    return [
        RUNTIME_DIR,
        HERE,
        REPO_ROOT,
        REPO_ROOT / "data",
        REPO_ROOT / "log",
        HERE / "inputs",
    ]


def find_report_file(
    search_dirs: list[Path] | None = None, name: str = REPORT_NAME
) -> Path | None:
    """Return the newest probe report found in the usual places."""
    newest: tuple[float, Path] | None = None
    for directory in search_dirs if search_dirs is not None else report_search_dirs():
        try:
            candidates = [directory / name]
            if directory.is_dir():
                candidates.extend(sorted(directory.glob(f"*/{name}")))
        except OSError:
            continue
        for candidate in candidates:
            try:
                if not candidate.is_file():
                    continue
                mtime = candidate.stat().st_mtime
            except OSError:
                continue
            if newest is None or mtime > newest[0]:
                newest = (mtime, candidate)
    return newest[1] if newest else None


def write_client_config(url: str, token: str, path: Path | None = None) -> Path:
    """Write an MCP client config that can be imported as-is."""
    target = Path(path) if path is not None else CONFIG_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "mcpServers": {
            "mxsj-client": {
                "url": url,
                "headers": {"Authorization": f"Bearer {token}"},
            }
        }
    }
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return target


def server_args(port: int, token: str, report: Path | None) -> list[str]:
    """Build the ``run.py`` arguments used by the launcher."""
    args = [
        "--transport",
        "http",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--http-token",
        token,
    ]
    if report is not None:
        args.extend(["--report-file", str(report)])
    return args


class ReportWatcher:
    """Turn report-file observations into one message per state change.

    A per-second heartbeat changes the file's mtime constantly, so keying on
    the mtime printed the banner on every poll (the Windows run showed it
    repeating).  This keys on (path, fresh/stale) instead.
    """

    def __init__(self, finder=None, clock=None, stale_seconds=STALE_SECONDS):
        self._find = finder or find_report_file
        self._clock = clock or time.time
        self._stale = float(stale_seconds)
        self._path = None
        self._state = None

    def poll(self) -> list[str]:
        report = self._find()
        if report is None:
            return []
        try:
            age = self._clock() - report.stat().st_mtime
        except OSError:
            return []
        state = "fresh" if age <= self._stale else "stale"
        if state == self._state and report == self._path:
            return []
        self._path, self._state = report, state
        if state == "fresh":
            return [
                f"[状态] 客户端正在运行，报告每秒更新：{report}",
                "[状态] 编程工具里 client_ping 应返回 alive=true，"
                "client_get_probe_report 可读最新快照",
            ]
        if age >= 3600:
            age_text = f"{age / 3600:.1f} 小时"
        else:
            age_text = f"{int(age)} 秒"
        return [f"[状态] 这个报告已有 {age_text} 没更新（客户端可能没开）：{report}"]


def _watch_report(stop: threading.Event, interval: float = 2.0, watcher=None) -> None:
    """Print heartbeat transitions until ``stop`` is set."""
    watcher = watcher or ReportWatcher()
    while not stop.wait(interval):
        for line in watcher.poll():
            _say(line)


def _log_failure(text: str) -> None:
    try:
        with LOG_PATH.open("a", encoding="utf-8") as log:
            log.write(f"\n===== {datetime.now():%Y-%m-%d %H:%M:%S} =====\n")
            log.write(f"Python {sys.version}\n{text}\n")
    except OSError:
        pass


def _banner(url: str, config: Path, report: Path | None) -> None:
    line = "=" * 62
    _say()
    _say(line)
    _say(" MXSJ 客户端 MCP 已启动")
    _say("-" * 62)
    _say(f" 编程工具接入地址：{url}")
    _say(f" 配置文件：        {config}")
    _say(
        f" 客户端报告：      {report if report else '暂未找到（启动游戏后会自动发现）'}"
    )
    _say("-" * 62)
    _say(" 关闭这个窗口即停止服务。不需要在这里输入任何命令。")
    _say(line)
    _say()


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    check_only = "--check-only" in args
    args = [arg for arg in args if arg != "--check-only"]

    _say("MXSJ 客户端 MCP · 启动自检")
    _say(f"Python {sys.version.split()[0]}：{sys.executable}")
    if sys.version_info < MIN_PYTHON:  # noqa: UP036
        _say(
            f"Python 版本过低：需要 {MIN_PYTHON[0]}.{MIN_PYTHON[1]} 以上，"
            f"当前是 {sys.version.split()[0]}。"
        )
        _say(
            "请到 https://www.python.org/downloads/ 安装新版 Python，"
            "安装时勾选 “Add python.exe to PATH”。"
        )
        return 2

    missing = find_missing()
    if missing and (check_only or not install_packages(missing)):
        _say("缺少依赖：" + "、".join(missing))
        _say(
            "自动安装未成功。请确认电脑能上网，然后双击重试；"
            "仍然失败就把本窗口内容和 启动日志.txt 一起发回来。"
        )
        return 2
    if missing:
        _say("依赖已补齐。")

    sys.path.insert(0, str(HERE / "src"))
    if check_only:
        _say("环境已就绪，可以双击启动。")
        return 0

    if "--transport" in args:
        transport = args[args.index("--transport") + 1]
        if transport == "stdio":
            # 编程工具用 stdio 拉起本脚本时保持原行为，不弹一键启动界面。
            from mxsj_client_mcp.run import main as run_main

            return run_main(args)

    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    token = load_or_create_token()
    port = pick_port()
    PORT_PATH.write_text(f"{port}\n", encoding="utf-8", newline="\n")
    url = f"http://127.0.0.1:{port}/mcp"
    report = find_report_file()
    config = write_client_config(url, token, CONFIG_PATH)
    _banner(url, config, report)

    stop = threading.Event()
    watcher = threading.Thread(
        target=_watch_report, args=(stop,), name="report-watch", daemon=True
    )
    watcher.start()
    from mxsj_client_mcp.run import main as run_main

    try:
        return run_main([*server_args(port, token, report), *args])
    except KeyboardInterrupt:
        return 0
    finally:
        stop.set()


def entrypoint() -> int:
    try:
        return main()
    except Exception:
        text = traceback.format_exc()
        _log_failure(text)
        _say("")
        _say("启动失败，错误详情已写入日志文件：")
        _say(f"    {LOG_PATH}")
        _say("把日志内容发给开发者即可定位问题。")
        return 2


if __name__ == "__main__":
    raise SystemExit(entrypoint())
