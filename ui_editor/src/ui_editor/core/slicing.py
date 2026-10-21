"""九宫格/横竖三片的切片几何（纯逻辑，无 Qt）。

切割线从**资源本身**取，不是猜的：

- 横三片 ``left1.png`` + ``middle.png`` + ``right2.png``：左右两块按各自像素
  宽度固定，中间那块吃掉剩余宽度，三块都按控件高度纵向拉伸；
- 竖三片 ``top`` + ``middle`` + ``bottom``：上下两块按各自像素高度固定，中间
  吃掉剩余高度，三块都按控件宽度横向拉伸；
- 九片 ``top/left.png`` … ``bottom/right.png``：左右列的宽度取该列各块的最大
  像素宽、上下行的高度取该行各块的最大像素高，四角按切片尺寸原样放，四条边
  单向拉伸，中心双向拉伸。

依据：反编译 ``combdialog.py`` 的 ``left1.png``/``middle.png``/``right2.png``
与 ``top/left%s``/``middle%s`` 字面量（拼名族由 :mod:`ui_editor.core.dir_base`
给出），切片尺寸由这些文件的真实像素尺寸给出。**单张图的九宫格**没有切割线
证据（`.dlg` 里没有切割字段），不在这里猜，由绘制层单独标「近似」。

目标尺寸不够放四角/两端时按比例缩小固定块（总和压到目标尺寸），不出现负尺寸、
不越界；文档里明确这是保底行为。
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "BLANK_SKIP_DOC",
    "Cell",
    "Piece",
    "SlicePlan",
    "fixed_thirds",
    "h_slice",
    "nine_slice",
    "nine_thirds_cells",
    "layout",
    "stretch",
    "v_slice",
]

BLANK_SKIP_DOC = (
    "整块全透明的切片不绘制（不占位、不留白色底），底下内容照常露出。"
)


@dataclass(frozen=True)
class Piece:
    """一块切片的像素尺寸（内容由绘制层提供；单图三分可能带小数）。"""

    width: float
    height: float


@dataclass(frozen=True)
class Cell:
    """一块切片画到哪：源矩形（切片内）与目标矩形（控件内）。"""

    index: int
    src: tuple[float, float, float, float]
    dst: tuple[float, float, float, float]

    @property
    def empty(self) -> bool:
        return self.dst[2] <= 0 or self.dst[3] <= 0


@dataclass(frozen=True)
class SlicePlan:
    """一套切片：``kind`` 为 stretch/h_slice/v_slice/nine_slice。"""

    kind: str
    pieces: tuple[Piece, ...]

    def __post_init__(self) -> None:
        expected = {"stretch": 1, "h_slice": 3, "v_slice": 3, "nine_slice": 9}
        if self.kind not in expected:
            raise ValueError(f"未知切片类型：{self.kind}")
        if len(self.pieces) != expected[self.kind]:
            raise ValueError(
                f"{self.kind} 需要 {expected[self.kind]} 块，"
                f"实际 {len(self.pieces)} 块")


def stretch(piece: Piece) -> SlicePlan:
    """普通拉伸：整张图拉到控件尺寸。"""
    return SlicePlan("stretch", (piece,))


def h_slice(left: Piece, middle: Piece, right: Piece) -> SlicePlan:
    return SlicePlan("h_slice", (left, middle, right))


def v_slice(top: Piece, middle: Piece, bottom: Piece) -> SlicePlan:
    return SlicePlan("v_slice", (top, middle, bottom))


def nine_slice(pieces: tuple[Piece, ...]) -> SlicePlan:
    return SlicePlan("nine_slice", pieces)


def fixed_thirds(width: float, height: float) -> SlicePlan:
    """单图九宫格的固定三分（`.dlg` 没有切割字段，切割线是编辑器近似）。"""
    piece = Piece(float(width) / 3.0, float(height) / 3.0)
    return nine_slice((piece,) * 9)


def nine_thirds_cells(
    src_w: float, src_h: float, dst_w: float, dst_h: float
) -> tuple[tuple[tuple[float, float, float, float],
                  tuple[float, float, float, float]], ...]:
    """单图九宫格：源图固定三分，源格与目标格**按 index** 对齐。

    只按目标尺寸布局一次是不够的：源格必须始终是原图的九块三分
    （``src_w/3 × src_h/3``），而不是"按原图尺寸再布局一次"得到的
    四块半图。返回 ``[(src_rect, dst_rect), ...]``，目标过小时被压成 0
    的格子不出现在结果里。
    """
    plan = fixed_thirds(src_w, src_h)
    sources = {cell.index: cell.dst for cell in layout(plan, src_w, src_h)}
    return tuple((sources[cell.index], cell.dst)
                 for cell in layout(plan, dst_w, dst_h)
                 if cell.index in sources)


def _fit(first: float, last: float, total: float) -> tuple[float, float, float]:
    """两端固定块 + 中间剩余；总量超了就按比例缩两端。"""
    total = max(0.0, total)
    if first + last <= total:
        return first, max(0.0, total - first - last), last
    fixed = first + last
    if fixed <= 0:
        return 0.0, total, 0.0
    scale = total / fixed
    return first * scale, 0.0, last * scale


def _column_widths(pieces: tuple[Piece, ...]) -> tuple[float, float, float]:
    left = max(pieces[0].width, pieces[3].width, pieces[6].width)
    right = max(pieces[2].width, pieces[5].width, pieces[8].width)
    return float(left), 0.0, float(right)


def _row_heights(pieces: tuple[Piece, ...]) -> tuple[float, float, float]:
    top = max(pieces[0].height, pieces[1].height, pieces[2].height)
    bottom = max(pieces[6].height, pieces[7].height, pieces[8].height)
    return float(top), 0.0, float(bottom)


def _cell(index: int, piece: Piece, x: float, y: float,
          width: float, height: float) -> Cell:
    return Cell(index, (0.0, 0.0, float(piece.width), float(piece.height)),
                (x, y, width, height))


def layout(plan: SlicePlan, target_w: float, target_h: float,
           blank: frozenset[int] = frozenset()) -> tuple[Cell, ...]:
    """按 ``plan`` 把切片摆进 ``target_w``×``target_h``。

    ``blank`` 是「整块全透明」的切片下标，这些块不出 Cell（见
    :data:`BLANK_SKIP_DOC`）。
    """
    width = max(0.0, float(target_w))
    height = max(0.0, float(target_h))
    pieces = plan.pieces
    cells: list[Cell] = []
    if plan.kind == "stretch":
        cells.append(_cell(0, pieces[0], 0.0, 0.0, width, height))
    elif plan.kind == "h_slice":
        left, middle, right = _fit(
            float(pieces[0].width), float(pieces[2].width), width)
        x = 0.0
        for index, span in ((0, left), (1, middle), (2, right)):
            cells.append(_cell(index, pieces[index], x, 0.0, span, height))
            x += span
    elif plan.kind == "v_slice":
        top, middle, bottom = _fit(
            float(pieces[0].height), float(pieces[2].height), height)
        y = 0.0
        for index, span in ((0, top), (1, middle), (2, bottom)):
            cells.append(_cell(index, pieces[index], 0.0, y, width, span))
            y += span
    else:
        first, _, last = _column_widths(pieces)
        left, center_x, right = _fit(first, last, width)
        first, _, last = _row_heights(pieces)
        top, center_y, bottom = _fit(first, last, height)
        xs = (0.0, left, left + center_x)
        widths = (left, center_x, right)
        ys = (0.0, top, top + center_y)
        heights = (top, center_y, bottom)
        for row in range(3):
            for col in range(3):
                index = row * 3 + col
                cells.append(_cell(index, pieces[index], xs[col], ys[row],
                                   widths[col], heights[row]))
    return tuple(cell for cell in cells
                 if cell.index not in blank and not cell.empty)
