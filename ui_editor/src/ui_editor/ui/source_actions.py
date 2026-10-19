"""来源操作：文本重解码、事务式刷新与布局原字节导出。"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QFileDialog, QMessageBox

from ..core import dlg_codec
from ..core.model import LayoutDocument
from ..core.output_paths import guard_output
from ..core.styles import StyleBook


class SourceActionsMixin:
    """只在成功读取后切换文档；失败保留当前文档及其来源。"""

    @staticmethod
    def _source_bytes(doc, resolver) -> bytes:
        if doc.source_path:
            return Path(doc.source_path).read_bytes()
        if doc.source_pack:
            return resolver.fetch_pack_dlg_bytes(*doc.source_pack)
        raise ValueError("当前布局尚未保存，没有可重新读取的来源。")

    def _restore_encoding_choice(self) -> None:
        with QSignalBlocker(self._encoding_combo):
            self._encoding_combo.setCurrentIndex(
                self._encoding_combo.findData(self.resolver.text_encoding))

    def change_text_encoding(self, index: int) -> None:
        encoding = self._encoding_combo.itemData(index)
        if encoding == self.resolver.text_encoding:
            return
        if self.doc is None:
            self.resolver.text_encoding = encoding
            return
        if not self._confirm_discard():
            self._restore_encoding_choice()
            return
        try:
            # 绝不从已经解码的 Unicode 文字反向转码。
            data = self.doc.source_bytes
            if data is None:
                data = self._source_bytes(self.doc, self.resolver)
            dicts, md5 = dlg_codec.parse_bytes(data, text_encoding=encoding)
            doc = LayoutDocument.from_dicts(dicts, md5)
            doc.source_bytes = data
            doc.source_path = self.doc.source_path
            doc.source_pack = self.doc.source_pack
            if self.doc.pending_pack_import:
                doc.begin_pack_import(self.doc._saved_state)
        except Exception as exc:
            self._restore_encoding_choice()
            QMessageBox.warning(self, "切换编码失败", str(exc))
            return
        self.resolver.text_encoding = encoding
        self._set_document(doc)
        if doc.pending_pack_import:
            self.resource_panel.show_pending(*doc.source_pack)
        self._update_status(f"布局文本已按 {encoding.upper()} 重新读取；源文件未修改。")

    def refresh_sources(self) -> None:
        if not self.resolver.has_sources and not self._layout_dirs:
            QMessageBox.information(self, "刷新", "请先打开布局文件、目录或资源包。")
            return
        for doc in self._dirty_docs():
            if not self._confirm_discard(doc):
                return
        try:
            fresh, docs, book, layouts = self.run_busy(
                "从来源刷新（重开资源包并重扫）…",
                lambda h: self._reload_bundle(h))
        except Exception as exc:
            QMessageBox.warning(self, "刷新失败", f"保留当前布局与来源。\n{exc}")
            return
        old = self.resolver
        self.resolver = fresh
        self.ctx.assets = fresh
        self.props_panel.assets = fresh
        self.styles = book
        self.ctx.styles = book
        # 从磁盘重建树，既反映新增，也移除已删除的散装布局。
        self.resource_panel.reset_sources()
        for path, names in layouts:
            self._add_pack_to_tree(path, names)
        for root in self._layout_dirs:
            self.resource_panel.add_loose_dir(root)
        self.resource_panel._apply_search(self.resource_panel._search.text())
        # 逐标签换上重读内容（清选择快照）；活动标签同步界面。
        pairs = ([(s, s.doc) for s in self._sessions]
                 or [(None, self._doc)])
        active_new = None
        for (session, _was), nd in zip(pairs, docs, strict=True):
            if nd is None:
                continue
            if session is not None:
                session.doc = nd
                session.selected = None
                session.selection_anchor = None
                if session is self._active:
                    active_new = nd
            else:
                active_new = nd
        if active_new is not None:
            self._set_document(active_new)
        elif self._doc is None:
            self._set_document(None)
        if self._doc is not None and (
                self._doc.source_path or self._doc.source_pack):
            key = (("file", self._doc.source_path) if self._doc.source_path
                   else ("pack", *self._doc.source_pack))
            self.resource_panel.reveal_selection(key)
        old.close()
        self.scene.refresh_all()
        self._update_status("已从磁盘重新加载布局、目录列表、资源包、图片与样式。")

    def _reload_bundle(self, handle):
        """后台任务：重开全部来源并重读全部标签布局/样式/布局清单。

        未保存且无来源的标签跳过（内容保留）；读取失败原样重抛
        （调用方提示后整单保留现状）。出错时关掉半成品 fresh。
        """
        fresh = None
        try:
            handle.report(0, 3, "重开资源包…")
            fresh = self.resolver.reloaded(self._resource_dirs)
            pairs = ([(s, s.doc) for s in self._sessions]
                     or [(None, self._doc)])
            docs: list = []
            for i, (_session, was) in enumerate(pairs):
                if was is None or not (was.source_path or was.source_pack):
                    docs.append(None)  # 无来源（如新建页）：跳过保留
                    continue
                handle.report(1, 3, f"重读布局 {i + 1}/{len(pairs)}…")
                data = self._source_bytes(was, fresh)
                dicts, md5 = dlg_codec.parse_bytes(
                    data, text_encoding=fresh.text_encoding)
                nd = LayoutDocument.from_dicts(dicts, md5)
                nd.source_bytes = data
                nd.source_path = was.source_path
                nd.source_pack = was.source_pack
                docs.append(nd)
            # 样式也从新来源读取，不能保留上次 ui.lst 的缓存。
            handle.report(2, 3, "扫描布局与样式…")
            book = fresh.fetch_styles() or StyleBook()
            for root in reversed(self._layout_dirs):
                local_lst = Path(root) / "ui.lst"
                if local_lst.is_file():
                    book = StyleBook.parse_bytes(local_lst.read_bytes())
                    break
            layouts = [(str(path), fresh.scan_layouts(path))
                       for path in fresh.pack_paths]
        except Exception:
            if fresh is not None:
                fresh.close()
            raise
        return fresh, docs, book, layouts

    def export_layout(self, source: tuple) -> None:
        """树节点的来源快照导出，不导出当前未保存编辑、不改变编码。"""
        try:
            if source[0] == "file":
                filename = Path(source[1]).name
                data = Path(source[1]).read_bytes()
                protected = [Path(source[1])]
            elif source[0] == "pack":
                filename = source[2].replace("\\", "/").split("/")[-1]
                data = self.resolver.fetch_pack_dlg_bytes(source[1], source[2])
                protected = [Path(source[1])]
            else:
                raise ValueError("只能导出已有的布局文件；待入包布局请使用另存为。")
            # 验证为布局，但输出仍用原始解密字节，不 dump、不转码。
            dlg_codec.parse_bytes(data, text_encoding=self.resolver.text_encoding)
            path, _ = QFileDialog.getSaveFileName(
                self, "导出布局（来源原文，不含未保存编辑）", filename,
                "布局文件 (*.dlg);;所有文件 (*)")
            if not path:
                return
            target = Path(path)
            if not target.suffix:
                target = target.with_suffix(".dlg")
            if target.suffix.lower() != ".dlg":
                raise ValueError("布局请导出为 .dlg 文件。")
            protected.extend(self._pack_sources())
            if self.doc and self.doc.source_path:
                protected.append(Path(self.doc.source_path))
            # 防止覆盖任何散装源资源（含图片），也保护硬链接别名。
            for root in self.resolver._loose_dirs:
                protected.extend(p for p in root.rglob("*")
                                 if p.is_file())
            guard_output(target, protected)
            target.write_bytes(data)
        except Exception as exc:
            QMessageBox.warning(self, "导出布局失败", str(exc))
            return
        self._update_status(f"已导出来源布局：{target}（未转码，不含未保存编辑）")
