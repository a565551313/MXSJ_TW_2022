"""应用入口：组装 QApplication 与主窗口。"""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .gui.main_window import MainWindow


def main(argv: list[str] | None = None) -> int:
    """启动资源编辑器；可带一个资源包路径作为初始打开文件。"""
    args = list(sys.argv if argv is None else argv)
    app = QApplication(args)
    app.setApplicationName("MXSJ 资源编辑器")
    window = MainWindow()
    window.show()
    if len(args) > 1:
        window.open_file(args[1])
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
