"""主窗口：设定目录→左侧文件树→双击打开到中间分页网格→单击条目
在右侧预览/检查。多个已打开的包驻留内存（惰性索引，驻留成本低），
切换不重读。

后台任务的回调统一登记在 ``_job_callbacks`` 中、经主窗口的
槽函数分发，保证所有回调都在 GUI 线程执行（直接把普通函数
连接为槽会在工作线程触发，碰 GUI 会挂死）。
"""
from __future__ import annotations

import time
from collections import OrderedDict
from pathlib import Path

from PIL import Image
from PySide6.QtCore import QPoint, QSettings, Qt, QThreadPool
from PySide6.QtGui import QAction, QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..core.codecs.detect import EntryKind
from ..core.codecs.sprite import Sprite, decode_sprite, encode_sprite
from ..core.model.document import PackDocument
from ..core.services import exporter
from ..core.services.saver import save_document
from .dialogs import ReplaceImagesDialog
from .file_tree import DirectoryPanel
from .grid_panel import EntryGridPanel
from .inspector import Inspector
from .preview.animation_bar import AnimationBar
from .preview.sprite_view import MODE_CANVAS, MODE_FRAME, SpriteView
from .preview.text_hex import HexPreview, TextPreview
from .qtutil import pil_to_qimage
from .workers import Job

_ZOOM_ITEMS = [("适应窗口", None), ("50%", 0.5), ("100%", 1.0), ("200%", 2.0),
               ("300%", 3.0), ("400%", 4.0), ("600%", 6.0)]
_THUMB_SIZE = 72
_THUMB_CACHE_MAX = 500


def _key_of(path: str | Path) -> str:
    return str(Path(path).resolve())


def _scan_fls(directory: Path) -> list[Path]:
    """列出目录顶层的 .fls 文件（不含子目录），按文件名排序。"""
    try:
        files = [p for p in directory.iterdir()
                 if p.is_file() and p.suffix.lower() == ".fls"]
    except OSError:
        return []
    return sorted(files, key=lambda p: p.name.lower())


