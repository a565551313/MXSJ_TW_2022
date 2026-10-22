"""保存模式：严格（原包只读）与宽松（直接改写原包）。

用户要的是工具栏上一个「模式」下拉，两项：

* **严格模式**（默认，也是以前唯一的行为）：Ctrl+S 写编辑器自己的
  输出包，游戏原包一个字节都不动；第一次保存问一次输出包，之后静默写回。
* **宽松模式**：Ctrl+S 直接把改动写进布局**所在的资源包**，不生成新包。
  写前检查、写后逐条校验、临时副本 + 原子替换都照旧——宽松改的只是
  「写到哪儿」，不是「少校验」。但校验只能证明写得对，找不回被覆盖的内容，
  所以**切到宽松必须二次确认**，切回严格不拦。

模式记在 ``QSettings("save_mode")`` 里，重启后保持；启动时若读到宽松，
界面上常驻红字提示（工具栏按钮变红 + 状态栏一句话），不需要再确认一次
（确认只在「切换」这个动作上）。

本模块只负责**模式状态与界面**；真正换保存目标在
:mod:`ui_editor.ui.save_workflows` 与 :mod:`ui_editor.ui.import_queue`。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QMessageBox

from . import icons
from .toolbar_controls import build_mode_button

__all__ = ["LOOSE", "MODE_LABELS", "STRICT", "SaveModeMixin"]

STRICT = "strict"
LOOSE = "loose"
MODE_LABELS = {STRICT: "严格模式", LOOSE: "宽松模式"}

_LOOSE_TEXT = (
    "宽松模式下 Ctrl+S 会直接改写布局所在的资源包：\n"
    "· 不生成新包，也不自动留备份；\n"
    "· 覆盖之后编辑器里没有「撤销保存」；\n"
    "· 写前检查与写后逐条校验仍然执行，但它们只能证明写得对，"
    "找不回被覆盖的内容。\n\n"
    "建议先把原包复制一份再继续。\n\n"
    "确定切换到宽松模式吗？")

_STRICT_TEXT = (
    "已切回严格模式：Ctrl+S 写编辑器自己的输出包，原包只读。\n"
    "下次保存会重新问你输出包放在哪。")


class SaveModeMixin:
    """主窗口的「保存模式」职责分组，不独立创建窗口。"""

    # -- 状态 ---------------------------------------------------------
    def _init_save_mode(self) -> None:
        """从设置读模式（启动不弹确认，只把界面标红）。"""
        raw = str(self._settings.value("save_mode", STRICT) or STRICT)
        self._save_mode = raw if raw in MODE_LABELS else STRICT

    def save_mode(self) -> str:
        """:data:`STRICT` 或 :data:`LOOSE`。"""
        return getattr(self, "_save_mode", STRICT)

    def _loose_mode(self) -> bool:
        return self.save_mode() == LOOSE

    # -- 工具栏 -------------------------------------------------------
    def _build_mode_control(self, bar) -> None:
        self._mode_btn, self._mode_actions = build_mode_button(
            self, self.choose_save_mode)
        bar.addWidget(self._mode_btn)
        self._sync_save_mode_ui()

    def choose_save_mode(self, mode: str) -> None:
        """菜单点了某一项：切到宽松先二次确认，不确认就勾回原模式。"""
        if mode not in MODE_LABELS:
            return
        if mode == self.save_mode():
            self._sync_save_mode_ui()
            return
        if mode == LOOSE and not self._confirm_loose_mode():
            self._sync_save_mode_ui()
            return
        self._apply_save_mode(mode)

    def _confirm_loose_mode(self) -> bool:
        text = _LOOSE_TEXT
        doc = getattr(self, "doc", None)
        if doc is not None and doc.source_pack:
            # 说「会被改写的那个包」：严格模式保存过一次之后
            # source_pack[0] 已经是新包，而宽松模式写的是 origin。
            target = doc.origin_pack or doc.source_pack[0]
            text = (f"当前布局所在的包：\n{target}\n\n" + text)
        box = QMessageBox(
            QMessageBox.Icon.Warning, "切换到宽松模式（会直接改写原包）", text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            self)
        # 按钮说人话：默认焦点在「取消」，误按回车不会切到危险模式。
        box.button(QMessageBox.StandardButton.Yes).setText("切换到宽松模式")
        box.button(QMessageBox.StandardButton.No).setText("取消")
        box.setDefaultButton(QMessageBox.StandardButton.No)
        return box.exec() == QMessageBox.StandardButton.Yes

    def _apply_save_mode(self, mode: str) -> None:
        self._save_mode = mode
        self._settings.setValue("save_mode", mode)
        if mode == STRICT:
            # 宽松模式写过的文档，output_pack 指向的就是它自己的原包；
            # 切回严格必须把这个「目标」清掉，否则下一次 Ctrl+S 还会
            # 直接覆盖原包。清掉后第一次保存会重新问输出包。
            self._forget_in_place_outputs()
        self._sync_save_mode_ui()
        self._update_title()
        if mode == LOOSE:
            self._update_status(
                "已切到宽松模式：Ctrl+S 会直接改写布局所在的资源包（无备份）。")
        else:
            self._update_status(_STRICT_TEXT.replace("\n", ""))

    def _forget_in_place_outputs(self) -> None:
        """切回严格时，清掉「输出包就是原包」这一类目标。

        必须拿 **origin**（这篇布局真正来自哪个包）比，不能拿
        ``source_pack[0]``：严格模式保存成功后，``source_pack[0]`` 已经
        变成编辑器自己写的新包，拿它比会把合法的新包也当成本地写回，
        白白清掉，下一次保存又会问路径、默认名多出一个 ``_edited2``。
        """
        for doc in self._documents_for_mode():
            if not doc.output_pack or not doc.source_pack:
                continue
            origin = doc.origin_pack or doc.source_pack[0]
            try:
                same = Path(doc.output_pack).resolve() == Path(origin).resolve()
            except OSError:
                same = False
            if same:
                doc.output_pack = None

    def _documents_for_mode(self) -> list:
        """所有标签里的文档 + 当前文档 + 还排着队的待入布局（去重）。

        队列里的文档没有标签（只有第一个会打开），漏了它们的话，宽松
        模式里排进来的那些会带着「输出包＝原包」的旧值切回严格——之后
        打开一篇、按 Ctrl+S，就会在严格模式里直接改写原包。
        """
        docs: list = []
        for session in getattr(self, "_sessions", []):
            doc = getattr(session, "doc", None)
            if doc is not None and doc not in docs:
                docs.append(doc)
        current = getattr(self, "_doc", None)
        if current is not None and current not in docs:
            docs.append(current)
        for store in getattr(self, "_pending_imports", {}).values():
            for doc in store.values():
                if doc not in docs:
                    docs.append(doc)
        return docs

    def _sync_save_mode_ui(self) -> None:
        loose = self._loose_mode()
        actions = getattr(self, "_mode_actions", {})
        for mode, action in actions.items():
            action.setChecked(mode == self.save_mode())
        button = getattr(self, "_mode_btn", None)
        if button is not None:
            button.setIcon(icons.icon_mode(loose))
            button.setText("模式")
            button.setToolTip(
                ("宽松模式：Ctrl+S 直接写原包（无备份）；点小箭头切回严格模式"
                 if loose else
                 "严格模式：原包只读，Ctrl+S 写编辑器自己的输出包；"
                 "点小箭头可切到宽松模式")
                + "\n保存模式（缩写：模式）。")
            # 宽松是危险状态：按钮文字常驻红字，不用展开菜单才看得见。
            button.setStyleSheet(
                "color:#c0392b; font-weight:600;" if loose else "")
