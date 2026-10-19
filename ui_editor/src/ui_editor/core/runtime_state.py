"""运行时可见状态：`bShow` / `bLoad` 的归一化（纯逻辑，无 Qt）。

`.dlg` 里这两个字段的写法不止一种：``bool``、``0/1``、``"0"/"1"``、
``"true"/"false"``，也有写成单元素列表的。这里统一成三态，供画布与
诊断共用，避免两处各写一套判断。

**字段语义边界**：``bShow=0`` 的含义（布局里有、运行时隐藏）在官服布局
里可直接观察到——这些控件在编辑器里看得见、进游戏不显示；``bLoad=0``
的含义**未与客户端核实**，只能按字面理解为「运行时不加载/不创建这个
控件」，所以 :func:`describe` 对它的措辞保留「未核实」。
"""

from __future__ import annotations

__all__ = ["HIDDEN", "NOT_LOADED", "SHOWN", "UNKNOWN", "describe", "state_of",
           "truthy"]

SHOWN = "shown"
HIDDEN = "hidden"        # bShow = 0：布局里有、运行时隐藏
NOT_LOADED = "not_loaded"  # bLoad = 0：运行时可能不加载（语义未核实）
UNKNOWN = "unknown"      # 字段缺失或写法认不出


def _first(value: object) -> object:
    if isinstance(value, (list, tuple)):
        return value[0] if value else None
    return value


def truthy(value: object) -> bool | None:
    """把 `bShow` 的写法归一成布尔；认不出返回 None（不当成 false 猜）。"""
    value = _first(value)
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        text = value.strip().lower()
        if text in ("1", "true", "yes", "on"):
            return True
        if text in ("0", "false", "no", "off"):
            return False
    return None


def state_of(widget) -> str:
    """控件的运行时可见状态：SHOWN / HIDDEN / NOT_LOADED / UNKNOWN。"""
    props = widget.props
    show = truthy(props.get("bShow"))
    if show is False:
        return HIDDEN
    load = truthy(props.get("bLoad"))
    if load is False:
        return NOT_LOADED
    if show is None and "bShow" not in props:
        return UNKNOWN
    return SHOWN


def describe(state: str) -> str:
    """给用户看的一句话说明（画布角标与诊断共用措辞）。"""
    if state == HIDDEN:
        return "运行时隐藏（bShow=0）：布局里有，进游戏不显示。"
    if state == NOT_LOADED:
        return ("bLoad=0：字段字面意思是运行时不加载这个控件；"
                "具体行为未与客户端核实。")
    if state == UNKNOWN:
        return "布局里没有 bShow 字段，按显示处理。"
    return "运行时正常显示。"
