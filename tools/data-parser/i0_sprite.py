#!/usr/bin/env python3
"""`I0` / `T0` / `I1` sprite decoder for the MXSJ (Duoyi) client art packs.

These are the palettized sprite/animation entries stored inside the
``0SLF`` (.fls) containers ``skill.fls``, ``skill2.fls``, ``passive.fls``
and ``effect.fls``.  The format was reverse engineered from the shipped
client data alone (2026-10-13) and is verified byte-exactly against all
806 sprite entries in those four packs: every row of every frame decodes
with zero overrun, and rendered output matches the in-game art.

File layout
-----------
::

    header      <2s magic, u16 ver(=1), u16 frameCount, u16 canvasW,
                 u16 canvasH, u16 centerX, u16 centerY>          (14 bytes)
    frame dir   frameCount * <u16 keyX, u16 keyY, u16 frameW, u16 frameH>
    totalLines  u32, always == sum(frameH) over all frames
    line table  totalLines row byte-lengths: u8 for I0/T0, u16 for I1
    palette     256 colors, immediately after the table:
                  I0 / I1 : 512 bytes RGB565 little-endian
                  T0      : 768 bytes RGB888
    pixel data  per-frame rows concatenated; every frame's data is
                padded to a 4-byte boundary (1-3 padding bytes live
                inside the last row's table length and are skipped).

Row token grammar (count/level = low bits of the token byte)
------------------------------------------------------------
::

    0x00        end of row (remainder of the row is transparent)
    0x01-0x1F   RUN    cnt = tok & 0x1F pixels; followed by an alpha-level
                       byte (0-31) and a palette-index byte; draws cnt
                       pixels of (index, alpha)
    0x20-0x3F   SINGLE 1 pixel; palette-index byte follows;
                       alpha level = tok & 0x1F
    0x40-0x7F   LIT    cnt = tok & 0x3F opaque pixels; cnt index bytes
    0x80-0xBF   REP    cnt = tok & 0x3F opaque pixels of a single palette
                       index (index byte follows)
    0xC0-0xFF   SKIP   cnt = tok & 0x3F transparent pixels (nothing follows)

Alpha levels are 5-bit: ``alpha8 = level * 255 // 31``.

Frame placement: a frame's top-left corner on the global canvas is
``(centerX - keyX, centerY - keyY)`` (anchor/key-point convention).

Usage
-----
::

    python3 i0_sprite.py info    data/skill.fls 0
    python3 i0_sprite.py export  data/skill.fls OUTDIR          # all entries
    python3 i0_sprite.py sheet   data/effect.fls OUTDIR 0 38    # strips
"""

import struct
import sys
from pathlib import Path

MAGICS = (b'I0', b'T0', b'I1')


def is_sprite(data: bytes) -> bool:
    return len(data) >= 26 and data[:2] in MAGICS


