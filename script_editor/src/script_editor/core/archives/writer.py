"""Private streaming replacement writers. Publication belongs to native_build.

Existing IDs/order/flags retained; no module insertion or path hashing. Physical
0SLF payload order can differ from its sorted directory order (real baseline).
"""

from __future__ import annotations

import struct
import zlib

from .document import ArchiveDocument
from .flsdata import CD_SIG, LOCAL_SIG, TRAILER_MAGIC


def write_script(source: ArchiveDocument, changed: dict[int, bytes], out):
    entries = source.index.metas
    if any(
        a.entry_id >= b.entry_id for a, b in zip(entries, entries[1:], strict=False)
    ):
        raise ValueError("script directory IDs must be strictly ordered")
    if any(not entry.r1 for entry in entries):
        raise ValueError("unknown zero-r1 script format")
    directory = struct.unpack("<I", source.reader.read_at(8, 4))[0]
    physical = sorted(range(len(entries)), key=lambda i: source.index.spans[i].offset)
    cursor, offsets, sizes = 0, {}, {}
    for i in physical:
        span = source.index.spans[i]
        if span.offset < cursor:
            raise ValueError("overlapping script payloads")
        source.reader.copy_to(cursor, span.offset - cursor, out)
        offsets[i] = out.tell()
        if i in changed:
            data = changed[i]
            out.write(data)
            sizes[i] = len(data)
        else:
            source.reader.copy_to(span.offset, span.length, out)
            sizes[i] = span.length
        cursor = span.offset + span.length
    source.reader.copy_to(cursor, directory - cursor, out)
    new_directory = out.tell()
    for i, meta in enumerate(entries):
        r2 = ((meta.r1 * meta.entry_id + 0xDF25E) & 0xFFFFFFFF) ^ sizes[i]
        r3 = ((r2 * i * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ offsets[i]
        out.write(struct.pack("<IIII", meta.entry_id, meta.r1, r2, r3))
    tail_start = directory + 16 * len(entries)
    source.reader.copy_to(tail_start, source.reader.size - tail_start, out)
    out.seek(8)
    out.write(struct.pack("<I", new_directory))
    out.seek(0, 2)


def write_data(source: ArchiveDocument, changed: dict[int, bytes], out):
    directory = struct.unpack("<I", source.reader.read_at(source.reader.size - 8, 4))[0]
    prefix = source.index.spans[0].local_offset
    source.reader.copy_to(0, prefix, out)
    positions, attrs = [], []
    for i, span in enumerate(source.index.spans):
        positions.append(out.tell())
        if i not in changed:
            source.reader.copy_to(span.local_offset, span.local_len, out)
            attrs.append((span.crc, span.csize, span.usize))
            continue
        native = changed[i]
        stored = zlib.compress(native, 9)[2:-4]
        method = source.index.metas[i].w1
        if method != 8:
            raise ValueError("unsupported modified data entry compression method")
        crc = zlib.crc32(native) & 0xFFFFFFFF
        out.write(
            struct.pack("<IHIII", LOCAL_SIG, method, crc, len(stored), len(native))
        )
        out.write(stored)
        pad_start = span.data_offset + span.csize
        source.reader.copy_to(
            pad_start, span.local_offset + span.local_len - pad_start, out
        )
        attrs.append((crc, len(stored), len(native)))
    new_directory = out.tell()
    cursor = directory
    for i, (crc, csize, usize) in enumerate(attrs):
        header = bytearray(source.reader.read_at(cursor, 28))
        if struct.unpack_from("<I", header)[0] != CD_SIG:
            raise ValueError("unexpected central record while writing")
        name_len = struct.unpack_from("<H", header, 26)[0]
        raw_name = source.reader.read_at(cursor + 28, name_len)
        struct.pack_into("<IIII", header, 10, crc, csize, usize, positions[i])
        out.write(header)
        out.write(raw_name)
        cursor += 28 + name_len
    out.write(struct.pack("<II", new_directory, TRAILER_MAGIC))
