"""主窗口：文件/资源工作流与五大区域的组装。

布局：左侧（布局文件树 + 控件树）、中央画布、右侧（属性面板 +
控件调色板）。打开来源两种：散装 ``.dlg`` 文件/目录，以及从
``interface.fls`` 等资源包按路径直开（自动解密）；保存可写散装
``.dlg``，也可生成写回布局的新资源包（原包不动，见 M1）。
"""

from __future__ import annotations

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabBar,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..core import snap
from ..core.assets import AssetResolver
from ..core.diagnostics import (
    Diagnostic,
    diagnose,
    reference_impacts,
    widget_at_path,
)
from ..core.model import LayoutDocument, Widget
from ..core.painters import PaintContext
from ..core.script_index import ScriptIndex, get_default_index
from ..core.styles import StyleBook
from .busy import BusyHostMixin
from .canvas import CanvasView, LayoutScene
from .commands import EditingCommandsMixin
from .diagnostics_panel import DiagnosticsPanel
from .panels import PalettePanel, ResourceTreePanel, WidgetTreePanel
from .property_panel import PropertyPanel
from .save_workflows import SaveWorkflowsMixin
from .script_panel import ScriptPanel
from .source_actions import SourceActionsMixin
from .tabs import EditorSession
from .window_setup import WindowSetupMixin
from .workflows import FileWorkflowsMixin


