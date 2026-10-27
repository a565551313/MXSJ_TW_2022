"""工具栏「资源」按钮：把选图窗当独立浏览器打开（0.17.0）。

选图窗（``image_picker.ResourcePickerDialog``）原来只能从属性面板
图片字段的「…」进入，且绑定「选完写回某个属性」。本模块给它一个
不绑定属性的独立入口：

* 看：搜索 / 缩略图 / 拼名族说明，与属性路径完全同款；
* 导出副本、把图片放进包、几张图组成按钮（拼名族）都保留——这些是
  资源级操作，不依赖目标属性；
* **只有「选完写回控件属性」没有**：浏览模式没有目标属性，确定按钮
  改成「关闭」，双击条目也只关闭，不写任何东西。

导出副本的处理函数从属性面板原封不动搬来（``make_export_handler``），
两条路径共用一份实现，避免复制粘贴漂移。

0.21.0 加第二个独立入口——工具栏「批图」按钮：直接从磁盘选图片
文件 / 选文件夹批处理（缩放 / 亮度 / 饱和度），磁盘进磁盘出、
不用挂包也不用打开任何布局；参数窗与执行链和浏览窗「批量处理…」
共用同一套（:mod:`.image_batch`），见 :meth:`AssetBrowserMixin._run_disk_batch`。
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from .image_picker import ResourcePickerDialog

# 导出处理函数的真源在 property_panel（既有测试按该模块命名空间打补丁），
# 这里复用同一份实现，避免复制粘贴漂移。
from .property_panel import make_export_handler

__all__ = ["AssetBrowserMixin", "build_browser_dialog",
           "make_export_handler", "open_asset_browser"]

# 批处理范围＝与浏览窗分筛同一组（PNG/JPG/BMP/TGA ＋ .igs）。
_PLAIN_SUFFIXES = (".png", ".jpg", ".jpeg", ".bmp", ".tga")
_BATCH_SUFFIXES = _PLAIN_SUFFIXES + (".igs",)


def build_browser_dialog(host, assets, candidates: list[str],
                         widget_type: str | None = None,
                         save_staged: Callable[[], bool] | None = None
                         ) -> ResourcePickerDialog:
    """组装浏览模式的选图窗（不 exec，便于测试）。"""
    def thumb(path: str):
        frames = assets.fetch_image(path)
        return frames[0] if frames else None

    def family_label(path: str) -> str | None:
        from ..core import dir_base
        return dir_base.describe(assets.family_plan(path))

    def family_pieces(path: str) -> list[str] | None:
        pieces = assets.family_pieces(path)
        if not pieces:
            return None
        prefix = path.replace("\\", "/").rstrip("/") + "/"
        relative: list[str] = []
        for piece in pieces:
            text = piece.replace("\\", "/")
            if text.startswith(prefix):
                relative.append(text[len(prefix):])
            else:
                relative.append(text.rsplit("/", 1)[-1])
        return relative

    def family_kind(path: str) -> str | None:
        chosen = assets.family_plan(path)
        return chosen.kind if chosen is not None else None

    return ResourcePickerDialog(
        host, "浏览资源（看 / 导出 / 放进包 / 拼名族；不写控件属性）",
        candidates, "",
        thumb,
        on_stage=assets.stage_image,
        export_handler=make_export_handler(assets, host),
        family_label=family_label,
        widget_type=widget_type,
        exists=assets.resource_exists,
        family_pieces=family_pieces,
        family_kind=family_kind,
        browse_only=True,
        save_staged=save_staged,
        staged_count=(lambda: len(assets.staged_images())
                      if save_staged is not None else None),
        fetch_bytes=assets.fetch_bytes)


def open_asset_browser(host, assets, widget_type: str | None = None,
                       save_staged: Callable[[], bool] | None = None) -> None:
    """整理包内资源清单后打开浏览窗；关闭即结束，不写任何属性。"""
    from .busy import run_busy_or_plain

    def build_candidates(h):
        return list(assets.candidates_with_staged(h.report))

    candidates = run_busy_or_plain(
        host.window() if hasattr(host, "window") else host,
        "整理包内资源清单（首次较慢）…", build_candidates)
    build_browser_dialog(host, assets, candidates,
                         widget_type, save_staged=save_staged).exec()


class AssetBrowserMixin:
    """主窗口 mixin：工具栏「资源」按钮的入口。"""

    def browse_resources(self) -> None:
        assets = getattr(self, "resolver", None)
        if assets is None or not assets._packs:
            self._update_status(
                "还没挂载资源包：先「打开 ▸ 资源包（.fls…）」"
                "或「打开 ▸ 资源目录…」，再点「资源」浏览。")
            return
        open_asset_browser(self, assets,
                           save_staged=self._browser_save_staged)

    def _browser_save_staged(self) -> bool:
        """浏览窗「保存新资源」按钮的宿主端：写包并回报成败（0.18.0）。"""
        handler = getattr(self, "save_staged_resources", None)
        if handler is None:
            return False
        report = handler()
        return bool(report and report.get("ok"))

    # -- 0.21.0：图像批处理独立入口（磁盘进磁盘出，不用挂包） ------------
    def batch_images_from_disk(self) -> None:
        """工具栏「批图」主按钮：从磁盘选图片文件（可多选）批处理。"""
        files, _filter = QFileDialog.getOpenFileNames(
            self, "选择要批处理的图片（可多选）",
            self._settings.value("batch_dir", ""),
            "图片 (*.png *.jpg *.jpeg *.bmp *.tga *.igs);;所有文件 (*)")
        if not files:
            return
        self._settings.setValue("batch_dir", str(Path(files[0]).parent))
        self._run_disk_batch([str(f) for f in files])

    def batch_folder_from_disk(self) -> None:
        """小箭头「选文件夹批处理…」：只扫文件夹顶层的支持格式。

        不递归钻子文件夹——范围可预期，也免得误吞整棵大树；要处理
        子文件夹就再点一次选它。
        """
        folder = QFileDialog.getExistingDirectory(
            self, "选择要批处理的图片文件夹",
            self._settings.value("batch_dir", ""))
        if not folder:
            return
        self._settings.setValue("batch_dir", folder)
        paths = sorted(
            str(p) for p in Path(folder).iterdir()
            if p.is_file() and p.suffix.lower() in _BATCH_SUFFIXES)
        if not paths:
            self._update_status(
                f"{folder}：没找到可批处理的图片"
                "（PNG/JPG/BMP/TGA/.igs，只扫了这一层）")
            return
        self._run_disk_batch(paths)

    def _run_disk_batch(self, paths: Sequence[str]) -> None:
        """磁盘批处理共用执行链：读字节 → 参数窗 → 执行 → 回报。

        与浏览窗「批量处理…」同一套规矩（:mod:`.image_batch`）：
        范围外后缀 / 读不到的文件拒收并各给一句话原因，能处理的照常
        进参数窗；原文件一律不动；输出永不覆盖；单项失败不中断整批。
        差别只在字节来自磁盘、且**只能写磁盘**——磁盘文件没有包内
        路径，「挂账进包」无从谈起（参数窗 ``can_stage=False``）。
        """
        items: list[tuple[str, str, bytes]] = []
        rejected: list[str] = []
        for path in paths:
            suffix = Path(path).suffix.lower()
            if suffix == ".igs":
                kind = "igs"
            elif suffix in _PLAIN_SUFFIXES:
                kind = "image"
            else:
                rejected.append(
                    f"{path}：{suffix or '无后缀'} 不在批处理范围"
                    "（PNG/JPG/BMP/TGA/.igs）")
                continue
            try:
                data = Path(path).read_bytes()
            except OSError as exc:
                rejected.append(f"{path}：读不到文件（{exc}）")
                continue
            items.append((path, kind, data))
        if not items:
            QMessageBox.warning(
                self, "选中的都不能批处理", "\n".join(rejected[:8]))
            return
        from .image_batch import ImageBatchDialog, run_batch
        dialog = ImageBatchDialog(
            self, items, suggested_dir=str(Path(paths[0]).parent),
            can_stage=False)
        if dialog.exec() != QDialog.DialogCode.Accepted or \
                dialog.plan is None:
            return
        plan = dialog.plan
        ok, failed = run_batch(items, plan, stage=None)
        failed.extend(rejected)
        if failed:
            QMessageBox.warning(
                self, "有些没能处理",
                "下面这些没有批处理成功：\n\n" + "\n".join(failed[:8]))
        if ok:
            self._update_status(
                f"图像批处理完成 {len(ok)} 张 → 写入 {plan.out_dir}")
