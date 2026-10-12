"""条目列表面板：表格模型 + 类型/文本过滤 + 缩略图列。"""
from __future__ import annotations

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    Signal,
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from ..core.codecs.detect import KIND_LABELS, EntryKind
from ..core.model.document import PackDocument

ROLE_KIND = Qt.UserRole + 1
ROLE_INDEX = Qt.UserRole + 2


class EntryTableModel(QAbstractTableModel):
    """资源包条目表模型（种类与大小在打开时预计算，避免逐格嗅探）。"""

    HEADERS = ["", "#", "名称", "类型", "大小", "状态"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._doc: PackDocument | None = None
        self._kinds: list[EntryKind] = []
        self._sizes: list[int] = []
        self._thumb_images: dict[int, QImage] = {}
        self._thumb_pixmaps: dict[int, QPixmap] = {}

    # ---------------------------------------------------------- 数据 ----
    def set_document(self, doc: PackDocument, kinds: list[EntryKind]) -> None:
        self.beginResetModel()
        self._doc = doc
        self._kinds = list(kinds)
        self._sizes = [len(doc.content(i)) for i in range(doc.count)]
        self._thumb_images.clear()
        self._thumb_pixmaps.clear()
        self.endResetModel()

    def refresh_entry(self, index: int) -> None:
        """条目被修改后刷新其种类、大小与缩略图。"""
        if self._doc is None or not 0 <= index < self._doc.count:
            return
        self._kinds[index] = self._doc.entry_kind(index)
        self._sizes[index] = len(self._doc.content(index))
        self._thumb_images.pop(index, None)
        self._thumb_pixmaps.pop(index, None)
        left = self.index(index, 0)
        right = self.index(index, len(self.HEADERS) - 1)
        self.dataChanged.emit(left, right)

    def refresh_all_states(self) -> None:
        if self._doc is None:
            return
        left = self.index(0, len(self.HEADERS) - 1)
        right = self.index(self._doc.count - 1, len(self.HEADERS) - 1)
        self.dataChanged.emit(left, right)

    def set_thumbnail(self, index: int, image: QImage) -> None:
        self._thumb_images[index] = image
        self._thumb_pixmaps.pop(index, None)
        cell = self.index(index, 0)
        self.dataChanged.emit(cell, cell, [Qt.DecorationRole])

    def kind_of(self, index: int) -> EntryKind:
        return self._kinds[index]

    def source_index(self, row: int) -> int:
        return row

    # ------------------------------------------------------- Qt 模型 ----
    def rowCount(self, parent=None) -> int:  # noqa: N802
        if (parent is not None and parent.isValid()) or self._doc is None:
            return 0
        return self._doc.count

    def columnCount(self, parent=None) -> int:  # noqa: N802
        return len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):  # noqa: N802
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.HEADERS[section]
        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):  # noqa: N802
        if not index.isValid() or self._doc is None:
            return None
        row, col = index.row(), index.column()
        doc = self._doc
        if role == ROLE_KIND:
            return self._kinds[row]
        if role == ROLE_INDEX:
            return row
        if role == Qt.DecorationRole and col == 0:
            pix = self._thumb_pixmaps.get(row)
            if pix is None and row in self._thumb_images:
                pix = QPixmap.fromImage(self._thumb_images[row])
                self._thumb_pixmaps[row] = pix
            return pix
        if role != Qt.DisplayRole:
            return None
        if col == 1:
            return row
        if col == 2:
            return doc.label(row)
        if col == 3:
            return KIND_LABELS[self._kinds[row]]
        if col == 4:
            return self._sizes[row]
        if col == 5:
            return "已修改" if doc.is_dirty(row) else ""
        return None


class EntryFilterProxy(QSortFilterProxyModel):
    """按类型与文本（名称或序号）过滤条目。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = ""
        self._kind: EntryKind | None = None

    def set_text(self, text: str) -> None:
        self._text = text.strip()
        self.invalidateFilter()

    def set_kind(self, kind: EntryKind | None) -> None:
        self._kind = kind
        self.invalidateFilter()

    def filterAcceptsRow(self, row, parent):  # noqa: N802
        model: EntryTableModel = self.sourceModel()  # type: ignore[assignment]
        if self._kind is not None and model.kind_of(row) is not self._kind:
            return False
        if self._text:
            label = model.data(model.index(row, 2), Qt.DisplayRole) or ""
            if self._text not in str(label) and self._text != str(row):
                return False
        return True


class EntryPanel(QWidget):
    """左侧条目面板：搜索框 + 类型下拉 + 条目表。"""

    entry_selected = Signal(int)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.model = EntryTableModel(self)
        self.proxy = EntryFilterProxy(self)
        self.proxy.setSourceModel(self.model)

        self._search = QLineEdit(self)
        self._search.setPlaceholderText("按名称或序号过滤…")
        self._search.textChanged.connect(self.proxy.set_text)
        self._kind_box = QComboBox(self)
        self._kind_box.addItem("全部类型", None)
        for kind, label in KIND_LABELS.items():
            self._kind_box.addItem(label, kind)
        self._kind_box.currentIndexChanged.connect(
            lambda _i: self.proxy.set_kind(self._kind_box.currentData()))

        self._table = QTableView(self)
        self._table.setModel(self.proxy)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        self._table.setSelectionMode(QTableView.SingleSelection)
        self._table.setEditTriggers(QTableView.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setColumnWidth(0, 52)
        self._table.setColumnWidth(1, 52)
        self._table.selectionModel().selectionChanged.connect(
            self._on_selection)

        top = QHBoxLayout()
        top.addWidget(self._search, 1)
        top.addWidget(self._kind_box)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(top)
        layout.addWidget(self._table, 1)

    # ---------------------------------------------------------- 接口 ----
    def set_document(self, doc: PackDocument, kinds: list[EntryKind]) -> None:
        self.model.set_document(doc, kinds)

    def select_entry(self, source_index: int) -> None:
        proxy_index = self.proxy.mapFromSource(self.model.index(source_index, 0))
        if proxy_index.isValid():
            self._table.setCurrentIndex(proxy_index)
            self._table.scrollTo(proxy_index)

    def current_entry(self) -> int:
        proxy_index = self._table.currentIndex()
        if not proxy_index.isValid():
            return -1
        return int(proxy_index.data(ROLE_INDEX))

    def _on_selection(self) -> None:
        index = self.current_entry()
        if index >= 0:
            self.entry_selected.emit(index)
