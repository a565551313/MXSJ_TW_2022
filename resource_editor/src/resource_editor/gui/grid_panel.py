"""中间批量网格：把当前包的条目以缩略图网格分页展示。

分页而非滚动：一页固定条数（默认 50，可选 25/50/100/200），
支持首页/上一页/下一页/末页与页码跳转。缩略图由主窗口按页
在后台补齐（set_icons），缺图时显示按类型着色的占位图。
单击条目发 entry_selected，右侧详情随之更新。
"""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..core.codecs.detect import KIND_LABELS, EntryKind
from ..core.model.document import PackDocument

PAGE_SIZE_OPTIONS = (25, 50, 100, 200)
DEFAULT_PAGE_SIZE = 50

_ROLE_INDEX = Qt.UserRole

_KIND_COLORS = {
    EntryKind.SPRITE: QColor(66, 133, 244),
    EntryKind.PNG: QColor(52, 168, 107),
    EntryKind.JSON: QColor(230, 159, 34),
    EntryKind.TEXT: QColor(120, 120, 130),
    EntryKind.SCRIPT: QColor(142, 68, 173),
    EntryKind.BINARY: QColor(96, 96, 104),
}


def _placeholder_icon(kind: EntryKind) -> QIcon:
    """按类型生成占位图标（真实缩略图未就绪时显示）。"""
    pix = QPixmap(72, 72)
    color = _KIND_COLORS.get(kind, QColor(96, 96, 104))
    pix.fill(color)
    painter = QPainter(pix)
    painter.setPen(QColor(255, 255, 255))
    font = painter.font()
    font.setPixelSize(15)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(pix.rect(), Qt.AlignCenter, KIND_LABELS.get(kind, "?"))
    painter.end()
    return QIcon(pix)


