#!/usr/bin/env python3
"""interface.fls 专项探针：目录型拼帧实测 + .spr 悬案定案 + 引用命中核对。

用法（仓库根执行）::

    PYTHONPATH=ui_editor/src python3 ui_editor/tools/interface_probe.py \
        path/to/interface.fls [--item path/to/item.fls] [--json out.json]

报告内容（对齐 notes/fls_path_hash_and_dlg.md §9 口径）：

1. 包概览与 .dlg 全量解密（unpack_packed_text + dlg_codec.parse_bytes）；
2. sFileName 引用分布：目录型伪引用 / 文件型引用，文件型逐条命中核对
   （本包 + 可选 item.fls；未命中清单全列）；
3. 目录型基路径逐条 :func:`dir_base.plan` 实测：命中族统计、三条案例
   明细、拼不出清单与「扩展候选」探查（发现 dir_base 未知族）；
4. `.spr` 悬案：全部 .spr 引用存在性 + 存在条目的字节头/是否可按
   编辑器精灵格式解码；专项查 hash ``0x1310B991``（`烟2_.spr`）：
   「未找到 vs 在包未解码 vs 可解码」定案。

纯命令行、无 Qt；大包跑几十秒属正常。只读探针，不改任何文件。
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ui_editor" / "src"))

from ui_editor.core import dlg_codec, sprite  # noqa: E402
from ui_editor.core.dir_base import is_dir_base, plan  # noqa: E402
from ui_editor.core.mxhash import path_hash  # noqa: E402
from ui_editor.core.native_layout import plain_if_layout  # noqa: E402
from ui_editor.core.pack import FlsPack  # noqa: E402
from ui_editor.core.pack_build import unpack_packed_text  # noqa: E402

#: 专项哈希：`烟2_.spr`（见 notes：疑 mxmain.dll 解析，编辑器画布占位）
SPR_PROBE_HASH = 0x1310B991

#: 三条用户验收案例的基路径特征
CASE_MARKERS = ("输入底框", "上文字底", "勾选框底")

#: 扩展候选：dir_base 四族之外的常见拼法（发现未知族用，只探测不入库）
EXTRA_CANDIDATES = (
    ("two_h", ("left.png", "right.png")),
    ("two_v", ("top.png", "bottom.png")),
    ("two_h_igs", ("left.igs", "right.igs")),
    ("frame_1", ("1.png",)),          # 从 1 起算（无 0 号）
    ("frame_0_only", ("0.png",)),     # 仅 0 号
    ("bg", ("bg.png",)),
    ("updown", ("up.png", "down.png")),
)


def probe_layouts(pack: FlsPack) -> tuple[list[dict], int]:
    """全量条目尝试解密 .dlg；返回（布局 dict 列表, 成功数）。

    快路径 `plain_if_layout`（明文 + 头部反推 4 字节 XOR）覆盖 UI 编辑器
    产出的全部 .dlg；频率恢复兜底只对小条目（<100KB）开，避免在
    PNG/精灵大块上空转。
    """
    layouts: list[dict] = []
    ok = 0
    for index in range(pack.count):
        stored = pack.read_index(index)
        plain = None
        try:
            plain = plain_if_layout(stored)
        except ValueError:
            plain = None  # 识别为布局但损坏：不再兜底
        if plain is None and 200 <= len(stored) <= 100_000:
            try:
                plain = unpack_packed_text(stored)
            except Exception:
                plain = None
        if plain is None:
            continue
        try:
            dicts, _md5 = dlg_codec.parse_bytes(plain)
        except Exception:
            continue
        ok += 1
        layouts.extend(dicts)
        if ok % 500 == 0:
            print(f"      …已解出 {ok} 条布局（扫过 {index + 1}/{pack.count}）",
                  flush=True)
    return layouts, ok


def walk_widgets(nodes: list, out: list) -> None:
    for node in nodes:
        if isinstance(node, dict):
            out.append(node)
            children = node.get("lChildren") or []
            if isinstance(children, list):
                walk_widgets(children, out)


def collect_file_fields(layouts: list[dict]) -> dict[str, set[str]]:
    """收集资源字段值：字段名 → 原值集合。"""
    fields: dict[str, set[str]] = {}
    for root in layouts:
        widgets: list = []
        walk_widgets([root], widgets)
        for widget in widgets:
            for key, value in widget.items():
                if isinstance(value, str) and value:
                    if key in ("sFileName", "sSoundPath", "sSelectImageName",
                               "sMouseOverImageName", "sCheckedImageName",
                               "sDisabledImageName", "sDownImageName",
                               "sImageName", "sPath"):
                        fields.setdefault(key, set()).add(value)
    return fields



def image_size(data: bytes) -> tuple[int, int] | None:
    """从字节读图片宽高：PNG/JPEG/GIF 头即可，不需要 Qt。"""
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24:
        return (int.from_bytes(data[16:20], "big"),
                int.from_bytes(data[20:24], "big"))
    if data[:6] in (b"GIF87a", b"GIF89a") and len(data) >= 10:
        return (int.from_bytes(data[6:8], "little"),
                int.from_bytes(data[8:10], "little"))
    if data[:2] == b"\xff\xd8":
        index = 2
        while index + 9 < len(data):
            if data[index] != 0xFF:
                index += 1
                continue
            marker = data[index + 1]
            length = int.from_bytes(data[index + 2:index + 4], "big")
            if marker in (0xC0, 0xC1, 0xC2) and index + 9 < len(data):
                return (int.from_bytes(data[index + 7:index + 9], "big"),
                        int.from_bytes(data[index + 5:index + 7], "big"))
            index += 2 + max(2, length)
    return None


def slice_stats(pack: FlsPack, item: FlsPack | None, plans: dict[str, dict],
                ) -> dict:
    """切片族的真实像素尺寸：切割线的唯一证据来源（无 Qt，只读图片头）。"""
    stats: dict = {"families": {}, "samples": []}
    for base, info in plans.items():
        if info["kind"] not in ("h_slice", "v_slice", "nine_slice"):
            continue
        sizes = {}
        for piece in info["pieces"]:
            found = None
            for source in (pack, item):
                if source is None or not source.contains(piece):
                    continue
                try:
                    found = image_size(source.read_named(piece) or b"")
                except Exception:
                    found = None
                if found:
                    break
            sizes[piece] = found
        stats["families"][info["kind"]] = (
            stats["families"].get(info["kind"], 0) + 1)
        if len(stats["samples"]) < 12:
            stats["samples"].append({"base": base, "kind": info["kind"],
                                     "sizes": sizes})
    return stats


def button_state_stats(layouts: list[dict], pack: FlsPack,
                       item: FlsPack | None) -> dict:
    """按钮状态证据摸底：状态字段出现次数 + 图高与控件高的比例。"""
    button_types = {"CButton", "CHPageButton", "CVPageButton",
                    "CHPagePngButton", "CVPagePngButton", "CTextButton"}
    state_fields = ("sDownImageName", "sMouseOverImageName",
                    "sDisabledImageName", "sCheckedImageName")
    field_hits: Counter = Counter()
    ratios: Counter = Counter()
    frames_seen: Counter = Counter()
    for root in layouts:
        widgets: list = []
        walk_widgets([root], widgets)
        for widget in widgets:
            for field in state_fields:
                if widget.get(field):
                    field_hits[field] += 1
            if widget.get("sWidgetType") not in button_types:
                continue
            name = widget.get("sFileName")
            if not isinstance(name, str) or not name or name.endswith(("\\", "/")):
                continue
            height = widget.get("iHeight")
            data = None
            for source in (pack, item):
                if source is None or not source.contains(name):
                    continue
                try:
                    data = source.read_named(name)
                except Exception:
                    data = None
                if data:
                    break
            size = image_size(data or b"")
            if size is None or not isinstance(height, int) or height <= 0:
                continue
            parts = round(size[1] / height, 2)
            ratios[parts] += 1
            frames_seen[size] += 1
    return {
        "state_fields": dict(field_hits),
        "height_ratio": dict(ratios.most_common(20)),
        "top_sizes": [[list(size), count]
                      for size, count in frames_seen.most_common(20)],
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fls", help="interface.fls 路径")
    parser.add_argument("--item", help="item.fls 路径（可选，回退资源包）")
    parser.add_argument("--json", help="完整结果 JSON 落盘路径")
    args = parser.parse_args()

    pack = FlsPack(args.fls)
    item = FlsPack(args.item) if args.item else None
    report: dict = {"pack": str(args.fls), "entries": pack.count}

    print(f"[1/5] 包概览：{args.fls} 条目 {pack.count} 条")

    print("[2/5] 全量解密 .dlg …")
    layouts, ok = probe_layouts(pack)
    report["dlg_decoded"] = ok
    print(f"      解出布局 {ok} 条（参考笔记口径 2,706）")

    fields = collect_file_fields(layouts)
    sfn = fields.get("sFileName", set())
    dir_bases = sorted(p for p in sfn if is_dir_base(p))
    file_refs = sorted(p for p in sfn if not is_dir_base(p))
    report["sfile_names"] = len(sfn)
    report["dir_bases"] = len(dir_bases)
    report["file_refs"] = len(file_refs)
    print(f"[3/5] sFileName：共 {len(sfn)} 个；目录型 {len(dir_bases)}；"
          f"文件型 {len(file_refs)}（参考口径 2738/706/2032）")

    def exists(name: str) -> bool:
        return pack.contains(name) or (item is not None and item.contains(name))

    missing = [p for p in file_refs if not exists(p)]
    hit = len(file_refs) - len(missing)
    report["file_hit"] = hit
    report["file_missing"] = missing
    print(f"      文件型命中 {hit}，未命中 {len(missing)}：")
    for path in missing:
        print(f"        MISS {path}")

    print("[4/5] 目录型基路径拼帧实测 …")
    family_counter: Counter = Counter()
    plans: dict[str, dict] = {}
    uncomposed: list[str] = []
    extras_found: dict[str, dict] = {}
    for base in dir_bases:
        got = plan(base, exists)
        if got is not None:
            family_counter[got.kind] += 1
            plans[base] = {"kind": got.kind, "pieces": list(got.pieces)}
        else:
            family_counter["none"] += 1
            uncomposed.append(base)
            extra_hits = {}
            for kind, names in EXTRA_CANDIDATES:
                full = [base + n for n in names]
                if all(exists(n) for n in full):
                    extra_hits[kind] = full
            if extra_hits:
                extras_found[base] = extra_hits
    report["family_counts"] = dict(family_counter)
    report["plans"] = plans
    report["uncomposed"] = uncomposed
    report["extras_found"] = extras_found
    print("      族命中统计：" +
          "，".join(f"{k}={v}" for k, v in sorted(family_counter.items())))
    print(f"      拼不出 {len(uncomposed)} 条；其中扩展候选有发现 "
          f"{len(extras_found)} 条（疑似 dir_base 未知族）：")
    for base, hits in list(extras_found.items())[:20]:
        print(f"        EXTRA {base} -> {list(hits)}")
    print("      三条验收案例：")
    for marker in CASE_MARKERS:
        matched = [b for b in dir_bases if marker in b]
        for base in matched:
            info = plans.get(base)
            text = (f"{info['kind']} {info['pieces']}" if info
                    else "未拼出")
            print(f"        [{marker}] {base} -> {text}")
        if not matched:
            print(f"        [{marker}] 无同名基路径")

    print("[4b/5] 切片尺寸与按钮状态证据 …")
    stats = slice_stats(pack, item, plans)
    button_stats = button_state_stats(layouts, pack, item)
    report["slice_stats"] = stats
    report["button_state_stats"] = button_stats
    print("      切片族实例：" +
          "，".join(f"{k}={v}" for k, v in sorted(
              stats["families"].items())) or "（无）")
    for sample in stats["samples"][:6]:
        print(f"        {sample['kind']} {sample['base']} -> {sample['sizes']}")
    print("      按钮状态字段出现次数：" +
          ("，".join(f"{k}={v}" for k, v in
                     sorted(button_stats["state_fields"].items())) or "（无）"))
    print("      图高/控件高 比例分布：" +
          ("，".join(f"{k}x={v}" for k, v in
                     button_stats["height_ratio"].items()) or "（无样本）"))

    print("[5/5] .spr 悬案 …")
    spr_refs = sorted(p for p in file_refs if p.lower().endswith(".spr"))
    spr_info = []
    for ref in spr_refs:
        entry_id = path_hash(ref)
        present = exists(ref)
        magic = None
        decoded = None
        if present:
            data = pack.read_named(ref) or (item.read_named(ref) if item else None)
            if data:
                magic = data[:16].hex()
                decoded = bool(sprite.is_sprite(data))
        spr_info.append({"ref": ref, "hash": hex(entry_id), "in_pack": present,
                         "magic16": magic, "is_sprite": decoded})
        print(f"        SPR {ref} hash={hex(entry_id)} 在包={present} "
              f"头16={magic} 编辑器精灵={decoded}")
    report["spr_refs"] = spr_info

    # 专项：不依赖引用名，直接按哈希查目录（定案「未找到 vs 未解码」）
    entry_id = SPR_PROBE_HASH
    named = [r for r in spr_refs if path_hash(r) == entry_id]
    probe_stored = pack.read_id(entry_id)
    probe = {"hash": hex(entry_id), "known_names": named,
             "in_pack": probe_stored is not None}
    if probe_stored is not None:
        probe["size"] = len(probe_stored)
        probe["magic32"] = probe_stored[:32].hex()
        probe["is_sprite"] = bool(sprite.is_sprite(probe_stored))
        try:
            probe["text_head"] = probe_stored[:80].decode("gb18030",
                                                          "replace")
        except Exception:
            probe["text_head"] = None
        verdict = ("可按编辑器精灵解码" if probe["is_sprite"]
                   else "在包但不是已支持的精灵格式（未解码案定案）")
    else:
        verdict = "包里没有这个哈希条目（未找到案定案）"
    probe["verdict"] = verdict
    report["spr_probe"] = probe
    print(f"        专项 0x{entry_id:08X}：{verdict}")
    print("        完整报告见 JSON。")

    if args.json:
        Path(args.json).write_text(
            json.dumps(report, ensure_ascii=False, indent=1),
            encoding="utf-8")
        print(f"[OK] JSON 已写入 {args.json}")
    pack.close()
    if item is not None:
        item.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
