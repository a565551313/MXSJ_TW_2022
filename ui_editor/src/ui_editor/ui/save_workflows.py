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
from ..core.errors import Cancelled, PackError
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
            # 散装 .dlg 本来就是覆盖自己的文件，两种模式一致。
            self._write_to(self.doc.source_path)
        elif self.doc.source_pack:
            if self._loose_mode():
                # 宽松模式：所有改动写入原包，不再问输出包、也不生成新包。
                target = self._save_target_pack() or self.doc.source_pack[0]
            else:
                target = self.doc.output_pack
                if not target:
                    target = self._ask_output_pack()
                    if not target:
                        return
            self._save_to_pack(target)
        else:
            self.save_as()

    # -- 写回资源包 ---------------------------------------------------
    def _referenced_staged_images(self) -> dict[str, bytes]:
        """选图窗挂账的新图里，被当前布局引用到的那些（随包写入）。"""
        if self.doc is None:
            return {}
        return referenced_staged_images(self.doc.to_dicts(),
                                        self.resolver.staged_images())

    def _confirm_save_review(self, target: str, *, to_pack: bool,
                             in_place: bool = False) -> bool:
        """保存前清单：数据部分在 `core.publish.save_review_plan`，这里只弹窗。"""
        if self.doc is None:
            return False
        try:
            guard_output(target, self._pack_sources(
                for_pack_write=to_pack,
                allow=target if in_place else None))
            pack_path, res_path = (
                (self._save_target_pack() or self.doc.source_pack[0],
                 self.doc.source_pack[1])
                if self.doc.source_pack else (None, None))
            extra_layouts = (self._pending_layout_dicts(pack_path)
                             if pack_path else {})
            extra_layouts.pop(res_path, None)
            plan = publish.save_review_plan(
                target=target, to_pack=to_pack,
                issues=self._layout_diagnostics(),
                staged=self.resolver.staged_images(),
                extras=self._referenced_staged_images(),
                pack_path=pack_path, res_path=res_path,
                pending_pack_import=self.doc.pending_pack_import,
                extra_layouts={
                    path: dlg_codec.dump_bytes(
                        dicts, text_encoding=self.doc.text_encoding)
                    for path, dicts in extra_layouts.items()},
                new_plain=dlg_codec.dump_bytes(
                    self.doc.to_dicts(), text_encoding=self.doc.text_encoding))
            # 「记住输出包」之后的日常保存不再每次拦一道清单：清单里的
            # 诊断警告（比如脚本索引里没找到的引用）是常驻信息，面板里随时
            # 能看，不该每次都拦一次保存。只有确实有新东西要用户确认
            # （待写入的新图、导入布局待入包）才弹。
            repeat = self.doc.output_pack == str(target)
            quiet = (repeat and not plan.images and not plan.layouts
                     and not self.doc.pending_pack_import)
            if quiet:
                return True
            dialog = SaveReviewDialog(target, self.doc.changes(), plan.issues,
                                      plan.images, to_pack=to_pack,
                                      parent=self, layout_notice=plan.notice,
                                      layouts=plan.layouts,
                                      in_place=in_place)
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
        extra_layouts = {}
        source_pack = None
        if self.doc is not None and self.doc.source_pack:
            source_pack = self._save_target_pack() or self.doc.source_pack[0]
            extra_layouts = self._pending_layout_dicts(source_pack)
            extra_layouts.pop(self.doc.source_pack[1], None)
        report = self._write_pack_copy_file(
            out_path, extra_layouts=extra_layouts,
            progress=progress, cancelled=cancelled)
        if report is None or not report.get("ok"):
            return report
        report["source_pack"] = source_pack
        report["batch_size"] = len(extra_layouts)
        self._adopt_written_pack(report)
        return report

    def _write_pack_copy_file(self, out_path: str, *,
                              pending_import: bool | None = None,
                              encoding: str | None = None,
                              extra_layouts: dict[str, list[dict]] | None = None,
                              progress=None,
                              cancelled=None) -> dict | None:
        """只写文件 + 校验，**不碰界面状态/控件**（可在后台线程跑）。

        返回的 ``report["plain"]`` 供 :meth:`_adopt_written_pack` 迁移用。

        ``extra_layouts``：批量导入待入新包的其它布局（``{包内路径: 字典}``），
        和当前布局一次复制包体、一次校验、一次原子替换写进去——不是每个
        布局各写一遍整包。

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
        src_pack = self._save_target_pack() or self.doc.source_pack[0]
        res_path = self.doc.source_pack[1]
        extras = self._referenced_staged_images()
        self._require_save_encoding(extras)
        plain = dlg_codec.dump_bytes(
            self.doc.to_dicts(), text_encoding=encoding)
        tmp_out = str(out_path)
        layouts = {res_path: plain}
        expected = {res_path: self.doc.to_dicts()}
        for path, dicts in (extra_layouts or {}).items():
            if path == res_path:
                continue
            layouts[path] = dlg_codec.dump_bytes(
                dicts, text_encoding=encoding)
            expected[path] = dicts
        report = self._write_pack_file(
            src_pack, res_path, layouts, expected, extras, tmp_out,
            pending_import=pending_import, encoding=encoding,
            overwrite_self=(self._is_own_output(tmp_out)
                            or self._is_source_pack_target(tmp_out)),
            progress=progress, cancelled=cancelled)
        report["layout_path"] = res_path
        report["layout_paths"] = list(layouts)
        report["plain"] = plain
        report["extras"] = sorted(extras)
        return report

    def _write_pack_file(self, src_pack: str, res_path: str,
                         layouts: dict[str, bytes],
                         expected: dict[str, list[dict]],
                         extras: dict[str, bytes], tmp_out: str, *,
                         pending_import: bool, encoding: str,
                         overwrite_self: bool = False,
                         progress=None, cancelled=None) -> dict:
        """落盘 + 校验（不碰界面状态、不读 self.doc）。

        ``layouts`` 是这次要写进新包的全部布局（``{包内路径: 明文}``）；
        ``res_path`` 是当前文档自己的那条，报告的 ``target_write``
        只描述它。

        ``pending_import`` / ``encoding`` / ``overwrite_self`` 是显式参数，
        不再挂在 ``self`` 上：每次写包各用各的值，互不串味。
        ``overwrite_self`` 只在上次的输出包 == 这次的目标时为真（原子替换）。
        """
        # 写包本身也要进度：复制 614 MB、逐条校验 5.3 万条，机械盘上
        # 是十几秒到一分钟的活，只转圈会被当成卡死。
        # 队列里的布局是「待入包」的新路径，必须允许新建；当前文档只有
        # 自己也是待入包时才允许。否则在「包里已有布局」的标签上按 Ctrl+S
        # 会拿新路径去 _plan_patch，报「包中找不到条目」，整批都存不进去。
        create_paths = set(layouts) - {res_path}
        if pending_import:
            create_paths.add(res_path)
        read_back = (self._fresh_pack_readback
                     if encoding == "big5" else
                     lambda p, r, n: self._fresh_pack_readback(
                         p, r, n, encoding))
        verified: dict = {}

        def check_staging(path, info):
            """原子替换之前校验临时文件（结构 + 回读）。

            以前这一步跑在 ``os.replace`` 之后：校验不过时目标文件已经被
            换掉了——目标正是原包（宽松模式）时，那就是「校验失败但原包
            已经毁了」。现在失败就抛，替换不会发生。
            """
            result = publish.verify_written_pack(
                src_pack=src_pack, out_path=path, res_path=res_path,
                extras=extras, expected_dicts=expected[res_path], info=info,
                extra_layouts={p: d for p, d in expected.items()
                               if p != res_path},
                progress=progress, cancelled=cancelled,
                read_back=read_back, trusted_copy=True)
            verified.update(result)
            if not result.get("ok"):
                raise PackError(result.get("error") or "写回校验未通过")

        info = pack_build.patch_pack_copy_many(
            src_pack, layouts, tmp_out, extra_entries=extras,
            protected_paths=self._pack_sources(
                for_pack_write=True,
                allow=tmp_out if overwrite_self else None),
            allow_create=create_paths or False,
            allow_overwrite_self=overwrite_self,
            progress=progress, cancelled=cancelled,
            verify=check_staging)
        report: dict = {"out": tmp_out, "bytes": info["bytes"],
                        "mode": info["mode"],
                        "layout_added": bool(info.get("layout_added")),
                        "layouts_added": list(info.get("layouts_added") or []),
                        "layouts_replaced": list(
                            info.get("layouts_replaced") or []),
                        "native_layout_storage": bool(
                            info.get("native_layout_storage")),
                        "images_added": len(info["images_added"]),
                        "images_replaced": len(info["images_replaced"])}
        staged_all = set(self.resolver.staged_images())
        report["staged_unreferenced"] = sorted(staged_all - set(extras))
        target_write = publish.classify_target_path(
            src_pack, res_path, layouts[res_path])
        report["target_write"] = target_write.summary
        report["target_write_kind"] = target_write.storage
        # 校验结果来自替换前那次（check_staging），这里只并入报告。
        report.update(verified)
        report["ok"] = "error" not in verified
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
        source_pack = report.get("source_pack") or (
            self.doc.source_pack[0] if self.doc.source_pack else None)
        self.doc.pending_pack_import = False
        self.resource_panel.clear_pending()
        if self.doc.origin_pack is None and self.doc.source_pack:
            self.doc.origin_pack = self.doc.source_pack[0]
        self.doc.mark_saved()
        self.doc.source_bytes = plain
        self.doc.source_pack = (tmp_out, res_path)
        # 批量导入的布局也一起销账：它们已经在新包里，队列清空，
        # 打开的标签改成「来自新包」。树上的叶子按写出的清单补齐。
        self._adopt_pending_batch(source_pack, tmp_out,
                                  report.get("layout_paths") or [res_path])
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
        src_pack = self._save_target_pack() or self.doc.source_pack[0]
        res_path = self.doc.source_pack[1]
        in_place = self._is_source_pack_target(path)
        if not self._confirm_save_review(path, to_pack=True, in_place=in_place):
            return False
        # 这两个事实在界面线程抓好再交给后台：后台只写文件、不回头读文档。
        pending_import = bool(self.doc.pending_pack_import)
        encoding = self.doc.text_encoding
        # 批量导入的布局和当前布局一起写：一次复制、一次校验、一次替换。
        extra_layouts = self._pending_layout_dicts(src_pack)
        extra_layouts.pop(res_path, None)
        # Windows 不能 os.replace 覆盖打开中的文件：写前放掉句柄，写后挂回。
        released = False
        if (Path(path).resolve() == Path(src_pack).resolve()
                and (self._is_own_output(path) or in_place)):
            # 宽松模式改写原包同样要先放手：Windows 不允许覆盖打开中的文件。
            released = self.resolver.release_pack(path)
        self._update_status("正在写回资源包并校验…")
        try:
            report = self.run_busy(
                "写回资源包并校验…",
                lambda h: self._write_pack_copy_file(
                    path, pending_import=pending_import, encoding=encoding,
                    extra_layouts=extra_layouts,
                    progress=h.report, cancelled=lambda: h.cancelled),
                cancellable=True, cancellable_text="取消（不写新包）")
        except Cancelled:
            # patch_pack_copy 在 os.replace 之前取消，并自己删掉临时文件；
            # path 可能是用户选来覆盖的旧包，这里不能删。
            if released:
                self.resolver.mount_pack(path, priority=True)
            self._update_status(
                "写回已取消：没有写出新包，原包与目标文件都没动。")
            return False
        except PackError as exc:
            # 校验在原子替换之前跑：失败时目标文件（可能就是原包）没动过。
            if released:
                self.resolver.mount_pack(path, priority=True)
            target = ("原包" if in_place else
                      "目标包" if self._is_own_output(path) else "已有文件")
            QMessageBox.warning(
                self, "写回校验未通过",
                f"{exc}\n{target}没有改动，可以继续编辑后重试。")
            return False
        except Exception as exc:
            if released:
                self.resolver.mount_pack(path, priority=True)
            QMessageBox.warning(self, "写回失败", str(exc))
            return False
        if not report or not report.get("ok"):
            if released:
                self.resolver.mount_pack(path, priority=True)
            QMessageBox.warning(
                self, "写回校验未通过",
                (report or {}).get("error", "未知错误")
                + "\n目标文件没有改动。")
            return False
        # 迁移在界面线程做（后台线程只写文件与校验）。
        # 先记下保存目标再迁移：adopt 里会刷新标题，晚一步标题就还写着
        # 「还没写回新包」。
        had_output = bool(self.doc.output_pack)
        report["source_pack"] = src_pack
        report["batch_size"] = len(extra_layouts)
        self.doc.output_pack = str(path)
        self._adopt_written_pack(report)
        unused = report.get("staged_unreferenced") or []
        extra_note = ""
        if report.get("images_added") or report.get("images_replaced"):
            extra_note += (f"，并写入新图 {report.get('images_added', 0)} 张、"
                           f"替换 {report.get('images_replaced', 0)} 张")
        changed = report.get("changed_entries")
        same_file = Path(path).resolve() == Path(src_pack).resolve()
        # 同一文件原地写回（宽松模式写原包，或续写自己的输出包）：现在是
        # 拿「写前的文件」和临时副本比，所以能给出真实条数，不再是「0 条」。
        prefix = "就地写回，" if same_file else ""
        if changed is None:
            changed_note = prefix + "包内条目已更新"
        elif changed:
            changed_note = f"{prefix}改变 {changed} 条"
        else:
            changed_note = f"{prefix}内容与包内一致"
        # 保存成功不再弹模态框：这次设计的目标就是「之后 Ctrl+S 静默写回」。
        # 需要用户动手的（有新图没被引用、没写进包）才弹。
        where = f"原包：{path}" if in_place else f"新包：{path}"
        if unused:
            shown = "\n".join(f"· {name}" for name in unused[:6])
            if len(unused) > 6:
                shown += f"\n· ……等共 {len(unused)} 张"
            QMessageBox.warning(
                self, "已写回（有新图未写入）",
                f"已写回：{res_path}\n{where}\n\n"
                f"⚠ 有 {len(unused)} 张「把图片放进包」的图片未被当前布局"
                "引用，未写入新包：\n" + shown +
                "\n\n要写入：先在本布局的控件上把图片改选为上面列出的"
                "新图（或在该图片所在的布局里保存），再保存回包。")
            self._update_status(
                f"已写回 {res_path} → {Path(path).name}，"
                f"但有 {len(unused)} 张新图没被引用、未写进包。")
            return True
        batch = int(report.get("batch_size") or 0)
        batch_note = f"，连同 {batch} 个导入布局一起写入" if batch else ""
        if in_place:
            self._update_status(
                f"已直接写回原包：{res_path} → {Path(path).name}"
                f"（{changed_note}{extra_note}{batch_note}）。"
                "宽松模式：没有留备份。")
            return True
        if not had_output:
            self._update_status(
                f"已写回：{res_path} → {Path(path).name}"
                f"（{changed_note}{extra_note}{batch_note}）。"
                "安装时先备份原包、再把新包改名替换；以后 Ctrl+S 直接写回"
                "这个包，不再询问。")
        else:
            self._update_status(
                f"已写回：{res_path} → {Path(path).name}"
                f"（{changed_note}{extra_note}{batch_note}）。")
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
