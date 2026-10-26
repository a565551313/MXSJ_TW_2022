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
"""

from __future__ import annotations

from collections.abc import Callable

from .image_picker import ResourcePickerDialog

# 导出处理函数的真源在 property_panel（既有测试按该模块命名空间打补丁），
# 这里复用同一份实现，避免复制粘贴漂移。
from .property_panel import make_export_handler

__all__ = ["AssetBrowserMixin", "build_browser_dialog",
           "make_export_handler", "open_asset_browser"]


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
