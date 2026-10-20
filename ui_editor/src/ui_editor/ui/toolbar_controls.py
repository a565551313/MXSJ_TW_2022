"""工具栏上的两个「下拉按钮」：文本编码与预览帧。

和「对齐」「按钮态」同一套外观：``ToolButtonTextUnderIcon`` +
``InstantPopup``，按钮文字两三个字（编码 / 帧），点小箭头才展开。

* 编码：菜单里三个可勾选项（Big5（繁体）/ GBK（简体）/ UTF-8），
  勾上的就是当前正用来读布局文本的那个；切换走
  :meth:`ui_editor.ui.source_actions.SourceActionsMixin.change_text_encoding`。
* 帧：菜单里不是条目，而是一块横向滑块（``QWidgetAction`` 装一个
  QWidget），拖到哪帧就预览哪帧，上面一行「预览帧 3 / 7」实时显示。
  范围由当前布局里的 ``.spr`` 帧数决定（见
  ``WindowSetupMixin._refresh_animation_frame_control``）。
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QLabel,
    QMenu,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from . import icons

__all__ = [
    "ENCODING_CHOICES",
    "build_encoding_button",
    "build_frame_button",
]

# (菜单文案, 编码值)；顺序就是菜单顺序，第一项为默认。
ENCODING_CHOICES = (
    ("Big5（繁体）", "big5"),
    ("GBK（简体）", "gbk"),
    ("UTF-8", "utf-8"),
)

_ENCODING_TIP = (
    "布局文本编码（缩写：编码）。切换会按所选编码重新读取布局文本；\n"
    "资源路径仍为 GBK，不自动保存或简繁转换。")
_FRAME_TIP = (
    "动画预览帧（缩写：帧）：点小箭头拖横向滑块选帧；\n"
    "只影响画布预览，不修改布局或资源。")


def _dropdown(host, text: str, icon, tip: str) -> QToolButton:
    """工具栏下拉按钮的统一外观，与「对齐」「按钮态」一致。"""
    button = QToolButton(host)
    button.setText(text)
    button.setIcon(icon)
    button.setToolTip(tip)
    button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
    button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
    return button


def build_encoding_button(host, on_choose) -> tuple[QToolButton, dict[str, QAction]]:
    """「编码」下拉按钮；返回 (按钮, {编码: QAction})。"""
    button = _dropdown(host, "编码", icons.icon_encoding(), _ENCODING_TIP)
    button.setObjectName("layoutTextEncoding")
    menu = QMenu(button)
    actions: dict[str, QAction] = {}
    for label, codec in ENCODING_CHOICES:
        action = menu.addAction(label)
        action.setCheckable(True)
        action.setChecked(codec == "big5")
        action.setToolTip(f"按 {label} 重新读取布局文本")
        action.triggered.connect(
            lambda _checked=False, codec=codec: on_choose(codec))
        actions[codec] = action
    button.setMenu(menu)
    return button, actions


def build_frame_button(host, on_change) -> tuple[QToolButton, QSlider, QLabel]:
    """「帧」下拉按钮：小箭头下面是横向滑块，返回 (按钮, 滑块, 读数标签)。"""
    button = _dropdown(host, "帧", icons.icon_frame(), _FRAME_TIP)
    button.setObjectName("animationFrameButton")
    menu = QMenu(button)
    panel = QWidget(menu)
    panel.setMinimumWidth(260)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(10, 6, 10, 6)
    layout.setSpacing(4)
    readout = QLabel("预览帧 0 / 0", panel)
    slider = QSlider(Qt.Orientation.Horizontal, panel)
    slider.setObjectName("animationFrameSlider")
    slider.setRange(0, 0)
    slider.setSingleStep(1)
    slider.setPageStep(1)
    slider.setMinimumWidth(230)
    slider.setTickPosition(QSlider.TickPosition.NoTicks)
    layout.addWidget(readout)
    layout.addWidget(slider)
    action = QWidgetAction(menu)
    action.setDefaultWidget(panel)
    menu.addAction(action)
    button.setMenu(menu)
    slider.valueChanged.connect(on_change)
    return button, slider, readout
