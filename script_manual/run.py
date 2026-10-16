from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path

if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))


def main():
    try:
        from mxsj_manual.app import main as application_main

        return application_main()
    except Exception:
        import os

        from PySide6.QtWidgets import QApplication, QMessageBox

        detail = traceback.format_exc()
        folder = Path(os.environ.get("APPDATA", Path.home())) / "MXSJScriptManual"
        message = detail
        try:
            folder.mkdir(parents=True, exist_ok=True)
            with (folder / "启动日志.txt").open("a", encoding="utf-8") as stream:
                stream.write(f"\n{datetime.now().isoformat()}\n{sys.version}\n{detail}")
            message = f"启动失败，完整日志：{folder / '启动日志.txt'}\n{detail}"
        except OSError:
            pass
        app = QApplication.instance() or QApplication([])
        QMessageBox.critical(None, "手册启动失败", message)
        del app
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
