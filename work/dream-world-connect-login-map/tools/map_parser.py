#!/usr/bin/env python3
"""Read-only, bounded parser for the five observed MXSJ 0.1M map samples.

Does not decode the proprietary GEPJ image bitstream or interpret LLEC values.
All offsets are absolute file offsets; unknown fields are named conservatively.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

MAGIC = b"0.1M"
SECTORS = 49
GRID_WIDTH = 16  # 192 bytes displayed as 16x12: provisional, tested against samples
GRID_HEIGHT = 12
MAX_FILE = 64 * 1024 * 1024
MAX_RECORDS = 100_000


class MapFormatError(ValueError):
    pass


def uint32(blob: bytes, at: int) -> int:
    if at < 0 or at + 4 > len(blob):
        raise MapFormatError(f"u32 out of range at 0x{at:x}")
    return struct.unpack_from("<I", blob, at)[0]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MapFormatError(message)


def parse_map_bytes(data: bytes, *, source: str = "<bytes>") -> dict:
    require(216 <= len(data) <= MAX_FILE, "map size out of bounds")
    require(data[:4] == MAGIC, f"unsupported map signature {data[:4]!r}")
    width, height = struct.unpack_from("<II", data, 4)
    require(0 < width <= 100_000 and 0 < height <= 100_000, "implausible dimensions")
    offsets = list(struct.unpack_from("<49I", data, 12))
    unknown_208 = uint32(data, 208)
    record_count = uint32(data, 212)
    require(record_count <= MAX_RECORDS, "excessive prefix record count")
    record_index_end = 216 + 4 * record_count
    require(record_index_end <= len(data), "truncated prefix index")
    require(unknown_208 == 212, "unknown header word at 208 differs from observed 212")
    require(offsets[0] >= record_index_end and offsets[-1] < len(data), "bad sector offset range")
    require(all(a < b for a, b in zip(offsets, offsets[1:])), "sector offsets not increasing")
    records = []
    record_offsets = list(struct.unpack_from(f"<{record_count}I", data, 216)) if record_count else []
    if record_offsets:
        require(record_offsets[0] == record_index_end, "prefix records do not start after index")
        require(all(record_index_end <= a < b <= offsets[0]
                    for a, b in zip(record_offsets, record_offsets[1:] + [offsets[0]])),
                "invalid prefix record offsets")
        for idx, begin in enumerate(record_offsets):
            end = record_offsets[idx + 1] if idx + 1 < record_count else offsets[0]
            raw = data[begin:end]
            require(len(raw) >= 20, f"prefix record {idx}: shorter than five u32 fields")
            x, y, w, h, payload_length = struct.unpack_from("<5I", raw)
            require(len(raw) == 20 + payload_length, f"prefix record {idx}: payload length mismatch")
            require(0 < w <= width and 0 < h <= height and x + w <= width and y + h <= height,
                    f"prefix record {idx}: bounds outside map dimensions")
            records.append({
                "index": idx, "offset": begin, "length": len(raw),
                "bounds_px": {"x": x, "y": y, "width": w, "height": h},
                "payload_length": payload_length,
                "payload_sha256": hashlib.sha256(raw[20:]).hexdigest(),
                "sha256": hashlib.sha256(raw).hexdigest(),
            })
    elif record_index_end != offsets[0]:
        # Preserve rather than silently discard unrecognized bytes.
        raise MapFormatError("unexpected unindexed bytes before first sector")

    sectors = []
    value_counts = Counter()
    for idx, begin in enumerate(offsets):
        end = offsets[idx + 1] if idx + 1 < SECTORS else len(data)
        buf = memoryview(data)[begin:end]
        require(len(buf) >= 4 + 8 + 26 + 200 + 34, f"sector {idx}: too short")
        ref_count = uint32(buf, 0)
        require(ref_count < MAX_RECORDS and 4 + ref_count * 4 + 8 <= len(buf),
                f"sector {idx}: invalid record reference count")
        references = list(struct.unpack_from(f"<{ref_count}I", buf, 4)) if ref_count else []
        if references:
            require(all(ref < record_count for ref in references), f"sector {idx}: invalid record reference")
        g = 4 + ref_count * 4
        require(bytes(buf[g:g + 4]) == b"GEPJ", f"sector {idx}: missing GEPJ")
        jpeg_payload_len = uint32(buf, g + 4)
        jpeg_end = g + 8 + jpeg_payload_len
        # 13 x uint16 preceding the proprietary JPEG-like data are not interpreted.
        image_begin = g + 34
        require(jpeg_payload_len >= 26 and jpeg_end + 200 + 34 == len(buf),
                f"sector {idx}: section lengths disagree")
        require(bytes(buf[image_begin:image_begin + 4]) == b"\xff\xd8\xff\xa0",
                f"sector {idx}: unknown GEPJ image preamble")
        segment_lengths = list(struct.unpack_from("<13H", buf, g + 8))
        require(sum(segment_lengths) == jpeg_end - image_begin and all(n > 0 for n in segment_lengths),
                f"sector {idx}: GEPJ segments do not match payload length")
        cell_section = jpeg_end
        require(bytes(buf[cell_section:cell_section + 4]) == b"LLEC", f"sector {idx}: missing LLEC")
        require(uint32(buf, cell_section + 4) == 192, f"sector {idx}: non-192 LLEC")
        cells = list(buf[cell_section + 8:cell_section + 200])
        require(len(cells) == GRID_WIDTH * GRID_HEIGHT, "cell array truncated")
        value_counts.update(cells)
        brig = cell_section + 200
        require(bytes(buf[brig:brig + 4]) == b"GIRB", f"sector {idx}: missing GIRB")
        require(uint32(buf, brig + 4) == 22, f"sector {idx}: non-22 GIRB")
        # GIRB's 22-byte body and four-byte trailer have not been interpreted.
        sectors.append({
            "index": idx, "offset": begin, "length": end - begin,
            "record_references": references,
            "image": {"offset": begin + image_begin, "length": jpeg_end - image_begin,
                      "sha256": hashlib.sha256(buf[image_begin:jpeg_end]).hexdigest(),
                      "segment_lengths_u16_le": segment_lengths},
            "cell_offset": begin + cell_section + 8,
            "cells": cells,
            "brig_body_hex": bytes(buf[brig + 8:brig + 30]).hex(),
            "brig_trailer_hex": bytes(buf[brig + 30:brig + 34]).hex(),
        })
    return {
        "format": "MXSJ-0.1M-observed", "source": source,
        "sha256": hashlib.sha256(data).hexdigest(), "file_length": len(data),
        "header": {"signature_ascii": "0.1M", "width": width, "height": height,
                   "unknown_u32_at_208": unknown_208, "prefix_record_count": record_count},
        "grid": {"sector_columns": 7, "sector_rows": 7,
                 "cell_columns_per_sector": GRID_WIDTH, "cell_rows_per_sector": GRID_HEIGHT,
                 "interpretation": "raw LLEC bytes, row-major 16x12 visualization hypothesis; 0/1 semantics unknown"},
        "cell_value_counts": dict(sorted(value_counts.items())),
        "prefix_records": records, "sectors": sectors,
    }


def parse_map(path: str | Path) -> dict:
    path = Path(path)
    require(path.stat().st_size <= MAX_FILE, "map exceeds maximum size")
    return parse_map_bytes(path.read_bytes(), source=str(path))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="single .map file or directory of .map files")
    parser.add_argument("--output-dir", type=Path, help="explicit destination for JSON exports")
    parser.add_argument("--extract-gepj", type=int, metavar="SECTOR", help="extract ONE raw, undecoded image payload (0-48)")
    parser.add_argument("--texture-dir", type=Path, help="explicit destination for --extract-gepj")
    args = parser.parse_args()
    if args.extract_gepj is not None and (not 0 <= args.extract_gepj < SECTORS or not args.texture_dir):
        parser.error("--extract-gepj requires sector 0-48 and --texture-dir")
    paths = sorted(args.input.glob("*.map")) if args.input.is_dir() else [args.input]
    if not paths:
        parser.error("no .map files found")
    for path in paths:
        result = parse_map(path)
        print(f"{path}: {result['header']['width']}x{result['header']['height']}, "
              f"{len(result['sectors'])} sectors, {len(result['prefix_records'])} prefix records, "
              f"LLEC values={result['cell_value_counts']}")
        if args.output_dir:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            output = args.output_dir / (path.stem + ".json")
            output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"  -> {output}")
        if args.extract_gepj is not None:
            image = result["sectors"][args.extract_gepj]["image"]
            # Preserve the proprietary bytes exactly; do not give them a .jpg/.png extension.
            with path.open("rb") as stream:
                stream.seek(image["offset"])
                raw = stream.read(image["length"])
            require(hashlib.sha256(raw).hexdigest() == image["sha256"], "image changed during export")
            args.texture_dir.mkdir(parents=True, exist_ok=True)
            output = args.texture_dir / f"{path.stem}-sector-{args.extract_gepj:02d}.gepj.bin"
            output.write_bytes(raw)
            print(f"  raw undecoded GEPJ -> {output}")


if __name__ == "__main__":
    main()
