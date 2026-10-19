"""把普通图片编码成游戏精灵字节（与资源编辑器同一格式实现）。

供选图窗「添加新图到包 · 转成精灵图」使用：一张或多张帧图
（按文件名顺序成帧，GIF 自动展开）→ 一份游戏可读的精灵数据。
锚点与中心点都取左上角 (0, 0)，适合界面静态图与简单动画；
逐帧调整锚点的高级动画制作不在这里做。

只依赖 Pillow 做图片读取与 256 色量化；格式常量与 alpha 折算来自
共享真源 ``sprite_format``，编码规则与
``resource_editor/core/codecs/sprite.py`` 的一致性由
``tools/devkit/tests/test_sprite_parity.py`` 交叉验证（I0 优先，
单行过长自动改用 I1）。
"""
from __future__ import annotations

import re
import struct
from pathlib import Path

from PIL import Image, ImageSequence

from .errors import Cancelled, SpriteError
from .sprite_format import OPAQUE, ROW_LEN_U8_MAX, alpha_to_level

#: 兼容模块内旧名（与共享真源的 ``alpha_to_level`` 同一实现）
_alpha_to_level = alpha_to_level


def _encode_palette(magic: str,
                    palette: list[tuple[int, int, int]]) -> bytes:
    if magic == "T0":
        out = bytearray()
        for r, g, b in palette:
            out.extend((r, g, b))
        return bytes(out)
    out = bytearray()
    for r, g, b in palette:
        v = ((round(r * 31 / 255) << 11)
             | (round(g * 63 / 255) << 5)
             | round(b * 31 / 255))
        out.extend((v & 0xFF, (v >> 8) & 0xFF))
    return bytes(out)


def _build_palette(images, magic: str) -> list[tuple[int, int, int]]:
    """全部帧纵向拼图后 256 色量化；I0/I1 按 RGB565 提前取整。"""
    rgb_frames = [img.convert("RGB") for img in images]
    total_h = sum(img.height for img in rgb_frames)
    max_w = max(img.width for img in rgb_frames)
    stack = Image.new("RGB", (max_w, total_h), (0, 0, 0))
    y = 0
    for img in rgb_frames:
        stack.paste(img, (0, y))
        y += img.height
    quantized = stack.quantize(colors=256, method=Image.MEDIANCUT)
    raw = (quantized.getpalette() or []) + [0] * 768
    palette = [(raw[3 * i], raw[3 * i + 1], raw[3 * i + 2])
               for i in range(256)]
    if magic in ("I0", "I1"):  # 按 RGB565 取整，映射与存储一致
        palette = [
            (round(r * 31 / 255) * 255 // 31,
             round(g * 63 / 255) * 255 // 63,
             round(b * 31 / 255) * 255 // 31)
            for (r, g, b) in palette
        ]
    return palette


def _map_indices(image, palette) -> list[list[tuple[int, int]]]:
    """RGBA 图 → 逐行 (调色板序号, alpha 等级) 网格。"""
    rgba = image.convert("RGBA")
    width, height = rgba.size
    src = rgba.load()
    exact = {color: i for i, color in enumerate(palette)}
    nearest_cache: dict[tuple[int, int, int], int] = {}
    rows: list[list[tuple[int, int]]] = []
    for y in range(height):
        row: list[tuple[int, int]] = []
        for x in range(width):
            r, g, b, a = src[x, y]
            level = _alpha_to_level(a)
            if level == 0:
                row.append((0, 0))
                continue
            key = (r, g, b)
            idx = exact.get(key)
            if idx is None:
                idx = nearest_cache.get(key)
                if idx is None:
                    idx = min(
                        range(256),
                        key=lambda i: (palette[i][0] - r) ** 2
                        + (palette[i][1] - g) ** 2
                        + (palette[i][2] - b) ** 2,
                    )
                    nearest_cache[key] = idx
            row.append((idx, level))
        rows.append(row)
    return rows


def _encode_row(grid_row: list[tuple[int, int]]) -> bytes:
    """一行网格 → token 流（含结尾 EOL），编码法与解码端对应。"""
    out = bytearray()
    x, width = 0, len(grid_row)
    while x < width:
        idx, level = grid_row[x]
        if level == 0:  # 透明段
            run = 0
            while x + run < width and grid_row[x + run][1] == 0:
                run += 1
            if x + run >= width:
                break  # 行尾全透明，用 EOL 收尾
            step = min(run, 63)
            out.append(0xC0 | step)
            x += step
        elif level == OPAQUE:  # 不透明段
            same = 0
            while (x + same < width and grid_row[x + same][1] == OPAQUE
                   and grid_row[x + same][0] == idx):
                same += 1
            if same >= 2:  # REP
                step = min(same, 63)
                out.append(0x80 | step)
                out.append(idx)
                x += step
            else:  # LIT
                lit: list[int] = []
                while (x + len(lit) < width
                       and grid_row[x + len(lit)][1] == OPAQUE
                       and len(lit) < 63):
                    lit.append(grid_row[x + len(lit)][0])
                out.append(0x40 | len(lit))
                out.extend(lit)
                x += len(lit)
        else:  # 半透明像素
            same = 0
            while (x + same < width and grid_row[x + same][1] == level
                   and grid_row[x + same][0] == idx):
                same += 1
            if same >= 2:  # RUN
                step = min(same, 31)
                out.append(step)
                out.append(level)
                out.append(idx)
                x += step
            else:  # SINGLE
                out.append(0x20 | level)
                out.append(idx)
                x += 1
    out.append(0x00)
    return bytes(out)


def encode_frames(images, magic: str = "I0") -> bytes:
    """一组 PIL 帧图 → 精灵字节（画布=最大帧尺寸，锚点左上）。"""
    if magic not in ("I0", "T0", "I1"):
        raise SpriteError(f"未知精灵魔数：{magic}")
    if not images:
        raise SpriteError("没有可编码的帧图")
    palette = _build_palette(images, magic)
    canvas_w = max(img.width for img in images)
    canvas_h = max(img.height for img in images)
    frames_meta: list[tuple[int, int, int, int]] = []
    frames_rows: list[list[bytes]] = []
    for img in images:
        rows = [_encode_row(row) for row in _map_indices(img, palette)]
        if magic != "I1":
            for row in rows:
                if len(row) > ROW_LEN_U8_MAX:
                    raise SpriteError(
                        f"单行编码 {len(row)} 字节超过 I0/T0 的行长上限")
        frames_meta.append((0, 0, img.width, img.height))
        frames_rows.append(rows)
    out = bytearray()
    out.extend(struct.pack(
        "<2sHHHHHH", magic.encode("ascii"), 1, len(images),
        canvas_w, canvas_h, 0, 0))
    for meta in frames_meta:
        out.extend(struct.pack("<HHHH", *meta))
    out.extend(struct.pack(
        "<I", sum(len(rows) for rows in frames_rows)))  # 总行数
    len_fmt = "<H" if magic == "I1" else "<B"
    body = bytearray()
    all_lens: list[int] = []
    for rows in frames_rows:
        frame_len = sum(len(r) for r in rows)
        pad = (-frame_len) % 4
        for ri, row in enumerate(rows):
            extra = pad if ri == len(rows) - 1 else 0
            all_lens.append(len(row) + extra)
            body.extend(row)
            body.extend(b"\x00" * extra)
    for length in all_lens:
        out.extend(struct.pack(len_fmt, length))
    out.extend(_encode_palette(magic, palette))
    out.extend(body)
    return bytes(out)


def _natural_key(name: str):
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r"(\d+)", name)]


