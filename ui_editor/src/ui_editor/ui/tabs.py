"""多标签编辑会话状态（纯 Python，不依赖 Qt）。

每个标签页是一个 :class:`EditorSession`：保存自己的文档、选择快照与
视图变换；画布（QGraphicsView）全窗共享一份，切标签时换文档、还
视图状态。同来源（包内路径 / 散装路径）视为同一布局：再次打开只
切回已有标签，不新开重复页、不丢未保存编辑。
"""

from __future__ import annotations

from typing import Any

from ..core.model import LayoutDocument

__all__ = ["EditorSession"]


class EditorSession:
    """一个标签页的编辑会话（纯状态；画布共享，切换时换文档）。"""

    def __init__(self, doc: LayoutDocument | None, key: tuple | None,
                 view: Any = None) -> None:
        self.doc = doc
        self.key = key
        self.selected: Any = None
        self.selection_anchor: list[int] | None = None
        self.transform: Any = None  # QTransform 不进类型标注：本模块无 Qt 依赖
        self._view = view
        # 标签锁定：只影响批量关闭（左/右/其他/全部），单独关闭仍然可以。
        # 不进布局文件，也不影响保存；关掉编辑器就没了。
        self.locked = False

    @staticmethod
    def key_of(doc: LayoutDocument | None) -> tuple | None:
        """文档的来源身份：同键即同一布局（重开=切回旧标签）。"""
        if doc is None:
            return None
        if doc.source_pack:
            return ("pack", *doc.source_pack)
        if doc.source_path:
            return ("file", doc.source_path)
        return None

    def snapshot(self, selected: Any, selection_anchor: list[int] | None
                 ) -> None:
        """切走前收存选择与缩放/平移（视图状态随标签带走）。"""
        self.selected = selected
        self.selection_anchor = selection_anchor
        if self._view is not None:
            self.transform = self._view.transform()

    def label(self) -> str:
        """标签文字：显示名 + 未保存（或待入新包）星标。"""
        name = self.doc.display_name if self.doc else "未打开布局"
        return f"{name}*" if self.needs_confirm() else name

    def needs_confirm(self) -> bool:
        """关闭/刷新前需要用户确认丢弃的条件。"""
        return self.doc is not None and bool(
            self.doc.dirty or self.doc.pending_pack_import)
