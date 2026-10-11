#!/usr/bin/env python3
"""
MXSJ Universal FLS Archive Tool
Comprehensive Unpacker & Repacker supporting ALL .fls formats in the game:
  Type 1: 0SLF Archives (script.fls, skill.fls, skill2.fls, passive.fls, effect.fls)
          - End-of-file index table with 3-degree polynomial encryption
          - Zlib compression / raw payload support
  Type 2: FLS\x00 Archives (data.fls)
          - Custom ZIP-like structure with 0x87F2017C signature
          - XOR 0xA5 filename obfuscation, raw zlib compression
"""

import os
import sys
import struct
import zlib
import argparse
from pathlib import Path

MASK32 = 0xFFFFFFFF

# ==============================================================================
# 0SLF Engine (script.fls, skill.fls, skill2.fls, passive.fls, effect.fls)
# ==============================================================================

def decode_0slf_dir(index: int, raw: tuple[int, int, int, int]):
    entry_id, r1, r2, r3 = raw
    f1 = (((index * 0x0E7C83D2 + entry_id) & MASK32) ^ r1) & MASK32
    f2 = (((r1 * entry_id + 0x0DF25E) & MASK32) ^ r2) & MASK32
    f3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32) ^ r3) & MASK32
    return f1, f2, f3

def encode_0slf_dir(index: int, entry_id: int, r1: int, clen: int, doff: int):
    r2 = (((r1 * entry_id + 0x0DF25E) & MASK32) ^ clen) & MASK32
    r3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32) ^ doff) & MASK32
    return (entry_id, r1, r2, r3)

