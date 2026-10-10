#!/usr/bin/env python3
"""
MXSJ FLS Archive Repacker & Patching Engine
Allows modifying game data (equipment, scenes, dialogue, strings) and repacking
back into valid FLS archives without corrupting game files.
Always works out-of-place (creates new target archive or patch file).
"""

import os
import sys
import struct
import zlib
import json
import argparse
from collections import Counter

MASK32 = 0xFFFFFFFF

def decode_directory(index: int, raw: tuple[int, int, int, int]):
    entry_id, r1, r2, r3 = raw
    f1 = (((index * 0x0E7C83D2 + entry_id) & MASK32) ^ r1) & MASK32
    f2 = (((r1 * entry_id + 0x0DF25E) & MASK32) ^ r2) & MASK32
    f3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32) ^ r3) & MASK32
    return f1, f2, f3

def encode_directory(index: int, entry_id: int, r1: int, clen: int, doff: int):
    """
    Inverse algebraic mapping for FLS directory entry:
    r2 = ((r1 * entry_id + 0x0DF25E) & MASK32) ^ clen
    r3 = ((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32) ^ doff
    """
    r2 = (((r1 * entry_id + 0x0DF25E) & MASK32) ^ clen) & MASK32
    r3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32) ^ doff) & MASK32
    return (entry_id, r1, r2, r3)

def deobfuscate_5seg(exp: bytes):
    N = len(exp)
    if N < 50:
        return bytearray(exp), [0], [0, N]
    target = N / 5.0
    keys = []
    for i in range(5):
        mid = int((i + 0.5) * target)
        s = exp[max(0, mid-200):min(N, mid+200)]
        keys.append(Counter(s).most_common(1)[0][0])

    bounds = [0]
    for i in range(1, 5):
        k1 = keys[i-1]
        k2 = keys[i]
        c = int(i * target)
        b_best = c
        s_best = -1e9
        for b in range(max(bounds[-1]+10, c-300), min(N-10*(5-i), c+300)):
            score = sum(1 for p in range(b-40, b) if exp[p] == k1) + sum(1 for p in range(b, b+40) if exp[p] == k2)
            if score > s_best:
                s_best = score
                b_best = b
        bounds.append(b_best)
    bounds.append(N)

    dec = bytearray(N)
    for i in range(5):
        k = keys[i]
        for p in range(bounds[i], bounds[i+1]):
            dec[p] = exp[p] ^ k
    return dec, keys, bounds

def reobfuscate_5seg(dec: bytearray, keys: list[int], bounds: list[int]) -> bytes:
    """Re-applies the exact 5-segment XOR keys across boundaries"""
    N = len(dec)
    enc = bytearray(N)
    for i in range(5):
        k = keys[i]
        b_start = bounds[i]
        b_end = bounds[i+1] if i+1 < len(bounds) else N
        for p in range(b_start, min(b_end, N)):
            enc[p] = dec[p] ^ k
    return bytes(enc)

def patch_entry(src_fls_path: str, dst_fls_path: str, target_entry_idx: int, modified_payload: bytes):
    """
    Applies updated uncompressed bytecode/data to target entry, recompresses,
    appends to file body, updates the directory table, and produces a complete new archive.
    """
    print(f"[*] Reading source archive: {src_fls_path}")
    with open(src_fls_path, "rb") as f:
        arc = f.read()

    magic = arc[:4]
    count = struct.unpack("<I", arc[4:8])[0]
    idx_off = struct.unpack("<I", arc[8:12])[0]
    print(f"[*] Archive Magic: {magic}, Entries: {count}, Index Offset: {idx_off}")

    # Read all existing directory entries
    entries = []
    for i in range(count):
        raw = struct.unpack_from("<IIII", arc, idx_off + i*16)
        f1, clen, doff = decode_directory(i, raw)
        entries.append({
            "idx": i,
            "entry_id": raw[0],
            "orig_r1": raw[1],
            "clen": clen,
            "doff": doff
        })

    print(f"[*] Compressing modified data for Entry {target_entry_idx}...")
    new_compressed = zlib.compress(modified_payload, 9)
    new_clen = len(new_compressed)

    # In MXSJ FLS files, data blocks sit before the index table.
    # We place new compressed block right before index table, or append after old data.
    # To keep archive clean, we reconstruct:
    # [0..idx_off] (original data area) + [new_compressed] + [new_index_table]
    new_data_offset = idx_off
    new_idx_offset = idx_off + new_clen

    # Update target entry
    entries[target_entry_idx]["clen"] = new_clen
    entries[target_entry_idx]["doff"] = new_data_offset

    print(f"    -> Old clen={entries[target_entry_idx]['clen']}, New clen={new_clen} at offset={new_data_offset}")

    # Build new index table
    new_index_bytes = bytearray()
    for e in entries:
        i = e["idx"]
        eid = e["entry_id"]
        r1 = e["orig_r1"]
        clen = e["clen"]
        doff = e["doff"]
        new_raw = encode_directory(i, eid, r1, clen, doff)
        new_index_bytes += struct.pack("<IIII", *new_raw)

    # Build new header
    # Header format: [magic 4B] [count 4B] [idx_off 4B] [pad 4B]
    new_header = struct.pack("<4sIII", magic, count, new_idx_offset, 0)

    print(f"[*] Writing repackaged archive to: {dst_fls_path}")
    with open(dst_fls_path, "wb") as f:
        # Write header
        f.write(new_header)
        # Write original data up to old idx_off (excluding old header)
        f.write(arc[16:idx_off])
        # Write new compressed payload
        f.write(new_compressed)
        # Write new index table
        f.write(new_index_bytes)

    print(f"[✓] Successfully repacked archive! New size: {os.path.getsize(dst_fls_path)} bytes.")

