"""标题栏与状态栏里「这篇布局从哪来、会写到哪」的措辞。

只做字符串，不碰控件：主窗口 ``_update_title`` 调一次，标签页切换、
保存、换来源都会重新算。分出来是因为这几句话要能单独测，也免得
``main_window.py`` 再往上涨（结构护栏是每模块 ≤ 600 行）。
"""

from __future__ import annotations

__all__ = ["pack_name", "place_hint", "place_text", "window_title"]


def pack_name(path: str) -> str:
    """路径最后一段（兼容 ``\\`` 与 ``/``）。"""
    return str(path).replace("\\", "/").rsplit("/", 1)[-1]


def place_text(doc, *, loose: bool = False) -> str:
    """标题栏里的「从哪来 → 往哪写」，一句话。

    ``loose``：宽松模式，Ctrl+S 直接改写来源包——标题里说清楚，
    不要写成「→ 同一个包名」让人以为没保存。
    """
    if doc is None:
        return ""
    if doc.source_pack:
        source = pack_name(doc.origin_pack or doc.source_pack[0])
        if loose:
            return f"（{source}，宽松模式：原地写回）"
        if doc.output_pack:
            return f"（{source} → {pack_name(doc.output_pack)}）"
        return f"（{source}，还没写回新包）"
    if doc.source_path:
        return "（散装 .dlg）"
    return "（未保存）"


def place_hint(doc, *, loose: bool = False) -> str:
    """状态栏常驻：这个布局从哪读、Ctrl+S 会写到哪。"""
    if doc is None:
        return ""
    if doc.source_pack:
        source = pack_name(doc.origin_pack or doc.source_pack[0])
        if loose:
            return f"宽松模式：Ctrl+S 直接改写原包 {source}（无备份）"
        if doc.output_pack:
            return (f"来源只读：{source}　"
                    f"Ctrl+S 写回：{pack_name(doc.output_pack)}")
        return f"来源只读：{source}　第一次 Ctrl+S 会让你选输出包"
    if doc.source_path:
        return f"Ctrl+S 覆盖原文件：{pack_name(doc.source_path)}"
    return "还没保存过：Ctrl+S 会让你选存到哪"


def window_title(doc, version: str, *, loose: bool = False) -> str:
    name = doc.display_name if doc else "未打开布局"
    pending = doc and (doc.dirty or doc.pending_pack_import)
    star = "*" if pending else ""
    return f"{name}{star}{place_text(doc, loose=loose)} — MXSJ UI 编辑器 {version}"
