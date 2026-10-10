#!/usr/bin/env python3
"""Offline MXSJ LLEC byte-grid viewer (SVG or terminal; standard library only).

Colors describe byte values, NOT confirmed walkability or terrain height.
No textures are decoded by this viewer.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
from pathlib import Path
import struct

from map_parser import parse_map

COLORS = {0: "#d6e8df", 1: "#334559"}
OTHER = "#e6ad56"


def build_grid(doc: dict) -> list[list[int]]:
    spec = doc["grid"]
    cols = spec["sector_columns"]
    rows = spec["sector_rows"]
    sw = spec["cell_columns_per_sector"]
    sh = spec["cell_rows_per_sector"]
    if (cols, rows, sw, sh) != (7, 7, 16, 12) or len(doc["sectors"]) != 49:
        raise ValueError("viewer supports only observed 7x7 sectors with 16x12 LLEC data")
    grid = [[0] * (cols * sw) for _ in range(rows * sh)]
    for sector in doc["sectors"]:
        n = sector["index"]
        if not 0 <= n < 49 or len(sector["cells"]) != sw * sh:
            raise ValueError("invalid sector index or LLEC data")
        x, y = (n % cols) * sw, (n // cols) * sh
        for row in range(sh):
            grid[y + row][x:x + sw] = sector["cells"][row * sw:(row + 1) * sw]
    return grid


def render_svg(doc: dict, *, scale: int = 8, overlay_records: bool = False) -> str:
    if not 2 <= scale <= 32:
        raise ValueError("scale must be between 2 and 32")
    grid = build_grid(doc)
    cols, rows = len(grid[0]), len(grid)
    margin = 38
    w, h = cols * scale, rows * scale
    name = html.escape(Path(doc["source"]).name)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w+2*margin} {h+2*margin+34}" role="img">',
             '<rect width="100%" height="100%" fill="#faf8f3"/>',
             f'<title>{name} - LLEC raw-byte overview</title>',
             f'<text x="{margin}" y="23" font-family="sans-serif" font-size="16" fill="#273b4a">{name} / LLEC raw bytes (not confirmed collision)</text>',
             f'<g transform="translate({margin},{margin})" shape-rendering="crispEdges">',
             f'<rect width="{w}" height="{h}" fill="{COLORS[0]}"/>']
    # Group contiguous horizontal runs, keeping the output small and legible.
    for y, row in enumerate(grid):
        x = 0
        while x < cols:
            value = row[x]
            end = x + 1
            while end < cols and row[end] == value:
                end += 1
            if value != 0:
                color = COLORS.get(value, OTHER)
                parts.append(f'<rect x="{x*scale}" y="{y*scale}" width="{(end-x)*scale}" height="{scale}" fill="{color}"/>')
            x = end
    for col in range(1, 7):
        parts.append(f'<path d="M {col*16*scale} 0 V {h}" stroke="#fff" stroke-opacity=".55" stroke-width="1"/>')
    for row in range(1, 7):
        parts.append(f'<path d="M 0 {row*12*scale} H {w}" stroke="#fff" stroke-opacity=".55" stroke-width="1"/>')
    if overlay_records:
        for record in doc["prefix_records"]:
            rect = record["bounds_px"]
            # Verified for map/2303: 16x12 grid per 320x240 sector = 20px per byte cell.
            rx, ry = rect["x"] * scale / 20, rect["y"] * scale / 20
            rw, rh = rect["width"] * scale / 20, rect["height"] * scale / 20
            label = f"record {record['index']} ({rect['x']}, {rect['y']}, {rect['width']}×{rect['height']})"
            parts.append(f'<rect x="{rx:.2f}" y="{ry:.2f}" width="{rw:.2f}" height="{rh:.2f}" fill="none" stroke="#ec4f4a" stroke-width="1.5"><title>{html.escape(label)}</title></rect>')
    parts.append('</g>')
    legend = '0 = pale | 1 = dark | other = amber | 16×12 byte grid'
    if overlay_records:
        legend += ' | red outlines = prefix-record bounds (not identified NPCs)'
    parts.append(f'<text x="{margin}" y="{h+margin+20}" font-family="sans-serif" font-size="12" fill="#273b4a">{legend}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def render_image_overlay(doc: dict, png_bytes: bytes, *, overlay_cells: bool = False,
                         overlay_records: bool = False) -> str:
    """Self-contained SVG with offline PNG background and optional investigative layers."""
    width, height = doc["header"]["width"], doc["header"]["height"]
    if png_bytes[:8] != b"\x89PNG\r\n\x1a\n" or struct.unpack_from(">II", png_bytes, 16) != (width, height):
        raise ValueError("base PNG dimensions/signature do not match the map")
    title = html.escape(Path(doc["source"]).name)
    embedded = base64.b64encode(png_bytes).decode("ascii")
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">',
             f'<title>{title}: restored map (LLEC semantics not confirmed)</title>',
             f'<image width="{width}" height="{height}" href="data:image/png;base64,{embedded}"/>']
    if overlay_cells:
        grid = build_grid(doc)
        # Tile geometry: 320x240 per sector, 16x12 bytes => 20x20 pixel squares.
        for y, row in enumerate(grid):
            if y * 20 >= height:
                break
            for x, value in enumerate(row):
                if x * 20 >= width or value == 0:
                    continue
                color = "#eb3c39" if value == 1 else "#ffbd3d"
                parts.append(f'<rect x="{x*20}" y="{y*20}" width="20" height="20" fill="{color}" opacity="0.28"><title>LLEC byte: {value}</title></rect>')
    if overlay_records:
        for rec in doc["prefix_records"]:
            rect = rec["bounds_px"]
            tip = f"record {rec['index']}: bounds ({rect['x']},{rect['y']},{rect['width']},{rect['height']}); object type unknown"
            parts.append(f'<rect x="{rect["x"]}" y="{rect["y"]}" width="{rect["width"]}" height="{rect["height"]}" fill="none" stroke="#28dfff" stroke-width="2"><title>{html.escape(tip)}</title></rect>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def probe_cell(doc: dict, x: int, y: int) -> dict:
    """Return a raw LLEC byte at logical pixel coordinates, without interpreting movement."""
    width, height = doc["header"]["width"], doc["header"]["height"]
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(f"pixel coordinate outside map: ({x}, {y})")
    col, row = x // 20, y // 20
    value = build_grid(doc)[row][col]
    return {"x": x, "y": y, "grid_col": col, "grid_row": row, "raw_llec_byte": value,
            "note": "raw value only; 0/1/2 movement semantics not proven"}


def render_ascii(doc: dict) -> str:
    grid = build_grid(doc)
    lines = [f"{Path(doc['source']).name}: raw LLEC values (0='.', 1='#', other='?'; not confirmed walkability)"]
    for y, row in enumerate(grid):
        text = "".join("." if b == 0 else "#" if b == 1 else "?" for b in row)
        lines.append(" ".join(text[i:i+16] for i in range(0, 112, 16)))
        if (y + 1) % 12 == 0 and y + 1 < 84:
            lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="source .map or exported .json")
    parser.add_argument("--output", type=Path, help="write standalone SVG (without this, show ASCII on stdout)")
    parser.add_argument("--scale", type=int, default=8, help="SVG cell size, 2-32 (default 8)")
    parser.add_argument("--overlay-records", action="store_true", help="overlay prefix-record rectangles (not NPC markers)")
    parser.add_argument("--base-image", type=Path, help="embed previously decoded local map PNG in SVG")
    parser.add_argument("--overlay-cells", action="store_true", help="tint raw LLEC bytes over --base-image; semantics unconfirmed")
    parser.add_argument("--probe", nargs=2, type=int, metavar=("X", "Y"), help="query raw LLEC value at a logical pixel coordinate")
    args = parser.parse_args()
    if (args.base_image or args.overlay_cells) and not args.output:
        parser.error("--base-image/--overlay-cells require --output SVG")
    if args.overlay_cells and not args.base_image:
        parser.error("--overlay-cells requires --base-image")
    doc = json.loads(args.input.read_text(encoding="utf-8")) if args.input.suffix.lower() == ".json" else parse_map(args.input)
    if args.probe:
        print(json.dumps(probe_cell(doc, *args.probe), ensure_ascii=False))
        if not args.output:
            return
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        svg = (render_image_overlay(doc, args.base_image.read_bytes(), overlay_cells=args.overlay_cells,
                                    overlay_records=args.overlay_records) if args.base_image else
               render_svg(doc, scale=args.scale, overlay_records=args.overlay_records))
        args.output.write_text(svg, encoding="utf-8")
        print(f"SVG written: {args.output}")
    else:
        print(render_ascii(doc), end="")


if __name__ == "__main__":
    main()
