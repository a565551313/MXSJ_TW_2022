"""脚本关联面板：当前布局与 script.fls 的静态关联（只读信息）。

数据来自 core.script_index 的静态字节码挖掘：引用此布局的脚本
模块、被脚本按名取用的控件、代码现造按钮的皮肤。静态索引覆盖
不了动态拼名，面板文案如实注明「静态推断」，不假装运行时事实。
点列表中的名字可回画布选中对应控件。
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from ..core.model import Widget
from ..core.script_index import LayoutLink


class ScriptPanel(QWidget):
    """「脚本」页：布局级关联清单 + 当前选中控件的关联详情。"""

    name_chosen = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        self._title = QLabel("脚本关联（静态索引）")
        self._title.setWordWrap(True)
        layout.addWidget(self._title)
        self._info = QLabel(
            "打开布局后，这里显示引用它的脚本与被脚本取用的控件。")
        self._info.setWordWrap(True)
        self._info.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._info)
        self._names = QListWidget()
        self._names.setToolTip("被脚本按名取用的控件；点击在画布上选中它")
        self._names.itemClicked.connect(self._emit_name)
        layout.addWidget(self._names, 1)
        self._detail = QLabel("未选中控件。")
        self._detail.setWordWrap(True)
        self._detail.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._detail)
        self._link: LayoutLink | None = None

    # ------------------------------------------------------------------
    def _emit_name(self, item: QListWidgetItem) -> None:
        name = item.data(Qt.ItemDataRole.UserRole)
        if name:
            self.name_chosen.emit(str(name))

    def set_link(self, path: str | None, link: LayoutLink | None) -> None:
        """切换当前布局的关联（打开文档/换文档时调用）。"""
        self._link = link
        self._names.clear()
        self._detail.setText("未选中控件。")
        if link is None:
            self._title.setText("脚本关联（静态索引）")
            self._info.setText(
                f"布局「{path or '未命名'}」在静态索引里没有脚本关联"
                "（可能没还原、动态引用，或尚未被脚本加载）。"
                if path else "先打开一个布局。")
            return
        self._title.setText(f"脚本关联：{link.path}")
        module_lines = "\n".join(
            f"· {module}（条目 {entry}）" for entry, module in link.modules)
        claimed = set(link.objects) | set(link.skins)
        self._info.setText(
            f"引用脚本 {len(link.modules)} 个；被脚本取用的控件 "
            f"{len(claimed)} 个，其中代码现造皮肤 "
            f"{len(link.skins)} 个（静态推断，进游戏为准）：\n"
            f"{module_lines}")
        for name in sorted(claimed):
            tags = []
            if any(ref.anchor for ref in link.objects.get(name, [])):
                tags.append("占位锚点")
            if name in link.skins:
                tags.append("代码皮肤")
            item = QListWidgetItem(
                f"{name}（{'、'.join(tags)}）" if tags else name)
            item.setData(Qt.ItemDataRole.UserRole, name)
            self._names.addItem(item)

    def set_widget(self, widget: Widget | None) -> None:
        """按当前选中控件刷新底部详情。"""
        link = self._link
        if widget is None:
            self._detail.setText("未选中控件。")
            return
        if link is None:
            self._detail.setText(
                f"「{widget.name}」：当前布局无脚本关联信息。")
            return
        lines = []
        refs = link.objects.get(widget.name, [])
        if refs:
            wheres = "；".join(
                f"{ref.cls}.{ref.func}" for ref in refs[:3])
            lines.append(
                f"被脚本按名取用 {len(refs)} 处（{wheres}）"
                + ("；取后读位置，是占位锚点。"
                   if any(ref.anchor for ref in refs) else "。"))
        skins = link.skins.get(widget.name, [])
        if skins:
            skin = skins[0]
            lines.append(
                f"游戏里真按钮由代码现造：{skin.factory}"
                f"（皮肤 {skin.skin}"
                + (f"，文字「{skin.text}」" if skin.text else "")
                + (f"，消息号 {skin.msgid}" if skin.msgid is not None
                   else "")
                + f"，出自 {skin.cls}.{skin.func}）。"
                "挪它的位置有效（脚本读原地坐标），"
                "改它自己的图/字不会影响真按钮。")
        if not lines:
            lines.append("静态索引里没有脚本按名取用它"
                         "（可能是纯布局控件，或脚本用了动态名字）。")
        self._detail.setText(f"「{widget.name}」：\n" + "\n".join(lines))
