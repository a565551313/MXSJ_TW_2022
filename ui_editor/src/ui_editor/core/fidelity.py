"""画布绘制的保真度说明（纯逻辑，无 Qt）。

编辑器画的东西分三档，这里只说清楚「这一件控件现在属于哪一档、为什么」：

- **原生**：资源形态与拼法都有证据（九片/横三片/竖三片/三态横片按资源切片的
  真实像素尺寸拼；整图按原尺寸 1:1 绘制；`.spr` 画帧表里真实存在的那一帧）；
- **近似**：拼法是文档化的推断而非客户端实据（单图九宫格固定三分、整图
  拉伸、态序号→悬停/按下的对应、按帧序推断按钮状态）；
- **模拟**：编辑器自己加上去的东西（按下/悬停/禁用的压暗提亮灰化、缺图
  占位框）。

用户可见的落点：画布右下角角标、状态栏、诊断面板。三档措辞固定，便于
对照真机截图时一眼分清「客户端本来就这样」和「编辑器猜的」。

本模块不加载图片：资源侧通过 ``view`` 提供两个查询——
``slice_kind(name)``（"h_slice"/"v_slice"/"nine_slice"/None；三态按钮的
常态态也按 h_slice 报）与
``frame_count(name)``（帧数，取不到 0）。
"""

from __future__ import annotations

from dataclasses import dataclass

from . import runtime_state

__all__ = ["APPROX", "BUTTON_STATE_INDEX", "MARKERS", "NATIVE", "SIMULATED",
           "Marker", "markers", "summary"]

#: 按钮状态 → 帧序号。**顺序未与客户端核实**：只能按「按下在前、悬停次之、
#: 禁用最后」的常见排法推断，画布据此取帧时必须标「近似」。
#:
#: 2026-10-20 实测（interface.fls，729 个目录型基路径）：按钮的态**就是文件名
#: 前缀**——``CButton`` 是整图 ``0/1/2.png``（最多到 ``4.png``），
#: ``CTextButton``/``*PagePngButton`` 是每态横三片 ``{n}l/{n}c/{n}r``；
#: 实测态数 2～5。文件里没有任何字段说明「第几态是悬停」，故序号语义仍是推断。
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


#: 与 :mod:`ui_editor.core.painters` 的 `SOURCE_*` 同值（不反向依赖 Qt 模块）
_SRC_NONE = "none"
_SRC_CODE_SKIN = "code_skin"
_SRC_SLICE = "slice"
_SRC_SLICE_STATE = "slice_state"
_SRC_IMAGE = "image"
_SRC_DLG_COLOR = "dlg_color"
_SRC_STYLE_SKIN = "style_skin"
_SRC_BUTTON_STYLE = "button_style"
_SRC_EDITOR_DEFAULT = "editor_default"
_SRC_PLACEHOLDER = "placeholder"


def _source_of(widget, view) -> str | None:
    """绘制来源；view 不支持时返回 None（走旧的资源探测路径）。"""
    getter = getattr(view, "source_kind", None)
    if getter is None:
        return None
    try:
        return getter(widget)
    except Exception:  # 标注失败不影响绘制，退回过探测
        return None


#: 有按钮态预览的控件类型（与 painters 同口径）
_BUTTON_TYPES = frozenset({
    "CButton", "CHPageButton", "CVPageButton",
    "CHPagePngButton", "CVPagePngButton", "CTextButton",
})


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
    source = _source_of(widget, view)
    if source is not None:
        # 绘制层直接告诉我们画的是哪条路（皮肤/切片/图/占位），不再自己猜
        if source == _SRC_NONE:
            return result
        if source == _SRC_CODE_SKIN:
            result.append(Marker(
                APPROX, "code_skin",
                "脚本现造按钮：按代码皮肤绘制（静态索引推断，"
                "客户端由脚本运行时创建）。"))
            return result
        if source == _SRC_DLG_COLOR:
            result.append(Marker(
                APPROX, "dlg_color",
                "图片取不到，按 .dlg 的 lNormalColor 画底色"
                "（不是 ui.lst；客户端实际外观未核实）。"))
            return result
        if source == _SRC_STYLE_SKIN:
            result.append(Marker(
                APPROX, "style_skin",
                "图片取不到，按 ui.lst 的 iStyle 样式表配色绘制"
                "（客户端实际外观未核实）。"))
            return result
        if source == _SRC_BUTTON_STYLE:
            result.append(Marker(
                SIMULATED, "button_style",
                "没有图片，iStyle 也没给出常态色：底色是编辑器默认色。"))
            return result
        if source == _SRC_EDITOR_DEFAULT:
            result.append(Marker(
                SIMULATED, "editor_default",
                "图片取不到：按编辑器默认配色绘制，不是客户端画面。"))
            return result
        if source == _SRC_PLACEHOLDER:
            text = ("目录型基路径没拼出任何切片族：画的是编辑器占位框。"
                    if name.endswith(("\\", "/")) else
                    "资源取不到：画的是编辑器占位框，不是客户端画面。")
            result.append(Marker(SIMULATED, "missing_placeholder", text))
            return result

    if not name:
        return result

    kind = view.slice_kind(name) if view is not None else None
    if kind in _SLICE_LABEL:
        result.append(Marker(
            NATIVE, "native_" + kind,
            f"{_SLICE_LABEL[kind]}：切割线来自资源切片本身，"
            "四角/两端按原像素、中间拉伸。"))
        if button_state != "normal" and widget.wtype in _BUTTON_TYPES:
            if source == _SRC_SLICE_STATE:
                result.append(Marker(
                    APPROX, "state_slice_by_index",
                    "按钮态按文件名前缀取该态切片；"
                    "哪个序号是悬停/按下未与客户端核实。"))
            else:
                result.append(Marker(
                    SIMULATED, "state_overlay",
                    "该切片族没有真实按钮态：按下/悬停/禁用是"
                    "编辑器压暗/提亮/灰化的模拟效果。"))
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

    if button_state != "normal" and widget.wtype in _BUTTON_TYPES:
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
