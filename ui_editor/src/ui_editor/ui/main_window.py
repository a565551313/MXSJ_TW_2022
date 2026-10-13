"""主窗口：文件/资源工作流与五大区域的组装。

布局：左侧（布局文件树 + 控件树）、中央画布、右侧（属性面板 +
控件调色板）。打开来源两种：散装 ``.dlg`` 文件/目录，以及从
``interface.fls`` 等资源包按路径直开（自动解密）；保存可写散装
``.dlg``，也可生成写回布局的新资源包（原包不动，见 M1）。
"""

from __future__ import annotations

from bisect import bisect_left
from pathlib import Path

from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..core import dlg_codec, pack_build, snap
from ..core.assets import AssetResolver
from ..core.catalog import known_layout_paths
from ..core.model import LayoutDocument, Widget
from ..core.mxhash import mx_hash
from ..core.pack import FlsPack
from ..core.painters import PaintContext
from ..core.styles import StyleBook
from . import icons
from .canvas import CanvasView, LayoutScene
from .panels import PalettePanel, ResourceTreePanel, WidgetTreePanel
from .property_panel import PropertyPanel


class MainWindow(QMainWindow):
    """UI 编辑器主窗口。"""

    def __init__(self) -> None:
        super().__init__()
        self._settings = QSettings("MXSJ", "UIEditor")
        self.resolver = AssetResolver()
        self.styles = StyleBook()
        self.ctx = PaintContext(assets=self.resolver, styles=self.styles)
        self.doc: LayoutDocument | None = None
        self._selected: Widget | None = None
        self._selection_anchor: list[int] | None = None
        self._syncing_selection = False
        self._loading = False

        self.scene = LayoutScene(self.ctx, self._on_geometry_changed,
                                 self._on_geometry_committed)
        self.view = CanvasView(self.scene)
        self.setCentralWidget(self.view)

        self.resource_panel = ResourceTreePanel()
        self.tree_panel = WidgetTreePanel()
        self.props_panel = PropertyPanel()
        self.props_panel.assets = self.resolver  # 文件字段从包里选
        self.palette_panel = PalettePanel()
        self._build_docks()
        self._build_menus()
        self._connect_signals()

        delete_key = QShortcut(QKeySequence.StandardKey.Delete, self)
        delete_key.activated.connect(self.delete_selected)

        self.setStatusBar(QStatusBar())
        self._update_title()
        self._update_status("就绪：打开一个 .dlg、布局目录，或从资源包打开。")
        self.resize(1360, 860)

    # ------------------------------------------------------------------
    # 界面组装
    # ------------------------------------------------------------------
    def _build_docks(self) -> None:
        from PySide6.QtWidgets import QDockWidget

        left = QDockWidget("布局与控件树", self)
        left_host = QWidget()
        left_layout = QVBoxLayout(left_host)
        left_tabs = QTabWidget()
        left_tabs.addTab(self.resource_panel, "资源树")
        left_tabs.addTab(self.tree_panel, "控件树")
        left_layout.addWidget(left_tabs)
        left.setWidget(left_host)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, left)

        right = QDockWidget("属性与控件", self)
        right_host = QWidget()
        right_layout = QVBoxLayout(right_host)
        right_split = QSplitter(Qt.Orientation.Vertical)
        right_split.addWidget(self.props_panel)
        right_split.addWidget(self.palette_panel)
        right_split.setSizes([520, 300])
        right_layout.addWidget(right_split)
        right.setWidget(right_host)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right)

    def _build_menus(self) -> None:
        file_menu = self.menuBar().addMenu("文件")
        self._act_open_file = self._add_action(
            file_menu, "打开布局文件…", self.open_layout_file_dialog,
            QKeySequence.StandardKey.Open)
        self._add_action(file_menu, "打开布局目录…", self.open_layout_dir_dialog)
        self._act_open_pack = self._add_action(
            file_menu, "从资源包打开布局…", self.open_from_pack)
        self._add_action(file_menu, "从资源目录打开布局…",
                         self.open_resource_dir_dialog)
        file_menu.addSeparator()
        self._add_action(file_menu, "新建布局", self.new_layout,
                         QKeySequence.StandardKey.New)
        self._act_save = self._add_action(
            file_menu, "保存", self.save, QKeySequence.StandardKey.Save)
        self._act_save.setToolTip("保存当前布局（Ctrl+S）")
        self._add_action(file_menu, "另存为…", lambda: self.save_as())
        self._act_save_pack = self._add_action(
            file_menu, "保存回资源包（生成新包）…", self.save_to_pack_dialog)
        self._act_save_pack.setToolTip("写回资源包生成新包（编辑包内布局时）")
        self._act_export_png = self._add_action(
            file_menu, "导出 PNG…", self.export_png)
        file_menu.addSeparator()
        self._add_action(file_menu, "退出", self.close,
                         QKeySequence.StandardKey.Quit)

        view_menu = self.menuBar().addMenu("视图")
        self._act_fit = self._add_action(
            view_menu, "适应窗口", self.view.fit_content)
        self._act_actual = self._add_action(
            view_menu, "实际大小（100%）", self.view.actual_size)
        names_action = QAction("显示占位/控件名标注", self, checkable=True)
        names_action.setChecked(True)
        names_action.toggled.connect(self._toggle_names)
        view_menu.addAction(names_action)
        self._names_action = names_action
        self._act_grid = QAction("显示网格与标尺", self, checkable=True)
        self._act_grid.toggled.connect(self._toggle_grid)
        view_menu.addAction(self._act_grid)
        state_menu = view_menu.addMenu("按钮状态预览")
        self._button_state_actions: dict[str, QAction] = {}
        for state_key, state_label in (("normal", "正常"),
                                       ("pressed", "按下"),
                                       ("hover", "悬停"),
                                       ("disabled", "禁用")):
            act = QAction(state_label, self, checkable=True)
            act.setChecked(state_key == "normal")
            act.triggered.connect(
                lambda _checked=False, k=state_key:
                self.set_button_state(k))
            state_menu.addAction(act)
            self._button_state_actions[state_key] = act

        edit_menu = self.menuBar().addMenu("编辑")
        self._undo_action = QAction("撤销", self)
        self._undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        self._undo_action.triggered.connect(self.undo)
        self._undo_action.setEnabled(False)
        edit_menu.addAction(self._undo_action)
        self._redo_action = QAction("重做", self)
        self._redo_action.setShortcuts(
            [QKeySequence("Ctrl+Y"), QKeySequence("Ctrl+Shift+Z")])
        self._redo_action.triggered.connect(self.redo)
        self._redo_action.setEnabled(False)
        edit_menu.addAction(self._redo_action)

        help_menu = self.menuBar().addMenu("帮助")
        self._add_action(help_menu, "关于", self._about)
        self._build_toolbar()

    def _build_toolbar(self) -> None:
        """顶部图标工具栏：与菜单共用同一 QAction（状态同步）。"""
        for action, icon, tip, short in (
                (self._act_open_file, icons.icon_open_file(),
                 "打开布局文件", "打开"),
                (self._act_open_pack, icons.icon_open_pack(),
                 "从资源包打开布局", "开包"),
                (self._undo_action, icons.icon_undo(),
                 "撤销（Ctrl+Z）", "撤销"),
                (self._redo_action, icons.icon_redo(),
                 "重做（Ctrl+Y）", "重做"),
                (self._act_save, icons.icon_save(),
                 "保存（Ctrl+S）", "保存"),
                (self._act_save_pack, icons.icon_save_pack(),
                 "保存回资源包（生成新包）", "存包"),
                (self._act_export_png, icons.icon_export_image(),
                 "导出 PNG 预览图", "导出"),
                (self._act_fit, icons.icon_fit(), "适应窗口", "适屏"),
                (self._act_actual, icons.icon_actual_size(),
                 "实际大小（100%）", "100%"),
                (self._names_action, icons.icon_names(),
                 "显示/隐藏名字标注", "标注")):
            action.setIcon(icon)
            action.setToolTip(tip)
            action.setIconText(short)
        bar = QToolBar("主工具栏", self)
        bar.setMovable(False)
        bar.setIconSize(QSize(26, 26))
        bar.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, bar)
        bar.addAction(self._act_open_file)
        bar.addAction(self._act_open_pack)
        bar.addSeparator()
        bar.addAction(self._undo_action)
        bar.addAction(self._redo_action)
        bar.addSeparator()
        bar.addAction(self._act_save)
        bar.addAction(self._act_save_pack)
        bar.addAction(self._act_export_png)
        bar.addSeparator()
        bar.addAction(self._act_fit)
        bar.addAction(self._act_actual)
        bar.addAction(self._names_action)
        # 网格/标尺开关与对齐下拉都进工具栏（常用手势不走菜单）
        self._act_grid.setIcon(icons.icon_grid())
        self._act_grid.setIconText("网格")
        self._act_grid.setToolTip("显示/隐藏网格与标尺")
        bar.addAction(self._act_grid)
        align_btn = QToolButton(self)
        align_btn.setText("对齐")
        align_btn.setIcon(icons.icon_align())
        align_btn.setToolTip("对齐与等距分布（先在画布上 Ctrl+点选多个同级控件）")
        align_btn.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        align_btn.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup)
        align_menu = QMenu(align_btn)
        for text, mode in (("左对齐", "left"), ("水平居中", "hcenter"),
                           ("右对齐", "right"), ("顶对齐", "top"),
                           ("垂直居中", "vcenter"), ("底对齐", "bottom")):
            act = align_menu.addAction(text)
            act.triggered.connect(
                lambda _checked=False, m=mode: self.apply_alignment(m))
        align_menu.addSeparator()
        act = align_menu.addAction("横向等距分布")
        act.triggered.connect(lambda: self.apply_distribute("x"))
        act = align_menu.addAction("纵向等距分布")
        act.triggered.connect(lambda: self.apply_distribute("y"))
        align_btn.setMenu(align_menu)
        bar.addWidget(align_btn)
        self._align_btn = align_btn
        state_btn = QToolButton(self)
        state_btn.setText("按钮态")
        state_btn.setIcon(icons.icon_button_state())
        state_btn.setToolTip("切换画布上按钮的预览状态（正常/按下/悬停/禁用）")
        state_btn.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        state_btn.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup)
        state_menu = QMenu(state_btn)
        self._button_state_btn_actions: dict[str, QAction] = {}
        for state_key, state_label in (("normal", "正常"),
                                       ("pressed", "按下"),
                                       ("hover", "悬停"),
                                       ("disabled", "禁用")):
            act = state_menu.addAction(state_label)
            act.setCheckable(True)
            act.setChecked(state_key == "normal")
            act.triggered.connect(
                lambda _checked=False, k=state_key:
                self.set_button_state(k))
            self._button_state_btn_actions[state_key] = act
        state_btn.setMenu(state_menu)
        bar.addWidget(state_btn)
        self._button_state_btn = state_btn
        self._toolbar = bar
        # 状态栏右端常驻缩放百分比
        self._zoom_label = QLabel("100%", self)
        self.statusBar().addPermanentWidget(self._zoom_label)
        self.view.zoom_changed.connect(self._on_zoom_changed)

    @staticmethod
    def _add_action(menu, text, slot, shortcut=None) -> QAction:
        action = QAction(text, menu)
        if shortcut is not None:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _connect_signals(self) -> None:
        self.resource_panel.open_pack_layout.connect(
            self._open_pack_layout)
        self.resource_panel.open_loose_file.connect(self.open_layout_file)
        self.resource_panel.choose_resource_dir.connect(
            self.open_resource_dir_dialog)
        self.resource_panel.choose_loose_dir.connect(
            self.open_layout_dir_dialog)
        self.tree_panel.widget_selected.connect(self._select_from_tree)
        self.tree_panel.add_child_requested.connect(self._add_child_from_tree)
        self.tree_panel.add_root_requested.connect(self._add_root_from_tree)
        self.tree_panel.promote_requested.connect(
            self.promote_selected_to_root)
        self.tree_panel.delete_requested.connect(self.delete_selected)
        self.tree_panel.reorder_requested.connect(self._reorder_widget)
        self.palette_panel.add_requested.connect(self.add_widget)
        self.props_panel.changed.connect(self._on_property_changed)
        self.scene.selectionChanged.connect(self._on_scene_selection)

    # ------------------------------------------------------------------
    # 文档打开/新建/保存
    # ------------------------------------------------------------------
    def _confirm_discard(self) -> bool:
        if self.doc is None or not self.doc.dirty:
            return True
        answer = QMessageBox.question(
            self, "未保存的修改",
            "当前布局有未保存的修改，确定丢弃吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return answer == QMessageBox.StandardButton.Yes

    def _set_document(self, doc: LayoutDocument | None) -> None:
        self._loading = True
        self.doc = doc
        self._selected = None
        self.scene.set_document(doc)
        self.tree_panel.build(doc)
        self.props_panel.set_widget(None)
        self._loading = False
        if doc is not None:
            doc.reset_history()
        self._sync_history_actions()
        if doc is not None:
            self.view.fit_content()
        self._update_title()
        count = len(doc.all_widgets()) if doc else 0
        self._update_status(
            f"已打开 {doc.display_name if doc else '—'}：{count} 个控件。"
            f"{self.resolver.summary}；"
            f"样式表："
            f"{'已加载 ui.lst' if self.styles.loaded else '未加载（默认字体）'}")

    def open_layout_file(self, path: str) -> None:
        if not self._confirm_discard():
            return
        try:
            dicts, md5 = dlg_codec.parse_bytes(Path(path).read_bytes())
        except Exception as exc:
            QMessageBox.warning(self, "打开失败", str(exc))
            return
        doc = LayoutDocument.from_dicts(dicts, md5)
        doc.source_path = str(path)
        self.resolver.add_loose_dir(Path(path).parent)
        self._try_load_styles()
        self._set_document(doc)
        self.resource_panel.reveal_selection(("file", str(path)))

    def open_layout_file_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "打开布局文件", self._settings.value("last_dir", ""),
            "布局文件 (*.dlg);;所有文件 (*)")
        if path:
            self._settings.setValue("last_dir", str(Path(path).parent))
            self.open_layout_file(path)

    def open_layout_dir(self, path: str) -> None:
        self.resource_panel.add_loose_dir(path)
        self.resolver.add_loose_dir(path)
        local_lst = Path(path) / "ui.lst"
        if local_lst.is_file():
            self._set_styles(
                StyleBook.parse_bytes(local_lst.read_bytes()),
                f"本地 {local_lst}")
        else:
            self._try_load_styles()
        self._update_status(f"布局目录：{path}（双击文件打开）")

    def open_layout_dir_dialog(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "打开布局目录", self._settings.value("last_dir", ""))
        if path:
            self._settings.setValue("last_dir", path)
            self.open_layout_dir(path)

    def open_pack_file(self, pack_path: str) -> int:
        """挂载一个资源包：有布局才入树并展开。返回布局数（无弹窗）。

        直接选包即可，不再经布局列表对话框；包内具体打开哪个
        布局，由用户在左侧资源树（可按名称搜索）双击决定。
        """
        try:
            if self.resolver.pack_for(pack_path) is None:
                self.resolver.mount_pack(pack_path)
        except Exception as exc:
            QMessageBox.warning(self, "挂载资源包失败", str(exc))
            return -1
        layouts = self.resolver.scan_layouts(pack_path)
        if layouts:
            self._add_pack_to_tree(pack_path, layouts)
            self.resource_panel.expand_pack(pack_path)
        self._try_load_styles()
        self.scene.refresh_all()
        return len(layouts)

    def _add_pack_to_tree(self, pack_path: str,
                          layouts: list[str]) -> None:
        """包入树；近乎全量的主 UI 包再挂包内缺失（灰显）名单。"""
        missing: list[str] = []
        if len(layouts) * 2 >= len(known_layout_paths()):
            missing = self.resolver.missing_layouts(pack_path)
        self.resource_panel.add_pack(pack_path, layouts, missing)

    def open_from_pack(self) -> None:
        """文件菜单入口：只选资源包本身，选完入树待双击。"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择资源包", self._settings.value("pack_dir", ""),
            "资源包 (*.fls);;所有文件 (*)")
        if not path:
            return
        self._settings.setValue("pack_dir", str(Path(path).parent))
        count = self.open_pack_file(path)
        if count == 0:
            QMessageBox.information(
                self, "没有布局文件",
                f"该资源包内没有布局文件：\n{path}\n\n"
                "（图片等其它资源已照常挂载，打开布局时可自动取图；"
                "布局请到资源树中按名称查找后双击。）")
        elif count > 0:
            self._update_status(
                f"已挂载 {Path(path).name}：识别到 {count} 个布局，"
                "在左侧资源树双击（可先按名称搜索）即可打开。")

    def _open_pack_layout(self, pack_path: str, res_path: str,
                          skip_discard: bool = False) -> None:
        """从包中打开一个布局（树双击与对话框共用）。包顺带入树。"""
        if not skip_discard and not self._confirm_discard():
            return
        try:
            if self.resolver.pack_for(pack_path) is None:
                self.resolver.mount_pack(pack_path)
        except Exception as exc:
            QMessageBox.warning(self, "挂载资源包失败", str(exc))
            return
        self._add_pack_to_tree(
            pack_path, self.resolver.scan_layouts(pack_path))
        result = self.resolver.fetch_dlg(res_path)
        if result is None:
            QMessageBox.warning(
                self, "找不到布局",
                f"在已挂载的包中找不到 {res_path}。\n"
                "树上灰色斜体的条目是内置目录里有、但该包内缺失的"
                "布局（已下线或走热更新），本来就打不开；其余情况"
                "请确认路径写法（如 dialog/xxx.dlg）与包是否正确。")
            return
        dicts, md5 = result
        doc = LayoutDocument.from_dicts(dicts, md5)
        doc.source_pack = (pack_path, res_path)
        self._try_load_styles()
        self._set_document(doc)
        self.resource_panel.reveal_selection(("pack", pack_path, res_path))

    def open_resource_dir(self, path: str) -> None:
        """从资源目录打开：挂载目录内全部包并逐个入树。"""
        before = {str(p) for p in self.resolver.pack_paths}
        self.resolver.mount_dir(path)
        added = skipped = 0
        for pack_file in self.resolver.pack_paths:
            if str(pack_file) in before:
                continue
            layouts = self.resolver.scan_layouts(str(pack_file))
            if not layouts:
                skipped += 1  # 没有布局文件的包不进树（仍挂载供取图）
                continue
            self._add_pack_to_tree(str(pack_file), layouts)
            added += 1
        self._try_load_styles()
        self.scene.refresh_all()
        self._update_status(
            f"资源目录：{path}；新入树 {added} 个含布局的包"
            f"（跳过 {skipped} 个无布局包）。{self.resolver.summary}；"
            "双击包中布局即可切换打开。")

    def open_resource_dir_dialog(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "从资源目录打开布局（其中 .fls 全部挂载）",
            self._settings.value("pack_dir", ""))
        if path:
            self._settings.setValue("pack_dir", path)
            self.open_resource_dir(path)

    def new_layout(self) -> None:
        if not self._confirm_discard():
            return
        doc = LayoutDocument()
        frame = doc.new_widget("CMainFrame")
        frame.props["sTitle"] = "新对话框"
        doc.dirty = True
        self._set_document(doc)
        self._select_widget(frame)

    def save(self) -> None:
        if self.doc is None:
            return
        if self.doc.source_path:
            self._write_to(self.doc.source_path)
        elif self.doc.source_pack:
            box = QMessageBox(self)
            box.setWindowTitle("保存")
            box.setText("这个布局来自资源包，要怎么保存？原包不会被修改。")
            to_pack = box.addButton(
                "存回资源包（生成新包）", QMessageBox.ButtonRole.AcceptRole)
            box.addButton("另存为散装 .dlg", QMessageBox.ButtonRole.ActionRole)
            box.addButton(QMessageBox.StandardButton.Cancel)
            box.exec()
            if box.clickedButton() is to_pack:
                self.save_to_pack_dialog()
            elif box.clickedButton() is not None and \
                    box.button(QMessageBox.StandardButton.Cancel) \
                    is not box.clickedButton():
                self.save_as()
        else:
            self.save_as()

    # -- 写回资源包 ---------------------------------------------------
    def _referenced_staged_images(self) -> dict[str, bytes]:
        """选图窗挂账的新图里，被当前布局引用到的那些（随包写入）。"""
        if self.doc is None:
            return {}
        staged = self.resolver.staged_images()
        if not staged:
            return {}
        texts: set[str] = set()
        stack: list = [self.doc.to_dicts()]
        while stack:
            value = stack.pop()
            if isinstance(value, str):
                texts.add(value.replace("/", "\\").lower())
            elif isinstance(value, dict):
                stack.extend(value.values())
            elif isinstance(value, (list, tuple)):
                stack.extend(value)
        return {path: data for path, data in staged.items()
                if path.replace("/", "\\").lower() in texts}

    def write_pack_copy(self, out_path: str) -> dict | None:
        """把当前包内布局写回一个新包文件（原包不动）。返回校验报告。

        选图窗新加且被本布局引用到的图片随布局一并写入（按路径
        新增或替换）。写后硬性校验：条目数 = 原数 + 新增图片数、
        新包目录按条目号升序且布局与新图都能被二分查找命中
        （模拟引擎寻址）、条目集合与预期一致、除布局条目与这些
        图片外每条（按条目号）存储字节一致、用全新解析器回读
        目标布局与当前文档逐字段一致、新图逐字节回读一致；
        任一不过返回 None 并说明（弹错在对话框层，这里只记报告）。
        """
        if self.doc is None or not self.doc.source_pack:
            return None
        src_pack, res_path = self.doc.source_pack
        plain = dlg_codec.dump_bytes(self.doc.to_dicts())
        tmp_out = str(out_path)
        extras = self._referenced_staged_images()
        info = pack_build.patch_pack_copy(
            src_pack, res_path, plain, tmp_out, extra_entries=extras)
        report: dict = {"out": tmp_out, "bytes": info["bytes"],
                        "mode": info["mode"],
                        "images_added": len(info["images_added"]),
                        "images_replaced": len(info["images_replaced"])}
        try:
            from ..core.assets import AssetResolver as _Resolver

            with FlsPack(src_pack) as before, FlsPack(tmp_out) as after:
                expected = before.count + len(info["images_added"])
                if after.count != expected:
                    report["error"] = "条目数变化，写回结果不可信"
                    return report
                ids_after = after.entry_ids
                if any(a > b for a, b in
                       zip(ids_after, ids_after[1:], strict=False)):
                    report["error"] = ("新包目录未按条目号升序，"
                                        "引擎可能查不到条目")
                    return report

                def engine_finds(entry_id: int) -> bool:
                    """模拟引擎按有序目录二分寻址：找得到才算写入成功。"""
                    j = bisect_left(ids_after, entry_id)
                    return j < len(ids_after) and ids_after[j] == entry_id

                added_ids = {mx_hash(n.encode("gbk", "replace"))
                             for n in info["images_added"]}
                if set(ids_after) != set(before.entry_ids) | added_ids:
                    report["error"] = "新包条目集合与预期不符，写回结果不可信"
                    return report
                for name in [res_path, *extras]:
                    if not engine_finds(mx_hash(name.encode("gbk",
                                                             "replace"))):
                        report["error"] = f"新包中二分查找不到：{name}"
                        return report
                allowed = set(info["changed_ids"])
                changed = 0
                unexpected = 0
                for entry_id in before.entry_ids:
                    # 快速补丁不挪动其他条目：span 未变即可断定
                    # 存储字节未变，跳过读取（允许变化的条目即便
                    # span 未变也要比内容，可能只是等长改字）
                    if (entry_id not in allowed
                            and before.span_of(entry_id)
                            == after.span_of(entry_id)):
                        continue
                    if before.read_id(entry_id) != after.read_id(entry_id):
                        if entry_id in allowed:
                            changed += 1
                        else:
                            unexpected += 1
                if unexpected:
                    report["error"] = f"有 {unexpected} 条条目被意外改变"
                    return report
                report["changed_entries"] = changed
            fresh = _Resolver()
            fresh.mount_pack(tmp_out)
            try:
                got = fresh.fetch_dlg(res_path)
                for name, data in extras.items():
                    if fresh.fetch_bytes(name) != data:
                        report["error"] = f"新图 {name} 回读不一致"
                        return report
            finally:
                fresh.close()
            if got is None:
                report["error"] = "新包回读目标布局失败"
                return report
            dicts = self.doc.to_dicts()
            if got[0] != dicts:
                report["error"] = "新包回读内容与当前文档不一致"
                return report
        except Exception as exc:
            report["error"] = f"写回校验失败：{exc}"
            return report
        report["ok"] = True
        # 状态迁移：已验证落盘，标记干净并让后续保存续写新包
        self.doc.dirty = False
        self.doc.source_pack = (tmp_out, res_path)
        self.resolver.discard_staged(list(extras))  # 已进新包，销账
        self._update_title()
        return report

    def save_to_pack_dialog(self) -> None:
        if self.doc is None or not self.doc.source_pack:
            QMessageBox.information(
                self, "保存回资源包",
                "当前布局不是从资源包打开的（散装/新建布局请直接保存）。")
            return
        src_pack, res_path = self.doc.source_pack
        default = str(Path(src_pack).with_name(
            Path(src_pack).stem + "_patched.fls"))
        path, _ = QFileDialog.getSaveFileName(
            self, "保存回资源包（生成新包，原包不动）", default,
            "资源包 (*.fls);;所有文件 (*)")
        if not path:
            return
        if Path(path) == Path(src_pack):
            answer = QMessageBox.warning(
                self, "要覆盖原包吗？",
                "你选了原包本身。强烈建议改存为新文件，并保留原包备份。\n"
                "确定要直接覆盖原包吗？",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                return
        overwritten = Path(path) == Path(src_pack)
        self._update_status("正在写回资源包并校验…")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            report = self.write_pack_copy(path)
        except Exception as exc:
            QMessageBox.warning(self, "写回失败", str(exc))
            return
        finally:
            QApplication.restoreOverrideCursor()
        if not report or not report.get("ok"):
            QMessageBox.warning(
                self, "写回校验未通过",
                (report or {}).get("error", "未知错误")
                + "\n新包文件已生成但不可信，请勿替换进客户端。")
            return
        fast = report.get("mode") in ("inplace", "relocated")
        images_note = ""
        if report.get("images_added") or report.get("images_replaced"):
            images_note = (
                f"\n一并写入新图 {report.get('images_added', 0)} 张、"
                f"替换图片 {report.get('images_replaced', 0)} 张。")
        tail = ("已直接覆盖原文件——请确认你手边留有原包备份。"
                if overwritten else
                "原包未被修改。安装时请在完整客户端副本上操作：先备份"
                "原包，再把新包改名替换，最后进游戏验证该界面。")
        QMessageBox.information(
            self, "已生成新包",
            f"已写回：{res_path}\n新包：{path}\n"
            f"条目校验通过（改变 {report.get('changed_entries', 0)} 条，"
            f"大小 {report['bytes']} 字节"
            + ("，快速补丁未重写整包" if fast else "") + "）。"
            + images_note + "\n\n"
            + tail)

    def save_as(self, path: str | None = None) -> bool:
        if self.doc is None:
            return False
        if path is None:
            path, _ = QFileDialog.getSaveFileName(
                self, "另存为布局", self.doc.display_name,
                "布局文件 (*.dlg);;所有文件 (*)")
            if not path:
                return False
        self.doc.source_path = str(path)
        self.doc.source_pack = None
        self._write_to(str(path))
        return True

    def _write_to(self, path: str) -> None:
        data = dlg_codec.dump_bytes(self.doc.to_dicts())
        try:
            Path(path).write_bytes(data)
        except OSError as exc:
            QMessageBox.warning(self, "保存失败", str(exc))
            return
        self.doc.dirty = False
        self._update_title()
        self._update_status(f"已保存：{path}")

    def export_png(self) -> None:
        if self.doc is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "导出 PNG", self.doc.display_name + ".png",
            "PNG 图片 (*.png)")
        if not path:
            return
        image = self.view.export_image()
        if image.save(path):
            self._update_status(f"已导出：{path}")
        else:
            QMessageBox.warning(self, "导出失败", f"无法写入 {path}")

    # ------------------------------------------------------------------
    # 资源挂载与样式
    # ------------------------------------------------------------------
    def _set_styles(self, book: StyleBook, origin: str) -> None:
        self.styles = book
        self.ctx.styles = book
        self.scene.refresh_all()
        self._update_status(
            f"样式表已加载（{origin}）：字体 {len(book.fonts)} 条、"
            f"按钮样式 {len(book.tbstyles)} 套。{self.resolver.summary}")

    def _try_load_styles(self) -> None:
        if self.styles.loaded:
            return
        book = self.resolver.fetch_styles()
        if book is not None and book.loaded:
            self._set_styles(book, "资源/ui.lst")

    # ------------------------------------------------------------------
    # 编辑操作
    # ------------------------------------------------------------------
    def current_selection(self) -> Widget | None:
        return self._selected

    def add_widget(self, wtype: str) -> None:
        if self.doc is None:
            QMessageBox.information(self, "没有布局",
                                    "请先打开或新建一个布局。")
            return
        widget = self.doc.new_widget(wtype, parent=self._selected)
        self.doc.checkpoint()
        self._refresh_structure()
        self._select_widget(widget)
        self._update_title()

    def _add_child_from_tree(self) -> None:
        target = self.tree_panel.current_widget() or self._selected
        if target is None:
            QMessageBox.information(self, "未选中控件",
                                    "请先在控件树或画布中选中一个父控件。")
            return
        wtype = self.palette_panel.current_type()
        if wtype is None:
            QMessageBox.information(self, "未选控件类型",
                                    "请先在控件调色板中选中要添加的类型。")
            return
        if self.doc is None:
            return
        widget = self.doc.new_widget(wtype, parent=target)
        self.doc.checkpoint()
        self._refresh_structure()
        self._select_widget(widget)
        self._update_title()

    def _add_root_from_tree(self) -> None:
        """按调色板选中的类型新建一个顶级控件。"""
        if self.doc is None:
            QMessageBox.information(self, "没有布局",
                                    "请先打开或新建一个布局。")
            return
        wtype = self.palette_panel.current_type()
        if wtype is None:
            QMessageBox.information(self, "未选控件类型",
                                    "请先在控件调色板中选中要添加的类型。")
            return
        widget = self.doc.new_widget(wtype, parent=None)
        self.doc.checkpoint()
        self._refresh_structure()
        self._select_widget(widget)
        self._update_title()

    def promote_selected_to_root(self) -> None:
        """把当前控件提升为顶级控件（坐标换算，位置不跳）。"""
        widget = self._selected or self.tree_panel.current_widget()
        if self.doc is None or widget is None:
            QMessageBox.information(self, "未选中控件",
                                    "请先选中要提升的控件。")
            return
        if widget.parent is None:
            QMessageBox.information(self, "已是顶级控件",
                                    "这个控件本来就在顶层。")
            return
        self.doc.move_to_root(widget)
        self.doc.checkpoint()
        self._refresh_structure()
        self._select_widget(widget)
        self._update_title()

    def delete_selected(self) -> None:
        widget = self._selected or self.tree_panel.current_widget()
        if self.doc is None or widget is None:
            return
        if widget.children:
            answer = QMessageBox.question(
                self, "删除控件",
                f"控件 {widget.name} 有 {len(widget.children)} 个子控件，"
                "将一并删除，确定吗？",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                return
        parent = widget.parent
        self.doc.remove_widget(widget)
        self.doc.checkpoint()
        self._refresh_structure()
        self._select_widget(parent)
        self._update_title()

    def _reorder_widget(self, widget: Widget, delta: int) -> None:
        if self.doc is None:
            return
        siblings = self.doc.siblings_of(widget)
        index = siblings.index(widget)
        target = index + delta
        if not 0 <= target < len(siblings):
            return
        siblings[index], siblings[target] = siblings[target], siblings[index]
        self.doc.dirty = True
        self.doc.checkpoint()
        self._refresh_structure()
        self._select_widget(widget)
        self._update_title()

    def _refresh_structure(self) -> None:
        self.scene.set_document(self.doc)
        self.tree_panel.build(self.doc)

    # ------------------------------------------------------------------
    # 选择与回调
    # ------------------------------------------------------------------
    def _select_widget(self, widget: Widget | None,
                       *, sync_scene: bool = True) -> None:
        self._selected = widget
        if widget is not None:
            # 记住选择锚点：撤销重建对象后按它重解析选择
            anchor = self._selection_path(widget)
            if anchor is not None:
                self._selection_anchor = anchor
        self.props_panel.set_widget(widget)
        self.tree_panel.select_widget(widget)
        if self._syncing_selection or not sync_scene:
            return
        self._syncing_selection = True
        try:
            for item in self.scene.selectedItems():
                item.setSelected(False)
            if widget is not None:
                item = self.scene.item_for(widget)
                if item is not None:
                    item.setSelected(True)
        finally:
            self._syncing_selection = False

    def _select_from_tree(self, widget: Widget | None) -> None:
        self._select_widget(widget)

    def _on_scene_selection(self) -> None:
        if self._syncing_selection or self._loading:
            return
        try:
            selected = self.scene.selectedItems()
        except RuntimeError:
            return  # 窗口销毁过程中场景已释放，忽略残响信号
        widget = selected[0].widget if selected else None
        # 多选（Ctrl+点）时不能回灌单选同步，否则其余选中会被冲掉
        self._select_widget(widget, sync_scene=False)

    def _on_geometry_changed(self, widget: Widget) -> None:
        if self._loading or self.doc is None:
            return
        self.doc.dirty = True
        self.props_panel.refresh_values(widget)
        self._update_title()

    def _on_property_changed(self, widget: Widget, key: str) -> None:
        if self.doc is None:
            return
        self.doc.dirty = True
        self.doc.checkpoint(("prop", id(widget), key))
        self.scene.refresh_widget(widget)
        self.tree_panel.update_label(widget)
        self._update_title()

    # -- 撤销/重做 ----------------------------------------------------
    def _sync_history_actions(self) -> None:
        if not hasattr(self, "_undo_action"):
            return
        doc = self.doc
        self._undo_action.setEnabled(bool(doc and doc.can_undo))
        self._redo_action.setEnabled(bool(doc and doc.can_redo))

    def _selection_path(self, widget) -> list[int] | None:
        """选中控件的顶层序号路径，撤销重建对象后按它重解析。"""
        if widget is None or self.doc is None:
            return None
        path: list[int] = []
        node = widget
        while node is not None:
            siblings = (node.parent.children if node.parent is not None
                        else self.doc.roots)
            try:
                path.append(siblings.index(node))
            except ValueError:
                return None
            node = node.parent
        return list(reversed(path))

    def _resolve_path(self, path) -> Widget | None:
        if not path or self.doc is None:
            return None
        widgets = self.doc.roots
        node = None
        for index in path:
            if index >= len(widgets):
                return None
            node = widgets[index]
            widgets = node.children
        return node

    def undo(self) -> None:
        if self.doc is None:
            return
        path = (self._selection_path(self._selected)
                or self._selection_anchor)
        if not self.doc.undo():
            return
        self._refresh_structure()
        self._select_widget(self._resolve_path(path))
        self._update_title()

    def redo(self) -> None:
        if self.doc is None:
            return
        path = (self._selection_path(self._selected)
                or self._selection_anchor)
        if not self.doc.redo():
            return
        self._refresh_structure()
        self._select_widget(self._resolve_path(path))
        self._update_title()

    def _on_geometry_committed(self, widget: Widget) -> None:
        """拖放/缩放送手：这一次手势算撤销的一步。"""
        if self._loading or self.doc is None:
            return
        self.doc.checkpoint()
        self._update_title()

    # -- 画布像素级辅助（M3.1） ----------------------------------------
    def _on_zoom_changed(self, factor: float) -> None:
        if hasattr(self, "_zoom_label"):
            self._zoom_label.setText(f"缩放 {round(factor * 100)}%")

    def set_button_state(self, state: str) -> None:
        """切换画布按钮预览状态（多帧/竖条图取真状态图，余者模拟）。

        仅预览，不改文档；具体切法对不对以游戏内显示为准（M3.2）。
        """
        self.ctx.button_state = state
        labels = {"normal": "正常", "pressed": "按下",
                  "hover": "悬停", "disabled": "禁用"}
        for group in (self._button_state_actions,
                      getattr(self, "_button_state_btn_actions", {})):
            for key, act in group.items():
                act.setChecked(key == state)
        self.scene.refresh_all()
        self._update_status(
            f"按钮预览切到「{labels.get(state, state)}」：多帧精灵与"
            "竖条多态图显示对应状态，其余按钮为模拟效果（进游戏为准）。")

    def _toggle_grid(self, on: bool) -> None:
        self.scene.show_grid = on
        self.scene.update()

    def _selected_group(self):
        """画布多选的同级控件组；返回 (基准控件, 组内控件)。"""
        if self.doc is None:
            return None, []
        try:
            items = self.scene.selectedItems()
        except RuntimeError:
            return None, []
        widgets = [it.widget for it in items if hasattr(it, "widget")]
        if self._selected is not None and self._selected not in widgets:
            widgets.append(self._selected)
        if not widgets:
            return None, []
        # 基准取文档顺序最靠前者（可预测，状态栏会报它的名字）
        order = {id(w): i for i, w in enumerate(self.doc.all_widgets())}
        ref = min(widgets, key=lambda w: order.get(id(w), 0))
        return ref, [w for w in widgets if w.parent is ref.parent]

    def apply_alignment(self, mode: str) -> None:
        """把多选的同级控件按 mode 对齐到基准控件（默认当前选中）。"""
        if self.doc is None:
            return
        ref, group = self._selected_group()
        targets = [w for w in group if w is not ref]
        if ref is None or not targets:
            self._update_status(
                "对齐需要先在画布 Ctrl+点选至少两个同级控件。")
            return
        ref_rect = (ref.x, ref.y, ref.width, ref.height)
        for w in targets:
            x, y = snap.align_position(
                ref_rect, (w.x, w.y, w.width, w.height), mode)
            w.set_geometry(x=int(round(x)), y=int(round(y)))
            self.scene.refresh_widget(w)
        self.doc.checkpoint()
        self.doc.dirty = True
        self._update_title()
        self._update_status(f"已按基准「{ref.name}」对齐 {len(targets)} 个控件。")

    def apply_distribute(self, axis: str) -> None:
        """三个以上同级控件沿 axis 等距分布（首尾不动）。"""
        if self.doc is None:
            return
        _ref, group = self._selected_group()
        if len(group) < 3:
            self._update_status("等距分布需要至少三个同级控件被选中。")
            return
        rects = [(w.x, w.y, w.width, w.height) for w in group]
        for w, (x, y) in zip(
                group, snap.distribute_positions(rects, axis), strict=True):
            w.set_geometry(x=int(round(x)), y=int(round(y)))
            self.scene.refresh_widget(w)
        self.doc.checkpoint()
        self.doc.dirty = True
        self._update_title()
        direction = "横" if axis == "x" else "纵"
        self._update_status(f"已沿{direction}向等距分布 {len(group)} 个控件。")

    # ------------------------------------------------------------------
    # 视图/状态
    # ------------------------------------------------------------------
    def _toggle_names(self, on: bool) -> None:
        self.ctx.show_names = on
        self.scene.refresh_all()

    def _update_title(self) -> None:
        self._sync_history_actions()
        name = self.doc.display_name if self.doc else "未打开布局"
        star = "*" if self.doc and self.doc.dirty else ""
        self.setWindowTitle(f"{name}{star} — MXSJ UI 编辑器 {__version__}")

    def _update_status(self, text: str) -> None:
        self.statusBar().showMessage(text)

    def _about(self) -> None:
        QMessageBox.about(
            self, "关于 MXSJ UI 编辑器",
            f"MXSJ UI 编辑器 {__version__}\n\n"
            "可视化编辑客户端 UI 布局（.dlg）：打开现有布局改、"
            "或从空白新建。\n布局格式、路径哈希与解密均来自本仓库"
            "逆向结案成果。")

    def closeEvent(self, event) -> None:  # noqa: N802
        if not self._confirm_discard():
            event.ignore()
            return
        self.resolver.close()
        super().closeEvent(event)