def unpack_0slf(fls_path: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    with open(fls_path, "rb") as f:
        arc = f.read()

    magic = arc[:4]
    count = struct.unpack("<I", arc[4:8])[0]
    idx_off = struct.unpack("<I", arc[8:12])[0]
    print(f"[*] Unpacking 0SLF archive: {fls_path} ({count} entries)")

    manifest = {"type": "0SLF", "magic": magic.decode("latin1"), "count": count, "entries": []}

    for i in range(count):
        raw = struct.unpack_from("<IIII", arc, idx_off + i*16)
        f1, clen, doff = decode_0slf_dir(i, raw)
        chunk = arc[doff:doff+clen]
        is_compressed = False
        data = chunk
        try:
            data = zlib.decompress(chunk)
            is_compressed = True
        except Exception:
            pass

        out_name = f"entry_{i:04d}.bin"
        out_file = os.path.join(out_dir, out_name)
        with open(out_file, "wb") as f_out:
            f_out.write(data)

        manifest["entries"].append({
            "index": i,
            "entry_id": raw[0],
            "r1": raw[1],
            "file": out_name,
            "is_compressed": is_compressed,
            "orig_size": len(data)
        })

    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f_mf:
        import json
        json.dump(manifest, f_mf, indent=2)

    print(f"[✓] Unpacked {count} entries to {out_dir}/")

def repack_0slf(in_dir: str, out_fls: str):
    import json
    mf_path = os.path.join(in_dir, "manifest.json")
    if not os.path.exists(mf_path):
        raise ValueError(f"manifest.json not found in {in_dir}")
    with open(mf_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    magic = manifest["magic"].encode("latin1")
    count = manifest["count"]
    entries = manifest["entries"]
    print(f"[*] Repacking 0SLF archive to {out_fls} ({count} entries)")

    data_payload = bytearray()
    dir_entries = []

    for item in entries:
        i = item["index"]
        eid = item["entry_id"]
        r1 = item["r1"]
        f_path = os.path.join(in_dir, item["file"])
        with open(f_path, "rb") as f_in:
            data = f_in.read()

        if item.get("is_compressed", True):
            comp = zlib.compress(data, 9)
        else:
            comp = data

        offset = 16 + len(data_payload)
        clen = len(comp)
        data_payload.extend(comp)
        dir_entries.append((i, eid, r1, clen, offset))

    idx_off = 16 + len(data_payload)
    index_bytes = bytearray()
    for i, eid, r1, clen, offset in dir_entries:
        raw = encode_0slf_dir(i, eid, r1, clen, offset)
        index_bytes.extend(struct.pack("<IIII", *raw))

    header = struct.pack("<4sIII", magic, count, idx_off, 0)
    with open(out_fls, "wb") as f_out:
        f_out.write(header)
        f_out.write(data_payload)
        f_out.write(index_bytes)

    print(f"[✓] Successfully repacked {out_fls} (Size: {os.path.getsize(out_fls)} bytes)!")


# ==============================================================================
# FLS\x00 Engine (data.fls)
# ==============================================================================

def unpack_data_fls(fls_path: str, out_dir: str):
    with open(fls_path, "rb") as f:
        arc = f.read()

    pos = struct.unpack_from("<I", arc, len(arc) - 8)[0]
    entries = []
    while pos < len(arc) - 8:
        sig = struct.unpack_from("<I", arc, pos)[0]
        if sig != 0x87f2017c:
            break
        pos += 4
        w1, w2, w3 = struct.unpack_from("<HHH", arc, pos)
        pos += 6
        crc, csize, usize, l_off = struct.unpack_from("<IIII", arc, pos)
        pos += 16
        name_len = struct.unpack_from("<H", arc, pos)[0]
        pos += 2
        raw_name = arc[pos:pos+name_len]
        pos += name_len
        name = bytes([b ^ 0xa5 for b in raw_name]).decode("gbk", errors="replace")
        entries.append((name, w1, w2, w3, crc, csize, usize, l_off))

    print(f"[*] Unpacking FLS\\x00 (data.fls): {len(entries)} modules")
    os.makedirs(out_dir, exist_ok=True)
    manifest = {"type": "FLS_DATA", "entries": []}

    for name, w1, w2, w3, crc, csize, usize, l_off in entries:
        if csize == 0 or usize == 0:
            continue
        comp_data = arc[l_off + 18 : l_off + 18 + csize]
        try:
            decomp = zlib.decompress(comp_data, -15)
        except Exception:
            decomp = comp_data

        target_path = os.path.join(out_dir, name.replace("\\", os.sep))
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "wb") as f_out:
            f_out.write(decomp)

        manifest["entries"].append({
            "name": name, "w1": w1, "w2": w2, "w3": w3,
            "csize": csize, "usize": usize, "l_off": l_off
        })

    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f_mf:
        import json
        json.dump(manifest, f_mf, indent=2)

    print(f"[✓] Unpacked {len(entries)} files from data.fls to {out_dir}/")

def repack_data_fls(in_dir: str, out_fls: str, orig_fls_path: str):
    """
    Repacks modified files into data.fls format.
    Uses original archive as base template to preserve structure while updating edited files.
    """
    import json, binascii
    with open(os.path.join(in_dir, "manifest.json"), "r", encoding="utf-8") as f:
        manifest = json.load(f)

    with open(orig_fls_path, "rb") as f:
        arc = bytearray(f.read())

    print(f"[*] Repacking data.fls into {out_fls}...")
    for item in manifest["entries"]:
        name = item["name"]
        f_path = os.path.join(in_dir, name)
        if os.path.exists(f_path):
            with open(f_path, "rb") as f_in:
                new_data = f_in.read()
            # If length matches or we write in-place
            l_off = item["l_off"]
            csize = item["csize"]
            # Compress with raw deflate (-15)
            new_comp = zlib.compress(new_data, 9)[2:-4]
            if len(new_comp) <= csize:
                # Patch in-place with zero padding
                arc[l_off + 18 : l_off + 18 + len(new_comp)] = new_comp
                for p in range(l_off + 18 + len(new_comp), l_off + 18 + csize):
                    arc[p] = 0

    with open(out_fls, "wb") as f_out:
        f_out.write(arc)
    print(f"[✓] Repacked {out_fls} successfully!")


# ==============================================================================
# CLI Entrypoint
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="MXSJ Universal FLS Archive Tool")
    subparsers = parser.add_subparsers(dest="cmd", help="Action")

    # Unpack command
    p_unpack = subparsers.add_parser("unpack", help="Unpack .fls archive to a directory")
    p_unpack.add_argument("fls", help="Path to source .fls file")
    p_unpack.add_argument("out", help="Output directory")

    # Repack command
    p_repack = subparsers.add_parser("repack", help="Repack directory back to .fls archive")
    p_repack.add_argument("dir", help="Directory containing unpacked files and manifest.json")
    p_repack.add_argument("fls", help="Output .fls file")
    p_repack.add_argument("--base", default="data/data.fls", help="Base fls file (required for data.fls repacking)")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    if args.cmd == "unpack":
        with open(args.fls, "rb") as f:
            magic = f.read(4)
        if magic == b"0SLF":
            unpack_0slf(args.fls, args.out)
        elif magic == b"FLS\x00":
            unpack_data_fls(args.fls, args.out)
        else:
            print(f"[!] Unknown FLS magic: {magic}")

    elif args.cmd == "repack":
        import json
        mf_path = os.path.join(args.dir, "manifest.json")
        if not os.path.exists(mf_path):
            print(f"[!] Error: {mf_path} not found")
            return
        with open(mf_path, "r", encoding="utf-8") as f:
            mf = json.load(f)
        if mf.get("type") == "0SLF":
            repack_0slf(args.dir, args.fls)
        elif mf.get("type") == "FLS_DATA":
            repack_data_fls(args.dir, args.fls, args.base)
        else:
            print("[!] Unknown manifest format")

if __name__ == "__main__":
    main()
