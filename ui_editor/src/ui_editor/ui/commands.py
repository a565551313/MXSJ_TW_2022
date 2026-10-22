"""主窗口的控件编辑命令（Qt 界面层 mixin）。

由 MainWindow 组装，复用窗口的文档、选择、画布与动作对象；不独立创建
窗口、不保存文件。方法保持原有名称，菜单/信号和调用方无需更换入口。
添加/提升、复制粘贴、删除引用护栏、锁定与右键菜单集中在这里。
"""

from __future__ import annotations

from PySide6.QtCore import QMimeData
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QTextEdit,
)

from ..core import painters
from ..core.diagnostics import reference_impacts
from ..core.model import Widget


class EditingCommandsMixin:
    """依赖宿主窗口状态的编辑命令；不接管 QObject 初始化。"""

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

    def reparent_to(self, parent: Widget | None) -> None:
        """把选中的控件挂到 parent 下（None=顶层）；整组算一步撤销。"""
        if self.doc is None:
            return
        targets = self._selected_widgets()
        if not targets:
            self._update_status("请先选中要改父级的控件。")
            return
        # 先整组预检，避免前几个已经挪了才被锁定/防环拦下
        for widget in targets:
            reason = self.doc.reparent_reason(widget, parent)
            if reason is not None:
                self._update_status(reason)
                return
        size = (painters.effective_size(parent, self.ctx)
                if parent is not None else None)
        moved: list[Widget] = []
        for widget in targets:
            if widget.parent is parent:
                continue
            self.doc.set_parent(widget, parent, parent_size=size)
            moved.append(widget)
        if not moved:
            self._update_status("选中的控件已经在这个父控件下。")
            return
        self.doc.checkpoint()
        self._refresh_structure()
        self._select_widget(moved[0])
        self._update_title()
        where = f"「{parent.name or '(未命名)'}」下" if parent else "顶层"
        self._update_status(
            f"已把 {len(moved)} 个控件挂到{where}（坐标已换算并夹进父矩形）。")

    def indent_selected(self) -> None:
        """→ 降级：挂成上一个同级控件的子控件。"""
        widget = self._selected or self.tree_panel.current_widget()
        if self.doc is None or widget is None:
            self._update_status("请先选中要降级的控件。")
            return
        reason = self.doc.indent_widget(
            widget, sizer=lambda w: painters.effective_size(w, self.ctx))
        if reason is not None:
            self._update_status(reason)
            return
        self.doc.checkpoint()
        self._refresh_structure()
        self._select_widget(widget)
        self._update_title()
        self._update_status("已降为上一个同级控件的子控件。")

    def outdent_selected(self) -> None:
        """← 升级：脱离父控件，成为父控件的下一个同级。"""
        widget = self._selected or self.tree_panel.current_widget()
        if self.doc is None or widget is None:
            self._update_status("请先选中要升级的控件。")
            return
        reason = self.doc.outdent_widget(
            widget, sizer=lambda w: painters.effective_size(w, self.ctx))
        if reason is not None:
            self._update_status(reason)
            return
        self.doc.checkpoint()
        self._refresh_structure()
        self._select_widget(widget)
        self._update_title()
        self._update_status("已升一级（与父控件同级）。")

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
        名字：与文档里已有控件重名时自动加后缀（``BTN`` → ``BTN_1``、
        再粘 → ``BTN_2``；``BTN_1`` 复制后粘贴 → ``BTN_1_1``），子树里的
        重名子控件同样处理；不重名则保持原名。这样副本不会顶掉脚本对
        原控件的 sName 认领，也不会在诊断里变成重复名。
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
        used = {w.name for w in self.doc.all_widgets()}
        renamed = self.doc.rename_copies(clones, used)
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
        note = (f"（{renamed} 个重名的已自动改名）" if renamed else "")
        self._update_status(
            f"已粘贴 {len(clones)} 个控件{note}："
            f"首个为「{clones[0].name or '(未命名)'}」")

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
        previous = self._selected
        for widget in widgets:
            widget.locked = on
            item = self.scene.item_for(widget)
            if item is not None:
                item.apply_lock()
            self.tree_panel.set_lock_icon(widget)
        if previous is not None and previous.locked:
            # 锁定后画布不再选它（取消选中会清空当前选择），
            # 这里把面板/树的选择补回来，方便继续查看或解锁
            self._select_widget(previous, sync_scene=False)
        self._sync_lock_action()
        names = "、".join(w.name or "(无名)" for w in widgets[:3])
        if len(widgets) > 3:
            names += " 等"
        self._update_status(
            f"已锁定 {len(widgets)} 个控件（{names}）：画布上点不到、"
            "选不中、框选不到、拖不动；在控件树点锁图标解锁。"
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

    # -- 导出素材（右键） --------------------------------------------
    def _add_export_asset_menu(self, menu: QMenu, widgets: list) -> None:
        """右键「导出素材」子菜单：原格式 / 转成图片。"""
        from ..core.asset_export import asset_paths_of

        paths = [name for widget in widgets for _k, name in
                 asset_paths_of(widget)]
        submenu = menu.addMenu("导出素材")
        submenu.setToolTip("把这个控件引用的图片/精灵/音效导出成文件")
        if not paths:
            empty = submenu.addAction("（这个控件没有图片或音效素材）")
            empty.setEnabled(False)
            return
        raw = submenu.addAction("按原格式导出…")
        raw.setToolTip(
            "包里是什么格式就导出什么格式：PNG/JPG/GIF/BMP/TGA 原样写字节，"
            "游戏精灵保留原名（.igs/.png），.spr 连帧图一起导出")
        raw.triggered.connect(
            lambda _checked=False: self.export_widget_assets(widgets))
        converted = submenu.addAction("转成图片导出（精灵逐帧 PNG）…")
        converted.setToolTip("方便直接查看/编辑：精灵会解成逐帧 PNG")
        converted.triggered.connect(
            lambda _checked=False: self.export_widget_assets(
                widgets, convert=True))

    def _asset_export_dir(self) -> str | None:
        from PySide6.QtWidgets import QFileDialog

        return QFileDialog.getExistingDirectory(
            self, "选择素材导出到的文件夹")

    def export_widget_assets(self, widgets: list,
                             convert: bool = False) -> None:
        """把控件引用的素材导出到用户选的文件夹。

        convert=False：按原格式写原始字节（默认）；
        convert=True：精灵解成逐帧 PNG，方便查看/编辑。

        批量语义（多选导出时用户可见）：同一个资源路径只导一次；不同资源
        恰好同名的，后写的加序号而不是覆盖先写的；某个目标被
        ``guard_output`` 拒绝只跳过它，其余照常导出，最后在状态栏一并汇报。
        """
        from pathlib import Path

        from ..core.asset_export import (
            asset_paths_of,
            dir_piece_name,
            export_paths,
            export_raw_assets,
            family_prefixes,
            source_key,
            unexported_label,
        )
        from .image_export import export_image_files

        assets = self.resolver
        if assets is None:
            self._update_status("没有挂载资源包，取不到素材字节。")
            return
        directory = self._asset_export_dir()
        if not directory:
            return
        written: list[Path] = []
        missing: list[str] = []
        rejected: list[tuple[str, str]] = []
        seen: set[str] = set()          # 本批已导出的资源路径
        used_names: set[str] = set()    # 本批已占用的输出文件名（小写）
        # 一批有多个拼名族时前缀族名，免得后一族变成看不出出处的 0l-2.png。
        families = family_prefixes(
            name for widget in widgets for _key, name in asset_paths_of(widget))
        if convert:
            for widget in widgets:
                for _key, name in asset_paths_of(widget):
                    if source_key(name) in seen:
                        continue
                    prefix = families.get(source_key(name), "")
                    paths = export_paths(assets, name)
                    if not paths:
                        # 目录型基路径拼不出整族：说明原因，别把校验器的
                        # 「不能以目录分隔符结尾」当成用户的错。
                        seen.add(source_key(name))
                        missing.append(unexported_label(assets, name))
                        continue
                    for path in paths:
                        if source_key(path) in seen:
                            continue
                        seen.add(source_key(path))
                        # 目录型子图按族内相对路径命名（top-left.png），
                        # 否则九片的 top/bottom 会挤成 left.png、left-2.png。
                        dest_name = (None if path == name
                                     else dir_piece_name(path, name, prefix))
                        try:
                            data = assets.fetch_bytes(path)
                            if data is None:
                                # 目录型子图缺块要说清是「读取失败」，
                                # 普通资源维持原来的裸路径。
                                missing.append(path if path == name else
                                               f"{path}（子图读取失败）")
                                continue
                            files = export_image_files(
                                path, data, assets.fetch_image(path), directory,
                                dest_name,
                                protected_paths=assets.pack_paths,
                                used_names=used_names)
                        except (OSError, ValueError) as exc:
                            # 单个资源被拒/写不出不能连累整批：记账后继续。
                            rejected.append((path, str(exc)))
                            continue
                        if files:
                            written.extend(files)
                        else:
                            missing.append(path)
        else:
            for widget in widgets:
                files, lost = export_raw_assets(
                    assets, widget, directory,
                    protected_paths=assets.pack_paths,
                    seen=seen, rejected=rejected,
                    family_prefixes=families)
                written.extend(files)
                missing.extend(lost)
        if written:
            names = "、".join(path.name for path in written[:4])
            more = f" 等 {len(written)} 个文件" if len(written) > 4 else ""
            note = (f"；{len(missing)} 个资源没导出："
                    + "、".join(missing[:3]) if missing else "")
            if rejected:
                note += (f"；{len(rejected)} 个被拒绝："
                         + "、".join(name for name, _why in rejected[:2]))
            self._update_status(
                f"已导出 {names}{more} 到 {directory}{note}")
        else:
            if rejected:
                name, why = rejected[0]
                self._update_status(
                    f"导出被拒绝（{len(rejected)} 个）：{name} —— {why}")
                return
            self._update_status(
                "没有可导出的素材"
                + (f"（{'、'.join(missing[:3])}）" if missing else "。"))

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
        widgets = self._selected_widgets()
        if widget is not None and widgets:
            self._add_export_asset_menu(menu, widgets)
            from .hierarchy import build_parent_menu

            menu.addMenu(build_parent_menu(self, self.doc, widgets,
                                           self.reparent_to))
            promote = menu.addAction("设为顶级")
            promote.setEnabled(any(w.parent is not None for w in widgets))
            promote.triggered.connect(self.promote_selected_to_root)
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

