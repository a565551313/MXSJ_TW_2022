#!/usr/bin/env python3
"""资源编辑器的轻量入口（不装依赖、不做环境检查）。

    python run.py [资源包或目录路径]

日常双击请用 ``启动编辑器.bat``（会先自检并自动装依赖）；本文件是给
PyInstaller（``build_exe.bat`` / ``resource_editor.spec``）和已经配好环境的人用的，
缺 PySide6 时会直接抛 ImportError。
"""
from __future__ import annotations

import sys
from pathlib import Path

# 源码目录下直接运行时把 src/ 加进搜索路径；PyInstaller 打包后 src/ 不存在，
# 包已经在 PYZ 里，这里自然跳过。
_SRC = Path(__file__).resolve().parent / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from resource_editor.app import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
