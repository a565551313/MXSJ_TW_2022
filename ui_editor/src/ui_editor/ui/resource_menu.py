"""左侧资源树的右键菜单构建（只搭菜单，不 exec，便于测试与复用）。

节点数据形态：
* ``("packroot", 包路径)`` —— 资源包根节点；
* ``("pack", 包路径, 包内路径)`` —— 包里的一个布局；
* ``("file", 本地路径)`` —— 散装 ``.dlg``；
* ``("dirroot", 目录)`` 等其它形态不给菜单。
"""

from __future__ import annotations

from PySide6.QtWidgets import QMenu

__all__ = ["build_resource_menu", "REPLACE_TOOLTIP"]

REPLACE_TOOLTIP = (
    "用选中的 .dlg 内容顶掉这个布局：名字与路径不变，控件内容全换成\n"
    "所选文件的；包内布局按「存包」生成新包，散装文件按「保存」写回。")


def build_resource_menu(parent, data, *, missing: bool,
                        on_export, on_import, on_open_path,
                        on_replace) -> QMenu | None:
    """按节点类型搭右键菜单；不可操作的节点返回 None。"""
    kind = data[0] if data else ""
    menu = QMenu(parent)
    if kind in ("file", "pack"):
        export = menu.addAction("导出布局…")
        export.setToolTip("导出来源原文，不含未保存编辑，不转换文本编码")
        export.setEnabled(not missing)
        export.triggered.connect(lambda: on_export(tuple(data)))
        replace = menu.addAction("替换布局…")
        replace.setToolTip(REPLACE_TOOLTIP)
        replace.setEnabled(not missing)
        replace.triggered.connect(lambda: on_replace(tuple(data)))
    elif kind == "packroot":
        action = menu.addAction("导入布局文件…")
        action.triggered.connect(lambda: on_import(data[1]))
        open_action = menu.addAction("按包内路径打开布局…")
        open_action.triggered.connect(lambda: on_open_path(data[1]))
    else:
        return None
    return menu
