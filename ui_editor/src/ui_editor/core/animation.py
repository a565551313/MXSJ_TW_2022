"""UI 动画资源模型（纯数据层）。

``.spr`` 保存帧号和时长，像素帧由同名精灵或外部资源提供。这里不把
帧号压成列表下标，避免非连续帧号在画布预览和导出时丢失原生语义。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AnimationFrame:
    """一帧的原生编号、持续 tick 和已解码像素（可能为空）。"""

    frame_id: int
    duration: int
    image: Any


@dataclass(frozen=True)
class AnimationAsset:
    """一份可供画布/导出的动画资源。"""

    source: str
    frames: tuple[AnimationFrame, ...]
    package: str = ""
    branch: str = ""

    @property
    def complete(self) -> bool:
        """是否每一条帧记录都找到了像素。"""
        return bool(self.frames) and all(
            frame.image is not None for frame in self.frames)

    @property
    def images(self) -> tuple[Any, ...]:
        """按 .spr 原始帧表顺序返回图像；缺帧保留为 None。"""
        return tuple(frame.image for frame in self.frames)

    def frame(self, index: int) -> AnimationFrame | None:
        if 0 <= index < len(self.frames):
            return self.frames[index]
        return None


def build_animation(
    source: str,
    table: tuple[tuple[int, int], ...],
    images: list[Any],
    *,
    package: str = "",
    branch: str = "",
) -> AnimationAsset:
    """把帧表和精灵像素绑定。

    官服多数资源用帧号作为精灵数组下标；超出像素数组范围的帧号保留为
    缺失帧，不能按列表顺序猜测，否则会把动画显示成另一帧。
    """
    rows: list[AnimationFrame] = []
    for frame_id, duration in table:
        image = images[frame_id] if 0 <= frame_id < len(images) else None
        rows.append(AnimationFrame(frame_id, max(0, duration), image))
    if not rows:
        rows = [AnimationFrame(index, 0, image)
                for index, image in enumerate(images)]
    return AnimationAsset(source, tuple(rows), package, branch)
