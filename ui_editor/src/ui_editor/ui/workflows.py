"""布局文件与资源包的打开、导入、保存、导出工作流。

由 MainWindow 组合；依赖宿主窗口状态，不接管 QObject 初始化。
保留原有方法名与实现，回调入口保持不变。
"""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QInputDialog,
    QMessageBox,
)

from ..core import dlg_codec, pack_build, publish
from ..core.assets import AssetResolver
from ..core.catalog import known_layout_paths
from ..core.errors import Cancelled
from ..core.layout_import import prepare_layout_import, validate_layout_path
from ..core.model import LayoutDocument
from ..core.output_paths import guard_output
from ..core.pack import FlsPack
from ..core.review import referenced_staged_images
from ..core.styles import StyleBook
from .layout_import_dialog import LayoutImportDialog
from .save_review import SaveReviewDialog


class FileWorkflowsMixin:
    """主窗口界面层的职责分组，不独立创建窗口。"""

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
                new_plain=dlg_codec.dump_bytes(
                    self.doc.to_dicts(), text_encoding=self.doc.text_encoding))
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
    def _fresh_pack_readback(pack_path, res_path: str, names,
                             text_encoding: str = "big5"):
        """回读钩子：用**全新**解析器读目标布局与各新图（`core.publish` 注入用）。

        故意不复用当前窗口的 resolver：新包是在别处写出来的，
        用它自己的解析器回读才算独立验证。
        """
        fresh = AssetResolver()
        fresh.text_encoding = text_encoding
        fresh.mount_pack(str(pack_path))
        try:
            got = fresh.fetch_dlg(res_path)
            dicts = None if got is None else got[0]
            return dicts, {name: fresh.fetch_bytes(name) for name in names}
        finally:
            fresh.close()

    def write_pack_copy(self, out_path: str, *, progress=None,
                        cancelled=None) -> dict | None:
        """把当前包内布局写回一个新包文件（原包不动）。返回校验报告。

        选图窗新加且被本布局引用到的图片随布局一并写入（按路径
        新增或替换）。写后硬性校验（条目数、目录升序、条目集合、
        二分命中、未改条目保真、全新解析器回读）已抽到
        :mod:`ui_editor.core.publish`——那是保存链最危险的一段，
        现在能脱离窗口直接测（分析报告建议④）；任一不过填
        ``report["error"]`` 并返回（弹错在对话框层）。

        ``progress``/``cancelled`` 透传给逐条保真校验；取消抛
        :class:`core.errors.Cancelled`（状态不迁移，调用方删未验证产物）。
        """
        if self.doc is None or not self.doc.source_pack:
            return None
        src_pack, res_path = self.doc.source_pack
        extras = self._referenced_staged_images()
        self._require_save_encoding(extras)
        plain = dlg_codec.dump_bytes(
            self.doc.to_dicts(), text_encoding=self.doc.text_encoding)
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
            progress=progress, cancelled=cancelled,
            read_back=(self._fresh_pack_readback
                       if self.doc.text_encoding == "big5" else
                       lambda p, r, n: self._fresh_pack_readback(
                           p, r, n, self.doc.text_encoding))))
        if not report.get("ok"):
            return report
        # 状态迁移：已验证落盘，标记干净并让后续保存续写新包
        self.resolver.mount_pack(tmp_out, priority=True)
        self._remember_layout(res_path)
        self._add_pack_to_tree(tmp_out, self.resolver.scan_layouts(tmp_out))
        self.doc.pending_pack_import = False
        self.resource_panel.clear_pending()
        self.doc.mark_saved()
        self.doc.source_bytes = plain
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
        try:
            report = self.run_busy(
                "写回资源包并校验…",
                lambda h: self.write_pack_copy(
                    path, progress=h.report, cancelled=lambda: h.cancelled),
                cancellable=True, cancellable_text="取消（删除未验证的新包）")
        except Cancelled:
            with suppress(OSError):
                Path(path).unlink(missing_ok=True)
            self._update_status("写回已取消：未验证的新包已删除，原包未动。")
            return
        except Exception as exc:
            QMessageBox.warning(self, "写回失败", str(exc))
            return
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
            data = dlg_codec.dump_bytes(
                self.doc.to_dicts(), text_encoding=self.doc.text_encoding)
            Path(path).write_bytes(data)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "保存失败", str(exc))
            return False
        self.doc.mark_saved()
        self.doc.source_bytes = data
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
