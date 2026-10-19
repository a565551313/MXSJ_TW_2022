"""目录型基路径的子图拼名规则（纯逻辑、无 Qt）。

``sFileName`` 等资源字段以 ``\\``/``/`` 结尾的是目录型基路径：引擎运行时
在其下拼接子图，包内没有基路径本身这个条目（探针 v7 的 706 条伪引用）。
拼名族按来源分四类，本模块只负责「拼出哪几个名字、按什么结构拼」：

1. **序号帧**（三态按钮/勾选族）：``0.png`` 起连号，``GetInitPath`` 取
   ``\\0.png``、``SetFrame(n)`` 换 ``n.png``（interface.py 字节码；
   ``声音按钮\\`` 经用户实测 0/1/2.png）；
2. **横三片**（横框族）：``left1.png``+``middle.png``+``right2.png`` 等
   （combdialog.py ``CreatePngHFrame_New`` 字面量）；
3. **竖三片**（竖框族）：``top.png``+``middle.png``+``bottom.png``；
4. **九片**（九宫格族）：``top/left.png`` … ``bottom/right.png``
   （``top/left%s``/``middle%s`` 等字面量，``%s`` 为扩展名）。

候选按族优先级整组尝试，缺一块即换下一族；命中族即返回。图像取用与
合成由 :mod:`ui_editor.core.assets` 负责，本模块不加载任何图片。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

__all__ = ["DirBasePlan", "is_dir_base", "plan", "frame_series"]

#: 序号帧最多收集到几帧（游戏按钮族实测到 2，SetFrame(3) 另有目录；留余量）
FRAME_MAX = 8


@dataclass(frozen=True)
class DirBasePlan:
    """一族拼名方案：``kind`` 为 frames/h_slice/v_slice/nine_slice。"""

    kind: str
    pieces: tuple[str, ...]


def is_dir_base(name: str) -> bool:
    """资源值以斜杠结尾即目录型基路径。"""
    return bool(name) and name.endswith(("\\", "/"))


def frame_series(
    name: str, exists: Callable[[str], bool]
) -> tuple[str, ...] | None:
    """序号帧族：``0.png``/``0.igs`` 起连号收集；没有 0 号帧不算此族。"""

    def pick(index: int) -> str | None:
        for ext in (".png", ".igs"):
            candidate = f"{name}{index}{ext}"
            if exists(candidate):
                return candidate
        return None

    first = pick(0)
    if first is None:
        return None
    pieces = [first]
    for index in range(1, FRAME_MAX):
        candidate = pick(index)
        if candidate is None:
            break
        pieces.append(candidate)
    return tuple(pieces)


def _whole(names: tuple[str, ...], exists: Callable[[str], bool]) -> bool:
    return all(exists(name) for name in names)


def plan(name: str, exists: Callable[[str], bool]) -> DirBasePlan | None:
    """按族优先级返回第一组齐装的拼名方案；都拼不出返回 None。

    序：序号帧 → 横三片 → 九片 → 竖三片 → `bg` 单图（拼图族缺一块
    即换下族，单图族兜底）。
    """
    if not is_dir_base(name):
        return None
    series = frame_series(name, exists)
    if series is not None:
        return DirBasePlan("frames", series)
    for kind, candidates in (
        (
            "h_slice",
            (
                ("left1.png", "middle.png", "right2.png"),
                ("left2.png", "middle.png", "right1.png"),
                ("left.png", "middle.png", "right.png"),
                ("left.igs", "middle.igs", "right.igs"),
            ),
        ),
        (
            # 九片必须先于竖片：九片集含 top/middle/bottom.png，
            # 整组校验前先试九片，否则真九宫格会被误判成竖三片。
            "nine_slice",
            (
                (
                    "top/left.png",
                    "top.png",
                    "top/right.png",
                    "middle/left.png",
                    "middle.png",
                    "middle/right.png",
                    "bottom/left.png",
                    "bottom.png",
                    "bottom/right.png",
                ),
                (
                    "top/left.igs",
                    "top.igs",
                    "top/right.igs",
                    "middle/left.igs",
                    "middle.igs",
                    "middle/right.igs",
                    "bottom/left.igs",
                    "bottom.igs",
                    "bottom/right.igs",
                ),
            ),
        ),
        (
            "v_slice",
            (
                ("top.png", "middle.png", "bottom.png"),
                ("top.igs", "middle.igs", "bottom.igs"),
            ),
        ),
    ):
        for pieces in candidates:
            full = tuple(name + piece for piece in pieces)
            if _whole(full, exists):
                return DirBasePlan(kind, full)
    # bg 单图族（官服 1019 实测 6 例）：整目录就一张 bg，直接整图用。
    for piece in ("bg.png", "bg.igs"):
        if exists(name + piece):
            return DirBasePlan("single", (name + piece,))
    return None
