"""内置的已知布局路径目录（供资源包识别与代际标记）。

资源包内不存文件名、只有路径哈希，无法直接枚举包中布局。本
目录收录了从客户端脚本（script.fls 全部条目）中收获的全部被
引用的 ``.dlg`` 路径（2,901 条），挂载包时逐条用哈希核对是否
包含：命中的入资源树，近乎全量的主 UI 包还会列出包内缺失项
（死引用/热更新候选，灰显）。代际判读见 generation_of。
"""

from __future__ import annotations

import re
from pathlib import Path

_CACHE: list[str] | None = None
_HASH_CACHE: dict[int, str] | None = None
_UNENCODABLE: list[str] = []

__all__ = [
    "GENERATION_CURRENT",
    "GENERATION_LEGACY",
    "GENERATION_TRANSITIONAL",
    "generation_of",
    "known_layout_hashes",
    "known_layout_paths",
]

# 布局代际（静态判读：第四代与新登录、年份活动、new* 新系统目录
# 为现役；dialog3 为第三代过渡；其余多为历史沉积。老模块代码
# 仍在包中引用老布局，精确可达性需运行时调用图，这里只作标记。）
GENERATION_CURRENT = "current"
GENERATION_TRANSITIONAL = "transitional"
GENERATION_LEGACY = "legacy"

_YEAR_RE = re.compile(r"20\d\d")


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


def known_layout_hashes() -> dict[int, str]:
    """路径目录的哈希索引：{路径哈希: 路径}（整包扫描时快速相交）。

    GBK 不可编码的路径**跳过并留痕**，不参与索引：旧实现用
    ``encode("gbk", "replace")`` 把字符静默换成 ``?``，算出的哈希指向
    另一个路径——查得到/查不到都变得不可信（分析报告 P2-2）。引擎只认
    GBK 字节，这类路径在引擎侧同样寻址不到；清单用
    :func:`unencodable_layout_paths` 取。
    """
    global _HASH_CACHE
    if _HASH_CACHE is None:
        from .mxhash import path_hash

        _HASH_CACHE = {}
        _UNENCODABLE.clear()
        for path in known_layout_paths():
            try:
                digest = path_hash(path)
            except ValueError:
                _UNENCODABLE.append(path)
                continue
            _HASH_CACHE.setdefault(digest, path)
    return dict(_HASH_CACHE)


def unencodable_layout_paths() -> list[str]:
    """内置目录里 GBK 不可编码、因而引擎寻址不到的路径（读表后才有值）。"""
    known_layout_hashes()
    return list(_UNENCODABLE)


def generation_of(res_path: str) -> str:
    """按路径判断布局代际：current / transitional / legacy。"""
    parts = [seg.lower() for seg in
             res_path.replace("\\", "/").split("/") if seg]
    if not parts:
        return GENERATION_LEGACY
    top = parts[0]
    if top in ("dialog4", "combdialog4", "login_new"):
        return GENERATION_CURRENT
    if top == "dialog3":
        return GENERATION_TRANSITIONAL
    if any(_YEAR_RE.search(seg) for seg in parts):
        return GENERATION_CURRENT
    if any(seg.startswith("new") or seg.endswith(("_new", "_new.dlg"))
           for seg in parts):
        return GENERATION_CURRENT
    return GENERATION_LEGACY
