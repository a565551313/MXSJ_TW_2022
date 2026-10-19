"""``I0`` / ``T0`` / ``I1`` / ``T1`` / ``T4`` / ``T5`` 精灵解码（输出逐帧 RGBA 字节）。

格式已经字节级验证（见仓库 ``tools/data-parser/i0_sprite.py``），
此处移植为不依赖 Pillow 的实现，解码结果直接喂 ``QImage``。

布局：14 字节头 ``<2sHHHHHH``（魔数、版本、帧数、画布宽高、中心
点）；帧目录每帧 ``<HHHH``（关键点 x/y、帧宽高）；u32 总行数；
行长表（I0/T0/T4 每行 u8，I1/T1/T5 每行 u16）；调色板（T0/T1 为
256×RGB888，I0/I1 为 256×RGB565；T4/T5 无调色板，行内 token
后跟 3 字节 RGB 真彩像素，2026-10-14 在真实 item.fls 上定版）；
随后是逐帧逐行的 RLE 像素流（每帧数据按 4 字节对齐，填充计入
末行长度）。

行内算子（低位为计数/等级）：``0x00`` 行尾；``0x01–0x1F`` RUN
（半透明色块）；``0x20–0x3F`` SINGLE（单像素半透明）；
``0x40–0x7F`` LIT（不透明字面序列）；``0x80–0xBF`` REP（不透明
单色重复）；``0xC0–0xFF`` SKIP（透明跳过）。透明等级 5 位，
``alpha8 = level * 255 // 31``。

魔数表、行长表规律与 alpha 折算来自共享真源 ``sprite_format``
（生成副本见本文件所在目录，改真源才是改这里）；本模块只保留
「解码成 RGBA 字节」这一落点，与资源编辑器的 Pillow 落点由
``tools/devkit/tests/test_sprite_parity.py`` 交叉验证。
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

from .errors import SpriteError
from .sprite_format import DIRECT_MAGICS, MAGICS, is_sprite

__all__ = ["SpriteFrame", "Sprite", "is_sprite", "decode_sprite",
           "MAGICS", "DIRECT_MAGICS"]


@dataclass
class SpriteFrame:
    """一帧已解码图像：帧内尺寸 + 行主序 RGBA 字节。"""

    width: int
    height: int
    rgba: bytes


@dataclass
class Sprite:
    """一个精灵：元信息 + 全部帧。"""

    magic: str
    frame_count: int
    canvas_w: int
    canvas_h: int
    frames: list[SpriteFrame]


class _SpriteParser:
    def __init__(self, data: bytes) -> None:
        if not is_sprite(data):
            raise SpriteError("不是 I0/T0/I1/T4/T5 精灵")
        self.data = data
        self.direct = data[:2] in DIRECT_MAGICS
        (self.magic, _ver, self.frame_count, self.canvas_w, self.canvas_h,
         _cx, _cy) = struct.unpack_from("<2sHHHHHH", data, 0)
        off = 14
        self.frame_dims: list[tuple[int, int, int, int]] = []
        for _ in range(self.frame_count):
            self.frame_dims.append(struct.unpack_from("<HHHH", data, off))
            off += 8
        total_lines = struct.unpack_from("<I", data, off)[0]
        off += 4
        if total_lines != sum(f[3] for f in self.frame_dims):
            raise SpriteError("总行数与帧高之和不一致")
        len_size = 2 if self.magic in (b"I1", b"T1", b"T5") else 1
        fmt = "<H" if len_size == 2 else "<B"
        self.lens = [
            struct.unpack_from(fmt, data, off + i * len_size)[0]
            for i in range(total_lines)
        ]
        off += total_lines * len_size
        pal_size = (0 if self.direct
                    else (768 if self.magic in (b"T0", b"T1") else 512))
        if off + pal_size > len(data):
            raise SpriteError("调色板越界")
        self.palette = ([] if self.direct
                        else self._decode_palette(data[off:off + pal_size]))
        off += pal_size
        self.rows_offset = off

    def _decode_palette(self, pal: bytes) -> list[tuple[int, int, int]]:
        if self.magic in (b"T0", b"T1"):
            return [(pal[3 * i], pal[3 * i + 1], pal[3 * i + 2])
                    for i in range(256)]
        colors = []
        for i in range(256):  # RGB565 小端
            v = pal[2 * i] | (pal[2 * i + 1] << 8)
            colors.append((((v >> 11) & 0x1F) * 255 // 31,
                           ((v >> 5) & 0x3F) * 255 // 63,
                           (v & 0x1F) * 255 // 31))
        return colors

    def frame_rows(self) -> list[list[bytes]]:
        """逐帧切出原始行字节。"""
        data = self.data
        pos = self.rows_offset
        line_no = 0
        result: list[list[bytes]] = []
        for (_kx, _ky, _fw, fh) in self.frame_dims:
            rows = []
            for _ in range(fh):
                n = self.lens[line_no]
                rows.append(data[pos:pos + n])
                pos += n
                line_no += 1
            result.append(rows)
        return result


def _decode_row(line: bytes, width: int) -> list[tuple[int, int]]:
    """解一行，返回 [(调色板索引, alpha8), ...]，不足行宽由调用方透空。"""
    px: list[tuple[int, int]] = []
    i, n = 0, len(line)
    while i < n and len(px) < width:
        b = line[i]
        i += 1
        if b == 0x00:  # 行尾
            break
        elif b < 0x20:  # RUN：计数像素同一（索引, alpha）
            if i + 1 >= n:
                break
            cnt = b & 0x1F
            alpha = line[i] * 255 // 31
            idx = line[i + 1]
            i += 2
            px.extend([(idx, alpha)] * min(cnt, width - len(px)))
        elif b < 0x40:  # SINGLE：单像素半透明
            if i >= n:
                break
            px.append((line[i], (b & 0x1F) * 255 // 31))
            i += 1
        elif b < 0x80:  # LIT：不透明索引序列
            for _ in range(b & 0x3F):
                if i >= n:
                    break
                if len(px) < width:
                    px.append((line[i], 255))
                i += 1
        elif b < 0xC0:  # REP：不透明单色重复
            if i >= n:
                break
            cnt = b & 0x3F
            px.extend([(line[i], 255)] * min(cnt, width - len(px)))
            i += 1
        else:  # SKIP：透明像素
            px.extend([(0, 0)] * min(b & 0x3F, width - len(px)))
    return px


def _decode_row_direct(
    line: bytes, width: int
) -> list[tuple[tuple[int, int, int], int]]:
    """解真彩（T4/T5）一行，返回 [((r, g, b), alpha8), ...]。

    算子与调色板版一一对应，只是索引字节换成 3 字节 RGB。
    """
    px: list[tuple[tuple[int, int, int], int]] = []
    i, n = 0, len(line)
    while i < n and len(px) < width:
        b = line[i]
        i += 1
        if b == 0x00:  # 行尾
            break
        elif b < 0x20:  # RUN：cnt, alpha, RGB
            if i + 3 >= n:
                break
            cnt = b & 0x1F
            alpha = line[i] * 255 // 31
            color = (line[i + 1], line[i + 2], line[i + 3])
            i += 4
            px.extend([(color, alpha)] * min(cnt, width - len(px)))
        elif b < 0x40:  # SINGLE：RGB，alpha 在 token 内
            if i + 2 >= n:
                break
            px.append(((line[i], line[i + 1], line[i + 2]),
                       (b & 0x1F) * 255 // 31))
            i += 3
        elif b < 0x80:  # LIT：不透明 RGB 序列
            for _ in range(b & 0x3F):
                if i + 2 >= n:
                    break
                if len(px) < width:
                    px.append(((line[i], line[i + 1], line[i + 2]), 255))
                i += 3
        elif b < 0xC0:  # REP：不透明单色重复
            if i + 2 >= n:
                break
            cnt = b & 0x3F
            color = (line[i], line[i + 1], line[i + 2])
            px.extend([(color, 255)] * min(cnt, width - len(px)))
            i += 3
        else:  # SKIP：透明像素
            px.extend([((0, 0, 0), 0)] * min(b & 0x3F, width - len(px)))
    return px


def decode_sprite(data: bytes) -> Sprite:
    """把精灵字节解码为逐帧 RGBA，失败抛 :class:`SpriteError`。"""
    parser = _SpriteParser(data)
    frames: list[SpriteFrame] = []
    all_rows = parser.frame_rows()
    for fi, (_kx, _ky, fw, fh) in enumerate(parser.frame_dims):
        buf = bytearray(fw * fh * 4)
        for y, line in enumerate(all_rows[fi]):
            base = y * fw * 4
            if parser.direct:
                row = _decode_row_direct(line, fw)
            else:
                row = [((parser.palette[idx]), alpha)
                       for idx, alpha in _decode_row(line, fw)]
            for x, ((r, g, b), alpha) in enumerate(row):
                if alpha:
                    off = base + x * 4
                    buf[off] = r
                    buf[off + 1] = g
                    buf[off + 2] = b
                    buf[off + 3] = alpha
        frames.append(SpriteFrame(fw, fh, bytes(buf)))
    return Sprite(parser.magic.decode("ascii"), parser.frame_count,
                  parser.canvas_w, parser.canvas_h, frames)
