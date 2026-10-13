"""应用入口：组装 QApplication 与主窗口。

命令行可带一个路径参数：``.dlg`` 文件直接打开、目录打开为布局
目录、``.fls`` 资源包则挂载后待选布局。
"""

from __future__ import annotations

import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv[:1])
    app.setApplicationName("MXSJ UI 编辑器")
    app.setOrganizationName("MXSJ")

    from .ui.main_window import MainWindow

    window = MainWindow()
    window.show()
    for arg in args:
        path = Path(arg)
        if path.is_file() and path.suffix.lower() == ".dlg":
            window.open_layout_file(str(path))
        elif path.is_dir():
            window.open_layout_dir(str(path))
        elif path.is_file() and path.suffix.lower() == ".fls":
            try:
                window.resolver.mount_pack(path)
                window._try_load_styles()
                window.scene.refresh_all()
            except Exception as exc:  # 启动参数错误不挡界面
                window._update_status(f"挂载 {arg} 失败：{exc}")
        break
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
