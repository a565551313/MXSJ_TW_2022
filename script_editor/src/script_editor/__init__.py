"""Standalone dual-VM source editor with pinned standard Windows compilers."""

from __future__ import annotations

import sys

__version__ = "0.6.0.dev14"


def gui_version(version):
    # Qt 6.10 excludes Python 3.15; keep the tested older-host pin unchanged.
    return "6.12.0" if version >= (3, 15) else "6.10.3"


GUI_VERSION = gui_version(sys.version_info)
