"""精灵预览画布：棋盘格透明背景、帧/画布两种显示模式、缩放。

* 帧模式：显示当前帧本身；
* 画布模式：显示当前帧按锚点合成到整张画布的结果，
  并标出画布中心（锚点）十字与当前帧边框。
"""
from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPen
from PySide6.QtWidgets import QWidget

MODE_FRAME = "frame"
MODE_CANVAS = "canvas"


class SpriteView(QWidget):
    """显示一组帧图的预览控件。"""

    frame_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._frames: list[QImage] = []
        self._canvas_frames: list[QImage] = []
        self._offsets: list[QPoint] = []
        self._center = QPoint(0, 0)
        self._frame = 0
        self._mode = MODE_CANVAS
        self._scale = 3.0
        self._fit = False
        self._show_anchor = True
        self.setMinimumSize(120, 120)

    # ---------------------------------------------------------- 内容 ----
    def set_content(
        self,
        frames: list[QImage],
        canvas_frames: list[QImage] | None = None,
        offsets: list[QPoint] | None = None,
        center: QPoint | None = None,
    ) -> None:
        """设置帧图（与可选的画布合成图）。"""
        self._frames = frames
        self._canvas_frames = canvas_frames or []
        self._offsets = offsets or []
        self._center = center or QPoint(0, 0)
        self._frame = 0
        self._refresh_size()

    def set_image(self, image: QImage) -> None:
        """显示单张静态图（PNG 预览复用本控件）。"""
        self.set_content([image])

    def clear(self) -> None:
        self.set_content([])

    # ---------------------------------------------------------- 状态 ----
    @property
    def frame_count(self) -> int:
        return len(self._frames)

    @property
    def current_frame(self) -> int:
        return self._frame

    def set_frame(self, index: int) -> None:
        if not self._frames:
            return
        index = max(0, min(index, len(self._frames) - 1))
        if index != self._frame:
            self._frame = index
            self.frame_changed.emit(index)
        self._refresh_size()

    def set_mode(self, mode: str) -> None:
        self._mode = mode
        self._refresh_size()

    def set_show_anchor(self, show: bool) -> None:
        self._show_anchor = show
        self.update()

    def set_scale(self, scale: float) -> None:
        self._fit = False
        self._scale = max(0.25, scale)
        self._refresh_size()

    def set_fit(self, viewport: QSize) -> None:
        """按视口大小自动缩放（不放大超过 8 倍）。"""
        self._fit = True
        img = self._current_image()
        if img is None or img.isNull():
            return
        sx = viewport.width() / max(1, img.width())
        sy = viewport.height() / max(1, img.height())
        self._scale = max(0.25, min(8.0, sx, sy))
        self._refresh_size()

    # ---------------------------------------------------------- 绘制 ----
    def _current_image(self) -> QImage | None:
        if self._mode == MODE_CANVAS and self._canvas_frames:
            if 0 <= self._frame < len(self._canvas_frames):
                return self._canvas_frames[self._frame]
            return None
        if 0 <= self._frame < len(self._frames):
            return self._frames[self._frame]
        return None

    def _refresh_size(self) -> None:
        img = self._current_image()
        if img is None:
            self.setFixedSize(240, 120)
        else:
            self.setFixedSize(
                max(1, round(img.width() * self._scale)),
                max(1, round(img.height() * self._scale)),
            )
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt 命名)
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(64, 64, 72))
        img = self._current_image()
        if img is None:
            painter.setPen(QColor(200, 200, 200))
            painter.drawText(self.rect(), Qt.AlignCenter, "未选择条目")
            return
        target = self.rect()
        self._paint_checkerboard(painter, target)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)
        painter.drawImage(target, img)
        painter.setPen(QPen(QColor(150, 150, 160), 1))
        painter.drawRect(target.adjusted(0, 0, -1, -1))
        if self._mode == MODE_CANVAS and self._show_anchor:
            self._paint_anchor(painter, target)

    def _paint_checkerboard(self, painter: QPainter, rect: QRect) -> None:
        cell = max(4, round(8 * self._scale))
        light, dark = QColor(176, 176, 176), QColor(128, 128, 128)
        painter.save()
        painter.setClipRect(rect)
        y = rect.top()
        row = 0
        while y < rect.bottom():
            x = rect.left()
            col = 0
            while x < rect.right():
                painter.fillRect(
                    x, y, cell, cell, light if (row + col) % 2 == 0 else dark)
                x += cell
                col += 1
            y += cell
            row += 1
        painter.restore()

    def _paint_anchor(self, painter: QPainter, rect: QRect) -> None:
        cx = rect.left() + round(self._center.x() * self._scale)
        cy = rect.top() + round(self._center.y() * self._scale)
        painter.setPen(QPen(QColor(235, 64, 52), 1))
        painter.drawLine(cx, rect.top(), cx, rect.bottom())
        painter.drawLine(rect.left(), cy, rect.right(), cy)
        if 0 <= self._frame < len(self._offsets) and self._frames:
            off = self._offsets[self._frame]
            img = self._frames[self._frame]
            frame_rect = QRect(
                rect.left() + round(off.x() * self._scale),
                rect.top() + round(off.y() * self._scale),
                round(img.width() * self._scale),
                round(img.height() * self._scale),
            )
            painter.setPen(QPen(QColor(52, 168, 235), 1))
            painter.drawRect(frame_rect.adjusted(0, 0, -1, -1))
