"""PySide6 widgets — a thin binding over :mod:`map_editor.ui.viewmodel`.

Everything that decides *what* to show lives in the view model; this module only
translates user actions into view-model calls and view-model state into pixels.

Rendering is tiled and lazy.  A tile is exactly one map sector (320x240), which
matches the on-disk unit, so painting a viewport decodes only the sectors it
actually covers.  An LRU keeps recently decoded tiles so panning stays smooth.
For the largest scenes in the client (10000x6000, 800 sectors) decoding the whole
map up front would need ~180 MB of RGB, which is why this is not optional.

This is the only module that imports Qt.  ``tests/test_viewmodel_headless.py``
asserts that the rest of the package does not, so the model stays runnable where
``QtWidgets`` cannot even be imported.
"""
from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QCheckBox, QDoubleSpinBox, QFileDialog,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel, QMainWindow, QMessageBox,
    QPushButton, QScrollArea, QSpinBox, QTableWidget, QTableWidgetItem,
    QToolBar, QVBoxLayout, QWidget,
)

from ..client.config import Config
from ..client.discovery import DiscoveryError
from ..core.mapfile import CELL_PX, SECTOR_PX_H, SECTOR_PX_W, MapFormatError
from .viewmodel import LAYERS, EditorViewModel

TILE_CACHE_SIZE = 96
LAYER_LABELS = {
    "texture": "底图 (GEPJ)",
    "grid": "LLEC 网格 (20px)",
    "records": "空间记录框",
    "sector_bounds": "扇区边界 (320x240)",
}
COLUMNS = ("编号", "名称", "尺寸", "扇区", "记录", "文件大小", "状态")
MAX_VIEW_DIMENSION = 20000      # Qt will not rasterise a widget larger than this


