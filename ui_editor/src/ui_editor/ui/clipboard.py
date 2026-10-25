"""主窗口的剪贴板命令（Qt 界面层 mixin，0.17.0 自 commands.py 拆出）。

复制 / 剪切 / 粘贴与「焦点在文本框时三键作用于文本」的守卫集中在这里；
删除护栏、右键菜单与引用检查仍留在 ``commands.py``。剪切＝进剪贴板＋
走删除护栏（整组一步撤销），确认取消时剪贴板留副本、文档不动。
"""

from __future__ import annotations

from PySide6.QtCore import QMimeData
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QPlainTextEdit,
    QTextEdit,
)

from ..core.model import Widget


class ClipboardMixin:
    """依赖宿主窗口状态的剪贴板命令；不接管 QObject 初始化。"""

    _MIME_WIDGETS = "application/x-mxsj-widget+json"

    def _focused_text_editor(self):
        """焦点在文本输入里时，复制/粘贴/删除应作用于文本而非控件。"""
        fw = QApplication.focusWidget()
        if isinstance(fw, (QLineEdit, QTextEdit, QPlainTextEdit)):
            return fw
        return None

    def _edit_copy(self) -> None:
        fw = self._focused_text_editor()
        if fw is not None:
            fw.copy()
            return
        self.copy_selected_widgets()

    def _edit_paste(self) -> None:
        fw = self._focused_text_editor()
        if fw is not None:
            fw.paste()
            return
        self.paste_widgets()

    def _edit_cut(self) -> None:
        fw = self._focused_text_editor()
        if fw is not None:
            fw.cut()
            return
        self.cut_selected_widgets()

    def cut_selected_widgets(self) -> None:
        """剪切 = 进剪贴板 + 走删除护栏；整组算一步撤销（删除那步）。

        确认框里取消的话剪贴板会留下副本（与多数编辑器一致：
        复制动作已发生），文档不动。
        """
        widgets = self._selected_widgets()
        if not widgets or self.doc is None:
            return
        self._copy_to_clipboard(widgets)
        deleted = self.delete_selected(verb="剪切")
        if deleted:
            self._update_status(
                f"已剪切 {deleted} 个控件（Ctrl+V 可粘贴；Ctrl+Z 撤销）")

    def _copy_to_clipboard(self, widgets: list) -> None:
        """把给定控件（含子树）序列化进系统剪贴板（不发状态栏）。"""
        import json

        payload = json.dumps([w.to_dict() for w in widgets],
                             ensure_ascii=False).encode("utf-8")
        mime = QMimeData()
        mime.setData(self._MIME_WIDGETS, payload)
        mime.setText(payload.decode("utf-8"))
        QGuiApplication.clipboard().setMimeData(mime)
        self._sync_edit_actions()

    def copy_selected_widgets(self) -> None:
        """把选中的控件（含子树）序列化进系统剪贴板。"""
        widgets = self._selected_widgets()
        if not widgets:
            return
        self._copy_to_clipboard(widgets)
        self._update_status(f"已复制 {len(widgets)} 个控件")

    def _clipboard_payload(self) -> list[dict] | None:
        """读剪贴板中的控件负载（本工具复制的），无效返回 None。"""
        import json

        clipboard = QGuiApplication.clipboard()
        mime = clipboard.mimeData()
        raw = None
        if mime is not None and mime.hasFormat(self._MIME_WIDGETS):
            raw = bytes(mime.data(self._MIME_WIDGETS))
        elif mime is not None and mime.hasText():
            raw = mime.text().encode("utf-8")
        if not raw:
            return None
        try:
            data = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None
        if (not isinstance(data, list) or not data
                or not all(isinstance(d, dict) for d in data)):
            return None
        return data

    def paste_widgets(self) -> None:
        """把剪贴板控件粘进文档：作为当前选中控件的同级（无选择挂顶层）。

        位置统一偏移 (16,16) 免与原件重叠；整组粘贴算一步撤销。
        名字：与文档里已有控件重名时自动加后缀（``BTN`` → ``BTN_1``、
        再粘 → ``BTN_2``；``BTN_1`` 复制后粘贴 → ``BTN_1_1``），子树里的
        重名子控件同样处理；不重名则保持原名。这样副本不会顶掉脚本对
        原控件的 sName 认领，也不会在诊断里变成重复名。
        """
        if self.doc is None:
            return
        payload = self._clipboard_payload()
        if not payload:
            return
        clones = [Widget.from_dict(d) for d in payload]
        selection = self._selected_widgets()
        anchor = selection[0] if selection else None
        parent = anchor.parent if anchor is not None else None
        siblings = (parent.children if parent is not None
                    else self.doc.roots)
        index = (siblings.index(anchor) + 1 if anchor is not None
                 else None)
        used = {w.name for w in self.doc.all_widgets()}
        renamed = self.doc.rename_copies(clones, used)
        for clone in clones:
            clone.set_geometry(x=clone.x + 16, y=clone.y + 16)
            self.doc.insert_widget(clone, parent,
                                   None if index is None else index)
            if index is not None:
                index += 1
        self.doc.checkpoint()
        self._refresh_structure()
        self._select_widget(clones[0])
        self._update_title()
        note = (f"（{renamed} 个重名的已自动改名）" if renamed else "")
        self._update_status(
            f"已粘贴 {len(clones)} 个控件{note}："
            f"首个为「{clones[0].name or '(未命名)'}」")

