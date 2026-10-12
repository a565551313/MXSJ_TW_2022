"""Command-line front end.

The GUI needs Qt, which is not available everywhere (headless Linux, CI, a
sandbox without ``libGL``).  Everything the editor *knows* is reachable without
it, so this CLI exists both as a debugging tool and as the automated check that
discovery, parsing and export really work end to end.

    python -m map_editor.cli --cli --scan "D:/Games/MXSJ"
    python -m map_editor.cli --cli --scan . --export-json 2101:out/2101.json
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .client.config import Config
from .client.discovery import DiscoveryError
from .ui.viewmodel import EditorViewModel


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="map-editor",
        description="《夢想世界》地图编辑器 — 只需指定客户端目录，自动发现全部地图。")
    p.add_argument("--client-root", help="客户端根目录（会递归搜索 *.map）")
    p.add_argument("--scene-table", help="场景名表 JSON（默认使用内置的 TW v2.27.2 表）")
    p.add_argument("--cli", action="store_true",
                   help="不开图形界面，只在终端列出地图（默认行为，除非指定 --gui）")
    p.add_argument("--gui", action="store_true", help="启动图形界面")
    p.add_argument("--scan", metavar="DIR", help="扫描指定目录")
    p.add_argument("--export-json", metavar="KEY:PATH",
                   help="导出某张地图的结构 JSON，如 2101:out.json")
    p.add_argument("--export-png", metavar="KEY:PATH",
                   help="导出某张地图的整图 PNG，如 2101:out.png")
    p.add_argument("--girb-report", action="store_true",
                   help="报告每张地图的 GIRB（碰撞网格）解压成功率，供排查用")
    p.add_argument("--girb-dump", metavar="KEY[:N]",
                   help="导出某张地图解不出的扇区的 GIRB 原始字节（十六进制），"
                        "N 为最多输出几个不同的压缩体，默认 12。"
                        "输出是纯文本、几 KB，可直接贴回来，不必上传地图文件")
    return p


def _print_table(vm: EditorViewModel) -> None:
    print(f"{'编号':<8}{'名称':<20}{'尺寸':<14}{'扇区':>6}{'记录':>6}  大小")
    print("-" * 68)
    for r in vm.rows:
        if r.broken:
            print(f"{r.key:<8}{(r.name or '—'):<20}{'解析失败':<14}{'':>6}{'':>6}  {r.error}")
            continue
        try:
            vm.open_map(r)
            records = vm.state.current_records
            vm.close_map()
        except Exception:                                  # pragma: no cover
            records = -1
        print(f"{r.key:<8}{(r.name or '—'):<20}{f'{r.width}x{r.height}':<14}"
              f"{r.sectors:>6}{records:>6}  {r.size / 1024:.0f} KB")


def run_cli(vm: EditorViewModel, root: str, export_json: str | None,
            export_png: str | None) -> int:
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

    for spec, kind in ((export_json, "json"), (export_png, "png")):
        if not spec:
            continue
        key, _, dest = spec.partition(":")
        if not dest:
            print(f"[错误] --export-{kind} 需要 KEY:PATH 形式", file=sys.stderr)
            return 2
        try:
            vm.open_map(key)
            path = (vm.export_json(dest) if kind == "json" else vm.export_png(dest))
        except Exception as exc:
            print(f"[错误] 导出失败: {exc}", file=sys.stderr)
            return 1
        finally:
            vm.close_map()
        print(f"\n已导出 {path}")
    return 0


def _print_girb_report(vm: EditorViewModel) -> None:
    print(f"{'编号':<8}{'名称':<20}{'尺寸':<14}{'扇区':>6}{'解出':>6}{'失败':>6}"
          f"{'取值':>6}  GIRB字节")
    print("-" * 78)
    bad: list[str] = []
    for r in vm.girb_report():
        if r.get("error"):
            print(f"{r['key']:<8}{(r.get('name') or '—'):<20}解析失败: {r['error']}")
            bad.append(r["key"])
            continue
        flag = "" if r["failed"] == 0 else "  ← 有失败"
        print(f"{r['key']:<8}{(r['name'] or '—'):<20}{r['size']:<14}"
              f"{r['sectors']:>6}{r['decoded']:>6}{r['failed']:>6}"
              f"{r['distinct_values']:>6}  {r['girb_len_min']}~{r['girb_len_max']}{flag}")
        if r["failed"]:
            bad.append(r["key"])
    print()
    if bad:
        print(f"[!] 以下地图的 GIRB 尚未完全解出，把这些编号发回来即可定位："
              f"{' '.join(bad)}")
    else:
        print("[ok] 全部地图的 GIRB 均完整解出。")
    print("    说明：解出的扇区一律是 2400 字节 = 1200 个 u16 = 40x30 格（8x8 像素/格）。")


def _girb_dump(vm: EditorViewModel, spec: str) -> int:
    """Print the raw GIRB bodies that fail to inflate, deduplicated.

    The whole point: a failing body is 22-1500 bytes, so a handful of them is
    a few KB of hex that can be pasted into chat.  That beats transferring a
    255 MB client dump just to look at nine sectors.
    """
    key, _, tail = spec.partition(":")
    limit = 12
    if tail:
        try:
            limit = max(1, int(tail))
        except ValueError:
            print(f"[错误] --girb-dump 的 N 必须是整数，收到 {tail!r}", file=sys.stderr)
            return 2
    try:
        vm.open_map(key)
    except Exception as exc:
        print(f"[错误] 打不开 {key}: {exc}", file=sys.stderr)
        return 1
    doc = vm.document
    assert doc is not None
    st = doc.collision_stats()
    print(f"### {key}  {doc.header.width}x{doc.header.height}  "
          f"{st['sectors']}扇区  解出{st['decoded']}  失败{st['failed']}")
    if st["failed"] == 0:
        print("# 这张图全部解出，没有需要排查的扇区。")
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
    print(f"# 失败扇区共 {st['failed']} 个，压缩体去重后 {len(order)} 种；"
          f"下面列出前 {min(limit, len(order))} 种")
    print("# 格式：s<首个扇区号> len=<字节数>")
    for body in order[:limit]:
        print(f"s{seen[body]} len={len(body)}")
        print(body.hex())
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = Config.load()
    if args.scene_table:
        config.scene_table = args.scene_table
    vm = EditorViewModel(config=config)
    root = args.scan or args.client_root or config.client_root

    if args.gui:
        if args.client_root:
            config.remember_root(args.client_root)
            config.save()
        # Imported late so the CLI keeps working without Qt installed.
        from .ui.widgets import run
        return run(vm)

    if not root:
        print("[错误] 需要 --scan 或已记住的客户端目录（--client-root）", file=sys.stderr)
        return 2
    code = run_cli(vm, root, args.export_json, args.export_png)
    if args.girb_report:
        print()
        _print_girb_report(vm)
    if args.girb_dump:
        print()
        code = _girb_dump(vm, args.girb_dump) or code
    return code


if __name__ == "__main__":
    raise SystemExit(main())
