"""Tray uses the exact QAction instances used by the menu and toolbar."""

from __future__ import annotations

from PySide6.QtWidgets import QMenu, QSystemTrayIcon


def make_tray(window):
    tray = QSystemTrayIcon(window.windowIcon(), window)
    menu = QMenu(window)
    menu.addAction("显示主窗口", window.restore_window)
    menu.addSeparator()
    for kind, title in [("public", "公开服务"), ("admin", "Web 后台")]:
        submenu = menu.addMenu(title)
        for action in ("start", "pause", "restart", "stop"):
            submenu.addAction(window.actions[f"{kind}.{action}"])
    menu.addSeparator()
    menu.addAction("打开公开访问地址", lambda: window.open_url("public"))
    menu.addAction("打开后台登录页", lambda: window.open_url("admin"))
    menu.addSeparator()
    menu.addAction(window.actions["settings"])
    menu.addAction(window.actions["help"])
    menu.addSeparator()
    menu.addAction("退出…", window.close)
    tray.setContextMenu(menu)
    tray.activated.connect(
        lambda reason: (
            window.restore_window()
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick
            else None
        )
    )
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray.show()
    return tray
