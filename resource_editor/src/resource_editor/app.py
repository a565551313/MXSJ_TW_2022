"""应用入口：组装 QApplication 与主窗口。"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .gui.main_window import MainWindow


def main(argv: list[str] | None = None) -> int:
    """启动资源编辑器。

    可带一个参数：资源包路径（打开它并把工作目录切到其所在文件夹）
    或目录路径（设为工作目录）；无参数时恢复上次的工作目录。
    """
    args = list(sys.argv if argv is None else argv)
    app = QApplication(args)
    app.setApplicationName("MXSJ 资源编辑器")
    window = MainWindow()
    window.show()
    if len(args) > 1:
        target = Path(args[1])
        if target.is_dir():
            window.set_workspace(target)
        else:
            window.open_file(args[1])
    else:
        window.restore_workspace()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
