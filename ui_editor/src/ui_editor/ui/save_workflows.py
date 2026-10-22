"""保存工作流：散装 .dlg 原子保存与写回资源包。

由 MainWindow 组合（与 :mod:`ui_editor.ui.workflows` 平级）。
散装保存走「临时文件 → 回读校验 → fsync → 原子替换」；
写回资源包走 :mod:`ui_editor.core.publish` 的校验链。
"""

from __future__ import annotations

import os
import tempfile
from contextlib import suppress
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox,
)

from ..core import dlg_codec, pack_build, publish
from ..core.assets import AssetResolver
from ..core.errors import Cancelled
from ..core.output_paths import guard_output
from ..core.review import referenced_staged_images
from .save_review import SaveReviewDialog


class SaveWorkflowsMixin:
    """主窗口保存职责分组，不独立创建窗口。"""

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

        ``progress``/``cancelled`` 透传给写包与逐条校验；取消抛
        :class:`core.errors.Cancelled`（状态不迁移，调用方删未验证产物）。

        这个入口**写文件 + 迁移界面状态**（供测试/脚本用）。窗口里要
        放在忙碌遮罩后台线程跑的只有 :meth:`_write_pack_copy_file`：
        后台线程碰控件会卡死或崩，状态迁移由界面线程自己收尾。
        """
        report = self._write_pack_copy_file(
            out_path, progress=progress, cancelled=cancelled)
        if report is None or not report.get("ok"):
            return report
        self._adopt_written_pack(report)
        return report

    def _write_pack_copy_file(self, out_path: str, *, progress=None,
                              cancelled=None) -> dict | None:
        """只写文件 + 校验，**不碰界面状态**（可在后台线程跑）。

        返回的 ``report["plain"]`` 供 :meth:`_adopt_written_pack` 迁移用。
        """
        if self.doc is None or not self.doc.source_pack:
            return None
        src_pack, res_path = self.doc.source_pack
        extras = self._referenced_staged_images()
        self._require_save_encoding(extras)
        plain = dlg_codec.dump_bytes(
            self.doc.to_dicts(), text_encoding=self.doc.text_encoding)
        tmp_out = str(out_path)
        expected = self.doc.to_dicts()
        # 后台线程里**不要**再读文档/控件状态：把这一步需要的两个事实
        # 在界面线程先抓好，连同字节一起传下去。
        self._writing_pending_import = bool(self.doc.pending_pack_import)
        self._writing_encoding = self.doc.text_encoding
        report = self._write_pack_file(
            src_pack, res_path, plain, expected, extras, tmp_out,
            progress=progress, cancelled=cancelled)
        report["layout_path"] = res_path
        report["plain"] = plain
        report["extras"] = sorted(extras)
        return report

    def _write_pack_file(self, src_pack: str, res_path: str, plain: bytes,
                         expected: list[dict], extras: dict[str, bytes],
                         tmp_out: str, *, progress=None,
                         cancelled=None) -> dict:
        """落盘 + 校验（不碰界面状态、不读 self.doc）。"""
        # 写包本身也要进度：复制 614 MB、逐条校验 5.3 万条，机械盘上
        # 是十几秒到一分钟的活，只转圈会被当成卡死。
        info = pack_build.patch_pack_copy(
            src_pack, res_path, plain, tmp_out, extra_entries=extras,
            protected_paths=self._pack_sources(),
            allow_create=bool(self._writing_pending_import),
            progress=progress, cancelled=cancelled)
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
            extras=extras, expected_dicts=expected, info=info,
            progress=progress, cancelled=cancelled,
            read_back=(self._fresh_pack_readback
                       if self._writing_encoding == "big5" else
                       lambda p, r, n: self._fresh_pack_readback(
                           p, r, n, self._writing_encoding))))
        return report

    def _adopt_written_pack(self, report: dict) -> None:
        """校验通过后迁移界面状态（**必须在界面线程**调用）。"""
        if not report.get("ok"):
            return
        tmp_out = str(report.get("out"))
        res_path = str(report.get("layout_path") or "")
        plain = report.get("plain") or b""
        extras = report.get("extras") or []
        # 已验证落盘，标记干净并让后续保存续写新包
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
                lambda h: self._write_pack_copy_file(
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
        # 迁移在界面线程做（后台线程只写文件与校验）
        self._adopt_written_pack(report)
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
        temp_path: Path | None = None
        try:
            target = Path(path)
            guard_output(target, self._pack_sources())
            if not target.parent.is_dir():
                # 不替用户建目录：路径多半是打错的，悄悄建出来会让人
                # 以为存到了原来的地方（导出素材才按目录建）。放在保存前
                # 复核之前：打错目录时不必先点一遍「保存前检查」。
                raise ValueError(f"目标文件夹不存在：{target.parent}")
            if not self._confirm_save_review(path, to_pack=False):
                return False
            self._require_save_encoding({})
            data = dlg_codec.dump_bytes(
                self.doc.to_dicts(), text_encoding=self.doc.text_encoding)
            with tempfile.NamedTemporaryFile(
                    prefix=f".{target.name}.", suffix=".tmp",
                    dir=target.parent, delete=False) as handle:
                temp_path = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            parsed, _ = dlg_codec.parse_bytes(
                temp_path.read_bytes(), text_encoding=self.doc.text_encoding)
            if parsed != self.doc.to_dicts():
                raise ValueError("临时布局回读与当前文档不一致")
            os.replace(temp_path, target)
            temp_path = None
        except (OSError, ValueError, UnicodeError) as exc:
            QMessageBox.warning(self, "保存失败", str(exc))
            return False
        finally:
            if temp_path is not None:
                with suppress(OSError):
                    temp_path.unlink()
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
