from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .core.catalog import load_catalog
from .core.export import export_site
from .core.io import ManualError
from .paths import application_root


def parser():
    result = argparse.ArgumentParser(description="MXSJ 只读脚本手册 0.1.0.dev1")
    result.add_argument("--version", action="version", version=__version__)
    result.add_argument("--content", type=Path, default=application_root())
    commands = result.add_subparsers(dest="command")
    for command in ("validate", "build"):
        child = commands.add_parser(command)
        child.add_argument("--verify-evidence", action="store_true")
        child.add_argument("--repository", type=Path)
        child.add_argument("--require-full-inventory", action="store_true")
        if command == "build":
            child.add_argument("--output", type=Path, required=True)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    if args.command is None:
        from PySide6.QtWidgets import QApplication

        from .gui.window import ManualWindow

        app = QApplication.instance() or QApplication([])
        window = ManualWindow(args.content)
        window.show()
        return app.exec()
    try:
        if args.verify_evidence and args.repository is None:
            raise ManualError("--verify-evidence 必须显式指定 --repository 仓库根目录")
        catalog = load_catalog(
            args.content,
            repository=args.repository if args.verify_evidence else None,
            require_full=args.require_full_inventory,
        )
        if args.command == "build":
            print(export_site(catalog, args.output, content_root=args.content))
        print(json.dumps(catalog.coverage(), ensure_ascii=False))
        for warning in catalog.warnings:
            print("WARNING:", warning)
        return 0
    except (OSError, ManualError) as exc:
        print(f"手册校验/生成失败：{exc}")
        return 2
