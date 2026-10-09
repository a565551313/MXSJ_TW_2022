#!/usr/bin/env python3
"""Read-only decoder for data/script.fls entry 516.

The script validates the FLS directory transform, zlib payload, five XOR
segments, and the Python 2.7 marshal object tree. It never writes to the
client sample; generated files are placed beside this script unless changed
with --out-dir.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path


MASK32 = 0xFFFFFFFF
EXPECTED_ARCHIVE_SHA256 = "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72"
EXPECTED_COUNT = 5002
EXPECTED_INDEX_OFFSET = 0x173EB22
ENTRY_INDEX = 516
ENTRY_ID = 0x183E0854
XOR_SEGMENTS = (
    (0x0000, 0x0D84, 0xB1),
    (0x0D84, 0x1B4D, 0x44),
    (0x1B4D, 0x28F5, 0x30),
    (0x28F5, 0x367C, 0x41),
    (0x367C, 0x4352, 0x20),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def decode_directory(index: int, raw: tuple[int, int, int, int]) -> tuple[int, int, int]:
    entry_id, r1, r2, r3 = raw
    f1 = (((index * 0x0E7C83D2 + entry_id) & MASK32) ^ r1) & MASK32
    f2 = (((r1 * entry_id + 0x0DF25E) & MASK32) ^ r2) & MASK32
    f3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32) ^ r3) & MASK32
    return f1, f2, f3


def extract_entry(archive: bytes, entry_index: int) -> dict:
    if archive[:4] != b"0SLF":
        raise ValueError(f"bad FLS magic: {archive[:4]!r}")
    count = u32(archive, 4)
    index_offset = u32(archive, 8)
    if count != EXPECTED_COUNT:
        raise ValueError(f"unexpected FLS entry count: {count}")
    if index_offset != EXPECTED_INDEX_OFFSET:
        raise ValueError(f"unexpected FLS index offset: 0x{index_offset:x}")
    if index_offset + count * 16 != len(archive):
        raise ValueError("FLS directory does not occupy the final fixed-size records")
    if not 0 <= entry_index < count:
        raise IndexError(entry_index)
    raw_offset = index_offset + entry_index * 16
    raw = struct.unpack_from("<IIII", archive, raw_offset)
    decoded = decode_directory(entry_index, raw)
    _reserved, compressed_length, data_offset = decoded
    compressed = archive[data_offset : data_offset + compressed_length]
    if len(compressed) != compressed_length:
        raise ValueError("entry payload is truncated")
    expanded = zlib.decompress(compressed)
    return {
        "index": entry_index,
        "raw_offset": raw_offset,
        "raw_words": list(raw),
        "decoded_fields": {
            "field1": decoded[0],
            "compressed_length": decoded[1],
            "data_offset": decoded[2],
        },
        "compressed_sha256": sha256(compressed),
        "expanded_sha256": sha256(expanded),
        "compressed": compressed,
        "expanded": expanded,
    }


def verify_all_entries(archive: bytes, count: int, index_offset: int) -> dict:
    total_expanded = 0
    for index in range(count):
        raw_offset = index_offset + index * 16
        raw = struct.unpack_from("<IIII", archive, raw_offset)
        _field1, compressed_length, data_offset = decode_directory(index, raw)
        compressed = archive[data_offset : data_offset + compressed_length]
        if len(compressed) != compressed_length:
            raise ValueError(f"entry {index} payload is truncated")
        total_expanded += len(zlib.decompress(compressed))
    return {
        "verified_entry_count": count,
        "total_expanded_length": total_expanded,
    }


def xor_decode(expanded: bytes) -> bytes:
    if len(expanded) != XOR_SEGMENTS[-1][1]:
        raise ValueError(f"unexpected expanded length: {len(expanded)}")
    output = bytearray(expanded)
    for start, end, key in XOR_SEGMENTS:
        for offset in range(start, end):
            output[offset] ^= key
    return bytes(output)


class MarshalReader:
    """Small Python 2.7 marshal reader with interned-string support."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.interned_strings = []
        self.code_objects = []
        self.strings = []

    def take(self, size: int) -> bytes:
        end = self.pos + size
        if end > len(self.data):
            raise ValueError(f"marshal truncated at 0x{self.pos:x}, need {size} bytes")
        result = self.data[self.pos:end]
        self.pos = end
        return result

    def byte(self) -> int:
        return self.take(1)[0]

    def i32(self) -> int:
        return struct.unpack("<i", self.take(4))[0]

    def u32(self) -> int:
        return struct.unpack("<I", self.take(4))[0]

    def string_bytes(self, length: int) -> bytes:
        value = self.take(length)
        self.strings.append(value)
        return value

    def read(self):
        type_code = self.byte()

        if type_code == ord("0"):
            value = None
        elif type_code == ord("N"):
            value = None
        elif type_code == ord("F"):
            value = False
        elif type_code == ord("T"):
            value = True
        elif type_code == ord("S"):
            value = StopIteration
        elif type_code == ord("i"):
            value = self.i32()
        elif type_code == ord("I"):
            value = struct.unpack("<q", self.take(8))[0]
        elif type_code == ord("f"):
            value = float(self.take(self.u32()).decode("ascii"))
        elif type_code == ord("g"):
            value = struct.unpack("<d", self.take(8))[0]
        elif type_code in (ord("s"), ord("t"), ord("a"), ord("A")):
            value = self.string_bytes(self.u32())
            if type_code == ord("t"):
                self.interned_strings.append(value)
        elif type_code == ord("u"):
            value = self.take(self.u32()).decode("utf-8", "replace")
        elif type_code == ord("R"):
            index = self.u32()
            try:
                value = self.interned_strings[index]
            except IndexError as exc:
                raise ValueError(f"bad marshal string reference {index}") from exc
        elif type_code in (ord("("), ord("["), ord("<")):
            length = self.u32()
            items = [self.read() for _ in range(length)]
            value = tuple(items) if type_code == ord("(") else items
        elif type_code == ord("{"):
            value = {}
            while True:
                key = self.read()
                if key is None:
                    break
                value[key] = self.read()
        elif type_code == ord("c"):
            value = self.read_code_object()
        else:
            raise ValueError(
                f"unsupported marshal type 0x{type_code:02x} at 0x{self.pos - 1:x}"
            )
        return value

    def read_code_object(self):
        start = self.pos - 1
        argcount = self.i32()
        nlocals = self.i32()
        stacksize = self.i32()
        flags = self.i32()
        code = self.read()
        consts = self.read()
        names = self.read()
        varnames = self.read()
        freevars = self.read()
        cellvars = self.read()
        filename = self.read()
        name = self.read()
        firstlineno = self.i32()
        lnotab = self.read()
        record = {
            "offset": start,
            "argcount": argcount,
            "nlocals": nlocals,
            "stacksize": stacksize,
            "flags": flags,
            "code_len": len(code) if isinstance(code, (bytes, bytearray)) else None,
            "consts": consts,
            "names": names,
            "varnames": varnames,
            "freevars": freevars,
            "cellvars": cellvars,
            "filename": filename,
            "name": name,
            "firstlineno": firstlineno,
            "lnotab_len": len(lnotab) if isinstance(lnotab, (bytes, bytearray)) else None,
        }
        self.code_objects.append(record)
        return record


