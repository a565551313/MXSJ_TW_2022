"""保存目标解析：输出包、来源包与「哪些包不能被覆盖」。

从 :mod:`ui_editor.ui.save_workflows` 抽出来的一组方法，只做路径与保护
名单的判定，不写文件：

* 严格模式：Ctrl+S 写「上次的输出包」；第一次问一次（默认
  ``<原包名>_edited.fls``）。
* 宽松模式：Ctrl+S 直接写布局所在的资源包（见 :mod:`ui_editor.ui.save_mode`）。

``_pack_sources`` 决定 ``guard_output`` 的保护名单：游戏原包与其它已挂载包
永远受保护；只有「这次明确要写的目标」（自己的输出包，或宽松模式下的原包）
由调用方用 ``allow`` 剔除。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog

__all__ = ["SaveTargetsMixin"]


class SaveTargetsMixin:
    """主窗口的「保存到哪个包」职责分组，不独立创建窗口。"""

    # -- 包内布局：记住输出包 ------------------------------------------
    def _is_source_pack_target(self, path: str) -> bool:
        """这次要写的，是不是当前文档的来源包（宽松模式原地写回）。

        只有宽松模式才成立：严格模式即便路径碰巧相同也不放开，
        原包仍然只读。
        """
        if not self._loose_mode():
            return False
        target = self._save_target_pack()
        if not target:
            return False
        try:
            return Path(path).resolve() == Path(target).resolve()
        except OSError:
            return False

    def _save_target_pack(self, doc=None) -> str | None:
        """这篇布局的 Ctrl+S 会写进哪个包。

        严格模式：上次的输出包（还没存过就是 None，由调用方去问）；
        宽松模式：**一律回原包**——对已经存过新包的文档也一样，
        用的是 ``origin_pack``，不是那个新包。

        注意 ``doc.source_pack[0]`` 在严格模式保存成功后会变成新包
        （见 ``_adopt_written_pack``），所以宽松模式不能顺手拿它。
        """
        doc = self.doc if doc is None else doc
        if doc is None or not doc.source_pack:
            return None
        if self._loose_mode() and doc.origin_pack:
            return str(doc.origin_pack)
        return str(doc.source_pack[0])

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

    def _pack_sources(self, *, for_pack_write: bool = False,
                      allow: str | Path | None = None) -> list[Path]:
        """受保护的源包：游戏原包、其它已挂载包、同目录里还没挂载的包。

        只有**写回资源包**（``for_pack_write=True``）时，当前文档自己写出来
        的输出包不算源——它是这次的保存目标；不排除的话，第二次 Ctrl+S 会被
        `guard_output` 当成「覆盖源资源」拒掉（实测）。**另存为散装 .dlg**
        时必须继续保护它：否则选中上次的输出包，`.fls` 会被整包写成 `.dlg`
        明文，包里几十万条资源一次丢光。

        ``allow``：这次明确要写的目标（宽松模式的原包、自己的输出包），
        只从保护名单里剔除它一个，其它源包照旧受保护。
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
        own = self._own_output_pack() if for_pack_write else None
        allowed = None
        if allow is not None:
            try:
                allowed = str(Path(allow).resolve())
            except OSError:
                allowed = str(allow)
        kept: list[Path] = []
        seen: set[str] = set()
        for path in sources:
            try:
                resolved = str(path.resolve())
            except OSError:
                resolved = str(path)
            if allowed is not None and resolved == allowed:
                continue
            if own is not None and resolved == str(own):
                continue
            if resolved in seen:
                continue
            seen.add(resolved)
            kept.append(path)
        return kept

