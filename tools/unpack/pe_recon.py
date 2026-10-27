#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PE 侦察（修正版）：段特征 / 熵 / TLS 回调 / 入口落点 / 导入表状态。仅用标准库。"""
import sys, struct, math, hashlib

def entropy(b):
    if not b:
        return 0.0
    cnt = [0] * 256
    for x in b:
        cnt[x] += 1
    n = len(b)
    e = 0.0
    for c in cnt:
        if c:
            p = c / n
            e -= p * math.log2(p)
    return e

def rva_to_raw(rva, sects, imgbase):
    for (name, va, vs, ra, rs) in sects:
        if va <= rva < va + vs:
            return ra + (rva - va)
    return None

def main():
    path = sys.argv[1]
    with open(path, "rb") as f:
        d = f.read()
    print("file:", path, "size:", len(d), "md5:", hashlib.md5(d).hexdigest())
    assert d[:2] == b"MZ"
    e_lfanew = struct.unpack_from("<I", d, 0x3C)[0]
    off = e_lfanew + 4
    machine, nsec, ts, p_sym, n_sym, optsz, chars = struct.unpack_from("<HHIIIHH", d, off)
    print("machine=0x%04x sections=%d ts=0x%08x optsz=%d characteristics=0x%04x"
          % (machine, nsec, ts, optsz, chars))
    o = off + 20  # optional header
    ep, imgbase, sectalign, filealign = struct.unpack_from("<IIII", d, o+16)
    imgbase = struct.unpack_from("<I", d, o+28)[0]   # explicit ImageBase
    subsystem = struct.unpack_from("<H", d, o+68)[0]
    print("entry RVA=0x%08x  imagebase=0x%08x  sectalign=0x%x filealign=0x%x subsystem=0x%x"
          % (ep, imgbase, sectalign, filealign, subsystem))
    dd_off = o + 96  # PE32 data directory array base
    ndirs = (optsz - 96) // 8
    print("data dirs:", ndirs)

    # parse sections
    sh_off = e_lfanew + 24 + optsz
    sects = []
    print("\n--- sections ---")
    for i in range(nsec):
        so = sh_off + i*40
        name = d[so:so+8].split(b"\x00")[0].decode("latin1")
        vsize, vaddr, rsize, rptr, _, _, _, c = struct.unpack_from("<IIIIIIII", d, so+8)
        raw = d[rptr:rptr+rsize] if rsize else b""
        e = entropy(raw)
        perm = "R X" if (c & 0x20000000) else ("R" if (c & 0x40000000) else "RW" if (c & 0x80000000) else "?")
        print("%-10s VA=0x%08x VS=0x%07x RAW=0x%07x ent=%.2f %s chars=0x%08x"
              % (name, imgbase+vaddr, vsize, len(raw), e, perm, c))
        sects.append((name, imgbase+vaddr, vsize, rptr, rsize))

    ea = imgbase + ep
    esec = [s for s in sects if s[1] <= ea < s[1]+s[2]]
    print("\nentry VA=0x%08x lands in: %s" % (ea, esec[0][0] if esec else "??"))

    # TLS dir index 9
    tls_rva, tls_size = struct.unpack_from("<II", d, dd_off + 9*8)
    print("\nTLS dir: RVA=0x%08x size=0x%x" % (tls_rva, tls_size))
    if tls_rva and tls_size:
        tls_raw = rva_to_raw(tls_rva, sects, imgbase)
        if tls_raw is not None:
            sa, ea2, aoi, aoc = struct.unpack_from("<IIII", d, tls_raw)
            print("TLS StartRaw=0x%08x EndRaw=0x%08x Index=0x%08x CallBacksRVA=0x%08x"
                  % (sa, ea2, aoi, aoc))
            if aoc:
                cb_raw = rva_to_raw(aoc, sects, imgbase)
                cbs = []
                p = cb_raw
                while True:
                    (r,) = struct.unpack_from("<I", d, p)
                    if r == 0:
                        break
                    cbs.append(hex(r))
                    p += 4
                    if len(cbs) > 64:
                        break
                print("TLS callbacks (%d): %s" % (len(cbs), cbs))

    # Import dir index 1
    imp_rva, imp_size = struct.unpack_from("<II", d, dd_off + 1*8)
    print("\nimport dir RVA=0x%08x size=0x%x" % (imp_rva, imp_size))
    if imp_rva and imp_size:
        imp_raw = rva_to_raw(imp_rva, sects, imgbase)
        mods = 0; p = imp_raw
        while True:
            o3, t0, f0, name_rva, thunk_rva = struct.unpack_from("<IIII", d, p)
            if name_rva == 0:
                break
            nr = rva_to_raw(name_rva, sects, imgbase)
            mod = d[nr:nr+40].split(b"\x00")[0].decode("latin1") if nr is not None else "?"
            mods += 1; p += 20
            if mods > 400:
                break
        print("import descriptors: %d modules" % mods)

if __name__ == "__main__":
    main()
