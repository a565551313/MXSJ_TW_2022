"""Qt graphical studio workbench for the MXSJ map editor.

All Qt imports live exclusively inside this module so ``core`` and
``ui.viewmodel`` stay 100% headlessly testable without ``PySide6``.
"""
from __future__ import annotations

import io
from collections import OrderedDict
from pathlib import Path

from PIL import Image
from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import (
    QAction,
    QActionGroup,
    QColor,
    QFont,
    QFontDatabase,
    QImage,
    QKeySequence,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ..client.discovery import DiscoveryError
from ..core import MapDocument, MapFormatError, RgbImage, render_sector
from ..core.girb import LIGHT_CELL_PX, NEUTRAL_NIBBLE
from ..core.mapfile import CELL_PX, SECTOR_PX_H, SECTOR_PX_W
from .viewmodel import LAYERS, EditorViewModel, ExportBlockedError, MapRow

TILE_CACHE_MAX = 128
MASK_CACHE_MAX = 96

CELL_RGBA: dict[int, tuple[int, int, int, int]] = {
    0: (46, 204, 113, 66),   # walkable
    1: (231, 76, 60, 145),   # blocked
    2: (52, 198, 226, 128),  # shaded walkable (roof/canopy shadow)
    3: (155, 89, 182, 165),  # shaded blocked
}

CELL_NAMES: dict[int, str] = {
    0: "0 · 可行走 (平地)",
    1: "1 · 不可行走 (阻挡)",
    2: "2 · 阴影可行走 (树荫/屋檐)",
    3: "3 · 阴影阻挡 (墙体遮挡)",
}

TOOL_SPECS: list[tuple[str, str, str]] = [
    ("pan", "1 漫游检视", "1"),
    ("cell_brush", "2 行走画笔", "2"),
    ("cell_rect", "3 矩形填充", "3"),
    ("cell_line", "4 直线绘制", "4"),
    ("cell_fill", "5 油漆桶", "5"),
    ("light_brush", "6 光照画笔", "6"),
    ("path_sim", "7 A*寻路", "7"),
    ("mask_select", "8 遮罩拾取", "8"),
]

DARK_QSS = """
QMainWindow, QDialog {
    background-color: #161920;
    color: #e6eaf2;
}
QMenuBar {
    background-color: #1c2029;
    color: #e6eaf2;
    border-bottom: 1px solid #2b3140;
    padding: 2px 6px;
}
QMenuBar::item:selected, QMenu::item:selected {
    background-color: #2d5be3;
    color: #ffffff;
}
QMenu {
    background-color: #1f2430;
    color: #e6eaf2;
    border: 1px solid #32394a;
}
QToolBar {
    background-color: #1b1f28;
    border-bottom: 1px solid #2b3140;
    spacing: 4px;
    padding: 4px 6px;
}
QToolButton {
    background-color: #252b38;
    color: #dce2ee;
    border: 1px solid #323a4c;
    border-radius: 4px;
    padding: 4px 9px;
}
QToolButton:hover {
    background-color: #30384a;
    border-color: #4b6cb7;
}
QToolButton:checked {
    background-color: #2d5be3;
    color: #ffffff;
    border-color: #5b86ff;
    font-weight: bold;
}
QPushButton {
    background-color: #272e3d;
    color: #e6eaf2;
    border: 1px solid #384156;
    border-radius: 4px;
    padding: 5px 10px;
}
QPushButton:hover {
    background-color: #333d52;
    border-color: #5b86ff;
}
QPushButton:pressed {
    background-color: #2447b8;
}
QLineEdit, QComboBox, QSpinBox, QTextEdit {
    background-color: #12151c;
    color: #e6eaf2;
    border: 1px solid #31384a;
    border-radius: 4px;
    padding: 4px 6px;
}
QTableWidget {
    background-color: #13161e;
    alternate-background-color: #181c26;
    color: #e6eaf2;
    gridline-color: #252b39;
    border: 1px solid #2b3140;
    selection-background-color: #2d5be3;
    selection-color: #ffffff;
}
QHeaderView::section {
    background-color: #1f2430;
    color: #a9b4c9;
    border: none;
    border-right: 1px solid #2b3140;
    border-bottom: 1px solid #2b3140;
    padding: 5px 6px;
    font-weight: bold;
}
QTabWidget::pane {
    border: 1px solid #2b3140;
    background-color: #191d26;
}
QTabBar::tab {
    background-color: #1f2430;
    color: #9aa5ba;
    border: 1px solid #2b3140;
    padding: 6px 10px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background-color: #2d5be3;
    color: #ffffff;
    font-weight: bold;
}
QGroupBox {
    border: 1px solid #2c3344;
    border-radius: 5px;
    margin-top: 9px;
    padding-top: 8px;
    font-weight: bold;
    color: #9db8ff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 9px;
    padding: 0 4px;
}
QStatusBar {
    background-color: #191d26;
    color: #b8c2d6;
    border-top: 1px solid #2b3140;
}
QCheckBox {
    spacing: 5px;
    color: #e4eaf5;
}
QLabel {
    color: #d8e0ef;
}
QTableWidget::item {
    padding: 2px 4px;
}
"""


def _install_cjk_fonts(app: QApplication, extra_dir: Path | None = None) -> None:
    candidates: list[Path] = []
    here = Path(__file__).resolve()
    for anc in here.parents:
        fdir = anc / "Fonts"
        if fdir.is_dir():
            candidates.extend(sorted(fdir.glob("*.ttf")))
            break
    if extra_dir is not None:
        fdir = extra_dir / "Fonts"
        if fdir.is_dir():
            candidates.extend(sorted(fdir.glob("*.ttf")))
    loaded_families: list[str] = []
    for ttf in candidates:
        fid = QFontDatabase.addApplicationFont(str(ttf))
        if fid >= 0:
            loaded_families.extend(QFontDatabase.applicationFontFamilies(fid))

    preferred = [
        "Microsoft YaHei UI",
        "Microsoft YaHei",
        "FZLanTingYuan-DB-GBK",
        *loaded_families,
        "SimHei",
        "Noto Sans CJK SC",
        "DejaVu Sans",
    ]
    available = set(QFontDatabase.families())
    chosen = next((f for f in preferred if f in available), "")
    if chosen:
        font = QFont(chosen, 9)
        font.setFamilies([f for f in preferred if f in available])
        app.setFont(font)


def _rgb_to_qimage(img: RgbImage) -> QImage:
    ppm = f"P6\n{img.width} {img.height}\n255\n".encode("ascii") + img.data
    return QImage.fromData(ppm, "PPM")


def _pil_rgba_to_qimage(im: Image.Image) -> QImage:
    buf = io.BytesIO()
    im.convert("RGBA").save(buf, format="PNG", compress_level=1)
    return QImage.fromData(buf.getvalue(), "PNG")


class MapCanvas(QWidget):
    """Interactive world viewport supporting pan/zoom, live brush/rect/line/fill,
    GIRB dynamic light painting, foreground mask alpha cutouts & drag-move,
    NPC/portal telemetry markers, CAStar path visualization, and mini-map HUD."""

    cursorMoved = Signal(int, int)
    strokeCommitted = Signal(str)
    recordSelected = Signal(int)

    def __init__(
        self, vm: EditorViewModel, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.vm = vm
        self.setMouseTracking(True)
        self.setMinimumSize(560, 420)
        self.zoom = 1.0
        self.offset = QPointF(0.0, 0.0)
        self._tiles: OrderedDict[tuple[int, bool], QImage] = OrderedDict()
        self._mask_imgs: OrderedDict[int, QImage] = OrderedDict()
        self._minimap_img: QImage | None = None
        self._drag_pan_last: QPointF | None = None
        self._stroke_active = False
        self._stroke_cell_old: dict[tuple[int, int], int] = {}
        self._stroke_cell_val = 0
        self._stroke_light_old: dict[tuple[int, int], int] = {}
        self._stroke_light_val = NEUTRAL_NIBBLE
        self._shape_start_px: tuple[int, int] | None = None
        self._shape_cur_px: tuple[int, int] | None = None
        self._mask_drag_idx: int | None = None
        self._mask_drag_origin: tuple[int, int] = (0, 0)
        self._mask_drag_start_px: tuple[int, int] = (0, 0)
        self._path_toggle_goal = False

    def reset_view(self, *, fit: bool = True) -> None:
        self.invalidate_caches()
        self.offset = QPointF(0.0, 0.0)
        self.zoom = 1.0
        doc = self.vm.document
        if fit and doc is not None and self.width() > 64 and self.height() > 64:
            zx = (self.width() - 24) / max(1, doc.header.width)
            zy = (self.height() - 24) / max(1, doc.header.height)
            self.zoom = max(0.12, min(1.0, min(zx, zy)))
        self.update()

    def invalidate_caches(self, *, sector_index: int | None = None) -> None:
        if sector_index is None:
            self._tiles.clear()
            self._mask_imgs.clear()
            self._minimap_img = None
        else:
            self._tiles.pop((sector_index, False), None)
            self._tiles.pop((sector_index, True), None)
            self._minimap_img = None
        self.update()

    def center_on_world(self, wx: float, wy: float, zoom: float | None = None) -> None:
        if zoom is not None:
            self.zoom = max(0.08, min(8.0, zoom))
        self.offset = QPointF(
            wx - (self.width() * 0.5) / self.zoom,
            wy - (self.height() * 0.5) / self.zoom,
        )
        self.update()

    def _tile(self, doc: MapDocument, index: int, lit: bool) -> QImage:
        key = (index, lit)
        hit = self._tiles.get(key)
        if hit is not None:
            self._tiles.move_to_end(key)
            return hit
        rgb = render_sector(doc, doc.sector(index), apply_lighting=lit)
        img = _rgb_to_qimage(rgb)
        self._tiles[key] = img
        while len(self._tiles) > TILE_CACHE_MAX:
            self._tiles.popitem(last=False)
        return img

    def _mask_overlay(self, doc: MapDocument, ridx: int) -> QImage:
        hit = self._mask_imgs.get(ridx)
        if hit is not None:
            self._mask_imgs.move_to_end(ridx)
            return hit
        dm = doc.decode_record(ridx)
        w, h = dm.width, dm.height
        rgba = bytearray(w * h * 4)
        for py in range(h):
            for px in range(w):
                a = dm.alpha_2bit(px, py)
                if a:
                    off = (py * w + px) * 4
                    rgba[off] = 56
                    rgba[off + 1] = 224
                    rgba[off + 2] = 255
                    rgba[off + 3] = 52 + a * 36
        out = _pil_rgba_to_qimage(Image.frombytes("RGBA", (w, h), bytes(rgba)))
        self._mask_imgs[ridx] = out
        while len(self._mask_imgs) > MASK_CACHE_MAX:
            self._mask_imgs.popitem(last=False)
        return out

    def _ensure_minimap(self, doc: MapDocument) -> QImage:
        if self._minimap_img is not None:
            return self._minimap_img
        # Render the full map via Pillow downscale for instant crisp RGB32 preview.
        mw = 190
        h = doc.header
        mh = max(96, int(round(mw * h.height / max(1, h.width))))
        canvas = QImage(mw, mh, QImage.Format.Format_RGB32)
        canvas.fill(QColor(20, 24, 32))
        p = QPainter(canvas)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        sx = mw / max(1, h.width)
        sy = mh / max(1, h.height)
        for sec in doc.iter_sectors():
            tile = self._tile(doc, sec.index, False)
            p.drawImage(
                QRectF(
                    sec.origin_x * sx,
                    sec.origin_y * sy,
                    SECTOR_PX_W * sx + 0.8,
                    SECTOR_PX_H * sy + 0.8,
                ),
                tile,
            )
        p.end()
        self._minimap_img = canvas
        return canvas

    def _minimap_rect(self, doc: MapDocument) -> QRectF:
        mm = self._ensure_minimap(doc)
        return QRectF(
            self.width() - mm.width() - 14,
            self.height() - mm.height() - 14,
            mm.width(),
            mm.height(),
        )

    def _to_world(self, pos: QPointF) -> tuple[int, int]:
        return (
            int(pos.x() / self.zoom + self.offset.x()),
            int(pos.y() / self.zoom + self.offset.y()),
        )

    # -- painting ---------------------------------------------------------
    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.fillRect(self.rect(), QColor(17, 20, 27))
        doc = self.vm.document
        if doc is None:
            painter.setPen(QColor(150, 162, 184))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "《夢想世界》地图编辑器 Studio v1.0\n\n"
                "左侧双击任意地图打开，或使用“文件 → 选择客户端目录 / 新建编译地图”",
            )
            return

        h = doc.header
        vx0 = max(0.0, self.offset.x())
        vy0 = max(0.0, self.offset.y())
        vx1 = min(float(h.width), self.offset.x() + self.width() / self.zoom)
        vy1 = min(float(h.height), self.offset.y() + self.height() / self.zoom)

        painter.save()
        painter.scale(self.zoom, self.zoom)
        painter.translate(-self.offset)

        lit_on = self.vm.layer("lit_preview")
        if self.vm.layer("texture") and vx1 > vx0 and vy1 > vy0:
            c0 = int(vx0 // SECTOR_PX_W)
            r0 = int(vy0 // SECTOR_PX_H)
            c1 = min(int(vx1 // SECTOR_PX_W) + 1, h.sector_columns)
            r1 = min(int(vy1 // SECTOR_PX_H) + 1, h.sector_rows)
            for r in range(r0, r1):
                for c in range(c0, c1):
                    idx = r * h.sector_columns + c
                    painter.drawImage(
                        QPointF(c * SECTOR_PX_W, r * SECTOR_PX_H),
                        self._tile(doc, idx, lit_on),
                    )
        else:
            painter.fillRect(0, 0, h.width, h.height, QColor(28, 32, 42))

        # LLEC walkability layer (rendered per visible sector as crisp 16x12 RGBA)
        if self.vm.layer("walkability") and vx1 > vx0 and vy1 > vy0:
            c0 = int(vx0 // SECTOR_PX_W)
            r0 = int(vy0 // SECTOR_PX_H)
            c1 = min(int(vx1 // SECTOR_PX_W) + 1, h.sector_columns)
            r1 = min(int(vy1 // SECTOR_PX_H) + 1, h.sector_rows)
            for sr in range(r0, r1):
                for sc in range(c0, c1):
                    rgba_buf = bytearray(16 * 12 * 4)
                    for ly in range(12):
                        gy = sr * 12 + ly
                        if gy >= h.grid_rows:
                            continue
                        for lx in range(16):
                            gx = sc * 16 + lx
                            if gx >= h.grid_columns:
                                continue
                            v = doc.cell_at_index(gx, gy)
                            if v is not None:
                                off = (ly * 16 + lx) * 4
                                rgba_buf[off:off + 4] = bytes(
                                    CELL_RGBA.get(v, (241, 196, 15, 160))
                                )
                    overlay = _pil_rgba_to_qimage(
                        Image.frombytes("RGBA", (16, 12), bytes(rgba_buf))
                    )
                    painter.drawImage(
                        QRectF(
                            sc * SECTOR_PX_W,
                            sr * SECTOR_PX_H,
                            SECTOR_PX_W,
                            SECTOR_PX_H,
                        ),
                        overlay,
                    )

        # GIRB raw lightmap heatmap overlay (80x60 RGBA per visible sector)
        if self.vm.layer("collision") and vx1 > vx0 and vy1 > vy0:
            c0 = int(vx0 // SECTOR_PX_W)
            r0 = int(vy0 // SECTOR_PX_H)
            c1 = min(int(vx1 // SECTOR_PX_W) + 1, h.sector_columns)
            r1 = min(int(vy1 // SECTOR_PX_H) + 1, h.sector_rows)
            for sr in range(r0, r1):
                for sc in range(c0, c1):
                    nibs = doc.lightmap_nibbles(sr * h.sector_columns + sc)
                    if nibs is None:
                        continue
                    rgba_buf = bytearray(80 * 60 * 4)
                    for i, nib in enumerate(nibs):
                        if nib < NEUTRAL_NIBBLE:
                            a = min(200, (NEUTRAL_NIBBLE - nib) * 20)
                            rgba_buf[i * 4:i * 4 + 4] = bytes((15, 25, 65, a))
                        elif nib > NEUTRAL_NIBBLE:
                            a = min(200, (nib - NEUTRAL_NIBBLE) * 22)
                            rgba_buf[i * 4:i * 4 + 4] = bytes((255, 214, 102, a))
                    overlay = _pil_rgba_to_qimage(
                        Image.frombytes("RGBA", (80, 60), bytes(rgba_buf))
                    )
                    painter.drawImage(
                        QRectF(
                            sc * SECTOR_PX_W,
                            sr * SECTOR_PX_H,
                            SECTOR_PX_W,
                            SECTOR_PX_H,
                        ),
                        overlay,
                    )

        # Foreground mask 2-bit alpha silhouettes + bounding boxes
        sel_rec = self.vm.state.selected_record
        if (self.vm.layer("mask_cutout") or self.vm.layer("records")) and doc.records:
            for rec in doc.records:
                rx1, ry1 = rec.x + rec.width, rec.y + rec.height
                if rx1 < vx0 or rec.x > vx1 or ry1 < vy0 or rec.y > vy1:
                    continue
                if self.vm.layer("mask_cutout") and self.zoom >= 0.2:
                    painter.drawImage(
                        QPointF(rec.x, rec.y), self._mask_overlay(doc, rec.index)
                    )
                if self.vm.layer("records") or rec.index == sel_rec:
                    is_sel = rec.index == sel_rec
                    pen = QPen(
                        QColor(255, 208, 64, 245)
                        if is_sel
                        else QColor(72, 209, 255, 165)
                    )
                    pen.setWidthF((2.2 if is_sel else 1.0) / self.zoom)
                    painter.setPen(pen)
                    painter.drawRect(rec.x, rec.y, rec.width, rec.height)

        # 20x20 logical grid
        if self.vm.layer("grid") and self.zoom >= 0.45:
            pen = QPen(QColor(255, 255, 255, 42))
            pen.setWidthF(0.0)
            painter.setPen(pen)
            gx0 = int(vx0 // CELL_PX) * CELL_PX
            gy0 = int(vy0 // CELL_PX) * CELL_PX
            for x in range(gx0, int(vx1) + CELL_PX, CELL_PX):
                painter.drawLine(x, int(vy0), x, int(vy1))
            for y in range(gy0, int(vy1) + CELL_PX, CELL_PX):
                painter.drawLine(int(vx0), y, int(vx1), y)

        # 320x240 sector boundaries
        if self.vm.layer("sector_bounds"):
            pen = QPen(QColor(255, 196, 87, 130))
            pen.setWidthF(1.0 / self.zoom)
            painter.setPen(pen)
            for x in range(0, h.width + 1, SECTOR_PX_W):
                painter.drawLine(x, 0, x, h.height)
            for y in range(0, h.height + 1, SECTOR_PX_H):
                painter.drawLine(0, y, h.width, y)

        # CAStar simulated path
        path_res = self.vm.state.last_path
        if self.vm.layer("path") and path_res and path_res.cells:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            poly = QPainterPath()
            for idx_pt, (cx, cy) in enumerate(path_res.cells):
                px = cx * CELL_PX + CELL_PX * 0.5
                py = cy * CELL_PX + CELL_PX * 0.5
                if idx_pt == 0:
                    poly.moveTo(px, py)
                else:
                    poly.lineTo(px, py)
            glow = QPen(QColor(255, 230, 80, 110))
            glow.setWidthF(7.0 / self.zoom)
            painter.setPen(glow)
            painter.drawPath(poly)
            core_pen = QPen(QColor(255, 245, 130, 245))
            core_pen.setWidthF(2.6 / self.zoom)
            painter.setPen(core_pen)
            painter.drawPath(poly)
            sx0, sy0 = path_res.cells[0]
            gx0, gy0 = path_res.cells[-1]
            painter.setBrush(QColor(46, 204, 113))
            painter.drawEllipse(
                QPointF(sx0 * 20 + 10, sy0 * 20 + 10),
                7.0 / self.zoom,
                7.0 / self.zoom,
            )
            painter.setBrush(QColor(255, 94, 87))
            painter.drawEllipse(
                QPointF(gx0 * 20 + 10, gy0 * 20 + 10),
                7.0 / self.zoom,
                7.0 / self.zoom,
            )
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # Live shape rubber-band preview (rect / line)
        if self._shape_start_px and self._shape_cur_px:
            x0, y0 = self._shape_start_px
            x1, y1 = self._shape_cur_px
            pen = QPen(QColor(255, 235, 99, 235))
            pen.setWidthF(2.0 / self.zoom)
            painter.setPen(pen)
            painter.setBrush(QColor(255, 235, 99, 45))
            if self.vm.state.active_tool == "cell_rect":
                rx0 = min(x0 // 20, x1 // 20) * 20
                ry0 = min(y0 // 20, y1 // 20) * 20
                rw = (abs(x1 // 20 - x0 // 20) + 1) * 20
                rh = (abs(y1 // 20 - y0 // 20) + 1) * 20
                painter.drawRect(rx0, ry0, rw, rh)
            elif self.vm.state.active_tool == "cell_line":
                painter.drawLine(x0, y0, x1, y1)

        painter.restore()

        # Screen-space crisp labels for NPCs & Portals (always readable at any zoom!)
        if self.vm.layer("entities"):
            self._paint_entity_overlays(painter, vx0, vy0, vx1, vy1)

        # Top-left HUD badge + Bottom-right Eagle-eye Minimap
        self._paint_hud(painter, doc)

    def _paint_entity_overlays(
        self, painter: QPainter, vx0: float, vy0: float, vx1: float, vy1: float
    ) -> None:
        ents = self.vm.current_entities()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)

        # Arrival point
        arr = ents["arrival"]
        if arr is not None:
            sx = (arr["px"] - self.offset.x()) * self.zoom
            sy = (arr["py"] - self.offset.y()) * self.zoom
            painter.setPen(QPen(QColor(255, 255, 255), 1.5))
            painter.setBrush(QColor(52, 152, 219))
            painter.drawEllipse(QPointF(sx, sy), 6.0, 6.0)

        # Portals (diamond cyan beacons)
        for p in ents["portals"]:
            in_view = (
                vx0 - 60 <= p["px"] <= vx1 + 60
                and vy0 - 60 <= p["py"] <= vy1 + 60
            )
            if not in_view:
                continue
            sx = (p["px"] - self.offset.x()) * self.zoom
            sy = (p["py"] - self.offset.y()) * self.zoom
            diamond = QPolygonF(
                [
                    QPointF(sx, sy - 7),
                    QPointF(sx + 7, sy),
                    QPointF(sx, sy + 7),
                    QPointF(sx - 7, sy),
                ]
            )
            painter.setPen(QPen(QColor(15, 30, 45), 1.5))
            painter.setBrush(QColor(0, 229, 255, 230))
            painter.drawPolygon(diamond)
            if self.zoom >= 0.3:
                tag = f"传送 · {p['name']}"
                tw = painter.fontMetrics().horizontalAdvance(tag) + 10
                rect = QRectF(sx - tw / 2, sy - 25, tw, 16)
                painter.setPen(QPen(QColor(0, 210, 245, 160), 1.0))
                painter.setBrush(QColor(10, 32, 48, 215))
                painter.drawRoundedRect(rect, 3.0, 3.0)
                painter.setPen(QColor(132, 240, 255))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, tag)

        # NPCs (gold/emerald pins)
        for n in ents["npcs"]:
            in_view = (
                vx0 - 60 <= n["px"] <= vx1 + 60
                and vy0 - 60 <= n["py"] <= vy1 + 60
            )
            if not in_view:
                continue
            sx = (n["px"] - self.offset.x()) * self.zoom
            sy = (n["py"] - self.offset.y()) * self.zoom
            ok = n["walkable"]
            painter.setPen(QPen(QColor(20, 24, 30), 1.5))
            painter.setBrush(
                QColor(255, 199, 44, 235) if ok else QColor(255, 99, 72, 235)
            )
            painter.drawEllipse(QPointF(sx, sy), 5.0, 5.0)
            if self.zoom >= 0.35:
                tag = n["name"]
                tw = painter.fontMetrics().horizontalAdvance(tag) + 8
                rect = QRectF(sx - tw / 2, sy - 22, tw, 15)
                painter.setPen(QPen(QColor(90, 104, 132, 160), 1.0))
                painter.setBrush(QColor(20, 24, 34, 215))
                painter.drawRoundedRect(rect, 3.0, 3.0)
                painter.setPen(QColor(255, 232, 163) if ok else QColor(255, 160, 150))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, tag)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

    def _paint_hud(self, painter: QPainter, doc: MapDocument) -> None:
        s = self.vm.state
        tool_label = dict((k, lbl) for k, lbl, _ in TOOL_SPECS).get(
            s.active_tool, s.active_tool
        )
        hud_text = (
            f" {s.current_key} {s.current_name}"
            f"{' [已修改]' if self.vm.dirty else ''}  |  "
            f"{doc.header.width}×{doc.header.height} px  |  "
            f"缩放 {self.zoom * 100:.0f}%  |  工具: {tool_label} "
        )
        if s.last_path is not None:
            p = s.last_path
            path_msg = (
                f"可达 ({len(p.cells)} 步)" if p.found else "不可达"
            )
            hud_text += f" | 寻路: {path_msg} "
        fm = painter.fontMetrics()
        box = QRectF(10, 10, fm.horizontalAdvance(hud_text) + 16, 26)
        painter.setPen(QPen(QColor(78, 129, 255, 200), 1.0))
        painter.setBrush(QColor(15, 19, 28, 230))
        painter.drawRoundedRect(box, 4.0, 4.0)
        painter.setPen(QColor(235, 240, 250))
        painter.drawText(box, Qt.AlignmentFlag.AlignCenter, hud_text)

        # Mini-map navigator
        if self.width() >= 420 and self.height() >= 300:
            mm = self._ensure_minimap(doc)
            mrect = self._minimap_rect(doc)
            painter.setPen(QPen(QColor(92, 118, 178), 1.0))
            painter.setBrush(QColor(12, 15, 22, 235))
            painter.drawRect(mrect.adjusted(-2, -2, 2, 2))
            painter.drawImage(mrect, mm)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QColor(92, 118, 178))
            painter.drawRect(mrect)
            sx = mrect.width() / max(1, doc.header.width)
            sy = mrect.height() / max(1, doc.header.height)
            vp = QRectF(
                mrect.x() + max(0.0, self.offset.x()) * sx,
                mrect.y() + max(0.0, self.offset.y()) * sy,
                min(mrect.width(), (self.width() / self.zoom) * sx),
                min(mrect.height(), (self.height() / self.zoom) * sy),
            )
            painter.setPen(QPen(QColor(255, 212, 71), 1.8))
            painter.drawRect(vp)

    # -- mouse & wheel interaction ----------------------------------------
    def wheelEvent(self, event: QWheelEvent) -> None:
        factor = 1.18 if event.angleDelta().y() > 0 else 1 / 1.18
        new_zoom = max(0.08, min(8.0, self.zoom * factor))
        pos = event.position()
        world_before = pos / self.zoom + self.offset
        self.zoom = new_zoom
        self.offset = world_before - pos / self.zoom
        self.update()

    def mousePressEvent(self, event) -> None:
        doc = self.vm.document
        if doc is None:
            return
        pos = event.position()
        # Mini-map click jump
        if self.width() >= 420 and self.height() >= 300:
            mrect = self._minimap_rect(doc)
            if mrect.contains(pos):
                wx = (pos.x() - mrect.x()) / mrect.width() * doc.header.width
                wy = (pos.y() - mrect.y()) / mrect.height() * doc.header.height
                self.center_on_world(wx, wy)
                return

        if event.button() == Qt.MouseButton.MiddleButton or (
            event.button() == Qt.MouseButton.LeftButton
            and self.vm.state.active_tool == "pan"
        ):
            self._drag_pan_last = pos
            return

        wx, wy = self._to_world(pos)
        tool = self.vm.state.active_tool

        if tool == "cell_brush" and event.button() in (
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.RightButton,
        ):
            val = (
                0
                if event.button() == Qt.MouseButton.RightButton
                else self.vm.state.brush_cell_value
            )
            self._stroke_active = True
            self._stroke_cell_old = {}
            self._stroke_cell_val = val
            self._apply_live_cell_dab(wx, wy)
        elif tool in ("cell_rect", "cell_line") and (
            event.button() == Qt.MouseButton.LeftButton
        ):
            self._shape_start_px = (wx, wy)
            self._shape_cur_px = (wx, wy)
            self.update()
        elif tool == "cell_fill" and event.button() == Qt.MouseButton.LeftButton:
            n = self.vm.flood_fill_cells_at(wx, wy)
            self.strokeCommitted.emit(f"区域油漆桶填充 {n} 格")
            self.update()
        elif tool == "light_brush" and event.button() in (
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.RightButton,
        ):
            nib = (
                NEUTRAL_NIBBLE
                if event.button() == Qt.MouseButton.RightButton
                else self.vm.state.light_value
            )
            self._stroke_active = True
            self._stroke_light_old = {}
            self._stroke_light_val = nib
            self._apply_live_light_dab(wx, wy)
        elif tool == "path_sim":
            if event.button() == Qt.MouseButton.RightButton or self._path_toggle_goal:
                start = self.vm.state.path_start or (wx, wy)
                res = self.vm.simulate_path(start, (wx, wy))
                self._path_toggle_goal = False
                self.strokeCommitted.emit(
                    f"A* 寻路: {'可达' if res.found else '不可达'} "
                    f"({len(res.cells)} 步, 探索 {res.explored} 节点)"
                )
            else:
                self.vm.state.path_start = (wx, wy)
                self._path_toggle_goal = True
                if self.vm.state.path_goal is not None:
                    self.vm.simulate_path((wx, wy), self.vm.state.path_goal)
                self.strokeCommitted.emit(f"已设寻路起点 ({wx}, {wy})，再次点击设终点")
            self.update()
        elif tool == "mask_select" and event.button() == Qt.MouseButton.LeftButton:
            hits = doc.records_at(wx, wy)
            if hits:
                chosen = hits[-1]
                self.vm.state.selected_record = chosen.index
                self._mask_drag_idx = chosen.index
                self._mask_drag_origin = (chosen.x, chosen.y)
                self._mask_drag_start_px = (wx, wy)
                self.recordSelected.emit(chosen.index)
                self.update()

    def mouseMoveEvent(self, event) -> None:
        pos = event.position()
        if self._drag_pan_last is not None:
            delta = pos - self._drag_pan_last
            self._drag_pan_last = pos
            self.offset -= delta / self.zoom
            self.update()
            return
        if self.vm.document is None:
            return
        wx, wy = self._to_world(pos)
        if self._stroke_active and self.vm.state.active_tool == "cell_brush":
            self._apply_live_cell_dab(wx, wy)
        elif self._stroke_active and self.vm.state.active_tool == "light_brush":
            self._apply_live_light_dab(wx, wy)
        elif self._shape_start_px is not None:
            self._shape_cur_px = (wx, wy)
            self.update()
        self.cursorMoved.emit(wx, wy)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pan_last = None
        if self._stroke_active and self.vm.state.active_tool == "cell_brush":
            self._stroke_active = False
            n = self.vm.record_cell_changes(
                self._stroke_cell_old,
                self._stroke_cell_val,
                f"行走画笔 ({len(self._stroke_cell_old)} 格)",
            )
            self._stroke_cell_old = {}
            if n:
                self._refresh_active_path()
                self.strokeCommitted.emit(f"已绘制 {n} 个行走格")
        elif self._stroke_active and self.vm.state.active_tool == "light_brush":
            self._stroke_active = False
            n = self.vm.record_light_changes(
                self._stroke_light_old,
                self._stroke_light_val,
                f"光照画笔 ({len(self._stroke_light_old)} 采样)",
            )
            self._stroke_light_old = {}
            if n:
                self.strokeCommitted.emit(f"已绘制 {n} 个 4x4 动态光照采样")
        elif self._shape_start_px is not None and self._shape_cur_px is not None:
            x0, y0 = self._shape_start_px
            x1, y1 = self._shape_cur_px
            self._shape_start_px = None
            self._shape_cur_px = None
            if self.vm.state.active_tool == "cell_rect":
                n = self.vm.paint_cell_rect(x0, y0, x1, y1)
                self._refresh_active_path()
                self.strokeCommitted.emit(f"矩形填充 {n} 格")
            elif self.vm.state.active_tool == "cell_line":
                n = self.vm.paint_cell_line(x0, y0, x1, y1)
                self._refresh_active_path()
                self.strokeCommitted.emit(f"直线绘制 {n} 格")
            self.update()
        elif self._mask_drag_idx is not None:
            idx = self._mask_drag_idx
            ox, oy = self._mask_drag_origin
            sx0, sy0 = self._mask_drag_start_px
            wx, wy = self._to_world(event.position())
            self._mask_drag_idx = None
            dx, dy = wx - sx0, wy - sy0
            if dx != 0 or dy != 0:
                self.vm.move_mask_record(idx, ox + dx, oy + dy)
                self.recordSelected.emit(idx)
                self.strokeCommitted.emit(
                    f"已移动前景遮罩 #{idx} 至 ({ox + dx}, {oy + dy})"
                )
                self.update()

    def _apply_live_cell_dab(self, wx: int, wy: int) -> None:
        doc = self.vm.document
        if doc is None:
            return
        changed = doc.paint_cells_brush(
            wx // CELL_PX,
            wy // CELL_PX,
            self._stroke_cell_val,
            self.vm.state.brush_radius,
        )
        for coord, old in changed.items():
            self._stroke_cell_old.setdefault(coord, old)
        if changed:
            self.update()

    def _apply_live_light_dab(self, wx: int, wy: int) -> None:
        doc = self.vm.document
        if doc is None:
            return
        changed = doc.paint_lightmap_brush(
            wx // LIGHT_CELL_PX,
            wy // LIGHT_CELL_PX,
            self._stroke_light_val,
            self.vm.state.light_radius,
        )
        touched_sectors: set[int] = set()
        for (lx, ly), old in changed.items():
            self._stroke_light_old.setdefault((lx, ly), old)
            sc, sr = lx // 80, ly // 60
            touched_sectors.add(sr * doc.header.sector_columns + sc)
        for sidx in touched_sectors:
            self.invalidate_caches(sector_index=sidx)

    def _refresh_active_path(self) -> None:
        if self.vm.state.path_start and self.vm.state.path_goal:
            self.vm.simulate_path(self.vm.state.path_start, self.vm.state.path_goal)


class NewMapDialog(QDialog):
    """Dialog for creating a blank ``.map`` or compiling one from a PNG/JPEG image."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("新建 / 从美术底图编译 .map")
        self.resize(460, 240)
        layout = QFormLayout(self)

        self.img_edit = QLineEdit()
        self.img_edit.setPlaceholderText(
            "可选：选择整张 PNG/JPG 地图美术图自动切片编译…"
        )
        browse_img = QPushButton("选择底图…")
        browse_img.clicked.connect(self._pick_image)
        img_row = QHBoxLayout()
        img_row.addWidget(self.img_edit, 1)
        img_row.addWidget(browse_img)
        layout.addRow("美术底图:", img_row)

        self.w_spin = QSpinBox()
        self.w_spin.setRange(320, 16000)
        self.w_spin.setSingleStep(320)
        self.w_spin.setValue(960)
        self.h_spin = QSpinBox()
        self.h_spin.setRange(240, 16000)
        self.h_spin.setSingleStep(240)
        self.h_spin.setValue(720)
        layout.addRow("地图宽度 (px):", self.w_spin)
        layout.addRow("地图高度 (px):", self.h_spin)

        self.dest_edit = QLineEdit()
        self.dest_edit.setPlaceholderText("输出 .map 路径，例如 out/9001.map")
        browse_out = QPushButton("保存位置…")
        browse_out.clicked.connect(self._pick_dest)
        out_row = QHBoxLayout()
        out_row.addWidget(self.dest_edit, 1)
        out_row.addWidget(browse_out)
        layout.addRow("输出 .map:", out_row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _pick_image(self) -> None:
        p, _ = QFileDialog.getOpenFileName(
            self, "选择地图底图", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if p:
            self.img_edit.setText(p)
            with Image.open(p) as im:
                self.w_spin.setValue(im.width)
                self.h_spin.setValue(im.height)

    def _pick_dest(self) -> None:
        p, _ = QFileDialog.getSaveFileName(
            self, "新地图保存位置", "new_scene.map", "MXSJ Map (*.map)"
        )
        if p:
            self.dest_edit.setText(p)


class EditorWindow(QMainWindow):
    """Full studio workbench window for inspecting, editing, compiling, and
    verifying ``MXSJ`` ``0.1M`` maps."""

    def __init__(self, vm: EditorViewModel) -> None:
        super().__init__()
        self.vm = vm
        self.setWindowTitle("《夢想世界》地图编辑器 Studio v1.0 — MXSJ TW v2.27.2")
        win_dims = list(self.vm.config.window)
        w = win_dims[0] if len(win_dims) >= 2 else 1420
        h = win_dims[1] if len(win_dims) >= 2 else 880
        self.resize(max(w, 1380), max(h, 860))

        self._filtered_rows: list[MapRow] = []
        self._tool_actions: dict[str, QAction] = {}
        self._layer_checks: dict[str, QCheckBox] = {}
        self._entity_jump_targets: list[tuple[int, int]] = []

        self.canvas = MapCanvas(self.vm)
        self.canvas.cursorMoved.connect(self._on_cursor_moved)
        self.canvas.strokeCommitted.connect(self._on_stroke_committed)
        self.canvas.recordSelected.connect(self._select_record_row)

        self._build_ui()
        self._build_menus_and_toolbar()

        status = QStatusBar()
        self.setStatusBar(status)
        self._refresh_status()

        if self.vm.config.client_root:
            QTimer.singleShot(0, lambda: self._open_root(self.vm.config.client_root))

    # -- UI layout --------------------------------------------------------
    def _build_ui(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Left panel: Map browser + search filter
        left = QWidget()
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(6, 6, 4, 6)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索编号 / 场景名 / 現行 / 遮罩…")
        self.search_edit.textChanged.connect(self._populate_map_table)
        left_lay.addWidget(self.search_edit)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["编号", "场景名称", "尺寸", "扇区", "遮罩"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.itemSelectionChanged.connect(self._on_row_selected)
        left_lay.addWidget(self.table, 1)

        # 2. Right panel: Multi-tab Inspector / Palette / Masks / Entities / Audit
        right = QTabWidget()
        right.setMinimumWidth(330)
        right.addTab(self._build_layers_palette_tab(), "图层与画笔")
        right.addTab(self._build_masks_tab(), "前景遮罩")
        right.addTab(self._build_entities_tab(), "NPC与寻路")
        right.addTab(self._build_audit_tab(), "审计与扇区")
        self.right_tabs = right

        splitter.addWidget(left)
        splitter.addWidget(self.canvas)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([415, 725, 360])
        self.setCentralWidget(splitter)

    def _build_layers_palette_tab(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(6, 5, 6, 6)
        lay.setSpacing(5)

        layer_box = QGroupBox("视图叠加层 (快捷键实时开关)")
        lb_lay = QVBoxLayout(layer_box)
        lb_lay.setContentsMargins(7, 6, 7, 5)
        lb_lay.setSpacing(3)
        layer_labels = [
            ("texture", "底图纹理 (GEPJ 320×240)"),
            ("lit_preview", "GIRB 动态光照实时合成"),
            ("walkability", "LLEC 通行与阴影网格 (绿/红/青/紫)"),
            ("mask_cutout", "前景遮罩 2-bit Alpha 剪影"),
            ("records", "前景遮罩包围盒线框"),
            ("entities", "场景 NPC / 传送阵 / 出生点标注"),
            ("path", "CAStar 8方向寻路轨迹"),
            ("grid", "20×20 px 逻辑格线"),
            ("sector_bounds", "320×240 px 扇区分界线"),
            ("collision", "GIRB 原始亮度偏差热力层"),
        ]
        for key, text in layer_labels:
            chk = QCheckBox(text)
            chk.setChecked(self.vm.layer(key))
            chk.toggled.connect(lambda on, n=key: self._toggle_layer(n, on))
            lb_lay.addWidget(chk)
            self._layer_checks[key] = chk
        lay.addWidget(layer_box)

        cell_box = QGroupBox("LLEC 通行格编辑画笔 (右键擦除为可行走)")
        cb_form = QFormLayout(cell_box)
        self.cell_combo = QComboBox()
        for val, label in CELL_NAMES.items():
            self.cell_combo.addItem(label, val)
        self.cell_combo.setCurrentIndex(1)
        self.cell_combo.currentIndexChanged.connect(
            lambda _: setattr(
                self.vm.state, "brush_cell_value", int(self.cell_combo.currentData())
            )
        )
        cb_form.addRow("格类型:", self.cell_combo)

        self.cell_rad_slider = QSlider(Qt.Orientation.Horizontal)
        self.cell_rad_slider.setRange(0, 6)
        self.cell_rad_slider.setValue(self.vm.state.brush_radius)
        self.cell_rad_lbl = QLabel("1×1 格")
        self.cell_rad_slider.valueChanged.connect(self._on_cell_radius_changed)
        rad_row = QHBoxLayout()
        rad_row.addWidget(self.cell_rad_slider, 1)
        rad_row.addWidget(self.cell_rad_lbl)
        cb_form.addRow("画笔半径:", rad_row)
        lay.addWidget(cell_box)

        light_box = QGroupBox("GIRB 动态角色/地面光照画笔 (0暗 ~ 8标准 ~ 15亮)")
        lt_form = QFormLayout(light_box)
        self.light_slider = QSlider(Qt.Orientation.Horizontal)
        self.light_slider.setRange(0, 15)
        self.light_slider.setValue(self.vm.state.light_value)
        self.light_lbl = QLabel(f"亮度 {self.vm.state.light_value} / 15")
        self.light_slider.valueChanged.connect(self._on_light_val_changed)
        lv_row = QHBoxLayout()
        lv_row.addWidget(self.light_slider, 1)
        lv_row.addWidget(self.light_lbl)
        lt_form.addRow("目标亮度:", lv_row)

        self.light_rad_slider = QSlider(Qt.Orientation.Horizontal)
        self.light_rad_slider.setRange(1, 12)
        self.light_rad_slider.setValue(self.vm.state.light_radius)
        self.light_rad_slider.valueChanged.connect(
            lambda v: setattr(self.vm.state, "light_radius", int(v))
        )
        lt_form.addRow("光斑半径:", self.light_rad_slider)

        reset_light_btn = QPushButton("重置光标所在扇区光照为标准值 (8)")
        reset_light_btn.clicked.connect(self._reset_cursor_sector_light)
        lt_form.addRow(reset_light_btn)
        lay.addWidget(light_box)

        # Live cursor telemetry box
        tele_box = QGroupBox("实时坐标与格属性检视")
        t_lay = QVBoxLayout(tele_box)
        self.telemetry_lbl = QLabel("移动鼠标至地图画布查看像素 / 服务端坐标 / 光照…")
        self.telemetry_lbl.setMinimumHeight(105)
        self.telemetry_lbl.setWordWrap(True)
        t_lay.addWidget(self.telemetry_lbl)
        lay.addWidget(tele_box)
        lay.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea, QWidget { background-color: #191d26; }")
        scroll.setWidget(page)
        return scroll

    def _build_masks_tab(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(8, 8, 8, 8)

        self.mask_table = QTableWidget(0, 4)
        self.mask_table.setHorizontalHeaderLabels(["#", "位置 (X,Y)", "尺寸", "字节"])
        self.mask_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.mask_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.mask_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.mask_table.verticalHeader().setVisible(False)
        mhdr = self.mask_table.horizontalHeader()
        mhdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        mhdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        mhdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        mhdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.mask_table.itemSelectionChanged.connect(self._on_mask_row_chosen)
        lay.addWidget(self.mask_table, 1)

        preview_box = QGroupBox("选中遮罩 RGBA 镂空预览 (LZO1X 2-bit Alpha)")
        p_lay = QVBoxLayout(preview_box)
        self.mask_preview_lbl = QLabel("未选择遮罩记录")
        self.mask_preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mask_preview_lbl.setMinimumHeight(145)
        self.mask_preview_lbl.setFrameStyle(QFrame.Shape.StyledPanel)
        p_lay.addWidget(self.mask_preview_lbl)
        lay.addWidget(preview_box)

        btn_row1 = QHBoxLayout()
        add_btn = QPushButton("导入 PNG 新增遮罩…")
        add_btn.clicked.connect(self._add_mask_dialog)
        move_btn = QPushButton("修改遮罩坐标…")
        move_btn.clicked.connect(self._move_mask_dialog)
        btn_row1.addWidget(add_btn)
        btn_row1.addWidget(move_btn)
        lay.addLayout(btn_row1)

        btn_row2 = QHBoxLayout()
        exp_btn = QPushButton("导出选中遮罩 PNG…")
        exp_btn.clicked.connect(self._export_selected_mask)
        del_btn = QPushButton("删除选中遮罩")
        del_btn.clicked.connect(self._delete_selected_mask)
        btn_row2.addWidget(exp_btn)
        btn_row2.addWidget(del_btn)
        lay.addLayout(btn_row2)
        return page

    def _build_entities_tab(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(8, 8, 8, 8)

        info_lbl = QLabel("双击任意 NPC 或传送阵可立即平滑定位镜头，或一键测试寻路：")
        info_lbl.setWordWrap(True)
        lay.addWidget(info_lbl)

        self.entity_table = QTableWidget(0, 4)
        self.entity_table.setHorizontalHeaderLabels(
            ["类型", "名称", "服务端坐标", "状态"]
        )
        self.entity_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.entity_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.entity_table.verticalHeader().setVisible(False)
        ehdr = self.entity_table.horizontalHeader()
        ehdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        ehdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        ehdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        ehdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.entity_table.cellDoubleClicked.connect(self._jump_to_entity_row)
        lay.addWidget(self.entity_table, 1)

        path_btn = QPushButton("模拟从场景出生点 → 当前选中实体的 A* 寻路")
        path_btn.clicked.connect(self._path_to_selected_entity)
        lay.addWidget(path_btn)
        return page

    def _build_audit_tab(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(8, 8, 8, 8)

        tile_box = QGroupBox("底图纹理与服务端 .blk 同步")
        tb_lay = QVBoxLayout(tile_box)
        imp_full_btn = QPushButton("导入整张 PNG/JPG 底图自动切分替换…")
        imp_full_btn.clicked.connect(self._import_full_image_dialog)
        rep_sec_btn = QPushButton("替换指定扇区底图 (320×240 GEPJ)…")
        rep_sec_btn.clicked.connect(self._replace_sector_dialog)
        blk_row = QHBoxLayout()
        exp_blk_btn = QPushButton("导出 .blk…")
        exp_blk_btn.clicked.connect(lambda: self._export("blk"))
        imp_blk_btn = QPushButton("导入 .blk…")
        imp_blk_btn.clicked.connect(self._import_blk_dialog)
        blk_row.addWidget(exp_blk_btn)
        blk_row.addWidget(imp_blk_btn)
        tb_lay.addWidget(imp_full_btn)
        tb_lay.addWidget(rep_sec_btn)
        tb_lay.addLayout(blk_row)
        lay.addWidget(tile_box)

        audit_box = QGroupBox("地图健康度与二进制一致性审计")
        ab_lay = QVBoxLayout(audit_box)
        run_audit_btn = QPushButton("运行完整审计 (通行连通域 / 光照 / 遮罩索引 / NPC)")
        run_audit_btn.clicked.connect(self._refresh_audit_panel)
        self.audit_text = QTextEdit()
        self.audit_text.setReadOnly(True)
        ab_lay.addWidget(run_audit_btn)
        ab_lay.addWidget(self.audit_text, 1)
        lay.addWidget(audit_box, 1)
        return page

    def _build_menus_and_toolbar(self) -> None:
        file_menu = self.menuBar().addMenu("文件(&F)")

        open_dir = QAction("选择客户端目录…", self)
        open_dir.setShortcut(QKeySequence("Ctrl+O"))
        open_dir.triggered.connect(self._pick_root)
        file_menu.addAction(open_dir)

        open_file_act = QAction("打开独立 .map 文件…", self)
        open_file_act.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_file_act.triggered.connect(self._open_single_map_dialog)
        file_menu.addAction(open_file_act)

        new_map_act = QAction("新建 / 从美术底图编译 .map…", self)
        new_map_act.setShortcut(QKeySequence("Ctrl+N"))
        new_map_act.triggered.connect(self._new_map_dialog)
        file_menu.addAction(new_map_act)

        file_menu.addSeparator()

        self.save_act = QAction("保存地图 (.map)…", self)
        self.save_act.setShortcut(QKeySequence.StandardKey.Save)
        self.save_act.triggered.connect(self._save_map_smart)
        file_menu.addAction(self.save_act)

        save_as_act = QAction("另存为 (.map)…", self)
        save_as_act.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_act.triggered.connect(self._save_map_as_dialog)
        file_menu.addAction(save_as_act)

        file_menu.addSeparator()
        exp_menu = file_menu.addMenu("导出通道与服务端数据")
        for label, kind in (
            ("导出整图底图 PNG…", "png"),
            ("导出实时光照合成整图 PNG…", "lit_png"),
            ("导出服务端/客户端通行网格 (.blk)…", "blk"),
            ("导出通行状态可视化图 PNG…", "walk_png"),
            ("导出 GIRB 动态光照灰度图 PNG…", "light_png"),
            ("导出完整结构 JSON…", "json"),
        ):
            act = QAction(label, self)
            act.triggered.connect(lambda _=False, k=kind: self._export(k))
            exp_menu.addAction(act)

        file_menu.addSeparator()
        quit_act = QAction("退出", self)
        quit_act.setShortcut(QKeySequence.StandardKey.Quit)
        quit_act.triggered.connect(self.close)
        file_menu.addAction(quit_act)

        # Edit menu
        edit_menu = self.menuBar().addMenu("编辑(&E)")
        self.undo_act = QAction("撤销", self)
        self.undo_act.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_act.triggered.connect(self._do_undo)
        edit_menu.addAction(self.undo_act)

        self.redo_act = QAction("重做", self)
        self.redo_act.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_act.triggered.connect(self._do_redo)
        edit_menu.addAction(self.redo_act)

        edit_menu.addSeparator()
        self.loose_mode_act = QAction("允许宽松覆盖源地图 (仍需二次确认)", self)
        self.loose_mode_act.setCheckable(True)
        self.loose_mode_act.setChecked(self.vm.config.save_mode == "loose")
        self.loose_mode_act.toggled.connect(self._toggle_save_mode)
        edit_menu.addAction(self.loose_mode_act)

        # View menu
        view_menu = self.menuBar().addMenu("视图(&V)")
        fit_act = QAction("适配窗口缩放 (Fit)", self)
        fit_act.setShortcut(QKeySequence("F"))
        fit_act.triggered.connect(lambda: self.canvas.reset_view(fit=True))
        view_menu.addAction(fit_act)
        one_act = QAction("100% 原始像素比例 (1:1)", self)
        one_act.setShortcut(QKeySequence("0"))
        one_act.triggered.connect(self._set_zoom_100)
        view_menu.addAction(one_act)

        # Main Studio Toolbar
        tb = QToolBar("主工具栏")
        tb.setMovable(False)
        self.addToolBar(tb)
        tb.addAction(open_dir)
        tb.addAction(new_map_act)
        tb.addAction(save_as_act)
        tb.addSeparator()
        tb.addAction(self.undo_act)
        tb.addAction(self.redo_act)
        tb.addSeparator()

        tool_group = QActionGroup(self)
        tool_group.setExclusive(True)
        for key, label, shortcut in TOOL_SPECS:
            act = QAction(label, self)
            act.setCheckable(True)
            act.setShortcut(QKeySequence(shortcut))
            if key == self.vm.state.active_tool:
                act.setChecked(True)
            act.triggered.connect(lambda _=False, k=key: self._select_tool(k))
            tool_group.addAction(act)
            tb.addAction(act)
            self._tool_actions[key] = act

        tb.addSeparator()
        tb.addAction(fit_act)
        tb.addAction(one_act)

    # -- handlers & workflows ---------------------------------------------
    def _select_tool(self, tool: str) -> None:
        self.vm.set_tool(tool)
        if tool in ("cell_brush", "cell_rect", "cell_line", "cell_fill"):
            self._ensure_layer_on("walkability")
        elif tool == "light_brush":
            self._ensure_layer_on("lit_preview")
        elif tool == "path_sim":
            self._ensure_layer_on("path")
        elif tool == "mask_select":
            self._ensure_layer_on("mask_cutout")
            self._ensure_layer_on("records")
        self.canvas.update()
        self._refresh_status()

    def _ensure_layer_on(self, name: str) -> None:
        if not self.vm.layer(name):
            self.vm.set_layer(name, True)
            if name in self._layer_checks:
                self._layer_checks[name].blockSignals(True)
                self._layer_checks[name].setChecked(True)
                self._layer_checks[name].blockSignals(False)

    def _toggle_layer(self, name: str, on: bool) -> None:
        self.vm.set_layer(name, on)
        self.canvas.update()

    def _on_cell_radius_changed(self, value: int) -> None:
        self.vm.state.brush_radius = int(value)
        side = value * 2 + 1
        self.cell_rad_lbl.setText(f"{side}×{side} 格")

    def _on_light_val_changed(self, value: int) -> None:
        self.vm.state.light_value = int(value)
        self.light_lbl.setText(f"亮度 {value} / 15 ({value / 8.0:.2f}×)")

    def _set_zoom_100(self) -> None:
        self.canvas.zoom = 1.0
        self.canvas.update()

    def _toggle_save_mode(self, loose: bool) -> None:
        self.vm.config.save_mode = "loose" if loose else "strict"
        self._refresh_status()

    def _do_undo(self) -> None:
        lbl = self.vm.undo()
        if lbl:
            self.canvas.invalidate_caches()
            self._refresh_masks_and_audit()
            self.statusBar().showMessage(f"已撤销：{lbl}", 4000)

    def _do_redo(self) -> None:
        lbl = self.vm.redo()
        if lbl:
            self.canvas.invalidate_caches()
            self._refresh_masks_and_audit()
            self.statusBar().showMessage(f"已重做：{lbl}", 4000)

    def _on_stroke_committed(self, msg: str) -> None:
        self.statusBar().showMessage(msg, 4500)
        self._refresh_audit_panel()

    def _pick_root(self) -> None:
        chosen = QFileDialog.getExistingDirectory(
            self, "选择客户端或地图目录", self.vm.state.client_root
        )
        if chosen:
            self._open_root(chosen)

    def _open_root(self, path: str) -> None:
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            self.vm.set_client_root(
                path, progress=lambda m: self.statusBar().showMessage(m)
            )
            self._populate_map_table()
        except DiscoveryError as exc:
            QMessageBox.warning(self, "未找到地图", str(exc))
            self._refresh_status()
            return
        finally:
            QApplication.restoreOverrideCursor()

        app = QApplication.instance()
        if isinstance(app, QApplication):
            _install_cjk_fonts(app, Path(path))
        self._refresh_status()
        if self._filtered_rows:
            self.table.selectRow(0)

    def _populate_map_table(self) -> None:
        needle = self.search_edit.text().strip().lower()
        all_rows = self.vm.rows
        self._filtered_rows = [
            r
            for r in all_rows
            if not needle
            or needle in r.key.lower()
            or needle in r.name.lower()
            or (needle == "遮罩" and r.records > 0)
        ]
        self.table.blockSignals(True)
        self.table.setRowCount(len(self._filtered_rows))
        for i, r in enumerate(self._filtered_rows):
            items = [
                QTableWidgetItem(r.key),
                QTableWidgetItem(r.name or "—"),
                QTableWidgetItem("损坏" if r.broken else f"{r.width}×{r.height}"),
                QTableWidgetItem("" if r.broken else str(r.sectors)),
                QTableWidgetItem("" if r.broken else str(r.records)),
            ]
            for col, item in enumerate(items):
                if col >= 3:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                if r.broken:
                    item.setForeground(QColor(235, 95, 95))
                    item.setToolTip(r.error)
                elif "現行" in r.name:
                    item.setForeground(QColor(138, 226, 168))
                self.table.setItem(i, col, item)
        self.table.blockSignals(False)

    def _confirm_discard_current_edits(self) -> bool:
        if not self.vm.dirty:
            return True
        answer = QMessageBox.question(
            self,
            "放弃未保存修改？",
            "切换地图将放弃当前地图的未保存修改。是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def _on_row_selected(self) -> None:
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            return
        idx = sel[0].row()
        if not (0 <= idx < len(self._filtered_rows)):
            return
        row = self._filtered_rows[idx]
        if row.broken:
            QMessageBox.critical(self, "地图损坏", f"{row.path.name}\n\n{row.error}")
            return
        if not self._confirm_discard_current_edits():
            return
        try:
            self.vm.open_map(row, discard_changes=True)
        except (MapFormatError, OSError) as exc:
            QMessageBox.critical(self, "打开失败", str(exc))
            return
        self._after_document_opened()

    def _after_document_opened(self) -> None:
        self.canvas.reset_view(fit=True)
        self._refresh_masks_and_audit()
        self._populate_entities_table()
        self._refresh_status()

    def _open_single_map_dialog(self) -> None:
        p, _ = QFileDialog.getOpenFileName(
            self, "打开 .map 地图文件", "", "MXSJ Map (*.map)"
        )
        if not p or not self._confirm_discard_current_edits():
            return
        try:
            self.vm.open_map_file(p, discard_changes=True)
        except Exception as exc:
            QMessageBox.critical(self, "打开失败", str(exc))
            return
        self._after_document_opened()

    def _new_map_dialog(self) -> None:
        dlg = NewMapDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        dest = dlg.dest_edit.text().strip()
        if not dest:
            QMessageBox.warning(self, "缺少输出路径", "请指定新 .map 文件保存路径。")
            return
        if not self._confirm_discard_current_edits():
            return
        img_path = dlg.img_edit.text().strip() or None
        try:
            self.vm.create_new_map(
                dest,
                dlg.w_spin.value(),
                dlg.h_spin.value(),
                image=img_path,
                discard_changes=True,
            )
        except Exception as exc:
            QMessageBox.critical(self, "创建地图失败", str(exc))
            return
        self._after_document_opened()
        self.statusBar().showMessage(f"已创建并打开新地图 {dest}", 5000)

    def _save_map_smart(self) -> None:
        doc = self.vm.document
        if doc is None:
            return
        if self.vm.config.save_mode == "loose":
            ans = QMessageBox.warning(
                self,
                "宽松模式 — 确认直接覆盖源地图？",
                f"即将直接覆盖地图文件：\n{doc.path}\n\n"
                "建议优先使用“另存为”保留原始客户端地图备份。确认覆盖吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if ans == QMessageBox.StandardButton.Yes:
                try:
                    saved = self.vm.save_map(doc.path, allow_overwrite_source=True)
                    self.statusBar().showMessage(f"已保存并校验通过：{saved}", 5000)
                    self.canvas.update()
                except Exception as exc:
                    QMessageBox.critical(self, "保存失败", str(exc))
                return
        self._save_map_as_dialog()

    def _save_map_as_dialog(self) -> None:
        if self.vm.document is None:
            return
        suggested = f"{self.vm.state.current_key}_edited.map"
        dest, _ = QFileDialog.getSaveFileName(
            self, "另存为 .map (写后自动重解析校验)", suggested, "MXSJ Map (*.map)"
        )
        if not dest:
            return
        try:
            saved = self.vm.save_map(dest)
            self.statusBar().showMessage(
                f"已写出并完成 0.1M 二进制重解析校验：{saved}", 6000
            )
            self.canvas.update()
        except ExportBlockedError as exc:
            QMessageBox.warning(self, "严苛保护拦截", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", str(exc))

    def _refresh_masks_and_audit(self) -> None:
        doc = self.vm.document
        self.mask_table.blockSignals(True)
        self.mask_table.setRowCount(0 if doc is None else len(doc.records))
        if doc is not None:
            for i, rec in enumerate(doc.records):
                vals = [
                    str(rec.index),
                    f"{rec.x}, {rec.y}",
                    f"{rec.width}×{rec.height}",
                    str(rec.payload_length),
                ]
                for col, text in enumerate(vals):
                    self.mask_table.setItem(i, col, QTableWidgetItem(text))
        self.mask_table.blockSignals(False)
        if doc is not None and doc.records:
            sel = self.vm.state.selected_record or 0
            if 0 <= sel < len(doc.records):
                self.mask_table.selectRow(sel)
        else:
            from PySide6.QtGui import QPixmap

            self.mask_preview_lbl.setPixmap(QPixmap())
            self.mask_preview_lbl.setText("当前地图无 PrefixRecord 前景遮罩")
        self._refresh_audit_panel()

    def _select_record_row(self, index: int) -> None:
        if 0 <= index < self.mask_table.rowCount():
            self.mask_table.selectRow(index)

    def _on_mask_row_chosen(self) -> None:
        doc = self.vm.document
        if doc is None:
            return
        sel = self.mask_table.selectionModel().selectedRows()
        if not sel:
            return
        idx = sel[0].row()
        if not (0 <= idx < len(doc.records)):
            return
        self.vm.state.selected_record = idx
        dm = doc.decode_record(idx)
        bx0 = max(0, dm.x)
        by0 = max(0, dm.y)
        bx1 = min(doc.header.width, dm.x + dm.width)
        by1 = min(doc.header.height, dm.y + dm.height)
        backdrop = (
            self.vm.render(bx0, by0, bx1, by1)
            if bx1 > bx0 and by1 > by0
            else None
        )
        cutout = dm.to_rgba_cutout(backdrop, backdrop_origin=(bx0, by0))
        qimg = _pil_rgba_to_qimage(cutout)
        from PySide6.QtGui import QPixmap

        pix = QPixmap.fromImage(qimg).scaled(
            260,
            150,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.mask_preview_lbl.setPixmap(pix)
        self.canvas.update()

    def _add_mask_dialog(self) -> None:
        if self.vm.document is None:
            return
        p, _ = QFileDialog.getOpenFileName(
            self, "选择前景遮罩 Alpha PNG", "", "PNG Images (*.png)"
        )
        if not p:
            return
        cx, cy = self.vm.state.cursor or (64, 64)
        idx = self.vm.import_mask_image(p, max(0, cx), max(0, cy))
        self.canvas.invalidate_caches()
        self._refresh_masks_and_audit()
        self.mask_table.selectRow(idx)

    def _move_mask_dialog(self) -> None:
        doc = self.vm.document
        idx = self.vm.state.selected_record
        if doc is None or idx is None or not (0 <= idx < len(doc.records)):
            return
        rec = doc.records[idx]
        text, ok = QInputDialog.getText(
            self,
            f"移动前景遮罩 #{idx}",
            "输入新像素坐标 X,Y：",
            text=f"{rec.x},{rec.y}",
        )
        if not ok or "," not in text:
            return
        nx, ny = (int(v.strip()) for v in text.split(",", 1))
        self.vm.move_mask_record(idx, nx, ny)
        self._refresh_masks_and_audit()
        self.canvas.update()

    def _export_selected_mask(self) -> None:
        idx = self.vm.state.selected_record
        if self.vm.document is None or idx is None:
            return
        dest, _ = QFileDialog.getSaveFileName(
            self,
            "导出遮罩镂空 PNG",
            f"{self.vm.state.current_key}_mask_{idx:03d}.png",
            "PNG (*.png)",
        )
        if dest:
            out = self.vm.export_mask_png(idx, dest, cutout=True)
            self.statusBar().showMessage(f"已导出遮罩 PNG：{out}", 5000)

    def _delete_selected_mask(self) -> None:
        idx = self.vm.state.selected_record
        if self.vm.document is None or idx is None:
            return
        self.vm.delete_mask_record(idx)
        self.canvas.invalidate_caches()
        self._refresh_masks_and_audit()

    def _populate_entities_table(self) -> None:
        ents = self.vm.current_entities() if self.vm.document else {
            "npcs": [],
            "portals": [],
            "arrival": None,
        }
        rows_data: list[tuple[str, str, str, str, int, int]] = []
        if ents["arrival"] is not None:
            a = ents["arrival"]
            rows_data.append(
                ("出生点", "默认落点", f"{a['sx']},{a['sy']}", "标准", a["px"], a["py"])
            )
        for p in ents["portals"]:
            rows_data.append(
                (
                    "传送点",
                    p["name"],
                    f"{p['sx']},{p['sy']}",
                    "跳转阵",
                    p["px"],
                    p["py"],
                )
            )
        for n in ents["npcs"]:
            rows_data.append(
                (
                    "NPC",
                    n["name"],
                    f"{n['sx']},{n['sy']}",
                    "可行走" if n["walkable"] else "阻挡格",
                    n["px"],
                    n["py"],
                )
            )
        self._entity_jump_targets = [(r[4], r[5]) for r in rows_data]
        self.entity_table.setRowCount(len(rows_data))
        for i, (kind, name, coord, status, _, _) in enumerate(rows_data):
            for c, val in enumerate((kind, name, coord, status)):
                it = QTableWidgetItem(val)
                if kind == "传送点":
                    it.setForeground(QColor(110, 232, 255))
                elif status == "阻挡格":
                    it.setForeground(QColor(255, 165, 120))
                self.entity_table.setItem(i, c, it)

    def _jump_to_entity_row(self, row: int, _col: int) -> None:
        if 0 <= row < len(self._entity_jump_targets):
            px, py = self._entity_jump_targets[row]
            self.canvas.center_on_world(px, py, zoom=max(self.canvas.zoom, 1.0))

    def _path_to_selected_entity(self) -> None:
        if self.vm.document is None or not self._entity_jump_targets:
            return
        sel = self.entity_table.selectionModel().selectedRows()
        row = sel[0].row() if sel else len(self._entity_jump_targets) - 1
        gx, gy = self._entity_jump_targets[row]
        ents = self.vm.current_entities()
        if ents["arrival"] is not None:
            sx, sy = ents["arrival"]["px"], ents["arrival"]["py"]
        else:
            sx, sy = self._entity_jump_targets[0]
        res = self.vm.simulate_path((sx, sy), (gx, gy))
        self._ensure_layer_on("path")
        self.canvas.update()
        self.statusBar().showMessage(
            f"A* 寻路模拟结果: {'可达' if res.found else '不可达'} · "
            f"{len(res.cells)} 步 · 代价 {res.cost}",
            5000,
        )

    def _reset_cursor_sector_light(self) -> None:
        if self.vm.document is None:
            return
        cx, cy = self.vm.state.cursor or (10, 10)
        self.vm.reset_sector_lightmap_at(cx, cy)
        self.canvas.invalidate_caches()

    def _import_full_image_dialog(self) -> None:
        if self.vm.document is None:
            return
        p, _ = QFileDialog.getOpenFileName(
            self, "选择替换整张地图的底图", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if p:
            self.vm.import_full_map_image(p)
            self.canvas.invalidate_caches()
            self.statusBar().showMessage("已完成整图 GEPJ 扇区重编码替换", 5000)

    def _replace_sector_dialog(self) -> None:
        doc = self.vm.document
        if doc is None:
            return
        cx, cy = self.vm.state.cursor or (0, 0)
        default_idx = min(
            doc.header.sector_count - 1,
            max(0, (cy // SECTOR_PX_H) * doc.header.sector_columns + cx // SECTOR_PX_W),
        )
        idx, ok = QInputDialog.getInt(
            self,
            "选择要替换底图的扇区",
            f"扇区编号 (0 ~ {doc.header.sector_count - 1}):",
            default_idx,
            0,
            doc.header.sector_count - 1,
        )
        if not ok:
            return
        p, _ = QFileDialog.getOpenFileName(
            self, f"选择扇区 #{idx} 的 320×240 底图", "", "Images (*.png *.jpg *.jpeg)"
        )
        if p:
            self.vm.replace_sector_tile(idx, p)
            self.canvas.invalidate_caches(sector_index=idx)

    def _import_blk_dialog(self) -> None:
        if self.vm.document is None:
            return
        p, _ = QFileDialog.getOpenFileName(
            self, "选择要导入同步的 .blk 文件", "", "BLK Walkability (*.blk)"
        )
        if p:
            changed = self.vm.import_blk(p)
            self.canvas.update()
            self._refresh_audit_panel()
            self.statusBar().showMessage(f"已从 .blk 同步更新 {changed} 个格子", 5000)

    def _refresh_audit_panel(self) -> None:
        if self.vm.document is None:
            self.audit_text.setPlainText("尚未打开地图。")
            return
        rep = self.vm.audit_current_map()
        w = rep["walkability"]
        lines = [
            f"地图编号 : {rep['key']}  ({rep['name']})",
            f"像素尺寸 : {rep['width']} × {rep['height']} px  ({rep['sectors']} 扇区)",
            f"通行统计 : 可行走 {w['walkable_cells']}/{w['total_cells']} "
            f"({w['walkable_ratio'] * 100:.1f}%) · 阴影格 {w['shaded_cells']}",
            f"连通区域 : 共 {w['island_count']} 个连通域 "
            f"(孤立不可达格 {w['isolated_walkable_cells']} 个)",
            f"GIRB光照 : 非中性扇区 {rep['girb_non_neutral_sectors']}"
            f"/{rep['sectors']} · "
            f"亮度范围 {rep['girb_nibble_range'][0]}..{rep['girb_nibble_range'][1]}",
            f"前景遮罩 : {rep['records']} 个 PrefixRecord "
            f"(越界 {rep['out_of_bounds_records']} · "
            f"扇区索引偏差 {rep['sector_ref_mismatches']})",
            f"场景实体 : {rep['npc_count']} 个 NPC · {rep['portal_count']} 个传送点",
        ]
        if rep["trailing_bytes"]:
            lines.append(
                f"历史残留 : 尾部含 {rep['trailing_bytes']} B 旧版 rb+ 残余扇区"
                "（另存为将自动紧凑清理）"
            )
        self.audit_text.setPlainText("\n".join(lines))

    def _on_cursor_moved(self, x: int, y: int) -> None:
        info = self.vm.locate(x, y)
        if info["inside"]:
            cv = info["cell_value"]
            cname = CELL_NAMES.get(cv, str(cv))
            self.telemetry_lbl.setText(
                f"客户端像素 : ({x}, {y})\n"
                f"客户端网格 : ({info['cell'][0]}, {info['cell'][1]})\n"
                f"服务端坐标 : ({info['server_cell'][0]}, {info['server_cell'][1]})\n"
                f"所属扇区   : #{info['sector']} {info['sector_cell']}\n"
                f"LLEC 通行  : {cname}\n"
                f"GIRB 光照  : {info['light']} / 15 ({(info['light'] or 8) / 8:.2f}×)"
            )
        else:
            self.telemetry_lbl.setText(f"画布越界坐标 : ({x}, {y})")
        self._refresh_status()

    def _export(self, kind: str) -> None:
        if self.vm.document is None:
            QMessageBox.information(self, "尚未选择地图", "请先打开一张地图。")
            return
        ext_map = {
            "png": ("导出底图 PNG", "png", "PNG (*.png)"),
            "lit_png": ("导出实时光照合成 PNG", "png", "PNG (*.png)"),
            "walk_png": ("导出通行状态图 PNG", "png", "PNG (*.png)"),
            "light_png": ("导出 GIRB 动态光照图 PNG", "png", "PNG (*.png)"),
            "blk": ("导出服务端/客户端 .blk", "blk", "BLK (*.blk)"),
            "json": ("导出结构 JSON", "json", "JSON (*.json)"),
        }
        title, ext, filt = ext_map[kind]
        suggested = f"{self.vm.state.current_key}.{ext}"
        dest, _ = QFileDialog.getSaveFileName(self, title, suggested, filt)
        if not dest:
            return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            if kind == "png":
                out = self.vm.export_png(dest, apply_lighting=False)
            elif kind == "lit_png":
                out = self.vm.export_png(dest, apply_lighting=True)
            elif kind == "walk_png":
                out = self.vm.export_walkability_png(dest)
            elif kind == "light_png":
                out = self.vm.export_lightmap_png(dest)
            elif kind == "blk":
                out = self.vm.export_blk(dest)
            else:
                out = self.vm.export_json(dest, include_cells=True)
        except ExportBlockedError as exc:
            QMessageBox.warning(self, "拒绝覆盖源地图", str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(self, "导出失败", str(exc))
            return
        finally:
            QApplication.restoreOverrideCursor()
        self.statusBar().showMessage(f"已导出：{out}", 6000)

    def _refresh_status(self) -> None:
        mode = "宽松覆盖" if self.vm.config.save_mode == "loose" else "严苛只读保护"
        self.statusBar().showMessage(f"[{mode}]  {self.vm.status_line()}")

    def closeEvent(self, event) -> None:
        if self.vm.dirty:
            ans = QMessageBox.question(
                self,
                "未保存的修改",
                "当前地图有尚未保存的编辑内容，确定直接退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if ans != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        self.vm.config.window = [self.width(), self.height()]
        self.vm.save_config()
        self.vm.close_map()
        super().closeEvent(event)


def run(vm: EditorViewModel) -> int:
    app = QApplication.instance() or QApplication([])
    assert isinstance(app, QApplication)
    app.setStyleSheet(DARK_QSS)
    _install_cjk_fonts(
        app, Path(vm.config.client_root) if vm.config.client_root else None
    )
    window = EditorWindow(vm)
    window.show()
    return app.exec()


__all__ = ["EditorWindow", "LAYERS", "MapCanvas", "NewMapDialog", "run"]
