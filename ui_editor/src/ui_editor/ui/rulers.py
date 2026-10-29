"""Photoshop 式视口标尺：固定在上/左侧，随场景缩放与平移换算。"""

from __future__ import annotations

import math

from PySide6.QtCore import QEvent, QObject, QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QMessageBox, QWidget

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
        self.setCursor(Qt.CursorShape.SizeVerCursor if self._horizontal()
                       else Qt.CursorShape.SizeHorCursor)
        self.setToolTip("向下拖出水平参考线" if self._horizontal()
                        else "向右拖出垂直参考线；拖回标尺可删除")

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

    def mousePressEvent(self, event) -> None:  # noqa: N802
        try:
            if (event.button() == Qt.MouseButton.LeftButton
                    and self._view.rulers.begin_ruler_drag(
                        self._orientation, event.globalPosition().toPoint())):
                event.accept()
                return
            super().mousePressEvent(event)
        except Exception as exc:
            self._view.rulers.report_drag_error(exc)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        try:
            if self._view.rulers.update_ruler_drag(
                    self._orientation, event.globalPosition().toPoint()):
                event.accept()
                return
            super().mouseMoveEvent(event)
        except Exception as exc:
            self._view.rulers.report_drag_error(exc)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        try:
            if (event.button() == Qt.MouseButton.LeftButton
                    and self._view.rulers.finish_ruler_drag(
                        self._orientation, event.globalPosition().toPoint())):
                event.accept()
                return
            super().mouseReleaseEvent(event)
        except Exception as exc:
            self._view.rulers.report_drag_error(exc)


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
        self._drag_orientation = None
        self._drag_index = None
        self._drag_source = None
        self._drag_document = None
        self._drag_offset = 0.0
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
        if not visible:
            self.cancel_drag()
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

    @staticmethod
    def _axis(orientation: Qt.Orientation) -> str:
        return "y" if orientation == Qt.Orientation.Horizontal else "x"

    def _reset_drag(self) -> None:
        self._drag_orientation = None
        self._drag_index = None
        self._drag_source = None
        self._drag_document = None
        self._drag_offset = 0.0

    def cancel_drag(self) -> None:
        self.view.scene().set_ruler_preview(None)
        self._reset_drag()

    def report_drag_error(self, exc: Exception) -> None:
        """Qt 回调边界的用户可见错误报告，并停止本次参考线拖动。"""
        self._reset_drag()
        QMessageBox.warning(self.view, "参考线操作失败", str(exc))

    def _begin_drag(self, orientation: Qt.Orientation, index: int | None,
                    global_pos: QPoint, source: str) -> bool:
        scene = self.view.scene()
        if scene.document is None:
            return False
        self.cancel_drag()
        self._drag_orientation = orientation
        self._drag_index = index
        self._drag_source = source
        self._drag_document = scene.document
        if index is not None:
            xs, ys = scene.manual_guides()
            values = (ys if orientation == Qt.Orientation.Horizontal else xs)
            if 0 <= index < len(values):
                value, _inside, _on_ruler = self._drag_position(global_pos)
                self._drag_offset = values[index] - value
        self._update_drag(global_pos)
        return True

    def begin_ruler_drag(self, orientation: Qt.Orientation,
                         global_pos: QPoint) -> bool:
        if not self.visible:
            return False
        return self._begin_drag(orientation, None, global_pos, "ruler")

    def update_ruler_drag(self, orientation: Qt.Orientation,
                          global_pos: QPoint) -> bool:
        if (self._drag_source != "ruler"
                or self._drag_orientation != orientation):
            return False
        self._update_drag(global_pos)
        return True

    def finish_ruler_drag(self, orientation: Qt.Orientation,
                          global_pos: QPoint) -> bool:
        if (self._drag_source != "ruler"
                or self._drag_orientation != orientation):
            return False
        self._finish_drag(global_pos)
        return True

    def _drag_position(self, global_pos: QPoint) -> tuple[float, bool, bool]:
        view_pos = self.view.mapFromGlobal(global_pos)
        viewport = self.view.viewport()
        viewport_pos = view_pos - viewport.geometry().topLeft()
        scene_pos = self.view.mapToScene(viewport_pos)
        horizontal = self._drag_orientation == Qt.Orientation.Horizontal
        value = scene_pos.y() if horizontal else scene_pos.x()
        inside = viewport.rect().contains(viewport_pos)
        ruler = self.horizontal if horizontal else self.vertical
        on_ruler = ruler.geometry().contains(view_pos)
        return float(value), inside, on_ruler

    def _update_drag(self, global_pos: QPoint) -> None:
        scene = self.view.scene()
        if self._drag_document is not scene.document:
            self.cancel_drag()
            return
        value, inside, _on_ruler = self._drag_position(global_pos)
        value += self._drag_offset
        if inside:
            scene.set_ruler_preview(
                self._axis(self._drag_orientation), value, self._drag_index)
        else:
            scene.set_ruler_preview(None)

    def _finish_drag(self, global_pos: QPoint) -> None:
        scene = self.view.scene()
        if self._drag_document is not scene.document:
            self.cancel_drag()
            return
        value, inside, on_ruler = self._drag_position(global_pos)
        value += self._drag_offset
        axis = self._axis(self._drag_orientation)
        index = self._drag_index
        xs, ys = scene.manual_guides()
        values = ys if axis == "y" else xs
        if inside:
            if index is None:
                if all(abs(existing - value) > 1e-6 for existing in values):
                    values.append(value)
            elif 0 <= index < len(values):
                values[index] = value
            scene.set_ruler_guides(xs, ys)
        elif on_ruler and index is not None and 0 <= index < len(values):
            values.pop(index)
            scene.set_ruler_guides(xs, ys)
        scene.set_ruler_preview(None)
        self._reset_drag()

    def _guide_at(self, viewport_pos: QPoint):
        scene = self.view.scene()
        scene_pos = self.view.mapToScene(viewport_pos)
        manual_x, manual_y = scene.manual_guides()
        candidates = []
        for index, gx in enumerate(manual_x):
            screen_x = self.view.mapFromScene(QPointF(gx, scene_pos.y())).x()
            distance = abs(screen_x - viewport_pos.x())
            if distance <= 6:
                candidates.append((distance, Qt.Orientation.Vertical, index))
        for index, gy in enumerate(manual_y):
            screen_y = self.view.mapFromScene(QPointF(scene_pos.x(), gy)).y()
            distance = abs(screen_y - viewport_pos.y())
            if distance <= 6:
                candidates.append((distance, Qt.Orientation.Horizontal, index))
        if not candidates:
            return None
        _distance, orientation, index = min(
            candidates, key=lambda candidate: candidate[0])
        return orientation, index

    def eventFilter(self, watched, event) -> bool:  # noqa: N802
        try:
            return self._event_filter(watched, event)
        except Exception as exc:
            handled = self._drag_orientation is not None
            self.report_drag_error(exc)
            return handled

    def _event_filter(self, watched, event) -> bool:
        try:
            viewport = self.view.viewport()
        except RuntimeError:
            return False  # 视图销毁中的尾随事件，不再碰已删除的 C++ 对象
        if watched is not viewport:
            return False
        event_type = event.type()
        if (event_type == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
                and self.visible
                and self._drag_orientation is None):
            viewport_pos = event.position().toPoint()
            hit = self._guide_at(viewport_pos)
            # 图元与移动／缩放手柄优先；只有空白处才抓取参考线。
            if hit is not None and self.view.itemAt(viewport_pos) is None:
                orientation, index = hit
                if self._begin_drag(orientation, index,
                                    event.globalPosition().toPoint(),
                                    "viewport"):
                    event.accept()
                    return True
        if self._drag_source == "viewport":
            if event_type == QEvent.Type.MouseMove:
                self._update_drag(event.globalPosition().toPoint())
                event.accept()
                return True
            if (event_type == QEvent.Type.MouseButtonRelease
                    and event.button() == Qt.MouseButton.LeftButton):
                self._finish_drag(event.globalPosition().toPoint())
                event.accept()
                return True
        if event_type == QEvent.Type.Hide:
            self.cancel_drag()
        if event_type in (QEvent.Type.Resize, QEvent.Type.Show):
            self.update_geometry()
        return False