class MainWindow(QMainWindow):
    """资源编辑器主窗口。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MXSJ 资源编辑器")
        self.resize(1240, 800)
        self._settings = QSettings("MXSJ", "resource_editor")
        self._docs: dict[str, PackDocument] = {}
        self._kinds_map: dict[str, list[EntryKind]] = {}
        self._current_key: str | None = None
        self._workspace: Path | None = None
        self._current = -1
        self._sprite: Sprite | None = None
        self._pool = QThreadPool.globalInstance()
        self._render_cache: OrderedDict[int, tuple] = OrderedDict()
        self._thumb_cache: OrderedDict[tuple[str, int], QImage] = OrderedDict()
        self._busy = False
        # 任务回调注册表：以 JobSignals 为键，经槽函数在 GUI 线程分发
        self._job_callbacks: dict[object, tuple] = {}

        self._build_ui()
        self._build_menus()
        self._update_actions()

    # ---------------------------------------------------------- 文档 ----
    @property
    def _doc(self) -> PackDocument | None:
        if self._current_key is None:
            return None
        return self._docs.get(self._current_key)

    # ---------------------------------------------------------- 界面 ----
    def _build_ui(self) -> None:
        self._dir_panel = DirectoryPanel(self)
        self._dir_panel.choose_dir_requested.connect(self.choose_workspace)
        self._dir_panel.refresh_requested.connect(self.refresh_workspace)
        self._dir_panel.file_selected.connect(self._on_file_selected)
        self._dir_panel.file_activated.connect(self.open_pack)
        left = QDockWidget("资源文件", self)
        left.setWidget(self._dir_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, left)

        self._grid = EntryGridPanel(self)
        self._grid.entry_selected.connect(self._select_entry)
        self._grid.page_changed.connect(self._ensure_page_thumbnails)
        per_page = self._settings.value("per_page", 0, int)
        if per_page:
            self._grid.set_per_page(per_page)
        self.setCentralWidget(self._grid)

        right = QDockWidget("预览与检查", self)
        right.setWidget(self._build_right_panel())
        self.addDockWidget(Qt.RightDockWidgetArea, right)
        self.resizeDocks([left, right], [240, 400], Qt.Horizontal)

        self._log = QPlainTextEdit(self)
        self._log.setReadOnly(True)
        self._log.setMaximumBlockCount(800)
        bottom = QDockWidget("日志", self)
        bottom.setWidget(self._log)
        self.addDockWidget(Qt.BottomDockWidgetArea, bottom)

        self._status_label = QLabel("未打开资源包", self)
        self._progress = QProgressBar(self)
        self._progress.setMaximumWidth(220)
        self._progress.hide()
        self.statusBar().addWidget(self._status_label, 1)
        self.statusBar().addPermanentWidget(self._progress)

    def _build_right_panel(self) -> QWidget:
        """右侧栏：上方预览（精灵动画/图片/文本/Hex 切换），下方检查器。"""
        container = QWidget(self)
        splitter = QSplitter(Qt.Vertical, container)

        self._preview_stack = QStackedWidget(splitter)
        self._preview_stack.addWidget(self._build_sprite_page())
        self._text_preview = TextPreview(splitter)
        self._preview_stack.addWidget(self._text_preview)
        self._hex_preview = HexPreview(splitter)
        self._preview_stack.addWidget(self._hex_preview)

        self._inspector = Inspector(splitter)
        self._inspector.frame_chosen.connect(self._on_frame_chosen)
        splitter.addWidget(self._preview_stack)
        splitter.addWidget(self._inspector)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)
        return container

    def _build_sprite_page(self) -> QWidget:
        page = QWidget(self)
        self._mode_box = QComboBox(self)
        self._mode_box.addItem("画布模式", MODE_CANVAS)
        self._mode_box.addItem("帧模式", MODE_FRAME)
        self._mode_box.currentIndexChanged.connect(
            lambda _i: self._sprite_view.set_mode(self._mode_box.currentData()))
        self._zoom_box = QComboBox(self)
        for label, value in _ZOOM_ITEMS:
            self._zoom_box.addItem(label, value)
        self._zoom_box.setCurrentIndex(0)  # 适应窗口（右侧小窗默认）
        self._zoom_box.currentIndexChanged.connect(self._apply_zoom)
        self._anchor_check = QCheckBox("锚点十字", self)
        self._anchor_check.setChecked(True)
        self._anchor_check.toggled.connect(
            lambda on: self._sprite_view.set_show_anchor(on))

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("显示：", self))
        toolbar.addWidget(self._mode_box)
        toolbar.addWidget(QLabel("缩放：", self))
        toolbar.addWidget(self._zoom_box)
        toolbar.addWidget(self._anchor_check)
        toolbar.addStretch(1)

        self._sprite_view = SpriteView(self)
        self._sprite_view.frame_changed.connect(self._on_view_frame)
        self._scroll = QScrollArea(self)
        self._scroll.setWidget(self._sprite_view)
        self._scroll.setAlignment(Qt.AlignCenter)

        self._anim_bar = AnimationBar(self)
        self._anim_bar.frame_requested.connect(self._sprite_view.set_frame)

        layout = QVBoxLayout(page)
        layout.addLayout(toolbar)
        layout.addWidget(self._scroll, 1)
        layout.addWidget(self._anim_bar)
        return page

    def _build_menus(self) -> None:
        file_menu = self.menuBar().addMenu("文件")
        self._act_workspace = self._action("设定工作目录…", "Ctrl+O",
                                           self.choose_workspace)
        self._act_open = self._action("打开资源包…", None,
                                      lambda: self.open_file())
        self._act_save = self._action("保存", "Ctrl+S",
                                      lambda: self.save_file(False))
        self._act_save_as = self._action("另存为…", "Ctrl+Shift+S",
                                         lambda: self.save_file(True))
        self._act_export_entry = self._action("导出当前条目…", None,
                                              self.export_current)
        self._act_export_all = self._action("导出全部精灵…", None,
                                            self.export_all_sprites)
        act_quit = self._action("退出", "Ctrl+Q", self.close)
        for act in (self._act_workspace, self._act_open, self._act_save,
                    self._act_save_as, self._act_export_entry,
                    self._act_export_all, act_quit):
            file_menu.addAction(act)

        edit_menu = self.menuBar().addMenu("编辑")
        self._act_replace_img = self._action("替换图片…", None,
                                             self.replace_images)
        self._act_replace_raw = self._action("替换原始数据…", None,
                                             self.replace_raw)
        self._act_add = self._action("新增条目…", None, self.add_entry)
        self._act_delete = self._action("删除条目", None, self.delete_entry)
        self._act_undo = self._action("撤销条目修改", None, self.undo_entry)
        self._act_revert = self._action("还原条目", None, self.revert_entry)
        for act in (self._act_replace_img, self._act_replace_raw, self._act_add,
                    self._act_delete, self._act_undo, self._act_revert):
            edit_menu.addAction(act)

        about = self._action("关于", None, self._show_about)
        self.menuBar().addMenu("帮助").addAction(about)

    def _action(self, text, shortcut, slot) -> QAction:
        act = QAction(text, self)
        if shortcut:
            act.setShortcut(shortcut)
        act.triggered.connect(slot)
        return act

    # ---------------------------------------------------------- 日志 ----
    def log(self, message: str) -> None:
        stamp = time.strftime("%H:%M:%S")
        self._log.appendPlainText(f"[{stamp}] {message}")

    # ----------------------------------------------------- 工作目录 ----
    def choose_workspace(self) -> None:
        start = str(self._workspace) if self._workspace else ""
        directory = QFileDialog.getExistingDirectory(
            self, "设定工作目录（资源 .fls 所在文件夹）", start)
        if directory:
            self.set_workspace(directory)

    def set_workspace(self, directory: str | Path, remember: bool = True) -> None:
        """设定工作目录并刷新文件树；目录为空/不存在都不报错。"""
        d = Path(directory)
        if not d.is_dir():
            self._workspace = None
            self._dir_panel.set_files(None, [], set())
            self.log(f"目录不存在或不可用：{d}")
            return
        self._workspace = d
        if remember:
            self._settings.setValue("workspace_dir", str(d))
        files = _scan_fls(d)
        modified = {k for k, doc in self._docs.items() if doc.is_modified}
        self._dir_panel.set_files(d, files, modified)
        self.log(f"工作目录：{d}（找到 {len(files)} 个 .fls 文件）")

    def refresh_workspace(self) -> None:
        if self._workspace is not None:
            self.set_workspace(self._workspace, remember=False)

    def restore_workspace(self) -> None:
        """启动时恢复上次的工作目录（没有则空着）。"""
        saved = self._settings.value("workspace_dir", "", str)
        if saved:
            self.set_workspace(saved, remember=False)

    def _on_file_selected(self, key: str) -> None:
        doc = self._docs.get(key)
        note = "（已打开）" if doc is not None else ""
        self.statusBar().showMessage(f"{key}{note}", 4000)

    # ---------------------------------------------------------- 打开 ----
    def open_file(self, path: str | None = None) -> None:
        """打开单个资源包（同时把工作目录切到它所在文件夹）。"""
        if path is None:
            start = str(self._workspace) if self._workspace else ""
            path, _ = QFileDialog.getOpenFileName(
                self, "打开资源包", start, "资源包 (*.fls);;所有文件 (*)")
            if not path:
                return
        p = Path(path)
        if self._workspace is None or _key_of(p.parent) != _key_of(self._workspace):
            self.set_workspace(p.parent)
        self.open_pack(str(p))

    def open_pack(self, path: str) -> None:
        """把资源包打开到中间网格（已打开过的直接切换，不重读）。"""
        key = _key_of(path)
        if key in self._docs:
            self._activate_pack(key)
            return
        if self._busy:
            return
        p = Path(path)

        def job(progress):
            doc = PackDocument.open(p)
            kinds = []
            for i in range(doc.count):
                kinds.append(doc.entry_kind(i))
                if i % 250 == 0:
                    progress(i, doc.count)
            progress(doc.count, doc.count)
            return doc, kinds

        def done(result) -> None:
            doc, kinds = result
            self._docs[key] = doc
            self._kinds_map[key] = kinds
            self.log(f"已打开 {doc.path}：{doc.count} 个条目")
            self._activate_pack(key)

        self._run_job(Job(job, "打开资源包"), done)

    def _activate_pack(self, key: str) -> None:
        doc = self._docs[key]
        self._current_key = key
        self._current = -1
        self._sprite = None
        self._render_cache.clear()
        self._grid.set_document(doc, self._kinds_map[key])
        self._dir_panel.select_file(key)
        name = doc.path.name if doc.path else "未命名"
        self.setWindowTitle(f"{name} — MXSJ 资源编辑器")
        self._inspector.clear()
        self._sprite_view.clear()
        self._update_actions()
        if doc.count:
            self._grid.select_entry(0)
            self._select_entry(0)
        else:
            self._ensure_page_thumbnails()

    # -------------------------------------------------------- 缩略图 ----
    def _ensure_page_thumbnails(self) -> None:
        doc = self._doc
        key = self._current_key
        if doc is None or key is None:
            return
        entries = [i for i in self._grid.page_entries()
                   if (key, i) not in self._thumb_cache]
        self._apply_cached_icons()
        if not entries:
            return

        def job(_progress):
            thumbs: dict[int, QImage] = {}
            for i in entries:
                try:
                    kind = doc.entry_kind(i)
                    if kind is EntryKind.SPRITE:
                        sprite = decode_sprite(doc.content(i))
                        img = sprite.render_frame(0)
                        img.thumbnail((_THUMB_SIZE, _THUMB_SIZE),
                                      Image.NEAREST)
                        thumbs[i] = pil_to_qimage(img)
                    elif kind is EntryKind.PNG:
                        qimg = QImage.fromData(doc.content(i))
                        thumbs[i] = qimg.scaled(
                            _THUMB_SIZE, _THUMB_SIZE,
                            Qt.KeepAspectRatio, Qt.FastTransformation)
                except Exception:
                    pass  # 缩略图失败不影响浏览，占位图即可
            return thumbs

        j = Job(job, "生成缩略图")
        self._register_job(
            j, lambda thumbs: self._on_thumbnails(key, thumbs),
            on_error=lambda _t: None)

    def _apply_cached_icons(self) -> None:
        key = self._current_key
        if key is None:
            return
        icons = {}
        for i in self._grid.page_entries():
            img = self._thumb_cache.get((key, i))
            if img is not None:
                self._thumb_cache.move_to_end((key, i))
                icons[i] = QIcon(QPixmap.fromImage(img))
        if icons:
            self._grid.set_icons(icons)

    def _on_thumbnails(self, key: str, thumbs: dict) -> None:
        for index, image in thumbs.items():
            self._thumb_cache[(key, index)] = image
            self._thumb_cache.move_to_end((key, index))
        while len(self._thumb_cache) > _THUMB_CACHE_MAX:
            self._thumb_cache.popitem(last=False)
        if key == self._current_key:
            self._apply_cached_icons()

    # ---------------------------------------------------------- 选中 ----
    def _select_entry(self, index: int) -> None:
        doc = self._doc
        if doc is None or not 0 <= index < doc.count:
            return
        self._current = index
        kind = doc.entry_kind(index)
        self._anim_bar.stop()
        if kind is EntryKind.SPRITE:
            self._show_sprite(index)
        elif kind is EntryKind.PNG:
            self._sprite = None
            self._inspector.set_entry(doc, index, None)
            qimg = QImage.fromData(doc.content(index))
            self._sprite_view.set_image(qimg)
            self._apply_zoom()
            self._anim_bar.set_frame_count(1)
            self._preview_stack.setCurrentIndex(0)
        elif kind in (EntryKind.JSON, EntryKind.TEXT):
            self._sprite = None
            self._inspector.set_entry(doc, index, None)
            self._text_preview.set_content(doc.content(index))
            self._preview_stack.setCurrentIndex(1)
        else:
            self._sprite = None
            self._inspector.set_entry(doc, index, None)
            note = ("zlib 包装的脚本数据（内层含 XOR，编辑器不解码）"
                    if kind is EntryKind.SCRIPT else "")
            self._hex_preview.set_content(doc.content(index), note)
            self._preview_stack.setCurrentIndex(2)
        self._update_actions()

    def _show_sprite(self, index: int) -> None:
        doc = self._doc
        assert doc is not None
        cached = self._render_cache.get(index)
        if cached is not None:
            self._render_cache.move_to_end(index)
            self._apply_sprite_bundle(index, cached)
            return

        def job(_progress):
            sprite = decode_sprite(doc.content(index))
            frames = [pil_to_qimage(sprite.render_frame(fi))
                      for fi in range(sprite.frame_count)]
            canvas = [pil_to_qimage(sprite.render_canvas_frame(fi))
                      for fi in range(sprite.frame_count)]
            offsets = [QPoint(*sprite.frame_offset(fi))
                       for fi in range(sprite.frame_count)]
            center = QPoint(sprite.center_x, sprite.center_y)
            return sprite, (frames, canvas, offsets, center)

        j = Job(job, "解码精灵")
        self._register_job(
            j, lambda bundle: self._on_sprite_decoded(index, bundle))

    def _on_sprite_decoded(self, index: int, bundle) -> None:
        self._render_cache[index] = bundle
        while len(self._render_cache) > 8:
            self._render_cache.popitem(last=False)
        if index == self._current:
            self._apply_sprite_bundle(index, bundle)

    def _apply_sprite_bundle(self, index: int, bundle) -> None:
        sprite, (frames, canvas, offsets, center) = bundle
        self._sprite = sprite
        if self._doc is not None:
            self._inspector.set_entry(self._doc, index, sprite)
        self._sprite_view.set_content(frames, canvas, offsets, center)
        self._sprite_view.set_mode(self._mode_box.currentData())
        self._apply_zoom()
        self._anim_bar.set_frame_count(sprite.frame_count)
        self._preview_stack.setCurrentIndex(0)

    def _on_frame_chosen(self, frame: int) -> None:
        if frame < 0:
            return
        self._anim_bar.stop()
        self._sprite_view.set_frame(frame)
        self._anim_bar.set_current(frame)

    def _on_view_frame(self, frame: int) -> None:
        self._anim_bar.set_current(frame)
        self._inspector.set_current_frame(frame)

    def _apply_zoom(self) -> None:
        value = self._zoom_box.currentData()
        if value is None:  # 适应窗口
            self._sprite_view.set_fit(self._scroll.viewport().size())
        else:
            self._sprite_view.set_scale(float(value))

    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt 命名)
        super().resizeEvent(event)
        if hasattr(self, "_zoom_box") and self._zoom_box.currentData() is None:
            self._apply_zoom()

    # ---------------------------------------------------------- 编辑 ----
    def replace_images(self) -> None:
        if self._doc is None or self._sprite is None or self._current < 0:
            return
        sprite = self._sprite
        index = self._current
        dialog = ReplaceImagesDialog(
            self, sprite, self._sprite_view.current_frame)
        if dialog.exec() != dialog.Accepted:
            return
        paths = dialog.file_paths
        current_frame = self._sprite_view.current_frame
        use_base = dialog.use_base_palette

        def job(_progress):
            new_images = [Image.open(p).convert("RGBA") for p in paths]
            if len(new_images) == sprite.frame_count:
                frames = new_images
            else:  # 1 张：只换当前帧，其余帧由现图重编码（像素无损）
                frames = [sprite.render_frame(fi)
                          for fi in range(sprite.frame_count)]
                frames[current_frame] = new_images[0]
            keys = [(f[0], f[1]) for f in sprite.frames]
            encoded, _pal, report = encode_sprite(
                frames, keys, sprite.canvas_w, sprite.canvas_h,
                sprite.center_x, sprite.center_y,
                magic=sprite.magic,
                base_palette=sprite.palette if use_base else None,
            )
            return encoded, report

        j = Job(job, "编码精灵")
        self._register_job(
            j, lambda result: self._confirm_replace(index, result))

    def _confirm_replace(self, index: int, result) -> None:
        encoded, report = result
        detail = (
            f"往返误差：最大颜色差 {report.max_rgb_error}，"
            f"平均 {report.mean_rgb_error:.2f}，"
            f"最大 alpha 差 {report.max_alpha_error}，"
            f"超差像素 {report.pixels_over_tolerance}/{report.total_pixels}。\n"
            "确认把编码结果写入条目？（保存到文件前仍可撤销）"
        )
        if QMessageBox.question(self, "替换图片", detail) != QMessageBox.Yes:
            self.log("已取消替换图片")
            return
        assert self._doc is not None
        self._doc.replace_content(index, encoded)
        self.log(f"条目 {index} 已替换图片，新大小 {len(encoded)} 字节")
        self._after_entry_changed(index)

    def replace_raw(self) -> None:
        if self._doc is None or self._current < 0:
            return
        path, _ = QFileDialog.getOpenFileName(self, "选择原始数据文件")
        if not path:
            return
        data = Path(path).read_bytes()
        index = self._current
        if QMessageBox.question(
            self, "替换原始数据",
            f"用所选文件（{len(data)} 字节）替换条目 {index} 的内容？",
        ) != QMessageBox.Yes:
            return
        self._doc.replace_content(index, data)
        self.log(f"条目 {index} 已替换原始数据")
        self._after_entry_changed(index)

    def add_entry(self) -> None:
        if self._doc is None:
            return
        path, _ = QFileDialog.getOpenFileName(self, "选择要新增的文件")
        if not path:
            return
        name = None
        if self._doc.kind != "0slf":
            name, ok = QInputDialog.getText(
                self, "新增条目", "新条目文件名（如 sub\\mod.pyo）：")
            if not ok or not name:
                return
        index = self._doc.add_entry(Path(path).read_bytes(), name)
        self.log(f"已新增条目 {index}")
        self._reload_grid(select=index)

    def delete_entry(self) -> None:
        if self._doc is None or self._current < 0:
            return
        index = self._current
        if QMessageBox.question(
            self, "删除条目", f"确认删除条目 {index}？",
        ) != QMessageBox.Yes:
            return
        self._doc.delete_entry(index)
        self._render_cache.clear()
        # 序号整体移位：该包的缩略图缓存失效
        if self._current_key is not None:
            key = self._current_key
            self._thumb_cache = OrderedDict(
                (k, v) for k, v in self._thumb_cache.items() if k[0] != key)
        self.log(f"已删除条目 {index}")
        nxt = min(index, self._doc.count - 1)
        self._reload_grid(select=nxt)

    def undo_entry(self) -> None:
        if self._doc is None or self._current < 0:
            return
        if self._doc.undo(self._current):
            self.log(f"条目 {self._current} 已撤销一次修改")
            self._after_entry_changed(self._current)
        else:
            self.log("该条目没有可撤销的修改")

    def revert_entry(self) -> None:
        if self._doc is None or self._current < 0:
            return
        self._doc.revert(self._current)
        self.log(f"条目 {self._current} 已还原为打开时状态")
        self._after_entry_changed(self._current)

    def _after_entry_changed(self, index: int) -> None:
        assert self._doc is not None and self._current_key is not None
        self._render_cache.pop(index, None)
        self._thumb_cache.pop((self._current_key, index), None)
        kinds = self._kinds_map[self._current_key]
        if 0 <= index < len(kinds):
            kinds[index] = self._doc.entry_kind(index)
        self._grid.refresh_entry(index)
        self._select_entry(index)
        self._sync_doc_marks()
        self._update_actions()

    def _reload_grid(self, select: int = -1) -> None:
        doc = self._doc
        assert doc is not None and self._current_key is not None
        kinds = [doc.entry_kind(i) for i in range(doc.count)]
        self._kinds_map[self._current_key] = kinds
        self._grid.set_document(doc, kinds)
        self._sync_doc_marks()
        if 0 <= select < doc.count:
            self._current = -1
            self._grid.select_entry(select)
            self._select_entry(select)
        elif doc.count == 0:
            self._current = -1
            self._inspector.clear()
        self._update_actions()

    # ---------------------------------------------------------- 导出 ----
    def export_current(self) -> None:
        if self._doc is None or self._current < 0:
            return
        out = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not out:
            return
        doc, index = self._doc, self._current
        self._run_job(
            Job(lambda _p: exporter.export_entry(doc, index, Path(out)),
                "导出条目"),
            lambda paths: self.log(f"条目 {index} 已导出到 {out}"),
        )

    def export_all_sprites(self) -> None:
        if self._doc is None:
            return
        out = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not out:
            return
        doc = self._doc
        self._run_job(
            Job(lambda _p: exporter.export_all_sprites(doc, Path(out)),
                "导出全部精灵"),
            lambda count: self.log(f"已导出 {count} 个精灵到 {out}"),
        )

    # ---------------------------------------------------------- 保存 ----
    def save_file(self, save_as: bool) -> None:
        if self._doc is None or self._busy:
            return
        doc = self._doc
        old_key = self._current_key
        target = None if save_as else doc.path
        if target is None:
            path, _ = QFileDialog.getSaveFileName(
                self, "保存资源包", "", "资源包 (*.fls);;所有文件 (*)")
            if not path:
                return
            target = Path(path)

        def job(progress):
            return save_document(doc, target, progress)

        def done(report) -> None:
            self._docs.pop(old_key, None)
            if old_key is not None:
                self._kinds_map.pop(old_key, None)
            new_key = _key_of(target)
            self._docs[new_key] = doc
            self._kinds_map[new_key] = [doc.entry_kind(i)
                                        for i in range(doc.count)]
            self._current_key = new_key
            if save_as:
                self.set_workspace(target.parent)
            self._dir_panel.select_file(new_key)
            self._grid.refresh_header()
            backup = target.with_suffix(target.suffix + ".bak")
            note = f"，原文件备份为 {backup.name}" if backup.exists() else ""
            self.log(
                f"已保存到 {target}（校验通过，试解码精灵 "
                f"{report.sprite_checked} 个{note}）")
            self.setWindowTitle(f"{target.name} — MXSJ 资源编辑器")
            self._sync_doc_marks()
            self._update_actions()

        self._run_job(Job(job, "保存资源包"), done)

    def _sync_doc_marks(self) -> None:
        doc = self._doc
        if doc is not None and self._current_key is not None:
            self._dir_panel.set_modified(
                self._current_key, doc.is_modified)
            self._grid.refresh_header()

    # ---------------------------------------------------------- 任务 ----
    def _register_job(self, job: Job, on_finished, on_error=None) -> None:
        """登记任务回调并启动；回调经主窗口槽在 GUI 线程分发。"""
        self._job_callbacks[job.signals] = (
            on_finished, on_error or self._on_job_error)
        job.signals.finished.connect(self._dispatch_finished)
        job.signals.error.connect(self._dispatch_error)
        job.signals.progress.connect(self._on_progress)
        self._pool.start(job)

    def _dispatch_finished(self, result) -> None:
        self._busy = False
        self._progress.hide()
        on_finished, _on_err = self._job_callbacks.pop(
            self.sender(), (None, None))
        if on_finished is not None:
            on_finished(result)

    def _dispatch_error(self, text: str) -> None:
        self._busy = False
        self._progress.hide()
        _on_fin, on_error = self._job_callbacks.pop(
            self.sender(), (None, self._on_job_error))
        on_error(text)

    def _run_job(self, job: Job, on_finished) -> None:
        """带忙碌状态与进度条的任务启动（打开/保存/导出用）。"""
        self._busy = True
        self._progress.setRange(0, 0)
        self._progress.show()
        self._register_job(job, on_finished)

    def _on_progress(self, done: int, total: int) -> None:
        if total > 0:
            self._progress.setRange(0, total)
            self._progress.setValue(done)

    def _on_job_error(self, text: str) -> None:
        first = text.strip().splitlines()[-1] if text.strip() else "未知错误"
        self.log(f"操作失败：{first}")
        QMessageBox.critical(self, "操作失败", first)

    # ---------------------------------------------------------- 状态 ----
    def _update_actions(self) -> None:
        has_doc = self._doc is not None
        has_entry = has_doc and self._current >= 0
        is_sprite = (
            has_entry and self._doc is not None
            and self._doc.entry_kind(self._current) is EntryKind.SPRITE)
        self._act_save.setEnabled(has_doc)
        self._act_save_as.setEnabled(has_doc)
        self._act_export_entry.setEnabled(has_entry)
        self._act_export_all.setEnabled(has_doc)
        self._act_replace_img.setEnabled(is_sprite)
        self._act_replace_raw.setEnabled(has_entry)
        self._act_add.setEnabled(has_doc)
        self._act_delete.setEnabled(has_entry)
        self._act_undo.setEnabled(has_entry)
        self._act_revert.setEnabled(has_entry)
        if has_doc:
            assert self._doc is not None
            dirty = self._doc.dirty_count
            self._status_label.setText(
                f"{self._doc.path.name if self._doc.path else '未命名'} · "
                f"{self._doc.count} 个条目 · 容器 {self._doc.kind} · "
                f"已修改 {dirty} 条")

    def _show_about(self) -> None:
        QMessageBox.about(
            self, "关于",
            "MXSJ 资源编辑器 0.2.0\n"
            "梦想世界客户端 FLS 资源包浏览与编辑工具。\n"
            "目录式工作区 + 分页网格浏览 + 惰性加载（大包秒开）。\n"
            "精灵格式 I0/T0/I1 规格见 tools/data-parser/I0_SPRITE_FORMAT.md。")

    # ---------------------------------------------------------- 事件 ----
    def keyPressEvent(self, event) -> None:  # noqa: N802 (Qt 命名)
        if (event.key() == Qt.Key_Space and self._sprite is not None
                and not isinstance(self.focusWidget(),
                                   (QLineEdit, QPlainTextEdit, QSpinBox))):
            self._anim_bar.toggle_play()
            event.accept()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt 命名)
        modified = [doc.path.name if doc.path else "未命名"
                    for doc in self._docs.values() if doc.is_modified]
        if modified:
            names = "、".join(modified[:5])
            more = f" 等 {len(modified)} 个包" if len(modified) > 5 else ""
            answer = QMessageBox.question(
                self, "退出",
                f"以下资源包有未保存的修改：{names}{more}，确认退出？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if answer != QMessageBox.Yes:
                event.ignore()
                return
        self._settings.setValue("per_page", self._grid.per_page)
        for doc in self._docs.values():
            doc.close()
        super().closeEvent(event)