class MainWindow(
    BusyHostMixin, EditingCommandsMixin, FileWorkflowsMixin,
    SaveWorkflowsMixin, SourceActionsMixin, WindowSetupMixin, QMainWindow
):
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
        self._resource_dirs: list[str] = []
        self._layout_dirs: list[str] = []
        self.styles = StyleBook()
        self.ctx = PaintContext(assets=self.resolver, styles=self.styles)
        self.script_index: ScriptIndex = get_default_index()
        self._doc: LayoutDocument | None = None
        self._sessions: list[EditorSession] = []
        self._active: EditorSession | None = None
        self._selected: Widget | None = None
        self._selection_anchor: list[int] | None = None
        self._syncing_selection = False
        self._loading = False

        self.scene = LayoutScene(self.ctx, self._on_geometry_changed,
                                 self._on_geometry_committed)
        self.view = CanvasView(self.scene)
        self.view.context_menu_handler = self._show_canvas_context_menu
        # 多标签：标签栏 + 共享画布；切标签换文档，各标签自存选择/缩放
        self._tab_bar = QTabBar()
        self._tab_bar.setDocumentMode(True)
        self._tab_bar.setTabsClosable(True)
        self._tab_bar.setExpanding(False)
        self._tab_bar.setUsesScrollButtons(True)
        self._tab_bar.currentChanged.connect(self._on_tab_changed)
        self._tab_bar.tabCloseRequested.connect(self._close_tab)
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(self._tab_bar)
        central_layout.addWidget(self.view, 1)
        self.setCentralWidget(central)

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
        # 状态栏要在建工具栏之前：工具栏把缩放/保真度常驻标签挂到
        # statusBar() 上，晚一步 setStatusBar 换新栏会把旧栏连同标签一起销毁。
        self.setStatusBar(QStatusBar())
        self._build_docks()
        self._build_menus()
        self._connect_signals()
        # 删除键由「删除控件」QAction 统一接管（_edit_delete 带文本焦点分流）

        self._update_title()
        self._update_status("就绪：打开一个 .dlg、布局目录，或从资源包打开。")
        self.resize(1360, 860)

    # ------------------------------------------------------------------
    # 界面组装
    # ------------------------------------------------------------------
    def _get_doc(self) -> LayoutDocument | None:
        """当前标签的文档（各标签共用画布，此属性指向激活页）。"""
        return self._doc

    def _set_doc(self, value: LayoutDocument | None) -> None:
        """外部直接赋值入口（测试/工具）：None=撤销当前标签。"""
        if value is None:
            if self._active is not None and self._active in self._sessions:
                self._remove_session(self._sessions.index(self._active))
            else:
                self._doc = None
            return
        self._doc = value
        if self._active is not None:
            self._active.doc = value
        else:
            self._set_document(value)

    doc = property(_get_doc, _set_doc)

    def _confirm_discard(self, doc: LayoutDocument | None = None) -> bool:
        target = self.doc if doc is None else doc
        if target is None or not (target.dirty or target.pending_pack_import):
            return True
        answer = QMessageBox.question(
            self, "未保存的修改",
            f"布局「{target.display_name}」有未保存的修改，确定丢弃吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return answer == QMessageBox.StandardButton.Yes

    def _set_document(self, doc: LayoutDocument | None) -> None:
        if self._active is None and doc is not None:
            self._add_session(doc, EditorSession.key_of(doc))
            self._tab_bar.blockSignals(True)
            self._tab_bar.setCurrentIndex(len(self._sessions) - 1)
            self._tab_bar.blockSignals(False)
            self._active = self._sessions[-1]
        self._loading = True
        if doc is not None:
            doc.text_encoding = self.resolver.text_encoding
        self.resource_panel.clear_pending()
        self._doc = doc
        if self._active is not None:
            self._active.doc = doc
            # 就地换文档可能改变来源身份（如导入待入包）：同步会话键
            self._active.key = EditorSession.key_of(doc)
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
        if hasattr(self, "_refresh_animation_frame_control"):
            self._refresh_animation_frame_control()
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
        issues = diagnose(
            self.doc, link=self._script_link(),
            resource_exists=(self.resolver.resource_exists
                             if self.resolver.has_sources else None),
            staged_paths=self.resolver.staged_images())
        issues.extend(
            Diagnostic("错误" if issue.code in {
                       "RESOURCE_PACK_CORRUPT", "RESOURCE_READ_ERROR",
                       "RESOURCE_INVALID_PATH"} else "警告",
                       issue.code, None, "资源路径",
                       f"{issue.path}：{issue.message}")
            for issue in self.resolver.issues)
        return issues

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
            # 锁定的控件在画布上完全无视：树/诊断点它只更新面板，
            # 不让它进画布选择（画布上也点不到它）。
            if widget is not None and not widget.locked:
                item = self.scene.item_for(widget)
                if item is not None:
                    item.setSelected(True)
        finally:
            self._syncing_selection = False
        self._sync_lock_action()
        self._update_fidelity_label(widget)

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
        widgets = [it.widget for it in selected if hasattr(it, "widget")]
        if len(widgets) > 1 and self.doc is not None:
            # 多选（Ctrl+点/拖框）时按文档顺序取第一个当主选中，属性面板
            # 只编辑它；状态栏报数量，删/复制/锁定仍作用于整组。
            order = {id(w): i for i, w in enumerate(self.doc.all_widgets())}
            widgets.sort(key=lambda w: order.get(id(w), 0))
            self._update_status(
                f"已选中 {len(widgets)} 个控件（属性面板编辑最上层"
                f"「{widgets[0].name or '(未命名)'}」）")
        widget = widgets[0] if widgets else None
        # 多选时不能回灌单选同步，否则其余选中会被冲掉
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

    def _clamp_in_parent(self, widget: Widget,
                         x: float, y: float) -> tuple[float, float, int]:
        """对齐/分布算出的坐标夹回父矩形，返回 (x, y, 是否被夹)。"""
        parent = widget.parent
        box = None if parent is None else (parent.width, parent.height)
        cx, cy, clamped = snap.clamp_in_parent(
            box, x, y, widget.width, widget.height)
        return cx, cy, int(clamped)

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
        clamped = 0
        for w in targets:
            x, y = snap.align_position(
                ref_rect, (w.x, w.y, w.width, w.height), mode)
            x, y, was_clamped = self._clamp_in_parent(w, x, y)
            clamped += was_clamped
            w.set_geometry(x=int(round(x)), y=int(round(y)))
            self.scene.refresh_widget(w)
        self.doc.checkpoint()
        self.doc.dirty = True
        self._update_title()
        note = (f"（其中 {clamped} 个被父控件边界挡住，差几个像素没完全对齐）"
                if clamped else "")
        self._update_status(
            f"已按基准「{ref.name}」对齐 {len(targets)} 个控件{note}。")

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
        clamped = 0
        for w, (x, y) in zip(
                group, snap.distribute_positions(rects, axis), strict=True):
            x, y, was_clamped = self._clamp_in_parent(w, x, y)
            clamped += was_clamped
            w.set_geometry(x=int(round(x)), y=int(round(y)))
            self.scene.refresh_widget(w)
        self.doc.checkpoint()
        self.doc.dirty = True
        self._update_title()
        direction = "横" if axis == "x" else "纵"
        note = (f"（其中 {clamped} 个被父控件边界挡住）" if clamped else "")
        self._update_status(
            f"已沿{direction}向等距分布 {len(group)} 个控件{note}。")

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
        if self._active is not None and self._active in self._sessions:
            self._tab_bar.setTabText(
                self._sessions.index(self._active), self._active.label())

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
        for doc in self._dirty_docs():
            if not self._confirm_discard(doc):
                event.ignore()
                return
        self.resolver.close()
        super().closeEvent(event)

