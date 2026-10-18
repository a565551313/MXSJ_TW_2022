"""Application assembly: CLI today, future PySide6 entry stays outside core."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from wsgiref.simple_server import WSGIRequestHandler, make_server

from mxsj_web_server import __version__
from mxsj_web_server.core.content import build
from mxsj_web_server.core.paths import initialize_example, user_directory
from mxsj_web_server.core.publication import create_app


def resource_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "mxsj_web_server" / "data"
    return Path(__file__).resolve().parent / "data"


class SafeHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        # No arbitrary URL/query/header/error text in the development access log.
        pass

    def log_request(self, code="-", size="-"):
        try:
            status = int(code)
        except (TypeError, ValueError):
            status = 0
        print(json.dumps({"event": "http.response", "status": status}), file=sys.stderr)


def content_main(argv: list[str] | None = None, *, raise_errors: bool = False) -> int:
    parser = argparse.ArgumentParser(description="生成已知原生文本资源，不生成更新清单")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        build(args.source, args.output)
    except Exception:
        if raise_errors:
            raise
        print(
            "CONTENT_BUILD_FAILED: check schema, Big5 text and new output path",
            file=sys.stderr,
        )
        return 1
    print("Built three legacy text resources; native client acceptance still required")
    return 0


def main(argv: list[str] | None = None, *, raise_errors: bool = False) -> int:
    args_list = list(sys.argv[1:] if argv is None else argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    if args_list[:1] == ["content"]:
        return content_main(args_list[1:], raise_errors=raise_errors)
    parser = argparse.ArgumentParser(
        description="Web 文本分发服务（当前仅命令行，无管理 GUI）"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument(
        "--check-only", action="store_true", help="校验配置，不启动服务"
    )
    parser.add_argument("--init-example", type=Path, help="复制假数据到全新目录后退出")
    args = parser.parse_args(args_list)
    if args.init_example and args.config:
        parser.error("--init-example and --config cannot be used together")
    try:
        if args.init_example:
            initialize_example(resource_directory(), args.init_example)
            print("已生成独立示例配置；未启动服务，未修改客户端。")
            return 0
        config = args.config
        if config is None:
            if args.check_only:
                config = resource_directory() / "config.example.json"
            else:
                profile = user_directory(os.environ.get("APPDATA"), Path.home())
                config = profile / "config.json"
                if not config.exists():
                    initialize_example(resource_directory(), profile)
        app = create_app(config)
        if args.check_only:
            print("Publication configuration validated; no server started")
            return 0
        with make_server(
            args.host, args.port, app, handler_class=SafeHandler
        ) as server:
            print(
                "web_server 开发服务已启动；无管理 GUI，不是生产 HTTP 服务器。",
                flush=True,
            )
            print(
                f"监听 {server.server_address[0]}:{server.server_address[1]}"
                "；Ctrl+C 停止。",
                flush=True,
            )
            server.serve_forever()
    except KeyboardInterrupt:
        return 0
    except Exception:
        if raise_errors:
            raise
        print(
            "WEB_SERVER_START_FAILED: inspect configuration, files and port",
            file=sys.stderr,
        )
        return 1
    return 0
