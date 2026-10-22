"""目录型基路径的子图拼名规则（纯逻辑、无 Qt）。

``sFileName`` 等资源字段以 ``\\\\``/``/`` 结尾的是目录型基路径：引擎运行时
在其下拼接子图，包内没有基路径本身这个条目。

拼名族**按 interface.fls 全量实测定版**（2026-10-20，614,482,967 B、
2,708 篇 ``.dlg``、729 个目录型基路径全部探测过，结果见
``docs/EXTERNAL_CORPUS.md``）：

1. **三态横片**（``CTextButton``/``CHPagePngButton``/``CVPagePngButton``）：
   ``0l.png``+``0c.png``+``0r.png``、``1l``… 每个状态是横三片，状态数即
   连号段长度（实测 2～5 态）。状态序号就是文件名前缀，**哪个序号是悬停/
   按下仍未与客户端核实**；
2. **序号帧**（``CButton`` 等）：``0.png`` 起连号，整张一行一态；``.igs``
   与 ``.png`` 同族不混用；
3. **九片**（``CPngNineFrame``/``CFrame``/``CBorder``）：``top/left`` …
   ``bottom/right`` 共 9 块，中列是 ``top/middle``、``middle/middle``、
   ``bottom/middle``——**没有** 平铺的 ``top.png``/``middle.png``/``bottom.png``
   （实测 130 个九片基路径，全部 9 块齐装）；
4. **横三片**（``CHPngFrame``/``CHFrame``/``CProgress``）：``left`` +
   ``middle`` + ``right``（实测 105 个）；
5. **竖三片**（``CVPngFrame``/``CVFrame``）：``top`` + ``middle`` + ``bottom``
   （实测 22 个）；
6. **单图**：整目录只有一张 ``bg``/``middle``（实测 10 个）。

整族同扩展名（``.png`` 或 ``.igs``）：实测包里没有一族混扩展名的情况，
故按扩展名整组尝试，缺一块即换下一族。

早前版本按反编译字面量写下的 ``left1.png``/``right2.png``/平铺 ``top.png``
三块九片在真语料上 **0 命中**（前者保留为兜底候选，后者已删）。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

__all__ = [
    "DirBasePlan", "KIND_LABELS", "WIDGET_KINDS", "describe", "frame_series",
    "guess_kind", "is_dir_base", "match_kind", "piece_names", "plan",
    "state_series",
]

#: 序号帧/状态最多收到第几号（实测按钮最多 5 态，留余量）
FRAME_MAX = 8

#: 同族候选扩展名（按优先级；整族同扩展名）
EXTS = (".png", ".igs")

#: 拼名族 → 给人看的名字（诊断文案、选图窗共用）。
#: ``h_state`` 旧称"三态横片"，容易被读成"必须三个态"——它其实是
#: "按钮横片"：每 3 张（左/中/右）一个状态，1 个状态也能用。
KIND_LABELS = {
    "h_state": "按钮横片",
    "frames": "序号帧",
    "nine_slice": "九片",
    "h_slice": "横三片",
    "v_slice": "竖三片",
    "single": "单图",
}

#: 九片：行 × 列（顺序必须是 nine_slice 要的行优先九块）
GRID_PIECES = tuple(
    f"{row}/{column}"
    for row in ("top", "middle", "bottom")
    for column in ("left", "middle", "right")
)


@dataclass(frozen=True)
class DirBasePlan:
    """一族拼名方案。

    ``kind``：

    - ``h_state``：三态横片，``pieces`` 是 ``状态数 × 3`` 条（``0l 0c 0r
      1l 1c 1r …``），按状态分行；
    - ``frames``：``pieces`` 每项是一帧整图；
    - ``nine_slice``/``h_slice``/``v_slice``：``pieces`` 依次是九/三块；
    - ``single``：一张整图。
    """

    kind: str
    pieces: tuple[str, ...]

    @property
    def states(self) -> int:
        """按钮态数（``h_state`` 家族）；其它家族为 1。"""
        return len(self.pieces) // 3 if self.kind == "h_state" else 1

    def state_pieces(self, index: int = 0) -> tuple[str, ...]:
        """取某态的横三片（``index`` 越界按 0 处理）。"""
        if self.kind != "h_state":
            return self.pieces
        count = self.states
        index = index if 0 <= index < count else 0
        return self.pieces[index * 3:index * 3 + 3]


#: 控件类型 → 新建族时的推荐拼名类型（与上面实测定版的族一致）
WIDGET_KINDS = {
    "CTextButton": "h_state",
    "CHPagePngButton": "h_state",
    "CVPagePngButton": "h_state",
    "CPngNineFrame": "nine_slice",
    "CFrame": "nine_slice",
    "CBorder": "nine_slice",
    "CHPngFrame": "h_slice",
    "CHFrame": "h_slice",
    "CProgress": "h_slice",
    "CVPngFrame": "v_slice",
    "CVFrame": "v_slice",
    "CButton": "frames",
}


def is_dir_base(name: str) -> bool:
    """资源值以斜杠结尾即目录型基路径。"""
    return bool(name) and name.endswith(("\\", "/"))


def piece_names(kind: str, count: int) -> tuple[str, ...] | None:
    """新建族时 ``count`` 张图对应的族内相对名（不含扩展名）。

    张数与该族对不上返回 None（三态横片要 3 的倍数、九片正好 9 张…）：
    拼名族是"整族齐装"才生效，张数不对写进包也拼不出来。
    """
    if count <= 0:
        return None
    if kind == "h_state":
        if count % 3 or count > FRAME_MAX * 3:
            return None
        return tuple(f"{index}{side}"
                     for index in range(count // 3) for side in "lcr")
    if kind == "nine_slice":
        return GRID_PIECES if count == len(GRID_PIECES) else None
    if kind == "h_slice":
        return ("left", "middle", "right") if count == 3 else None
    if kind == "v_slice":
        return ("top", "middle", "bottom") if count == 3 else None
    if kind == "single":
        return ("bg",) if count == 1 else None
    if kind == "frames":
        if 1 <= count <= FRAME_MAX:
            return tuple(str(index) for index in range(count))
        return None
    return None


def _stem_of(name: str) -> str:
    """文件名 → 族内相对名：去扩展名，导出的 ``top-left`` 还原成 ``top/left``。"""
    base = str(name).replace("\\", "/").rstrip("/").split("/")[-1]
    if "." in base[1:]:
        base = base[:base.rfind(".")]
    return base


def match_kind(names) -> str | None:
    """按**文件名**认出这是哪一种族（导出 → 改图 → 导回来的往返）。

    ``0l/0c/0r`` 走三态横片、``top-left`` … 走九片、``left/middle/right``
    走横三片、纯数字走序号帧。认不出返回 None——那种情况由用户选类型，
    按顺序分配族内名。
    """
    items = list(names)
    stems = {_stem_of(name).replace("-", "/").lower() for name in items}
    count = len(items)
    for kind in ("h_state", "nine_slice", "h_slice", "v_slice", "frames",
                 "single"):
        expected = piece_names(kind, count)
        if expected is None:
            continue
        if stems == {name.replace("-", "/").lower() for name in expected}:
            return kind
    return None


def guess_kind(count: int, widget_type: str | None = None) -> str | None:
    """没认出文件名时的推荐类型：先看控件，再看张数。"""
    preferred = WIDGET_KINDS.get(widget_type or "")
    if preferred and piece_names(preferred, count) is not None:
        return preferred
    for kind in ("nine_slice", "h_state", "h_slice", "v_slice", "single",
                 "frames"):
        if piece_names(kind, count) is not None:
            return kind
    return None


def describe(chosen: DirBasePlan | None) -> str | None:
    """族的一句话说明（``三态横片 · 2 态`` / ``九片 · 9 块``）。

    给选图窗、状态栏这类只有一行位置的地方用；没有命中返回 None。
    """
    if chosen is None:
        return None
    label = KIND_LABELS.get(chosen.kind, chosen.kind)
    if chosen.kind == "h_state":
        return f"{label} · {chosen.states} 态"
    if chosen.kind == "frames":
        return f"{label} · {len(chosen.pieces)} 帧"
    if chosen.kind == "single":
        return f"{label} · {chosen.pieces[0].rsplit(chr(92), 1)[-1]}"
    return f"{label} · {len(chosen.pieces)} 块"


def _whole(names: tuple[str, ...], exists: Callable[[str], bool]) -> bool:
    return all(exists(name) for name in names)


def frame_series(
    name: str, exists: Callable[[str], bool]
) -> tuple[str, ...] | None:
    """序号帧族：``0.png``/``0.igs`` 起连号收集；没有 0 号帧不算此族。"""

    def pick(index: int) -> str | None:
        for ext in EXTS:
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


def state_series(
    name: str, exists: Callable[[str], bool]
) -> tuple[str, ...] | None:
    """三态横片族：``{n}l``+``{n}c``+``{n}r`` 同扩展名连号收集。

    返回按状态平铺的 ``3 × 状态数`` 条路径；没有 0 号态返回 None。
    """
    for ext in EXTS:
        pieces: list[str] = []
        for index in range(FRAME_MAX):
            trio = tuple(f"{name}{index}{side}{ext}" for side in "lcr")
            if not _whole(trio, exists):
                break
            pieces.extend(trio)
        if pieces:
            return tuple(pieces)
    return None


def _grid(name: str, ext: str) -> tuple[str, ...]:
    return tuple(name + piece + ext for piece in GRID_PIECES)


#: 各族候选（同族同扩展名，整组齐装才算命中）
_H_SLICES = (
    ("left.png", "middle.png", "right.png"),
    ("left.igs", "middle.igs", "right.igs"),
    # 反编译字面量的历史候选：真语料 0 命中，仅作兜底
    ("left1.png", "middle.png", "right2.png"),
    ("left2.png", "middle.png", "right1.png"),
)
_V_SLICES = (("top.png", "middle.png", "bottom.png"),
             ("top.igs", "middle.igs", "bottom.igs"))
_SINGLES = (
    ("bg.png",), ("bg.igs",),
    ("middle.png",), ("middle.igs",),
    # 整个目录只有九片正中那一块（实测 combdialog\\主框架\\石纹\\，203 处引用）
    ("middle/middle.png",), ("middle/middle.igs",),
)


def plan(name: str, exists: Callable[[str], bool]) -> DirBasePlan | None:
    """按族优先级返回第一组齐装的拼名方案；都拼不出返回 None。

    序：三态横片 → 九片 → 横三片 → 竖三片 → 序号帧 → 单图。

    拼图族（三片/九片）一律先于整图族：

    - 九片必须先于横三片：48 个九片基路径同时有平铺 ``left/middle/right``
      （``CPngNineFrame``），按九片切才对；
    - 横三片必须先于序号帧：``combdialog4\\杂图\\经验进度条\\`` 这类
      ``CProgress`` 既有 ``0.png``（成品整条 134×14）又有 ``left/middle/
      right``（8+16+8，中间可拉伸），客户端按切片拉伸，整图会画出死尺寸。
    """
    if not is_dir_base(name):
        return None
    states = state_series(name, exists)
    if states is not None:
        return DirBasePlan("h_state", states)
    for ext in EXTS:
        pieces = _grid(name, ext)
        if _whole(pieces, exists):
            return DirBasePlan("nine_slice", pieces)
    for candidates in _H_SLICES:
        pieces = tuple(name + piece for piece in candidates)
        if _whole(pieces, exists):
            return DirBasePlan("h_slice", pieces)
    for candidates in _V_SLICES:
        pieces = tuple(name + piece for piece in candidates)
        if _whole(pieces, exists):
            return DirBasePlan("v_slice", pieces)
    series = frame_series(name, exists)
    if series is not None:
        return DirBasePlan("frames", series)
    for candidates in _SINGLES:
        pieces = tuple(name + piece for piece in candidates)
        if _whole(pieces, exists):
            return DirBasePlan("single", pieces)
    return None
