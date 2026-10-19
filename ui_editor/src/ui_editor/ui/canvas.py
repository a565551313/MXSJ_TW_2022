"""编辑画布：控件树映射为可选中/拖动/缩放的图元。

每个 :class:`~ui_editor.core.model.Widget` 对应一个
:class:`WidgetItem`，子控件作为子图元，坐标天然相对父级（与
.dlg 的相对坐标一致）。绘制委托给
:mod:`ui_editor.core.painters`。拖动改 ``iX/iY``，拖选中框的
把手改 ``iWidth/iHeight``，几何变更经回调同步属性面板。
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPen
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsSceneMouseEvent,
    QGraphicsView,
    QWidget,
)

from ..core import painters, snap
from ..core.model import LayoutDocument, Widget
from ..core.painters import PaintContext

_HANDLE = 7.0  # 选中把手边长（图元本地坐标）
_HANDLES = ("nw", "n", "ne", "e", "se", "s", "sw", "w")
_MIN_SIZE = 8.0  # 控件缩放下限（与自由缩放一致）


def aspect_resize(handle: str, x0: float, y0: float, w0: float, h0: float,
                  dx: float, dy: float) -> tuple[float, float, float, float]:
    """等比缩放：返回保持宽高比的新 (x, y, w, h)。

    角把手按拖动幅度相对更大的一轴定比例；边把手由拖动轴推另一轴，
    垂直/水平方向以中心为锚。被拖边的对边固定，最小 8px 仍保比例。
    """
    if w0 <= 0 or h0 <= 0:
        return x0, y0, w0, h0
    ratio = w0 / h0
    cand_w, cand_h = w0, h0
    if "e" in handle:
        cand_w = w0 + dx
    if "w" in handle:
        cand_w = w0 - dx
    if "s" in handle:
        cand_h = h0 + dy
    if "n" in handle:
        cand_h = h0 - dy
    if len(handle) == 2:  # 角：变化相对更大的一轴说了算
        if abs(cand_w - w0) / w0 >= abs(cand_h - h0) / h0:
            cand_h = cand_w / ratio
        else:
            cand_w = cand_h * ratio
    elif "e" in handle or "w" in handle:
        cand_h = cand_w / ratio
    else:
        cand_w = cand_h * ratio
    w, h = cand_w, cand_h
    if w < _MIN_SIZE:
        w, h = _MIN_SIZE, _MIN_SIZE / ratio
    if h < _MIN_SIZE:
        h, w = _MIN_SIZE, _MIN_SIZE * ratio
    if "w" in handle:
        x = x0 + w0 - w  # 右边固定
    elif handle in ("n", "s"):
        x = x0 + (w0 - w) / 2  # 水平居中
    else:
        x = x0
    if "n" in handle:
        y = y0 + h0 - h  # 底边固定
    elif handle in ("e", "w"):
        y = y0 + (h0 - h) / 2  # 垂直居中
    else:
        y = y0
    return x, y, w, h


class WidgetItem(QGraphicsItem):
    """一个控件对应的画布图元。"""

    def __init__(self, widget: Widget, ctx: PaintContext,
                 on_geometry: Callable[[Widget], None],
                 on_commit: Callable[[Widget], None] | None = None
                 ) -> None:
        super().__init__()
        self.widget = widget
        self.ctx = ctx
        self.on_geometry = on_geometry
        self.on_commit = on_commit  # 拖放/缩放送手时通知（撤销记步）
        self._press_geom: tuple[int, int, int, int] | None = None
        self._width, self._height = painters.effective_size(widget, ctx)
        self._syncing = False
        self._resize_handle: str | None = None
        self._resize_start: tuple[float, float, float, float, QPointF] \
            | None = None
        self.setPos(widget.x, widget.y)
        self.apply_lock()
        self.child_items: list[WidgetItem] = []
        for child in widget.children:
            item = WidgetItem(child, ctx, on_geometry, on_commit)
            item.setParentItem(self)
            self.child_items.append(item)

    def apply_lock(self) -> None:
        """按锁定状态刷新图元的交互能力并重绘。

        锁定 = 画布上**完全无视**这个控件：不可点击、不可选中、框选
        扫不到，鼠标按下直接穿透到下面的控件（不接收任何鼠标键）；
        仍照常绘制并按状态画右上角挂锁徽标。解锁回到控件树点锁图标。
        父控件锁定不影响子图元（子控件仍可单独操作）。
        """
        if self.widget.locked:
            if self.isSelected():
                self.setSelected(False)
            self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
            self.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            self.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges,
                False)
        else:
            self.setAcceptedMouseButtons(Qt.MouseButton.AllButtons)
            self.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            self.setFlag(
                QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges,
                True)
        self.update()

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
        if (change == QGraphicsItem.GraphicsItemChange.ItemPositionChange
                and not self._syncing):
            # 父子同时被选中拖动时，子控件靠父图元带着走；否则 Qt 会把
            # 父子各搬一次，子控件实际位移翻倍、局部坐标也被改错。
            if self._has_selected_ancestor():
                return self.pos()
            value = self._snapped_position(value)
            value = self._clamped_position(value)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged \
                and not self._syncing:
            pos = self.pos()
            self.widget.set_geometry(x=int(round(pos.x())),
                                     y=int(round(pos.y())))
            self.on_geometry(self.widget)
        return super().itemChange(change, value)

    # -- 拖动吸附 -----------------------------------------------------
    def _has_selected_ancestor(self) -> bool:
        """祖先里是否有被选中且能被拖动的（拖动时以最上层祖先为准）。"""
        item = self.parentItem()
        while item is not None:
            if (item.isSelected()
                    and item.flags()
                    & QGraphicsItem.GraphicsItemFlag.ItemIsMovable):
                return True
            item = item.parentItem()
        return False

    def _parent_box(self) -> tuple[float, float] | None:
        """父控件的有效尺寸（父图元按图片撑开时的真实像素）；未知返回 None。"""
        parent_item = self.parentItem()
        if parent_item is None:
            return None
        width = float(getattr(parent_item, "_width", 0.0))
        height = float(getattr(parent_item, "_height", 0.0))
        if width <= 0 or height <= 0:
            return None
        return width, height

    def _clamped_position(self, value):
        """拖动限制在父控件矩形内（父就是子的画布）。"""
        box = self._parent_box()
        if box is None:
            return value
        max_x = max(0.0, box[0] - self._width)
        max_y = max(0.0, box[1] - self._height)
        return QPointF(min(max(value.x(), 0.0), max_x),
                       min(max(value.y(), 0.0), max_y))

    def _snapped_position(self, value):
        """拖动中把坐标贴到同级控件/父边缘，返回修正后坐标（QPointF）。

        Alt 临时禁吸附；阈值按 6 屏幕像素折算到场景单位。命中的
        参考线同步给场景描红线（父坐标 → 场景坐标）。
        """
        from PySide6.QtWidgets import QApplication

        scene = self.scene()
        if scene is None:
            return value
        if QApplication.keyboardModifiers() & Qt.KeyboardModifier.AltModifier:
            scene.set_guides([], [])
            return value
        widget = self.widget
        parent = widget.parent
        if parent is not None:
            siblings = [c for c in parent.children
                        if c is not widget and not c.locked]
            parent_size = (float(parent.width), float(parent.height))
        else:
            doc = getattr(scene, "document", None)
            siblings = [r for r in (doc.roots if doc else [])
                        if r is not widget and not r.locked]
            parent_size = None
        others = [(float(c.x), float(c.y), float(c.width),
                   float(c.height)) for c in siblings]
        views = scene.views()
        scale = views[0].transform().m11() if views else 1.0
        threshold = max(6.0 / scale, 1.0) if scale > 0 else 6.0
        new_x, new_y, guides_x, guides_y = snap.snap_position(
            (float(value.x()), float(value.y()),
             float(widget.width), float(widget.height)),
            others, parent_size, threshold)
        parent_item = self.parentItem()
        if parent_item is not None:
            scene_x = [parent_item.mapToScene(
                QPointF(gx, 0)).x() for gx in guides_x]
            scene_y = [parent_item.mapToScene(
                QPointF(0, gy)).y() for gy in guides_y]
        else:
            scene_x, scene_y = guides_x, guides_y
        scene.set_guides(scene_x, scene_y)
        from PySide6.QtCore import QPointF as _PF
        return _PF(new_x, new_y)

    # -- 绘制 -------------------------------------------------------
    def paint(self, painter: QPainter, option, widget: QWidget = None) -> None:
        try:
            painters.paint_widget(painter, self.widget, self.ctx)
        except Exception:  # 单个控件绘制异常不拖垮画布
            painter.setPen(QPen(QColor(255, 90, 90), 1,
                                Qt.PenStyle.DashLine))
            painter.drawRect(self.boundingRect())
        if self.isSelected() and not self.widget.locked:
            rect = self.boundingRect()
            painter.setPen(QPen(QColor(80, 200, 255), 1,
                                Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)
            if not self.widget.locked:
                painter.setBrush(QColor(80, 200, 255))
                painter.setPen(Qt.PenStyle.NoPen)
                for cx, cy in self._handle_points():
                    painter.drawRect(QRectF(cx - _HANDLE / 2,
                                            cy - _HANDLE / 2,
                                            _HANDLE, _HANDLE))
        if self.widget.locked:
            self._paint_lock_badge(painter)

    def _paint_lock_badge(self, painter: QPainter) -> None:
        """右上角橙色小挂锁：未选中也看得见这件控件锁住了。"""
        painter.save()
        bx, by = self._width - 17.0, 3.0
        painter.setPen(QPen(QColor("#7a4d12"), 1.2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(QRectF(bx + 2.5, by, 8, 9), 0, 180 * 16)
        painter.setBrush(QColor("#f2b04a"))
        painter.drawRoundedRect(QRectF(bx, by + 5, 13, 9), 2, 2)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#7a4d12"))
        painter.drawEllipse(QRectF(bx + 5.2, by + 8.0, 2.6, 2.6))
        painter.restore()

    def _handle_points(self) -> list[tuple[float, float]]:
        w, h = self._width, self._height
        return [(0, 0), (w / 2, 0), (w, 0), (w, h / 2),
                (w, h), (w / 2, h), (0, h), (0, h / 2)]

    def _handle_at(self, pos: QPointF) -> str | None:
        if not self.isSelected() or self.widget.locked:
            return None
        tol = _HANDLE
        for name, (cx, cy) in zip(_HANDLES, self._handle_points(),
                                  strict=True):
            if abs(pos.x() - cx) <= tol and abs(pos.y() - cy) <= tol:
                return name
        return None

    # -- 缩放拖动 ---------------------------------------------------
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:  # noqa: N802
        self._press_geom = (self.widget.x, self.widget.y,
                            self.widget.width, self.widget.height)
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
        scene = self.scene()
        keep_aspect = bool(getattr(scene, "keep_aspect", False)) or bool(
            event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        if keep_aspect:
            x, y, w, h = aspect_resize(handle, x0, y0, w0, h0, dx, dy)
        else:
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
        box = self._parent_box()
        if box is not None:  # 缩放也限制在父矩形内
            x = min(max(x, 0.0), max(0.0, box[0] - 8.0))
            y = min(max(y, 0.0), max(0.0, box[1] - 8.0))
            w = min(w, max(8.0, box[0] - x))
            h = min(h, max(8.0, box[1] - y))
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

    def _commit_if_changed(self) -> None:
        """本次按压期间几何真变过才回调记一步。"""
        geom = (self.widget.x, self.widget.y,
                self.widget.width, self.widget.height)
        if (self.on_commit is not None and self._press_geom is not None
                and geom != self._press_geom):
            self.on_commit(self.widget)
        self._press_geom = None

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:  # noqa: N802
        if self._resize_handle is not None:
            self._resize_handle = None
            self._resize_start = None
            self._commit_if_changed()
            event.accept()
            return
        super().mouseReleaseEvent(event)
        self._commit_if_changed()
        scene = self.scene()
        if scene is not None:
            scene.set_guides([], [])


class LayoutScene(QGraphicsScene):
    """承载一个布局文档全部图元的场景。"""

    def __init__(self, ctx: PaintContext,
                 on_geometry: Callable[[Widget], None],
                 on_commit: Callable[[Widget], None] | None = None
                 ) -> None:
        super().__init__()
        self.ctx = ctx
        self.on_geometry = on_geometry
        self.on_commit = on_commit
        self.document: LayoutDocument | None = None
        self._items: dict[int, WidgetItem] = {}
        self.show_grid = False  # 网格+标尺（视图菜单/工具栏开关）
        self.keep_aspect = False  # 等比缩放（视图菜单/工具栏开关）
        self._guides_x: list[float] = []  # 场景坐标参考线（拖动吸附）
        self._guides_y: list[float] = []

    # -- 拖动参考线 ---------------------------------------------------
    def set_guides(self, xs, ys) -> None:
        if xs == self._guides_x and ys == self._guides_y:
            return
        self._guides_x = list(xs)
        self._guides_y = list(ys)
        self.update()

    # -- 网格/标尺/参考线绘制 ------------------------------------------
    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:  # noqa: N802
        super().drawBackground(painter, rect)
        if not self.show_grid:
            return
        left, top = int(rect.left()) // 10 * 10, int(rect.top()) // 10 * 10
        faint = QPen(QColor(255, 255, 255, 14), 0)
        strong = QPen(QColor(255, 255, 255, 30), 0)
        x = left
        while x <= rect.right():
            painter.setPen(strong if x % 50 == 0 else faint)
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
            x += 10
        y = top
        while y <= rect.bottom():
            painter.setPen(strong if y % 50 == 0 else faint)
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            y += 10

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:  # noqa: N802
        super().drawForeground(painter, rect)
        bounds = self.sceneRect()
        if self.show_grid:  # 简易标尺：沿场景左/上边界每 100 单位刻字
            painter.save()
            painter.setPen(QColor(200, 205, 215, 160))
            font = painter.font()
            font.setPixelSize(9)
            painter.setFont(font)
            x = int(bounds.left()) // 100 * 100
            while x <= bounds.right():
                painter.drawText(QPointF(x + 2, bounds.top() + 10), str(x))
                x += 100
            y = int(bounds.top()) // 100 * 100
            while y <= bounds.bottom():
                painter.drawText(QPointF(bounds.left() + 2, y + 10), str(y))
                y += 100
            painter.restore()
        if self._guides_x or self._guides_y:
            painter.save()
            pen = QPen(QColor(235, 60, 170), 0)
            painter.setPen(pen)
            for gx in self._guides_x:
                painter.drawLine(QPointF(gx, bounds.top()),
                                 QPointF(gx, bounds.bottom()))
            for gy in self._guides_y:
                painter.drawLine(QPointF(bounds.left(), gy),
                                 QPointF(bounds.right(), gy))
            painter.restore()

    def set_document(self, doc: LayoutDocument | None) -> None:
        self.clear()
        self._items = {}
        self.document = doc
        if doc is None:
            return
        for root in doc.roots:
            item = WidgetItem(root, self.ctx, self.on_geometry,
                            self.on_commit)
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

    zoom_changed = Signal(float)

    def __init__(self, scene: LayoutScene) -> None:
        super().__init__(scene)
        self.setRenderHints(QPainter.RenderHint.Antialiasing
                            | QPainter.RenderHint.SmoothPixmapTransform)
        self.setBackgroundBrush(QColor(38, 40, 46))
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        # 拖框擦到控件就选中；在控件上按下仍是拖动控件本身。
        self.setRubberBandSelectionMode(
            Qt.ItemSelectionMode.IntersectsItemShape)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        # 主窗口注入的右键菜单处理器：handler(global_pos, 命中的控件|None)
        self.context_menu_handler = None

    def contextMenuEvent(self, event) -> None:  # noqa: N802
        if self.context_menu_handler is None:
            super().contextMenuEvent(event)
            return
        self.context_menu_handler(event.globalPos(),
                                  self.widget_at(event.pos()))
        event.accept()

    def widget_at(self, pos) -> Widget | None:
        """视图坐标 pos 处的控件；锁定控件视而不见（穿透到下一层）。"""
        for item in self.items(pos):
            widget = getattr(item, "widget", None)
            if widget is not None and not widget.locked:
                return widget
        return None

    def wheelEvent(self, event) -> None:  # noqa: N802
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        current = self.transform().m11()
        if (factor > 1 and current > 8) or (factor < 1 and current < 0.08):
            return
        self.scale(factor, factor)
        self.zoom_changed.emit(self.transform().m11())

    # -- 空格拖动画布 / 中键平移 ---------------------------------------
    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            event.accept()
            return
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_start = (
                event.position().toPoint(),
                self.horizontalScrollBar().value(),
                self.verticalScrollBar().value())
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if getattr(self, "_pan_start", None) is not None:
            start, h0, v0 = self._pan_start
            delta = event.position().toPoint() - start
            self.horizontalScrollBar().setValue(h0 - delta.x())
            self.verticalScrollBar().setValue(v0 - delta.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if getattr(self, "_pan_start", None) is not None:
            self._pan_start = None
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def fit_content(self) -> None:
        rect = self.scene().itemsBoundingRect()
        if not rect.isEmpty():
            self.fitInView(rect.adjusted(-16, -16, 16, 16),
                           Qt.AspectRatioMode.KeepAspectRatio)
            self.zoom_changed.emit(self.transform().m11())

    def actual_size(self) -> None:
        self.resetTransform()
        self.zoom_changed.emit(self.transform().m11())

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
