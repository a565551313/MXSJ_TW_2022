from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from pathlib import Path

import pefile


ROOT = Path(r"D:\Lager\夢想世界")
OUT = Path(r"D:\Lager\夢想世界\work\dream-world-connect-login-map\evidence")
TARGETS = ["mx.exe", "IMProtocol.dll", "gameplayer.exe", "mxmain.dll"]
KEYWORDS = [
    "connect",
    "socket",
    "send",
    "recv",
    "http",
    "https",
    "wininet",
    "winhttp",
    "login",
    "account",
    "auth",
    "password",
    "user",
    "command",
    "opcode",
    "dispatch",
    "protocol",
    "map",
    "scene",
    "world",
    "load",
    "resource",
    "gate",
    "server",
    "port",
    "host",
    "select",
    "poll",
]
NETWORK_DLLS = {
    "WS2_32.dll",
    "WININET.dll",
    "WINHTTP.dll",
    "URLMON.dll",
    "HTTPAPI.dll",
    "DNSAPI.dll",
    "IPHLPAPI.dll",
    "SECUR32.dll",
    "CRYPT32.dll",
    "NSI.dll",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def ascii_strings(data: bytes, minimum: int = 4):
    pattern = re.compile(rb"[\x20-\x7e]{%d,}" % minimum)
    return [(m.start(), m.group().decode("ascii", "replace")) for m in pattern.finditer(data)]


def utf16le_strings(data: bytes, minimum: int = 4):
    pattern = re.compile((rb"(?:[\x20-\x7e]\x00){%d,}") % minimum)
    result = []
    for match in pattern.finditer(data):
        raw = match.group()
        result.append((match.start(), raw.decode("utf-16le", "replace")))
    return result


def section_for_offset(pe: pefile.PE, offset: int) -> str | None:
    for section in pe.sections:
        start = section.PointerToRawData
        end = start + max(section.SizeOfRawData, section.Misc_VirtualSize)
        if start <= offset < end:
            return section.Name.rstrip(b"\x00").decode("ascii", "replace")
    return None


def section_for_rva(pe: pefile.PE, rva: int) -> str | None:
    for section in pe.sections:
        start = section.VirtualAddress
        end = start + max(section.SizeOfRawData, section.Misc_VirtualSize)
        if start <= rva < end:
            return section.Name.rstrip(b"\x00").decode("ascii", "replace")
    return None


def entropy(raw: bytes) -> float:
    if not raw:
        return 0.0
    counts = [0] * 256
    for value in raw:
        counts[value] += 1
    size = len(raw)
    return -sum((count / size) * math.log2(count / size) for count in counts if count)


def decode_c_string(data: bytes, offset: int) -> str:
    end = data.find(b"\x00", offset)
    if end < 0:
        end = min(len(data), offset + 256)
    return data[offset:end].decode("utf-8", "replace")


def rich_header(pe: pefile.PE) -> dict:
    result = {"present": False}
    rich = getattr(pe, "RICH_HEADER", None)
    if not rich:
        return result
    result["present"] = True
    result["offset"] = rich.get("offset")
    result["key"] = f"0x{rich.get('key', 0):08X}"
    result["clear_data_hex"] = rich.get("clear_data", b"").hex()
    result["raw_data_hex"] = rich.get("raw_data", b"").hex()
    return result


def debug_entries(pe: pefile.PE) -> list[dict]:
    entries = []
    if not hasattr(pe, "DIRECTORY_ENTRY_DEBUG"):
        return entries
    for entry in pe.DIRECTORY_ENTRY_DEBUG:
        dbg = entry.struct
        item = {
            "type": int(dbg.Type),
            "size": int(dbg.SizeOfData),
            "timestamp": int(dbg.TimeDateStamp),
            "pointer_to_raw_data": int(dbg.PointerToRawData),
            "address_of_raw_data": int(dbg.AddressOfRawData),
        }
        if dbg.Type == 2:
            raw = pe.__data__[dbg.PointerToRawData : dbg.PointerToRawData + dbg.SizeOfData]
            if raw.startswith(b"RSDS") and len(raw) >= 24:
                guid = raw[4:20]
                age = struct.unpack_from("<I", raw, 20)[0]
                item["format"] = "CodeView RSDS"
                item["guid"] = (
                    f"{guid[0:4][::-1].hex()}-{guid[4:6][::-1].hex()}-"
                    f"{guid[6:8][::-1].hex()}-{guid[8:10].hex()}-{guid[10:16].hex()}"
                )
                item["age"] = age
                item["pdb_path"] = decode_c_string(raw, 24)
            elif raw.startswith(b"NB10") and len(raw) >= 16:
                item["format"] = "CodeView NB10"
                item["pdb_path"] = decode_c_string(raw, 16)
            else:
                item["format"] = "non-CodeView or truncated"
        entries.append(item)
    return entries


def version_info(pe: pefile.PE) -> dict:
    result = {}
    try:
        for item in pe.FileInfo:
            if not isinstance(item, list):
                continue
            for block in item:
                if getattr(block, "Key", b"") == b"StringFileInfo":
                    for table in block.StringTable:
                        for key, value in table.entries.items():
                            result[key.decode("utf-8", "replace")] = value.decode(
                                "utf-8", "replace"
                            )
    except AttributeError:
        pass
    return result


def imports(pe: pefile.PE) -> list[dict]:
    result = []
    if not hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
        return result
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        dll = entry.dll.decode("ascii", "replace")
        functions = []
        for imp in entry.imports:
            name = imp.name.decode("ascii", "replace") if imp.name else f"ordinal_{imp.ordinal}"
            functions.append(
                {
                    "name": name,
                    "ordinal": imp.ordinal,
                    "address": f"0x{imp.address:08X}",
                }
            )
        result.append({"dll": dll, "network_related": dll.upper() in NETWORK_DLLS, "functions": functions})
    return result


def exports(pe: pefile.PE) -> list[dict]:
    result = []
    if not hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
        return result
    for item in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        name = item.name.decode("ascii", "replace") if item.name else None
        result.append(
            {
                "name": name,
                "ordinal": int(item.ordinal),
                "address": f"0x{item.address:08X}",
                "forwarder": item.forwarder.decode("ascii", "replace") if item.forwarder else None,
            }
        )
    return result


def analyze(path: Path) -> dict:
    data = path.read_bytes()
    pe = pefile.PE(str(path), fast_load=False)
    pe.parse_data_directories()
    strings = ascii_strings(data) + utf16le_strings(data)
    strings.sort(key=lambda item: item[0])
    keyword_hits = []
    for offset, value in strings:
        lowered = value.lower()
        matched = [keyword for keyword in KEYWORDS if keyword in lowered]
        if matched:
            keyword_hits.append(
                {
                    "offset": f"0x{offset:08X}",
                    "section": section_for_offset(pe, offset),
                    "keywords": matched,
                    "text": value[:512],
                }
            )
    section_data = []
    for section in pe.sections:
        raw = section.get_data()
        section_data.append(
            {
                "name": section.Name.rstrip(b"\x00").decode("ascii", "replace"),
                "virtual_address": f"0x{section.VirtualAddress:08X}",
                "virtual_size": int(section.Misc_VirtualSize),
                "raw_pointer": f"0x{section.PointerToRawData:08X}",
                "raw_size": int(section.SizeOfRawData),
                "characteristics": f"0x{section.Characteristics:08X}",
                "entropy": round(entropy(raw), 4),
            }
        )
    file_header = pe.FILE_HEADER
    optional = pe.OPTIONAL_HEADER
    dirs = {}
    for index, directory in enumerate(optional.DATA_DIRECTORY):
        dirs[str(index)] = {
            "rva": f"0x{directory.VirtualAddress:08X}",
            "size": int(directory.Size),
        }
    imports_data = imports(pe)
    network_imports = [
        {"dll": item["dll"], "functions": item["functions"]}
        for item in imports_data
        if item["network_related"]
    ]
    return {
        "file": path.name,
        "path": str(path),
        "size": len(data),
        "sha256": sha256(path),
        "pe": {
            "machine": f"0x{file_header.Machine:04X}",
            "machine_name": pefile.MACHINE_TYPE.get(file_header.Machine, "unknown"),
            "number_of_sections": int(file_header.NumberOfSections),
            "timestamp": int(file_header.TimeDateStamp),
            "timestamp_hex": f"0x{file_header.TimeDateStamp:08X}",
            "characteristics": f"0x{file_header.Characteristics:04X}",
            "subsystem": int(optional.Subsystem),
            "image_base": f"0x{optional.ImageBase:08X}",
            "entry_point_rva": f"0x{optional.AddressOfEntryPoint:08X}",
            "entry_point_section": section_for_rva(pe, optional.AddressOfEntryPoint),
            "section_alignment": int(optional.SectionAlignment),
            "file_alignment": int(optional.FileAlignment),
            "dll_characteristics": f"0x{optional.DllCharacteristics:04X}",
            "linker_major": int(optional.MajorLinkerVersion),
            "linker_minor": int(optional.MinorLinkerVersion),
            "size_of_image": int(optional.SizeOfImage),
            "size_of_headers": int(optional.SizeOfHeaders),
            "data_directories": dirs,
            "rich_header": rich_header(pe),
        },
        "sections": section_data,
        "imports": imports_data,
        "network_imports": network_imports,
        "exports": exports(pe),
        "debug": debug_entries(pe),
        "version_info": version_info(pe),
        "string_count_ascii": len(ascii_strings(data)),
        "string_count_utf16le": len(utf16le_strings(data)),
        "keyword_hits": keyword_hits,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    all_data = {}
    for target in TARGETS:
        path = ROOT / target
        result = analyze(path)
        all_data[target] = result
        (OUT / f"{target}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    (OUT / "pe-static-triage.json").write_text(
        json.dumps(all_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