class MapCanvas(QWidget):
    """Paints the current map with the enabled overlays."""

    def __init__(self, vm: EditorViewModel) -> None:
        super().__init__()
        self.vm = vm
        self.zoom = 1.0
        self._cache: "OrderedDict[tuple[int, int], QImage]" = OrderedDict()
        self.setMinimumSize(1, 1)
        self.setMouseTracking(True)

    # -- geometry ---------------------------------------------------------
    def map_size(self) -> QSize:
        w, h = self.vm.state.current_size
        return QSize(int(w * self.zoom), int(h * self.zoom))

    def refresh_geometry(self) -> None:
        size = self.map_size()
        self.setFixedSize(max(1, size.width()), max(1, size.height()))
        self.update()

    def set_zoom(self, zoom: float) -> None:
        self.zoom = max(0.05, min(8.0, zoom))
        self.refresh_geometry()

    def invalidate(self) -> None:
        self._cache.clear()
        self.refresh_geometry()

    # -- tiles ------------------------------------------------------------
    def _tile(self, col: int, row: int) -> QImage | None:
        key = (col, row)
        hit = self._cache.get(key)
        if hit is not None:
            self._cache.move_to_end(key)
            return hit
        doc = self.vm.document
        if doc is None:
            return None
        cols = doc.header.sector_columns
        index = row * cols + col
        if index >= doc.header.sector_count:
            return None
        try:
            sector = doc.sector(index)
            img = self.vm.render(sector.origin_x, sector.origin_y,
                                 sector.origin_x + SECTOR_PX_W,
                                 sector.origin_y + SECTOR_PX_H)
        except (MapFormatError, OSError):
            return None
        # Copy the buffer: QImage.fromData would alias it, frombytes would not.
        qimg = QImage(bytes(img.data), img.width, img.height,
                      img.width * 3, QImage.Format_RGB888).copy()
        self._cache[key] = qimg
        while len(self._cache) > TILE_CACHE_SIZE:
            self._cache.popitem(last=False)
        return qimg

    # -- painting ---------------------------------------------------------
    def paintEvent(self, event) -> None:          # noqa: N802 (Qt naming)
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(28, 28, 30))
        doc = self.vm.document
        if doc is None:
            painter.setPen(QColor(180, 180, 180))
            painter.drawText(self.rect(), Qt.AlignCenter,
                             "请在左侧选择客户端目录，然后双击一张地图")
            painter.end()
            return

        width, height = doc.header.width, doc.header.height
        scaled = self.zoom != 1.0
        if scaled:
            painter.scale(self.zoom, self.zoom)
        visible = event.rect()
        if scaled:
            visible = QRect(int(visible.x() / self.zoom), int(visible.y() / self.zoom),
                            int(visible.width() / self.zoom) + 2,
                            int(visible.height() / self.zoom) + 2)
        if not self.vm.layer("texture"):
            painter.fillRect(QRect(0, 0, width, height), QColor(16, 16, 18))

        cols = (visible.right() // SECTOR_PX_W) + 1
        rows = (visible.bottom() // SECTOR_PX_H) + 1
        for row in range(max(0, visible.y() // SECTOR_PX_H), rows):
            for col in range(max(0, visible.x() // SECTOR_PX_W), cols):
                if self.vm.layer("texture"):
                    tile = self._tile(col, row)
                    if tile is not None:
                        painter.drawImage(col * SECTOR_PX_W, row * SECTOR_PX_H, tile)

        if self.vm.layer("sector_bounds"):
            painter.setPen(QPen(QColor(255, 255, 0, 90), max(1.0, 1.0 / self.zoom)))
            for c in range(doc.header.sector_columns + 1):
                painter.drawLine(c * SECTOR_PX_W, 0, c * SECTOR_PX_W, height)
            for r in range(doc.header.sector_rows + 1):
                painter.drawLine(0, r * SECTOR_PX_H, width, r * SECTOR_PX_H)

        if self.vm.layer("grid"):
            painter.setPen(QPen(QColor(0, 220, 255, 70), max(1.0, 1.0 / self.zoom)))
            for c in range(0, width, CELL_PX):
                painter.drawLine(c, 0, c, height)
            for r in range(0, height, CELL_PX):
                painter.drawLine(0, r, width, r)

        if self.vm.layer("records"):
            painter.setPen(QPen(QColor(255, 90, 90, 220), max(1.0, 2.0 / self.zoom)))
            for rec in doc.records:
                painter.drawRect(rec.x, rec.y, rec.width, rec.height)

        cursor = self.vm.state.cursor
        if cursor:
            painter.setPen(QPen(QColor(0, 255, 120, 230), max(1.0, 2.0 / self.zoom)))
            painter.drawRect(cursor[0] // CELL_PX * CELL_PX,
                             cursor[1] // CELL_PX * CELL_PX, CELL_PX, CELL_PX)
        painter.end()

    # -- interaction ------------------------------------------------------
    def mouseMoveEvent(self, event) -> None:     # noqa: N802
        doc = self.vm.document
        if doc is not None:
            x = int(event.position().x() / self.zoom)
            y = int(event.position().y() / self.zoom)
            info = self.vm.locate(x, y)
            self.vm.state.status = (
                f"像素 {x},{y} · 格 {info['cell'][0]},{info['cell'][1]}"
                + (f" · 扇区 {info['sector']}" if "sector" in info else "")
                + (f" · LLEC={info['cell_value']}" if info["cell_value"] is not None else ""))
            window = self.window()
            if isinstance(window, EditorWindow):
                window.set_cursor_status(self.vm.state.status)
            self.update()
        super().mouseMoveEvent(event)


class EditorWindow(QMainWindow):
    """Main window: client path, map list, layer toggles, locate, export."""

    def __init__(self, vm: EditorViewModel | None = None) -> None:
        super().__init__()
        self.vm = vm if vm is not None else EditorViewModel()
        self.setWindowTitle("夢想世界 地图编辑器 (第一期 · 只读)")
        self.resize(1440, 900)
        self._build_ui()
        self._restore_config()

    # -- construction -----------------------------------------------------
    def _build_ui(self) -> None:
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        self.act_pick = toolbar.addAction("选择客户端目录…", self.pick_client_root)
        toolbar.addSeparator()
        self.act_rescan = toolbar.addAction("重新扫描", self.rescan)
        toolbar.addSeparator()
        self.act_png = toolbar.addAction("导出 PNG…", self.export_png)
        self.act_json = toolbar.addAction("导出 JSON…", self.export_json)
        for act in (self.act_rescan, self.act_png, self.act_json):
            act.setEnabled(False)

        # left panel ------------------------------------------------------
        panel = QWidget()
        layout = QVBoxLayout(panel)

        layout.addWidget(QLabel("客户端根目录（地图会被递归搜索）"))
        row = QHBoxLayout()
        self.edit_root = QLabel("（未设置）")
        self.edit_root.setWordWrap(True)
        self.edit_root.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.btn_browse = QPushButton("浏览…")
        self.btn_browse.clicked.connect(self.pick_client_root)
        row.addWidget(self.edit_root, 1)
        row.addWidget(self.btn_browse)
        layout.addLayout(row)

        layout.addWidget(QLabel("地图列表（双击打开）"))
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.itemDoubleClicked.connect(lambda *_: self.open_selected())
        layout.addWidget(self.table, 1)

        self.btn_open = QPushButton("打开选中地图")
        self.btn_open.clicked.connect(self.open_selected)
        layout.addWidget(self.btn_open)

        box = QGroupBox("图层")
        bl = QVBoxLayout(box)
        self.layer_boxes: dict[str, QCheckBox] = {}
        for name in LAYERS:
            cb = QCheckBox(LAYER_LABELS.get(name, name))
            cb.setChecked(self.vm.layer(name))
            cb.toggled.connect(lambda on, n=name: self.toggle_layer(n, on))
            self.layer_boxes[name] = cb
            bl.addWidget(cb)
        layout.addWidget(box)

        locate = QGroupBox("坐标定位")
        ll = QHBoxLayout(locate)
        self.spin_x = QSpinBox()
        self.spin_y = QSpinBox()
        self.spin_x.setRange(-1, MAX_VIEW_DIMENSION)
        self.spin_y.setRange(-1, MAX_VIEW_DIMENSION)
        ll.addWidget(QLabel("X"))
        ll.addWidget(self.spin_x)
        ll.addWidget(QLabel("Y"))
        ll.addWidget(self.spin_y)
        btn = QPushButton("定位")
        btn.clicked.connect(self.do_locate)
        ll.addWidget(btn)
        layout.addWidget(locate)

        zoom = QHBoxLayout()
        zoom.addWidget(QLabel("缩放"))
        self.spin_zoom = QDoubleSpinBox()
        self.spin_zoom.setRange(0.05, 8.0)
        self.spin_zoom.setSingleStep(0.25)
        self.spin_zoom.setValue(1.0)
        self.spin_zoom.valueChanged.connect(self.set_zoom)
        zoom.addWidget(self.spin_zoom)
        layout.addLayout(zoom)

        self.dock = QWidget()
        self.dock.setLayout(layout)
        self.dock.setMaximumWidth(520)
        self.setCentralWidget(QWidget())
        outer = QHBoxLayout(self.centralWidget())
        outer.addWidget(self.dock)

        self.canvas = MapCanvas(self.vm)
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.canvas)
        self.scroll.setWidgetResizable(False)
        outer.addWidget(self.scroll, 1)

        self.status = self.statusBar()
        self.lbl_status = QLabel("未选择客户端目录")
        self.lbl_cursor = QLabel("")
        self.status.addWidget(self.lbl_status, 1)
        self.status.addPermanentWidget(self.lbl_cursor)

    def _restore_config(self) -> None:
        root = self.vm.config.client_root
        if root and Path(root).is_dir():
            self.edit_root.setText(root)
            try:
                self.vm.set_client_root(root)
                self._refresh_table()
            except DiscoveryError as exc:
                self.lbl_status.setText(f"上次目录不可用: {exc}")

    # -- actions ----------------------------------------------------------
    def pick_client_root(self) -> None:
        start = self.vm.config.client_root or str(Path.home())
        chosen = QFileDialog.getExistingDirectory(self, "选择《夢想世界》客户端根目录", start)
        if not chosen:
            return
        self.edit_root.setText(chosen)
        try:
            self.vm.set_client_root(chosen, progress=self.lbl_status.setText)
        except DiscoveryError as exc:
            QMessageBox.warning(self, "无法扫描", str(exc))
            return
        self._refresh_table()
        self.vm.save_config()

    def rescan(self) -> None:
        if self.vm.config.client_root:
            try:
                self.vm.set_client_root(self.vm.config.client_root,
                                        progress=self.lbl_status.setText)
                self._refresh_table()
            except DiscoveryError as exc:
                QMessageBox.warning(self, "无法扫描", str(exc))

    def _refresh_table(self) -> None:
        rows = self.vm.rows
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            values = (
                r.key, r.name or "—",
                f"{r.width}x{r.height}" if r.width else "—",
                str(r.sectors) if r.sectors else "—",
                "—",
                f"{r.size / 1024:.0f} KB",
                "解析失败" if r.broken else "OK",
            )
            for c, text in enumerate(values):
                item = QTableWidgetItem(text)
                if r.broken:
                    item.setToolTip(r.error)
                self.table.setItem(i, c, item)
            if r.width:
                meta = self.vm.scenes.get(r.key)
                if meta and meta.name:
                    self.table.item(i, 1).setToolTip(
                        meta.minimap_name or meta.name)
        self.act_rescan.setEnabled(True)
        self.lbl_status.setText(self.vm.status_line())

    def open_selected(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.vm.rows):
            return
        target = self.vm.rows[row]
        try:
            self.vm.open_map(target)
        except (MapFormatError, KeyError, OSError) as exc:
            QMessageBox.warning(self, "无法打开地图", str(exc))
            return
        w, h = self.vm.state.current_size
        self.spin_x.setRange(0, max(0, w - 1))
        self.spin_y.setRange(0, max(0, h - 1))
        self.canvas.invalidate()
        self.act_png.setEnabled(True)
        self.act_json.setEnabled(True)
        self.setWindowTitle(
            f"{self.vm.state.current_key} {self.vm.state.current_name} "
            f"{w}x{h} — 夢想世界 地图编辑器 (只读)")
        self.lbl_status.setText(self.vm.status_line())

    def toggle_layer(self, name: str, on: bool) -> None:
        self.vm.set_layer(name, on)
        self.canvas.update()
        self.vm.save_config()

    def set_zoom(self, value: float) -> None:
        self.canvas.set_zoom(float(value))

    def do_locate(self) -> None:
        if self.vm.document is None:
            QMessageBox.information(self, "尚未打开地图", "请先在列表中双击一张地图。")
            return
        info = self.vm.locate(self.spin_x.value(), self.spin_y.value())
        text = (f"像素 {info['x']},{info['y']} → 格 {info['cell'][0]},{info['cell'][1]}"
                f"，LLEC 原始值 = {info['cell_value']}")
        if "sector" in info:
            text += f"，扇区 {info['sector']}（第 {info['sector_cell'][1]} 行第 " \
                    f"{info['sector_cell'][0]} 列）"
        QMessageBox.information(self, "定位结果", text)
        self.canvas.update()

    def set_cursor_status(self, text: str) -> None:
        self.lbl_cursor.setText(text)

    def export_png(self) -> None:
        if self.vm.document is None:
            return
        doc = self.vm.document
        default = f"{self.vm.state.current_key}_{doc.header.width}x{doc.header.height}.png"
        dest, _ = QFileDialog.getSaveFileName(self, "导出 PNG", default, "PNG 图片 (*.png)")
        if not dest:
            return
        if doc.header.width * doc.header.height > 40_000_000:
            ok = QMessageBox.question(
                self, "文件很大",
                f"整图为 {doc.header.width}x{doc.header.height}（约 "
                f"{doc.header.width * doc.header.height / 1_000_000:.0f} 百万像素），"
                "导出可能耗时较久。继续？")
            if ok != QMessageBox.Yes:
                return
        try:
            self.lbl_status.setText("正在导出 PNG…")
            QApplication.processEvents()
            path = self.vm.export_png(dest)
        except Exception as exc:
            QMessageBox.warning(self, "导出失败", str(exc))
            return
        self.lbl_status.setText(f"已导出 {path}")

    def export_json(self) -> None:
        if self.vm.document is None:
            return
        default = f"{self.vm.state.current_key}_map.json"
        dest, _ = QFileDialog.getSaveFileName(self, "导出 JSON", default, "JSON (*.json)")
        if not dest:
            return
        try:
            path = self.vm.export_json(dest)
        except Exception as exc:
            QMessageBox.warning(self, "导出失败", str(exc))
            return
        self.lbl_status.setText(f"已导出 {path}")

    def closeEvent(self, event) -> None:        # noqa: N802
        try:
            self.vm.config.window = {"w": self.width(), "h": self.height()}
            self.vm.save_config()
            self.vm.close_map()
        finally:
            super().closeEvent(event)


def run(vm: EditorViewModel | None = None) -> int:
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("MXSJ Map Editor")
    window = EditorWindow(vm)
    geo = (vm or window.vm).config.window
    if geo.get("w") and geo.get("h"):
        window.resize(int(geo["w"]), int(geo["h"]))
    window.show()
    return app.exec()


__all__ = ["EditorWindow", "MapCanvas", "run"]
