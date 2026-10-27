"""Save mode: strict (a new package) versus loose (overwrite the original).

The UI editor has had this switch for a while; the script editor's equivalent
is:

* **strict** (default, and the only behaviour until now): ``F6`` compiles the
  bound module into a *new* ``.fls``; the original package stays byte-identical.
* **loose**: ``Ctrl+S`` compiles and writes the changes straight back into the
  package they belong to. Nothing else is skipped — the temporary package is
  still re-read and verified entry by entry, and the previous bytes are kept as
  ``<name>.fls.bak``. Loose mode changes *where* the bytes go, not *what* is
  checked.

Because an overwrite cannot be undone from inside the editor, switching to
loose asks once; switching back never asks. On top of that, a save that targets
a package inside an installed game client (detected by ``mx.exe`` /
``mxmain.dll`` next to it) asks again every time — see
:mod:`script_editor.core.services.client_install`.

The mode is remembered in ``QSettings("save_mode")`` and shown in red in the
toolbar while loose is active.
"""

from __future__ import annotations

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMessageBox, QToolButton

STRICT = "strict"
LOOSE = "loose"
MODE_LABELS = {STRICT: "严格模式", LOOSE: "宽松模式"}

_LOOSE_TEXT = (
    "宽松模式下 Ctrl+S 会直接改写这些源码所属的原包：\n"
    "· 不再生成新包，也不再询问输出文件名；\n"
    "· 覆盖前会把原包复制成 <包名>.fls.bak（只保留最近一份，会被下次覆盖）；\n"
    "· 写前校验、写后逐条回读校验照常执行，但它们只能证明写得对，\n"
    "  找不回被覆盖的内容；\n"
    "· 游戏正在运行的包可能写不进去（文件被占用），会明确报错且不改动原包。\n\n"
    "确定切换到宽松模式吗？"
)

_STRICT_TEXT = "已切回严格模式：F6 生成新包，原包不会被改写。"


class SaveModeMixin:
    """Mode state and its toolbar control; the write itself is LooseSaveMixin."""

    # -- state ---------------------------------------------------------
    def _init_save_mode(self) -> None:
        raw = ""
        if getattr(self, "settings", None) is not None:
            raw = str(self.settings.value("save_mode", STRICT) or STRICT)
        self._save_mode = raw if raw in MODE_LABELS else STRICT

    def save_mode(self) -> str:
        return getattr(self, "_save_mode", STRICT)

    def loose_mode(self) -> bool:
        return self.save_mode() == LOOSE

    def _remember_save_mode(self, mode: str) -> None:
        if getattr(self, "settings", None) is not None:
            self.settings.setValue("save_mode", mode)

    # -- toolbar -------------------------------------------------------
    def _build_mode_control(self, toolbar) -> None:
        button = QToolButton(self)
        button.setObjectName("saveModeButton")
        button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        menu = QMenu(button)
        self.mode_actions = {}
        for mode in (STRICT, LOOSE):
            action = QAction(MODE_LABELS[mode], self)
            action.setCheckable(True)
            action.triggered.connect(
                lambda _checked=False, target=mode: self.choose_save_mode(target)
            )
            menu.addAction(action)
            self.mode_actions[mode] = action
        button.setMenu(menu)
        button.clicked.connect(self.choose_save_mode)
        self.mode_button = button
        toolbar.addWidget(button)
        self._sync_save_mode_ui()

    def choose_save_mode(self, mode: str = STRICT) -> None:
        """Switch modes; a switch *into* loose needs one explicit confirmation."""
        # QToolButton.clicked passes a bool, which must not be read as a mode.
        if not isinstance(mode, str):
            mode = STRICT if self.loose_mode() else LOOSE
        if mode not in MODE_LABELS or mode == self.save_mode():
            self._sync_save_mode_ui()
            return
        if mode == LOOSE and not self.confirm_loose_mode():
            self._sync_save_mode_ui()
            return
        self._apply_save_mode(mode)

    def confirm_loose_mode(self) -> bool:
        box = QMessageBox(
            QMessageBox.Icon.Warning,
            "切换到宽松模式（会直接改写原包）",
            _LOOSE_TEXT,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            self,
        )
        box.button(QMessageBox.StandardButton.Yes).setText("切换到宽松模式")
        box.button(QMessageBox.StandardButton.No).setText("取消")
        box.setDefaultButton(QMessageBox.StandardButton.No)
        return box.exec() == QMessageBox.StandardButton.Yes

    def _apply_save_mode(self, mode: str) -> None:
        self._save_mode = mode
        self._remember_save_mode(mode)
        self._sync_save_mode_ui()
        self.statusBar().showMessage(
            "已切到宽松模式：Ctrl+S 直接把改动写回原包（覆盖前留 .fls.bak）。"
            if mode == LOOSE
            else _STRICT_TEXT,
            8000,
        )

    def _sync_save_mode_ui(self) -> None:
        loose = self.loose_mode()
        for mode, action in getattr(self, "mode_actions", {}).items():
            action.setChecked(mode == self.save_mode())
        button = getattr(self, "mode_button", None)
        if button is None:
            return
        button.setText("宽松" if loose else "严格")
        button.setToolTip(
            (
                "宽松模式：Ctrl+S 直接写回原包（覆盖前留 .fls.bak）；"
                "点小箭头切回严格模式"
                if loose
                else "严格模式：F6 生成新包，原包不改写；点小箭头可切到宽松模式"
            )
            + "\n保存模式：严格=新包，宽松=写原包。"
        )
        # Loose is the dangerous state, so it stays visibly red without opening
        # the menu.
        button.setStyleSheet(
            "QToolButton { color:#c0392b; font-weight:600; }" if loose else ""
        )
