"""标签栏右键菜单：关闭当前 / 左侧 / 右侧 / 其他 / 全部。

只关标签（会话），不动布局文件；每个有未保存修改的标签单独确认。
从左往右数就是标签栏上看到的顺序，关的时候从右往左执行，下标不漂移。
"""

from __future__ import annotations

from PySide6.QtWidgets import QMenu

__all__ = ["TabMenuMixin"]


class TabMenuMixin:
    """主窗口标签菜单职责分组，不独立创建窗口。"""

    # -- 标签右键菜单（关闭当前/左侧/右侧/全部） ---------------------
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

    def _active_index(self) -> int:
        if self._active is None or self._active not in self._sessions:
            return -1
        return self._sessions.index(self._active)

    def _close_tab_range(self, start: int, stop: int) -> int:
        """关闭 [start, stop) 区间的标签，从右往左关（下标不漂移）。

        每个有未保存修改的标签都会单独确认；任意一个说「不」，只跳过
        那一个，其余照关。返回真正关掉的个数。
        """
        start = max(0, start)
        stop = min(len(self._sessions), stop)
        closed = skipped = 0
        for index in range(stop - 1, start - 1, -1):
            if index >= len(self._sessions):
                continue
            if not self._confirm_discard(self._sessions[index].doc):
                skipped += 1
                continue
            self._remove_session(index)
            closed += 1
        notes = []
        if closed:
            notes.append(f"已关闭 {closed} 个标签"
                         f"（剩 {len(self._sessions)} 个）")
        if skipped:
            notes.append(f"{skipped} 个有未保存修改，按你的选择跳过")
        if notes:
            self._update_status("；".join(notes))
        return closed

    def _close_tab_except(self, keep: int) -> int:
        """关闭除 keep 以外的所有标签。"""
        if not 0 <= keep < len(self._sessions):
            return 0
        closed = self._close_tab_range(keep + 1, len(self._sessions))
        closed += self._close_tab_range(0, keep)
        return closed
