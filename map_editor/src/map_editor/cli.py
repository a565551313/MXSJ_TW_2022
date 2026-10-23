"""Command-line front end for the MXSJ map editor.

Provides complete headless inspection, diagnostics, path simulation, format
conversion, image-to-``.map`` compilation, ``.blk`` synchronization, and
GIRB/mask verification without requiring Qt:

    python -m map_editor.cli --scan "D:/Games/MXSJ"
    python -m map_editor.cli --scan . --export-json 2303:out/2303.json
    python -m map_editor.cli --scan . --export-blk 2101:out/2101.blk
    python -m map_editor.cli --scan . --audit 2303
    python -m map_editor.cli --build-map art/world.png:out/9001.map
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .client.config import Config
from .client.discovery import DiscoveryError
from .ui.viewmodel import EditorViewModel


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="map-editor",
        description=(
            "《夢想世界》地图编辑器 — 完整支持 .map/.blk 解析、编辑、编译、校验与导出。"
        ),
    )
    p.add_argument("--client-root", help="客户端根目录（会递归搜索 *.map）")
    p.add_argument(
        "--scene-table", help="场景名表 JSON（默认使用内置的 TW v2.27.2 表）"
    )
    p.add_argument(
        "--cli",
        action="store_true",
        help="不开图形界面，只在终端执行命令（默认行为，除非指定 --gui）",
    )
    p.add_argument("--gui", action="store_true", help="启动图形界面")
    p.add_argument("--scan", metavar="DIR", help="扫描指定目录")
    p.add_argument(
        "--export-json",
        metavar="KEY:PATH",
        help="导出某张地图的结构 JSON，如 2101:out.json",
    )
    p.add_argument(
        "--export-png",
        metavar="KEY:PATH",
        help="导出某张地图的整图 PNG，如 2101:out.png",
    )
    p.add_argument(
        "--export-blk",
        metavar="KEY:PATH",
        help="导出某张地图的服务端/客户端通行网格 .blk，如 2101:out/2101.blk",
    )
    p.add_argument(
        "--export-lightmap",
        metavar="KEY:PATH",
        help="导出某张地图的 4x4px GIRB 动态光照灰度图 PNG，如 1034:out/1034_light.png",
    )
    p.add_argument(
        "--export-walkability",
        metavar="KEY:PATH",
        help="导出某张地图的 LLEC 通行/阴影可视化图 PNG，如 2303:out/2303_walk.png",
    )
    p.add_argument(
        "--import-blk",
        metavar="KEY:BLK_PATH:OUT_MAP",
        help="将 .blk 通行网格同步写入指定地图并另存为新 .map（自动重解析校验）",
    )
    p.add_argument(
        "--build-map",
        metavar="IMG_PATH:OUT_MAP",
        help="将整张 PNG/JPG 地图美术底图切片编译为完整 0.1M .map 文件",
    )
    p.add_argument(
        "--audit",
        metavar="KEY",
        help="对某张地图执行完整通行连通域、GIRB 光照、前景遮罩与 NPC 合法性审计",
    )
    p.add_argument(
        "--find-path",
        metavar="KEY:X0,Y0:X1,Y1",
        help="在指定地图上运行 8 方向 CAStar 寻路模拟（客户端像素坐标）",
    )
    p.add_argument(
        "--girb-report",
        action="store_true",
        help="报告每张地图的 GIRB 解压成功率与字节分布",
    )
    p.add_argument(
        "--girb-dump",
        metavar="KEY[:N]",
        help="导出某张地图解不出的扇区的 GIRB 原始字节（十六进制）",
    )
    return p


def _print_table(vm: EditorViewModel) -> None:
    print(f"{'编号':<16}{'名称':<26}{'尺寸':<13}{'扇区':>6}{'遮罩':>6}  大小")
    print("-" * 80)
    for r in vm.rows:
        if r.broken:
            print(
                f"{r.key:<16}{(r.name or '—'):<26}{'解析失败':<13}"
                f"{'':>6}{'':>6}  {r.error}"
            )
            continue
        print(
            f"{r.key:<16}{(r.name or '—'):<26}{f'{r.width}x{r.height}':<13}"
            f"{r.sectors:>6}{r.records:>6}  {r.size / 1024:.0f} KB"
        )


def _export_pair(vm: EditorViewModel, spec: str, kind: str) -> int:
    key, _, dest = spec.partition(":")
    if not dest:
        print(f"[错误] --export-{kind} 需要 KEY:PATH 形式", file=sys.stderr)
        return 2
    try:
        vm.open_map(key)
        if kind == "json":
            path = vm.export_json(dest)
        elif kind == "png":
            path = vm.export_png(dest)
        elif kind == "blk":
            path = vm.export_blk(dest)
        elif kind == "lightmap":
            path = vm.export_lightmap_png(dest)
        else:
            path = vm.export_walkability_png(dest)
    except Exception as exc:
        print(f"[错误] 导出失败: {exc}", file=sys.stderr)
        return 1
    finally:
        vm.close_map()
    print(f"\n已导出 {path}")
    return 0


def run_cli(
    vm: EditorViewModel,
    root: str,
    export_json: str | None,
    export_png: str | None,
    *,
    export_blk: str | None = None,
    export_lightmap: str | None = None,
    export_walkability: str | None = None,
    import_blk: str | None = None,
    audit_key: str | None = None,
    find_path_spec: str | None = None,
) -> int:
    try:
        vm.set_client_root(root)
    except DiscoveryError as exc:
        print(f"[错误] {exc}", file=sys.stderr)
        return 2
    assert vm.layout is not None
    print(f"客户端目录 : {vm.state.client_root}")
    print(f"扫描文件数 : {vm.state.scanned_files}")
    print(f"发现地图   : {vm.state.map_count}")
    print(f"扫描耗时   : {vm.layout.elapsed_s:.2f}s")
    print(f"script.fls : {vm.layout.script_fls or '(未找到)'}")
    print(f"mx.exe     : {vm.layout.main_exe or '(未找到)'}")
    print(f"场景名表   : {vm.scenes.source or '(未加载，名称留空)'}")
    print()
    _print_table(vm)

    for spec, kind in (
        (export_json, "json"),
        (export_png, "png"),
        (export_blk, "blk"),
        (export_lightmap, "lightmap"),
        (export_walkability, "walkability"),
    ):
        if spec:
            rc = _export_pair(vm, spec, kind)
            if rc != 0:
                return rc

    if import_blk:
        parts = _split_colon_spec(import_blk, 3)
        if len(parts) != 3 or not all(parts):
            print("[错误] --import-blk 需要 KEY:BLK_PATH:OUT_MAP 形式", file=sys.stderr)
            return 2
        key, blk_path, out_map = parts
        try:
            vm.open_map(key)
            changed = vm.import_blk(blk_path)
            saved = vm.save_map(out_map)
            print(f"\n已同步 {changed} 个格子并写出 {saved}")
        except Exception as exc:
            print(f"[错误] 导入 .blk 失败: {exc}", file=sys.stderr)
            return 1
        finally:
            vm.close_map()

    if audit_key:
        try:
            vm.open_map(audit_key)
            report = vm.audit_current_map()
            print("\n" + json.dumps(report, ensure_ascii=False, indent=2))
        except Exception as exc:
            print(f"[错误] 审计失败: {exc}", file=sys.stderr)
            return 1
        finally:
            vm.close_map()

    if find_path_spec:
        parts = find_path_spec.split(":")
        if len(parts) != 3 or "," not in parts[1] or "," not in parts[2]:
            print("[错误] --find-path 需要 KEY:X0,Y0:X1,Y1 形式", file=sys.stderr)
            return 2
        key = parts[0]
        try:
            x0, y0 = (int(v) for v in parts[1].split(",", 1))
            x1, y1 = (int(v) for v in parts[2].split(",", 1))
        except ValueError:
            print("[错误] --find-path 坐标必须是整数", file=sys.stderr)
            return 2
        try:
            vm.open_map(key)
            res = vm.simulate_path((x0, y0), (x1, y1))
            print(
                f"\n寻路结果: found={res.found}, steps={len(res.cells)}, "
                f"cost={res.cost}, explored={res.explored}"
            )
        except Exception as exc:
            print(f"[错误] 寻路失败: {exc}", file=sys.stderr)
            return 1
        finally:
            vm.close_map()
    return 0


def _print_girb_report(vm: EditorViewModel) -> None:
    print(
        f"{'编号':<16}{'名称':<26}{'尺寸':<13}{'扇区':>6}{'解出':>6}{'失败':>6}"
        f"{'取值':>6}  GIRB字节"
    )
    print("-" * 92)
    bad: list[str] = []
    for r in vm.girb_report():
        if r.get("error"):
            print(f"{r['key']:<16}{(r.get('name') or '—'):<26}解析失败: {r['error']}")
            bad.append(r["key"])
            continue
        flag = "" if r["failed"] == 0 else "  ← 有失败"
        print(
            f"{r['key']:<16}{(r['name'] or '—'):<26}{r['size']:<13}"
            f"{r['sectors']:>6}{r['decoded']:>6}{r['failed']:>6}"
            f"{r['distinct_values']:>6}  "
            f"{r['girb_len_min']}~{r['girb_len_max']}{flag}"
        )
        if r["failed"]:
            bad.append(r["key"])
    print()
    if bad:
        print(f"[!] 以下地图的 GIRB 存在异常扇区：{' '.join(bad)}")
    else:
        print("[ok] 全部地图的 GIRB 均完整解出。")
    print(
        "    说明：解出的扇区一律是 2400 字节 = 80x60 个 4-bit 动态亮度采样"
        "（兼容视图 1200 个 u16 = 40x30 格）。"
    )


def _girb_dump(vm: EditorViewModel, spec: str) -> int:
    key, _, tail = spec.partition(":")
    limit = 12
    if tail:
        try:
            limit = max(1, int(tail))
        except ValueError:
            print(
                f"[错误] --girb-dump 的 N 必须是整数，收到 {tail!r}", file=sys.stderr
            )
            return 2
    try:
        vm.open_map(key)
    except Exception as exc:
        print(f"[错误] 打不开 {key}: {exc}", file=sys.stderr)
        return 1
    doc = vm.document
    assert doc is not None
    st = doc.collision_stats()
    print(
        f"### {key}  {doc.header.width}x{doc.header.height}  "
        f"{st['sectors']}扇区  解出{st['decoded']}  失败{st['failed']}"
    )
    if st["failed"] == 0:
        print("# 这张图全部解出，没有需要排查的扇区。")
        vm.close_map()
        return 0

    seen: dict[bytes, int] = {}
    order: list[bytes] = []
    for sec in doc.iter_sectors():
        if doc.collision_cells(sec) is not None:
            continue
        body = sec.girb_body
        if body not in seen:
            seen[body] = sec.index
            order.append(body)
    print(
        f"# 失败扇区共 {st['failed']} 个，压缩体去重后 {len(order)} 种；"
        f"下面列出前 {min(limit, len(order))} 种"
    )
    print("# 格式：s<首个扇区号> len=<字节数>")
    for body in order[:limit]:
        print(f"s{seen[body]} len={len(body)}")
        print(body.hex())
    vm.close_map()
    return 0


def _bare_double_click_launch(argv: list[str] | None) -> bool:
    if not getattr(sys, "frozen", False):
        return False
    effective = sys.argv[1:] if argv is None else argv
    return len(effective) == 0


def _split_colon_spec(spec: str, fields: int) -> list[str]:
    """Split colon-delimited CLI fields while preserving Windows drive colons."""
    parts: list[str] = []
    start = 0
    for idx, char in enumerate(spec):
        if char != ":":
            continue
        if (
            idx == start + 1
            and spec[start:idx].isalpha()
            and spec[idx + 1 : idx + 2] in ("\\", "/")
        ):
            continue
        parts.append(spec[start:idx])
        start = idx + 1
        if len(parts) == fields - 1:
            break
    parts.append(spec[start:])
    return parts


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = Config.load()
    if args.scene_table:
        config.scene_table = args.scene_table
    vm = EditorViewModel(config=config)
    root = args.scan or args.client_root or config.client_root

    if args.build_map and not args.gui:
        spec_parts = _split_colon_spec(args.build_map, 2)
        img_str, out_str = spec_parts if len(spec_parts) == 2 else ("", "")
        if not img_str or not out_str:
            print("[错误] --build-map 需要 IMG_PATH:OUT_MAP 形式", file=sys.stderr)
            return 2
        if root:
            try:
                vm.set_client_root(root)
            except DiscoveryError as exc:
                print(f"[错误] {exc}", file=sys.stderr)
                return 2
        from PIL import Image

        img_path = Path(img_str)
        if not img_path.is_file():
            print(f"[错误] 找不到底图文件: {img_path}", file=sys.stderr)
            return 2
        with Image.open(img_path) as im:
            w, h = im.size
        try:
            vm.create_new_map(out_str, w, h, image=img_path)
        except Exception as exc:
            print(f"[错误] 编译地图失败: {exc}", file=sys.stderr)
            return 1
        vm.close_map()
        print(f"已编译生成地图 {out_str} ({w}x{h})")
        if not root:
            return 0

    if args.gui or _bare_double_click_launch(argv):
        if args.client_root:
            config.remember_root(args.client_root)
            config.save()
        from .ui.widgets import run

        return run(vm)

    if not root:
        print(
            "[错误] 需要 --scan 或已记住的客户端目录（--client-root）", file=sys.stderr
        )
        return 2
    code = run_cli(
        vm,
        root,
        args.export_json,
        args.export_png,
        export_blk=args.export_blk,
        export_lightmap=args.export_lightmap,
        export_walkability=args.export_walkability,
        import_blk=args.import_blk,
        audit_key=args.audit,
        find_path_spec=args.find_path,
    )
    if args.girb_report:
        print()
        _print_girb_report(vm)
    if args.girb_dump:
        print()
        code = _girb_dump(vm, args.girb_dump) or code
    return code


if __name__ == "__main__":
    raise SystemExit(main())
