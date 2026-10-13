"""编辑画布：控件树映射为可选中/拖动/缩放的图元。

每个 :class:`~ui_editor.core.model.Widget` 对应一个
:class:`WidgetItem`，子控件作为子图元，坐标天然相对父级（与
.dlg 的相对坐标一致）。绘制委托给
:mod:`ui_editor.core.painters`。拖动改 ``iX/iY``，拖选中框的
把手改 ``iWidth/iHeight``，几何变更经回调同步属性面板。
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsSceneMouseEvent,
    QGraphicsView,
    QWidget,
)

from ..core import painters
from ..core.model import LayoutDocument, Widget
from ..core.painters import PaintContext

_HANDLE = 7.0  # 选中把手边长（图元本地坐标）
_HANDLES = ("nw", "n", "ne", "e", "se", "s", "sw", "w")


class WidgetItem(QGraphicsItem):
    """一个控件对应的画布图元。"""

    def __init__(self, widget: Widget, ctx: PaintContext,
                 on_geometry: Callable[[Widget], None]) -> None:
        super().__init__()
        self.widget = widget
        self.ctx = ctx
        self.on_geometry = on_geometry
        self._width, self._height = painters.effective_size(widget, ctx)
        self._syncing = False
        self._resize_handle: str | None = None
        self._resize_start: tuple[float, float, float, float, QPointF] \
            | None = None
        self.setPos(widget.x, widget.y)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.child_items: list[WidgetItem] = []
        for child in widget.children:
            item = WidgetItem(child, ctx, on_geometry)
            item.setParentItem(self)
            self.child_items.append(item)

    # -- 几何同步 ---------------------------------------------------
    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self._width, self._height)

    def refresh_geometry(self) -> None:
        """属性面板改动后把模型几何同步回图元。"""
        width, height = painters.effective_size(self.widget, self.ctx)
        if (width, height) != (self._width, self._height):
            self.prepareGeometryChange()
            self._width, self._height = width, height
        self._syncing = True
        self.setPos(self.widget.x, self.widget.y)
        self._syncing = False
        self.update()

    def itemChange(self, change, value):  # noqa: N802 (Qt 命名)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged \
                and not self._syncing:
            pos = self.pos()
            self.widget.set_geometry(x=int(round(pos.x())),
                                     y=int(round(pos.y())))
            self.on_geometry(self.widget)
        return super().itemChange(change, value)

    # -- 绘制 -------------------------------------------------------
    def paint(self, painter: QPainter, option, widget: QWidget = None) -> None:
        try:
            painters.paint_widget(painter, self.widget, self.ctx)
        except Exception:  # 单个控件绘制异常不拖垮画布
            painter.setPen(QPen(QColor(255, 90, 90), 1,
                                Qt.PenStyle.DashLine))
            painter.drawRect(self.boundingRect())
        if self.isSelected():
            rect = self.boundingRect()
            painter.setPen(QPen(QColor(80, 200, 255), 1,
                                Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)
            painter.setBrush(QColor(80, 200, 255))
            painter.setPen(Qt.PenStyle.NoPen)
            for cx, cy in self._handle_points():
                painter.drawRect(QRectF(cx - _HANDLE / 2, cy - _HANDLE / 2,
                                        _HANDLE, _HANDLE))

    def _handle_points(self) -> list[tuple[float, float]]:
        w, h = self._width, self._height
        return [(0, 0), (w / 2, 0), (w, 0), (w, h / 2),
                (w, h), (w / 2, h), (0, h), (0, h / 2)]

    def _handle_at(self, pos: QPointF) -> str | None:
        if not self.isSelected():
            return None
        tol = _HANDLE
        for name, (cx, cy) in zip(_HANDLES, self._handle_points(),
                                  strict=True):
            if abs(pos.x() - cx) <= tol and abs(pos.y() - cy) <= tol:
                return name
        return None

    # -- 缩放拖动 ---------------------------------------------------
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:  # noqa: N802
        handle = self._handle_at(event.pos())
        if handle is not None:
            self._resize_handle = handle
            self._resize_start = (
                float(self.widget.x), float(self.widget.y),
                float(self._width), float(self._height), event.scenePos())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:  # noqa: N802
        if self._resize_handle is None or self._resize_start is None:
            super().mouseMoveEvent(event)
            return
        x0, y0, w0, h0, start_scene = self._resize_start
        delta = event.scenePos() - start_scene
        dx, dy = delta.x(), delta.y()
        handle = self._resize_handle
        x, y, w, h = x0, y0, w0, h0
        if "e" in handle:
            w = w0 + dx
        if "s" in handle:
            h = h0 + dy
        if "w" in handle:
            x, w = x0 + dx, w0 - dx
        if "n" in handle:
            y, h = y0 + dy, h0 - dy
        if w < 8:
            if "w" in handle:
                x -= 8 - w
            w = 8
        if h < 8:
            if "n" in handle:
                y -= 8 - h
            h = 8
        self.widget.set_geometry(x=int(round(x)), y=int(round(y)),
                                 width=int(round(w)), height=int(round(h)))
        self.prepareGeometryChange()
        self._width, self._height = float(self.widget.width), float(self.widget.height)
        self._syncing = True
        self.setPos(self.widget.x, self.widget.y)
        self._syncing = False
        self.update()
        self.on_geometry(self.widget)
        event.accept()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:  # noqa: N802
        if self._resize_handle is not None:
            self._resize_handle = None
            self._resize_start = None
            event.accept()
            return
        super().mouseReleaseEvent(event)


class LayoutScene(QGraphicsScene):
    """承载一个布局文档全部图元的场景。"""

    def __init__(self, ctx: PaintContext,
                 on_geometry: Callable[[Widget], None]) -> None:
        super().__init__()
        self.ctx = ctx
        self.on_geometry = on_geometry
        self.document: LayoutDocument | None = None
        self._items: dict[int, WidgetItem] = {}

    def set_document(self, doc: LayoutDocument | None) -> None:
        self.clear()
        self._items = {}
        self.document = doc
        if doc is None:
            return
        for root in doc.roots:
            item = WidgetItem(root, self.ctx, self.on_geometry)
            self.addItem(item)
            self._register(item)
        if self.items():
            rect = self.itemsBoundingRect()
            self.setSceneRect(rect.adjusted(-40, -40, 40, 40))

    def _register(self, item: WidgetItem) -> None:
        self._items[id(item.widget)] = item
        for child in item.child_items:
            self._register(child)

    def item_for(self, widget: Widget) -> WidgetItem | None:
        return self._items.get(id(widget))

    def refresh_widget(self, widget: Widget) -> None:
        item = self.item_for(widget)
        if item is not None:
            item.refresh_geometry()
            item.update()

    def refresh_all(self) -> None:
        for item in self._items.values():
            item.refresh_geometry()
        if self.items():
            rect = self.itemsBoundingRect()
            self.setSceneRect(rect.adjusted(-40, -40, 40, 40))


class CanvasView(QGraphicsView):
    """带滚轮缩放的画布视图。"""

    def __init__(self, scene: LayoutScene) -> None:
        super().__init__(scene)
        self.setRenderHints(QPainter.RenderHint.Antialiasing
                            | QPainter.RenderHint.SmoothPixmapTransform)
        self.setBackgroundBrush(QColor(38, 40, 46))
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def wheelEvent(self, event) -> None:  # noqa: N802
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        current = self.transform().m11()
        if (factor > 1 and current > 8) or (factor < 1 and current < 0.08):
            return
        self.scale(factor, factor)

    def fit_content(self) -> None:
        rect = self.scene().itemsBoundingRect()
        if not rect.isEmpty():
            self.fitInView(rect.adjusted(-16, -16, 16, 16),
                           Qt.AspectRatioMode.KeepAspectRatio)

    def actual_size(self) -> None:
        self.resetTransform()

    def export_image(self) -> QImage:
        """把布局区域渲染为一张图片（导出 PNG 用）。"""
        scene = self.scene()
        rect = scene.itemsBoundingRect()
        if rect.isEmpty():
            rect = QRectF(0, 0, 640, 480)
        image = QImage(int(rect.width()), int(rect.height()),
                       QImage.Format.Format_ARGB32)
        image.fill(QColor(43, 48, 60))
        painter = QPainter(image)
        scene.render(painter, QRectF(0, 0, rect.width(), rect.height()), rect)
        painter.end()
        return image