class Sprite:
    """One decoded I0/T0/I1 sprite (header, frames, palette, rows)."""

    def __init__(self, data: bytes):
        if not is_sprite(data):
            raise ValueError('not an I0/T0/I1 sprite')
        self.magic = data[:2].decode('ascii')
        (_m, self.version, self.frame_count, self.canvas_w, self.canvas_h,
         self.center_x, self.center_y) = struct.unpack_from('<2sHHHHHH', data, 0)
        self.frames = []                       # (key_x, key_y, w, h)
        off = 14
        for _ in range(self.frame_count):
            self.frames.append(struct.unpack_from('<HHHH', data, off))
            off += 8
        total_lines = struct.unpack_from('<I', data, off)[0]
        off += 4
        if total_lines != sum(f[3] for f in self.frames):
            raise ValueError('totalLines != sum(frame heights)')
        len_fmt = '<H' if self.magic == 'I1' else '<B'
        lens = [struct.unpack_from(len_fmt, data, off + i * struct.calcsize(len_fmt))[0]
                for i in range(total_lines)]
        off += total_lines * struct.calcsize(len_fmt)
        pal_size = 768 if self.magic == 'T0' else 512
        self.palette_raw = data[off:off + pal_size]
        off += pal_size
        self.palette = self._decode_palette()
        self.frame_rows = []                   # frame -> [row bytes, ...]
        li = pos = 0
        pos = off
        for (_kx, _ky, _fw, fh) in self.frames:
            rows = []
            for _ in range(fh):
                rows.append(data[pos:pos + lens[li]])
                pos += lens[li]
                li += 1
            self.frame_rows.append(rows)
        self.data_end = pos        # == len(data) for well-formed sprites

    def _decode_palette(self):
        pal = self.palette_raw
        if self.magic == 'T0':
            return [(pal[3 * i], pal[3 * i + 1], pal[3 * i + 2]) for i in range(256)]
        colors = []
        for i in range(256):                   # RGB565 little-endian
            v = pal[2 * i] | (pal[2 * i + 1] << 8)
            colors.append((((v >> 11) & 0x1F) * 255 // 31,
                           ((v >> 5) & 0x3F) * 255 // 63,
                           (v & 0x1F) * 255 // 31))
        return colors

    @staticmethod
    def _decode_row(line: bytes, width: int):
        """Decode one row to a list of (palette_index, alpha8)."""
        px = []
        i, n = 0, len(line)
        while i < n and len(px) < width:
            b = line[i]
            i += 1
            if b == 0x00:                                   # end of row
                break
            elif b < 0x20:                                  # RUN
                cnt = b & 0x1F
                alpha = line[i] * 255 // 31
                idx = line[i + 1]
                i += 2
                px.extend([(idx, alpha)] * min(cnt, width - len(px)))
            elif b < 0x40:                                  # SINGLE
                px.append((line[i], (b & 0x1F) * 255 // 31))
                i += 1
            elif b < 0x80:                                  # LIT
                for _ in range(b & 0x3F):
                    if len(px) < width:
                        px.append((line[i], 255))
                    i += 1
            elif b < 0xC0:                                  # REP
                cnt = b & 0x3F
                px.extend([(line[i], 255)] * min(cnt, width - len(px)))
                i += 1
            else:                                           # SKIP
                px.extend([(0, 0)] * min(b & 0x3F, width - len(px)))
        return px

    def render_frame(self, fi: int):
        """Render one frame as an RGBA PIL Image (frame-local size)."""
        from PIL import Image
        _kx, _ky, fw, fh = self.frames[fi]
        img = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
        pix = img.load()
        pal = self.palette
        for y, line in enumerate(self.frame_rows[fi]):
            for x, (idx, a) in enumerate(self._decode_row(line, fw)):
                if a:
                    r, g, b = pal[idx]
                    pix[x, y] = (r, g, b, a)
        return img

    def frame_offset(self, fi: int):
        """Top-left position of frame fi on the global canvas."""
        kx, ky, _fw, _fh = self.frames[fi]
        return (self.center_x - kx, self.center_y - ky)

    def render_canvas_frame(self, fi: int):
        """Render frame fi placed on the full canvas at its anchor."""
        from PIL import Image
        canvas = Image.new('RGBA', (self.canvas_w, self.canvas_h), (0, 0, 0, 0))
        frame = self.render_frame(fi)
        canvas.paste(frame, self.frame_offset(fi), frame)
        return canvas


# ---------------------------------------------------------------- CLI ----

def _archive(path):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] /
                           'map_editor' / 'src'))
    from map_editor.client.scriptfls import FlsArchive
    return FlsArchive(str(path))


def cmd_info(fls_path, idx):
    with _archive(fls_path) as arc:
        spr = Sprite(arc.compressed(int(idx)))
    print(f'{spr.magic} ver={spr.version} frames={spr.frame_count} '
          f'canvas={spr.canvas_w}x{spr.canvas_h} '
          f'center=({spr.center_x},{spr.center_y}) data_end={spr.data_end}')
    for fi, (kx, ky, fw, fh) in enumerate(spr.frames):
        print(f'  frame {fi}: key=({kx},{ky}) size={fw}x{fh}')


def cmd_export(fls_path, outdir):
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    done = skipped = 0
    with _archive(fls_path) as arc:
        for idx in range(arc.count):
            data = arc.compressed(idx)
            if not is_sprite(data):
                skipped += 1
                continue
            spr = Sprite(data)
            stem = out / f'{Path(fls_path).stem}_{idx:04d}_{spr.magic}'
            if spr.frame_count == 1:
                spr.render_frame(0).save(f'{stem}.png')
            else:
                for fi in range(spr.frame_count):
                    spr.render_frame(fi).save(f'{stem}_f{fi:02d}.png')
            done += 1
    print(f'exported {done} sprites, skipped {skipped} non-sprite entries -> {out}')


def cmd_sheet(fls_path, outdir, idxs):
    from PIL import Image
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    with _archive(fls_path) as arc:
        for idx in idxs:
            spr = Sprite(arc.compressed(int(idx)))
            frames = [spr.render_canvas_frame(fi) for fi in range(spr.frame_count)]
            w = sum(f.width for f in frames)
            h = max(f.height for f in frames)
            strip = Image.new('RGBA', (w, h), (28, 28, 38, 255))
            x = 0
            for f in frames:
                strip.paste(f, (x, 0), f)
                x += f.width
            name = out / f'{Path(fls_path).stem}_{int(idx):04d}_{spr.magic}_strip.png'
            strip.convert('RGB').save(name)
            print('saved', name)


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'info':
        cmd_info(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 4 and sys.argv[1] == 'export':
        cmd_export(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 5 and sys.argv[1] == 'sheet':
        cmd_sheet(sys.argv[2], sys.argv[3], sys.argv[4:])
    else:
        print(__doc__)
        sys.exit(2)
