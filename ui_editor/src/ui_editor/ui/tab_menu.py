"""标签栏右键菜单：锁定 / 关闭当前 / 左侧 / 右侧 / 其他 / 全部。

只关标签（会话），不动布局文件；每个有未保存修改的标签单独确认。
从左往右数就是标签栏上看到的顺序，关的时候从右往左执行，下标不漂移。

锁定是标签会话自己的状态（``EditorSession.locked``）：锁上以后批量
关闭一律跳过它，状态栏会说明跳过了几个；单个「关闭当前标签」和标签
上的 ✕ 仍然能关。锁定不进布局文件、不影响保存与撤销。
"""

from __future__ import annotations

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu

from . import icons

__all__ = ["TabMenuMixin"]

_LOCK_HINT = "已锁定：批量关闭（左/右/其他/全部）会跳过它；可以单独关闭。"


class TabMenuMixin:
    """主窗口标签菜单职责分组，不独立创建窗口。"""

    # -- 标签右键菜单（锁定/关闭当前/左侧/右侧/全部） -------------------
    def _setup_tab_context_menu(self) -> None:
        """标签栏右键菜单：只关标签，不动布局文件。"""
        from PySide6.QtCore import Qt as _Qt

        self._tab_bar.setContextMenuPolicy(
            _Qt.ContextMenuPolicy.CustomContextMenu)
        self._tab_bar.customContextMenuRequested.connect(
            self._show_tab_context_menu)

    def build_tab_context_menu(self, index: int) -> QMenu:
        """标签右键菜单（不在此处 exec，便于测试）。"""
        menu = QMenu(self)
        total = len(self._sessions)
        has_tab = 0 <= index < total
        current = (self._tab_bar.currentIndex() if has_tab
                   else (self._active_index() if total else -1))
        target = index if has_tab else current
        locked = has_tab and bool(self._sessions[target].locked)
        lock = menu.addAction("解锁标签" if locked else "锁定标签")
        lock.setEnabled(has_tab)
        lock.setToolTip("锁定后批量关闭会跳过这个标签；单独关闭仍然可以")
        lock.triggered.connect(
            lambda _checked=False: self._set_tab_locked(target, not locked))
        menu.addSeparator()
        close_this = menu.addAction("关闭当前标签")
        close_this.setEnabled(has_tab or total > 0)
        close_this.triggered.connect(
            lambda _checked=False: self._close_tab(target))
        menu.addSeparator()
        left = menu.addAction("关闭左侧全部标签")
        left.setEnabled(target > 0)
        left.triggered.connect(
            lambda _checked=False: self._close_tab_range(0, target))
        right = menu.addAction("关闭右侧全部标签")
        right.setEnabled(0 <= target < total - 1)
        right.triggered.connect(
            lambda _checked=False: self._close_tab_range(target + 1, total))
        menu.addSeparator()
        others = menu.addAction("关闭其他标签")
        others.setEnabled(total > 1)
        others.triggered.connect(
            lambda _checked=False: self._close_tab_except(target))
        all_tabs = menu.addAction("关闭全部标签")
        all_tabs.setEnabled(total > 0)
        all_tabs.triggered.connect(
            lambda _checked=False: self._close_tab_range(0, total))
        return menu

    def _show_tab_context_menu(self, pos) -> None:
        if not self._sessions:
            return
        index = self._tab_bar.tabAt(pos)
        # 右键先切到那个标签：菜单里的「当前标签」就是眼前这一个，
        # 左边/右边也按看到的顺序算。
        if 0 <= index < len(self._sessions) and index != self._tab_bar.currentIndex():
            self._activate_session(index)
        self._exec_tab_menu(self.build_tab_context_menu(index),
                            self._tab_bar.mapToGlobal(pos))

    def _exec_tab_menu(self, menu: QMenu, global_pos) -> None:
        """真正弹出菜单（单独一层，测试可替换，避免阻塞在模态循环里）。"""
        menu.exec(global_pos)

    # -- 锁定 ---------------------------------------------------------
    def _set_tab_locked(self, index: int, locked: bool) -> None:
        """锁定/解锁一个标签，并同步标签上的锁图标与提示。"""
        if not 0 <= index < len(self._sessions):
            return
        session = self._sessions[index]
        session.locked = bool(locked)
        self._refresh_tab_marks()
        name = session.doc.display_name if session.doc else session.label()
        self._update_status(
            f"已锁定标签「{name}」：批量关闭会跳过它，可单独关闭。"
            if locked else f"已解锁标签「{name}」。")

    def _refresh_tab_marks(self) -> None:
        """把每个标签的锁图标/提示刷成与 ``session.locked`` 一致。"""
        lock_icon = icons.icon_lock()
        for i, session in enumerate(self._sessions):
            self._tab_bar.setTabIcon(
                i, lock_icon if session.locked else QIcon())
            self._tab_bar.setTabToolTip(
                i, _LOCK_HINT if session.locked else "")

    def _active_index(self) -> int:
        if self._active is None or self._active not in self._sessions:
            return -1
        return self._sessions.index(self._active)

    # -- 批量关闭（跳过锁定） ------------------------------------------
    def _close_tab_range(self, start: int, stop: int) -> int:
        """关闭 [start, stop) 区间的标签，从右往左关（下标不漂移）。

        锁定的标签不参与批量关闭，只跳过、不算失败；每个有未保存修改的
        标签都会单独确认，任意一个说「不」也只跳过那一个。返回真正关掉
        的个数。
        """
        counts = self._close_range(start, stop)
        self._report_batch_close(*counts)
        return counts[0]

    def _close_range(self, start: int, stop: int) -> tuple[int, int, int]:
        """关区间，返回 (关掉, 因未保存跳过, 因锁定跳过)；不报状态栏。"""
        start = max(0, start)
        stop = min(len(self._sessions), stop)
        closed = skipped = locked = 0
        for index in range(stop - 1, start - 1, -1):
            if index >= len(self._sessions):
                continue
            if self._sessions[index].locked:
                locked += 1
                continue
            if not self._confirm_discard(self._sessions[index].doc):
                skipped += 1
                continue
            self._remove_session(index)
            closed += 1
        return closed, skipped, locked

    def _report_batch_close(self, closed: int, skipped: int,
                            locked: int) -> None:
        notes = []
        if closed:
            notes.append(f"已关闭 {closed} 个标签"
                         f"（剩 {len(self._sessions)} 个）")
        if locked:
            notes.append(f"{locked} 个已锁定，未关闭")
        if skipped:
            notes.append(f"{skipped} 个有未保存修改，按你的选择跳过")
        if notes:
            self._update_status("；".join(notes))
        self._refresh_tab_marks()

    def _close_tab_except(self, keep: int) -> int:
        """关闭除 keep 以外的所有标签（锁定的一并跳过）。"""
        if not 0 <= keep < len(self._sessions):
            return 0
        # 先关右段再关左段：每段内部都重新取长度，下标不会漂移。
        parts = (self._close_range(keep + 1, len(self._sessions)),
                 self._close_range(0, keep))
        total = tuple(sum(part[i] for part in parts) for i in range(3))
        self._report_batch_close(*total)
        return total[0]
