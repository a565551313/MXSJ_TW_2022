"""资源浏览窗「保存新资源」：只把挂账新图写回包，不碰任何布局（0.18.0）。

Ctrl+S 只把「被当前布局引用到」的挂账图片带进包；没被引用的会一直
挂在内存里（保存后的警告框列过它们），重启就没了。本 mixin 给资源
浏览窗一个专门入口：按当前保存模式（严格=编辑器输出包，宽松=原包，
与 Ctrl+S 同一套目标决议）把**全部**挂账图片写进目标包，任何布局
条目都不读不写。

安全管线与布局保存完全同款：临时副本 + 原位补丁 + 原子替换**之前**
的回读校验（:func:`ui_editor.core.publish.verify_written_pack`，
``res_path=None`` 即「只写资源」形态）+ 未改条目逐字节保真；
成功才销账（清挂账），失败/取消时目标文件一个字节不动。
"""

from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from ..core import publish
from ..core.errors import Cancelled
from ..core.pack_build import patch_pack_copy_many
from .save_workflows import _StagingVerifyFailed

__all__ = ["StagedSaveMixin"]


class StagedSaveMixin:
    """主窗口「挂账新图 → 资源包」的专用保存链（不含布局）。"""

    def save_staged_resources(self) -> dict | None:
        """把全部挂账新图按保存模式写进包；返回报告（None = 没写）。"""
        staged = dict(self.resolver.staged_images())
        if not staged:
            QMessageBox.information(
                self, "保存新资源",
                "没有挂账的新资源。\n先在浏览窗用「把图片放进包…」"
                "或「几张图组成按钮（拼名族）…」挂账。")
            return None
        if self.doc is None or not self.doc.source_pack:
            QMessageBox.information(
                self, "保存新资源",
                "新资源要写回「它被浏览的那个包」：请先打开资源包里的"
                "任意布局，再按这个按钮。\n（严格模式下若还没存过，"
                "会先问一次输出包路径，与 Ctrl+S 一致。）")
            return None
        target = self._staged_save_target()
        if not target:
            return None
        if not self._confirm_staged_save(target, staged):
            return None
        in_place = (self._is_own_output(target)
                    or self._is_source_pack_target(target))
        src_pack = target if in_place else (
            self._save_target_pack() or self.doc.source_pack[0])
        # Windows 不允许 os.replace 覆盖打开中的文件：就地写前放手柄，
        # 失败路径负责挂回来（与 _save_to_pack 同款）。
        released = self.resolver.release_pack(src_pack) if in_place else False
        self._update_status("正在把新资源写入包并校验…")
        try:
            report = self.run_busy(
                "写入新资源并校验…",
                lambda h: self._write_staged_only_file(
                    src_pack, target, staged, in_place,
                    progress=h.report, cancelled=lambda: h.cancelled),
                cancellable=True, cancellable_text="取消（不写包）")
        except Cancelled:
            if released:
                self.resolver.mount_pack(src_pack, priority=True)
            self._update_status("写入已取消：目标包与原包都没动。")
            return None
        except _StagingVerifyFailed as exc:
            if released:
                self.resolver.mount_pack(src_pack, priority=True)
            QMessageBox.warning(
                self, "写回校验未通过",
                f"{exc}\n目标包没有改动，挂账仍然保留。")
            return None
        except Exception as exc:  # PackError/守卫拒绝/磁盘满…都没进入替换
            if released:
                self.resolver.mount_pack(src_pack, priority=True)
            QMessageBox.warning(self, "写入失败", str(exc))
            return None
        if not report or not report.get("ok"):
            if released:
                self.resolver.mount_pack(src_pack, priority=True)
            QMessageBox.warning(
                self, "写回校验未通过",
                (report or {}).get("error", "未知错误") + "\n目标包没有改动。")
            return report
        # 状态迁移在界面线程做（后台线程只写文件与校验）。
        self._adopt_staged_write(target, staged, report)
        return report

    # -- 目标决议与确认 -------------------------------------------------
    def _staged_save_target(self) -> str | None:
        """只存新资源的目标包：与 Ctrl+S 同一套决议（跟随保存模式）。

        严格模式：编辑器输出包（还没存过就问一次路径；**成功后**才记住，
        与 Ctrl+S 的 ``_report_save_target`` 时机一致）；
        宽松模式：一律回原包（``origin_pack`` 优先）。
        """
        if self._loose_mode():
            return self._save_target_pack() or self.doc.source_pack[0]
        target = self.doc.output_pack
        if not target:
            target = self._ask_output_pack()
        return target or None

    def _confirm_staged_save(self, target: str,
                             staged: dict[str, bytes]) -> bool:
        """写前确认：列清楚写哪些资源、写到哪、布局不动。"""
        names = sorted(staged)
        shown = "\n".join(f"· {name}" for name in names[:8])
        if len(names) > 8:
            shown += f"\n· ……等共 {len(names)} 个"
        if self._is_source_pack_target(target):
            where = "就地改写原包"
        elif self._is_own_output(target):
            where = "就地写入编辑器输出包"
        else:
            where = "写入新包"
        question = (
            f"将把 {len(names)} 个挂账新资源{where}：\n{target}\n\n"
            f"{shown}\n\n"
            "不会改动任何布局条目（校验通过后才原子替换）。继续吗？")
        return (QMessageBox.question(self, "只保存新资源", question)
                == QMessageBox.StandardButton.Yes)

    # -- 写文件（可在后台线程跑，不碰界面状态） -------------------------
    def _write_staged_only_file(self, src_pack: str, target: str,
                                staged: dict[str, bytes], in_place: bool,
                                *, progress=None, cancelled=None) -> dict:
        """只写文件 + 校验：``layouts={}`` 的 :func:`patch_pack_copy_many`。

        编码闸门与布局保存同款（原生字段编码检查不过就拒绝写入）；
        回读校验传 ``res_path=None``/``expected_dicts=None``——
        「只写资源」形态：新图逐字节回读 + 未改条目保真，没有布局项。
        """
        publish.require_save_encoding(self.doc, staged)
        verified: dict = {}

        def check_staging(path, info):
            """原子替换之前校验临时文件；失败即抛，替换不会发生。"""
            result = publish.verify_written_pack(
                src_pack=src_pack, out_path=path, res_path=None,
                extras=staged, expected_dicts=None, info=info,
                extra_layouts={}, progress=progress, cancelled=cancelled,
                read_back=self._fresh_pack_readback, trusted_copy=True)
            verified.update(result)
            if not result.get("ok"):
                raise _StagingVerifyFailed(
                    result.get("error") or "写回校验未通过")

        info = patch_pack_copy_many(
            src_pack, {}, target, extra_entries=staged,
            protected_paths=self._pack_sources(
                for_pack_write=True, allow=target if in_place else None),
            allow_overwrite_self=in_place,
            progress=progress, cancelled=cancelled,
            verify=check_staging)
        report: dict = {"out": target, "bytes": info["bytes"],
                        "mode": info["mode"],
                        "images_added": len(info["images_added"]),
                        "images_replaced": len(info["images_replaced"]),
                        "staged_written": sorted(staged)}
        report.update(verified)
        report["ok"] = "error" not in verified
        return report

    # -- 成功后的状态迁移（必须在界面线程） -----------------------------
    def _adopt_staged_write(self, target: str, staged: dict[str, bytes],
                            report: dict) -> None:
        """销账 + 包来源迁移；**不碰**布局脏状态与待入包队列。

        与布局保存的 ``_adopt_written_pack`` 的关键差异：不调
        ``mark_saved``/``clear_pending``（本次没写任何布局）。但包的
        「来源」要跟着迁移（``doc.source_pack`` → 写出的包）：严格模式
        下若不迁移，下一次 Ctrl+S 会从**原包**重新复制整包，把这次写进
        输出包的新资源悄悄丢掉（实测语义，见 0.18.0 设计说明）。
        """
        if self.resolver.pack_for(target) is not None:
            self.resolver.reload_pack(target)
        self.resolver.mount_pack(target, priority=True)
        self._add_pack_to_tree(target, self.resolver.scan_layouts(target))
        if self.doc is not None and self.doc.source_pack:
            if self.doc.origin_pack is None:
                self.doc.origin_pack = self.doc.source_pack[0]
            self.doc.source_pack = (target, self.doc.source_pack[1])
            self._report_save_target(target)   # 记住输出包（严格模式续写）
        self.resolver.discard_staged(sorted(staged))
        added = report.get("images_added", 0)
        replaced = report.get("images_replaced", 0)
        self._update_status(
            f"已写入 {len(staged)} 个新资源（新增 {added}、替换 {replaced}），"
            f"布局未改动：{target}")
        self._update_title()