def text_values(value, output: list[str]) -> None:
    if isinstance(value, bytes):
        try:
            text = value.decode("utf-8")
        except UnicodeDecodeError:
            text = value.decode("latin-1")
        if text and all((ch.isprintable() or ch in "\r\n\t") for ch in text):
            output.append(text)
    elif isinstance(value, str):
        if value:
            output.append(value)
    elif isinstance(value, dict):
        for key, item in value.items():
            text_values(key, output)
            text_values(item, output)
    elif isinstance(value, (tuple, list)):
        for item in value:
            text_values(item, output)


def run(archive_path: Path, out_dir: Path) -> dict:
    archive = archive_path.read_bytes()
    archive_hash = sha256(archive)
    if archive_hash != EXPECTED_ARCHIVE_SHA256:
        raise ValueError(f"archive SHA-256 mismatch: {archive_hash}")
    extracted = extract_entry(archive, ENTRY_INDEX)
    archive_validation = verify_all_entries(
        archive,
        u32(archive, 4),
        u32(archive, 8),
    )
    if extracted["raw_words"][0] != ENTRY_ID:
        raise ValueError(f"entry id mismatch: 0x{extracted['raw_words'][0]:08x}")
    expanded = extracted["expanded"]
    decoded = xor_decode(expanded)

    reader = MarshalReader(decoded)
    root = reader.read()
    if reader.pos != len(decoded):
        raise ValueError(f"marshal parser stopped at 0x{reader.pos:x} of 0x{len(decoded):x}")
    if not isinstance(root, dict):
        raise ValueError(f"marshal root is {type(root).__name__}, expected dict-like tree")

    names = []
    for code_object in reader.code_objects:
        name = code_object.get("name")
        if isinstance(name, bytes):
            name = name.decode("utf-8", "replace")
        if isinstance(name, str):
            names.append(name)
    all_text = []
    text_values(root, all_text)
    unique_text = sorted(set(all_text))
    wanted = [
        "CMXNet",
        "OnServerCmd",
        "ProcessServerCmd",
        "C2STransferServer",
        "ReselectServerConnect",
        "S2CServerRoleInfo",
        "ModuleReset",
        "RefreshServerInfo",
        "Connect",
        "RandomConnect",
    ]
    key_strings = [value for value in wanted if value in unique_text or value in names]

    out_dir.mkdir(parents=True, exist_ok=True)
    expanded_path = out_dir / "entry516-expanded.bin"
    decoded_path = out_dir / "entry516-five-xor-marshal.bin"
    expanded_path.write_bytes(expanded)
    decoded_path.write_bytes(decoded)

    result = {
        "archive": {
            "path": str(archive_path),
            "sha256": archive_hash,
            "size": len(archive),
            "magic": archive[:4].decode("ascii"),
            "entry_count": u32(archive, 4),
            "index_offset": u32(archive, 8),
            "all_entries_zlib_verified": True,
            **archive_validation,
        },
        "entry": {
            "index": ENTRY_INDEX,
            "id": f"0x{extracted['raw_words'][0]:08x}",
            "raw_offset": f"0x{extracted['raw_offset']:x}",
            "decoded_field1": f"0x{extracted['decoded_fields']['field1']:08x}",
            "compressed_length": extracted["decoded_fields"]["compressed_length"],
            "data_offset": extracted["decoded_fields"]["data_offset"],
            "data_offset_hex": f"0x{extracted['decoded_fields']['data_offset']:x}",
            "compressed_sha256": extracted["compressed_sha256"],
            "expanded_length": len(expanded),
            "expanded_sha256": extracted["expanded_sha256"],
        },
        "xor_segments": [
            {"start": start, "end": end, "key": f"0x{key:02x}"}
            for start, end, key in XOR_SEGMENTS
        ],
        "marshal": {
            "decoded_length": len(decoded),
            "decoded_sha256": sha256(decoded),
            "bytes_consumed": reader.pos,
            "root_type": type(root).__name__,
            "code_object_count": len(reader.code_objects),
            "code_object_names": names,
            "key_strings": key_strings,
        },
        "outputs": {
            "expanded": str(expanded_path),
            "decoded": str(decoded_path),
        },
    }
    (out_dir / "entry516-result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--archive",
        type=Path,
        default=Path(__file__).parents[4] / "data" / "script.fls",
    )
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    try:
        result = run(args.archive, args.out_dir)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
