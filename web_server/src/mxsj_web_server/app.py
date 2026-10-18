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


def create_manager(directory: Path):
    from mxsj_web_server.core.manager import Manager
    from mxsj_web_server.web.gateway import dispatch

    initial = json.loads(
        (resource_directory() / "content.example.json").read_text(encoding="utf-8-sig")
    )
    static = Path(__file__).resolve().parent / "web/admin/static"
    if getattr(sys, "frozen", False):
        static = Path(sys._MEIPASS) / "mxsj_web_server/web/admin/static"
    return Manager(directory, initial, static, dispatch)


def management_main(
    directory: Path, *, headless=False, enable_admin=False, set_password=False
):
    manager = create_manager(directory)
    if headless or set_password:
        try:
            if set_password:
                import getpass

                if not sys.stdin.isatty():
                    raise ValueError("设置密码必须使用交互终端")
                password = getpass.getpass("管理员密码：")
                if password != getpass.getpass("再次输入："):
                    raise ValueError("两次密码不一致")
                manager.set_password(password)
                return 0
            manager.control("public", "start")
            if enable_admin:
                manager.control("admin", "start")
            import threading

            stopped = threading.Event()
            import signal

            old_handler = signal.signal(signal.SIGTERM, lambda *_: stopped.set())
            try:
                stopped.wait()
            except KeyboardInterrupt:
                pass
            finally:
                signal.signal(signal.SIGTERM, old_handler)
        finally:
            manager.close()
        return 0
    try:
        from PySide6.QtWidgets import QApplication

        from mxsj_web_server.gui.main_window import MainWindow

        application = QApplication.instance() or QApplication(sys.argv[:1])
        application.setQuitOnLastWindowClosed(False)
        application.setApplicationName("MXSJWebServer")
        application.setApplicationVersion(__version__)
        window = MainWindow(manager)
        window.show()
        return application.exec()
    finally:
        manager.close()


def main(argv: list[str] | None = None, *, raise_errors: bool = False) -> int:
    args_list = list(sys.argv[1:] if argv is None else argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    if args_list[:1] == ["content"]:
        return content_main(args_list[1:], raise_errors=raise_errors)
    parser = argparse.ArgumentParser(
        description="Web 服务管理器：本地 GUI、独立公开服务与管理后台"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--gui", action="store_true")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--state-dir", type=Path)
    parser.add_argument("--enable-admin", action="store_true")
    parser.add_argument("--set-admin-password", action="store_true")
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
    if args.gui and args.headless:
        parser.error("--gui and --headless are mutually exclusive")
    if args.enable_admin and not args.headless:
        parser.error(
            "--enable-admin requires --headless; GUI always starts with listeners off"
        )
    if args.config and (args.gui or args.headless or args.set_admin_password):
        parser.error(
            "--config is the legacy read-only runner; management uses --state-dir"
        )
    try:
        if (
            not args.check_only
            and not args.init_example
            and (not args.config or args.gui or args.headless)
        ):
            directory = (
                args.state_dir
                or user_directory(os.environ.get("APPDATA"), Path.home()) / "manager"
            )
            return management_main(
                directory,
                headless=args.headless,
                enable_admin=args.enable_admin,
                set_password=args.set_admin_password,
            )
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


def entry_main(argv: list[str] | None = None) -> int:
    """Frozen/windowed entry still leaves diagnostics and an error dialog."""
    try:
        return main(argv, raise_errors=True)
    except Exception:
        import traceback
        from datetime import datetime, timezone

        text = traceback.format_exc()
        directory = user_directory(os.environ.get("APPDATA"), Path.home())
        try:
            directory.mkdir(parents=True, exist_ok=True)
            with (directory / "启动日志.txt").open("a", encoding="utf-8") as stream:
                stream.write(
                    f"[{datetime.now(timezone.utc).isoformat()}] "
                    f"Python {sys.version}\n{text}\n"
                )
        except OSError:
            pass
        args = list(sys.argv[1:] if argv is None else argv)
        cli = any(
            flag in args
            for flag in (
                "--headless",
                "--check-only",
                "--config",
                "content",
                "--set-admin-password",
                "--init-example",
            )
        )
        if cli:
            if sys.stderr:
                print("WEB_START_FAILED: inspect user startup log", file=sys.stderr)
            return 1
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox

            application = QApplication.instance() or QApplication(sys.argv[:1])
            QMessageBox.critical(
                None,
                "启动失败",
                "请检查管理目录、端口和依赖。启动诊断保存在用户目录，分享前请脱敏。",
            )
            del application
        except (ImportError, OSError):
            if sys.stderr:
                print(
                    "WEB_START_FAILED: inspect user startup log and Qt dependencies",
                    file=sys.stderr,
                )
        return 1
