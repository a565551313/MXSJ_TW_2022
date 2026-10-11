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
    return run_cli(vm, root, args.export_json, args.export_png)


if __name__ == "__main__":
    raise SystemExit(main())
