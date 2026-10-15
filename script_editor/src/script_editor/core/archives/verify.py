"""Byte-level envelope checks, separate from streaming writer implementations."""

from __future__ import annotations

import struct


def equal_region(old, old_offset, new, new_offset, length):
    for offset in range(0, length, 1024 * 1024):
        size = min(1024 * 1024, length - offset)
        a = old.reader.read_at(old_offset + offset, size)
        b = new.reader.read_at(new_offset + offset, size)
        if len(a) != size or len(b) != size or a != b:
            raise ValueError("unchanged file region differs/truncated")


def _gap(old, oa, ob, new, na, nb):
    if ob - oa != nb - na or ob < oa:
        raise ValueError("container gap/order changed")
    equal_region(old, oa, new, na, ob - oa)


def envelope(old, new, modified):
    if len(old.entries) != len(new.entries) or old.kind != new.kind:
        raise ValueError("container kind/count changed")
    for a, b in zip(old.entries, new.entries, strict=True):
        if (a.index, a.identity, a.directory) != (b.index, b.identity, b.directory):
            raise ValueError("entry identity/order changed")
    if old.kind == "0slf":

        def regions(document):
            directory = struct.unpack("<I", document.reader.read_at(8, 4))[0]
            result = [
                (span.offset, span.length, i)
                for i, span in enumerate(document.index.spans)
            ]
            result.append((directory, len(document.entries) * 16, -1))
            return sorted(result, key=lambda region: (region[0], region[1], region[2]))

        old_regions, new_regions = regions(old), regions(new)
        if [r[2] for r in old_regions] != [r[2] for r in new_regions]:
            raise ValueError("script physical region order changed")
        _gap(old, 0, 8, new, 0, 8)  # Only the directory pointer @8 may change.
        old_cursor = new_cursor = 12
        for (oa, ol, _), (na, nl, _) in zip(old_regions, new_regions, strict=True):
            _gap(old, old_cursor, oa, new, new_cursor, na)
            old_cursor, new_cursor = oa + ol, na + nl
        _gap(old, old_cursor, old.reader.size, new, new_cursor, new.reader.size)
    else:
        _gap(
            old,
            0,
            old.index.spans[0].local_offset,
            new,
            0,
            new.index.spans[0].local_offset,
        )
        for i in modified:
            a, b = old.index.spans[i], new.index.spans[i]
            _gap(
                old,
                a.data_offset + a.csize,
                a.local_offset + a.local_len,
                new,
                b.data_offset + b.csize,
                b.local_offset + b.local_len,
            )
        od = struct.unpack("<I", old.reader.read_at(old.reader.size - 8, 4))[0]
        nd = struct.unpack("<I", new.reader.read_at(new.reader.size - 8, 4))[0]
        for _ in old.entries:
            # Retain original central flags and encoded name bytes, not re-encoding.
            _gap(old, od, od + 10, new, nd, nd + 10)
            old_len = struct.unpack("<H", old.reader.read_at(od + 26, 2))[0]
            new_len = struct.unpack("<H", new.reader.read_at(nd + 26, 2))[0]
            _gap(old, od + 26, od + 28 + old_len, new, nd + 26, nd + 28 + new_len)
            od, nd = od + 28 + old_len, nd + 28 + new_len
