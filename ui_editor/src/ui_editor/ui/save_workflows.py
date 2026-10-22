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
    """主窗口保存职责分组，不独立创建窗口。

    保存只有一种意思：**回到它来的地方**。散装 ``.dlg`` 覆盖原文件；
    包内布局写回「上次写出的那个新包」（第一次问一次路径，之后静默写）。
    要换地方走 :meth:`save_as` / :meth:`save_to_pack_dialog`（另存为），
    要拿副本走导出。原包永远只读。
    """

    def save(self) -> None:
        """Ctrl+S：不再弹「存回资源包还是另存为」，也不再套 `_patched`。"""
        if self.doc is None:
            return
        if self.doc.source_path:
            self._write_to(self.doc.source_path)
        elif self.doc.source_pack:
            target = self.doc.output_pack
            if not target:
                target = self._ask_output_pack()
                if not target:
                    return
            self._save_to_pack(target)
        else:
            self.save_as()

    # -- 包内布局：记住输出包 ------------------------------------------
    def _own_output_pack(self) -> Path | None:
        """当前文档自己写出来的推广包（不是源；允许被下次保存覆盖）。"""
        if self.doc is None or not self.doc.output_pack:
            return None
        try:
            return Path(self.doc.output_pack).resolve()
        except OSError:
            return None

    def _is_own_output(self, path: str) -> bool:
        """这次要写的是不是编辑器自己上次写出来的那个包。"""
        if self.doc is None or not self.doc.output_pack:
            return False
        try:
            return Path(path).resolve() == Path(self.doc.output_pack).resolve()
        except OSError:
            return False

    def _default_output_pack(self) -> str:
        """第一次保存的默认名字：``<原包名>_edited.fls``，不再叠 _patched。"""
        source = ""
        if self.doc is not None:
            source = str(self.doc.origin_pack or
                         (self.doc.source_pack[0]
                          if self.doc.source_pack else ""))
        if not source:
            return ""
        folder = Path(source).parent
        stem = Path(source).stem
        for suffix in ("_edited", "_patched"):
            while stem.lower().endswith(suffix):
                stem = stem[: -len(suffix)]
        taken = {str(Path(source).resolve())}
        own = self._own_output_pack()
        if own is not None:
            taken.add(str(own))
        for index in range(1, 100):
            name = (f"{stem}_edited.fls" if index == 1
                    else f"{stem}_edited{index}.fls")
            candidate = folder / name
            if str(candidate.resolve()) in taken:
                continue
            if not candidate.exists():
                return str(candidate)
        return str(folder / f"{stem}_edited.fls")

    def _ask_output_pack(self) -> str | None:
        path, _ = QFileDialog.getSaveFileName(
            self, "保存为新资源包（原包不动，下次 Ctrl+S 直接写这里）",
            self._default_output_pack(),
            "资源包 (*.fls);;所有文件 (*)")
        return path or None

    def _report_save_target(self, path: str) -> None:
        if self.doc is None:
            return
        self.doc.output_pack = str(path)
        self._update_title()

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
            # 「记住输出包」之后的日常保存不再每次拦一道清单：清单里的
            # 诊断警告（比如脚本索引里没找到的引用）是常驻信息，面板里随时
            # 能看，不该每次都拦一次保存。只有确实有新东西要用户确认
            # （待写入的新图、导入布局待入包）才弹。
            repeat = self.doc.output_pack == str(target)
            quiet = (repeat and not plan.images
                     and not self.doc.pending_pack_import)
            if quiet:
                return True
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
        :class:`core.errors.Cancelled`（状态不迁移；临时文件由
        ``patch_pack_copy`` 自己删，用户选的目标路径保持原样）。

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

    def _write_pack_copy_file(self, out_path: str, *,
                              pending_import: bool | None = None,
                              encoding: str | None = None,
                              progress=None,
                              cancelled=None) -> dict | None:
        """只写文件 + 校验，**不碰界面状态/控件**（可在后台线程跑）。

        返回的 ``report["plain"]`` 供 :meth:`_adopt_written_pack` 迁移用。

        ``pending_import`` / ``encoding`` 由调用方（界面线程）抓好再传进来：
        后台线程再回头读文档会有竞态，两次并发写也会互相覆盖。不传时在这里
        按当前文档取一次（测试/脚本直接调用这个入口的情况）。
        """
        if self.doc is None or not self.doc.source_pack:
            return None
        if pending_import is None:
            pending_import = bool(self.doc.pending_pack_import)
        if encoding is None:
            encoding = self.doc.text_encoding
        src_pack, res_path = self.doc.source_pack
        extras = self._referenced_staged_images()
        self._require_save_encoding(extras)
        plain = dlg_codec.dump_bytes(
            self.doc.to_dicts(), text_encoding=encoding)
        tmp_out = str(out_path)
        expected = self.doc.to_dicts()
        report = self._write_pack_file(
            src_pack, res_path, plain, expected, extras, tmp_out,
            pending_import=pending_import, encoding=encoding,
            overwrite_self=self._is_own_output(tmp_out),
            progress=progress, cancelled=cancelled)
        report["layout_path"] = res_path
        report["plain"] = plain
        report["extras"] = sorted(extras)
        return report

    def _write_pack_file(self, src_pack: str, res_path: str, plain: bytes,
                         expected: list[dict], extras: dict[str, bytes],
                         tmp_out: str, *, pending_import: bool,
                         encoding: str, overwrite_self: bool = False,
                         progress=None, cancelled=None) -> dict:
        """落盘 + 校验（不碰界面状态、不读 self.doc）。

        ``pending_import`` / ``encoding`` / ``overwrite_self`` 是显式参数，
        不再挂在 ``self`` 上：每次写包各用各的值，互不串味。
        ``overwrite_self`` 只在上次的输出包 == 这次的目标时为真（原子替换）。
        """
        # 写包本身也要进度：复制 614 MB、逐条校验 5.3 万条，机械盘上
        # 是十几秒到一分钟的活，只转圈会被当成卡死。
        info = pack_build.patch_pack_copy(
            src_pack, res_path, plain, tmp_out, extra_entries=extras,
            protected_paths=self._pack_sources(),
            allow_create=pending_import,
            allow_overwrite_self=overwrite_self,
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
                       if encoding == "big5" else
                       lambda p, r, n: self._fresh_pack_readback(
                           p, r, n, encoding))))
        return report

    def _adopt_written_pack(self, report: dict) -> None:
        """校验通过后迁移界面状态（**必须在界面线程**调用）。"""
        if not report.get("ok"):
            return
        tmp_out = str(report.get("out"))
        res_path = str(report.get("layout_path") or "")
        plain = report.get("plain") or b""
        extras = report.get("extras") or []
        # 同一个文件被原地覆盖：包对象还握着替换前的句柄，先关掉再挂回来，
        # 否则画布继续拿旧字节画（保存了却看不到变化）。
        if self.resolver.pack_for(tmp_out) is not None:
            self.resolver.reload_pack(tmp_out)
        # 已验证落盘，标记干净并让后续保存续写新包
        self.resolver.mount_pack(tmp_out, priority=True)
        self._remember_layout(res_path)
        self._add_pack_to_tree(tmp_out, self.resolver.scan_layouts(tmp_out))
        self.doc.pending_pack_import = False
        self.resource_panel.clear_pending()
        if self.doc.origin_pack is None and self.doc.source_pack:
            self.doc.origin_pack = self.doc.source_pack[0]
        self.doc.mark_saved()
        self.doc.source_bytes = plain
        self.doc.source_pack = (tmp_out, res_path)
        self.resource_panel.expand_pack(tmp_out)
        self.resource_panel.reveal_selection(("pack", tmp_out, res_path))
        self.resolver.discard_staged(list(extras))  # 已进新包，销账
        self._update_title()

    def save_as_default(self) -> None:
        """工具栏「另存为」主按钮：包内布局 → 新资源包；其余 → 散装 .dlg。"""
        if self.doc is not None and self.doc.source_pack:
            self.save_to_pack_dialog()
        else:
            self.save_as()

    def save_to_pack_dialog(self) -> None:
        """另存为 ▸ 新资源包：每次都重新选路径（Ctrl+S 用的是记住的那个）。"""
        if self.doc is None or not self.doc.source_pack:
            QMessageBox.information(
                self, "另存为新资源包",
                "当前布局不是从资源包打开的（散装/新建布局请用"
                "「另存为 ▸ 散装布局」）。")
            return
        path = self._ask_output_pack()
        if path:
            self._save_to_pack(path)

    def _save_to_pack(self, path: str) -> bool:
        """把当前布局写进 ``path`` 这个新包（原包只读）。"""
        if self.doc is None or not self.doc.source_pack:
            return False
        res_path = self.doc.source_pack[1]
        if not self._confirm_save_review(path, to_pack=True):
            return False
        # 这两个事实在界面线程抓好再交给后台：后台只写文件，不再回头读
        # 文档状态；两次写包也不会互相覆盖（各用各的参数）。
        pending_import = bool(self.doc.pending_pack_import)
        encoding = self.doc.text_encoding
        self._update_status("正在写回资源包并校验…")
        try:
            report = self.run_busy(
                "写回资源包并校验…",
                lambda h: self._write_pack_copy_file(
                    path, pending_import=pending_import, encoding=encoding,
                    progress=h.report, cancelled=lambda: h.cancelled),
                cancellable=True, cancellable_text="取消（不写新包）")
        except Cancelled:
            # patch_pack_copy 在 os.replace 之前取消，并自己删掉临时文件；
            # path 可能是用户选来覆盖的旧包，这里不能删。
            self._update_status(
                "写回已取消：没有写出新包，原包与目标文件都没动。")
            return False
        except Exception as exc:
            QMessageBox.warning(self, "写回失败", str(exc))
            return False
        if not report or not report.get("ok"):
            QMessageBox.warning(
                self, "写回校验未通过",
                (report or {}).get("error", "未知错误")
                + "\n新包文件已生成但不可信，请勿替换进客户端。")
            return False
        # 迁移在界面线程做（后台线程只写文件与校验）。
        # 先记下保存目标再迁移：adopt 里会刷新标题，晚一步标题就还写着
        # 「还没写回新包」。
        had_output = bool(self.doc.output_pack)
        self.doc.output_pack = str(path)
        self._adopt_written_pack(report)
        unused = report.get("staged_unreferenced") or []
        extra_note = ""
        if report.get("images_added") or report.get("images_replaced"):
            extra_note += (f"，并写入新图 {report.get('images_added', 0)} 张、"
                           f"替换 {report.get('images_replaced', 0)} 张")
        changed = report.get("changed_entries")
        if changed is None:
            changed_note = "就地写回，包内条目已更新"
        elif changed:
            changed_note = f"改变 {changed} 条"
        else:
            changed_note = "内容与包内一致"
        # 保存成功不再弹模态框：这次设计的目标就是「之后 Ctrl+S 静默写回」。
        # 需要用户动手的（有新图没被引用、没写进包）才弹。
        if unused:
            shown = "\n".join(f"· {name}" for name in unused[:6])
            if len(unused) > 6:
                shown += f"\n· ……等共 {len(unused)} 张"
            QMessageBox.warning(
                self, "已生成新包（有新图未写入）",
                f"已写回：{res_path}\n新包：{path}\n\n"
                f"⚠ 有 {len(unused)} 张「把图片放进包」的图片未被当前布局"
                "引用，未写入新包：\n" + shown +
                "\n\n要写入：先在本布局的控件上把图片改选为上面列出的"
                "新图（或在该图片所在的布局里保存），再保存回包。")
            self._update_status(
                f"已写回 {res_path} → {Path(path).name}，"
                f"但有 {len(unused)} 张新图没被引用、未写进包。")
            return True
        if not had_output:
            self._update_status(
                f"已写回：{res_path} → {Path(path).name}"
                f"（{changed_note}{extra_note}）。"
                "安装时先备份原包、再把新包改名替换；以后 Ctrl+S 直接写回"
                "这个包，不再询问。")
        else:
            self._update_status(
                f"已写回：{res_path} → {Path(path).name}"
                f"（{changed_note}{extra_note}）。")
        return True

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
        self.doc.output_pack = None   # 散装文件不再写回包
        self.doc.origin_pack = None
        self._update_title()
        return True

    def _pack_sources(self) -> list[Path]:
        """受保护的源包：游戏原包、其它已挂载包、同目录里还没挂载的包。

        当前文档**自己写出来的**输出包不算源——它是保存目标。不排除的话，
        第二次 Ctrl+S 会被 `guard_output` 当成「覆盖源资源」拒掉（实测）。
        """
        sources = list(self.resolver.pack_paths)
        if self.doc and self.doc.source_pack:
            sources.append(Path(self.doc.source_pack[0]))
        # 同一客户端资源目录中尚未挂载的包也不能被另存覆盖。
        directories = {source.parent for source in sources}
        for directory in directories:
            try:
                sources.extend(path for path in directory.iterdir()
                               if path.suffix.lower() == ".fls")
            except OSError:
                continue
        own = self._own_output_pack()
        kept: list[Path] = []
        seen: set[str] = set()
        for path in sources:
            try:
                resolved = str(path.resolve())
            except OSError:
                resolved = str(path)
            if own is not None and resolved == str(own):
                continue
            if resolved in seen:
                continue
            seen.add(resolved)
            kept.append(path)
        return kept

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
