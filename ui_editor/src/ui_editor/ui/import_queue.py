"""批量导入本地布局：排队、树上展示、保存时一次写进新包。

用户报的原话是「每导入一个布局文件都得保存一次，一次只能选择一个布局
文件，没法批量导入」。这里只负责**排队**：把多个本地 ``.dlg`` 解析成
待入包的文档，挂在树上，等保存链一次写完。真正写包仍然走
:mod:`ui_editor.ui.save_workflows`（原包只读，保存生成新包）。

队列按「保存会写到哪个包」记在窗口上（``_pending_imports``），所以：
刷新来源不丢、保存成功后统一销账、打开过的标签从队列里拿出去也不丢。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QDialog, QMessageBox

from ..core.layout_import import prepare_layout_import
from ..core.pack import FlsPack
from .batch_import import BatchImportDialog


class ImportQueueMixin:
    """主窗口的「批量导入」职责分组，不独立创建窗口。"""

    # -- 导入入口 -----------------------------------------------------
    def import_pack_layout(self, pack_path: str) -> None:
        """把本地布局放进这个包：可多选文件 / 整个文件夹，保存一次全写。

        这里只把布局「排进队」并打开第一个；真正写包仍然由保存链完成。
        """
        known = self.resolver.scan_layouts(pack_path)
        dialog = BatchImportDialog(
            pack_path, known, self,
            start_dir=str(self._settings.value("last_import_dir", "")))
        if dialog.exec() != QDialog.Accepted:
            return
        entries = dialog.entries()
        if not entries:
            return
        self._settings.setValue("last_import_dir", str(entries[0][0].parent))

        docs: dict[str, object] = {}
        failed: list[tuple[str, str]] = []
        try:
            pack_handle = FlsPack(pack_path)
        except Exception as exc:
            QMessageBox.warning(self, "导入布局失败", str(exc))
            return
        with pack_handle as pack:
            for local, res_path in entries:
                try:
                    doc, _replacing = prepare_layout_import(
                        pack, res_path, Path(local).read_bytes(),
                        text_encoding=self.resolver.text_encoding)
                except Exception as exc:      # 单个坏文件不拖垮整批
                    failed.append((res_path, str(exc)))
                    continue
                doc.source_pack = (pack_path, res_path)
                docs[res_path] = doc
        if not docs:
            QMessageBox.warning(
                self, "导入布局失败",
                "选中的布局都没能导入：\n"
                + "\n".join(f"· {path}：{reason}"
                            for path, reason in failed[:10]))
            return
        if not self._confirm_discard():
            return

        # 队列跟着「保存会写到哪个包」走：当前标签若已经从源包写成了新包，
        # 用户再右点源包导入时，也排到新包那条队里，否则保存时会漏掉。
        queue_path = pack_path
        doc_now = self.doc
        if (doc_now is not None and doc_now.source_pack
                and doc_now.source_pack[0] != pack_path
                and doc_now.origin_pack == pack_path):
            queue_path = doc_now.source_pack[0]
        for doc in docs.values():
            doc.source_pack = (queue_path, doc.source_pack[1])
            doc.origin_pack = pack_path
            if queue_path != pack_path:
                # 已经在写新包了：这批导入也跟着写进同一个新包
                doc.output_pack = queue_path

        store = self._pending_imports.setdefault(queue_path, {})
        first_path = next(iter(docs))
        store.update({path: doc for path, doc in docs.items()
                      if path != first_path})
        self._set_document(docs[first_path])
        self.resource_panel.show_pending_many(
            queue_path, [first_path, *store], current=first_path)
        message = (f"已导入 {len(docs)} 个布局（待入新包），当前打开 {first_path}；"
                   "Ctrl+S 一次全部写进新包（原包不动）。")
        if failed:
            message += f" 另有 {len(failed)} 个没能导入。"
        self._update_status(message)
        if failed:
            QMessageBox.warning(
                self, "部分布局没能导入",
                "这些文件有问题，已跳过（其余照常排队）：\n"
                + "\n".join(f"· {path}：{reason}"
                            for path, reason in failed[:10])
                + ("\n……" if len(failed) > 10 else ""))

    # -- 队列与树 -----------------------------------------------------
    def _pending_layout_dicts(self, pack_path: str) -> dict[str, list[dict]]:
        """待写入这个新包的全部布局（队列 + 已打开标签），路径 → 字典。

        以标签里正在编辑的内容为准：同一路径两边都有时用标签那份，
        否则用户改了没保存就会写出旧内容。
        """
        out: dict[str, list[dict]] = {}
        for path, doc in self._pending_imports.get(pack_path, {}).items():
            out[path] = doc.to_dicts()
        for doc in self._docs_with_pending_pack(pack_path):
            if doc.source_pack is not None:
                out[doc.source_pack[1]] = doc.to_dicts()
        return out

    def _docs_with_pending_pack(self, pack_path: str) -> list:
        """所有「待入这个新包」的文档：各标签里的 + 当前文档。"""
        seen = []
        for session in self._sessions:
            doc = session.doc
            if doc is not None and doc not in seen:
                seen.append(doc)
        if self._doc is not None and self._doc not in seen:
            seen.append(self._doc)
        return [doc for doc in seen
                if doc.pending_pack_import and doc.source_pack is not None
                and doc.source_pack[0] == pack_path]

    def _show_pending_for(self, pack_path: str,
                          current: str | None = None) -> None:
        """把某个包的待入队列重新画到树上（队列 + 已打开的标签）。"""
        paths = list(self._pending_imports.get(pack_path, {}))
        for doc in self._docs_with_pending_pack(pack_path):
            path = doc.source_pack[1]
            if path not in paths:
                paths.insert(0, path)
            if doc is self._doc:
                current = path
        self.resource_panel.show_pending_many(pack_path, paths,
                                             current=current)

    def _open_pending_layout(self, pack_path: str, res_path: str) -> bool:
        """双击「待入新包」叶子：打开队列里的那份（不从源包读）。"""
        store = self._pending_imports.get(pack_path) or {}
        doc = store.pop(res_path, None)
        if doc is None:
            return False
        self._open_in_tab(doc, ("pack", pack_path, res_path))
        self._show_pending_for(pack_path, current=res_path)
        self._update_status(
            f"已打开导入的 {res_path}（还没写进包）；保存时和其它导入布局一起写。")
        return True

    def _restore_pending_items(self) -> None:
        """刷新来源后把「待入新包」叶子重新挂回树上（多个包各挂各的）。"""
        first = True
        for pack_path, store in self._pending_imports.items():
            paths = list(store)
            current = None
            for doc in self._docs_with_pending_pack(pack_path):
                path = doc.source_pack[1]
                if path not in paths:
                    paths.insert(0, path)
                if doc is self._doc:
                    current = path
            if paths:
                self.resource_panel.show_pending_many(
                    pack_path, paths, current=current, clear=first)
                first = False

    def _adopt_pending_batch(self, source_pack, out_pack: str,
                             written: list[str]) -> None:
        """保存成功：批量导入队列整体迁到新包（必须在界面线程）。"""
        if not source_pack:
            return
        queued = self._pending_imports.pop(source_pack, {})
        for path, doc in queued.items():
            doc.pending_pack_import = False
            doc.mark_saved()
            doc.source_pack = (str(out_pack), path)
        # 队列里也可能有已打开标签的（打开过的从队列里拿出去过），
        # 一并把来源改成新包，避免下次保存又去写源包。
        for doc in self._docs_with_pending_pack(source_pack):
            doc.pending_pack_import = False
            doc.mark_saved()
            doc.source_pack = (str(out_pack), doc.source_pack[1])
        for path in written:
            self._remember_layout(str(path))
            self.resource_panel.add_known_layout(str(out_pack), str(path))
