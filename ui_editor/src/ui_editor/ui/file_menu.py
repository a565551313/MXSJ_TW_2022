"""文件菜单与工具栏上「打开 / 保存 / 另存为 / 导出副本」的搭建。

为什么单独一个模块：

* 这几项的名字被反复改（菜单名、工具栏短字、测试断言三处要一致），
  集中在一处才不容易又对不上；
* `window_setup.py` 有「每模块 ≤ 600 行」的结构护栏，菜单正文挪出来
  之后它才装得下视图/编辑/帮助菜单。

命名口径（0.14.0 起，旧名对照见 README）：

* **打开** —— 只问「从哪来」：布局文件 / 布局目录 / 资源包 / 资源目录；
  选包或目录只是挂到左边树，双击才出标签页。
* **保存** —— 只问「回哪去」：回到它来的地方（散装覆盖原文件、
  包内布局写回上次那个新包）。
* **另存为** —— 换地方：新资源包 / 散装布局。
* **导出副本** —— 拿一份，不动原文件：布局原文件 / 画布 PNG / 控件素材。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenu, QMessageBox, QToolButton

from .. import __version__

__all__ = [
    "add_action",
    "build_file_menu",
    "rebuild_recent_menu",
    "show_about",
    "split_button",
]


def add_action(menu, text, slot, shortcut=None, tooltip: str = "") -> QAction:
    """往菜单里加一项并返回 QAction（工具栏与菜单共用同一个对象）。"""
    action = QAction(text, menu)
    if shortcut is not None:
        action.setShortcut(shortcut)
    if tooltip:
        action.setToolTip(tooltip)
    action.triggered.connect(slot)
    menu.addAction(action)
    return action


def build_file_menu(host, file_menu: QMenu) -> None:
    """把整个「文件」菜单挂到 ``host``（主窗口）上。

    动作对象都存回 ``host._act_*``：工具栏、测试、状态同步都按名字取，
    换布局不用跟着改调用点。
    """
    # 子菜单留个名字挂到 host 上（和下面 `_recent_menu` 同一种做法），
    # 测试按名字取比 `action.menu()` 稳。
    host._file_menu = file_menu
    open_menu = file_menu.addMenu("打开")
    host._open_menu = open_menu
    open_menu.setToolTip("从哪读：布局文件、布局目录、资源包、资源目录")
    host._act_open_file = add_action(
        open_menu, "布局文件（.dlg）…", host.open_layout_file_dialog,
        QKeySequence.StandardKey.Open,
        "打开一个散装 .dlg，直接出标签页")
    host._act_open_dir = add_action(
        open_menu, "布局目录（一个文件夹里的 .dlg）…",
        host.open_layout_dir_dialog, None,
        "把一个装着 .dlg 的文件夹挂到左边树；双击其中的布局打开")
    open_menu.addSeparator()
    host._act_open_pack = add_action(
        open_menu, "资源包（.fls，先挂到左边树）…", host.open_from_pack,
        None, "挂载资源包；挂上之后在左边树里双击要改的布局")
    host._act_open_res_dir = add_action(
        open_menu, "资源目录（整个客户端目录）…",
        host.open_resource_dir_dialog, None,
        "把目录下所有 .fls 都挂上，并逐包列出布局")
    open_menu.addSeparator()
    host._recent_menu = open_menu.addMenu("最近打开")
    host._recent_menu.aboutToShow.connect(lambda: rebuild_recent_menu(host))
    rebuild_recent_menu(host)

    host._act_reload = add_action(
        file_menu, "重新读取（从来源，丢弃未保存改动）", host.refresh_sources,
        QKeySequence("F5"), "从磁盘重新加载布局、目录与资源（F5）")
    host._act_reload.setIcon(host.style().standardIcon(
        host.style().StandardPixmap.SP_BrowserReload))
    host._act_reload.setIconText("刷新")
    file_menu.addSeparator()
    add_action(file_menu, "新建布局", host.new_layout,
               QKeySequence.StandardKey.New)
    file_menu.addSeparator()
    host._act_save = add_action(
        file_menu, "保存（回到它来的地方）", host.save,
        QKeySequence.StandardKey.Save,
        "散装 .dlg 覆盖原文件；包内布局写回上次那个新包"
        "（第一次会让你选输出包）")
    save_as_menu = file_menu.addMenu("另存为")
    host._save_as_menu = save_as_menu
    host._act_save_pack = add_action(
        save_as_menu, "新资源包（.fls）…", host.save_to_pack_dialog, None,
        "把当前布局写进另一个新包（原包不动，之后 Ctrl+S 写这里）")
    host._act_save_as_dlg = add_action(
        save_as_menu, "散装布局（.dlg）…", lambda: host.save_as(), None,
        "存成独立的 .dlg 文件，脱离资源包")
    file_menu.addSeparator()
    export_menu = file_menu.addMenu("导出副本")
    host._export_menu = export_menu
    export_menu.setToolTip("都是「另拿一份」，不影响原文件与保存目标")
    host._act_export_layout = add_action(
        export_menu, "布局原文件（.dlg 原字节）…",
        host.export_current_layout_source, None,
        "导出这篇布局的来源原文：不含未保存编辑、不转换编码")
    host._act_export_png = add_action(
        export_menu, "画布预览图（PNG）…", host.export_png, None,
        "把当前画布截一张 PNG")
    host._act_export_assets = add_action(
        export_menu, "控件素材图片…", host.export_layout_assets, None,
        "把这篇布局引用到的图片/音效各导一份到文件夹（原格式）")
    file_menu.addSeparator()
    add_action(file_menu, "退出", host.close,
               QKeySequence.StandardKey.Quit)


def rebuild_recent_menu(host) -> None:
    """「最近打开」每次弹出前重建（文件可能已被删或改名）。"""
    menu = getattr(host, "_recent_menu", None)
    if menu is None:
        return
    menu.clear()
    entries = host._recent_entries()
    if not entries:
        empty = menu.addAction("（还没有记录）")
        empty.setEnabled(False)
        return
    labels = {"dlg": "布局", "dlgdir": "布局目录",
              "pack": "资源包", "resdir": "资源目录"}
    # 不同目录里可能有同名文件：光写文件名会出现好几行一模一样的
    # 「布局：a.dlg」，用户没法挑。同名时补上父目录名。
    counts: dict[str, int] = {}
    for _kind, path in entries:
        name = Path(path).name or path
        counts[name] = counts.get(name, 0) + 1
    for kind, path in entries:
        name = Path(path).name or path
        if counts.get(name, 0) > 1:
            parent = Path(path).parent.name
            if parent:
                name = f"{name}（{parent}）"
        act = menu.addAction(f"{labels.get(kind, kind)}：{name}")
        act.setToolTip(path)
        act.triggered.connect(
            lambda _checked=False, k=kind, p=path: host.open_recent(k, p))
    menu.addSeparator()
    clear = menu.addAction("清空这个列表")
    clear.triggered.connect(host.clear_recent)


def split_button(bar, text: str, icon, actions, default_slot,
                 tip: str = "") -> QToolButton:
    """工具栏「主按钮 + 小箭头」：点按钮＝最常用那个，点箭头选其它。

    主按钮不挂 QAction（挂了就显示菜单项的长标题），只发 clicked；
    ``actions`` 里的 QAction 与菜单共用，启用状态天然同步。
    """
    btn = QToolButton(bar)
    btn.setText(text)
    btn.setIcon(icon)
    btn.setIconSize(QSize(26, 26))
    btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
    btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
    if tip:
        btn.setToolTip(tip)
    menu = QMenu(btn)
    for action in actions:
        if action is None:
            menu.addSeparator()
        else:
            menu.addAction(action)
    btn.setMenu(menu)
    btn.clicked.connect(default_slot)
    return btn


def show_about(host) -> None:
    QMessageBox.about(
        host, "关于 MXSJ UI 编辑器",
        f"MXSJ UI 编辑器 {__version__}\n\n"
        "可视化编辑客户端 UI 布局（.dlg）：打开现有布局改、"
        "或从空白新建。\n布局格式、路径哈希与解密均来自本仓库"
        "逆向结案成果。")
