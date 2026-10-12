"""替换图片对话框：选择新图与调色板策略。"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)

from ..core.codecs.sprite import Sprite


class ReplaceImagesDialog(QDialog):
    """为精灵条目选择替换图片。

    选 1 张图＝替换当前帧；选满与帧数相同的图片＝整精灵替换。
    """

    def __init__(self, parent, sprite: Sprite, current_frame: int):
        super().__init__(parent)
        self.setWindowTitle("替换图片")
        self._sprite = sprite
        self._current_frame = current_frame

        info = QLabel(
            f"精灵 {sprite.magic} · {sprite.frame_count} 帧 · "
            f"画布 {sprite.canvas_w}×{sprite.canvas_h}\n"
            f"选 1 张图替换当前帧 {current_frame}；"
            f"选满 {sprite.frame_count} 张按序替换全部帧。",
            self,
        )
        info.setWordWrap(True)

        self._list = QListWidget(self)
        add_btn = QPushButton("添加图片…", self)
        add_btn.clicked.connect(self._add_files)
        remove_btn = QPushButton("移除所选", self)
        remove_btn.clicked.connect(self._remove_selected)
        clear_btn = QPushButton("清空", self)
        clear_btn.clicked.connect(self._list.clear)
        btn_row = QHBoxLayout()
        btn_row.addWidget(add_btn)
        btn_row.addWidget(remove_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch(1)

        self._keep_palette = QRadioButton("沿用原调色板（原有颜色零误差）", self)
        self._keep_palette.setChecked(True)
        self._new_palette = QRadioButton("按新图重建调色板", self)
        group = QButtonGroup(self)
        group.addButton(self._keep_palette)
        group.addButton(self._new_palette)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(info)
        layout.addWidget(self._list, 1)
        layout.addLayout(btn_row)
        layout.addWidget(self._keep_palette)
        layout.addWidget(self._new_palette)
        layout.addWidget(buttons)

    # ---------------------------------------------------------- 接口 ----
    @property
    def file_paths(self) -> list[str]:
        return [self._list.item(i).text() for i in range(self._list.count())]

    @property
    def use_base_palette(self) -> bool:
        return self._keep_palette.isChecked()

    # ---------------------------------------------------------- 内部 ----
    def _add_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp);;所有文件 (*)")
        for path in paths:
            if not self.file_paths.count(path):
                self._list.addItem(path)

    def _remove_selected(self) -> None:
        for item in self._list.selectedItems():
            self._list.takeItem(self._list.row(item))

    def _validate_and_accept(self) -> None:
        count = len(self.file_paths)
        if count == 0:
            QMessageBox.warning(self, "替换图片", "请先添加图片文件。")
            return
        if count not in (1, self._sprite.frame_count):
            QMessageBox.warning(
                self, "替换图片",
                f"当前选了 {count} 张图：只能选 1 张（替换当前帧）"
                f"或 {self._sprite.frame_count} 张（整精灵替换）。")
            return
        self.accept()
