"""主窗口的面板、菜单、工具栏与信号组装。

由 MainWindow 组合；依赖宿主窗口状态，不接管 QObject 初始化。
保留原有方法名与实现，回调入口保持不变。
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QLabel,
    QMenu,
    QSplitter,
    QTabWidget,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..core import fidelity
from ..core.model import Widget
from . import icons, status_text
from .canvas import FidelityView
from .file_menu import (
    add_action,
    build_file_menu,
    show_about,
    split_button,
)
from .toolbar_controls import build_encoding_button, build_frame_button


class WindowSetupMixin:
    """主窗口界面层的职责分组，不独立创建窗口。"""

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
        """文件菜单的三段（打开 / 保存 / 导出副本）见 :mod:`.file_menu`。"""
        file_menu = self.menuBar().addMenu("文件")
        build_file_menu(self, file_menu)

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
        badges_action = QAction("显示绘制保真度角标", self, checkable=True)
        badges_action.setChecked(True)
        badges_action.setToolTip(
            "画布控件右下角的「近似/模拟」小角标：关掉只影响角标，"
            "不影响绘制本身与状态栏说明")
        badges_action.toggled.connect(self._toggle_badges)
        view_menu.addAction(badges_action)
        self._badges_action = badges_action
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
        self._act_cut = QAction("剪切控件", self)
        self._act_cut.setShortcut(QKeySequence.StandardKey.Cut)
        self._act_cut.triggered.connect(self._edit_cut)
        self._act_cut.setEnabled(False)
        edit_menu.addAction(self._act_cut)
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
        self._add_action(help_menu, "关于", lambda: show_about(self))
        self._build_toolbar()

    def _update_title(self) -> None:
        """标题栏与状态栏常驻文案：从哪来、Ctrl+S 会写到哪、当前什么模式。"""
        self._sync_history_actions()
        self.diagnostics_panel.mark_stale()
        loose = self._loose_mode()
        self.setWindowTitle(
            status_text.window_title(self.doc, __version__, loose=loose))
        label = getattr(self, "_source_label", None)
        if label is not None:
            label.setText(status_text.place_hint(self.doc, loose=loose))
            # 宽松模式常驻红字：状态栏一眼能看出「Ctrl+S 会写原包」。
            label.setStyleSheet("color:#c0392b; font-weight:600;"
                                if loose else "")
        if self._active is not None and self._active in self._sessions:
            self._tab_bar.setTabText(
                self._sessions.index(self._active), self._active.label())

    def _build_toolbar(self) -> None:
        """顶部图标工具栏：与菜单共用同一 QAction（状态同步）。"""
        self._act_assets = QAction("浏览资源", self)
        self._act_assets.triggered.connect(self.browse_resources)
        for action, icon, tip, short in (
                (self._act_assets, icons.icon_assets(),
                 "浏览资源（看 / 导出副本 / 放进包 / 拼名族；"
                 "不写控件属性）", "资源"),
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
        # 三个动词各一个按钮：打开（从哪来）、保存（回哪去）、导出副本。
        # 主按钮 = 最常用的那一种，小箭头里是同一件事的其它来源/去向。
        self._open_btn = split_button(
            bar, "打开", icons.icon_open_file(),
            [self._act_open_file, self._act_open_dir, None,
             self._act_open_pack, self._act_open_res_dir],
            self.open_layout_file_dialog,
            "打开（主按钮＝布局文件；点小箭头选其它来源）")
        bar.addWidget(self._open_btn)
        bar.addAction(self._act_save)
        self._save_as_btn = split_button(
            bar, "另存为", icons.icon_save_pack(),
            [self._act_save_pack, self._act_save_as_dlg],
            self.save_as_default,
            "另存为（主按钮：包内布局＝新资源包，散装＝散装 .dlg）")
        bar.addWidget(self._save_as_btn)
        self._export_btn = split_button(
            bar, "导出副本", icons.icon_export_image(),
            [self._act_export_layout, self._act_export_png,
             self._act_export_assets],
            self.export_png,
            "导出副本（另拿一份，不影响原文件；主按钮＝画布 PNG）")
        bar.addWidget(self._export_btn)
        bar.addSeparator()
        bar.addAction(self._undo_action)
        bar.addAction(self._redo_action)
        bar.addAction(self._act_reload)
        bar.addAction(self._act_assets)
        # 文本编码：与「对齐」「按钮态」同款下拉按钮，缩写「编码」
        self._encoding_btn, self._encoding_actions = build_encoding_button(
            self, self.change_text_encoding)
        bar.addWidget(self._encoding_btn)
        # 保存模式：严格（原包只读）/ 宽松（直接写原包），切宽松要二次确认
        self._build_mode_control(bar)
        bar.addSeparator()
        bar.addAction(self._act_fit)
        bar.addAction(self._act_actual)
        bar.addAction(self._names_action)
        self._badges_action.setIcon(icons.icon_badge())
        self._badges_action.setIconText("角标")
        self._badges_action.setToolTip(
            "显示/隐藏绘制保真度角标（近似=橙、模拟=红）")
        bar.addAction(self._badges_action)
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
        # 预览帧：同款下拉按钮，小箭头里是横向滑块
        self._frame_btn, self._frame_slider, self._frame_readout = (
            build_frame_button(self, self._set_animation_frame))
        bar.addWidget(self._frame_btn)
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
        # 状态栏常驻：这篇布局从哪读、Ctrl+S 会写到哪（标题栏放不下时看这里）
        self._source_label = QLabel("", self)
        self._source_label.setToolTip(
            "来源包只读；Ctrl+S 写回的是编辑器自己生成的新包，"
            "游戏原包不会被改")
        self.statusBar().addPermanentWidget(self._source_label)
        # 状态栏右端常驻缩放百分比
        self._zoom_label = QLabel("100%", self)
        self.statusBar().addPermanentWidget(self._zoom_label)
        # 选中控件的绘制保真度（原生/近似/模拟），常驻、不抢临时消息
        self._fidelity_label = QLabel("", self)
        self._fidelity_label.setToolTip(
            "当前选中控件的绘制依据：原生=有实据，近似=文档化推断，"
            "模拟=编辑器自己加的效果")
        self.statusBar().addPermanentWidget(self._fidelity_label)
        self.view.zoom_changed.connect(self._on_zoom_changed)

    def _update_fidelity_label(self, widget: Widget | None) -> None:
        """状态栏常驻一段保真度说明：这件控件的画法有没有实据。"""
        label = getattr(self, "_fidelity_label", None)
        if label is None:
            return
        if widget is None:
            label.setText("")
            return
        try:
            text = fidelity.summary(widget, FidelityView(self.ctx),
                                    self.ctx.button_state)
        except Exception:  # 标注失败不能影响选择
            text = ""
        label.setText(text[:60])

    def _toggle_names(self, on: bool) -> None:
        self.ctx.show_names = on
        self.scene.refresh_all()

    def _toggle_badges(self, on: bool) -> None:
        """工具栏/视图菜单的「角标」开关：只影响右下角保真度小角标。"""
        self.ctx.show_badges = on
        self.scene.refresh_all()
        self._update_status(
            "已显示绘制保真度角标（近似=橙、模拟=红）。" if on
            else "已隐藏绘制保真度角标（状态栏说明仍可用）。")

    def _refresh_animation_frame_control(self) -> None:
        """按当前文档的 .spr 资源更新帧滑块范围，不修改布局。"""
        control = getattr(self, "_frame_slider", None)
        if control is None:
            return
        maximum = 0
        if self.doc is not None:
            names = {
                str(widget.props.get(key, ""))
                for widget in self.doc.all_widgets()
                for key in ("sFileName", "sBgFileName", "sBarFileName")
                if str(widget.props.get(key, ""))
            }
            for name in sorted(names):
                if name.lower().endswith(".spr"):
                    asset = self.resolver.fetch_animation(name)
                    if asset is not None:
                        maximum = max(maximum, len(asset.frames) - 1)
        previous = control.value()
        top = max(0, maximum)
        control.blockSignals(True)
        control.setRange(0, top)
        control.setValue(min(control.value(), top))
        control.blockSignals(False)
        frame = control.value()
        if frame != previous:
            # 夹值后画布也要真的换帧，否则读数变了、画面还是旧帧。
            self._set_animation_frame(frame)
        else:
            self._refresh_frame_readout(frame, top)

    def _refresh_frame_readout(self, frame: int, maximum: int) -> None:
        """滑块上方的「预览帧 3 / 7」与按钮悬停提示同步。"""
        readout = getattr(self, "_frame_readout", None)
        if readout is not None:
            readout.setText(f"预览帧 {frame} / {maximum}")
        button = getattr(self, "_frame_btn", None)
        if button is not None:
            button.setToolTip(
                f"动画预览帧（缩写：帧）：当前 {frame} / {maximum}。\n"
                "点小箭头拖横向滑块选帧；只影响画布预览，"
                "不修改布局或资源。")

    def _set_animation_frame(self, frame: int) -> None:
        slider = getattr(self, "_frame_slider", None)
        self._refresh_frame_readout(
            frame, slider.maximum() if slider is not None else frame)
        self.ctx.animation_frame = frame
        self.ctx._pixmaps.clear()
        self.scene.refresh_all()
        asset_note = ""
        if self.doc is not None:
            for widget in self.doc.all_widgets():
                for key in ("sFileName", "sBgFileName", "sBarFileName"):
                    name = str(widget.props.get(key, "") or "")
                    if not name.lower().endswith(".spr"):
                        continue
                    asset = self.resolver.fetch_animation(name)
                    if asset is not None:
                        item = asset.frame(frame)
                        asset_note = (
                            f"；{name} 当前帧号 {item.frame_id if item else '—'}，"
                            f"时长 {item.duration if item else '—'}"
                        )
                        break
                if asset_note:
                    break
        self._update_status(f"动画预览帧：{frame}{asset_note}")

    @staticmethod
    def _add_action(menu, text, slot, shortcut=None) -> QAction:
        return add_action(menu, text, slot, shortcut)

    def _connect_signals(self) -> None:
        self.resource_panel.export_layout_requested.connect(self.export_layout)
        self.resource_panel.replace_layout_requested.connect(
            self.replace_layout_dialog)
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
        self.tree_panel.indent_requested.connect(self.indent_selected)
        self.tree_panel.outdent_requested.connect(self.outdent_selected)
        self.tree_panel.set_parent_requested.connect(self.reparent_to)
        self.tree_panel.delete_requested.connect(self.delete_selected)
        self.tree_panel.reorder_requested.connect(self._reorder_widget)
        self.palette_panel.add_requested.connect(self.add_widget)
        self.props_panel.changed.connect(self._on_property_changed)
        self.scene.selectionChanged.connect(self._on_scene_selection)

    # ------------------------------------------------------------------
    # 多标签编辑会话（画布共享，切换换文档；ui/tabs.py 存状态）
    # ------------------------------------------------------------------
    def _session_index(self, key: tuple | None) -> int:
        if key is None:
            return -1
        for i, session in enumerate(self._sessions):
            if session.key == key:
                return i
        return -1

    def _save_session_state(self, session) -> None:
        session.snapshot(self._selected, self._selection_anchor)

    def _add_session(self, doc, key: tuple | None) -> None:
        from .tabs import EditorSession

        session = EditorSession(doc, key, self.view)
        self._sessions.append(session)
        self._tab_bar.blockSignals(True)
        self._tab_bar.addTab(session.label())
        self._tab_bar.blockSignals(False)
        self._refresh_tab_marks()

    def _remove_session(self, index: int) -> None:
        """无确认移除一个标签；移除激活页时切邻页或回到空态。"""
        was_active = self._sessions[index] is self._active
        self._sessions.pop(index)
        self._tab_bar.blockSignals(True)
        self._tab_bar.removeTab(index)
        self._tab_bar.blockSignals(False)
        self._refresh_tab_marks()
        if not was_active:
            return
        self._active = None
        if self._sessions:
            self._activate_session(min(index, len(self._sessions) - 1))
        else:
            self._set_document(None)

    def _activate_session(self, index: int) -> None:
        """切到某标签：共享画布换文档，还回该标签的选择与缩放/平移。"""
        if not 0 <= index < len(self._sessions):
            return
        if self._tab_bar.currentIndex() != index:
            self._tab_bar.blockSignals(True)
            self._tab_bar.setCurrentIndex(index)
            self._tab_bar.blockSignals(False)
        old = self._active
        session = self._sessions[index]
        if old is not None and old is not session and old in self._sessions:
            self._save_session_state(old)
        self._active = session
        self._doc = session.doc
        self._selected = None
        self._selection_anchor = session.selection_anchor
        self._loading = True
        if session.doc is not None:
            session.doc.text_encoding = self.resolver.text_encoding
        self.resource_panel.clear_pending()
        if session.doc is not None and session.doc.pending_pack_import:
            self.resource_panel.show_pending(*session.doc.source_pack)
        self.scene.set_document(session.doc)
        self.tree_panel.build(session.doc)
        self.props_panel.set_widget(None)
        self._loading = False
        self._apply_script_link(session.doc)
        self._select_widget(session.selected)
        if session.transform is not None:
            self.view.setTransform(session.transform)
        self._update_title()
        self._update_status(
            f"已切换到标签：{session.label()}"
            f"（共 {len(self._sessions)} 个标签）")

    def _open_in_tab(self, doc, key: tuple | None) -> None:
        """打开布局进新标签；同来源已开则切回旧标签（不丢未保存编辑）。"""
        idx = self._session_index(key)
        if idx >= 0:
            self._activate_session(idx)
            return
        self._add_session(doc, key)
        self._activate_session(len(self._sessions) - 1)
        doc.reset_history()
        self._sync_history_actions()
        self.view.fit_content()

    def _close_tab(self, index: int) -> None:
        """标签关闭按钮：脏/待入包先确认丢弃，再移除该标签。"""
        if not 0 <= index < len(self._sessions):
            return
        if not self._confirm_discard(self._sessions[index].doc):
            return
        self._remove_session(index)

    def _on_tab_changed(self, index: int) -> None:
        if 0 <= index < len(self._sessions):
            self._activate_session(index)

    def _dirty_docs(self) -> list:
        """全部未保存（或待入新包）的文档：关窗/刷新前逐个确认。"""
        seen = [s.doc for s in self._sessions]
        docs = [d for d in seen if d is not None and
                (d.dirty or d.pending_pack_import)]
        if self._doc is not None and self._doc not in seen and (
                self._doc.dirty or self._doc.pending_pack_import):
            docs.append(self._doc)
        return docs
