#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把内存转储 mx_unpacked.bin 重建成 IDA 可正确加载的 PE，并做脱壳校验：
  - 逐段报告转储里的熵（_dyprot 段若降到 ~6.x 即脱壳成功）；
  - 把转储 .text 与磁盘 .text 原始字节对拍，确认 .text 在内存是否被壳改写；
  - 把每个段的 PointerToRawData 改为 (VirtualAddress-ImageBase)，SizeOfRawData 改为内存尺寸；
  - 清 import/IAT/delay-import 数据目录，保留 export 目录。
用法: python3 rebuild_pe.py <dump> <out_pe> <orig_dll_for_compare>
"""
import sys, struct, math, hashlib

def entropy(b):
    if not b: return 0.0
    cnt = [0]*256
    for x in b: cnt[x]+=1
    n=len(b); e=0.0
    for c in cnt:
        if c:
            p=c/n; e-=p*math.log2(p)
    return e

def main():
    dump_path, out_path, orig = sys.argv[1], sys.argv[2], sys.argv[3]
    imgbase = 0x400000
    with open(dump_path,"rb") as f: d=bytearray(f.read())
    print("dump size:", len(d), "md5:", hashlib.md5(d).hexdigest())
    assert d[:2]==b"MZ"
    e_lfanew = struct.unpack_from("<I", d, 0x3C)[0]
    off = e_lfanew+4
    machine,nsec,ts,p_sym,n_sym,optsz,chars = struct.unpack_from("<HHIIIHH", d, off)
    o = off+20
    imgbase_hdr = struct.unpack_from("<I", d, o+28)[0]
    print("machine=0x%04x nsec=%d optsz=%d hdr_imgbase=0x%08x" % (machine,nsec,optsz,imgbase_hdr))
    dd_off = o+96
    sh_off = e_lfanew+24+optsz

    # 取磁盘 .text 原始字节用于对拍
    ondisk = open(orig,"rb").read()
    # 磁盘 .text 的 PointerToRawData / VirtualSize 从磁盘 PE 头取
    e2 = struct.unpack_from("<I", ondisk, 0x3C)[0]
    off2 = e2+4; nsec2,optsz2 = struct.unpack_from("<HH", ondisk, off2+2)
    sh2 = e2+24+optsz2
    disk_text_raw = disk_text_vs = None
    for i in range(nsec2):
        so=sh2+i*40; name=ondisk[so:so+8].split(b"\x00")[0].decode("latin1")
        vs,va,rs,pr = struct.unpack_from("<IIII", ondisk, so+8)
        if name==".text": disk_text_raw, disk_text_vs = pr, vs

    print("\n--- per-section dump entropy (decrypt check) ---")
    for i in range(nsec):
        so=sh_off+i*40
        name=d[so:so+8].split(b"\x00")[0].decode("latin1")
        vs,va,rs,pr = struct.unpack_from("<IIII", d, so+8)
        foff = va-imgbase
        avail = len(d)-foff if foff < len(d) else 0
        seg = bytes(d[foff:foff+min(vs,avail)]) if avail>0 else b""
        e = entropy(seg)
        note = ""
        if name==".text" and disk_text_raw is not None:
            ds = ondisk[disk_text_raw:disk_text_raw+min(vs, len(ondisk)-disk_text_raw)]
            same = len(ds)==len(seg) and ds==seg
            note = "  ondisk_ent=%.2f  identical_to_ondisk=%s" % (entropy(ds), same)
        print("%-10s VA=0x%08x VS=0x%07x dump_ent=%.2f%s" % (name, imgbase+va, vs, e, note))
        if 0 <= foff < len(d):
            new_rs = vs if foff+vs <= len(d) else (len(d)-foff)
            struct.pack_into("<II", d, so+16, max(0,new_rs), foff)  # SizeOfRawData, PointerToRawData
    # 诱饵段（.text/.rdata/.data/.rsrc 在内存里是加密/清零的废段）清零，只留解密后的 _dyprot0/_dyprot1
    for i in range(nsec):
        so=sh_off+i*40
        name=d[so:so+8].split(b"\x00")[0].decode("latin1")
        if name in (".text",".rdata",".data",".rsrc"):
            struct.pack_into("<II", d, so+16, 0, 0)  # SizeOfRawData, PointerToRawData
            print("[*] zeroed decoy section:", name)
    for idx in (1,12,13):
        struct.pack_into("<II", d, dd_off+idx*8, 0, 0)
    print("\n[*] cleared import/IAT/delay-import; kept export dir")
    with open(out_path,"wb") as f: f.write(d)
    print("[*] rebuilt PE ->", out_path, "size", len(d))

if __name__=="__main__":
    main()
