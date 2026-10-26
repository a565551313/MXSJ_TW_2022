"""造一個最小可解析的假 DLL 記憶體映像（供 Unicorn 裡的「殼」去解析）。

殼不直接讀 IAT，而是 `GetModuleHandle` + 解析 PE 匯出表來拿 API 位址。要讓它
繼續往下走，就得給它一張結構合法、能按名字查到的匯出表。這裡的映像
**RVA == 檔案偏移**（直接寫進 Unicorn 記憶體，不經過檔案），所以只要把
DOS/PE 頭、一個 `.edata` 節和匯出目錄擺在正確的 RVA 上即可。

限度：沒有重定位、沒有資源、沒有 `.text`；只保證 `pefile` 與殼的
「找 e_lfanew → PE 簽章 → 資料目錄 → 匯出表」這條路能走通。
"""

from __future__ import annotations

import struct

SIZE = 0x4000  # 最小映像大小；實際大小依匯出名字數量自動放大


def build_module(dll_name: str, exports: dict[str, int], default: int) -> bytes:
    """回傳 `SIZE` 位元組的假 DLL 映像。

    `exports`：匯出名字 → 絕對位址（會寫進 AddressOfFunctions）。
    `default`：留給呼叫端的「未列出名字」位址，本函式不使用，只寫進
    `NumberOfFunctions` 之後的空位，方便呼叫端自己決定要不要放。
    """
    names = sorted(exports)
    count = len(names)

    edata = 0x1000
    funcs = edata + 0x28
    name_ptr = funcs + 4 * count
    ordinals = name_ptr + 4 * count
    strings = ordinals + 2 * count

    blob = bytearray(dll_name.encode("ascii", "replace") + b"\x00")
    offsets = {}
    for name in names:
        offsets[name] = len(blob)
        blob += name.encode("ascii", "replace") + b"\x00"
    while len(blob) % 4:
        blob += b"\x00"

    # 映像大小按需要自動放大（節與 SizeOfImage 都要跟著走）
    total = (strings + len(blob) + 0xFFF) & ~0xFFF
    total = max(total, SIZE)
    buf = bytearray(total)

    # DOS 頭
    buf[0:2] = b"MZ"
    struct.pack_into("<I", buf, 0x3C, 0x80)
    # PE 簽章 + COFF 頭（1 個節、可執行、DLL）
    buf[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into(
        "<HHIIIHH", buf, 0x84, 0x14C, 1, 0, 0, 0, 0xE0, 0x2102
    )
    opt = 0x98
    struct.pack_into("<H", buf, opt + 0x00, 0x10B)  # PE32
    struct.pack_into("<I", buf, opt + 0x04, total - edata)  # SizeOfCode
    struct.pack_into("<I", buf, opt + 0x08, 0)  # SizeOfInitializedData
    struct.pack_into("<I", buf, opt + 0x0C, 0)  # SizeOfUninitializedData
    struct.pack_into("<I", buf, opt + 0x10, edata)  # AddressOfEntryPoint
    struct.pack_into("<I", buf, opt + 0x14, edata)  # BaseOfCode
    struct.pack_into("<I", buf, opt + 0x18, edata)  # BaseOfData
    struct.pack_into("<I", buf, opt + 0x1C, 0x50000000)  # ImageBase（佔位）
    struct.pack_into("<I", buf, opt + 0x20, 0x1000)  # SectionAlignment
    struct.pack_into("<I", buf, opt + 0x24, 0x200)  # FileAlignment
    struct.pack_into("<H", buf, opt + 0x30, 6)  # MajorSubsystemVersion
    struct.pack_into("<I", buf, opt + 0x38, total)  # SizeOfImage
    struct.pack_into("<I", buf, opt + 0x3C, 0x400)  # SizeOfHeaders
    struct.pack_into("<H", buf, opt + 0x44, 3)  # Subsystem = console
    struct.pack_into("<H", buf, opt + 0x46, 0)  # DllCharacteristics
    struct.pack_into("<I", buf, opt + 0x48, 0x100000)  # SizeOfStackReserve
    struct.pack_into("<I", buf, opt + 0x4C, 0x1000)  # SizeOfStackCommit
    struct.pack_into("<I", buf, opt + 0x50, 0x100000)  # SizeOfHeapReserve
    struct.pack_into("<I", buf, opt + 0x54, 0x1000)  # SizeOfHeapCommit
    struct.pack_into("<I", buf, opt + 0x5C, 16)  # NumberOfRvaAndSizes
    struct.pack_into("<II", buf, opt + 0x60, edata, 0x400)  # 匯出目錄（第 0 項）

    section = opt + 0xE0
    buf[section:section + 8] = b".edata\x00\x00"
    struct.pack_into(
        "<IIIIIIHHI",
        buf,
        section + 8,
        total - edata,  # VirtualSize
        edata,  # VirtualAddress
        total - edata,  # SizeOfRawData
        edata,  # PointerToRawData（RVA == 偏移，直接寫進記憶體）
        0, 0, 0, 0,
        0x40000040,
    )

    # IMAGE_EXPORT_DIRECTORY
    struct.pack_into(
        "<IIHHIIIIIII",
        buf, edata,
        0,  # Characteristics
        0,  # TimeDateStamp
        0,  # MajorVersion
        0,  # MinorVersion
        strings,  # Name（DLL 名）
        1,  # Base（ordinal 起點）
        max(count, 1),  # NumberOfFunctions
        count,  # NumberOfNames
        funcs,
        name_ptr,
        ordinals,
    )
    if not count:
        struct.pack_into("<I", buf, funcs, default)
    for index, name in enumerate(names):
        struct.pack_into("<I", buf, funcs + 4 * index, exports[name])
        struct.pack_into("<I", buf, name_ptr + 4 * index, strings + offsets[name])
        struct.pack_into("<H", buf, ordinals + 2 * index, index)
    buf[strings:strings + len(blob)] = blob
    return bytes(buf)
