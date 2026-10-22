"""目录型基路径的子图拼名规则（纯逻辑、无 Qt）。

``sFileName`` 等资源字段以 ``\\\\``/``/`` 结尾的是目录型基路径：引擎运行时
在其下拼接子图，包内没有基路径本身这个条目。

拼名族**按 interface.fls 全量实测定版**（2026-10-22 复测同一真包：
614,482,967 B / 53,556 条目，2,708 篇 ``.dlg`` 全解，729 个目录型基路径
全部探到子图、0 个认不出）：

1. **按钮横片**（``h_state``，旧称“三态横片”）：``0l.png``+``0c.png``+
   ``0r.png``、``1l``… 每个状态是横三片（左/中/右），状态数即连号段长度
   （实测 36 个基路径：3 态 23、4 态 11、5 态 1、整图与横片混装 1）。
   **``CTextButton`` 不一定是横片**——同一个真包里它的基路径 53 个是
   整图、35 个是横片，所以族类型先看文件名结构，控件类型只在认不出时兜底；
   状态序号就是文件名前缀，**哪个序号是悬停/按下仍未与客户端核实**；
2. **序号帧**（``frames``）：``0.png`` 起连号，整张一行一态（按钮上就是
   一格一态）；实测 423 个基路径：3 张 351、4 张 49、2 张 14、1 张 4、
   5 张 2，另有 3 个混了 ``over.jpg``/``normal.bmp``/``0l.bmp`` 等杂项；``.igs``
   与 ``.png`` 同族不混用；
3. **九片**（``CPngNineFrame``/``CFrame``/``CBorder``）：``top/left`` …
   ``bottom/right`` 共 9 块，中列是 ``top/middle``、``middle/middle``、
   ``bottom/middle``——**没有** 平铺的 ``top.png``/``middle.png``/``bottom.png``
   （实测 130 个基路径：``.png`` 83、``.igs`` 41，另 6 个多出整图/``bg``，
   仍按九片切）；
4. **横三片**（``CHPngFrame``/``CHFrame``/``CProgress``）：``left`` +
   ``middle`` + ``right``（实测 109 个：``.png`` 75、``.igs`` 29，另 5 个
   同时带成品整图 ``0.png``/``bg.png``——按切片才对，整图是死尺寸）；
5. **竖三片**（``CVPngFrame``/``CVFrame``）：``top`` + ``middle`` + ``bottom``
   （实测 22 个：``.png`` 15、``.igs`` 6、多一张 ``normal.png`` 1）；
6. **单图**：整目录只有一张 ``bg``/``middle``（实测 9 个：``middle.png`` 4、
   ``middle.igs`` 4、``middle/middle.igs`` 1）。

整族同扩展名（``.png`` 或 ``.igs``）：实测包里没有一族混扩展名的情况，
故按扩展名整组尝试，缺一块即换下一族。

早前版本按反编译字面量写下的 ``left1.png``/``right2.png``/平铺 ``top.png``
三块九片在真语料上 **0 命中**（前者保留为兜底候选，后者已删）。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

__all__ = [
    "DirBasePlan", "KIND_LABELS", "WIDGET_DEFAULT_KINDS", "WIDGET_KINDS",
    "describe", "frame_series", "guess_kind", "is_dir_base",
    "map_stems_to_pieces", "match_kind", "naming_hint", "piece_names", "plan",
    "probe_pieces", "state_series",
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


#: 控件类型 → **位置词歧义**时按控件定族（文件名叫 ``left/middle/right``
#: 这种既可能是按钮的左/中/右片、也可能是普通横三片的时候用）。
#: 名字能说明结构（``0/1/2``、``0l/0c/0r``、``top/left``）时一律听文件名的。
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

#: 控件类型 → **文件名认不出**、只能按张数兜底时的默认族（真包多数派）。
#:
#: 2026-10-22 在同一份 ``interface.fls``（729 个目录型基路径）上逐控件类型
#: 复核，按**不同基路径**计：
#:
#: - ``CTextButton``：整图 ``0/1/2.png`` **53** 个，横片 ``0l/0c/0r`` **35** 个；
#: - ``CHPagePngButton``：整图 16，横片 10；
#: - ``CVPagePngButton``：整图 11，横片 **0**。
#:
#: 所以"按钮控件就是横片"不成立（0.13.3 之前 `CTextButton`→``h_state`` 只是
#: 推荐，不是实测）。名字认不出时整图才是多数派，位置词歧义仍按
#: :data:`WIDGET_KINDS` 走横片。其余类型两张表一致。
WIDGET_DEFAULT_KINDS = {
    **WIDGET_KINDS,
    "CTextButton": "frames",
    "CHPagePngButton": "frames",
    "CVPagePngButton": "frames",
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


#: 用户自己起名时常见的同义写法（英文/中文/缩写）→ 族内的边
_SIDE_WORDS = {
    "l": "left", "left": "left", "左": "left", "左边": "left", "左片": "left",
    "m": "middle", "middle": "middle", "c": "middle", "center": "middle",
    "centre": "middle", "中": "middle", "中间": "middle", "中片": "middle",
    "r": "right", "right": "right", "右": "right", "右边": "right",
    "右片": "right",
    "t": "top", "top": "top", "上": "top", "上边": "top", "上片": "top",
    "b": "bottom", "bottom": "bottom", "下": "bottom", "下边": "bottom",
    "下片": "bottom",
}
_H_SIDES = ("left", "middle", "right")
_V_SIDES = ("top", "middle", "bottom")


def _normalise_stem(stem: str) -> str:
    return stem.strip().lower().replace("_", "-").replace(" ", "")


def _side(token: str) -> str | None:
    return _SIDE_WORDS.get(_normalise_stem(token))


#: 只认 ASCII 数字：``str.isdigit()`` 对 ``①``/``²`` 也返回 True，但
#: ``int()`` 会抛 ValueError——一个叫 ``①.png`` 的文件就能让对话框打不开。
_DIGITS = "0123456789"


def _leading_digits(text: str) -> tuple[str, str]:
    """拆开头的 ASCII 数字：``"12l"`` → ``("12", "l")``。"""
    index = 0
    while index < len(text) and text[index] in _DIGITS:
        index += 1
    return text[:index], text[index:]


_GRID_ROWS = ("top", "middle", "bottom")
_GRID_COLUMNS = ("left", "middle", "right")


def _grid_pair(first: str | None, second: str | None) -> tuple[str, str] | None:
    """两个边 → (行, 列)。``tl`` 与中文 ``左上`` 的先后顺序不同，两种都认。"""
    if first in _GRID_ROWS and second in _GRID_COLUMNS:
        return (first, second)
    if first in _GRID_COLUMNS and second in _GRID_ROWS:
        return (second, first)
    return None


def _split_sides(stem: str) -> tuple[str, str] | None:
    """九片的一格：``top-left`` / ``tl`` / ``左上`` 都认。"""
    text = _normalise_stem(stem)
    if "-" in text:
        head, _, tail = text.partition("-")
        return _grid_pair(_side(head), _side(tail))
    if len(text) == 2:
        return _grid_pair(_side(text[0]), _side(text[1]))
    return None


def _piece_of_stem(stem: str, kind: str, count: int) -> str | None:
    """一个文件名 → 族内相对名；认不出返回 None。"""
    text = _normalise_stem(stem)
    names = piece_names(kind, count) or ()
    if not names:
        return None
    if kind == "single":
        return names[0]
    if kind == "frames":
        index = text[5:] if text.startswith("frame") else text
        if index and all(ch in _DIGITS for ch in index) \
                and int(index) < len(names):
            return names[int(index)]
        return None
    if kind == "h_state":
        states = count // 3
        digits, rest = _leading_digits(text)
        rest = rest.lstrip("-")
        side = _side(rest)
        # 竖排别名（上/下、top/bottom）不是横向的边：认出来也不能进
        # _H_SIDES 索引，否则 ValueError。返回 None 交给调用方按顺序分。
        if side not in _H_SIDES:
            return None
        # 只有一个状态时状态号是多余的：只导出了第 2 态、文件叫 1l/1c/1r
        # 也应当成这一族；多态时状态号必须对得上。
        index = 0 if states == 1 else (int(digits) if digits else 0)
        if index >= states:
            return None
        return f"{index}{'lcr'[_H_SIDES.index(side)]}"
    if kind == "nine_slice":
        pair = _split_sides(text)
        if pair is None:
            return None
        row, column = pair
        if row not in _GRID_ROWS or column not in _GRID_COLUMNS:
            return None
        return f"{row}/{column}"
    if kind == "h_slice":
        side = _side(text)
        return side if side in _H_SIDES else None
    if kind == "v_slice":
        side = _side(text)
        return side if side in _V_SIDES else None
    return None


def map_stems_to_pieces(stems, kind: str) -> list[str] | None:
    """按**文件名**把每张图对到族内名（``左.png`` → ``0l``、
    ``左上.png`` → ``top/left``）。

    返回与输入同序的族内名列表；有一张认不出、或两张抢同一个族内名时返回
    None（交回调用方按顺序分配）。用于"我自己起的名字"这种场景：不要求
    用户把文件改成 ``0l/0c/0r`` 才认得出来。
    """
    items = list(stems)
    count = len(items)
    if not items or piece_names(kind, count) is None:
        return None
    mapped = [_piece_of_stem(stem, kind, count) for stem in items]
    if any(piece is None for piece in mapped):
        return None
    if len(set(mapped)) != len(mapped):
        return None
    return [piece for piece in mapped if piece is not None]


def naming_hint(kind: str, count: int) -> str:
    """「想精确控制顺序该怎么命名」的一句话（对话框里显示）。"""
    names = piece_names(kind, count)
    if names is None:
        return "张数对不上这种族。"
    if kind == "h_state":
        return ("命名建议：每态三张叫 0l / 0c / 0r（或 左 / 中 / 右），"
                "多态就 1l / 1c / 1r …；名字认得出就与选择顺序无关。")
    if kind == "nine_slice":
        return ("命名建议：top-left / top-middle … bottom-right"
                "（或 左上 / 上中 … 右下）；名字认得出就与选择顺序无关。")
    if kind == "h_slice":
        return ("命名建议：left / middle / right（或 左 / 中 / 右）；"
                "名字认得出就与选择顺序无关。")
    if kind == "v_slice":
        return ("命名建议：top / middle / bottom（或 上 / 中 / 下）；"
                "名字认得出就与选择顺序无关。")
    if kind == "frames":
        return ("命名建议：0 / 1 / 2 …（或 frame0 / frame1 …）；"
                "名字认得出就与选择顺序无关。")
    return "单张图，随便叫什么名都行。"


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
    """没认出文件名时的推荐类型：先看控件的实测多数派，再看张数。

    ``WIDGET_DEFAULT_KINDS`` 是真包多数派（按钮多为整图），``WIDGET_KINDS``
    是位置词歧义时的选择（按钮写 ``0l/0c/0r``）：9 张对按钮正好是 3 态横片，
    多数派的 ``frames`` 收不下（上限 :data:`FRAME_MAX`），于是退到后者。
    """
    for table in (WIDGET_DEFAULT_KINDS, WIDGET_KINDS):
        preferred = table.get(widget_type or "")
        if preferred and piece_names(preferred, count) is not None:
            return preferred
    for kind in ("nine_slice", "h_state", "h_slice", "v_slice", "single",
                 "frames"):
        if piece_names(kind, count) is not None:
            return kind
    return None


#: 探测"这个目录里到底有什么"时试的名字（相对族目录、不含扩展名）。
#: 包里条目只存哈希、没有文件名，只能按候选名去问"在不在"——所以这张
#: 表要覆盖所有实测见过的写法，才谈得上"看得见里面是什么"。
_PROBE_STEMS: tuple[str, ...] = (
    *(f"{index}{side}" for index in range(FRAME_MAX) for side in "lcr"),
    *(str(index) for index in range(FRAME_MAX * 2)),
    "left", "middle", "right", "top", "bottom",
    *(f"{row}-{column}" for row in ("top", "middle", "bottom")
      for column in ("left", "middle", "right")),
    *(f"{row}/{column}" for row in ("top", "middle", "bottom")
      for column in ("left", "middle", "right")),
    "tl", "tm", "tr", "ml", "mm", "mr", "bl", "bm", "br",
    "bg", "middle/middle",
    # 反编译字面量里的历史写法（真语料 0 命中，但用户手上可能有）
    "left1", "left2", "right1", "right2",
)


def probe_pieces(name: str, exists: Callable[[str], bool]) -> tuple[str, ...]:
    """按候选名探一遍，返回这个目录里**实际存在**的子图（含扩展名）。

    包里没有"目录"这个条目，条目名也只是哈希——想知道某个基路径下面到底
    有哪几张图，只能拿候选名逐个问。用于选图窗的"里面是什么"说明：
    即使这个命名规则 :func:`plan` 认不出来，也能把找到的文件列给用户。
    """
    if not is_dir_base(name):
        return ()
    found: list[str] = []
    for stem in _PROBE_STEMS:
        for ext in EXTS:
            candidate = f"{name}{stem}{ext}"
            if exists(candidate):
                found.append(f"{stem}{ext}")
    return tuple(found)


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
