"""Photoshop 式视口标尺：固定在上/左侧，随场景缩放与平移换算。"""

from __future__ import annotations

import math

from PySide6.QtCore import QEvent, QObject, QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

RULER_THICKNESS = 24
MIN_MAJOR_PIXELS = 72


def ruler_step(scale: float, min_pixels: int = MIN_MAJOR_PIXELS) -> float:
    """返回主刻度的场景间距（1/2/5 系列），屏幕上至少约 min_pixels。"""
    scale = max(abs(float(scale)), 1e-9)
    target = max(1, int(min_pixels)) / scale
    base = 10.0 ** math.floor(math.log10(target))
    for factor in (1.0, 2.0, 5.0, 10.0):
        step = base * factor
        if step >= target:
            return step
    return base * 10.0


def _label(value: float) -> str:
    rounded = round(value)
    return str(int(rounded)) if abs(value - rounded) < 1e-7 else f"{value:g}"


class RulerStrip(QWidget):
    """一条水平或垂直标尺；坐标每次绘制都从视图实时换算。"""

    def __init__(self, view, orientation: Qt.Orientation) -> None:
        super().__init__(view)
        self._view = view
        self._orientation = orientation
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        self.setMouseTracking(False)

    def _horizontal(self) -> bool:
        return self._orientation == Qt.Orientation.Horizontal

    def _length(self) -> int:
        return self.width() if self._horizontal() else self.height()

    def _scale(self) -> float:
        transform = self._view.transform()
        return abs(transform.m11() if self._horizontal() else transform.m22())

    def _scene_range(self) -> tuple[float, float]:
        length = max(0, self._length() - 1)
        if self._horizontal():
            first = self._view.mapToScene(QPoint(0, 0)).x()
            last = self._view.mapToScene(QPoint(length, 0)).x()
        else:
            first = self._view.mapToScene(QPoint(0, 0)).y()
            last = self._view.mapToScene(QPoint(0, length)).y()
        return min(first, last), max(first, last)

    def _screen_position(self, value: float) -> int:
        point = (QPointF(value, 0.0) if self._horizontal()
                 else QPointF(0.0, value))
        mapped = self._view.mapFromScene(point)
        return mapped.x() if self._horizontal() else mapped.y()

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt 命名)
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(39, 44, 54))
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        font = painter.font()
        font.setPixelSize(9)
        painter.setFont(font)
        length = self._length()
        if length <= 0:
            return
        major = ruler_step(self._scale())
        minor = major / 5.0
        first, last = self._scene_range()
        first_index = math.floor(first / major)
        last_index = math.ceil(last / major)
        # 正常缩放下每 72 个屏幕像素一个主刻度；上限只是异常变换护栏。
        last_index = min(last_index, first_index + 512)
        for index in range(first_index, last_index + 1):
            value = index * major
            for part in range(5):
                tick = value + part * minor
                position = self._screen_position(tick)
                if position < 0 or position >= length:
                    continue
                is_major = part == 0
                painter.setPen(QPen(QColor(171, 181, 198) if is_major
                                    else QColor(99, 108, 124), 1))
                tick_size = 11 if is_major else 5
                if self._horizontal():
                    painter.drawLine(position, length - tick_size,
                                     position, length - 1)
                else:
                    painter.drawLine(self.width() - tick_size, position,
                                     self.width() - 1, position)
                if not is_major:
                    continue
                painter.setPen(QColor(220, 226, 236))
                text = _label(tick)
                if self._horizontal():
                    painter.drawText(QRectF(position + 3, 1, 62, 12),
                                     Qt.AlignmentFlag.AlignLeft
                                     | Qt.AlignmentFlag.AlignVCenter, text)
                else:
                    painter.drawText(QRectF(1, position + 2,
                                            self.width() - 2, 12),
                                     Qt.AlignmentFlag.AlignCenter, text)
        painter.setPen(QPen(QColor(80, 88, 103), 1))
        if self._horizontal():
            painter.drawLine(0, self.height() - 1,
                             self.width(), self.height() - 1)
        else:
            painter.drawLine(self.width() - 1, 0,
                             self.width() - 1, self.height())


class RulerCorner(QWidget):
    """左上角原点格。"""

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(39, 44, 54))
        painter.setPen(QColor(135, 145, 162))
        font = painter.font()
        font.setPixelSize(8)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "px")
        painter.setPen(QPen(QColor(80, 88, 103), 1))
        painter.drawLine(self.width() - 1, 0,
                         self.width() - 1, self.height())
        painter.drawLine(0, self.height() - 1,
                         self.width(), self.height() - 1)


class RulerOverlay(QObject):
    """管理两条标尺与视口边距；关闭时不留下空白边。"""

    def __init__(self, view) -> None:
        super().__init__(view)
        self.view = view
        self.visible = False
        self.horizontal = RulerStrip(view, Qt.Orientation.Horizontal)
        self.vertical = RulerStrip(view, Qt.Orientation.Vertical)
        self.corner = RulerCorner(view)
        for widget in (self.horizontal, self.vertical, self.corner):
            widget.hide()
        view.viewport().installEventFilter(self)
        view.horizontalScrollBar().valueChanged.connect(
            lambda _value: self.update())
        view.verticalScrollBar().valueChanged.connect(
            lambda _value: self.update())
        view.scene().sceneRectChanged.connect(lambda _rect: self.update())

    def set_visible(self, visible: bool) -> None:
        visible = bool(visible)
        if visible == self.visible:
            return
        self.visible = visible
        margin = RULER_THICKNESS if visible else 0
        self.view.setViewportMargins(margin, margin, 0, 0)
        for widget in (self.horizontal, self.vertical, self.corner):
            widget.setVisible(visible)
        self.update_geometry()
        self.update()

    def update_geometry(self) -> None:
        if not self.visible:
            return
        rect = self.view.viewport().geometry()
        size = RULER_THICKNESS
        self.horizontal.setGeometry(rect.x(), 0, rect.width(), size)
        self.vertical.setGeometry(0, rect.y(), size, rect.height())
        self.corner.setGeometry(0, 0, size, size)
        for widget in (self.horizontal, self.vertical, self.corner):
            widget.raise_()
        self.update()

    def update(self) -> None:
        self.horizontal.update()
        self.vertical.update()
        self.corner.update()

    def eventFilter(self, watched, event) -> bool:  # noqa: N802
        try:
            viewport = self.view.viewport()
        except RuntimeError:
            return False  # 视图销毁中的尾随事件，不再碰已删除的 C++ 对象
        if (watched is viewport
                and event.type() in (QEvent.Type.Resize, QEvent.Type.Show)):
            self.update_geometry()
        return False
