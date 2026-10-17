"""主窗口：文件/资源工作流与五大区域的组装。

布局：左侧（布局文件树 + 控件树）、中央画布、右侧（属性面板 +
控件调色板）。打开来源两种：散装 ``.dlg`` 文件/目录，以及从
``interface.fls`` 等资源包按路径直开（自动解密）；保存可写散装
``.dlg``，也可生成写回布局的新资源包（原包不动，见 M1）。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QMimeData, QSettings, QSize, Qt
from PySide6.QtGui import QAction, QGuiApplication, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..core import dlg_codec, pack_build, publish, snap
from ..core.assets import AssetResolver
from ..core.catalog import known_layout_paths
from ..core.diagnostics import (
    Diagnostic,
    diagnose,
    reference_impacts,
    widget_at_path,
)
from ..core.layout_import import prepare_layout_import, validate_layout_path
from ..core.model import LayoutDocument, Widget
from ..core.output_paths import guard_output
from ..core.pack import FlsPack
from ..core.painters import PaintContext
from ..core.review import referenced_staged_images
from ..core.script_index import ScriptIndex, get_default_index
from ..core.styles import StyleBook
from . import icons
from .canvas import CanvasView, LayoutScene
from .diagnostics_panel import DiagnosticsPanel
from .layout_import_dialog import LayoutImportDialog
from .panels import PalettePanel, ResourceTreePanel, WidgetTreePanel
from .property_panel import PropertyPanel
from .save_review import SaveReviewDialog
from .script_panel import ScriptPanel


class MainWindow(QMainWindow):
    """UI 编辑器主窗口。"""

    def __init__(self) -> None:
        super().__init__()
        self._settings = QSettings("MXSJ", "UIEditor")
        self.resolver = AssetResolver()
        paths = self._settings.value("known_layout_paths", [])
        if isinstance(paths, str):
            paths = [paths]
        if isinstance(paths, (list, tuple)):
            for path in paths:
                try:
                    self.resolver.remember_layout(path)
                except (ValueError, TypeError, AttributeError):
                    pass  # 损坏设置不阻塞启动，也不加入候选
        self.styles = StyleBook()
        self.ctx = PaintContext(assets=self.resolver, styles=self.styles)
        self.script_index: ScriptIndex = get_default_index()
        self.doc: LayoutDocument | None = None
        self._selected: Widget | None = None
        self._selection_anchor: list[int] | None = None
        self._syncing_selection = False
        self._loading = False

        self.scene = LayoutScene(self.ctx, self._on_geometry_changed,
                                 self._on_geometry_committed)
        self.view = CanvasView(self.scene)
        self.view.context_menu_handler = self._show_canvas_context_menu
        self.setCentralWidget(self.view)

        self.resource_panel = ResourceTreePanel()
        self.tree_panel = WidgetTreePanel()
        self.script_panel = ScriptPanel()
        self.props_panel = PropertyPanel()
        self.props_panel.assets = self.resolver  # 文件字段从包里选
        self.props_panel.before_change = self._before_property_change
        self.diagnostics_panel = DiagnosticsPanel()
        self.diagnostics_panel.refresh_requested.connect(self.run_diagnostics)
        self.diagnostics_panel.path_chosen.connect(self._select_diagnostic_path)
        self.palette_panel = PalettePanel()
        self._build_docks()
        self._build_menus()
        self._connect_signals()
        # 删除键由「删除控件」QAction 统一接管（_edit_delete 带文本焦点分流）

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
        left_tabs.addTab(self.script_panel, "脚本")
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
        diagnostics = QDockWidget("布局诊断（静态）", self)
        diagnostics.setWidget(self.diagnostics_panel)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, diagnostics)

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
        self._add_action(view_menu, "刷新布局诊断", self.run_diagnostics,
                         QKeySequence("Ctrl+Shift+D"))
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
        self._act_aspect = QAction("等比缩放", self, checkable=True)
        self._act_aspect.setToolTip(
            "打开后拖动把手缩放控件时保持宽高比，图片不变形；"
            "关着时按住 Shift 拖动也可临时等比")
        self._act_aspect.toggled.connect(self._toggle_aspect)
        view_menu.addAction(self._act_aspect)
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
        edit_menu.addSeparator()
        self._act_copy = QAction("复制控件", self)
        self._act_copy.setShortcut(QKeySequence.StandardKey.Copy)
        self._act_copy.triggered.connect(self._edit_copy)
        self._act_copy.setEnabled(False)
        edit_menu.addAction(self._act_copy)
        self._act_paste = QAction("粘贴控件", self)
        self._act_paste.setShortcut(QKeySequence.StandardKey.Paste)
        self._act_paste.triggered.connect(self._edit_paste)
        self._act_paste.setEnabled(False)
        edit_menu.addAction(self._act_paste)
        self._act_delete = QAction("删除控件", self)
        self._act_delete.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        self._act_delete.triggered.connect(self._edit_delete)
        self._act_delete.setEnabled(False)
        edit_menu.addAction(self._act_delete)
        edit_menu.addSeparator()
        self._act_lock = QAction("锁定控件", self, checkable=True)
        self._act_lock.setShortcut(QKeySequence("Ctrl+L"))
        self._act_lock.setToolTip(
            "锁定/解锁选中的控件：锁住后在画布上拖不动、缩不了、删不掉，"
            "排其他控件时防手滑碰歪（Ctrl+L）。锁定只在编辑器里生效，"
            "不写进布局文件；父控件锁定不影响其子控件。")
        self._act_lock.toggled.connect(self._toggle_lock)
        self._act_lock.setEnabled(False)
        edit_menu.addAction(self._act_lock)

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
        self._act_aspect.setIcon(icons.icon_aspect())
        self._act_aspect.setIconText("等比")
        bar.addAction(self._act_aspect)
        self._act_lock.setIcon(icons.icon_lock())
        self._act_lock.setIconText("锁定")
        bar.addAction(self._act_lock)
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
        self.resource_panel.import_pack_layout.connect(self.import_pack_layout)
        self.resource_panel.open_pack_path.connect(self.open_pack_path)
        self.resource_panel.open_loose_file.connect(self.open_layout_file)
        self.resource_panel.choose_resource_dir.connect(
            self.open_resource_dir_dialog)
        self.resource_panel.choose_loose_dir.connect(
            self.open_layout_dir_dialog)
        self.script_panel.name_chosen.connect(self._select_by_name)
        self.tree_panel.lock_toggled.connect(
            lambda widget, on: self._apply_lock([widget], on))
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
        if self.doc is None or not (self.doc.dirty or self.doc.pending_pack_import):
            return True
        answer = QMessageBox.question(
            self, "未保存的修改",
            "当前布局有未保存的修改，确定丢弃吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return answer == QMessageBox.StandardButton.Yes

    def _set_document(self, doc: LayoutDocument | None) -> None:
        self._loading = True
        self.resource_panel.clear_pending()
        self.doc = doc
        self.diagnostics_panel.reset()
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
        link_note = self._apply_script_link(doc)
        self._update_status(
            f"已打开 {doc.display_name if doc else '—'}：{count} 个控件。"
            f"{self.resolver.summary}；"
            f"样式表："
            f"{'已加载 ui.lst' if self.styles.loaded else '未加载（默认字体）'}"
            f"{link_note}")

    # -- 脚本联动（静态索引） ---------------------------------------
    def _doc_layout_path(self, doc: LayoutDocument | None) -> str | None:
        """当前文档对应的布局资源路径（包内路径优先，其次散装反查）。"""
        if doc is None:
            return None
        if doc.source_pack:
            return doc.source_pack[1]
        if doc.source_path:
            return self.script_index.match_loose_path(doc.source_path)
        return None

    def _script_link(self):
        return self.script_index.for_layout(self._doc_layout_path(self.doc))

    @staticmethod
    def _impact_text(impacts) -> str:
        lines = []
        for impact in impacts:
            lines.append(f"· {impact.name}")
            lines.extend(f"  {detail}" for detail in impact.details)
        return "\n".join(lines)

    def _before_property_change(self, widget: Widget, key: str, value) -> bool:
        if key != "sName" or value == widget.props.get(key):
            return True
        if not isinstance(value, str):
            QMessageBox.warning(self, "控件名无效", "sName 必须是字符串。")
            return False
        if self.doc and value and any(other is not widget and other.name == value
                                      for other in self.doc.all_widgets()):
            QMessageBox.warning(self, "控件名重复",
                                f"布局中已有控件名 {value!r}，请使用唯一名字。")
            return False
        impacts = reference_impacts([widget.name], self._script_link())
        if not impacts:
            return True  # 索引未命中不代表安全，诊断与脚本面板持续说明边界。
        return QMessageBox.question(
            self, "改名可能影响脚本引用（静态）",
            f"将 {widget.name!r} 改为 {value!r}。静态索引发现：\n"
            + self._impact_text(impacts)
            + "\n\n继续只修改布局，不会改写脚本或自动接线。"
              "索引可能漏动态引用或版本变化。确定继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes

    def _layout_diagnostics(self) -> list[Diagnostic]:
        if self.doc is None:
            return []
        return diagnose(
            self.doc, link=self._script_link(),
            resource_exists=(self.resolver.resource_exists
                             if self.resolver.has_sources else None),
            staged_paths=self.resolver.staged_images())

    def run_diagnostics(self) -> None:
        self.diagnostics_panel.set_issues(self._layout_diagnostics())

    def _select_diagnostic_path(self, path: tuple[int, ...]) -> None:
        if self.doc is None:
            return
        widget = widget_at_path(self.doc, path)
        if widget is not None:
            self._select_widget(widget)
            item = self.scene.item_for(widget)
            if item is not None:
                self.view.ensureVisible(item)

    def _apply_script_link(self, doc: LayoutDocument | None) -> str:
        """按文档路径挂上脚本关联（面板+代码皮肤），返回状态栏注记。"""
        path = self._doc_layout_path(doc)
        link = self.script_index.for_layout(path) if path else None
        self.ctx.code_skins = (
            {name: refs[0] for name, refs in link.skins.items() if refs}
            if link else {})
        self.script_panel.set_link(path, link)
        if link is None:
            return ""
        claimed = len(set(link.objects) | set(link.skins))
        return (f"；脚本关联：{len(link.modules)} 个模块引用此布局，"
                f"{claimed} 个控件被脚本取用、{len(link.skins)} 个"
                "按代码皮肤预览（静态推断，见左侧「脚本」页）")

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
                f"该资源包内没有已识别的布局：\n{path}\n\n"
                "（图片等其它资源已照常挂载，打开布局时可自动取图；"
                "可在左侧包节点右键导入本地布局。）")
        elif count > 0:
            self._update_status(
                f"已挂载 {Path(path).name}：识别到 {count} 个布局，"
                "在左侧资源树双击（可先按名称搜索）即可打开。")

    def _remember_layout(self, path: str) -> None:
        self.resolver.remember_layout(path)
        paths = sorted(set(self.resolver._session_layouts.values()), key=str.casefold)
        self._settings.setValue("known_layout_paths", paths)
        self._settings.sync()

    def open_pack_path(self, pack_path: str) -> None:
        path, ok = QInputDialog.getText(
            self, "按包内路径打开布局",
            "填写导入时的完整路径（如 login/regform.dlg）。\n"
            "只读核查，不会再次导入或改写资源包：")
        if not ok:
            return
        try:
            path = validate_layout_path(path)
            result = self.resolver.fetch_pack_dlg(pack_path, path)
            if result is None:
                raise ValueError("该包中找不到可解析布局；"
                                 "请核对保存的新包和当时填写的路径。")
            doc = LayoutDocument.from_dicts(*result)
        except Exception as exc:
            QMessageBox.warning(self, "按路径打开失败", str(exc))
            return
        if not self._confirm_discard():
            return
        doc.source_pack = (pack_path, path)
        self._remember_layout(path)
        self.resource_panel.add_known_layout(pack_path, path)
        self._set_document(doc)
        self.resource_panel._search.clear()
        self.resource_panel.expand_pack(pack_path)
        self.resource_panel.reveal_selection(("pack", pack_path, path))

    def import_pack_layout(self, pack_path: str) -> None:
        """本地 .dlg 导入到单一编辑文档，实际写入只在生成新包时。"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "选择本地布局文件", "", "布局文件 (*.dlg);;所有文件 (*)")
        if not filename:
            return
        dialog = LayoutImportDialog(Path(filename).name,
                                    self.resolver.scan_layouts(pack_path), self)
        if dialog.exec() != QDialog.Accepted:
            return
        try:
            with FlsPack(pack_path) as pack:
                doc, replacing = prepare_layout_import(
                    pack, dialog.path, Path(filename).read_bytes())
        except Exception as exc:
            QMessageBox.warning(self, "导入布局失败", str(exc))
            return
        if replacing:
            answer = QMessageBox.question(
                self, "确认替换布局",
                f"包内 {dialog.path} 已存在。保存新包时将替换该布局，继续吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                return
        if not self._confirm_discard():
            return
        doc.source_pack = (pack_path, dialog.path)
        self._set_document(doc)
        self.resource_panel.show_pending(pack_path, dialog.path)
        self._update_status(
            f"已导入 {dialog.path}（待入新包），可预览/编辑；"
            "保存前查看改动清单。未带图片，未接脚本，原包未修改。")

    def _open_pack_layout(self, pack_path: str, res_path: str,
                          skip_discard: bool = False) -> None:
        """从包中打开一个布局（树双击与对话框共用）。包顺带入树。"""
        if (self.doc and self.doc.pending_pack_import
                and self.doc.source_pack == (pack_path, res_path)):
            self.resource_panel.reveal_selection(("pending", pack_path, res_path))
            return
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
        result = self.resolver.fetch_pack_dlg(pack_path, res_path)
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
                skipped += 1  # 无已识别布局也入树，允许右键新增
            self._add_pack_to_tree(str(pack_file), layouts)
            added += 1
        self._try_load_styles()
        self.scene.refresh_all()
        self._update_status(
            f"资源目录：{path}；新入树 {added} 个包"
            f"（其中 {skipped} 个无已识别布局，可右键导入）。{self.resolver.summary}；"
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
        frame.props["sTitle"] = "新對話框"
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
        return referenced_staged_images(self.doc.to_dicts(),
                                        self.resolver.staged_images())

    def _confirm_save_review(self, target: str, *, to_pack: bool) -> bool:
        """保存前清单：数据部分在 `core.publish.save_review_plan`，这里只弹窗。"""
        if self.doc is None:
            return False
        try:
            guard_output(target, self._pack_sources())
            pack_path, res_path = (self.doc.source_pack
                                   if self.doc.source_pack else (None, None))
            plan = publish.save_review_plan(
                target=target, to_pack=to_pack,
                issues=self._layout_diagnostics(),
                staged=self.resolver.staged_images(),
                extras=self._referenced_staged_images(),
                pack_path=pack_path, res_path=res_path,
                pending_pack_import=self.doc.pending_pack_import,
                new_plain=dlg_codec.dump_bytes(self.doc.to_dicts()))
            dialog = SaveReviewDialog(target, self.doc.changes(), plan.issues,
                                      plan.images, to_pack=to_pack,
                                      parent=self, layout_notice=plan.notice)
            return dialog.exec() == QDialog.Accepted
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "保存前检查失败", str(exc))
            return False


    def _require_save_encoding(self, extras: dict[str, bytes]) -> None:
        """写回前的编码闸门（实现见 `core.publish.require_save_encoding`）。"""
        publish.require_save_encoding(self.doc, extras)

    @staticmethod
    def _fresh_pack_readback(pack_path, res_path: str, names):
        """回读钩子：用**全新**解析器读目标布局与各新图（`core.publish` 注入用）。

        故意不复用当前窗口的 resolver：新包是在别处写出来的，
        用它自己的解析器回读才算独立验证。
        """
        fresh = AssetResolver()
        fresh.mount_pack(str(pack_path))
        try:
            got = fresh.fetch_dlg(res_path)
            dicts = None if got is None else got[0]
            return dicts, {name: fresh.fetch_bytes(name) for name in names}
        finally:
            fresh.close()

    def write_pack_copy(self, out_path: str) -> dict | None:
        """把当前包内布局写回一个新包文件（原包不动）。返回校验报告。

        选图窗新加且被本布局引用到的图片随布局一并写入（按路径
        新增或替换）。写后硬性校验（条目数、目录升序、条目集合、
        二分命中、未改条目保真、全新解析器回读）已抽到
        :mod:`ui_editor.core.publish`——那是保存链最危险的一段，
        现在能脱离窗口直接测（分析报告建议④）；任一不过填
        ``report["error"]`` 并返回（弹错在对话框层）。
        """
        if self.doc is None or not self.doc.source_pack:
            return None
        src_pack, res_path = self.doc.source_pack
        extras = self._referenced_staged_images()
        self._require_save_encoding(extras)
        plain = dlg_codec.dump_bytes(self.doc.to_dicts())
        tmp_out = str(out_path)
        info = pack_build.patch_pack_copy(
            src_pack, res_path, plain, tmp_out, extra_entries=extras,
            protected_paths=self._pack_sources(),
            allow_create=self.doc.pending_pack_import)
        report: dict = {"out": tmp_out, "bytes": info["bytes"],
                        "mode": info["mode"],
                        "layout_added": bool(info.get("layout_added")),
                        "native_layout_storage": bool(
                            info.get("native_layout_storage")),
                        "images_added": len(info["images_added"]),
                        "images_replaced": len(info["images_replaced"])}
        staged_all = set(self.resolver.staged_images())
        report["staged_unreferenced"] = sorted(staged_all - set(extras))
        target_write = publish.classify_target_path(src_pack, res_path, plain)
        report["target_write"] = target_write.summary
        report["target_write_kind"] = target_write.storage
        report.update(publish.verify_written_pack(
            src_pack=src_pack, out_path=tmp_out, res_path=res_path,
            extras=extras, expected_dicts=self.doc.to_dicts(), info=info,
            read_back=self._fresh_pack_readback))
        if not report.get("ok"):
            return report
        # 状态迁移：已验证落盘，标记干净并让后续保存续写新包
        self.resolver.mount_pack(tmp_out, priority=True)
        self._remember_layout(res_path)
        self._add_pack_to_tree(tmp_out, self.resolver.scan_layouts(tmp_out))
        self.doc.pending_pack_import = False
        self.resource_panel.clear_pending()
        self.doc.mark_saved()
        self.doc.source_pack = (tmp_out, res_path)
        self.resource_panel.expand_pack(tmp_out)
        self.resource_panel.reveal_selection(("pack", tmp_out, res_path))
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
        if not self._confirm_save_review(path, to_pack=True):
            return
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
        fast = report.get("mode") in ("inplace", "relocated", "added")
        images_note = ""
        if report.get("images_added") or report.get("images_replaced"):
            images_note = (
                f"\n一并写入新图 {report.get('images_added', 0)} 张、"
                f"替换图片 {report.get('images_replaced', 0)} 张。")
        tail = ("原包未被修改。安装时请在完整客户端副本上操作：先备份"
                "原包，再把新包改名替换，最后进游戏验证该界面。")
        entries_note = ""
        if report.get("entries_after") is not None:
            entries_note = (
                f"\n新包条目总数：{report['entries_after']} 条"
                "（用资源编辑器打开新包应能对上这个数）。")
        unused = report.get("staged_unreferenced") or []
        unused_note = ""
        if unused:
            shown = "\n".join(f"· {name}" for name in unused[:6])
            if len(unused) > 6:
                shown += f"\n· ……等共 {len(unused)} 张"
            unused_note = (
                f"\n\n⚠ 有 {len(unused)} 张「添加新图到包」的图片未被"
                "当前布局引用，未写入新包：\n" + shown
                + "\n要写入：先在本布局的控件上把图片改选为上面列出的"
                "新图（或在该图片所在的布局里保存），再保存回包。")
        box = (QMessageBox.warning if unused
               else QMessageBox.information)
        box(self, "已生成新包" if not unused else "已生成新包（有新图未写入）",
            f"已写回：{res_path}\n新包：{path}\n"
            f"条目校验通过（改变 {report.get('changed_entries', 0)} 条，"
            f"大小 {report['bytes']} 字节"
            + ("，快速补丁未重写整包" if fast else "") + "）。"
            + "\n布局已按原生路径密钥写入并回读验证。\n"
            + str(report.get("target_write", ""))
            + images_note + entries_note + unused_note + "\n\n" + tail)

    def save_as(self, path: str | None = None) -> bool:
        if self.doc is None:
            return False
        if path is None:
            path, _ = QFileDialog.getSaveFileName(
                self, "另存为布局", self.doc.display_name,
                "布局文件 (*.dlg);;所有文件 (*)")
            if not path:
                return False
        if not self._write_to(str(path)):
            return False
        self.doc.source_path = str(path)
        self.doc.source_pack = None
        self._update_title()
        return True

    def _pack_sources(self) -> list[Path]:
        sources = self.resolver.pack_paths
        if self.doc and self.doc.source_pack:
            sources.append(Path(self.doc.source_pack[0]))
        # 同一客户端资源目录中尚未挂载的包也不能被另存覆盖。
        directories = {source.parent for source in sources}
        for directory in directories:
            sources.extend(path for path in directory.iterdir()
                           if path.suffix.lower() == ".fls")
        return sources

    def _write_to(self, path: str) -> bool:
        if self.doc is None:
            return False
        try:
            guard_output(path, self._pack_sources())
            if not self._confirm_save_review(path, to_pack=False):
                return False
            self._require_save_encoding({})
            data = dlg_codec.dump_bytes(self.doc.to_dicts())
            Path(path).write_bytes(data)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "保存失败", str(exc))
            return False
        self.doc.mark_saved()
        self._update_title()
        self._update_status(f"已保存：{path}")
        return True

    def export_png(self) -> None:
        if self.doc is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "导出 PNG", self.doc.display_name + ".png",
            "PNG 图片 (*.png)")
        if not path:
            return
        sources = self._pack_sources()
        if self.doc.source_path:
            sources.append(Path(self.doc.source_path))
        try:
            guard_output(path, sources)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "导出失败", str(exc))
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

    # -- 画布右键菜单与复制/粘贴/删除 --------------------------------
    _MIME_WIDGETS = "application/x-mxsj-widget+json"

    def _selected_widgets(self) -> list[Widget]:
        """当前生效的多选控件（按文档顺序，祖先已选则不带其子孙）。"""
        if self.doc is None:
            return []
        try:
            items = self.scene.selectedItems()
        except RuntimeError:
            items = []
        picked = [item.widget for item in items]
        if not picked and self._selected is not None:
            picked = [self._selected]
        chosen = {id(w) for w in picked}

        def has_chosen_ancestor(w: Widget) -> bool:
            node = w.parent
            while node is not None:
                if id(node) in chosen:
                    return True
                node = node.parent
            return False

        order = {id(w): i for i, w in enumerate(self.doc.all_widgets())}
        return sorted((w for w in picked if not has_chosen_ancestor(w)),
                      key=lambda w: order.get(id(w), 0))

    def _focused_text_editor(self):
        """焦点在文本输入里时，复制/粘贴/删除应作用于文本而非控件。"""
        fw = QApplication.focusWidget()
        if isinstance(fw, (QLineEdit, QTextEdit, QPlainTextEdit)):
            return fw
        return None

    def _edit_copy(self) -> None:
        fw = self._focused_text_editor()
        if fw is not None:
            fw.copy()
            return
        self.copy_selected_widgets()

    def _edit_paste(self) -> None:
        fw = self._focused_text_editor()
        if fw is not None:
            fw.paste()
            return
        self.paste_widgets()

    def _edit_delete(self) -> None:
        fw = self._focused_text_editor()
        if fw is not None:
            if isinstance(fw, QLineEdit):
                fw.del_() if hasattr(fw, "del_") else fw.backspace()
            else:
                fw.textCursor().removeSelectedText()
            return
        self.delete_selected()

    def copy_selected_widgets(self) -> None:
        """把选中的控件（含子树）序列化进系统剪贴板。"""
        import json

        widgets = self._selected_widgets()
        if not widgets:
            return
        payload = json.dumps([w.to_dict() for w in widgets],
                             ensure_ascii=False).encode("utf-8")
        mime = QMimeData()
        mime.setData(self._MIME_WIDGETS, payload)
        mime.setText(payload.decode("utf-8"))
        QGuiApplication.clipboard().setMimeData(mime)
        self._sync_edit_actions()
        self._update_status(f"已复制 {len(widgets)} 个控件")

    def _clipboard_payload(self) -> list[dict] | None:
        """读剪贴板中的控件负载（本工具复制的），无效返回 None。"""
        import json

        clipboard = QGuiApplication.clipboard()
        mime = clipboard.mimeData()
        raw = None
        if mime is not None and mime.hasFormat(self._MIME_WIDGETS):
            raw = bytes(mime.data(self._MIME_WIDGETS))
        elif mime is not None and mime.hasText():
            raw = mime.text().encode("utf-8")
        if not raw:
            return None
        try:
            data = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None
        if (not isinstance(data, list) or not data
                or not all(isinstance(d, dict) for d in data)):
            return None
        return data

    def paste_widgets(self) -> None:
        """把剪贴板控件粘进文档：作为当前选中控件的同级（无选择挂顶层）。

        位置统一偏移 (16,16) 免与原件重叠；整组粘贴算一步撤销。
        名字保持原样（脚本按 sName 认领，需要改名请在属性面板改）。
        """
        if self.doc is None:
            return
        payload = self._clipboard_payload()
        if not payload:
            return
        clones = [Widget.from_dict(d) for d in payload]
        selection = self._selected_widgets()
        anchor = selection[0] if selection else None
        parent = anchor.parent if anchor is not None else None
        siblings = (parent.children if parent is not None
                    else self.doc.roots)
        index = (siblings.index(anchor) + 1 if anchor is not None
                 else None)
        for clone in clones:
            clone.set_geometry(x=clone.x + 16, y=clone.y + 16)
            self.doc.insert_widget(clone, parent,
                                   None if index is None else index)
            if index is not None:
                index += 1
        self.doc.checkpoint()
        self._refresh_structure()
        self._select_widget(clones[0])
        self._update_title()
        self._update_status(f"已粘贴 {len(clones)} 个控件")

    def delete_selected(self) -> None:
        if self.doc is None:
            return
        targets = self._selected_widgets()
        if not targets:
            current = self.tree_panel.current_widget()
            targets = [current] if current is not None else []
        if not targets:
            return
        blocked = [w for w in targets
                   if any(node.locked for node in w.walk())]
        if blocked:
            targets = [w for w in targets if w not in blocked]
            names = "、".join(w.name or "(无名)" for w in blocked[:3])
            self._update_status(
                f"「{names}」已锁定（或其内有锁定控件），先解锁再删除。")
            if not targets:
                return
        descendants = sum(len(list(w.walk())) - 1 for w in targets)
        impacts = reference_impacts(
            (node.name for root in targets for node in root.walk()),
            self._script_link())
        if descendants or impacts:
            note = ("\n\n静态索引发现受影响引用（包含整棵子树）：\n"
                    + self._impact_text(impacts)
                    + "\n只删除布局控件，不改脚本，不自动接线；"
                      "静态索引可能漏动态引用或版本变化。"
                    if impacts else "")
            answer = QMessageBox.question(
                self, "删除控件" if not impacts else "删除可能影响脚本引用（静态）",
                f"将删除 {len(targets)} 个控件及其 {descendants} 个"
                "子控件，确定吗？" + note,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                return
        parent = targets[0].parent
        for widget in targets:
            self.doc.remove_widget(widget)
        self.doc.checkpoint()
        self._refresh_structure()
        self._select_widget(parent)
        self._update_title()

    def _sync_edit_actions(self) -> None:
        """按选择与剪贴板状态置灰复制/粘贴/删除（菜单与右键菜单共用）。"""
        has_widgets = self.doc is not None and bool(self._selected_widgets())
        self._act_copy.setEnabled(has_widgets)
        self._act_delete.setEnabled(has_widgets)
        self._act_paste.setEnabled(
            self.doc is not None and self._clipboard_payload() is not None)
        self._sync_lock_action()

    # -- 控件锁定（布局时防手滑；编辑器状态，不进文档/撤销） ------
    def _sync_lock_action(self) -> None:
        """锁定按钮按当前选择置灰/勾选（全锁才打勾，不回弹信号）。"""
        from PySide6.QtCore import QSignalBlocker

        if not hasattr(self, "_act_lock"):
            return
        widgets = self._selected_widgets() if self.doc is not None else []
        self._act_lock.setEnabled(bool(widgets))
        with QSignalBlocker(self._act_lock):
            self._act_lock.setChecked(
                bool(widgets) and all(w.locked for w in widgets))

    def _toggle_lock(self, on: bool) -> None:
        widgets = self._selected_widgets()
        if widgets:
            self._apply_lock(widgets, on)

    def _apply_lock(self, widgets: list, on: bool) -> None:
        """把锁定状态应用到一组控件（工具栏/右键/控件树共用）。"""
        for widget in widgets:
            widget.locked = on
            item = self.scene.item_for(widget)
            if item is not None:
                item.apply_lock()
            self.tree_panel.set_lock_icon(widget)
        self._sync_lock_action()
        names = "、".join(w.name or "(无名)" for w in widgets[:3])
        if len(widgets) > 3:
            names += " 等"
        self._update_status(
            f"已锁定 {len(widgets)} 个控件（{names}）：画布上拖不动、"
            "缩不了、删不掉；排其他控件不会碰歪它们。再点一次解锁。"
            if on else
            f"已解锁 {len(widgets)} 个控件（{names}）。")

    def _locked_paths(self) -> list[list[int]]:
        """全部已锁定控件的序号路径（撤销重建对象后按它恢复锁定）。"""
        if self.doc is None:
            return []
        paths = []
        for widget in self.doc.all_widgets():
            if widget.locked:
                path = self._selection_path(widget)
                if path is not None:
                    paths.append(path)
        return paths

    def _restore_locks(self, paths: list[list[int]]) -> None:
        for path in paths:
            widget = self._resolve_path(path)
            if widget is None:
                continue
            widget.locked = True
            item = self.scene.item_for(widget)
            if item is not None:
                item.apply_lock()
        self.tree_panel.refresh_locks()

    def build_canvas_context_menu(self, widget: Widget | None) -> QMenu:
        """画布右键菜单（不在此处 exec，便于测试与复用）。"""
        if widget is not None and widget not in self._selected_widgets():
            self._select_widget(widget)
        self._sync_edit_actions()
        menu = QMenu(self)
        menu.addAction(self._act_copy)
        menu.addAction(self._act_paste)
        menu.addAction(self._act_delete)
        menu.addSeparator()
        menu.addAction(self._act_lock)
        return menu

    def _show_canvas_context_menu(self, global_pos, widget) -> None:
        if self.doc is None:
            return
        self.build_canvas_context_menu(widget).exec(global_pos)

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
        if hasattr(self, "script_panel"):
            self.script_panel.set_widget(widget)
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
        self._sync_lock_action()

    def _select_from_tree(self, widget: Widget | None) -> None:
        self._select_widget(widget)

    def _select_by_name(self, name: str) -> None:
        """脚本面板点名字：按 sName 在画布上选中对应控件。"""
        if self.doc is None:
            return
        for widget in self.doc.all_widgets():
            if widget.name == name:
                self._select_widget(widget)
                return

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
        self._sync_edit_actions()

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
        if key == "sName":
            self.props_panel.refresh_label(widget)
            self.script_panel.set_widget(widget)
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
        locked_paths = self._locked_paths()
        if not self.doc.undo():
            return
        self._refresh_structure()
        self._restore_locks(locked_paths)  # 锁定不进时间线，手动恢复
        self._select_widget(self._resolve_path(path))
        self._sync_lock_action()
        self._update_title()

    def redo(self) -> None:
        if self.doc is None:
            return
        path = (self._selection_path(self._selected)
                or self._selection_anchor)
        locked_paths = self._locked_paths()
        if not self.doc.redo():
            return
        self._refresh_structure()
        self._restore_locks(locked_paths)
        self._select_widget(self._resolve_path(path))
        self._sync_lock_action()
        self._update_title()

    def _on_geometry_committed(self, widget: Widget) -> None:
        """拖放/缩放送手：这一次手势算撤销的一步。"""
        if self._loading or self.doc is None:
            return
        self.doc.checkpoint()
        self._update_title()

    # -- 画布像素级辅助（M3.1） ----------------------------------------
    def _on_zoom_changed(self, factor: float) -> None:
        # 窗口销毁过程中画布可能补发缩放信号，此时标签的 C++ 对象
        # 已删除（只剩 Python 壳），setText 会抛 RuntimeError。
        from shiboken6 import isValid

        label = getattr(self, "_zoom_label", None)
        if label is not None and isValid(label):
            label.setText(f"缩放 {round(factor * 100)}%")

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

    def _toggle_aspect(self, on: bool) -> None:
        self.scene.keep_aspect = on
        self._update_status(
            "等比缩放已打开：拖动把手时宽高按原比例一起变，图片不变形。"
            if on else
            "等比缩放已关闭：拖动把手自由缩放（按住 Shift 拖动可临时等比）。")

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
        targets = [w for w in group if w is not ref and not w.locked]
        if ref is None or not targets:
            self._update_status(
                "对齐需要先在画布 Ctrl+点选至少两个同级控件"
                "（锁定控件不会被移动）。")
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
        group = [w for w in group if not w.locked]  # 锁定的不参与挪位
        if len(group) < 3:
            self._update_status(
                "等距分布需要至少三个未锁定的同级控件被选中。")
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
        self.diagnostics_panel.mark_stale()
        name = self.doc.display_name if self.doc else "未打开布局"
        pending = self.doc and (self.doc.dirty or self.doc.pending_pack_import)
        star = "*" if pending else ""
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

