"""右侧检查器：条目元数据、精灵信息、调色板网格与帧列表。"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QListWidget,
    QVBoxLayout,
    QWidget,
)

from ..core.codecs.detect import KIND_LABELS
from ..core.codecs.sprite import Sprite
from ..core.model.document import PackDocument


class PaletteGrid(QWidget):
    """16×16 调色板色块网格，点击色块发出其序号与颜色。"""

    color_picked = Signal(int, tuple)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._colors: list[QColor] = []
        self._picked = -1
        self.setFixedHeight(16 * 11 + 1)

    def set_colors(self, colors: list[tuple[int, int, int]]) -> None:
        self._colors = [QColor(r, g, b) for (r, g, b) in colors]
        self._picked = -1
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        cell = max(4, self.width() // 16)
        for i, color in enumerate(self._colors):
            x, y = (i % 16) * cell, (i // 16) * cell
            painter.fillRect(x, y, cell, cell, color)
            if i == self._picked:
                painter.setPen(QColor(235, 64, 52))
                painter.drawRect(x, y, cell - 1, cell - 1)
        if not self._colors:
            painter.drawText(self.rect(), Qt.AlignCenter, "无调色板")

    def mousePressEvent(self, event) -> None:  # noqa: N802
        cell = max(4, self.width() // 16)
        x = int(event.position().x()) // cell
        y = int(event.position().y()) // cell
        index = y * 16 + x
        if 0 <= index < len(self._colors):
            self._picked = index
            c = self._colors[index]
            self.color_picked.emit(index, (c.red(), c.green(), c.blue()))
            self.update()


class Inspector(QWidget):
    """条目检查器面板。"""

    frame_chosen = Signal(int)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._fields: dict[str, QLabel] = {}
        form = QFormLayout()
        for key in ("名称", "类型", "内容大小", "存储大小", "状态",
                    "精灵格式", "画布", "中心", "帧数", "色块"):
            label = QLabel("—", self)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self._fields[key] = label
            form.addRow(f"{key}：", label)

        self._palette = PaletteGrid(self)
        self._palette.color_picked.connect(self._on_color_picked)
        self._frames = QListWidget(self)
        self._frames.currentRowChanged.connect(self.frame_chosen.emit)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(QLabel("调色板（点击查看色值）：", self))
        layout.addWidget(self._palette)
        layout.addWidget(QLabel("帧列表：", self))
        layout.addWidget(self._frames, 1)

    # ---------------------------------------------------------- 接口 ----
    def clear(self) -> None:
        for label in self._fields.values():
            label.setText("—")
        self._palette.set_colors([])
        self._frames.clear()

    def set_entry(
        self,
        doc: PackDocument,
        index: int,
        sprite: Sprite | None,
    ) -> None:
        kind = doc.entry_kind(index)
        f = self._fields
        f["名称"].setText(doc.label(index))
        f["类型"].setText(KIND_LABELS[kind])
        f["内容大小"].setText(f"{len(doc.content(index))} 字节")
        f["存储大小"].setText(f"{len(doc.stored(index))} 字节")
        f["状态"].setText("已修改" if doc.is_dirty(index) else "未修改")
        self._frames.clear()
        if sprite is None:
            for key in ("精灵格式", "画布", "中心", "帧数"):
                f[key].setText("—")
            self._palette.set_colors([])
            f["色块"].setText("—")
            return
        pal_kind = "RGB888" if sprite.magic == "T0" else "RGB565"
        f["精灵格式"].setText(f"{sprite.magic}（{pal_kind}）")
        f["画布"].setText(f"{sprite.canvas_w} × {sprite.canvas_h}")
        f["中心"].setText(f"({sprite.center_x}, {sprite.center_y})")
        f["帧数"].setText(str(sprite.frame_count))
        self._palette.set_colors(sprite.palette)
        for fi, (kx, ky, fw, fh) in enumerate(sprite.frames):
            self._frames.addItem(f"帧 {fi}：{fw}×{fh}，key=({kx}, {ky})")

    def set_current_frame(self, index: int) -> None:
        self._frames.blockSignals(True)
        self._frames.setCurrentRow(index)
        self._frames.blockSignals(False)

    def _on_color_picked(self, index: int, rgb: tuple) -> None:
        r, g, b = rgb
        self._fields["色块"].setText(f"#{index} RGB({r}, {g}, {b})")
