"""画布吸附与对齐的纯计算（不依赖 Qt，M3.1）。

矩形一律用 (x, y, w, h) 表示、同一父坐标系内比较；拖动控件时
把它的左/右/水平中线去贴同级控件与父容器边缘，贴中返回参考线
位置供画布描红线；对齐/分布直接算出各控件的新坐标。
"""
from __future__ import annotations

Rect = tuple[float, float, float, float]


def _anchors_x(rect: Rect) -> tuple[float, float, float]:
    x, _y, w, _h = rect
    return (x, x + w, x + w / 2)


def _anchors_y(rect: Rect) -> tuple[float, float, float]:
    _x, y, _w, h = rect
    return (y, y + h, y + h / 2)


def snap_position(moving: Rect, others: list[Rect],
                  parent_size: tuple[float, float] | None,
                  threshold: float,
                  ) -> tuple[float, float, list[float], list[float]]:
    """求拖动后坐标与命中的参考线。

    返回 (新x, 新y, 竖参考线xs, 横参考线ys)，参考线在同一父坐标
    系内。各方向独立取阈值内最近的一条；父容器边缘（0 与宽高）
    也参与吸附。
    """
    x, y, w, h = moving

    def snap_axis(pos: float, size: float, targets, parent_pairs):
        # 候选 (距离, 优先级, 新坐标, 参考线)：边缘优先于中线
        candidates = []
        anchors = [(pos, 0), (pos + size, 0), (pos + size / 2, 1)]
        for target_value, target_prio in targets:
            for anchor_value, anchor_prio in anchors:
                delta = target_value - anchor_value
                if abs(delta) <= threshold:
                    candidates.append((abs(delta), anchor_prio + target_prio,
                                       pos + delta, target_value))
        for anchor_value, target_value in parent_pairs:
            delta = target_value - anchor_value
            if abs(delta) <= threshold:
                candidates.append((abs(delta), 0, pos + delta, target_value))
        if not candidates:
            return pos, None
        candidates.sort(key=lambda c: (c[0], c[1]))
        _dist, _prio, new_pos, line = candidates[0]
        return new_pos, line

    def axis_targets(rects, is_x):
        targets = []
        for rect in rects:
            values = _anchors_x(rect) if is_x else _anchors_y(rect)
            targets.extend([(values[0], 0), (values[1], 0), (values[2], 1)])
        return targets

    parent_x = parent_y = []
    if parent_size is not None:
        pw, ph = parent_size
        parent_x = [(x, 0.0), (x + w, float(pw))]
        parent_y = [(y, 0.0), (y + h, float(ph))]
    new_x, line_x = snap_axis(x, w, axis_targets(others, True), parent_x)
    new_y, line_y = snap_axis(y, h, axis_targets(others, False), parent_y)
    guides_x = [line_x] if line_x is not None else []
    guides_y = [line_y] if line_y is not None else []
    return new_x, new_y, guides_x, guides_y


def align_position(reference: Rect, target: Rect, mode: str,
                   ) -> tuple[float, float]:
    """以 reference 为基准算 target 在 mode 下的新坐标。"""
    rx, ry, rw, rh = reference
    x, y, w, h = target
    if mode == "left":
        x = rx
    elif mode == "hcenter":
        x = rx + (rw - w) / 2
    elif mode == "right":
        x = rx + rw - w
    elif mode == "top":
        y = ry
    elif mode == "vcenter":
        y = ry + (rh - h) / 2
    elif mode == "bottom":
        y = ry + rh - h
    else:
        raise ValueError(f"未知对齐方式：{mode}")
    return x, y


def distribute_positions(rects: list[Rect], axis: str,
                         ) -> list[tuple[float, float]]:
    """三者以上等间距分布：首尾不动，中间按等间隔排。

    axis="x" 横向（按 x 排序），axis="y" 纵向。返回与输入同序的
    新坐标列表；不足三个时原样返回。
    """
    if len(rects) < 3:
        return [(r[0], r[1]) for r in rects]
    order = sorted(range(len(rects)),
                   key=lambda i: rects[i][0] if axis == "x" else rects[i][1])
    sorted_rects = [rects[i] for i in order]

    def pos(r: Rect) -> float:
        return r[0] if axis == "x" else r[1]

    def size(r: Rect) -> float:
        return r[2] if axis == "x" else r[3]

    start = pos(sorted_rects[0])
    end = pos(sorted_rects[-1]) + size(sorted_rects[-1])
    total_size = sum(size(r) for r in sorted_rects)
    gap = (end - start - total_size) / (len(rects) - 1)
    result: list[tuple[float, float]] = [(r[0], r[1]) for r in rects]
    cursor = start
    for idx, rect in zip(order, sorted_rects, strict=True):
        if axis == "x":
            result[idx] = (cursor, rect[1])
        else:
            result[idx] = (rect[0], cursor)
        cursor += size(rect) + gap
    return result


def clamp_in_parent(box: tuple[int, int] | None, x: float, y: float,
                    width: int, height: int) -> tuple[float, float, bool]:
    """把坐标夹回父矩形，返回 (x, y, 是否被夹)。

    ``box`` 为父的有效像素尺寸；None 表示顶级控件（没有父框，不夹）。
    父某一维 <=0 表示尺寸未知，该维只保证非负，不按未知尺寸硬夹。
    """
    if box is None:
        return x, y, False
    box_w, box_h = box
    cx, cy = x, y
    if box_w > 0:
        cx = min(max(x, 0.0), max(0.0, box_w - width))
    else:
        cx = max(x, 0.0)
    if box_h > 0:
        cy = min(max(y, 0.0), max(0.0, box_h - height))
    else:
        cy = max(y, 0.0)
    clamped = (cx != x) or (cy != y)
    return cx, cy, clamped
