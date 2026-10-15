from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="MXSJ脚本编辑器（实验版；Windows发行尚未验收）"
    )
    parser.add_argument("--version", action="version", version=__version__)
    args = sys.argv[1:] if argv is None else argv
    parser.parse_args(args)
    from PySide6.QtWidgets import QApplication

    from .gui.window import Window

    root = (
        Path(sys.executable).resolve().parent
        if getattr(sys, "frozen", False)
        else Path(__file__).resolve().parents[2]
    )
    application = QApplication.instance() or QApplication([sys.argv[0]])
    window = Window(root)
    window.show()
    return application.exec()
