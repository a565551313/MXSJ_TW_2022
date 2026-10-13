"""主窗口：文件/资源工作流与五大区域的组装。

布局：左侧（布局文件树 + 控件树）、中央画布、右侧（属性面板 +
控件调色板）。打开来源两种：散装 ``.dlg`` 文件/目录，以及从
``interface.fls`` 等资源包按路径直开（自动解密）。保存一期只写
散装 ``.dlg``（回写包内放二期）。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..core import dlg_codec
from ..core.assets import AssetResolver
from ..core.catalog import known_layout_paths
from ..core.model import LayoutDocument, Widget
from ..core.painters import PaintContext
from ..core.styles import StyleBook
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
        self._syncing_selection = False
        self._loading = False

        self.scene = LayoutScene(self.ctx, self._on_geometry_changed)
        self.view = CanvasView(self.scene)
        self.setCentralWidget(self.view)

        self.resource_panel = ResourceTreePanel()
        self.tree_panel = WidgetTreePanel()
        self.props_panel = PropertyPanel()
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
        self._add_action(file_menu, "打开布局文件…", self.open_layout_file_dialog,
                         QKeySequence.StandardKey.Open)
        self._add_action(file_menu, "打开布局目录…", self.open_layout_dir_dialog)
        self._add_action(file_menu, "从资源包打开布局…", self.open_from_pack)
        self._add_action(file_menu, "从资源目录打开布局…",
                         self.open_resource_dir_dialog)
        file_menu.addSeparator()
        self._add_action(file_menu, "新建布局", self.new_layout,
                         QKeySequence.StandardKey.New)
        self._add_action(file_menu, "保存", self.save,
                         QKeySequence.StandardKey.Save)
        self._add_action(file_menu, "另存为…", lambda: self.save_as())
        self._add_action(file_menu, "导出 PNG…", self.export_png)
        file_menu.addSeparator()
        self._add_action(file_menu, "退出", self.close,
                         QKeySequence.StandardKey.Quit)

        view_menu = self.menuBar().addMenu("视图")
        self._add_action(view_menu, "适应窗口", self.view.fit_content)
        self._add_action(view_menu, "实际大小（100%）", self.view.actual_size)
        names_action = QAction("显示占位/控件名标注", self, checkable=True)
        names_action.setChecked(True)
        names_action.toggled.connect(self._toggle_names)
        view_menu.addAction(names_action)

        help_menu = self.menuBar().addMenu("帮助")
        self._add_action(help_menu, "关于", self._about)

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
            QMessageBox.information(
                self, "保存为散装文件",
                "一期暂不支持回写资源包（.fls），请另存为散装 .dlg。")
            self.save_as()
        else:
            self.save_as()

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
        self._refresh_structure()
        self._select_widget(widget)
        self._update_title()

    def _refresh_structure(self) -> None:
        self.scene.set_document(self.doc)
        self.tree_panel.build(self.doc)

    # ------------------------------------------------------------------
    # 选择与回调
    # ------------------------------------------------------------------
    def _select_widget(self, widget: Widget | None) -> None:
        self._selected = widget
        self.props_panel.set_widget(widget)
        self.tree_panel.select_widget(widget)
        if self._syncing_selection:
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
        self._select_widget(widget)

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
        self.scene.refresh_widget(widget)
        self.tree_panel.update_label(widget)
        self._update_title()

    # ------------------------------------------------------------------
    # 视图/状态
    # ------------------------------------------------------------------
    def _toggle_names(self, on: bool) -> None:
        self.ctx.show_names = on
        self.scene.refresh_all()

    def _update_title(self) -> None:
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

