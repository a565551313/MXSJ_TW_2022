#!/usr/bin/env python3
"""按路径从 `0SLF` 资源包提取 `.dlg` 对话框布局（及同类文本资源）。

原理（见 ``notes/fls_path_hash_and_dlg.md``）：

* 包内以 ``entry_id = mx_hash(路径)`` 寻址（见 ``mx_path_hash.py``），
  目录解码公式逆向自 ``mxmain.dll`` 的 ``0x48F170`` / ``0x48ECF0``；
* ``.dlg`` 负载为源码文本与一把 4 字节密钥的周期 XOR。文本统一以
  ``# -*- coding: gbk -*-`` 开头，密钥可由前 4 字节反推。

用法::

    # 按路径提取任意个资源（在包内按哈希定位）
    python extract_dlg.py interface.fls out_dir dialog/worldmap.dlg ui.lst

    # 从清单文件批量提取（每行一条路径，如脚本引用的全部 .dlg）
    python extract_dlg.py interface.fls out_dir --paths-file dlg_paths.txt

    # 按条目下标直接 dump（不解密、不还原路径）
    python extract_dlg.py interface.fls out_dir --index 29720

解码策略：优先用固定文件头 ``# -*`` 反推密钥；失败时按周期 4 的
列频率恢复密钥并以“可读文本比例”验收；再失败则原样写出并在
文件名后加 ``.raw``。仅用 Python 标准库。
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mx_path_hash import mx_hash

MASK32 = 0xFFFFFFFF
KNOWN_HEADER4 = b"# -*- coding:"[:4]  # 实际以 '# -*' 四字节反推整把钥匙


class Fls0Slf:
    """最小 0SLF 只读解析：目录解码 + 按下标/哈希取负载。"""

    def __init__(self, data: bytes):
        if data[:4] != b"0SLF":
            raise ValueError("魔数不是 0SLF")
        self._data = data
        self.count, self.dir_offset = struct.unpack_from("<II", data, 4)
        self.entries = [self._decode(i) for i in range(self.count)]
        self.by_id = {}
        for index, (entry_id, offset, length) in enumerate(self.entries):
            self.by_id.setdefault(entry_id, index)

    def _decode(self, index: int) -> tuple[int, int, int]:
        entry_id, r1, r2, r3 = struct.unpack_from(
            "<IIII", self._data, self.dir_offset + index * 16
        )
        clen = (((r1 * entry_id + 0x0DF25E) & MASK32) ^ r2) & MASK32
        doff = (
            ((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32) ^ r3
        ) & MASK32
        return entry_id, doff, clen

    def payload_by_index(self, index: int) -> bytes:
        _entry_id, offset, length = self.entries[index]
        return self._data[offset : offset + length]

    def payload_by_path(self, path: str) -> bytes | None:
        digest = mx_hash(path.encode("gbk", "replace"))
        index = self.by_id.get(digest)
        if index is None:
            return None
        return self.payload_by_index(index)


def xor_with_key(data: bytes, key: bytes) -> bytes:
    return bytes(byte ^ key[i & 3] for i, byte in enumerate(data))


def _text_score(data: bytes) -> float:
    if not data:
        return 0.0
    good = sum(
        1 for b in data if b in b"\r\n\t" or 0x20 <= b < 0x7F or b >= 0x81
    )
    return good / len(data)


def _recover_key_frequency(data: bytes) -> bytes:
    """按周期 4 分列，以英文/代码常见字节频率恢复 XOR 密钥。"""
    favourites = set(b" etaoinshrdlu=(){}_#'\"0123456789.,:[]\n\t<>")
    key = bytearray(4)
    for residue in range(4):
        column = data[residue::4]
        best_byte, best_score = 0, -1
        for candidate in range(256):
            decoded = bytes(b ^ candidate for b in column[:2048])
            score = sum(1 for b in decoded if b in favourites)
            if score > best_score:
                best_score, best_byte = score, candidate
        key[residue] = best_byte
    return bytes(key)


def decode_payload(payload: bytes) -> tuple[bytes, bool]:
    """返回 (明文字节, 是否成功解码)。策略见模块 docstring。"""
    if len(payload) >= 4:
        key = bytes(a ^ b for a, b in zip(payload[:4], KNOWN_HEADER4))
        decoded = xor_with_key(payload, key)
        if decoded.startswith(b"# -*- coding:"):
            return decoded, True
        freq_key = _recover_key_frequency(payload)
        decoded_freq = xor_with_key(payload, freq_key)
        if _text_score(decoded_freq[:2000]) > 0.97:
            return decoded_freq, True
    return payload, False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", help="0SLF 资源包路径（如 interface.fls）")
    parser.add_argument("out_dir", help="输出目录")
    parser.add_argument("paths", nargs="*", help="资源路径（如 dialog/x.dlg）")
    parser.add_argument("--paths-file", help="路径清单文件（每行一条）")
    parser.add_argument(
        "--index", type=int, action="append", default=[],
        help="按条目下标直接 dump（可重复）",
    )
    args = parser.parse_args()

    pack = Fls0Slf(Path(args.pack).read_bytes())
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    targets = list(args.paths)
    if args.paths_file:
        targets += [
            line.strip()
            for line in Path(args.paths_file).read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]

    stats = Counter()
    for resource in targets:
        payload = pack.payload_by_path(resource)
        if payload is None:
            print(f"未命中：{resource}")
            stats["miss"] += 1
            continue
        decoded, is_text = decode_payload(payload)
        rel = resource.replace("\\", "/")
        dest = out_dir / rel
        if not is_text:
            dest = dest.with_suffix(dest.suffix + ".raw")
            stats["raw"] += 1
        else:
            stats["decoded"] += 1
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(decoded)
        print(f"{'解码' if is_text else '原始'} -> {dest}")

    for index in args.index:
        payload = pack.payload_by_index(index)
        decoded, is_text = decode_payload(payload)
        name = f"entry_{index}.bin" if not is_text else f"entry_{index}.txt"
        (out_dir / name).write_bytes(decoded)
        stats["index-dump"] += 1
        print(f"idx {index} -> {out_dir / name}（解码={is_text}）")

    print(f"完成：{dict(stats)}，包内共 {pack.count} 条")
    return 0 if stats["miss"] == 0 or targets == [] else 2


if __name__ == "__main__":
    raise SystemExit(main())
