"""父子级界面辅助：置父候选清单与「置父 ▸」子菜单。

画布右键与控件树右键共用同一套候选规则：排除被操作控件自身及其
子孙（防环），按树深度缩进显示 ``名称 · 类型``，父控件项回调交回
控件对象；「设为顶级」不在本模块，由调用方挂用现有提升命令。
"""

from __future__ import annotations

from PySide6.QtWidgets import QMenu, QWidget

from ..core.model import LayoutDocument, Widget


def depth_of(widget: Widget) -> int:
    """控件在树里的深度（顶级为 0）。"""
    depth = 0
    node = widget.parent
    while node is not None:
        depth += 1
        node = node.parent
    return depth


def parent_candidates(doc: LayoutDocument | None,
                      targets: list[Widget]) -> list[Widget]:
    """可以作为 targets 父控件的控件（文档顺序，排除 targets 子树）。"""
    if doc is None:
        return []
    blocked: set[int] = set()
    for widget in targets:
        blocked.update(id(node) for node in widget.walk())
    return [w for w in doc.all_widgets() if id(w) not in blocked]


def build_parent_menu(host: QWidget, doc: LayoutDocument | None,
                      targets: list[Widget], on_pick) -> QMenu:
    """构建「置父 ▸」子菜单；on_pick(控件) 由调用方执行置父。"""
    menu = QMenu("置父", host)
    candidates = parent_candidates(doc, targets)
    if not candidates:
        action = menu.addAction("（没有可选的父控件）")
        action.setEnabled(False)
        return menu
    for widget in candidates:
        label = ("　" * depth_of(widget)
                 + f"{widget.name or '(未命名)'} · {widget.wtype}")
        action = menu.addAction(label)
        action.triggered.connect(lambda _checked=False, w=widget: on_pick(w))
    return menu
