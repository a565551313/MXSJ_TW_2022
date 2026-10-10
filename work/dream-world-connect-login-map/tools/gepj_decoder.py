#!/usr/bin/env python3
"""Reconstruct MXSJ GEPJ's 12 independent 80x80 JPEG pieces per sector.

Offline, read-only source. Requires the locally installed ImageMagick `convert`.
Output PNG uses only Python's standard library. Refuses corrupt/partial JPEGs.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import shutil
import struct
import subprocess
import zlib

from map_parser import parse_map

PIECE = 80
SECTOR_WIDTH, SECTOR_HEIGHT = 320, 240


class ImageDecodeError(ValueError):
    pass


def _chunk(tag: bytes, content: bytes) -> bytes:
    return struct.pack(">I", len(content)) + tag + content + struct.pack(">I", zlib.crc32(tag + content))


def write_rgb_png(path: Path, width: int, height: int, pixels: bytes) -> None:
    if len(pixels) != width * height * 3:
        raise ImageDecodeError("RGB buffer length mismatch")
    stride = width * 3
    filtered = b"".join(b"\x00" + pixels[y * stride:(y + 1) * stride] for y in range(height))
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(filtered, level=6))
    png += _chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def unpack_gepj(payload: bytes, segment_sizes: list[int]) -> tuple[bytes, list[bytes]]:
    if len(segment_sizes) != 13 or any(n < 1 for n in segment_sizes):
        raise ImageDecodeError("expected 13 nonempty GEPJ segments")
    if sum(segment_sizes) != len(payload):
        raise ImageDecodeError("GEPJ segment sizes do not sum to image length")
    if payload[:4] != b"\xff\xd8\xff\xa0":
        raise ImageDecodeError("unknown GEPJ preamble")
    head_len = segment_sizes[0]
    header = payload[:head_len]
    if not header.endswith(b"\xff\xda\x00\x09\x03\x01\x00\x02\x11\x03\x22"):
        raise ImageDecodeError("unsupported GEPJ scan header")
    if b"\xff\xc0\x00\x11\x08\x00\x50\x00\x50" not in header:
        raise ImageDecodeError("unsupported JPEG piece dimensions")
    # Proprietary SOI extension FF A0 has no standard-JPEG payload.
    # SOS ends after three component selectors; JPEG requires 00 3F 00 too.
    jpeg_header = header[:2] + header[4:-11] + b"\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x22\x00\x3f\x00"
    parts = []
    at = head_len
    for size in segment_sizes[1:]:
        scan = payload[at:at + size]
        at += size
        # GEPJ stores independent unstuffed scan streams. JPEG encodes literal FF as FF 00.
        parts.append(jpeg_header + scan.replace(b"\xff", b"\xff\x00") + b"\xff\xd9")
    return jpeg_header, parts


def decode_jpeg(jpeg: bytes) -> bytes:
    if shutil.which("convert") is None:
        raise ImageDecodeError("local ImageMagick convert command is required")
    proc = subprocess.run(["convert", "jpeg:-", "-depth", "8", "rgb:-"], input=jpeg,
                          capture_output=True, timeout=20)
    if proc.returncode or proc.stderr or len(proc.stdout) != PIECE * PIECE * 3:
        raise ImageDecodeError(f"JPEG decode failed/produced warnings: exit={proc.returncode} "
                               f"size={len(proc.stdout)} stderr={proc.stderr.decode('utf-8', 'replace')[:400]}")
    return proc.stdout


def load_payload(path: Path, image: dict) -> bytes:
    with path.open("rb") as source:
        source.seek(image["offset"])
        payload = source.read(image["length"])
    if sha256(payload).hexdigest() != image["sha256"]:
        raise ImageDecodeError("source GEPJ payload SHA256 mismatch")
    return payload


def render(path: Path, *, sector_index: int | None = None) -> tuple[int, int, bytes]:
    doc = parse_map(path)
    if sector_index is not None and not 0 <= sector_index < 49:
        raise ImageDecodeError("sector index must be 0-48")
    width, height = ((SECTOR_WIDTH, SECTOR_HEIGHT) if sector_index is not None else
                     (doc["header"]["width"], doc["header"]["height"]))
    canvas = bytearray(width * height * 3)
    indices = [sector_index] if sector_index is not None else range(49)
    for i in indices:
        image = doc["sectors"][i]["image"]
        payload = load_payload(path, image)
        _header, jpeg_pieces = unpack_gepj(payload, image["segment_lengths_u16_le"])
        assert len(jpeg_pieces) == 12
        for j, jpeg in enumerate(jpeg_pieces):
            pixels = decode_jpeg(jpeg)
            x = (0 if sector_index is not None else i % 7 * SECTOR_WIDTH) + j % 4 * PIECE
            y = (0 if sector_index is not None else i // 7 * SECTOR_HEIGHT) + j // 4 * PIECE
            for row in range(PIECE):
                if y + row >= height or x >= width:
                    continue
                n = min(PIECE, width - x) * 3
                dest = ((y + row) * width + x) * 3
                canvas[dest:dest + n] = pixels[row * PIECE * 3:row * PIECE * 3 + n]
    return width, height, bytes(canvas)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map", type=Path, help="source .map")
    parser.add_argument("--sector", type=int, help="render only one 320x240 sector, 0-48")
    parser.add_argument("--output", type=Path, required=True, help="PNG destination")
    args = parser.parse_args()
    if args.output.suffix.lower() != ".png":
        parser.error("output must end in .png")
    w, h, rgb = render(args.map, sector_index=args.sector)
    write_rgb_png(args.output, w, h, rgb)
    print(f"{args.output}: {w}x{h}, RGB; decoded 12 JPEG pieces per sector")


if __name__ == "__main__":
    main()
