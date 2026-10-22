"""布局文件与资源包的打开、导入工作流（保存见 :mod:`save_workflows`）。

由 MainWindow 组合；依赖宿主窗口状态，不接管 QObject 初始化。
保留原有方法名与实现，回调入口保持不变。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QInputDialog,
    QMessageBox,
)

from ..core import dlg_codec
from ..core.catalog import known_layout_paths
from ..core.layout_import import prepare_layout_import, validate_layout_path
from ..core.model import LayoutDocument
from ..core.pack import FlsPack
from ..core.styles import StyleBook
from .layout_import_dialog import LayoutImportDialog


class FileWorkflowsMixin:
    """主窗口界面层的职责分组，不独立创建窗口。"""

    RECENT_LIMIT = 8

    # -- 最近打开（跨会话，QSettings） --------------------------------
    def _remember_recent(self, kind: str, path: str) -> None:
        """记一条「最近打开」。``kind``：dlg / dlgdir / pack / resdir。"""
        if not path:
            return
        entry = f"{kind}::{path}"
        items = self._settings.value("recent_open", [])
        if isinstance(items, str):
            items = [items]
        items = [str(item) for item in (items or []) if str(item) != entry]
        items.insert(0, entry)
        self._settings.setValue("recent_open", items[: self.RECENT_LIMIT])

    def _recent_entries(self) -> list[tuple[str, str]]:
        items = self._settings.value("recent_open", [])
        if isinstance(items, str):
            items = [items]
        out: list[tuple[str, str]] = []
        for item in items or []:
            kind, _, path = str(item).partition("::")
            if kind in ("dlg", "dlgdir", "pack", "resdir") and path:
                out.append((kind, path))
        return out

    def open_recent(self, kind: str, path: str) -> None:
        """从「最近打开」再开一次（文件没了就在状态栏说明，不弹栈）。"""
        if kind == "dlg":
            if not Path(path).is_file():
                self._update_status(f"最近打开的布局不在了：{path}")
                self._forget_recent("dlg", path)
                return
            self.open_layout_file(path)
        elif kind == "dlgdir":
            if not Path(path).is_dir():
                self._update_status(f"最近打开的布局目录不在了：{path}")
                self._forget_recent("dlgdir", path)
                return
            self.open_layout_dir(path)
        elif kind == "pack":
            if not Path(path).is_file():
                self._update_status(f"最近打开的资源包不在了：{path}")
                self._forget_recent("pack", path)
                return
            count = self.open_pack_file(path)
            if count > 0:
                self._update_status(
                    f"已挂载 {Path(path).name}：识别到 {count} 个布局，"
                    "在左侧资源树双击即可打开。")
        elif kind == "resdir":
            if not Path(path).is_dir():
                self._update_status(f"最近的资源目录不在了：{path}")
                self._forget_recent("resdir", path)
                return
            self.open_resource_dir(path)

    def _forget_recent(self, kind: str, path: str) -> None:
        entry = f"{kind}::{path}"
        items = self._settings.value("recent_open", [])
        if isinstance(items, str):
            items = [items]
        items = [str(item) for item in (items or []) if str(item) != entry]
        self._settings.setValue("recent_open", items)

    def clear_recent(self) -> None:
        self._settings.setValue("recent_open", [])
        self._update_status("已清空「最近打开」记录（只影响这份列表，不动文件）。")

    def open_layout_file(self, path: str) -> None:
        try:
            data = Path(path).read_bytes()
            dicts, md5 = dlg_codec.parse_bytes(
                data, text_encoding=self.resolver.text_encoding)
        except Exception as exc:
            QMessageBox.warning(self, "打开失败", str(exc))
            return
        doc = LayoutDocument.from_dicts(dicts, md5)
        doc.source_path = str(path)
        doc.source_bytes = data
        self.resolver.add_loose_dir(Path(path).parent)
        self._try_load_styles()
        self._open_in_tab(doc, ("file", str(path)))
        self.resource_panel.reveal_selection(("file", str(path)))
        self._remember_recent("dlg", str(path))

    def open_layout_file_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "打开布局文件", self._settings.value("last_dir", ""),
            "布局文件 (*.dlg);;所有文件 (*)")
        if path:
            self._settings.setValue("last_dir", str(Path(path).parent))
            self.open_layout_file(path)

    def open_layout_dir(self, path: str) -> None:
        if path not in self._layout_dirs:
            self._layout_dirs.append(path)
        self._remember_recent("dlgdir", str(path))
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
            layouts = self.run_busy(
                f"挂载资源包 {Path(pack_path).name}",
                lambda h: self._mount_and_scan(pack_path, h))
        except Exception as exc:
            QMessageBox.warning(self, "挂载资源包失败", str(exc))
            return -1
        self._add_pack_to_tree(pack_path, layouts)
        self._remember_recent("pack", str(pack_path))
        self.resource_panel.expand_pack(pack_path)
        self._try_load_styles()
        self.scene.refresh_all()
        return len(layouts)

    def _mount_and_scan(self, pack_path: str, handle) -> list[str]:
        handle.report(0, 2, "读取资源包索引…")
        if self.resolver.pack_for(pack_path) is None:
            self.resolver.mount_pack(pack_path)
        handle.report(1, 2, "扫描已知布局…")
        return self.resolver.scan_layouts(pack_path)

    def _add_pack_to_tree(self, pack_path: str,
                          layouts: list[str]) -> None:
        """只将有已识别布局的包入树；图片包仍挂载供资源读取。"""
        if not layouts:
            return
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
                "左侧已隐藏这个 0 布局包。）")
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
            doc.source_bytes = self.resolver.fetch_pack_dlg_bytes(pack_path, path)
        except Exception as exc:
            QMessageBox.warning(self, "按路径打开失败", str(exc))
            return
        doc.source_pack = (pack_path, path)
        self._remember_layout(path)
        self.resource_panel.add_known_layout(pack_path, path)
        self._open_in_tab(doc, ("pack", pack_path, path))
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
                    pack, dialog.path, Path(filename).read_bytes(),
                    text_encoding=self.resolver.text_encoding)
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

    def _open_pack_layout(self, pack_path: str, res_path: str) -> None:
        """从包中打开一个布局（树双击与对话框共用）。

        同来源布局开过就切回它的标签（保留未保存编辑），否则开新标签；
        包顺带入树。
        """
        if (self.doc is not None and self.doc.pending_pack_import
                and self.doc.source_pack == (pack_path, res_path)):
            self.resource_panel.reveal_selection(("pending", pack_path, res_path))
            return
        idx = self._session_index(("pack", pack_path, res_path))
        if idx >= 0:
            self._activate_session(idx)
            pending = (self.doc is not None and self.doc.pending_pack_import)
            self.resource_panel.reveal_selection(
                ("pending" if pending else "pack", pack_path, res_path))
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
        doc.source_bytes = self.resolver.fetch_pack_dlg_bytes(pack_path, res_path)
        self._try_load_styles()
        self._open_in_tab(doc, ("pack", pack_path, res_path))
        self.resource_panel.reveal_selection(("pack", pack_path, res_path))

    def open_resource_dir(self, path: str) -> None:
        """从资源目录打开：挂载目录内全部包并逐个入树（忙碌遮罩后跑）。"""
        if path not in self._resource_dirs:
            self._resource_dirs.append(path)
        self._remember_recent("resdir", str(path))
        before = {str(p) for p in self.resolver.pack_paths}
        try:
            scanned = self.run_busy(
                f"挂载资源目录 {Path(path).name or path}",
                lambda h: self._mount_dir_scanned(path, before, h))
        except Exception as exc:
            QMessageBox.warning(self, "挂载资源包失败", str(exc))
            return
        added = skipped = 0
        for pack_file, layouts in scanned:
            if not layouts:
                skipped += 1  # 保留资源挂载，但不在布局树显示
                continue
            self._add_pack_to_tree(pack_file, layouts)
            added += 1
        self._try_load_styles()
        self.scene.refresh_all()
        self._update_status(
            f"资源目录：{path}；新入树 {added} 个包"
            f"（另隐藏 {skipped} 个无已识别布局的包）。{self.resolver.summary}；"
            "双击包中布局即可切换打开。")

    def _mount_dir_scanned(self, path: str, before: set[str],
                           handle) -> list[tuple[str, list[str]]]:
        """后台任务：挂载目录内全部包并扫描（经遮罩回调进度）。"""
        self.resolver.mount_dir(path, progress=handle.report)
        handle.report(0, 1, "扫描已知布局…")
        return [(str(p), self.resolver.scan_layouts(str(p)))
                for p in self.resolver.pack_paths if str(p) not in before]

    def open_resource_dir_dialog(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "从资源目录打开布局（其中 .fls 全部挂载）",
            self._settings.value("pack_dir", ""))
        if path:
            self._settings.setValue("pack_dir", path)
            self.open_resource_dir(path)

    def new_layout(self) -> None:
        doc = LayoutDocument()
        frame = doc.new_widget("CMainFrame")
        frame.props["sTitle"] = "新對話框"
        doc.dirty = True
        self._open_in_tab(doc, None)
        self._select_widget(frame)

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
