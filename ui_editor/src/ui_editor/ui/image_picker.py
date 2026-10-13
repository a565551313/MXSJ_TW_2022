"""从资源包选择媒体资源的对话框。

包内资源按引用路径列出（清单由 AssetResolver.media_candidates
从已命名布局扒取），支持子串搜索、缩略图懒加载（分批填充，
大包不卡死）、双击确认。选到的路径本来就在包里，布局保存
回资源包后游戏按路径哈希即可找到，不会丢图。对话框同时
保留"从外部文件…"入口，选外部图仍是旧行为（只填文件名，
图本身不进包）。
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

_ROLE_PATH = Qt.ItemDataRole.UserRole
_THUMB_BATCH = 24


def _basename(path: str) -> str:
    return path.replace("\\", "/").rstrip("/").split("/")[-1]


class ResourcePickerDialog(QDialog):
    """包内资源选择窗：搜索过滤 + 网格缩略图 + 单选确认。"""

    def __init__(self, parent, title: str, paths: list[str],
                 current: str = "",
                 thumb_provider: Callable[[str], object] | None = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(760, 540)
        self.external_requested = False
        self._thumb_provider = thumb_provider
        all_paths = list(paths)
        if current and current not in all_paths:
            all_paths.insert(0, current)  # 当前值不在清单也置顶可见
        self._all_paths = all_paths

        self._search = QLineEdit(self)
        self._search.setPlaceholderText("输入关键字过滤，如 底板800")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._refilter)
        self._count = QLabel(self)

        self._list = QListWidget(self)
        self._list.setViewMode(QListWidget.ViewMode.IconMode)
        self._list.setIconSize(QSize(72, 72))
        self._list.setGridSize(QSize(110, 118))
        self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._list.setMovement(QListWidget.Movement.Static)
        self._list.itemDoubleClicked.connect(lambda _i: self.accept())

        self._thumb_timer = QTimer(self)
        self._thumb_timer.setInterval(30)
        self._thumb_timer.timeout.connect(self._fill_thumbs)
        self._thumb_queue: list[QListWidgetItem] = []

        external_btn = QPushButton("从外部文件…", self)
        external_btn.setToolTip(
            "改走系统文件框（旧行为：只填文件名，图本身不进包）")
        external_btn.clicked.connect(self._choose_external)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        bottom = QHBoxLayout()
        bottom.addWidget(external_btn)
        bottom.addStretch(1)
        bottom.addWidget(buttons)

        layout = QVBoxLayout(self)
        layout.addWidget(self._search)
        layout.addWidget(self._count)
        layout.addWidget(self._list, 1)
        layout.addLayout(bottom)

        self._refilter()
        if current:
            for row in range(self._list.count()):
                item = self._list.item(row)
                if item.data(_ROLE_PATH) == current:
                    self._list.setCurrentItem(item)
                    break

    # ---------------------------------------------------------- 结果 ----
    def selected_path(self) -> str | None:
        item = self._list.currentItem()
        return str(item.data(_ROLE_PATH)) if item is not None else None

    def _choose_external(self) -> None:
        self.external_requested = True
        self.reject()

    # ---------------------------------------------------------- 内部 ----
    def _refilter(self) -> None:
        query = self._search.text().strip().lower()
        visible = [p for p in self._all_paths
                   if not query or query in p.lower()]
        self._thumb_timer.stop()
        self._list.clear()
        blank = QIcon(QPixmap(72, 72))
        for path in visible:
            item = QListWidgetItem(_basename(path), self._list)
            item.setData(_ROLE_PATH, path)
            item.setToolTip(path)
            item.setIcon(blank)
        self._count.setText(
            f"共 {len(visible)} 个资源（包内已有，选完保存回包不丢图）")
        self._thumb_queue = [self._list.item(r)
                             for r in range(self._list.count())]
        if self._thumb_provider is not None and self._thumb_queue:
            self._thumb_timer.start()

    def _fill_thumbs(self) -> None:
        """分批给当前列表补缩略图（精灵解码不便宜，避免一次卡死）。"""
        batch, self._thumb_queue = (self._thumb_queue[:_THUMB_BATCH],
                                    self._thumb_queue[_THUMB_BATCH:])
        for item in batch:
            path = str(item.data(_ROLE_PATH))
            try:
                image = self._thumb_provider(path)  # type: ignore[misc]
            except Exception:
                image = None
            if image is not None:
                pixmap = QPixmap.fromImage(image)  # type: ignore[arg-type]
                if not pixmap.isNull():
                    item.setIcon(QIcon(pixmap.scaled(
                        72, 72, Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation)))
        if not self._thumb_queue:
            self._thumb_timer.stop()
