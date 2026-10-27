# -*- coding: utf-8 -*-
"""把扁平内存转储 mx_unpacked.bin 重建为单节扁平 PE，供 IDA 正确加载。

mx_unpacked.bin 是运行时内存扁平转储：file_offset F <-> VA 0x400000 + F。
之前 rebuild_pe.py 错误地把它当“带磁盘节表的正常 PE”重建，导致 OEP/VM
所在（落在磁盘节区之外、运行时解密的内存）被丢弃。这里强制：
  ImageBase = 0x400000
  AddressOfEntryPoint RVA = 0x8BA0AE   (VA 0xcba0ae, 真实 OEP)
  单个 ".flat" 节：VA=0x1000, RawOff=0x1000, VSize/RawSize = len-0x1000
这样 file_offset F -> VA 0x400000+F 的映射与转储一致，IDA 能看到全部运行时代码。

用法: python3 rebuild_flat.py <flat_bin> <out_pe>
"""
import sys, struct

def build_flat_pe(bin_data, image_base=0x400000, entry_rva=0x8BA0AE):
    payload = bin_data[0x1000:]          # 节数据：file 0x1000 起
    vsize = len(payload)
    # ---- DOS 头 ----
    dos = bytearray(0x40)
    dos[0:2] = b'MZ'
    struct.pack_into('<I', dos, 0x3C, 0x100)   # e_lfanew
    # ---- NT 头 ----
    nt = bytearray()
    nt += b'PE\x00\x00'
    # FileHeader (20)
    nt += struct.pack('<HHIIIHH', 0x14c, 1, 0, 0, 0, 0xE0, 0x102)
    # OptionalHeader PE32 (224)
    opt = bytearray(0xE0)
    struct.pack_into('<H', opt, 0, 0x10B)           # Magic
    struct.pack_into('<I', opt, 16, entry_rva)       # AddressOfEntryPoint
    struct.pack_into('<I', opt, 20, 0x1000)          # BaseOfCode
    struct.pack_into('<I', opt, 24, 0x1000)          # BaseOfData
    struct.pack_into('<I', opt, 28, image_base)      # ImageBase
    struct.pack_into('<I', opt, 32, 0x1000)          # SectionAlignment
    struct.pack_into('<I', opt, 36, 0x200)           # FileAlignment
    struct.pack_into('<H', opt, 40, 4); struct.pack_into('<H', opt, 42, 0)   # OS ver
    struct.pack_into('<H', opt, 44, 0); struct.pack_into('<H', opt, 46, 0)   # Image ver
    struct.pack_into('<H', opt, 48, 4); struct.pack_into('<H', opt, 50, 0)   # Subsys ver
    struct.pack_into('<I', opt, 52, 0)               # Win32VersionValue
    struct.pack_into('<I', opt, 56, 0x1000 + vsize)  # SizeOfImage
    struct.pack_into('<I', opt, 60, 0x400)           # SizeOfHeaders
    struct.pack_into('<I', opt, 64, 0)               # CheckSum
    struct.pack_into('<H', opt, 68, 2)               # Subsystem = GUI
    struct.pack_into('<H', opt, 70, 0)               # DllCharacteristics
    struct.pack_into('<I', opt, 72, 0x100000)        # StackReserve
    struct.pack_into('<I', opt, 76, 0x1000)          # StackCommit
    struct.pack_into('<I', opt, 80, 0x100000)        # HeapReserve
    struct.pack_into('<I', opt, 84, 0x1000)          # HeapCommit
    struct.pack_into('<I', opt, 88, 0)               # LoaderFlags
    struct.pack_into('<I', opt, 92, 16)              # NumberOfRvaAndSizes
    # 可选头 PE32 共 224 字节，末 128 字节即 16 个数据目录（默认已为 0）
    nt += opt
    # ---- 节头 (.flat) ----
    sh = bytearray(40)
    sh[0:8] = b'.flat\x00\x00\x00'
    struct.pack_into('<I', sh, 8, vsize)      # VirtualSize
    struct.pack_into('<I', sh, 12, 0x1000)    # VirtualAddress
    struct.pack_into('<I', sh, 16, vsize)     # SizeOfRawData
    struct.pack_into('<I', sh, 20, 0x1000)    # PointerToRawData
    struct.pack_into('<I', sh, 36, 0x60000020)# Characteristics: CODE|EXEC|READ
    # ---- 拼装 ----
    header = bytearray(0x1000)        # 与节 RawOff=0x1000 对齐，payload 从 0x1000 起
    header[0:0x40] = dos
    header[0x100:0x100+len(nt)] = nt
    header[0x100+len(nt):0x100+len(nt)+40] = sh
    out = bytes(header) + payload
    return out

def main():
    binp = sys.argv[1] if len(sys.argv) > 1 else 'tools/unpack/mx_unpacked.bin'
    outp = sys.argv[2] if len(sys.argv) > 2 else 'tools/unpack/mx_flat.exe'
    data = open(binp, 'rb').read()
    out = build_flat_pe(data)
    open(outp, 'wb').write(out)
    print('wrote %s (%d bytes) base=0x400000 entry_rva=0x8BA0AE' % (outp, len(out)))

if __name__ == '__main__':
    main()
