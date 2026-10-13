#!/usr/bin/env python3
"""UI 编辑器 M1 写回探针：在真实 script.fls 上验证 0SLF 容器写回。

- 身份重组：parse -> build 后逐条 (id, r1, 存储字节) 一致；
- 条目替换：改第 337 条负载（解压->改->重加密存储字节、长度
  变化），重开后逐条存储字节比对：除 337 外全部原样；337 与
  4007 用原有解码链验明文（337 为新内容、4007 不变）；
- 编辑器 FlsPack 能打开产物并解出目录。

结论用于评估“保存回资源包”是否进入编辑器集成（M1）。
运行：python3 tools/ui_pack_write_probe.py [script.fls 路径]
"""
import json
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "client_patches"))
sys.path.insert(0, str(ROOT / "ui_editor" / "src"))
import build_registration_preview as base  # noqa: E402

from ui_editor.core.pack import FlsPack  # noqa: E402
from ui_editor.core.pack_build import (  # noqa: E402
    build_archive,
    parse_archive,
)


def decrypt(rows, keys, index):
    return base.xor_payload(zlib.decompress(rows[index][1]), keys[str(index)])


def main() -> int:
    archive_path = Path(sys.argv[1]) if len(sys.argv) > 1 \
        else ROOT / "data" / "script.fls"
    raw = archive_path.read_bytes()
    keys = json.loads((ROOT / "tools/decompiler/script_fls_keys.json").read_text())
    _, rows = base.entries(raw)
    entries = parse_archive(raw)
    print(f"[1] 原包 {len(entries)} 条（{len(raw)} 字节）")

    identity = build_archive(entries)
    again = parse_archive(identity)
    same = all(a.stored == b.stored and a.entry_id == b.entry_id
               and a.r1 == b.r1 for a, b in zip(entries, again, strict=True))
    print(f"[2] 身份重组逐条一致: {same}（{len(raw)} -> {len(identity)} 字节）")
    if not same:
        return 1

    target, neighbor = 337, 4007
    plain_before = decrypt(rows, keys, target)
    neighbor_before = decrypt(rows, keys, neighbor)
    new_plain = plain_before + b"\n# M1 probe padding 0123456789\n"
    entries[target].stored = zlib.compress(
        base.xor_payload(new_plain, keys[str(target)]), 9)
    rebuilt = build_archive(entries)
    _, rows_after = base.entries(rebuilt)
    entries_after = parse_archive(rebuilt)
    others_equal = all(
        a.stored == b.stored for i, (a, b) in enumerate(
            zip(entries, entries_after, strict=True)) if i != target)
    target_plain = decrypt(rows_after, keys, target)
    neighbor_plain = decrypt(rows_after, keys, neighbor)
    print(f"[3] 替换条目 {target}: 其余存储字节不变={others_equal}, "
          f"目标明文为新内容={target_plain == new_plain}, "
          f"邻居 {neighbor} 明文不变={neighbor_plain == neighbor_before}"
          f"（{len(raw)} -> {len(rebuilt)} 字节）")

    tmp = ROOT / "tools" / "_ui_probe_tmp.fls"
    tmp.write_bytes(rebuilt)
    try:
        with FlsPack(tmp) as pack:
            count = pack.count
    finally:
        tmp.unlink()
    print(f"[4] 编辑器 FlsPack 打开产物: 条目数 {count}")
    ok = others_equal and target_plain == new_plain \
        and neighbor_plain == neighbor_before and count == len(entries)
    print("结论:", "通过，可进入编辑器集成" if ok else "失败，停止集成")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
