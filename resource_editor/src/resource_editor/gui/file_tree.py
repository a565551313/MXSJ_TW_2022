"""左侧文件面板：设定工作目录 + 目录内 .fls 文件树（只显示文件名）。

目录里有没有 .fls 都可以设定：没有就空列表，不报错；
双击文件名打开该包到中间网格，单击仅选中并回报给主窗口。
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

_ROLE_PATH = Qt.UserRole


def _fmt_size(size: int) -> str:
    if size >= 1 << 30:
        return f"{size / (1 << 30):.2f} GB"
    if size >= 1 << 20:
        return f"{size / (1 << 20):.1f} MB"
    if size >= 1 << 10:
        return f"{size / (1 << 10):.1f} KB"
    return f"{size} B"


class DirectoryPanel(QWidget):
    """工作目录面板：目录设定/刷新按钮 + .fls 文件树。"""

    choose_dir_requested = Signal()
    refresh_requested = Signal()
    file_selected = Signal(str)
    file_activated = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._dir_label = QLabel("未设定目录", self)
        self._dir_label.setWordWrap(True)
        choose_btn = QPushButton("设定目录…", self)
        choose_btn.clicked.connect(self.choose_dir_requested.emit)
        refresh_btn = QPushButton("刷新", self)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        btn_row = QHBoxLayout()
        btn_row.addWidget(choose_btn)
        btn_row.addWidget(refresh_btn)
        btn_row.addStretch(1)

        self._tree = QTreeWidget(self)
        self._tree.setHeaderHidden(True)
        self._tree.setRootIsDecorated(False)
        self._tree.itemClicked.connect(
            lambda item, _col: self._emit(item, self.file_selected))
        self._tree.itemActivated.connect(
            lambda item, _col: self._emit(item, self.file_activated))

        self._items: dict[str, QTreeWidgetItem] = {}
        self._names: dict[str, str] = {}

        layout = QVBoxLayout(self)
        layout.addWidget(self._dir_label)
        layout.addLayout(btn_row)
        layout.addWidget(self._tree, 1)

    # ---------------------------------------------------------- 接口 ----
    def set_files(
        self,
        directory: Path | None,
        files: list[Path],
        modified: set[str],
    ) -> None:
        """重建文件树。files 为目录内的 .fls；modified 为已打开且有
        未保存修改的文件路径字符串集合（文件名后加 * 号）。"""
        self._tree.clear()
        self._items.clear()
        self._names.clear()
        if directory is None:
            self._dir_label.setText("未设定目录（点「设定目录」选择资源所在文件夹）")
            return
        self._dir_label.setText(f"目录：{directory}")
        for path in files:
            key = str(path.resolve())
            item = QTreeWidgetItem(self._tree)
            item.setData(0, _ROLE_PATH, key)
            try:
                size = path.stat().st_size
                item.setToolTip(0, f"{path}\n大小 {_fmt_size(size)}")
            except OSError:
                item.setToolTip(0, str(path))
            self._items[key] = item
            self._names[key] = path.name
            self._render_name(key, key in modified)
        if not files:
            item = QTreeWidgetItem(self._tree)
            item.setText(0, "（该目录下没有 .fls 文件）")
            item.setFlags(Qt.NoItemFlags)

    def set_modified(self, path: str, modified: bool) -> None:
        if path in self._items:
            self._render_name(path, modified)

    def select_file(self, path: str) -> None:
        item = self._items.get(path)
        if item is not None:
            self._tree.setCurrentItem(item)

    # ---------------------------------------------------------- 内部 ----
    def _render_name(self, key: str, modified: bool) -> None:
        suffix = " *" if modified else ""
        self._items[key].setText(0, f"{self._names[key]}{suffix}")

    def _emit(self, item: QTreeWidgetItem, signal: Signal) -> None:
        path = item.data(0, _ROLE_PATH)
        if path:
            signal.emit(str(path))
