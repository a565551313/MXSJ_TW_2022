"""替换布局：用选中的 ``.dlg`` 内容顶掉现有布局，名字与路径不变。

「替换」= 目标布局的身份不动（资源包里还是 ``a.dlg``、散装还是那个
文件），但里面的控件全换成你选的那个 ``.dlg`` 的内容。典型用法：
从别的服/别人的包里拷一个 ``a.dlg`` 进来，盖掉当前的这个。

落盘走两条既有安全路径，都不会偷偷改原包：
* 包内布局 → 走和「导入布局」同一套预检（相对 GBK 路径、结构、编码），
  标记为「待入新包」，按工具栏「存包」生成新包才算落盘，原 ``.fls``
  一个字节都不动；
* 散装 ``.dlg`` → 标记为未保存，按「保存」写回原路径（仍受
  「不自动建缺失父文件夹」「非法资源名要拦截」等既有规则约束）。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox

from ..core import dlg_codec
from ..core.layout_import import prepare_layout_import
from ..core.model import LayoutDocument
from ..core.pack import FlsPack

__all__ = ["ReplaceLayoutMixin"]


class ReplaceLayoutMixin:
    """主窗口的「替换布局」职责分组，不独立创建窗口。"""

    # -- 入口 ---------------------------------------------------------
    def replace_layout_dialog(self, data: tuple) -> None:
        """资源树右键「替换布局…」：先选内容来源，再交给 replace_layout_with。"""
        target = self._replace_target(data)
        if target is None:
            return
        name, _hint = target
        last_dir = self._settings.value("last_dir", "")
        path, _ = QFileDialog.getOpenFileName(
            self, f"选择用来替换 {name} 的布局文件", last_dir,
            "布局文件 (*.dlg);;所有文件 (*)")
        if not path:
            return
        self._settings.setValue("last_dir", str(Path(path).parent))
        self.replace_layout_with(data, path)

    @staticmethod
    def _replace_target(data: tuple) -> tuple[str, str] | None:
        """返回 (给人看的名字, 身份说明)；不认识的节点返回 None。"""
        if not data:
            return None
        if data[0] == "pack":
            return data[2], f"包内路径 {data[2]} 保持不变"
        if data[0] == "file":
            return Path(data[1]).name, "散装文件路径保持不变"
        return None

    # -- 主流程 -------------------------------------------------------
    def replace_layout_with(self, data: tuple, source_path: str) -> bool:
        """用 source_path 的内容替换 data 指向的布局（保留目标身份）。

        成功返回 True；读不了、编码不合法、来源与目标同一个文件、或用户
        在「丢弃原标签未保存修改」时选了「不」，返回 False 且目标不动。
        """
        target = self._replace_target(data)
        if target is None:
            return False
        name, hint = target
        source = Path(source_path)
        if data[0] == "file" and source.resolve() == Path(data[1]).resolve():
            QMessageBox.warning(
                self, "替换布局",
                "所选文件就是这个布局本身，替换不会产生任何变化。")
            return False
        try:
            raw = source.read_bytes()
        except OSError as exc:
            QMessageBox.warning(
                self, "替换失败",
                f"读不了 {source}，目标布局未改动。\n{exc}")
            return False
        prepared = self._build_replace_document(data, raw)
        if prepared is None:
            return False
        doc, key, save_hint = prepared
        index = self._session_index(key)
        if index >= 0:
            old = self._sessions[index].doc
            if old is not None and not self._confirm_discard(old):
                return False
            self._activate_session(index)
            self._set_document(doc)
        else:
            self._open_in_tab(doc, key)
        if doc.pending_pack_import and doc.source_pack is not None:
            # _set_document 只清旧标记、不重挂；换进来的文档仍是「待入新包」，
            # 资源树要立刻显示它，并定位到那个待入包叶子。
            self.resource_panel.show_pending(*doc.source_pack)
            self.resource_panel.reveal_selection(("pending", *doc.source_pack))
        else:
            self.resource_panel.reveal_selection(key)
        count = len(doc.all_widgets())
        self._update_status(
            f"已用 {source.name} 的内容替换 {name}：{count} 个控件；"
            f"{hint}；{save_hint}")
        return True

    def _build_replace_document(self, data: tuple, raw: bytes):
        """按目标身份解析来源字节，返回 (文档, 会话键, 落盘提示)。"""
        if data[0] == "pack":
            pack_path, res_path = data[1], data[2]
            try:
                with FlsPack(Path(pack_path)) as pack:
                    doc, _replacing = prepare_layout_import(
                        pack, res_path, raw,
                        text_encoding=self.resolver.text_encoding)
            except Exception as exc:
                QMessageBox.warning(
                    self, "替换失败",
                    f"不能用这个文件替换 {res_path}，目标布局未改动。\n{exc}")
                return None
            doc.source_pack = (pack_path, res_path)
            doc.source_path = None
            return (doc, ("pack", pack_path, res_path),
                    "原包未修改，按「存包」生成新包才落盘")
        if data[0] == "file":
            target = Path(data[1])
            try:
                dicts, md5 = dlg_codec.parse_bytes(
                    raw, text_encoding=self.resolver.text_encoding)
            except Exception as exc:
                QMessageBox.warning(
                    self, "替换失败",
                    f"解析失败，{target.name} 未改动。\n{exc}")
                return None
            doc = LayoutDocument.from_native_dicts(dicts, md5)
            doc.source_bytes = raw
            doc.text_encoding = self.resolver.text_encoding
            doc.source_path = str(target)
            doc.source_pack = None
            doc.begin_inplace_replace(self._read_target_dicts(target))
            return doc, ("file", str(target)), "按「保存」写回这个文件"
        return None

    def _read_target_dicts(self, target: Path) -> list[dict]:
        """替换前的磁盘内容，用作「改了哪些」的对照基线。"""
        if not target.is_file():
            return []
        try:
            dicts, md5 = dlg_codec.parse_bytes(
                target.read_bytes(),
                text_encoding=self.resolver.text_encoding)
            return LayoutDocument.from_native_dicts(dicts, md5).to_dicts()
        except Exception:
            return []  # 原文件都读不出来就当空基线，仍然允许替换