def load_frame_files(paths, *, progress=None, cancelled=None) -> list:
    """按文件名自然序读帧图（01、02…），GIF 展开为多帧。

    ``progress(done, total, text)``/``cancelled()`` 供批量转精灵走
    忙碌遮罩；取消时抛 :class:`~ui_editor.core.errors.Cancelled`。
    """
    frames = []
    ordered = sorted((Path(p) for p in paths),
                       key=lambda p: _natural_key(p.name))
    total = len(ordered)
    for done, path in enumerate(ordered, 1):
        if cancelled is not None and cancelled():
            raise Cancelled("转精灵已取消")
        if progress is not None:
            progress(done - 1, total,
                     f"读取帧 {path.name}（{done}/{total}）…")
        try:
            with Image.open(path) as img:
                if getattr(img, "is_animated", False):
                    for frame in ImageSequence.Iterator(img):
                        frames.append(frame.convert("RGBA"))
                else:
                    frames.append(img.convert("RGBA"))
        except Exception as exc:
            raise SpriteError(f"读取图片 {path.name} 失败：{exc}") from exc
    if not frames:
        raise SpriteError("没有读到任何帧图")
    return frames


def sprite_bytes_from_files(paths, *, progress=None,
                            cancelled=None) -> tuple[bytes, int]:
    """文件列表 → (精灵字节, 帧数)。行过长自动退到 I1 格式。

    ``progress``/``cancelled`` 作用于逐帧读取阶段（编码阶段很短）。
    """
    frames = load_frame_files(paths, progress=progress, cancelled=cancelled)
    try:
        return encode_frames(frames, "I0"), len(frames)
    except SpriteError:
        return encode_frames(frames, "I1"), len(frames)