class EntryGridPanel(QWidget):
    """分页缩略图网格面板。"""

    entry_selected = Signal(int)
    page_changed = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._doc: PackDocument | None = None
        self._kinds: list[EntryKind] = []
        self._view: list[int] = []
        self._page = 0
        self._per_page = DEFAULT_PAGE_SIZE
        self._kind_filter: EntryKind | None = None
        self._icons: dict[int, QIcon] = {}

        self._header = QLabel("未打开资源包（双击左侧文件名打开）", self)

        self._kind_box = QComboBox(self)
        self._kind_box.addItem("全部类型", None)
        for kind, label in KIND_LABELS.items():
            self._kind_box.addItem(label, kind)
        self._kind_box.currentIndexChanged.connect(self._on_kind_changed)

        self._per_page_box = QComboBox(self)
        for size in PAGE_SIZE_OPTIONS:
            self._per_page_box.addItem(f"每页 {size}", size)
        self._per_page_box.setCurrentIndex(
            PAGE_SIZE_OPTIONS.index(DEFAULT_PAGE_SIZE))
        self._per_page_box.currentIndexChanged.connect(
            self._on_per_page_changed)

        self._first_btn = QPushButton("首页", self)
        self._prev_btn = QPushButton("上一页", self)
        self._next_btn = QPushButton("下一页", self)
        self._last_btn = QPushButton("末页", self)
        self._first_btn.clicked.connect(lambda: self.goto_page(0))
        self._prev_btn.clicked.connect(lambda: self.goto_page(self._page - 1))
        self._next_btn.clicked.connect(lambda: self.goto_page(self._page + 1))
        self._last_btn.clicked.connect(
            lambda: self.goto_page(self.page_count() - 1))
        self._page_spin = QSpinBox(self)
        self._page_spin.setMinimum(1)
        self._page_spin.valueChanged.connect(
            lambda v: self.goto_page(v - 1))
        self._page_label = QLabel("共 0 页", self)

        pager = QHBoxLayout()
        pager.addWidget(QLabel("类型：", self))
        pager.addWidget(self._kind_box)
        pager.addWidget(self._per_page_box)
        pager.addStretch(1)
        pager.addWidget(self._first_btn)
        pager.addWidget(self._prev_btn)
        pager.addWidget(QLabel("第", self))
        pager.addWidget(self._page_spin)
        pager.addWidget(QLabel("页", self))
        pager.addWidget(self._page_label)
        pager.addWidget(self._next_btn)
        pager.addWidget(self._last_btn)

        self._list = QListWidget(self)
        self._list.setViewMode(QListWidget.IconMode)
        self._list.setIconSize(QSize(72, 72))
        self._list.setGridSize(QSize(96, 112))
        self._list.setResizeMode(QListWidget.Adjust)
        self._list.setMovement(QListWidget.Static)
        self._list.setSelectionMode(QListWidget.SingleSelection)
        self._list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list.itemClicked.connect(self._on_item_clicked)

        layout = QVBoxLayout(self)
        layout.addWidget(self._header)
        layout.addLayout(pager)
        layout.addWidget(self._list, 1)

    # ---------------------------------------------------------- 接口 ----
    def set_document(self, doc: PackDocument, kinds: list[EntryKind]) -> None:
        """切换当前包（保留已有过滤与每页设置，页码自动夹紧）。"""
        self._doc = doc
        self._kinds = list(kinds)
        self._icons.clear()
        self._rebuild_view()

    def refresh_header(self) -> None:
        doc = self._doc
        if doc is None:
            self._header.setText("未打开资源包（双击左侧文件名打开）")
            return
        name = doc.path.name if doc.path else "未命名"
        self._header.setText(
            f"{name} · 共 {doc.count} 条 · 容器 {doc.kind} · "
            f"已修改 {doc.dirty_count} 条 · 当前显示 {len(self._view)} 条")

    def refresh_entry(self, index: int) -> None:
        """条目被改动后刷新其所在单元格（图标失效待主窗口补图）。"""
        if self._doc is None:
            return
        if 0 <= index < len(self._kinds):
            self._kinds[index] = self._doc.entry_kind(index)
        self._icons.pop(index, None)
        self.refresh_header()
        for item in self._page_items():
            if item.data(_ROLE_INDEX) == index:
                item.setText(self._item_text(index))
                item.setIcon(_placeholder_icon(self._kinds[index]))
        self.page_changed.emit()

    def set_icons(self, icons: dict[int, QIcon]) -> None:
        """补入主窗口生成的真实缩略图。"""
        self._icons.update(icons)
        for item in self._page_items():
            icon = self._icons.get(item.data(_ROLE_INDEX))
            if icon is not None:
                item.setIcon(icon)

    def page_entries(self) -> list[int]:
        """当前页的条目序号列表（主窗口据此按需生成缩略图）。"""
        start = self._page * self._per_page
        return self._view[start:start + self._per_page]

    def page_count(self) -> int:
        if not self._view:
            return 0
        return (len(self._view) + self._per_page - 1) // self._per_page

    @property
    def current_page(self) -> int:
        return self._page

    @property
    def per_page(self) -> int:
        return self._per_page

    def set_per_page(self, size: int) -> None:
        index = self._per_page_box.findData(size)
        if index >= 0:
            self._per_page_box.setCurrentIndex(index)

    def select_entry(self, index: int) -> bool:
        """翻到条目所在页并选中它（不发信号，选中回调由主窗口决定）。"""
        if index not in self._view:
            return False
        pos = self._view.index(index)
        self.goto_page(pos // self._per_page)
        for item in self._page_items():
            if item.data(_ROLE_INDEX) == index:
                self._list.setCurrentItem(item)
                return True
        return False

    def goto_page(self, page: int) -> None:
        page = max(0, min(page, self.page_count() - 1)) if self._view else 0
        if page == self._page and self._list.count():
            self._sync_pager()
            return
        self._page = page
        self._fill_page()

    # ---------------------------------------------------------- 内部 ----
    def _rebuild_view(self) -> None:
        if self._doc is None:
            self._view = []
        elif self._kind_filter is None:
            self._view = list(range(self._doc.count))
        else:
            self._view = [i for i, k in enumerate(self._kinds)
                          if k is self._kind_filter]
        self._page = max(0, min(self._page, self.page_count() - 1)) \
            if self._view else 0
        self._fill_page()
        self.refresh_header()

    def _fill_page(self) -> None:
        self._list.clear()
        for index in self.page_entries():
            item = QListWidgetItem(self._item_text(index), self._list)
            item.setData(_ROLE_INDEX, index)
            item.setTextAlignment(Qt.AlignCenter)
            icon = self._icons.get(index)
            item.setIcon(icon if icon is not None
                         else _placeholder_icon(self._kinds[index]))
            item.setToolTip(
                f"#{index} {self._doc.label(index) if self._doc else ''} · "
                f"{KIND_LABELS.get(self._kinds[index], '')}")
        self._sync_pager()
        self.page_changed.emit()

    def _sync_pager(self) -> None:
        pages = self.page_count()
        self._page_label.setText(f"共 {pages} 页")
        self._page_spin.blockSignals(True)
        self._page_spin.setMaximum(max(1, pages))
        self._page_spin.setValue(self._page + 1 if pages else 1)
        self._page_spin.blockSignals(False)
        has = pages > 0
        self._first_btn.setEnabled(has and self._page > 0)
        self._prev_btn.setEnabled(has and self._page > 0)
        self._next_btn.setEnabled(has and self._page < pages - 1)
        self._last_btn.setEnabled(has and self._page < pages - 1)

    def _page_items(self) -> list[QListWidgetItem]:
        return [self._list.item(r) for r in range(self._list.count())]

    def _item_text(self, index: int) -> str:
        label = self._doc.label(index) if self._doc else str(index)
        if len(label) > 16:
            label = label[:15] + "…"
        return f"#{index}\n{label}"

    def _on_kind_changed(self, _i: int) -> None:
        self._kind_filter = self._kind_box.currentData()
        self._page = 0
        self._rebuild_view()

    def _on_per_page_changed(self, _i: int) -> None:
        first = self._view[self._page * self._per_page] \
            if self._view else 0
        self._per_page = int(self._per_page_box.currentData())
        if first in self._view:
            self._page = self._view.index(first) // self._per_page
        self._fill_page()

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        self.entry_selected.emit(int(item.data(_ROLE_INDEX)))
