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
        if not self._confirm_discard():
            return
        fresh = None
        try:
            fresh = self.resolver.reloaded(self._resource_dirs)
            doc = None
            if self.doc is not None:
                data = self._source_bytes(self.doc, fresh)
                dicts, md5 = dlg_codec.parse_bytes(
                    data, text_encoding=fresh.text_encoding)
                doc = LayoutDocument.from_dicts(dicts, md5)
                doc.source_bytes = data
                doc.source_path = self.doc.source_path
                doc.source_pack = self.doc.source_pack
            # 样式也从新来源读取，不能保留上次 ui.lst 的缓存。
            book = fresh.fetch_styles() or StyleBook()
            for root in reversed(self._layout_dirs):
                local_lst = Path(root) / "ui.lst"
                if local_lst.is_file():
                    book = StyleBook.parse_bytes(local_lst.read_bytes())
                    break
            layouts = [(str(path), fresh.scan_layouts(path))
                       for path in fresh.pack_paths]
        except Exception as exc:
            if fresh is not None:
                fresh.close()
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
        self._set_document(doc)
        if doc is not None:
            key = (("file", doc.source_path) if doc.source_path else
                   ("pack", *doc.source_pack))
            self.resource_panel.reveal_selection(key)
        old.close()
        self.scene.refresh_all()
        self._update_status("已从磁盘重新加载布局、目录列表、资源包、图片与样式。")

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
