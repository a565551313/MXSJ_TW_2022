"""Hand-assembled marshal/container fixtures, no product writer dependency."""

from __future__ import annotations

import struct
import zlib

from script_editor.core.vm.py25 import codec as py25
from script_editor.core.vm.py27 import codec as py27


def raw_string(value):
    return b"s" + struct.pack("<I", len(value)) + value


def minimal_pyc(vm, value=1, code=b"d\0\0S", lnotab=b"", filename=b"authored.py"):
    empty = b"(" + bytes(4)
    root = (
        b"c"
        + struct.pack("<IIII", 0, 0, 1, 64)
        + raw_string(code)
        + b"(\1\0\0\0i"
        + struct.pack("<i", value)
        + empty * 4
        + raw_string(filename)
        + raw_string(b"<module>")
        + struct.pack("<I", 1)
        + raw_string(lnotab)
    )
    return (py25.MAGIC if vm == "py25" else py27.MAGIC) + bytes(4) + root


def xor(payload, keys, bounds):
    points = [0, *bounds, len(payload)]
    return b"".join(
        bytes(b ^ keys[i] for b in payload[points[i] : points[i + 1]]) for i in range(5)
    )


def script_fixture(expanded_size=512, two_modules=False, filename=b"authored.py"):
    # Golden sequence for seed 19084, independent of the product cipher helper.
    keys = [140, 89, 30, 116, 106]
    high_bytes = [74, 38, 125, 86]
    cursor, bounds = 0, []
    for high in high_bytes:
        cursor += expanded_size // 5 + high
        bounds.append(min(cursor, expanded_size))
    native = py25.encode(minimal_pyc("py25", filename=filename))
    stored = zlib.compress(
        xor(native + bytes(expanded_size - len(native)), keys, bounds)
    )
    payloads = [stored, stored if two_modules else b"unmodified-one", b"unmodified-two"]
    data = bytearray(struct.pack("<4sIII", b"0SLF", 3, 0, 0xCAFEBABE))
    offsets = {}
    # Physical order intentionally differs from sorted IDs/directory order.
    for i in (2, 0, 1):
        data.extend(b"GAP")
        offsets[i] = len(data)
        data.extend(payloads[i])
    data.extend(b"END-GAP")
    directory = len(data)
    struct.pack_into("<I", data, 8, directory)
    for i in range(3):
        eid, r1 = 100 + i, 17 + i
        r2 = ((eid * r1 + 0xDF25E) & 0xFFFFFFFF) ^ len(payloads[i])
        r3 = ((r2 * i * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ offsets[i]
        data.extend(struct.pack("<IIII", eid, r1, r2, r3))
    data.extend(b"TRAILER")
    catalog = {"0": {"keys": keys, "bounds": bounds}}
    if two_modules:
        catalog["1"] = {"keys": keys, "bounds": bounds}
    return bytes(data), catalog


def data_fixture(filename=b"authored.py"):
    payloads = [
        b"",
        py27.encode(minimal_pyc("py27", filename=filename)),
        b"opaque resource",
    ]
    names = ["lib\\", "lib\\sample.pyo", "config.txt"]
    data = bytearray(b"FLS\0" + bytes(range(60)) + b"BEFORE")
    rows = []
    for i, content in enumerate(payloads):
        stored = zlib.compress(content)[2:-4] if content else b""
        offset = len(data)
        crc = zlib.crc32(content)
        data.extend(
            struct.pack(
                "<IHIII", 0xA0975237, 0 if i == 0 else 8, crc, len(stored), len(content)
            )
        )
        data.extend(stored + b"PADDING")
        raw_name = bytes(b ^ 0xA5 for b in names[i].encode("gbk"))
        rows.append(
            struct.pack(
                "<IHHHIIIIH",
                0x87F2017C,
                8,
                i,
                77,
                crc,
                len(stored),
                len(content),
                offset,
                len(raw_name),
            )
            + raw_name
        )
    directory = len(data)
    data.extend(b"".join(rows))
    data.extend(struct.pack("<II", directory, 0xA1985237))
    return bytes(data)