def modify_equipment_example(src_fls: str, out_fls: str):
    """
    Example workflow:
    1. Reads Entry 17 (equipitemdata.py)
    2. Deobfuscates 5-seg XOR
    3. Modifies an equipment stat (e.g. boosts 短劍 attack)
    4. Reobfuscates 5-seg XOR
    5. Repacks back into new FLS file
    """
    with open(src_fls, "rb") as f:
        arc = f.read()

    raw17 = struct.unpack_from("<IIII", arc, 0x173EB22 + 17*16)
    _, clen17, doff17 = decode_directory(17, raw17)
    exp17 = zlib.decompress(arc[doff17:doff17+clen17])

    dec17, keys, bounds = deobfuscate_5seg(exp17)
    print(f"[*] Original Entry 17 keys: {[hex(k) for k in keys]}, bounds: {bounds}")

    # Search and replace in decrypted payload
    # Let's modify: 基礎屬性$攻擊 +108 -> 基礎屬性$攻擊 +999 (same byte length in Big5/GBK)
    old_str = "基礎屬性$攻擊 +108".encode("big5")
    new_str = "基礎屬性$攻擊 +999".encode("big5")

    if old_str in dec17:
        print(f"[*] Found target equipment attribute string! Modifying...")
        idx = dec17.index(old_str)
        dec17[idx:idx+len(old_str)] = new_str
        print(f"    -> Replaced '{old_str.decode('big5')}' with '{new_str.decode('big5')}'")
    else:
        print("[!] Target string not found in raw bytecode.")
        return

    # Re-obfuscate using same segment boundaries
    re_obf = reobfuscate_5seg(dec17, keys, bounds)
    # Patch into new archive
    patch_entry(src_fls, out_fls, 17, re_obf)

def verify_patched_archive(fls_path: str, entry_idx: int):
    """Verifies that the patched archive can be decoded cleanly by game engine routines"""
    print(f"\n[*] Verifying patched archive: {fls_path}...")
    with open(fls_path, "rb") as f:
        arc = f.read()
    idx_off = struct.unpack("<I", arc[8:12])[0]
    raw = struct.unpack_from("<IIII", arc, idx_off + entry_idx*16)
    f1, clen, doff = decode_directory(entry_idx, raw)
    comp = arc[doff:doff+clen]
    exp = zlib.decompress(comp)
    dec, _, _ = deobfuscate_5seg(exp)
    
    # Check if +999 exists
    if "攻擊 +999".encode("big5") in dec:
        print(f"[✓] Verification SUCCESS: Patched string '攻擊 +999' is fully readable and decrypted!")
    else:
        print("[!] Verification Failed: Target string not found.")

def main():
    parser = argparse.ArgumentParser(description="MXSJ FLS Archive Repacker & Patching Engine")
    parser.add_argument("--test-patch", action="store_true", help="Run a test patch on equipment (短劍 +999 攻擊)")
    parser.add_argument("--src", default="data/script.fls", help="Source FLS archive")
    parser.add_argument("--dst", default="tools/data-export/script_modded.fls", help="Output repacked FLS archive")
    args = parser.parse_args()

    if args.test_patch:
        modify_equipment_example(args.src, args.dst)
        verify_patched_archive(args.dst, 17)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
