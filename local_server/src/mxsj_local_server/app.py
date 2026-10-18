"""应用入口；当前只提供操作员 CLI，不宣称 GUI 已完成。"""

from __future__ import annotations

import sys

from mxsj_local_server import __version__


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["--version"]:
        print(__version__)
        return 0
    from mxsj_local_server.cli import main as console_main

    return console_main(args)
