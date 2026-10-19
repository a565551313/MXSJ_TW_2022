"""画布绘制的保真度说明（纯逻辑，无 Qt）。

编辑器画的东西分三档，这里只说清楚「这一件控件现在属于哪一档、为什么」：

- **原生**：资源形态与拼法都有证据（九片/横三片/竖三片按资源切片的真实
  像素尺寸拼；整图按原尺寸 1:1 绘制；`.spr` 画帧表里真实存在的那一帧）；
- **近似**：拼法是文档化的推断而非客户端实据（单图九宫格固定三分、整图
  拉伸、按帧序推断按钮状态）；
- **模拟**：编辑器自己加上去的东西（按下/悬停/禁用的压暗提亮灰化、缺图
  占位框）。

用户可见的落点：画布右下角角标、状态栏、诊断面板。三档措辞固定，便于
对照真机截图时一眼分清「客户端本来就这样」和「编辑器猜的」。

本模块不加载图片：资源侧通过 ``view`` 提供两个查询——
``slice_kind(name)``（"h_slice"/"v_slice"/"nine_slice"/None）与
``frame_count(name)``（帧数，取不到 0）。
"""

from __future__ import annotations

from dataclasses import dataclass

from . import runtime_state

__all__ = ["APPROX", "BUTTON_STATE_INDEX", "MARKERS", "NATIVE", "SIMULATED",
           "Marker", "markers", "summary"]

#: 按钮状态 → 帧/竖条序号。**顺序未与客户端核实**：只能按「按下在前、
#: 悬停次之、禁用最后」的常见排法推断，画布据此取帧时必须标「近似」。
BUTTON_STATE_INDEX = {"pressed": 1, "hover": 2, "disabled": 3}

NATIVE = "原生"
APPROX = "近似"
SIMULATED = "模拟"

#: 各档角标颜色（画布用；纯数据，方便测试与主题统一）
MARKERS = {NATIVE: "#3fb27f", APPROX: "#e0a83c", SIMULATED: "#e0645c"}

_SLICE_LABEL = {
    "h_slice": "横三片",
    "v_slice": "竖三片",
    "nine_slice": "九片",
}


@dataclass(frozen=True)
class Marker:
    """一条保真度说明：``level`` 是 原生/近似/模拟，``code`` 供测试与诊断。"""

    level: str
    code: str
    text: str


def _image_name(widget) -> str:
    key = "sBgFileName" if widget.wtype == "CProgress" else "sFileName"
    value = widget.props.get(key)
    return value if isinstance(value, str) else ""


def _natural_size(widget) -> tuple[int, int]:
    return widget.width, widget.height


def markers(widget, view, button_state: str = "normal") -> list[Marker]:
    """这件控件当前绘制属于哪些档；空列表表示没有任何图可谈。"""
    result: list[Marker] = []
    state = runtime_state.state_of(widget)
    if state == runtime_state.HIDDEN:
        result.append(Marker(NATIVE, "runtime_hidden",
                             "运行时隐藏（bShow=0）：布局里有，进游戏不显示。"))
    elif state == runtime_state.NOT_LOADED:
        result.append(Marker(APPROX, "runtime_not_loaded",
                             "bLoad=0：可能不加载这个控件；语义未与客户端核实。"))

    name = _image_name(widget)
    if not name:
        return result

    kind = view.slice_kind(name) if view is not None else None
    if kind in _SLICE_LABEL:
        result.append(Marker(
            NATIVE, "native_" + kind,
            f"{_SLICE_LABEL[kind]}：切割线来自资源切片本身，"
            "四角/两端按原像素、中间拉伸。"))
        return result

    frames = view.frame_count(name) if view is not None else 0
    if frames <= 0:
        result.append(Marker(SIMULATED, "missing_placeholder",
                             "资源取不到：画的是编辑器占位框，不是客户端画面。"))
        return result

    if name.lower().endswith(".spr"):
        result.append(Marker(APPROX, "spr_single_frame",
                             "只画 .spr 的当前帧；客户端按帧时序播放。"))

    if widget.wtype == "CPngNineFrame":
        result.append(Marker(APPROX, "nine_fixed_thirds",
                             "单图九宫格按固定三分切：.dlg 没有切割字段，"
                             "切割线未与客户端核实。"))
        return result

    if frames == 1:
        width, height = _natural_size(widget)
        if width > 0 and height > 0:
            image_size = view.image_size(name) if view is not None else None
            if image_size and (width, height) == tuple(image_size):
                result.append(Marker(NATIVE, "native_1to1",
                                     "整图按原尺寸 1:1 绘制。"))
            else:
                result.append(Marker(APPROX, "stretched_image",
                                     "整图拉伸到控件尺寸（客户端切法未核实）。"))

    if button_state != "normal" and widget.wtype in (
            "CButton", "CHPageButton", "CVPageButton",
            "CHPagePngButton", "CVPagePngButton", "CTextButton"):
        index = BUTTON_STATE_INDEX.get(button_state)
        if index is not None and frames > index:
            result.append(Marker(APPROX, "state_by_frame_order",
                                 "按钮状态按帧序取帧：顺序未与客户端核实。"))
        else:
            result.append(Marker(SIMULATED, "state_overlay",
                                 "按钮状态是编辑器压暗/提亮/灰化的模拟效果。"))
    return result


def summary(widget, view, button_state: str = "normal") -> str:
    """一句话给状态栏：最高的一档 + 主要说明。"""
    found = markers(widget, view, button_state)
    if not found:
        return "无图片素材：按控件类型/样式表绘制（编辑器样式）。"
    order = {NATIVE: 0, APPROX: 1, SIMULATED: 2}
    worst = max(found, key=lambda marker: order[marker.level])
    return f"{worst.level}：{worst.text}"
