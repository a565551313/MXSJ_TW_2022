"""左侧文件面板、控件树面板与控件面板（调色板）。"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.model import WIDGET_TYPES, LayoutDocument, Widget


class LayoutFilesPanel(QWidget):
    """一个目录下全部 .dlg 的文件树，双击打开。"""

    file_opened = Signal(str)
    directory_chosen = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        bar = QHBoxLayout()
        choose = QPushButton("打开布局目录…")
        choose.clicked.connect(lambda: self.directory_chosen.emit(""))
        refresh = QToolButton()
        refresh.setText("↻")
        refresh.setToolTip("刷新文件列表")
        refresh.clicked.connect(self.refresh)
        bar.addWidget(choose, 1)
        bar.addWidget(refresh)
        layout.addLayout(bar)
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.itemDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self._tree, 1)
        self._directory: Path | None = None

    def set_directory(self, path: str | Path) -> None:
        self._directory = Path(path)
        self.refresh()

    @property
    def directory(self) -> Path | None:
        return self._directory

    def refresh(self) -> None:
        self._tree.clear()
        if self._directory is None or not self._directory.is_dir():
            return

        def fill(parent_item: QTreeWidgetItem | QTreeWidget, folder: Path):
            try:
                entries = sorted(folder.iterdir(),
                                 key=lambda p: (p.is_file(), p.name.lower()))
            except OSError:
                return
            for entry in entries:
                item = QTreeWidgetItem(parent_item, [entry.name])
                if entry.is_dir():
                    item.setData(0, Qt.ItemDataRole.UserRole, "")
                    fill(item, entry)
                elif entry.suffix.lower() == ".dlg":
                    item.setData(0, Qt.ItemDataRole.UserRole, str(entry))

        fill(self._tree, self._directory)

    def _on_double_click(self, item: QTreeWidgetItem) -> None:
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path:
            self.file_opened.emit(path)


class WidgetTreePanel(QWidget):
    """布局的控件层级树，与画布/属性面板联动选择。"""

    widget_selected = Signal(object)
    add_child_requested = Signal()
    delete_requested = Signal()
    reorder_requested = Signal(object, int)  # (控件, -1 上移/+1 下移)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        bar = QHBoxLayout()
        self._add_btn = QPushButton("加子控件")
        self._add_btn.setToolTip("把调色板里选中的控件类型加为当前控件的子控件")
        self._del_btn = QPushButton("删除")
        up_btn = QToolButton()
        up_btn.setText("↑")
        up_btn.setToolTip("上移（绘制更靠前）")
        down_btn = QToolButton()
        down_btn.setText("↓")
        down_btn.setToolTip("下移")
        self._add_btn.clicked.connect(self.add_child_requested)
        self._del_btn.clicked.connect(self.delete_requested)
        up_btn.clicked.connect(lambda: self._reorder(-1))
        down_btn.clicked.connect(lambda: self._reorder(1))
        for btn in (self._add_btn, self._del_btn, up_btn, down_btn):
            bar.addWidget(btn)
        layout.addLayout(bar)
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.currentItemChanged.connect(self._on_current_changed)
        layout.addWidget(self._tree, 1)
        self._items: dict[int, QTreeWidgetItem] = {}
        self._widgets: dict[int, Widget] = {}
        self._current: Widget | None = None
        self._syncing = False

    def build(self, doc: LayoutDocument | None) -> None:
        self._tree.clear()
        self._items = {}
        self._widgets = {}
        self._current = None
        if doc is None:
            return

        def add(parent_item: QTreeWidgetItem | QTreeWidget, widget: Widget):
            label = f"{widget.name or '(未命名)'} · {widget.wtype}"
            item = QTreeWidgetItem(parent_item, [label])
            item.setData(0, Qt.ItemDataRole.UserRole, id(widget))
            self._items[id(widget)] = item
            self._widgets[id(widget)] = widget
            for child in widget.children:
                add(item, child)
            item.setExpanded(True)

        for root in doc.roots:
            add(self._tree, root)

    def update_label(self, widget: Widget) -> None:
        item = self._items.get(id(widget))
        if item is not None:
            item.setText(0, f"{widget.name or '(未命名)'} · {widget.wtype}")

    def select_widget(self, widget: Widget | None) -> None:
        self._current = widget
        item = self._items.get(id(widget)) if widget is not None else None
        self._syncing = True
        self._tree.setCurrentItem(item)
        self._syncing = False

    def current_widget(self) -> Widget | None:
        return self._current

    def _reorder(self, delta: int) -> None:
        if self._current is not None:
            self.reorder_requested.emit(self._current, delta)

    def _on_current_changed(self, item: QTreeWidgetItem | None) -> None:
        if self._syncing:
            return
        widget_id = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        self._current = self._find(widget_id)
        self.widget_selected.emit(self._current)

    def _find(self, widget_id: int | None) -> Widget | None:
        if widget_id is None:
            return None
        for item_id, tree_item in self._items.items():
            if item_id == widget_id:
                stack = [tree_item]
                while stack:
                    node = stack.pop()
                    if node is tree_item:
                        return self._widget_of(node)
                    stack.extend(node.child(i) for i in range(node.childCount()))
        return None

    def _widget_of(self, item: QTreeWidgetItem) -> Widget | None:
        # 控件对象由主窗口维护映射，这里借助 UserRole 的 id 反查其表
        return getattr(item, "_widget_ref", None)


class PalettePanel(QWidget):
    """控件调色板：双击或点按钮把控件加到选中控件/根级。"""

    add_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("控件类型（双击添加）："))
        self._list = QListWidget()
        for wtype in WIDGET_TYPES:
            self._list.addItem(QListWidgetItem(wtype))
        self._list.itemDoubleClicked.connect(
            lambda item: self.add_requested.emit(item.text()))
        layout.addWidget(self._list, 1)
        add = QPushButton("添加选中类型")
        add.clicked.connect(self._emit_current)
        layout.addWidget(add)
        hint = QLabel("目标：控件树/画布中选中的控件为父级，"
                      "未选中则加到根级。")
        hint.setWordWrap(True)
        layout.addWidget(hint)

    def _emit_current(self) -> None:
        item = self._list.currentItem()
        if item is not None:
            self.add_requested.emit(item.text())

    def current_type(self) -> str | None:
        item = self._list.currentItem()
        return item.text() if item is not None else None
