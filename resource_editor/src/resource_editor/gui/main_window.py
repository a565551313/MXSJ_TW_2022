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
from PySide6.QtCore import QPoint, QSettings, QSize, Qt, QThreadPool
from PySide6.QtGui import QAction, QIcon, QImage, QKeySequence, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..core.changes import counts
from ..core.codecs.detect import EntryKind
from ..core.codecs.sprite import Sprite, decode_sprite, encode_sprite
from ..core.model.document import PackDocument
from ..core.output_paths import guard_output
from ..core.services import exporter
from ..core.services.saver import save_document
from . import icons
from .dialogs import ReplaceImagesDialog
from .file_tree import DirectoryPanel
from .grid_panel import EntryGridPanel
from .inspector import Inspector
from .preview.animation_bar import AnimationBar
from .preview.audio_preview import AudioPreview
from .preview.sprite_view import MODE_CANVAS, MODE_FRAME, SpriteView
from .preview.text_hex import HexPreview, TextPreview
from .qtutil import pil_to_qimage
from .resource_path_dialog import ResourcePathDialog
from .save_review import SaveReviewDialog
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
        self._blocking_job = None
        self._preview_epoch = 0
        # 任务回调注册表：以 JobSignals 为键，经槽函数在 GUI 线程分发
        self._job_callbacks: dict[object, tuple] = {}

        self._build_ui()
        self._build_menus()
        self._build_toolbar()
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
        self._grid.selection_changed.connect(
            lambda _n: self._update_actions())
        self._grid.context_menu_requested.connect(
            self._show_grid_context_menu)
        find = QShortcut("Ctrl+F", self)
        find.activated.connect(self._grid.focus_search)
        per_page = self._settings.value("per_page", 0, int)
        if per_page:
            self._grid.set_per_page(per_page)
        self.setCentralWidget(self._grid)
        self._history_list = QListWidget()
        self._history_list.setToolTip(
            "当前包的只读时间线；用 Ctrl+Z / Ctrl+Y 逐步回退/重做。最多 50 步，"
            "64 MiB 增量预算（超大单步保留一条）；批量导入算一步。")
        history_dock = QDockWidget("操作历史（当前包）", self)
        history_dock.setWidget(self._history_list)
        self.addDockWidget(Qt.BottomDockWidgetArea, history_dock)

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
        self._audio_preview = AudioPreview(splitter)
        self._preview_stack.addWidget(self._audio_preview)

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
        self._act_refresh = self._action("刷新目录", "F5",
                                         self.refresh_workspace)
        self._act_save = self._action("保存", "Ctrl+S",
                                      lambda: self.save_file(False))
        self._act_save_as = self._action("另存为…", "Ctrl+Shift+S",
                                         lambda: self.save_file(True))
        self._act_export_entry = self._action("导出当前条目…", None,
                                              self.export_current)
        self._act_export_selected = self._action(
            "导出选中…", None, self.export_selected)
        self._act_export_all = self._action("导出全部精灵…", None,
                                            self.export_all_sprites)
        act_quit = self._action("退出", "Ctrl+Q", self.close)
        for act in (self._act_workspace, self._act_open, self._act_refresh,
                    self._act_save, self._act_save_as, self._act_export_entry,
                    self._act_export_selected, self._act_export_all,
                    act_quit):
            file_menu.addAction(act)

        edit_menu = self.menuBar().addMenu("编辑")
        self._act_replace_img = self._action("替换图片…", None,
                                             self.replace_images)
        self._act_replace_raw = self._action("替换原始数据…", None,
                                             self.replace_raw)
        self._act_add = self._action("新增条目…", None, self.add_entry)
        self._act_add_multi = self._action("多选导入…", None,
                                           self.import_entries_multi)
        self._act_import_path = self._action("按路径导入…", None,
                                             self.import_by_path)
        self._act_import_sprite = self._action(
            "帧图转精灵导入…", None, self.import_frames_as_sprite)
        self._act_delete = self._action("删除条目", None, self.delete_entry)
        self._act_undo = self._action("撤销", "Ctrl+Z", self.undo_entry)
        self._act_redo = self._action("重做", "Ctrl+Y", self.redo_entry)
        self._act_redo.setShortcuts(
            [QKeySequence("Ctrl+Y"), QKeySequence("Ctrl+Shift+Z")])
        self._act_revert = self._action("还原条目", None, self.revert_entry)
        for act in (self._act_replace_img, self._act_replace_raw, self._act_add,
                    self._act_add_multi, self._act_import_path,
                    self._act_import_sprite,
                    self._act_delete, self._act_undo, self._act_redo, self._act_revert):
            edit_menu.addAction(act)

        about = self._action("关于", None, self._show_about)
        self.menuBar().addMenu("帮助").addAction(about)

    def _action(self, text, shortcut, slot) -> QAction:
        act = QAction(text, self)
        if shortcut:
            act.setShortcut(shortcut)
        act.triggered.connect(slot)
        return act

    def _build_toolbar(self) -> None:
        """顶部图标工具栏：与菜单共用同一 QAction（状态同步）。

        图标在上、两字短名在下（与 UI 编辑器同一约定）；菜单与
        悬停提示仍显示全名。
        """
        for action, icon, tip, short in (
                (self._act_workspace, icons.icon_workspace(),
                 "设定工作目录（资源包所在文件夹）", "目录"),
                (self._act_open, icons.icon_open_pack(),
                 "打开资源包", "打开"),
                (self._act_refresh, icons.icon_refresh(),
                 "刷新工作目录文件列表（F5）", "刷新"),
                (self._act_save, icons.icon_save(), "保存（Ctrl+S）", "保存"),
                (self._act_save_as, icons.icon_save_as(),
                 "另存为（Ctrl+Shift+S）", "另存"),
                (self._act_export_selected, icons.icon_export(),
                 "导出选中条目（按真名目录树）", "导出"),
                (self._act_import_path, icons.icon_import_path(),
                 "按路径导入（游戏按路径找图，编号须为路径哈希）", "导入"),
                (self._act_import_sprite, icons.icon_import_sprite(),
                 "帧图转精灵导入（多张合成多帧动画）", "精灵"),
                (self._act_delete, icons.icon_delete(),
                 "删除当前条目", "删除")):
            action.setIcon(icon)
            action.setToolTip(tip)
            action.setIconText(short)
        bar = QToolBar("主工具栏", self)
        bar.setMovable(False)
        bar.setIconSize(QSize(26, 26))
        bar.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, bar)
        bar.addAction(self._act_workspace)
        bar.addAction(self._act_open)
        bar.addAction(self._act_refresh)
        bar.addSeparator()
        bar.addAction(self._act_save)
        bar.addAction(self._act_save_as)
        bar.addSeparator()
        bar.addAction(self._act_export_selected)
        bar.addAction(self._act_import_path)
        bar.addAction(self._act_import_sprite)
        bar.addSeparator()
        bar.addAction(self._act_delete)
        self._toolbar = bar

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
        if self._busy:
            return
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
            named = doc.resolve_names()  # 顺带把能认出的真名认了
            progress(doc.count, doc.count)
            return doc, kinds, named

        def done(result) -> None:
            doc, kinds, named = result
            self._docs[key] = doc
            self._kinds_map[key] = kinds
            suffix = f"（识别真名 {named} 条）" if named else ""
            self.log(f"已打开 {doc.path}：{doc.count} 个条目{suffix}")
            self._activate_pack(key)

        self._run_job(Job(job, "打开资源包"), done)

    def _activate_pack(self, key: str) -> None:
        doc = self._docs[key]
        self._current_key = key
        self._preview_epoch += 1
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

        epoch = self._preview_epoch

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
            j, lambda thumbs: self._on_thumbnails(key, thumbs)
            if epoch == self._preview_epoch and not self._busy else None,
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
        self._audio_preview.stop_playback()
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
        elif kind is EntryKind.AUDIO:
            self._sprite = None
            self._inspector.set_entry(doc, index, None)
            self._audio_preview.set_content(doc.content(index))
            self._preview_stack.setCurrentIndex(3)
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

        epoch = self._preview_epoch

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
            j, lambda bundle: self._on_sprite_decoded(index, bundle)
            if epoch == self._preview_epoch and not self._busy else None,
            on_error=lambda text: self._on_job_error(text)
            if epoch == self._preview_epoch and not self._busy else None)

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
        if self._busy or self._doc is None or self._sprite is None or self._current < 0:
            return
        self._open_replace_images_dialog(
            self._current, self._sprite,
            self._sprite_view.current_frame)

    def _replace_images_at(self, index: int) -> None:
        """右键替换图片：目标不是当前预览条目时先后台解码再弹框。"""
        doc = self._doc
        if doc is None or not 0 <= index < doc.count:
            return
        if doc.entry_kind(index) is not EntryKind.SPRITE:
            return
        if index == self._current and self._sprite is not None:
            self._open_replace_images_dialog(
                index, self._sprite, self._sprite_view.current_frame)
            return
        self._run_job(
            Job(lambda _p: decode_sprite(doc.content(index)), "解码精灵"),
            lambda sprite: self._open_replace_images_dialog(
                index, sprite, 0))

    def _open_replace_images_dialog(self, index: int, sprite,
                                    current_frame: int) -> None:
        dialog = ReplaceImagesDialog(
            self, sprite, current_frame)
        if dialog.exec() != dialog.Accepted:
            return
        paths = dialog.file_paths
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
        if self._busy or self._doc is None or self._current < 0:
            return
        self._replace_raw_at(self._current)

    def _replace_raw_at(self, index: int) -> None:
        if self._busy or self._doc is None or not 0 <= index < self._doc.count:
            return
        path, _ = QFileDialog.getOpenFileName(self, "选择原始数据文件")
        if not path:
            return
        data = Path(path).read_bytes()
        if QMessageBox.question(
            self, "替换原始数据",
            f"用所选文件（{len(data)} 字节）替换条目 {index} 的内容？",
        ) != QMessageBox.Yes:
            return
        self._doc.replace_content(index, data)
        self.log(f"条目 {index} 已替换原始数据")
        self._after_entry_changed(index)

    def add_entry(self) -> None:
        if self._busy or self._doc is None:
            return
        path, _ = QFileDialog.getOpenFileName(self, "选择要新增的文件")
        if not path:
            return
        if self._doc.kind == "0slf":
            # 0SLF 必须按路径导入：随便分配的编号游戏按名找不到
            self._import_files_by_path([path])
            return
        name, ok = QInputDialog.getText(
            self, "新增条目", "新条目文件名（如 sub\\mod.pyo）：")
        if not ok or not name:
            return
        index = self._doc.add_entry(Path(path).read_bytes(), name)
        self.log(f"已新增条目 {index}")
        self._reload_grid(select=index)

    def delete_entry(self) -> None:
        if self._busy or self._doc is None or self._current < 0:
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

    def _entry_identity(self, index: int):
        doc = self._doc
        assert doc is not None
        meta = doc.archive.extra_metas[index]
        return meta.entry_id if doc.kind == "0slf" else meta.name

    def _apply_history(self, redo: bool) -> None:
        doc = self._doc
        if doc is None or self._busy:
            return
        identity = (self._entry_identity(self._current)
                    if 0 <= self._current < doc.count else None)
        label = doc.history.redo_label if redo else doc.history.undo_label
        if not (doc.redo() if redo else doc.undo()):
            return
        self._render_cache.clear()
        self._thumb_cache.clear()
        select = next((i for i in range(doc.count)
                       if self._entry_identity(i) == identity), -1)
        if select < 0 and doc.count:
            select = min(max(self._current, 0), doc.count - 1)
        self._reload_grid(select=select)
        self.log(f"{'重做' if redo else '撤销'}：{label}")

    def undo_entry(self) -> None:
        focus = self.focusWidget()
        if isinstance(focus, (QLineEdit, QPlainTextEdit)) and not focus.isReadOnly():
            focus.undo()
            return
        self._apply_history(False)

    def redo_entry(self) -> None:
        focus = self.focusWidget()
        if isinstance(focus, (QLineEdit, QPlainTextEdit)) and not focus.isReadOnly():
            focus.redo()
            return
        self._apply_history(True)

    def revert_entry(self) -> None:
        if self._busy or self._doc is None or self._current < 0:
            return
        self._doc.revert(self._current)
        self.log(f"条目 {self._current} 已还原为打开时状态")
        self._after_entry_changed(self._current)

    def _after_entry_changed(self, index: int) -> None:
        self._preview_epoch += 1
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
        self._preview_epoch += 1
        # 所有旧下标缓存与未完成解码结果一起失效。
        self._render_cache.clear()
        if self._current_key:
            self._thumb_cache = OrderedDict(
                (key, value) for key, value in self._thumb_cache.items()
                if key[0] != self._current_key)
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
            self._sprite = None
            self._anim_bar.set_frame_count(0)
            self._audio_preview.stop_playback()
            self._sprite_view.clear()
            self._text_preview.set_content(b"")
            self._hex_preview.set_content(b"")
            self._preview_stack.setCurrentIndex(0)
            self._inspector.clear()
        self._update_actions()

    # ---------------------------------------------------------- 导出 ----
    def export_current(self) -> None:
        if self._busy or self._doc is None or self._current < 0:
            return
        out = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not out:
            return
        doc, index = self._doc, self._current
        protected = self._protected_sources()
        self._run_job(
            Job(lambda _p: exporter.export_entry(doc, index, Path(out), protected),
                "导出条目"),
            lambda paths: self.log(f"条目 {index} 已导出到 {out}"),
        )

    def export_all_sprites(self) -> None:
        if self._busy or self._doc is None:
            return
        out = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not out:
            return
        doc = self._doc
        protected = self._protected_sources()
        self._run_job(
            Job(lambda _p: exporter.export_all_sprites(doc, Path(out), protected),
                "导出全部精灵"),
            lambda count: self.log(f"已导出 {count} 个精灵到 {out}"),
        )

    # ------------------------------------------------ 网格右键/批量 ----
    def _show_grid_context_menu(self, index: int, pos) -> None:
        """网格右键菜单：导出（该条/选中/该页）、替换、多选导入。"""
        doc = self._doc
        if doc is None or not 0 <= index < doc.count:
            return
        if not self._grid.selection_mode:
            self._grid.select_entry(index)
            self._select_entry(index)
        menu = QMenu(self)
        menu.addAction("导出该条",
                       lambda: self.export_entries([index], "该条"))
        picked = len(self._grid.selected_indexes())
        act_selected = menu.addAction(
            f"导出选中 ({picked})", self.export_selected)
        act_selected.setEnabled(picked > 0)  # 与「选择」按钮联动
        menu.addAction("导出该页", self.export_page)
        menu.addSeparator()
        replace_menu = menu.addMenu("替换")
        act_img = replace_menu.addAction(
            "替换图片…", lambda: self._replace_images_at(index))
        act_img.setEnabled(doc.entry_kind(index) is EntryKind.SPRITE)
        replace_menu.addAction(
            "替换原始数据…", lambda: self._replace_raw_at(index))
        menu.addSeparator()
        menu.addAction("多选导入…", self.import_entries_multi)
        act_path = menu.addAction("按路径导入…", self.import_by_path)
        act_path.setEnabled(doc.kind == "0slf")  # 名字决定游戏能否找到
        act_sprite = menu.addAction("帧图转精灵导入…",
                                    self.import_frames_as_sprite)
        act_sprite.setEnabled(doc.kind == "0slf")
        menu.exec(pos)

    def export_entries(self, indexes: list[int], what: str = "条目") -> None:
        """按真名目录树批量导出（右键/文件菜单共用）。"""
        if self._busy or self._doc is None or not indexes:
            return
        out = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not out:
            return
        doc = self._doc
        targets = list(indexes)
        protected = self._protected_sources()

        def done(report) -> None:
            note = (f"已导出{what} {report['entries']} 条"
                    f"（{report['files']} 个文件）到 {out}")
            if report["failed"]:
                note += f"；失败 {len(report['failed'])} 条：{report['failed'][:5]}"
            self.log(note)

        self._run_job(
            Job(lambda _p: exporter.export_entries(
                doc, targets, Path(out), protected),
                f"导出{what}"),
            done)

    def export_selected(self) -> None:
        self.export_entries(self._grid.selected_indexes(), "选中条目")

    def export_page(self) -> None:
        self.export_entries(self._grid.page_entries(), "本页条目")

    def import_entries_multi(self) -> None:
        """多选导入：一次选多个文件逐个新增。

        0SLF 包逐个问资源路径并按路径导入（名字对了游戏才找得
        到）；data.fls 逐个问包内文件名后新增。
        """
        if self._busy or self._doc is None:
            return
        paths, _ = QFileDialog.getOpenFileNames(
            self, "选择要导入的文件（可多选）")
        if not paths:
            return
        doc = self._doc
        if doc.kind == "0slf":
            self._import_files_by_path(paths)
            return
        added: list[int] = []
        skipped = 0
        with doc.edit_group("多选导入"):
            for path in paths:
                name, ok = QInputDialog.getText(
                    self, "多选导入",
                    f"为 {Path(path).name} 输入包内文件名：",
                    text=Path(path).name)
                if not ok or not name:
                    skipped += 1
                    continue
                try:
                    added.append(doc.add_entry(Path(path).read_bytes(), name))
                except Exception as exc:
                    self.log(f"导入 {path} 失败：{exc}")
                    skipped += 1
        if added:
            self._reload_grid(select=added[-1])
        self.log(f"多选导入完成：新增 {len(added)} 条"
                 + (f"，跳过 {skipped} 个" if skipped else ""))
        self._update_actions()

    def import_by_path(self) -> None:
        """按路径导入（单个文件）：名字算编号，游戏才查得到。"""
        if self._busy or self._doc is None or self._doc.kind != "0slf":
            return
        path, _ = QFileDialog.getOpenFileName(self, "选择要导入的文件")
        if path:
            self._import_files_by_path([path])

    def _choose_resource_path(self, filename: str) -> tuple[str, bool]:
        doc = self._doc
        if doc is None:
            return "", False
        default = (doc.true_name(self._current)
                   if 0 <= self._current < doc.count else None) or filename
        dialog = ResourcePathDialog(filename, doc.known_resource_paths(), default, self)
        ok = dialog.exec() == QDialog.Accepted
        return dialog.path, ok

    def import_frames_as_sprite(self) -> None:
        """选一至多张帧图，转成游戏精灵后按路径导入。

        多张图按文件名顺序（01、02…）合成多帧动画；一张图就是
        单帧精灵。锚点取左上角，适合界面图与简单动画。
        """
        if self._busy or self._doc is None or self._doc.kind != "0slf":
            return
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择帧图片（多选 = 多帧动画，按文件名顺序）", "",
            "图片 (*.png *.jpg *.jpeg *.bmp *.tga *.gif);;所有文件 (*)")
        if not files:
            return
        res_path, ok = self._choose_resource_path(Path(files[0]).name)
        if not ok or not res_path.strip():
            return
        res_path = res_path.strip()
        from ..core.codecs import sprite as sprite_codec

        try:
            data, count, _report = sprite_codec.sprite_bytes_from_files(
                files)
        except Exception as exc:
            self.log(f"转精灵失败：{exc}")
            QMessageBox.warning(self, "转精灵失败", str(exc))
            return
        doc = self._doc
        existing = doc.index_by_path(res_path)
        if existing is not None:
            answer = QMessageBox.question(
                self, "这个路径已在包里",
                f"路径 {res_path} 已经是条目 {existing}。\n"
                "要用转好的精灵替换它的内容吗？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if answer != QMessageBox.Yes:
                return
            doc.replace_content(existing, data)
            self._after_entry_changed(existing)
            self.log(f"已用 {count} 帧精灵替换条目 {existing}：{res_path}")
            return
        index = doc.add_entry_for_path(data, res_path)
        self._reload_grid(select=index)
        self.log(f"已导入 {count} 帧精灵为条目 {index}：{res_path}")

    def _import_files_by_path(self, paths: list[str]) -> None:
        """逐个询问资源路径并导入；路径已存在时询问是否替换。"""
        doc = self._doc
        assert doc is not None
        added: list[int] = []
        replaced: list[int] = []
        skipped = 0
        with doc.edit_group("按路径批量导入"):
            for path in paths:
                filename = Path(path).name
                res_path, ok = self._choose_resource_path(filename)
                if not ok or not res_path.strip():
                    skipped += 1
                    continue
                res_path = res_path.strip()
                try:
                    data = Path(path).read_bytes()
                except OSError as exc:
                    self.log(f"读取 {path} 失败：{exc}")
                    skipped += 1
                    continue
                existing = doc.index_by_path(res_path)
                if existing is not None:
                    answer = QMessageBox.question(
                        self, "这个路径已在包里",
                        f"路径 {res_path} 已经是条目 {existing}。\n"
                        f"要用 {filename} 替换它的内容吗？",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if answer != QMessageBox.Yes:
                        skipped += 1
                        continue
                    doc.replace_content(existing, data)
                    replaced.append(existing)
                    self._after_entry_changed(existing)
                    self.log(f"已按路径替换条目 {existing}：{res_path}")
                    continue
                index = doc.add_entry_for_path(data, res_path)
                added.append(index)
                self.log(f"已按路径导入条目 {index}：{res_path}")
        if added:
            self._reload_grid(select=added[-1])
        self.log(f"按路径导入完成：新增 {len(added)} 条、"
                 f"替换 {len(replaced)} 条"
                 + (f"，跳过 {skipped} 个" if skipped else ""))
        self._update_actions()

    # ---------------------------------------------------------- 保存 ----
    def _protected_sources(self) -> list[Path]:
        sources = [path for doc in self._docs.values()
                   for path in doc.source_paths]
        if self._workspace is not None:
            sources.extend(path for path in self._workspace.iterdir()
                           if path.suffix.lower() == ".fls")
        return sources

    def save_file(self, save_as: bool) -> None:
        if self._busy or self._doc is None:
            return
        doc = self._doc
        old_key = self._current_key
        selected = self._current
        selected_id = (
            doc.archive.extra_metas[selected].entry_id
            if doc.kind == "0slf" and 0 <= selected < doc.count else None
        )
        # Ctrl+S 与另存都生成新包，不能直接覆盖源包或历史基线。
        default = (doc.path.with_name(doc.path.stem + "_patched.fls")
                   if doc.path else Path("new.fls"))
        sequence = 2
        while default.exists():
            default = default.with_name(
                f"{doc.path.stem if doc.path else 'new'}_patched_{sequence}.fls")
            sequence += 1
        path, _ = QFileDialog.getSaveFileName(
            self, "保存资源包（生成新包，原包不动）", str(default),
            "资源包 (*.fls);;所有文件 (*)")
        if not path:
            return
        target = Path(path)
        protected = self._protected_sources()
        try:
            guard_output(target, protected)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "保存失败", str(exc))
            return
        if SaveReviewDialog(doc.changes(), target, self).exec() != QDialog.Accepted:
            return

        def job(progress):
            return save_document(doc, target, progress, protected)

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
            # 保存会按 entry_id 排序，不能沿用旧下标的名称、图标、
            # 类型或选择；按稳定条目身份恢复选择并重建网格。
            self._render_cache.clear()
            self._thumb_cache.clear()
            if selected_id is not None:
                selected_after = next(
                    (i for i, meta in enumerate(doc.archive.extra_metas)
                     if meta.entry_id == selected_id), -1)
            else:
                selected_after = selected
            self._reload_grid(select=selected_after)
            note = "，源包未修改"
            gap = (f"，另有 {report.sprite_undecodable} 条原包精灵超出"
                   "本机解码器覆盖（字节原样保留，不影响保存）"
                   if report.sprite_undecodable else "")
            self.log(
                f"已保存到 {target}（校验通过，试解码精灵 "
                f"{report.sprite_checked} 个{note}{gap}）")
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
        sender = self.sender()
        if sender is self._blocking_job:
            self._busy = False
            self._blocking_job = None
            self._preview_epoch += 1
            self._grid.setEnabled(True)
            self._dir_panel.setEnabled(True)
            self._progress.hide()
        on_finished, _on_err = self._job_callbacks.pop(sender, (None, None))
        if on_finished is not None:
            on_finished(result)
        self._update_actions()

    def _dispatch_error(self, text: str) -> None:
        sender = self.sender()
        if sender is self._blocking_job:
            self._busy = False
            self._blocking_job = None
            self._preview_epoch += 1
            self._grid.setEnabled(True)
            self._dir_panel.setEnabled(True)
            self._progress.hide()
        _on_fin, on_error = self._job_callbacks.pop(
            sender, (None, self._on_job_error))
        on_error(text)
        self._update_actions()

    def _run_job(self, job: Job, on_finished) -> None:
        """带忙碌状态与进度条的任务启动（打开/保存/导出用）。"""
        if self._busy:
            return
        self._busy = True
        self._blocking_job = job.signals
        self._preview_epoch += 1
        self._grid.setEnabled(False)
        self._dir_panel.setEnabled(False)
        self._progress.setRange(0, 0)
        self._progress.show()
        self._update_actions()
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
        has_doc = self._doc is not None and not self._busy
        has_entry = has_doc and self._current >= 0
        is_sprite = (
            has_entry and self._doc is not None
            and self._doc.entry_kind(self._current) is EntryKind.SPRITE)
        self._act_save.setEnabled(has_doc)
        self._act_save_as.setEnabled(has_doc)
        self._act_export_entry.setEnabled(has_entry)
        self._act_export_selected.setEnabled(
            has_doc and bool(self._grid.selected_indexes()))
        self._act_export_all.setEnabled(has_doc)
        self._act_replace_img.setEnabled(is_sprite)
        self._act_replace_raw.setEnabled(has_entry)
        self._act_add.setEnabled(has_doc)
        self._act_add_multi.setEnabled(has_doc)
        self._act_import_path.setEnabled(
            has_doc and self._doc is not None
            and self._doc.kind == "0slf")
        self._act_import_sprite.setEnabled(
            has_doc and self._doc is not None
            and self._doc.kind == "0slf")
        self._act_delete.setEnabled(has_entry)
        self._act_undo.setEnabled(has_doc and self._doc.can_undo)
        self._act_redo.setEnabled(has_doc and self._doc.can_redo)
        doc = self._doc
        self._act_undo.setText("撤销" + (f"：{doc.history.undo_label}"
                                      if doc and doc.can_undo else ""))
        self._act_redo.setText("重做" + (f"：{doc.history.redo_label}"
                                      if doc and doc.can_redo else ""))
        self._history_list.clear()
        if doc:
            for step in doc.history.applied:
                self._history_list.addItem("已应用 · " + step.label)
            for step in reversed(doc.history.undone):
                self._history_list.addItem("待重做 · " + step.label)
        for action in (self._act_workspace, self._act_open, self._act_refresh):
            action.setEnabled(not self._busy)
        self._act_revert.setEnabled(has_entry)
        if has_doc:
            assert self._doc is not None
            summary = counts(self._doc.changes())
            self._status_label.setText(
                f"{self._doc.path.name if self._doc.path else '未命名'} · "
                f"{self._doc.count} 个条目 · 容器 {self._doc.kind} · "
                f"新增 {summary['新增']} · 修改 {summary['修改']} · "
                f"删除 {summary['删除']}")

    def _show_about(self) -> None:
        QMessageBox.about(
            self, "关于",
            f"MXSJ 资源编辑器 {__version__}\n"
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
        if self._busy:
            self.log("操作进行中，请等待打开/保存/导出完成后再关闭。")
            event.ignore()
            return
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
        self._preview_epoch += 1  # 关闭后旧预览结果/错误不再回灌窗口
        for doc in self._docs.values():
            doc.close()
        super().closeEvent(event)
