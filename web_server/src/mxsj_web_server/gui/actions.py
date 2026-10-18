"""One action registry for menus, exact-order toolbar and tray."""

from __future__ import annotations

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QLabel, QStyle


def create_actions(window):
    actions = {}
    icons = {
        "start": QStyle.StandardPixmap.SP_MediaPlay,
        "pause": QStyle.StandardPixmap.SP_MediaPause,
        "restart": QStyle.StandardPixmap.SP_BrowserReload,
        "stop": QStyle.StandardPixmap.SP_MediaStop,
    }
    for kind, title in [("public", "公开服务"), ("admin", "Web 后台")]:
        for operation, label in [
            ("start", "启动"),
            ("pause", "暂停"),
            ("restart", "重启"),
            ("stop", "停止"),
        ]:
            action = QAction(
                window.style().standardIcon(icons[operation]), label, window
            )
            action.setToolTip(title + "：" + label)
            action.triggered.connect(
                lambda checked=False, k=kind, op=operation: window.service_action(k, op)
            )
            actions[f"{kind}.{operation}"] = action
    for name, title, callback in [
        ("validate", "校验", window.validate_content),
        ("preview", "预览", window.preview_content),
        ("help", "帮助", window.help_dialog),
        ("settings", "设置", lambda: window.navigate(5)),
        ("save", "保存草稿", window.save_content),
        ("reload", "重新加载", window.reload_editors),
        ("build", "生成版本", window.build_release),
        ("activate", "发布／回退", window.activate_release),
        ("import", "导入内容…", window.import_content),
        ("export", "导出草稿…", window.export_content),
    ]:
        action = QAction(title, window)
        action.triggered.connect(callback)
        actions[name] = action
    actions["save"].setShortcut(QKeySequence.StandardKey.Save)
    window.actions = actions
    toolbar = window.addToolBar("主工具栏")
    toolbar.setObjectName("mainToolbar")
    for kind in ("public", "admin"):
        if kind == "admin":
            toolbar.addSeparator()
            toolbar.addAction(actions["validate"])
            toolbar.addAction(actions["preview"])
            toolbar.addSeparator()
        toolbar.addWidget(QLabel("公开服务 " if kind == "public" else "Web 后台 "))
        for operation in ("start", "pause", "restart", "stop"):
            toolbar.addAction(actions[f"{kind}.{operation}"])
    toolbar.addSeparator()
    toolbar.addAction(actions["help"])
    toolbar.addAction(actions["settings"])
    from PySide6.QtCore import Qt

    toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
    file_menu = window.menuBar().addMenu("文件")
    for name in ("reload", "save", "import", "export"):
        file_menu.addAction(actions[name])
    file_menu.addAction("退出…", window.close)
    edit = window.menuBar().addMenu("编辑")
    for title, method, shortcut in [
        ("撤销", "undo", QKeySequence.StandardKey.Undo),
        ("重做", "redo", QKeySequence.StandardKey.Redo),
        ("剪切", "cut", QKeySequence.StandardKey.Cut),
        ("复制", "copy", QKeySequence.StandardKey.Copy),
        ("粘贴", "paste", QKeySequence.StandardKey.Paste),
    ]:
        action = edit.addAction(title, lambda m=method: window.edit_action(m))
        action.setShortcut(shortcut)
    content = window.menuBar().addMenu("内容")
    for title, index in [("新闻公告", 1), ("客服公告", 2), ("区服列表", 3)]:
        content.addAction(title, lambda i=index: window.navigate(i))
    content.addAction(actions["validate"])
    content.addAction(actions["preview"])
    publish = window.menuBar().addMenu("发布")
    publish.addAction(actions["build"])
    publish.addAction("查看差异", window.inspect_release)
    publish.addAction(actions["activate"])
    services = window.menuBar().addMenu("服务")
    for kind, title in [("public", "公开服务"), ("admin", "Web 后台")]:
        submenu = services.addMenu(title)
        for operation in ("start", "pause", "restart", "stop"):
            submenu.addAction(actions[f"{kind}.{operation}"])
    services.addAction("设置／重置管理员密码…", window.reset_password)
    services.addAction(actions["settings"])
    view = window.menuBar().addMenu("视图")
    view.addAction(toolbar.toggleViewAction())
    status = view.addAction("显示状态栏")
    status.setCheckable(True)
    status.setChecked(True)
    status.toggled.connect(window.statusBar().setVisible)
    view.addAction("日志", lambda: window.navigate(6))
    view.addAction(
        "恢复默认布局",
        lambda: (toolbar.show(), window.statusBar().show(), status.setChecked(True)),
    )
    help_menu = window.menuBar().addMenu("帮助")
    help_menu.addAction(actions["help"])
    help_menu.addAction("打开日志目录", window.open_log_directory)
