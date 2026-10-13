"""内置的已知布局路径目录（供"从资源包打开"时自动识别）。

资源包内不存文件名、只有路径哈希，无法直接枚举包中布局。本
目录收录了从客户端脚本中收获的全部被引用的 ``.dlg`` 路径
（2,901 条），选包后逐条用哈希核对该包是否包含，命中的自动
进入可搜索的下拉列表；目录里没有的新布局仍可手动输入路径。
"""

from __future__ import annotations

from pathlib import Path

_CACHE: list[str] | None = None

__all__ = ["known_layout_paths"]


def _catalog_file() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "known_layouts.txt"


def known_layout_paths() -> list[str]:
    """返回内置布局路径目录（进程内缓存）。"""
    global _CACHE
    if _CACHE is None:
        try:
            text = _catalog_file().read_text(encoding="utf-8")
            _CACHE = [line.strip() for line in text.splitlines()
                      if line.strip()]
        except OSError:
            _CACHE = []
    return list(_CACHE)
