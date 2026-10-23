"""8-directional ``CAStar`` pathfinder & walkability connectivity analyzer.

Reproduces ``mx.exe``'s 8-directional ``CAStar`` grid search (``0x4bac30``):
* Cardinal step cost ``10``, diagonal step cost ``14``;
* Octile heuristic ``10 * max(dx, dy) + 4 * min(dx, dy)``;
* Walkable cells satisfy ``(cell & 1) == 0`` (both ``0`` normal walkable and ``2``
  shaded walkable).
"""
from __future__ import annotations

import heapq
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

_NEIGHBORS_8 = (
    (1, 0, 10),
    (-1, 0, 10),
    (0, 1, 10),
    (0, -1, 10),
    (1, 1, 14),
    (1, -1, 14),
    (-1, 1, 14),
    (-1, -1, 14),
)


@dataclass(frozen=True, slots=True)
class PathResult:
    found: bool
    cells: tuple[tuple[int, int], ...]
    cost: int
    explored: int

    @property
    def pixel_centers(self) -> list[tuple[int, int]]:
        return [(cx * 20 + 10, cy * 20 + 10) for cx, cy in self.cells]


def _octile(ax: int, ay: int, bx: int, by: int) -> int:
    dx = abs(ax - bx)
    dy = abs(ay - by)
    return 10 * max(dx, dy) + 4 * min(dx, dy)


def find_path(
    cols: int,
    rows: int,
    walkable_at: Callable[[int, int], bool],
    start: tuple[int, int],
    goal: tuple[int, int],
    *,
    max_expansions: int = 250_000,
) -> PathResult:
    """Find an optimal 8-directional path between cell ``start`` and ``goal``."""
    sx, sy = start
    gx, gy = goal
    if not (0 <= sx < cols and 0 <= sy < rows and 0 <= gx < cols and 0 <= gy < rows):
        return PathResult(False, (), 0, 0)
    if not walkable_at(sx, sy) or not walkable_at(gx, gy):
        return PathResult(False, (), 0, 0)
    if (sx, sy) == (gx, gy):
        return PathResult(True, ((sx, sy),), 0, 1)

    start_idx = sy * cols + sx
    goal_idx = gy * cols + gx
    inf = 1 << 60
    g_score: dict[int, int] = {start_idx: 0}
    came_from: dict[int, int] = {}
    open_heap: list[tuple[int, int, int]] = [(_octile(sx, sy, gx, gy), 0, start_idx)]
    closed: set[int] = set()
    explored = 0

    while open_heap and explored < max_expansions:
        _f, g, cur = heapq.heappop(open_heap)
        if cur in closed:
            continue
        closed.add(cur)
        explored += 1
        if cur == goal_idx:
            chain: list[tuple[int, int]] = []
            node = cur
            while True:
                chain.append((node % cols, node // cols))
                if node == start_idx:
                    break
                node = came_from[node]
            chain.reverse()
            return PathResult(True, tuple(chain), g, explored)

        cx, cy = cur % cols, cur // cols
        for dx, dy, step_cost in _NEIGHBORS_8:
            nx, ny = cx + dx, cy + dy
            if not (0 <= nx < cols and 0 <= ny < rows):
                continue
            nidx = ny * cols + nx
            if nidx in closed or not walkable_at(nx, ny):
                continue
            tentative = g + step_cost
            if tentative < g_score.get(nidx, inf):
                g_score[nidx] = tentative
                came_from[nidx] = cur
                f_score = tentative + _octile(nx, ny, gx, gy)
                heapq.heappush(open_heap, (f_score, tentative, nidx))

    return PathResult(False, (), 0, explored)


def analyze_walkability(
    cols: int,
    rows: int,
    cell_at: Callable[[int, int], int],
) -> dict:
    """Compute cell histogram and 8-connected walkable islands across the map."""
    total = cols * rows
    hist = {0: 0, 1: 0, 2: 0, 3: 0, "other": 0}
    walkable_mask = bytearray(total)
    for cy in range(rows):
        base = cy * cols
        for cx in range(cols):
            v = cell_at(cx, cy)
            if v in (0, 1, 2, 3):
                hist[v] += 1
            else:
                hist["other"] += 1
            if (v & 1) == 0:
                walkable_mask[base + cx] = 1

    visited = bytearray(total)
    component_sizes: list[int] = []
    for idx in range(total):
        if not walkable_mask[idx] or visited[idx]:
            continue
        visited[idx] = 1
        q = deque([idx])
        size = 0
        while q:
            cur = q.popleft()
            size += 1
            cx, cy = cur % cols, cur // cols
            for dx, dy, _ in _NEIGHBORS_8:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < cols and 0 <= ny < rows:
                    nidx = ny * cols + nx
                    if walkable_mask[nidx] and not visited[nidx]:
                        visited[nidx] = 1
                        q.append(nidx)
        component_sizes.append(size)

    component_sizes.sort(reverse=True)
    walkable_total = hist[0] + hist[2]
    largest = component_sizes[0] if component_sizes else 0
    return {
        "total_cells": total,
        "walkable_cells": walkable_total,
        "blocked_cells": hist[1] + hist[3],
        "shaded_cells": hist[2] + hist[3],
        "histogram": hist,
        "walkable_ratio": round(walkable_total / total, 4) if total else 0.0,
        "island_count": len(component_sizes),
        "largest_island_cells": largest,
        "isolated_walkable_cells": walkable_total - largest,
        "island_sizes_top5": component_sizes[:5],
    }


__all__ = ["PathResult", "analyze_walkability", "find_path"]
