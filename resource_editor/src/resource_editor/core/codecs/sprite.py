"""I0 / T0 / I1 / T4 / T5 精灵编解码。

格式规格见 ``tools/data-parser/I0_SPRITE_FORMAT.md``，I0/T0/I1
解码已对全部 807 个精灵字节级验证。T4/T5 是 2026-10-14 在真实
``item.fls`` 样本上定版的真彩变体：无调色板，行内 token 之后跟
的不是调色板索引而是 3 字节 RGB；行长 T4 用 u8、T5 用 u16。
编码器为其逆过程：

* 调色板：可沿用原精灵调色板（颜色最近邻映射），或从新图新建
  256 色（Pillow 中位切分量化）；I0/I1 量化到 RGB565，T0 保持 RGB888。
* alpha：不透明走 LIT/REP，半透明量化到 31 级走 SINGLE/RUN，
  全透明走 SKIP/EOL。
* 逐行生成 token（计数上限 LIT/REP/SKIP 63、RUN 31，自动切分），
  每帧尾部补齐 4 字节对齐（计入末行行长）。
* I0/T0 行长为 u8：任一行超过 255 字节抛 :class:`EncodeError`。

魔数表与 alpha 折算来自共享真源 ``core/sprite_format``（副本由
``tools/devkit/vendor_core.py`` 生成）；本模块是「Pillow 落点」，
与 UI 编辑器的 RGBA 落点由 ``tools/devkit/tests/test_sprite_parity.py``
交叉验证。
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

from PIL import Image

from ..errors import CodecError, EncodeError
from ..sprite_format import (
    DIRECT_MAGICS,
    MAGICS,
    OPAQUE,
    alpha_to_level,
    is_sprite,
    level_to_alpha,
)

# 兼容旧引用（``codecs/detect.py`` 用 SPRITE_MAGICS，模块内仍叫旧名）
SPRITE_MAGICS = MAGICS
_level_to_alpha = level_to_alpha
_alpha_to_level = alpha_to_level


@dataclass
class Sprite:
    """解码后的精灵：头信息、帧目录、调色板与逐帧行字节。"""

    magic: str
    version: int
    canvas_w: int
    canvas_h: int
    center_x: int
    center_y: int
    frames: list[tuple[int, int, int, int]]  # (key_x, key_y, w, h)
    palette: list[tuple[int, int, int]]
    frame_rows: list[list[bytes]] = field(default_factory=list)
    direct: bool = False  # T4/T5：像素为 3 字节 RGB，无调色板

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    def frame_offset(self, fi: int) -> tuple[int, int]:
        """帧 fi 左上角在画布上的坐标。"""
        kx, ky, _fw, _fh = self.frames[fi]
        return (self.center_x - kx, self.center_y - ky)

    @staticmethod
    def _decode_row(line: bytes, width: int) -> list[tuple[int, int]]:
        """解一行 token 流为 (palette_index, alpha8) 列表。"""
        px: list[tuple[int, int]] = []
        i, n = 0, len(line)
        while i < n and len(px) < width:
            b = line[i]
            i += 1
            if b == 0x00:  # 行结束
                break
            if b < 0x20:  # RUN：cnt, alpha, index
                cnt = b & 0x1F
                alpha = _level_to_alpha(line[i])
                idx = line[i + 1]
                i += 2
                px.extend([(idx, alpha)] * min(cnt, width - len(px)))
            elif b < 0x40:  # SINGLE：index，alpha 在 token 内
                px.append((line[i], _level_to_alpha(b & 0x1F)))
                i += 1
            elif b < 0x80:  # LIT：cnt 个不透明索引
                for _ in range(b & 0x3F):
                    if len(px) < width:
                        px.append((line[i], OPAQUE))
                    i += 1
            elif b < 0xC0:  # REP：cnt 个同色不透明像素
                cnt = b & 0x3F
                px.extend([(line[i], OPAQUE)] * min(cnt, width - len(px)))
                i += 1
            else:  # SKIP：cnt 个透明像素
                px.extend([(0, 0)] * min(b & 0x3F, width - len(px)))
        return px

    @staticmethod
    def _decode_row_direct(
        line: bytes, width: int
    ) -> list[tuple[tuple[int, int, int], int]]:
        """解真彩（T4/T5）一行 token 流为 ((r, g, b), alpha8) 列表。

        与调色板版算子一一对应，只是索引字节换成 3 字节 RGB。
        """
        px: list[tuple[tuple[int, int, int], int]] = []
        i, n = 0, len(line)
        while i < n and len(px) < width:
            b = line[i]
            i += 1
            if b == 0x00:  # 行结束
                break
            if b < 0x20:  # RUN：cnt, alpha, RGB
                cnt = b & 0x1F
                alpha = _level_to_alpha(line[i])
                color = (line[i + 1], line[i + 2], line[i + 3])
                i += 4
                px.extend([(color, alpha)] * min(cnt, width - len(px)))
            elif b < 0x40:  # SINGLE：RGB，alpha 在 token 内
                color = (line[i], line[i + 1], line[i + 2])
                px.append((color, _level_to_alpha(b & 0x1F)))
                i += 3
            elif b < 0x80:  # LIT：cnt 个不透明 RGB
                for _ in range(b & 0x3F):
                    if len(px) < width:
                        px.append(((line[i], line[i + 1], line[i + 2]),
                                   OPAQUE))
                    i += 3
            elif b < 0xC0:  # REP：cnt 个同色不透明像素
                cnt = b & 0x3F
                color = (line[i], line[i + 1], line[i + 2])
                px.extend([(color, OPAQUE)] * min(cnt, width - len(px)))
                i += 3
            else:  # SKIP：cnt 个透明像素
                px.extend([((0, 0, 0), 0)]
                          * min(b & 0x3F, width - len(px)))
        return px

    def render_frame(self, fi: int) -> Image.Image:
        """渲染单帧为 RGBA 图（帧本地尺寸）。"""
        _kx, _ky, fw, fh = self.frames[fi]
        img = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        pix = img.load()
        pal = self.palette
        for y, line in enumerate(self.frame_rows[fi]):
            if self.direct:
                for x, ((r, g, b), a) in enumerate(
                        self._decode_row_direct(line, fw)):
                    if a:
                        pix[x, y] = (r, g, b, a)
                continue
            for x, (idx, a) in enumerate(self._decode_row(line, fw)):
                if a:
                    r, g, b = pal[idx]
                    pix[x, y] = (r, g, b, a)
        return img

    def render_canvas_frame(self, fi: int) -> Image.Image:
        """把帧 fi 按锚点合成到整张画布上。"""
        canvas = Image.new("RGBA", (self.canvas_w, self.canvas_h), (0, 0, 0, 0))
        frame = self.render_frame(fi)
        canvas.paste(frame, self.frame_offset(fi), frame)
        return canvas


def decode_sprite(data: bytes) -> Sprite:
    """解析精灵字节，失败抛 :class:`CodecError`。"""
    if not is_sprite(data):
        raise CodecError("不是 I0/T0/I1 精灵数据")
    magic = data[:2].decode("ascii")
    try:
        (_m, version, nfr, w, h, cx, cy) = struct.unpack_from("<2sHHHHHH", data, 0)
        frames = []
        off = 14
        for _ in range(nfr):
            frames.append(struct.unpack_from("<HHHH", data, off))
            off += 8
        total_lines = struct.unpack_from("<I", data, off)[0]
        off += 4
    except struct.error as exc:
        raise CodecError(f"精灵头解析失败：{exc}") from exc
    if total_lines != sum(f[3] for f in frames):
        raise CodecError("totalLines 与帧高之和不符")
    len_fmt = "<H" if magic in ("I1", "T5") else "<B"
    len_size = struct.calcsize(len_fmt)
    lens = [
        struct.unpack_from(len_fmt, data, off + i * len_size)[0]
        for i in range(total_lines)
    ]
    off += total_lines * len_size
    direct = data[:2] in DIRECT_MAGICS
    pal_size = 0 if direct else (768 if magic == "T0" else 512)
    pal_raw = data[off:off + pal_size]
    if len(pal_raw) < pal_size:
        raise CodecError("调色板数据不完整")
    off += pal_size
    palette = [] if direct else _decode_palette(magic, pal_raw)
    frame_rows: list[list[bytes]] = []
    pos = off
    li = 0
    for (_kx, _ky, _fw, fh) in frames:
        rows = []
        for _ in range(fh):
            rows.append(data[pos:pos + lens[li]])
            pos += lens[li]
            li += 1
        frame_rows.append(rows)
    if pos != len(data):
        raise CodecError(f"精灵长度不符：解析到 {pos}，实际 {len(data)}")
    return Sprite(
        magic=magic, version=version, canvas_w=w, canvas_h=h,
        center_x=cx, center_y=cy, frames=frames,
        palette=palette, frame_rows=frame_rows, direct=direct,
    )


def _decode_palette(magic: str, pal_raw: bytes) -> list[tuple[int, int, int]]:
    if magic == "T0":
        return [
            (pal_raw[3 * i], pal_raw[3 * i + 1], pal_raw[3 * i + 2])
            for i in range(256)
        ]
    colors = []
    for i in range(256):  # RGB565 小端
        v = pal_raw[2 * i] | (pal_raw[2 * i + 1] << 8)
        colors.append((((v >> 11) & 0x1F) * 255 // 31,
                       ((v >> 5) & 0x3F) * 255 // 63,
                       (v & 0x1F) * 255 // 31))
    return colors


def _encode_palette(magic: str, palette: list[tuple[int, int, int]]) -> bytes:
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


# ------------------------------------------------------------ 编码 ----

@dataclass
class EncodeReport:
    """编码往返误差统计（新字节重新解码后与源图比对）。"""

    max_rgb_error: int = 0
    mean_rgb_error: float = 0.0
    max_alpha_error: int = 0
    pixels_over_tolerance: int = 0
    total_pixels: int = 0


def build_palette(
    images: list[Image.Image],
    magic: str,
    base_palette: list[tuple[int, int, int]] | None = None,
) -> list[tuple[int, int, int]]:
    """为一组 RGBA 图准备 256 色调色板。

    给定 ``base_palette`` 时原样沿用（配合最近邻映射可让原有颜色
    零误差）；否则把所有帧纵向拼图后做 256 色量化。
    I0/I1 的调色板最终会取整到 RGB565，返回时已按取整后的值给出。
    """
    if base_palette is not None:
        palette = list(base_palette[:256])
        palette += [(0, 0, 0)] * (256 - len(palette))
    else:
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
        palette = [
            (raw[3 * i], raw[3 * i + 1], raw[3 * i + 2]) for i in range(256)
        ]
    if magic in ("I0", "I1"):  # 提前按 RGB565 取整，保证映射与存储一致
        palette = [
            (round(r * 31 / 255) * 255 // 31,
             round(g * 63 / 255) * 255 // 63,
             round(b * 31 / 255) * 255 // 31)
            for (r, g, b) in palette
        ]
    return palette


def _map_indices(
    image: Image.Image, palette: list[tuple[int, int, int]]
) -> list[list[tuple[int, int]]]:
    """把 RGBA 图映射为逐行 (palette_index, alpha_level) 网格。

    alpha_level 为 0 表示透明、OPAQUE(255) 表示不透明、其余为
    1-30 的半透明等级。不透明判定与 alpha 等级只看 A 通道。
    """
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
    """把一行 (index, level) 网格编码为 token 流（含结尾 EOL）。"""
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
            if same >= 2:  # REP 更省
                step = min(same, 63)
                out.append(0x80 | step)
                out.append(idx)
                x += step
            else:  # LIT：收集连续不透明像素
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
            if same >= 2:  # RUN：cnt, alpha, index
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


def encode_sprite(
    images: list[Image.Image],
    keys: list[tuple[int, int]],
    canvas_w: int,
    canvas_h: int,
    center_x: int,
    center_y: int,
    magic: str = "I0",
    base_palette: list[tuple[int, int, int]] | None = None,
) -> tuple[bytes, list[tuple[int, int, int]], EncodeReport]:
    """把一组帧图编码为精灵字节。

    返回 ``(精灵字节, 实际使用调色板, 往返误差报告)``。
    ``keys`` 为每帧的 (key_x, key_y) 锚点偏移，与 images 一一对应。
    """
    if magic not in ("I0", "T0", "I1"):
        raise EncodeError(f"未知精灵魔数：{magic}")
    if not images or len(images) != len(keys):
        raise EncodeError("帧图与锚点数量不一致")
    palette = build_palette(images, magic, base_palette)
    frames_meta: list[tuple[int, int, int, int]] = []
    frames_rows: list[list[bytes]] = []
    for img, (kx, ky) in zip(images, keys, strict=True):
        grid = _map_indices(img, palette)
        rows = [_encode_row(row) for row in grid]
        if magic != "I1":
            for row in rows:
                if len(row) > 255:
                    raise EncodeError(
                        f"单行编码 {len(row)} 字节超过 I0/T0 的 u8 行长上限，"
                        "请改用 I1 格式或简化图片"
                    )
        frames_meta.append((kx, ky, img.width, img.height))
        frames_rows.append(rows)
    out = bytearray()
    out.extend(struct.pack(
        "<2sHHHHHH", magic.encode("ascii"), 1, len(images),
        canvas_w, canvas_h, center_x, center_y,
    ))
    for meta in frames_meta:
        out.extend(struct.pack("<HHHH", *meta))
    out.extend(struct.pack("<I", sum(len(r) for r in frames_rows)))
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
    encoded = bytes(out)
    report = _verify_roundtrip(encoded, images)
    return encoded, palette, report


def _verify_roundtrip(encoded: bytes, images: list[Image.Image]) -> EncodeReport:
    """重新解码新字节，与源帧逐像素比对误差。"""
    sprite = decode_sprite(encoded)
    report = EncodeReport()
    err_sum = 0
    for fi, src_img in enumerate(images):
        got = sprite.render_frame(fi)
        src = src_img.convert("RGBA")
        if got.size != src.size:
            raise EncodeError("往返解码尺寸不一致，编码器内部错误")
        sp, gp = src.load(), got.load()
        for y in range(src.height):
            for x in range(src.width):
                sr, sg, sb, sa = sp[x, y]
                gr, gg, gb, ga = gp[x, y]
                rgb_err = max(abs(sr - gr), abs(sg - gg), abs(sb - gb))
                if sa == 0 and ga == 0:
                    rgb_err = 0  # 全透明像素颜色不计较
                report.max_rgb_error = max(report.max_rgb_error, rgb_err)
                report.max_alpha_error = max(
                    report.max_alpha_error, abs(sa - ga))
                err_sum += rgb_err
                report.total_pixels += 1
                if rgb_err > 8 or abs(sa - ga) > 16:
                    report.pixels_over_tolerance += 1
    if report.total_pixels:
        report.mean_rgb_error = err_sum / report.total_pixels
    return report


def load_frame_files(paths) -> list[Image.Image]:
    """按文件名自然序（01、02…）读帧图，GIF 展开为多帧 RGBA。"""
    import re
    from pathlib import Path

    from PIL import ImageSequence

    def natural(name: str):
        return [int(p) if p.isdigit() else p.lower()
                for p in re.split(r"(\d+)", name)]

    frames: list[Image.Image] = []
    for path in sorted((Path(p) for p in paths),
                       key=lambda p: natural(p.name)):
        try:
            with Image.open(path) as img:
                if getattr(img, "is_animated", False):
                    for frame in ImageSequence.Iterator(img):
                        frames.append(frame.convert("RGBA"))
                else:
                    frames.append(img.convert("RGBA"))
        except Exception as exc:
            raise EncodeError(f"读取图片 {path.name} 失败：{exc}") from exc
    if not frames:
        raise EncodeError("没有读到任何帧图")
    return frames


def sprite_bytes_from_files(paths) -> tuple[bytes, int, EncodeReport]:
    """多张帧图 → (精灵字节, 帧数, 误差报告)，锚点一律左上角。

    画布取最大帧尺寸；I0 单行过长时自动改用 I1。与 UI 编辑器的
    core/sprite_encode 是同一格式的两种落点。
    """
    frames = load_frame_files(paths)
    keys = [(0, 0)] * len(frames)
    canvas_w = max(img.width for img in frames)
    canvas_h = max(img.height for img in frames)
    try:
        data, _pal, report = encode_sprite(
            frames, keys, canvas_w, canvas_h, 0, 0, magic="I0")
    except EncodeError:
        data, _pal, report = encode_sprite(
            frames, keys, canvas_w, canvas_h, 0, 0, magic="I1")
    return data, len(frames), report
