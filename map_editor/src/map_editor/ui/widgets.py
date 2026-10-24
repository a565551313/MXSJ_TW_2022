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
    QButtonGroup,
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
    QSizePolicy,
    QSlider,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QStyle,
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
    0: (46, 204, 113, 66),  # walkable
    1: (231, 76, 60, 145),  # blocked
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
    ("pan", "1 浏览", "1"),
    ("cell_brush", "2 通行", "2"),
    ("cell_rect", "3 矩形", "3"),
    ("cell_line", "4 直线", "4"),
    ("cell_fill", "5 油漆桶", "5"),
    ("light_brush", "6 光照", "6"),
    ("path_sim", "7 A*寻路", "7"),
    ("mask_select", "8 遮罩", "8"),
]

STUDIO_QSS = """
QMainWindow, QDialog {
    background: #f2f5f7;
    color: #263542;
}
QMenuBar {
    background: #ffffff;
    color: #344653;
    border-bottom: 1px solid #dce5e9;
    padding: 5px 8px;
}
QMenuBar::item { padding: 6px 10px; border-radius: 5px; }
QMenuBar::item:selected, QMenu::item:selected {
    background: #e3f3ef;
    color: #126b60;
}
QMenu {
    background: #ffffff;
    color: #344653;
    border: 1px solid #dce5e9;
    padding: 5px;
}
QMenu::item { padding: 7px 28px 7px 12px; border-radius: 4px; }
QToolBar {
    background: #ffffff;
    border: none;
    border-bottom: 1px solid #dce5e9;
    spacing: 5px;
    padding: 5px 12px;
}
QToolBar#mainToolbar { min-height: 52px; }
QToolBar#contextToolbar {
    min-height: 42px;
    background: #f8faf9;
    padding: 4px 14px;
    spacing: 7px;
}
QToolButton {
    background: #f4f7f8;
    color: #425663;
    border: 1px solid #e0e8eb;
    border-radius: 7px;
    padding: 7px 10px;
    min-height: 22px;
}
QToolButton:hover { background: #eaf4f2; border-color: #a9d3ca; }
QToolButton:checked {
    background: #e5f3ef;
    color: #126b60;
    border-color: #cce7df;
    font-weight: 700;
}
QPushButton:checked {
    background: #e5f3ef;
    color: #126b60;
    border-color: #a9d3ca;
    font-weight: 650;
}
QPushButton {
    background: #ffffff;
    color: #344653;
    border: 1px solid #d4e0e4;
    border-radius: 7px;
    padding: 8px 12px;
    min-height: 18px;
}
QPushButton:hover { background: #eff8f6; border-color: #8fc8bc; }
QPushButton:pressed { background: #d8eee9; }
QPushButton:default { background: #137c70; color: white; border-color: #137c70; }
QLineEdit, QComboBox, QSpinBox, QTextEdit {
    background: #ffffff;
    color: #263542;
    border: 1px solid #d6e1e5;
    border-radius: 7px;
    padding: 7px 9px;
    selection-background-color: #137c70;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {
    border: 1px solid #4da99a;
}
QTableWidget {
    background: #ffffff;
    alternate-background-color: #f7f9fa;
    color: #344653;
    gridline-color: #edf1f3;
    border: 1px solid #e0e8eb;
    border-radius: 8px;
    selection-background-color: #dff1ed;
    selection-color: #145c53;
}
QHeaderView::section {
    background: #f4f7f8;
    color: #60727c;
    border: none;
    border-bottom: 1px solid #e0e8eb;
    padding: 8px 7px;
    font-weight: 600;
}
QTabWidget::pane {
    border: 1px solid #dce5e9;
    border-radius: 8px;
    background: #ffffff;
    top: -1px;
}
QTabBar::tab {
    background: transparent;
    color: #6f8089;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 9px 11px;
    margin-right: 3px;
}
QTabBar::tab:selected {
    color: #137c70;
    border-bottom-color: #26a18e;
    font-weight: 600;
}
QTabBar::tab:hover:!selected { color: #2f665e; background: #f2f8f7; }
QGroupBox {
    border: 1px solid #e0e8eb;
    border-radius: 9px;
    margin-top: 12px;
    padding: 12px 9px 8px;
    font-weight: 600;
    color: #3d5963;
    background: #ffffff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 11px;
    padding: 0 5px;
    background: #ffffff;
}
QStatusBar {
    background: #ffffff;
    color: #657780;
    border-top: 1px solid #dce5e9;
    padding: 3px 8px;
}
QCheckBox { spacing: 7px; color: #465a64; padding: 3px; }
QCheckBox::indicator { width: 16px; height: 16px; }
QLabel { color: #3c505a; }
QTableWidget::item { padding: 4px 5px; }
QWidget#mapBrowserPanel, QScrollArea#inspectorScroll {
    background: #ffffff;
    border: 1px solid #dce6e5;
    border-radius: 11px;
}
QWidget#inspectorPage { background: #ffffff; }
QTableWidget#mapList {
    background: transparent;
    border: none;
    outline: none;
}
QTableWidget#mapList::item { border: none; padding: 3px 2px; background: transparent; }
QFrame#mapRowCard {
    background: #ffffff;
    border: 1px solid transparent;
    border-radius: 9px;
}
QFrame#mapRowCard[selected="true"] {
    background: #e9f5f1;
    border-color: #cce7de;
}
QFrame#mapRowCard:hover { background: #f5f9f8; border-color: #e7efec; }
QGroupBox#inspectorCard {
    background: #ffffff;
    border: none;
    border-top: 1px solid #edf1f0;
    border-radius: 0;
    margin-top: 8px;
    padding: 13px 3px 5px;
    font-size: 11px;
    color: #869598;
}
QGroupBox#inspectorCard::title {
    left: 2px;
    padding: 0 4px;
    background: #ffffff;
}
QLabel#inspectorObject {
    background: #f5f8f7;
    border: 1px solid #e7eeec;
    border-radius: 9px;
    padding: 10px;
    color: #334b51;
}
QLabel#inspectorMap { color: #71858a; font-size: 11px; }
QPushButton#quietButton { padding: 4px 8px; min-height: 16px; color: #5d7377; }
QPushButton#safeSaveButton {
    background: #167c70;
    color: #ffffff;
    border-color: #167c70;
    font-weight: 700;
}
QPushButton#safeSaveButton:hover { background: #126b60; }
QLabel#mapThumbnail {
    border-radius: 7px;
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
}
QLabel#mapCount {
    color: #7e9093;
    background: #f2f6f5;
    border-radius: 9px;
    padding: 3px 7px;
}
QTableWidget#entityList {
    background: #ffffff;
    border: none;
    gridline-color: transparent;
    selection-background-color: #e9f5f1;
    selection-color: #196d60;
}
QTableWidget#entityList::item { border: none; padding: 2px; background: transparent; }
QSplitter::handle { background: #e1e9ec; width: 5px; }
QScrollArea { border: none; background: #ffffff; }
QLabel#sectionTitle {
    color: #243b46;
    font-size: 15px;
    font-weight: 700;
    padding: 3px 2px;
}
QLabel#welcomeTitle { color: #183c43; font-size: 19px; font-weight: 700; }
QLabel#mutedText { color: #71838b; line-height: 150%; }
QLabel#tipBanner {
    color: #22685e;
    background: #eaf6f2;
    border: 1px solid #cde8df;
    border-radius: 7px;
    padding: 9px;
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
        font = QFont(chosen, 10)
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

    def __init__(self, vm: EditorViewModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.vm = vm
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setToolTip("滚轮缩放；1 浏览后左键拖动，或按住鼠标中键平移画布")
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
        self.eraser_mode = False
        self.pen_path_mode = False
        self.pen_curve_mode = False
        self._pen_nodes: list[tuple[int, int]] = []

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
            painter.fillRect(self.rect(), QColor("#f2f5f7"))
            card_w = min(620.0, max(360.0, self.width() - 72.0))
            card_h = 248.0
            card = QRectF(
                (self.width() - card_w) / 2,
                (self.height() - card_h) / 2,
                card_w,
                card_h,
            )
            painter.setPen(QPen(QColor("#dce6e9"), 1.0))
            painter.setBrush(QColor("#ffffff"))
            painter.drawRoundedRect(card, 16.0, 16.0)
            painter.setPen(QColor("#173f46"))
            title_font = QFont(self.font())
            title_font.setPointSize(20)
            title_font.setBold(True)
            painter.setFont(title_font)
            painter.drawText(
                QRectF(card.x() + 28, card.y() + 30, card.width() - 56, 38),
                Qt.AlignmentFlag.AlignCenter,
                "先打开一张地图，开始探索",
            )
            painter.setFont(self.font())
            painter.setPen(QColor("#647780"))
            painter.drawText(
                QRectF(card.x() + 34, card.y() + 82, card.width() - 68, 64),
                Qt.AlignmentFlag.AlignCenter,
                "从「文件」菜单打开客户端目录，或直接打开 .map 文件。\n"
                "滚轮缩放画布；按 F1 查看操作提示。",
            )
            painter.setPen(QColor("#188575"))
            painter.drawText(
                QRectF(card.x() + 30, card.y() + 169, card.width() - 60, 32),
                Qt.AlignmentFlag.AlignCenter,
                "安全提示：默认不会覆盖客户端原始地图",
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
                                rgba_buf[off : off + 4] = bytes(
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
                            rgba_buf[i * 4 : i * 4 + 4] = bytes((15, 25, 65, a))
                        elif nib > NEUTRAL_NIBBLE:
                            a = min(200, (nib - NEUTRAL_NIBBLE) * 22)
                            rgba_buf[i * 4 : i * 4 + 4] = bytes((255, 214, 102, a))
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

        if self.pen_path_mode and self._pen_nodes:
            preview = self._sample_pen_path(self._pen_nodes)
            pen = QPen(QColor(255, 235, 99, 235))
            pen.setWidthF(2.0 / self.zoom)
            painter.setPen(pen)
            painter.setBrush(QColor(255, 235, 99, 120))
            for start, end in zip(preview, preview[1:], strict=False):
                painter.drawLine(QPointF(*start), QPointF(*end))
            marker_radius = 4.0 / self.zoom
            for node in self._pen_nodes:
                painter.drawEllipse(QPointF(*node), marker_radius, marker_radius)

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
                vx0 - 60 <= p["px"] <= vx1 + 60 and vy0 - 60 <= p["py"] <= vy1 + 60
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
                vx0 - 60 <= n["px"] <= vx1 + 60 and vy0 - 60 <= n["py"] <= vy1 + 60
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
            path_msg = f"可达 ({len(p.cells)} 步)" if p.found else "不可达"
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

        if self.pen_path_mode and event.button() == Qt.MouseButton.RightButton:
            self._finish_pen_path()
            return
        if self.pen_path_mode and event.button() == Qt.MouseButton.LeftButton:
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            self._pen_nodes.append(tuple(map(int, self._to_world(pos))))
            self.update()
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
                if event.button() == Qt.MouseButton.RightButton or self.eraser_mode
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

    def _sample_pen_path(self, nodes: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if not self.pen_curve_mode or len(nodes) < 3:
            return nodes
        sampled: list[tuple[int, int]] = [nodes[0]]
        for index in range(len(nodes) - 1):
            p0 = nodes[max(0, index - 1)]
            p1 = nodes[index]
            p2 = nodes[index + 1]
            p3 = nodes[min(len(nodes) - 1, index + 2)]
            for step in range(1, 7):
                t = step / 6
                t2 = t * t
                t3 = t2 * t
                point = []
                for axis in range(2):
                    a, b, c, d = p0[axis], p1[axis], p2[axis], p3[axis]
                    value = 0.5 * (
                        2 * b
                        + (-a + c) * t
                        + (2 * a - 5 * b + 4 * c - d) * t2
                        + (-a + 3 * b - 3 * c + d) * t3
                    )
                    point.append(round(value))
                sampled.append((point[0], point[1]))
        return sampled

    def cancel_pending_pen_path(self) -> None:
        """Discard uncommitted nodes without changing the current map."""
        if self._pen_nodes:
            self._pen_nodes.clear()
            self.update()

    def _finish_pen_path(self) -> None:
        nodes = self._pen_nodes
        self._pen_nodes = []
        if len(nodes) < 2:
            self.update()
            return
        changed = self.vm.paint_cell_path(self._sample_pen_path(nodes))
        if changed:
            self._refresh_active_path()
            self.strokeCommitted.emit(f"路径钢笔绘制 {changed} 格")
        self.update()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape and self._pen_nodes:
            self.cancel_pending_pen_path()
            event.accept()
            return
        super().keyPressEvent(event)

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


class _MapListCard(QFrame):
    """Compact selectable map card matching the browser preview layout."""

    clicked = Signal()

    def __init__(self, row: MapRow, accent: tuple[str, str]) -> None:
        super().__init__()
        self.setObjectName("mapRowCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 7, 9, 7)
        layout.setSpacing(9)

        thumbnail = QLabel("地")
        thumbnail.setObjectName("mapThumbnail")
        thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumbnail.setFixedSize(42, 42)
        thumbnail.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {accent[0]}, stop:1 {accent[1]});"
        )
        layout.addWidget(thumbnail)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 1, 0, 1)
        text_column.setSpacing(3)
        name = QLabel(row.name or "未命名地图")
        name.setStyleSheet("font-weight:650;color:#334b51;")
        name.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        meta = QLabel(
            f"{row.key}  ·  "
            + (
                "文件损坏"
                if row.broken
                else f"{row.width} × {row.height} px  ·  {row.sectors} 区"
            )
        )
        meta.setStyleSheet("font-size:10px;color:#829397;")
        text_column.addWidget(name)
        text_column.addWidget(meta)
        layout.addLayout(text_column, 1)

        badge = QLabel("损坏" if row.broken else f"{row.records} 遮罩")
        badge_style = (
            "font-size:9px;color:#b45c51;background:#fbefec;"
            if row.broken
            else "font-size:9px;color:#27826e;background:#e1f1e9;"
        )
        badge.setStyleSheet(badge_style + "border-radius:5px;padding:3px 5px;")
        layout.addWidget(badge, 0, Qt.AlignmentFlag.AlignVCenter)
        for label in (thumbnail, name, meta, badge):
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        if row.broken:
            self.setToolTip(row.error)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            event.accept()
            return
        super().mousePressEvent(event)


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
        self.resize(max(w, 1280), max(h, 780))
        self.setMinimumSize(1100, 700)

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
        workspace = QSplitter(Qt.Orientation.Horizontal)
        workspace.setChildrenCollapsible(False)
        workspace.setHandleWidth(8)

        # Map browser: intentionally limited to search and map selection.
        left = QWidget()
        left.setObjectName("mapBrowserPanel")
        left.setMinimumWidth(225)
        left.setMaximumWidth(330)
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(10, 9, 8, 9)
        title_row = QHBoxLayout()
        title = QLabel("地图")
        title.setObjectName("sectionTitle")
        self.map_count_lbl = QLabel("0")
        self.map_count_lbl.setObjectName("mapCount")
        title_row.addWidget(title)
        title_row.addStretch(1)
        title_row.addWidget(self.map_count_lbl)
        left_lay.addLayout(title_row)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索地图编号或名称…")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self._populate_map_table)
        left_lay.addWidget(self.search_edit)
        self.table = QTableWidget(0, 1)
        self.table.setObjectName("mapList")
        self.table.horizontalHeader().hide()
        self.table.verticalHeader().hide()
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # 表头已隐藏，Qt 不会自动撑开列宽，列宽会锁死默认 100px，
        # 导致行卡片被挤在 100px 窄条里、面板右侧大片空白（「宽但挤」）。
        # 与下方实体列表表格保持一致：显式让唯一列随视口拉伸。
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.itemSelectionChanged.connect(self._on_map_table_selection_changed)
        left_lay.addWidget(self.table, 1)

        # Canvas and the frequently-used entity lists share an adjustable split.
        center = QSplitter(Qt.Orientation.Vertical)
        center.setChildrenCollapsible(False)
        center.setHandleWidth(7)
        center.addWidget(self.canvas)
        self.entity_tabs = QTabWidget()
        self.entity_tabs.setMinimumHeight(150)
        self.entity_tables: dict[str, QTableWidget] = {}
        # 底部实体列表为固定表头的文字表格（表头常驻可见）：
        # NPC 七列（编号/NPC/模型ID/朝向/服务端坐标/像素坐标/状态），
        # 传送点五列（编号/传送点/服务端坐标/跳转坐标/描述）。
        # 列宽按全表内容极值定（名称≤7 字、造型≤7 字符、坐标≤9 字符），
        # 文字一律居中；不做 Stretch——剩余空间摊给任何一列都会过宽，
        # 不如留白（面板与表格同为白底，无视觉断裂）。
        self._entity_headers: dict[str, list[str]] = {
            "npcs": ["编号", "NPC", "模型ID", "朝向", "服务端坐标", "像素坐标", "状态"],
            "portals": ["编号", "传送点", "服务端坐标", "跳转坐标", "描述"],
        }
        self._entity_column_widths: dict[str, list[int]] = {
            "npcs": [64, 170, 100, 56, 105, 115, 85],
            "portals": [64, 170, 105, 105, 130],
        }
        for tab_name, key in (("NPC", "npcs"), ("传送点", "portals")):
            page = QWidget()
            page_lay = QVBoxLayout(page)
            page_lay.setContentsMargins(5, 4, 5, 4)
            table = QTableWidget(0, len(self._entity_headers[key]))
            table.setObjectName("entityList")
            table.setHorizontalHeaderLabels(self._entity_headers[key])
            table.horizontalHeader().setDefaultAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            table.verticalHeader().hide()
            table.setShowGrid(False)
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            # 列宽定内容不拉伸：窗口过窄时允许横向滚动条，避免静默截断
            table.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            table.cellDoubleClicked.connect(self._jump_to_entity_row)
            table.itemSelectionChanged.connect(self._on_entity_selected)
            for column, width in enumerate(self._entity_column_widths[key]):
                table.setColumnWidth(column, width)
            page_lay.addWidget(table)
            self.entity_tables[key] = table
            self.entity_tabs.addTab(page, tab_name)
        entity_tools = QWidget()
        entity_tools_lay = QHBoxLayout(entity_tools)
        entity_tools_lay.setContentsMargins(4, 2, 6, 2)
        entity_tools_lay.setSpacing(6)
        self.entity_search = QLineEdit()
        self.entity_search.setPlaceholderText("搜索名称…")
        self.entity_search.setClearButtonEnabled(True)
        self.entity_search.setFixedWidth(160)
        self.entity_search.textChanged.connect(self._filter_entities_table)
        entity_tools_lay.addWidget(self.entity_search)
        self.entity_collapse_btn = QPushButton("收起")
        self.entity_collapse_btn.setObjectName("quietButton")
        self.entity_collapse_btn.clicked.connect(self._toggle_entity_panel)
        entity_tools_lay.addWidget(self.entity_collapse_btn)
        self.entity_tabs.setCornerWidget(
            entity_tools, Qt.Corner.TopRightCorner
        )
        self.entity_table = self.entity_tables["npcs"]
        self._entity_active_key = "npcs"
        self.entity_tabs.currentChanged.connect(self._on_entity_tab_changed)
        center.addWidget(self.entity_tabs)
        self._center_splitter = center
        self._entity_panel_collapsed = False
        center.setStretchFactor(0, 1)
        center.setStretchFactor(1, 0)
        center.setSizes([650, 210])

        # Right-hand inspector: map/object context, display layers and safe save.
        right_scroll = QScrollArea()
        right_scroll.setObjectName("inspectorScroll")
        right_scroll.setWidgetResizable(True)
        right_scroll.setMinimumWidth(255)
        right_scroll.setMaximumWidth(340)
        right_page = QWidget()
        right_page.setObjectName("inspectorPage")
        right_lay = QVBoxLayout(right_page)
        right_lay.setContentsMargins(10, 10, 10, 10)
        right_lay.setSpacing(10)
        inspector_title = QLabel("检查器")
        inspector_title.setObjectName("sectionTitle")
        right_lay.addWidget(inspector_title)

        object_box = QGroupBox("选中对象")
        object_box.setObjectName("inspectorCard")
        object_lay = QVBoxLayout(object_box)
        self.selected_object_lbl = QLabel("从下方 NPC 或传送点列表选择对象")
        self.selected_object_lbl.setObjectName("inspectorObject")
        self.selected_object_lbl.setWordWrap(True)
        object_lay.addWidget(self.selected_object_lbl)
        path_btn = QPushButton("从出生点模拟寻路到所选对象")
        path_btn.clicked.connect(self._path_to_selected_entity)
        object_lay.addWidget(path_btn)
        right_lay.addWidget(object_box)

        map_box = QGroupBox("地图信息")
        map_box.setObjectName("inspectorCard")
        map_lay = QVBoxLayout(map_box)
        self.map_info_lbl = QLabel("尚未打开地图")
        self.map_info_lbl.setObjectName("inspectorMap")
        self.map_info_lbl.setWordWrap(True)
        map_lay.addWidget(self.map_info_lbl)
        safe_save_btn = QPushButton("另存为副本…")
        safe_save_btn.setObjectName("safeSaveButton")
        safe_save_btn.setToolTip("保留客户端原始地图，另存一份可编辑副本")
        safe_save_btn.clicked.connect(self._save_map_as_dialog)
        map_lay.addWidget(safe_save_btn)
        right_lay.addWidget(map_box)

        layers_box = QGroupBox("常用图层")
        layers_lay = QVBoxLayout(layers_box)
        for key, label in (
            ("texture", "底图纹理"),
            ("walkability", "通行状态"),
            ("lit_preview", "光照合成"),
            ("mask_cutout", "前景遮罩"),
            ("entities", "NPC / 传送点"),
            ("path", "寻路轨迹"),
        ):
            check = QCheckBox(label)
            check.setChecked(self.vm.layer(key))
            check.toggled.connect(lambda on, name=key: self._toggle_layer(name, on))
            self._layer_checks[key] = check
            layers_lay.addWidget(check)
        right_lay.addWidget(layers_box)

        advanced_box = QGroupBox("高级显示与工具（展开）")
        advanced_box.setCheckable(True)
        advanced_box.setChecked(False)
        advanced_lay = QVBoxLayout(advanced_box)
        advanced_content = QWidget()
        advanced_content_lay = QVBoxLayout(advanced_content)
        advanced_content_lay.setContentsMargins(0, 0, 0, 0)
        for key, label in (
            ("records", "遮罩记录框"),
            ("grid", "逻辑格线"),
            ("sector_bounds", "扇区边界"),
            ("collision", "碰撞热力"),
        ):
            check = QCheckBox(label)
            check.setChecked(self.vm.layer(key))
            check.toggled.connect(lambda on, name=key: self._toggle_layer(name, on))
            self._layer_checks[key] = check
            advanced_content_lay.addWidget(check)
        self.telemetry_lbl = QLabel("移动鼠标到画布查看坐标与格属性。")
        self.telemetry_lbl.setWordWrap(True)
        advanced_content_lay.addWidget(self.telemetry_lbl)
        advanced_lay.addWidget(advanced_content)
        advanced_content.setVisible(False)
        advanced_box.toggled.connect(advanced_content.setVisible)
        right_lay.addWidget(advanced_box)

        masks_box = QGroupBox("遮罩记录")
        masks_lay = QVBoxLayout(masks_box)
        self.mask_table = QTableWidget(0, 4)
        self.mask_table.setHorizontalHeaderLabels(["#", "位置", "尺寸", "字节"])
        self.mask_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.mask_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.mask_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.mask_table.verticalHeader().setVisible(False)
        self.mask_table.setMaximumHeight(145)
        self.mask_table.itemSelectionChanged.connect(self._on_mask_row_chosen)
        masks_lay.addWidget(self.mask_table)
        self.mask_preview_lbl = QLabel("未选择遮罩记录")
        self.mask_preview_lbl.setWordWrap(True)
        masks_lay.addWidget(self.mask_preview_lbl)
        mask_actions = QHBoxLayout()
        for label, handler in (
            ("导入 PNG", self._add_mask_dialog),
            ("移动", self._move_mask_dialog),
            ("删除", self._delete_selected_mask),
        ):
            button = QPushButton(label)
            button.clicked.connect(handler)
            mask_actions.addWidget(button)
        masks_lay.addLayout(mask_actions)
        advanced_content_lay.addWidget(masks_box)

        audit_box = QGroupBox("数据审计")
        audit_lay = QVBoxLayout(audit_box)
        audit_button = QPushButton("运行地图审计")
        audit_button.clicked.connect(self._refresh_audit_panel)
        audit_lay.addWidget(audit_button)
        self.audit_text = QTextEdit()
        self.audit_text.setReadOnly(True)
        self.audit_text.setMaximumHeight(130)
        audit_lay.addWidget(self.audit_text)
        advanced_content_lay.addWidget(audit_box)
        right_lay.addStretch(1)
        right_scroll.setWidget(right_page)

        workspace.addWidget(left)
        workspace.addWidget(center)
        workspace.addWidget(right_scroll)
        workspace.setStretchFactor(0, 0)
        workspace.setStretchFactor(1, 1)
        workspace.setStretchFactor(2, 0)
        workspace.setSizes([252, 930, 286])
        self.setCentralWidget(workspace)

    def _on_entity_tab_changed(self, index: int) -> None:
        key = "npcs" if index == 0 else "portals"
        self.entity_table = self.entity_tables[key]
        self._entity_active_key = key
        self.entity_search.clear()
        self._populate_entities_table()
        self.entity_table.clearSelection()
        self.selected_object_lbl.setText("从下方 NPC 或传送点列表选择对象")

    def _filter_entities_table(self, text: str) -> None:
        needle = text.strip().casefold()
        for row in range(self.entity_table.rowCount()):
            item = self.entity_table.item(row, 1)
            self.entity_table.setRowHidden(
                row, bool(needle and item and needle not in item.text().casefold())
            )

    def _toggle_entity_panel(self) -> None:
        self._entity_panel_collapsed = not self._entity_panel_collapsed
        if self._entity_panel_collapsed:
            self.entity_tabs.setMinimumHeight(42)
            self.entity_tabs.setMaximumHeight(48)
            self._center_splitter.setSizes(
                [max(1, self._center_splitter.height() - 48), 48]
            )
            self.entity_collapse_btn.setText("展开")
        else:
            self.entity_tabs.setMaximumHeight(16777215)
            self.entity_tabs.setMinimumHeight(150)
            self._center_splitter.setSizes(
                [max(1, self._center_splitter.height() - 210), 210]
            )
            self.entity_collapse_btn.setText("收起")

    def _on_entity_selected(self) -> None:
        selected = self.entity_table.selectionModel().selectedRows()
        selected_row = selected[0].row() if selected else None
        if selected_row is None:
            self.selected_object_lbl.setText("从下方 NPC 或传送点列表选择对象")
            return
        headers = self._entity_headers[self._entity_active_key]
        pairs = []
        for column, header in enumerate(headers):
            item = self.entity_table.item(selected_row, column)
            pairs.append(f"{header} {item.text() if item is not None else '—'}")
        # 每行三组「表头 值」换行，检查器标签完整镜像当前选中行
        self.selected_object_lbl.setText(
            "\n".join(
                " · ".join(pairs[index : index + 3])
                for index in range(0, len(pairs), 3)
            )
        )
        if selected_row < len(self._entity_jump_targets):
            self._jump_to_entity_row(selected_row, 0)

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
        self.save_act.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
        )
        self.save_act.setShortcut(QKeySequence.StandardKey.Save)
        self.save_act.triggered.connect(self._save_map_smart)
        self.save_act.setToolTip("保存当前编辑；默认保护客户端原图，建议另存为副本")
        file_menu.addAction(self.save_act)

        save_as_act = QAction("另存为…", self)
        save_as_act.setToolTip("将当前地图另存为新的 .map 文件")
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
        self.undo_act.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack)
        )
        self.undo_act.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_act.triggered.connect(self._do_undo)
        edit_menu.addAction(self.undo_act)

        self.redo_act = QAction("重做", self)
        self.redo_act.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward)
        )
        self.redo_act.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_act.triggered.connect(self._do_redo)
        edit_menu.addAction(self.redo_act)

        edit_menu.addSeparator()
        self.loose_mode_act = QAction("允许宽松覆盖源地图 (仍需二次确认)", self)
        self.loose_mode_act.setCheckable(True)
        self.loose_mode_act.setChecked(self.vm.config.save_mode == "loose")
        self.loose_mode_act.toggled.connect(self._toggle_save_mode)
        edit_menu.addAction(self.loose_mode_act)

        map_menu = self.menuBar().addMenu("地图(&M)")
        for label, handler in (
            ("导入整张底图并替换纹理…", self._import_full_image_dialog),
            ("替换单个扇区底图…", self._replace_sector_dialog),
            ("导入服务端 .blk 通行数据…", self._import_blk_dialog),
        ):
            action = QAction(label, self)
            action.triggered.connect(handler)
            map_menu.addAction(action)

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

        help_menu = self.menuBar().addMenu("帮助(&H)")
        guide_act = QAction("打开快速开始指南", self)
        guide_act.setShortcut(QKeySequence("F1"))
        guide_act.triggered.connect(
            lambda: QMessageBox.information(
                self,
                "快速开始",
                "先从文件菜单打开客户端目录或单张地图。建议使用右侧「另存为副本」后再编辑。\n\n"
                "画布下方可切换 NPC 与传送点；右侧检查器显示图层、遮罩记录与审计信息。",
            )
        )
        guide_act.setStatusTip("显示地图编辑的基本操作和安全提示")
        help_menu.addAction(guide_act)

        # Primary tool categories: icon + label, followed by contextual controls.
        main_toolbar = QToolBar("主工具栏")
        main_toolbar.setObjectName("mainToolbar")
        main_toolbar.setMovable(False)
        main_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(main_toolbar)
        for action in (self.save_act, self.undo_act, self.redo_act):
            main_toolbar.addAction(action)
        main_toolbar.addSeparator()
        category_group = QActionGroup(self)
        category_group.setExclusive(True)
        categories = (
            ("browse", "浏览", QStyle.StandardPixmap.SP_DesktopIcon, "1"),
            ("walk", "通行", QStyle.StandardPixmap.SP_DialogApplyButton, "2"),
            ("mask", "遮罩", QStyle.StandardPixmap.SP_FileDialogDetailedView, "9"),
            ("light", "光照", QStyle.StandardPixmap.SP_DialogYesButton, "6"),
            ("entities", "实体", QStyle.StandardPixmap.SP_FileDialogInfoView, "7"),
            ("path", "寻路", QStyle.StandardPixmap.SP_ArrowRight, "8"),
        )
        self._category_actions: dict[str, QAction] = {}
        for key, label, icon, shortcut in categories:
            action = QAction(self.style().standardIcon(icon), label, self)
            action.setCheckable(True)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(
                lambda _=False, name=key: self._select_main_category(name)
            )
            category_group.addAction(action)
            main_toolbar.addAction(action)
            self._category_actions[key] = action
        self._category_actions["browse"].setChecked(True)
        spacer = QWidget()
        spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        main_toolbar.addWidget(spacer)
        toolbar_save_copy = QPushButton("另存为副本")
        toolbar_save_copy.setObjectName("safeSaveButton")
        toolbar_save_copy.clicked.connect(self._save_map_as_dialog)
        main_toolbar.addWidget(toolbar_save_copy)

        self.context_toolbar = QToolBar("当前工具选项")
        self.context_toolbar.setObjectName("contextToolbar")
        self.context_toolbar.setMovable(False)
        self.context_toolbar.setWindowTitle("当前工具选项")
        self.addToolBar(self.context_toolbar)
        self._main_category = "browse"
        self._walk_mode = "brush"
        self._pen_style_index = 0
        self._walk_brush_radius = self.vm.state.brush_radius
        self._update_context_toolbar()

    def _select_main_category(self, category: str) -> None:
        self._main_category = category
        if category in self._category_actions:
            self._category_actions[category].setChecked(True)
        tool_by_category = {
            "browse": "pan",
            "walk": "cell_brush",
            "light": "light_brush",
            "entities": "pan",
            "path": "path_sim",
            "mask": "mask_select",
        }
        if category != "walk":
            self.canvas.pen_path_mode = False
            self.canvas.eraser_mode = False
            self.canvas.cancel_pending_pen_path()
        self._select_tool(tool_by_category[category])
        if category == "walk":
            self._select_walk_mode(self._walk_mode)
        elif category == "entities":
            self._ensure_layer_on("entities")
        self._update_context_toolbar()

    def _update_context_toolbar(self) -> None:
        self.context_toolbar.clear()
        category = self._main_category
        if category == "walk":
            self.context_toolbar.addWidget(QLabel("状态"))
            self.cell_combo = QComboBox()
            for value, label in (
                (0, "可通行"),
                (1, "阻挡"),
                (2, "阴影下可通行"),
                (3, "阴影下阻挡"),
            ):
                self.cell_combo.addItem(label, value)
            self.cell_combo.setCurrentIndex(self.vm.state.brush_cell_value)
            self.cell_combo.currentIndexChanged.connect(
                lambda _index: setattr(
                    self.vm.state,
                    "brush_cell_value",
                    int(self.cell_combo.currentData()),
                )
            )
            self.context_toolbar.addWidget(self.cell_combo)
            for label, color in (
                ("可通行", "#55b98b"),
                ("阻挡", "#dd726a"),
                ("阴影通行", "#56abc3"),
                ("阴影阻挡", "#a07ac3"),
            ):
                chip = QLabel(f"● {label}")
                chip.setStyleSheet(f"color:{color};font-size:10px;")
                self.context_toolbar.addWidget(chip)
            self.context_toolbar.addSeparator()
            if hasattr(self, "walk_mode_group"):
                self.walk_mode_group.deleteLater()
            self.walk_mode_group = QButtonGroup(self)
            self.walk_mode_group.setExclusive(True)
            for mode, label in (
                ("brush", "画笔"),
                ("rect", "矩形"),
                ("line", "直线"),
                ("fill", "区域填充"),
                ("eraser", "橡皮"),
                ("pen", "钢笔⌄"),
            ):
                button = QPushButton(label)
                button.setCheckable(True)
                button.setChecked(
                    self._walk_mode == mode
                    or (mode == "pen" and self._walk_mode in {"pen_dot", "pen_path"})
                )
                self.walk_mode_group.addButton(button)
                button.clicked.connect(
                    lambda _checked=False, value=mode: self._activate_walk_mode(value)
                )
                self.context_toolbar.addWidget(button)
            if self._walk_mode in {"pen_dot", "pen_path"}:
                self.context_toolbar.addWidget(QLabel("钢笔"))
                self.pen_style_combo = QComboBox()
                self.pen_style_combo.addItems(
                    ["单格钢笔", "路径钢笔 · 折线", "路径钢笔 · 曲线"]
                )
                self.pen_style_combo.setCurrentIndex(self._pen_style_index)
                self.pen_style_combo.currentIndexChanged.connect(
                    self._select_pen_variant
                )
                self.context_toolbar.addWidget(self.pen_style_combo)
                if self._walk_mode == "pen_path":
                    self.context_toolbar.addWidget(
                        QLabel("点击添加节点，右键结束；Esc 取消")
                    )
            if self._walk_mode in {"brush", "eraser", "line", "pen_path"}:
                self.context_toolbar.addSeparator()
                self.context_toolbar.addWidget(
                    QLabel("尺寸" if self._walk_mode != "line" else "线宽")
                )
                self.brush_size_slider = QSlider(Qt.Orientation.Horizontal)
                self.brush_size_slider.setRange(1, 13)
                self.brush_size_slider.setSingleStep(2)
                self.brush_size_slider.setPageStep(2)
                self.brush_size_slider.setFixedWidth(110)
                size = self.vm.state.brush_radius * 2 + 1
                self.brush_size_slider.setValue(size)
                self.brush_size_spin = QSpinBox()
                self.brush_size_spin.setRange(1, 13)
                self.brush_size_spin.setSingleStep(2)
                self.brush_size_spin.setValue(size)
                self.brush_size_slider.valueChanged.connect(self._set_brush_size)
                self.brush_size_spin.valueChanged.connect(self._set_brush_size)
                self.context_toolbar.addWidget(self.brush_size_slider)
                self.context_toolbar.addWidget(self.brush_size_spin)
            elif self._walk_mode == "fill":
                self.context_toolbar.addWidget(
                    QLabel("点击相邻同类区域填充；可用 Ctrl+Z 撤销")
                )
            elif self._walk_mode == "pen_dot":
                self.context_toolbar.addWidget(QLabel("单格钢笔：点击画布绘制一个格子"))
        elif category == "light":
            self.context_toolbar.addWidget(QLabel("亮度"))
            self.light_slider = QSlider(Qt.Orientation.Horizontal)
            self.light_slider.setRange(0, 15)
            self.light_slider.setValue(self.vm.state.light_value)
            self.light_slider.setFixedWidth(150)
            self.light_slider.valueChanged.connect(self._on_light_val_changed)
            self.context_toolbar.addWidget(self.light_slider)
            self.light_lbl = QLabel(f"{self.vm.state.light_value} / 15")
            self.context_toolbar.addWidget(self.light_lbl)
            self.context_toolbar.addWidget(QLabel("光斑半径"))
            self.light_rad_slider = QSlider(Qt.Orientation.Horizontal)
            self.light_rad_slider.setRange(1, 12)
            self.light_rad_slider.setValue(self.vm.state.light_radius)
            self.light_rad_slider.setFixedWidth(100)
            self.light_rad_slider.valueChanged.connect(
                lambda value: setattr(self.vm.state, "light_radius", int(value))
            )
            self.context_toolbar.addWidget(self.light_rad_slider)
        elif category == "path":
            self.context_toolbar.addWidget(
                QLabel("依次点击地图上的起点与终点以模拟寻路。")
            )
        elif category == "entities":
            self.context_toolbar.addWidget(
                QLabel("在画布下方切换 NPC 与传送点；双击条目定位。")
            )
        elif category == "mask":
            for label, handler in (
                ("导入 PNG", self._add_mask_dialog),
                ("导出 PNG", self._export_selected_mask),
                ("移动遮罩", self._move_mask_dialog),
                ("删除遮罩", self._delete_selected_mask),
            ):
                button = QPushButton(label)
                button.clicked.connect(handler)
                self.context_toolbar.addWidget(button)
        else:
            fit = QPushButton("适配窗口")
            fit.clicked.connect(lambda: self.canvas.reset_view(fit=True))
            one = QPushButton("100%")
            one.clicked.connect(self._set_zoom_100)
            self.context_toolbar.addWidget(QLabel("滚轮缩放 · 中键拖动画布"))
            self.context_toolbar.addWidget(fit)
            self.context_toolbar.addWidget(one)

    def _activate_walk_mode(self, mode: str) -> None:
        if mode == "pen":
            if self._walk_mode not in {"pen_dot", "pen_path"}:
                self._select_pen_variant(self._pen_style_index)
            return
        self._select_walk_mode(mode)

    def _select_pen_variant(self, index: int) -> None:
        self._pen_style_index = int(index)
        self.canvas.pen_curve_mode = index == 2
        self._select_walk_mode("pen_dot" if index == 0 else "pen_path")

    def _select_walk_mode(self, mode: str) -> None:
        previous_mode = self._walk_mode
        if mode == "pen_dot" and previous_mode != "pen_dot":
            self._walk_brush_radius = self.vm.state.brush_radius
        elif mode != "pen_dot" and previous_mode == "pen_dot":
            self.vm.state.brush_radius = self._walk_brush_radius
        self._walk_mode = mode
        tools = {
            "brush": "cell_brush",
            "eraser": "cell_brush",
            "pen_dot": "cell_brush",
            "rect": "cell_rect",
            "line": "cell_line",
            "fill": "cell_fill",
            "pen_path": "cell_line",
        }
        self.vm.set_tool(tools[mode])
        self.canvas.eraser_mode = mode == "eraser"
        self.canvas.pen_path_mode = mode == "pen_path"
        if mode != "pen_path":
            self.canvas._pen_nodes.clear()
        if mode == "pen_dot":
            self.vm.state.brush_radius = 0
        self._ensure_layer_on("walkability")
        self._update_context_toolbar()
        self.canvas.update()

    def _set_brush_size(self, value: int) -> None:
        size = max(1, min(13, int(value)))
        size = size if size % 2 else size + 1
        self.vm.state.brush_radius = (size - 1) // 2
        if hasattr(self, "brush_size_slider"):
            self.brush_size_slider.blockSignals(True)
            self.brush_size_slider.setValue(size)
            self.brush_size_slider.blockSignals(False)
        if hasattr(self, "brush_size_spin"):
            self.brush_size_spin.blockSignals(True)
            self.brush_size_spin.setValue(size)
            self.brush_size_spin.blockSignals(False)

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
            self.map_info_lbl.setText(
                f"目录：{path}\n已扫描 {self.vm.state.map_count} 张地图"
            )
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

    def _on_map_table_selection_changed(self) -> None:
        selected = {
            index.row() for index in self.table.selectionModel().selectedRows()
        }
        for row in range(self.table.rowCount()):
            card = self.table.cellWidget(row, 0)
            if isinstance(card, _MapListCard):
                card.setProperty("selected", row in selected)
                card.style().unpolish(card)
                card.style().polish(card)
        self._on_row_selected()

    def _make_map_row_card(self, row: MapRow, index: int) -> _MapListCard:
        palettes = (
            ("#83b4a0", "#668e7e"),
            ("#9bb5a2", "#718b75"),
            ("#c2b08a", "#8c9b75"),
            ("#81a9ae", "#637f83"),
        )
        accent = palettes[index % len(palettes)]
        card = _MapListCard(row, accent)
        card.clicked.connect(lambda target=index: self.table.selectRow(target))
        return card

    def _populate_map_table(self) -> None:
        needle = self.search_edit.text().strip().lower()
        all_rows = self.vm.rows
        self._filtered_rows = [
            row
            for row in all_rows
            if not needle
            or needle in row.key.lower()
            or needle in row.name.lower()
            or (needle == "遮罩" and row.records > 0)
        ]
        self.table.blockSignals(True)
        self.table.clearSelection()
        self.table.clearContents()
        self.table.setRowCount(len(self._filtered_rows))
        for index, row in enumerate(self._filtered_rows):
            item = QTableWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, row.key)
            self.table.setItem(index, 0, item)
            self.table.setCellWidget(index, 0, self._make_map_row_card(row, index))
            self.table.setRowHeight(index, 70)
        self.table.blockSignals(False)
        self.map_count_lbl.setText(str(len(self._filtered_rows)))
        self._on_map_table_selection_changed()

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
        self.canvas.cancel_pending_pen_path()
        self.canvas.reset_view(fit=True)
        self._refresh_masks_and_audit()
        self._populate_entities_table()
        for table in self.entity_tables.values():
            table.clearSelection()
        state = self.vm.state
        self.map_info_lbl.setText(
            f"{state.current_key} · {state.current_name}\n"
            f"{state.current_size[0]} × {state.current_size[1]} px · "
            f"{state.current_sectors} 扇区 · {state.current_records} 个遮罩记录\n"
            f"保存模式：{'宽松' if self.vm.config.save_mode == 'loose' else '保护原图'}"
        )
        self.selected_object_lbl.setText("从下方 NPC 或传送点列表选择对象")
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
            self.vm.render(bx0, by0, bx1, by1) if bx1 > bx0 and by1 > by0 else None
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
        ents = (
            self.vm.current_entities()
            if self.vm.document
            else {
                "npcs": [],
                "portals": [],
                "arrival": None,
            }
        )
        # 每行 = 各列显示值（数量随标签页而定）+ 末尾两元素（跳转目标 px, py）
        grouped: dict[str, list[tuple[str, ...]]] = {
            "npcs": [],
            "portals": [],
        }
        if ents["arrival"] is not None:
            arrival = ents["arrival"]
            grouped["portals"].append(
                (
                    "—",
                    "默认落点",
                    f"{arrival['sx']},{arrival['sy']}",
                    "—",
                    "出生点",
                    arrival["px"],
                    arrival["py"],
                )
            )
        for portal in ents["portals"]:
            grouped["portals"].append(
                (
                    str(portal["npc_id"]) if portal["npc_id"] is not None else "—",
                    portal["name"],
                    f"{portal['sx']},{portal['sy']}",
                    f"{portal['jump_sx']},{portal['jump_sy']}",
                    portal["desc"] or "—",
                    portal["px"],
                    portal["py"],
                )
            )
        for npc in ents["npcs"]:
            grouped["npcs"].append(
                (
                    str(npc["npc_id"]),
                    npc["name"],
                    npc["shape"] or "—",
                    str(npc["direction"]),
                    f"{npc['sx']},{npc['sy']}",
                    f"{npc['px']},{npc['py']}",
                    "可通行" if npc["walkable"] else "阻挡格",
                    npc["px"],
                    npc["py"],
                )
            )

        # 行元组 = 各列显示值 + 末尾两元素（跳转目标 px, py，仅内部使用）
        for key, rows in grouped.items():
            table = self.entity_tables[key]
            headers = self._entity_headers[key]
            table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                for column, value in enumerate(row[:-2]):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if key == "portals" and row[1] != "默认落点":
                        item.setForeground(QColor(25, 126, 150))
                    elif (
                        key == "npcs"
                        and headers[column] == "状态"
                        and value == "阻挡格"
                    ):
                        item.setForeground(QColor(195, 82, 55))
                    table.setItem(row_index, column, item)
                table.setRowHeight(row_index, 28)

        self.entity_tabs.setTabText(0, f"NPC  {len(grouped['npcs']):,}")
        self.entity_tabs.setTabText(1, f"传送点  {len(grouped['portals']):,}")
        active_key = "npcs" if self.entity_tabs.currentIndex() == 0 else "portals"
        self.entity_table = self.entity_tables[active_key]
        self._entity_active_key = active_key
        self._entity_jump_targets = [(row[-2], row[-1]) for row in grouped[active_key]]
        self._filter_entities_table(self.entity_search.text())

    def _jump_to_entity_row(self, row: int, _col: int) -> None:
        if 0 <= row < len(self._entity_jump_targets):
            px, py = self._entity_jump_targets[row]
            self.canvas.center_on_world(px, py, zoom=max(self.canvas.zoom, 1.0))

    def _path_to_selected_entity(self) -> None:
        if self.vm.document is None or not self._entity_jump_targets:
            return
        sel = self.entity_table.selectionModel().selectedRows()
        if not sel:
            return
        row = sel[0].row()
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
    app.setStyleSheet(STUDIO_QSS)
    _install_cjk_fonts(
        app, Path(vm.config.client_root) if vm.config.client_root else None
    )
    window = EditorWindow(vm)
    window.show()
    return app.exec()


__all__ = ["EditorWindow", "LAYERS", "MapCanvas", "NewMapDialog", "run"]
