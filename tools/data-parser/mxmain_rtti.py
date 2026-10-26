#!/usr/bin/env python3
"""把 mxmain.dll 的明文 RTTI 还原成「类 → 基类链 → 虚析构 → 写 vfptr 位置」四表。

為什麼要有這個工具：`mxmain.dll` 沒有符號表也沒有 PDB，54% 鏡像在 `_dyprot0/1` 殼裡
（見 `notes/client_binary_reversibility.md` §2）。明文區唯一成體系的「類清單」就是
MSVC RTTI：`.data` 裡的 TypeDescriptor、`.rdata` 裡的 CompleteObjectLocator、
ClassHierarchyDescriptor、BaseClassArray 與虛表。本工具只做**只讀解析**，
不反編譯、不執行任何被解析出來的東西。

    python3 tools/data-parser/mxmain_rtti.py mxmain.dll --summary
    python3 tools/data-parser/mxmain_rtti.py mxmain.dll --json /tmp/rtti.json \
        --md /tmp/rtti.md

輸入檔全程唯讀；不給 `--json`/`--md` 就只印摘要、不寫盤。

## 實測出來的坑（改這個工具前先看）

1. **指標是絕對 VA，不是 RVA。** 這顆映像首選基址 0x400000，RTTI 裡的 `pTypeDescriptor`
   / `pClassHierarchyDescriptor` / 虛表前一個槽存的 COL 全是 `ImageBase + RVA`。
   照 SDK 註釋當 RVA 用會一個都對不上。
2. **TypeDescriptor 是 `[vfptr][spare][name]` 共 8+N 位元組**，352 條的 `vfptr` 都一樣
   值 `0x77cb64`（`??_7type_info@@6B@`，落在 `.rdata`）。所以「名字前 8 位元組」
   就是結構起點，不用另外找表頭。
3. **BaseClassDescriptor 步長實測是 28 位元組（7 個 dword），不是 SDK 寫的 24。**
   依據：同一條 BCA 的兩個目標相差 28；照 28 解出來的欄位順序
   `[pTD][numContainedBases][mdisp][pdisp][vdisp][attributes][pCHD]` 能一路把
   std 的 `failure@ios_base` → `system_error` → `_System_error` → `runtime_error`
   → `exception` 五層鏈完全解對（見測試 `test_std_exception_chain_order`）。
4. **BCA[0] 是類自己**，之後才是基底，順序是深度優先。把 BCA[0] 當基底會多算一層。
5. **明文虛表只有一個槽**：槽位 0 是 scalar deleting destructor，槽位 -1 是 COL。
   也就是這批類別除了虛析構之外沒有別的虛函式。**不能把槽數當方法數**，
   真正的業務方法要靠構造/析構函式的成員偏移或腳本綁定表另找。
6. `movl $vftable,(%reg)`（`C7 /0 imm32`）是寫 vfptr 的指令，構造函式與
   析構函式都會有；它只能給「類 → 指令位址」的錨點，不等於函式邊界。
   本工具用「往前找最近一段 0xCC 填充的結尾」估函式起點，並額外回報
   `frame_pointer` 表示起點是否真的是 `55 8B EC`，估不出來就留 None，不猜。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

IMAGE_BASE = 0x400000
SECTION_HEADER_SIZE = 40
# PE 節名 → 這個工具關心的用途；不在表裡的一樣會解析，只是不加標籤
SECTION_ROLES = {
    ".text": "code",
    ".rdata": "rtti",
    ".data": "type_descriptors",
    "_dyprot0": "protected",
    "_dyprot1": "protected",
    ".rsrc": "resources",
}


@dataclass(frozen=True)
class Section:
    name: str
    va: int
    vsize: int
    raw_offset: int
    raw_size: int

    # 注意：Section.va 存的是**絕對 VA**（ImageBase + RVA）。RTTI 裡的指標全是絕對 VA，
    # 用 RVA 混算會一個都對不上（模組 docstring 第 1 條）。
    def contains(self, va: int) -> bool:
        return self.va <= va < self.va + self.vsize

    @property
    def role(self) -> str:
        return SECTION_ROLES.get(self.name, "other")


@dataclass
class BaseClass:
    """RTTIBaseClassDescriptor 的欄位；欄位順序見模組 docstring 第 3 條。"""

    name: str
    type_descriptor_va: int
    num_contained_bases: int
    mdisp: int
    pdisp: int
    vdisp: int
    attributes: int
    class_hierarchy_va: int

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "type_descriptor_va": hex(self.type_descriptor_va),
            "num_contained_bases": self.num_contained_bases,
            "mdisp": self.mdisp,
            "pdisp": signed(self.pdisp),
            "vdisp": self.vdisp,
            "attributes_hex": hex(self.attributes),
            "class_hierarchy_va": hex(self.class_hierarchy_va),
        }


@dataclass
class ClassRecord:
    name: str
    type_descriptor_va: int
    object_locator_va: int | None = None
    class_hierarchy_va: int | None = None
    vftable_va: int | None = None
    virtual_slots: list[int] = field(default_factory=list)
    vfptr_writes: list[dict] = field(default_factory=list)
    bases: list[BaseClass] = field(default_factory=list)
    hierarchy_error: str | None = None

    @property
    def namespace(self) -> str:
        core = self.name[4:] if self.name.startswith(".?A") else self.name
        parts = [p for p in core.split("@") if p]
        # mangled 名的第一段是類名，之後可能還有 模板參數 殘留
        return parts[1] if len(parts) > 1 else ""

    @property
    def dtor_va(self) -> int | None:
        return self.virtual_slots[0] if self.virtual_slots else None

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "namespace": self.namespace,
            "type_descriptor_va": hex(self.type_descriptor_va),
            "object_locator_va": opt_hex(self.object_locator_va),
            "class_hierarchy_va": opt_hex(self.class_hierarchy_va),
            "vftable_va": opt_hex(self.vftable_va),
            "virtual_slots": [hex(v) for v in self.virtual_slots],
            "vfptr_writes": self.vfptr_writes,
            "bases": [b.as_dict() for b in self.bases],
            "hierarchy_error": self.hierarchy_error,
        }


def signed(value: int) -> int:
    return value - (1 << 32) if value >= 1 << 31 else value


def opt_hex(value: int | None) -> str | None:
    return None if value is None else hex(value)


class PeImage:
    """只解析到「節表 + 讀 dword」的程度；本工具不需要匯入/匯出/資源。"""

    def __init__(self, data: bytes, path: Path | None = None):
        self.data = data
        self.path = path
        if data[:2] != b"MZ":
            raise ValueError("不是 MZ 映像")
        e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
        if data[e_lfanew : e_lfanew + 4] != b"PE\x00\x00":
            raise ValueError("找不到 PE 簽名")
        coff = e_lfanew + 4
        machine, count = struct.unpack_from("<HH", data, coff)
        if machine != 0x14C:
            raise ValueError(f"只支援 i386（PE32），這個是 machine=0x{machine:04x}")
        opt_size = struct.unpack_from("<H", data, coff + 16)[0]
        opt = coff + 20
        if struct.unpack_from("<H", data, opt)[0] != 0x10B:
            raise ValueError("只支援 PE32 可選頭")
        self.image_base = struct.unpack_from("<I", data, opt + 28)[0]
        table = opt + opt_size
        self.sections: list[Section] = []
        for index in range(count):
            at = table + index * SECTION_HEADER_SIZE
            name = data[at : at + 8].rstrip(b"\x00").decode("latin-1")
            vsize, rva, raw_size, raw_off = struct.unpack_from("<IIII", data, at + 8)
            self.sections.append(
                Section(name, self.image_base + rva, vsize, raw_off, raw_size)
            )

    def section_of(self, va: int) -> Section | None:
        for section in self.sections:
            if section.contains(va):
                return section
        return None

    def section_role(self, va: int) -> str | None:
        section = self.section_of(va)
        return None if section is None else section.role

    def va_to_offset(self, va: int) -> int | None:
        section = self.section_of(va)
        if section is None:
            return None
        delta = va - section.va
        if delta >= section.raw_size:
            return None  # 落在虛擬填充裡，沒有檔案位元組可讀
        return section.raw_offset + delta

    def offset_to_va(self, offset: int) -> int | None:
        for section in self.sections:
            end = section.raw_offset + section.raw_size
            if section.raw_offset <= offset < end:
                return section.va + (offset - section.raw_offset)
        return None

    def u32(self, va: int) -> int | None:
        offset = self.va_to_offset(va)
        if offset is None:
            return None
        return struct.unpack_from("<I", self.data, offset)[0]

    def read(self, va: int, size: int) -> bytes | None:
        offset = self.va_to_offset(va)
        if offset is None or offset + size > len(self.data):
            return None
        return self.data[offset : offset + size]

    def cstring(self, va: int, limit: int = 512) -> str | None:
        # 只讀到所在節的實際位元組結尾：跨節讀取會失敗（例如節尾的名字）
        section = self.section_of(va)
        offset = self.va_to_offset(va)
        if section is None or offset is None:
            return None
        room = min(limit, section.raw_offset + section.raw_size - offset)
        raw = self.read(va, room)
        if raw is None:
            return None
        end = raw.find(b"\x00")
        if end < 0:
            return None
        return raw[:end].decode("latin-1")

    def find_u32(self, value: int) -> list[int]:
        """回傳所有存放 `value`（小端 4 位元組）的 VA。"""
        needle = struct.pack("<I", value & 0xFFFFFFFF)
        hits: list[int] = []
        start = 0
        while True:
            at = self.data.find(needle, start)
            if at < 0:
                return hits
            va = self.offset_to_va(at)
            if va is not None:
                hits.append(va)
            start = at + 1


def parse_type_descriptors(image: PeImage) -> dict[int, str]:
    """掃 `.data` 裡「8 位元組頭 + `.?A` 名字」的 TypeDescriptor。"""
    found: dict[int, str] = {}
    data = image.data
    start = 0
    while True:
        at = data.find(b".?A", start)
        if at < 0:
            return found
        start = at + 1
        if at < 8 or data[at + 3 : at + 4] not in (b"U", b"V"):
            continue
        if data[at - 4 : at] != b"\x00\x00\x00\x00":
            continue
        name_va = image.offset_to_va(at)
        if name_va is None:
            continue
        role = image.section_role(name_va)
        if role != "type_descriptors":
            continue
        name = image.cstring(name_va)
        if not name or not name.startswith(".?A"):
            continue
        found[name_va - 8] = name


def parse_object_locators(
    image: PeImage, type_descriptors: dict[int, str]
) -> dict[int, tuple[int, int]]:
    """在 `.rdata` 找 `[0][0][0][pTD][pCHD]` 形狀的 CompleteObjectLocator。"""
    locators: dict[int, tuple[int, int]] = {}
    for section in image.sections:
        if section.role != "rtti":
            continue
        at = section.raw_offset
        end = min(at + section.raw_size, len(image.data)) - 20
        while at <= end:
            sig, offset, cd, p_td, p_chd = struct.unpack_from("<IIIII", image.data, at)
            if (
                sig == 0
                and offset == 0
                and cd == 0
                and p_td in type_descriptors
                and image.section_role(p_chd) == "rtti"
            ):
                locators[p_td] = (image.offset_to_va(at), p_chd)
            at += 4
    return locators


def parse_hierarchy(
    image: PeImage, type_descriptors: dict[int, str], chd_va: int
) -> tuple[list[BaseClass], str | None]:
    """解 ClassHierarchyDescriptor → BaseClassArray → 每個基底描述符。"""
    header = image.read(chd_va, 16)
    if header is None:
        return [], "CHD 不可讀"
    _sig, _attr, count, base_array_va = struct.unpack("<IIII", header)
    if not 0 < count <= 256:
        return [], f"numBaseClasses={count} 不合理"
    bases: list[BaseClass] = []
    for index in range(count):
        entry_va = base_array_va + index * 4
        entry = image.u32(entry_va)
        if entry is None:
            return bases, f"BCA[{index}] 不可讀"
        record = image.read(entry, 28)
        if record is None:
            return bases, f"BCD[{index}] 不可讀"
        p_td, num, mdisp, pdisp, vdisp, attrs, p_chd = struct.unpack("<IIIIIII", record)
        bases.append(
            BaseClass(
                name=type_descriptors.get(p_td, f"<未登記 TD {p_td:#x}>"),
                type_descriptor_va=p_td,
                num_contained_bases=num,
                mdisp=signed(mdisp),
                pdisp=pdisp,
                vdisp=vdisp,
                attributes=attrs,
                class_hierarchy_va=p_chd,
            )
        )
    return bases, None


# 函式不會以這兩個位元組開頭：0x00 是 `add [eax],al`（MSVC 不生成），0x0F 是雙位元組
# 前綴。實測這條規則是必要的：`CMapHeroObject` 的虛表後面緊跟一段方法名字串
# （`GetHeight` / `ClickID` / `SetText`…），字串 "ii" 會被讀成 0x00696969，
# 落在 `.text` 內、看起來像指標。用「槽位目標必須是像樣的指令起點」把它擋掉。
IMPOSSIBLE_ENTRY_BYTES = frozenset({0x00, 0x0F})


def _looks_like_code_entry(image: PeImage, va: int) -> bool:
    """粗判「這個位址像不像函式入口」：在 `.text` 內，且不以不可能的位元組開頭。

    這裡**沒有**要求 4 位元組對齊：實測 std 例外的 scalar deleting destructor
    入口就是 0x5c6085（奇數位址），對齊假設會把 52 個類別的虛表整個砍掉。
    """
    if image.section_role(va) != "code":
        return False
    offset = image.va_to_offset(va)
    if offset is None:
        return False
    return image.data[offset] not in IMPOSSIBLE_ENTRY_BYTES


def parse_vftables(
    image: PeImage, locators: dict[int, tuple[int, int]]
) -> tuple[dict[int, int], dict[int, list[int]]]:
    """虛表 = 存放 COL 指標的位置 +4；槽位一直讀到「不像函式入口」的 dword 為止。"""
    vftable_of: dict[int, int] = {}
    slots_of: dict[int, list[int]] = {}
    for td_va, (col_va, _chd) in locators.items():
        for ref_va in image.find_u32(col_va):
            if image.section_role(ref_va) != "rtti":
                continue
            slots: list[int] = []
            slot_va = ref_va + 4
            while True:
                target = image.u32(slot_va)
                if target is None or not _looks_like_code_entry(image, target):
                    break
                slots.append(target)
                slot_va += 4
                if len(slots) > 256:
                    break
            if slots and td_va not in vftable_of:
                vftable_of[td_va] = ref_va + 4
                slots_of[td_va] = slots
    return vftable_of, slots_of


def _function_start(image: PeImage, site_va: int) -> dict:
    """往前找最近的 0xCC 填充，取它後面第一個位元組當函式起點（估計值）。

    MSVC 在 `.text` 裡用 0xCC 填充到 16 位元組邊界，所以「最近的 0xCC 之後」
    通常就是當前函式的入口；但如果這個函式前面沒有填充（例如緊接 `ret`），
    就會指到上一個函式，因此回報 `frame_pointer_prologue` 讓人自行判斷可信度。
    """
    offset = image.va_to_offset(site_va)
    if offset is None:
        return {"function_start_va": None, "frame_pointer_prologue": None}
    cursor = offset
    while cursor > 0 and image.data[cursor] != 0xCC:
        cursor -= 1
    if cursor == 0 or cursor == offset:
        return {"function_start_va": None, "frame_pointer_prologue": None}
    start_va = image.offset_to_va(cursor + 1)
    if start_va is None or image.section_role(start_va) != "code":
        return {"function_start_va": None, "frame_pointer_prologue": None}
    prologue = image.read(start_va, 3) == b"\x55\x8b\xec"
    return {"function_start_va": hex(start_va), "frame_pointer_prologue": prologue}


def find_vfptr_writes(image: PeImage, vftable_va: int) -> list[dict]:
    """找 `.text` 裡 `mov r/m32, imm32`（C7 /0）把這個虛表寫進物件的位置。"""
    sites: list[dict] = []
    needle = struct.pack("<I", vftable_va)
    start = 0
    while True:
        at = image.data.find(needle, start)
        if at < 0:
            return sites
        start = at + 1
        if at < 2 or image.data[at - 2] != 0xC7:
            continue
        modrm = image.data[at - 1]
        if (modrm >> 3) & 0x7:  # reg 欄位不是 /0 → 不是 mov imm32
            continue
        site_va = image.offset_to_va(at)
        if site_va is None or image.section_role(site_va) != "code":
            continue
        site = {"site_va": hex(site_va), "modrm": f"0x{modrm:02x}"}
        site.update(_function_start(image, site_va))
        sites.append(site)


def build_report(path: Path) -> dict:
    data = path.read_bytes()
    image = PeImage(data, path)
    type_descriptors = parse_type_descriptors(image)
    locators = parse_object_locators(image, type_descriptors)
    vftables, slots = parse_vftables(image, locators)

    records: list[ClassRecord] = []
    for td_va, name in sorted(type_descriptors.items(), key=lambda kv: kv[1]):
        record = ClassRecord(name=name, type_descriptor_va=td_va)
        if td_va in locators:
            col_va, chd_va = locators[td_va]
            record.object_locator_va = col_va
            record.class_hierarchy_va = chd_va
            record.bases, record.hierarchy_error = parse_hierarchy(
                image, type_descriptors, chd_va
            )
        if td_va in vftables:
            record.vftable_va = vftables[td_va]
            record.virtual_slots = slots[td_va]
            record.vfptr_writes = find_vfptr_writes(image, vftables[td_va])
        records.append(record)

    namespaces: dict[str, int] = {}
    for record in records:
        key = record.namespace or "(global)"
        namespaces[key] = namespaces.get(key, 0) + 1

    summary = {
        "input": path.name,
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "image_base": hex(image.image_base),
        "sections": [
            {
                "name": s.name,
                "va": hex(s.va),
                "vsize": s.vsize,
                "role": s.role,
            }
            for s in image.sections
        ],
        "type_descriptors": len(type_descriptors),
        "with_object_locator": len(locators),
        "with_vftable": len(vftables),
        "vftable_slot_counts": _count(slots.values()),
        "with_base_chain": sum(1 for r in records if r.bases),
        "with_vfptr_writes": sum(1 for r in records if r.vfptr_writes),
        "namespaces": dict(sorted(namespaces.items(), key=lambda kv: (-kv[1], kv[0]))),
        "hierarchy_errors": [
            {"name": r.name, "error": r.hierarchy_error}
            for r in records
            if r.hierarchy_error
        ],
    }
    return {"summary": summary, "classes": [r.as_dict() for r in records]}


def _count(values) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        key = str(len(value))
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: int(kv[0])))


def render_markdown(report: dict) -> str:
    """把 JSON 報告排成可直接貼進 notes/ 的表；不含任何解釋文字。"""
    summary = report["summary"]
    source = summary["input"]
    lines = [f"<!-- mxmain_rtti.py：{source} -->", ""]
    lines.append(
        f"輸入 `{summary['input']}`（{summary['size']:,} B，SHA-256 "
        f"`{summary['sha256']}`）：TypeDescriptor {summary['type_descriptors']}、"
        f"有 COL {summary['with_object_locator']}、有虛表 {summary['with_vftable']}、"
        f"有基底鏈 {summary['with_base_chain']}、有 vfptr 寫入點 "
        f"{summary['with_vfptr_writes']}。虛表槽數分布 "
        f"{summary['vftable_slot_counts']}。"
    )
    lines.append("")
    lines.append("| 類別 | 命名空間 | TD | COL | 虛表 | 虛析構 | 基底（深度優先） |")
    lines.append("|---|---|---|---|---|---|---|")
    for item in report["classes"]:
        bases = [
            f"{b['name'][4:] if b['name'].startswith('.?A') else b['name']}"
            f"@{b['mdisp']}"
            for b in item["bases"]
        ]
        chain = " → ".join(bases) if bases else "—"
        lines.append(
            "| {name} | {ns} | {td} | {col} | {vt} | {dtor} | {chain} |".format(
                name=item["name"][4:],
                ns=item["namespace"] or "(global)",
                td=item["type_descriptor_va"],
                col=item["object_locator_va"] or "—",
                vt=item["vftable_va"] or "—",
                dtor=item["virtual_slots"][0] if item["virtual_slots"] else "—",
                chain=chain,
            )
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="解析 mxmain.dll 的明文 MSVC RTTI（只讀）"
    )
    parser.add_argument("image", type=Path, help="PE 映像，例如 mxmain.dll")
    parser.add_argument("--summary", action="store_true", help="只印摘要（預設行為）")
    parser.add_argument("--json", type=Path, help="把完整報告寫成 JSON")
    parser.add_argument("--md", type=Path, help="把類別表寫成 Markdown")
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="摘要裡最多列幾個類別（0 = 不列）",
    )
    args = parser.parse_args(argv)

    report = build_report(args.image)
    summary = report["summary"]
    print(f"輸入：{summary['input']}  {summary['size']:,} B")
    print(f"SHA-256：{summary['sha256']}")
    print(f"ImageBase：{summary['image_base']}")
    print(
        "TypeDescriptor {td} / COL {col} / 虛表 {vt} / 基底鏈 {bc}"
        " / vfptr 寫入 {wf}".format(
            td=summary["type_descriptors"],
            col=summary["with_object_locator"],
            vt=summary["with_vftable"],
            bc=summary["with_base_chain"],
            wf=summary["with_vfptr_writes"],
        )
    )
    print(f"虛表槽數分布：{summary['vftable_slot_counts']}")
    print("命名空間：")
    for name, count in summary["namespaces"].items():
        print(f"  {count:4d}  {name}")
    if summary["hierarchy_errors"]:
        print(f"基底鏈解析失敗：{len(summary['hierarchy_errors'])} 條")
        for item in summary["hierarchy_errors"][:10]:
            print(f"  {item['name']}  {item['error']}")
    if args.limit:
        print()
        for item in report["classes"][: args.limit]:
            chain = " → ".join(b["name"] for b in item["bases"]) or "—"
            print(f"{item['name']}  TD={item['type_descriptor_va']}  基底={chain}")
    if args.json:
        args.json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"JSON → {args.json}")
    if args.md:
        args.md.write_text(render_markdown(report), encoding="utf-8")
        print(f"Markdown → {args.md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
