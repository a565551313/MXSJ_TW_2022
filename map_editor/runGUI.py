#!/usr/bin/env python3
"""GUI-only entry point for the MXSJ map editor.

Unlike ``run.py`` (which defaults to the CLI and only opens the window when
you pass ``--gui``, or — since the 2026-10-12 fix — when running as a
``console=False`` frozen EXE with no arguments), this script **always**
opens the graphical window, no matter what. It still accepts the same
flags as ``run.py`` so a remembered/explicit client root or scene table
still works, but any flag that would normally select a non-GUI action
(``--scan`` without ``--gui``, ``--export-json``, ``--export-png``,
``--girb-report``, ``--girb-dump``) is ignored for the purpose of deciding
*whether* to show the GUI — it opens either way.

    python runGUI.py                                   # 直接打开图形界面
    python runGUI.py --client-root "D:/Games/MXSJ"      # 打开界面并记住该目录
    python runGUI.py --scene-table my_scenes.json       # 打开界面并使用自定义场景表

If Qt is not installed/available, this fails with the same import error
``run.py --gui`` would — there is no headless fallback by design, since the
whole point of this entry point is "always show the window".
"""
from __future__ import annotations

import sys
from pathlib import Path

# Works from a source checkout and from a PyInstaller bundle (where the
# package is already importable and this insert is a harmless no-op).
_SRC = Path(__file__).resolve().parent / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from map_editor.cli import main  # noqa: E402


def main_gui(argv: list[str] | None = None) -> int:
    """Run the editor like ``run.py``, but always force the GUI on.

    Implemented by injecting ``--gui`` into the argument list handed to the
    shared CLI parser/dispatcher, so every other flag (``--client-root``,
    ``--scene-table``, ...) keeps working exactly like it does for
    ``run.py --gui ...``; only the "should I show a window" decision is
    hard-forced to yes.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if "--gui" not in args:
        args = ["--gui", *args]
    return main(args)


if __name__ == "__main__":
    raise SystemExit(main_gui())
