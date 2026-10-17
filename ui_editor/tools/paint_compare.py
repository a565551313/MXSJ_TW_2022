#!/usr/bin/env python3
"""把「编辑器样例图」与「真机截图」配对比对：只给统计，不给结论。

用法（仓库根目录）：

```bash
python3 ui_editor/tools/paint_compare.py \\
    --editor /tmp/paint_samples/CButton.png --game shot.png --out /tmp/paint_cmp
```

产出（写到 ``--out`` 目录）：

* ``*_side_by_side.png``：左编辑器、右真机（尺寸不同也不缩放，铺在原尺寸
  画布上，一眼能看出差别是不是尺寸引起的）；
* ``*_diff.png``：差异像素标红；
* 屏幕上的统计：尺寸是否一致、差异像素比例、差异包围盒、平均绝对差。

**它不做「通过/不通过」判定**：字体渲染、抗锯齿、系统主题造成的差异需要人
判断（见 ``ui_editor/docs/PAINT_CHECKLIST.md`` 的规矩）。这里的数字只是
帮眼睛定位差异区域。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops

DIFF_THRESHOLD = 16  # 单通道差 ≥ 该值算「差异像素」，低于它多半是抗锯齿


def load_rgba(path: Path) -> Image.Image:
    if not path.is_file():
        raise FileNotFoundError(f"找不到图片：{path}")
    return Image.open(path).convert("RGBA")


def diff_mask(editor: Image.Image, game: Image.Image,
              threshold: int = DIFF_THRESHOLD) -> Image.Image:
    """尺寸不一致时按左上角对齐（补透明），返回差异掩膜（'L' 模式）。"""
    width = max(editor.width, game.width)
    height = max(editor.height, game.height)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas.paste(editor, (0, 0))
    other = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    other.paste(game, (0, 0))
    raw = ImageChops.difference(canvas, other).convert("L")
    return raw.point(lambda value: 255 if value >= threshold else 0)


def bbox_of(mask: Image.Image) -> tuple[int, int, int, int] | None:
    return mask.getbbox()


def mean_abs_diff(mask: Image.Image) -> float:
    histogram = mask.histogram()
    total = sum(histogram)
    if not total:
        return 0.0
    return sum(value * count for value, count in enumerate(histogram)) / total


def compare(editor_path: Path, game_path: Path, out_dir: Path,
            label: str | None = None) -> dict:
    editor = load_rgba(editor_path)
    game = load_rgba(game_path)
    label = label or editor_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    width = max(editor.width, game.width)
    height = max(editor.height, game.height)
    side = Image.new("RGBA", (width * 2 + 4, height), (32, 32, 32, 255))
    side.paste(editor, (0, 0))
    side.paste(game, (width + 4, 0))
    side_path = out_dir / f"{label}_side_by_side.png"
    side.save(side_path)

    mask = diff_mask(editor, game)
    marked = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    marked.paste(game, (0, 0))
    red = Image.new("RGBA", (width, height), (255, 0, 0, 110))
    marked = Image.composite(red, marked, mask)
    diff_path = out_dir / f"{label}_diff.png"
    marked.save(diff_path)

    mask_hist = mask.histogram()
    differing = mask_hist[255]
    total = max(1, width * height)
    report = {
        "label": label,
        "editor": str(editor_path),
        "game": str(game_path),
        "sizes_match": (editor.size == game.size),
        "editor_size": list(editor.size),
        "game_size": list(game.size),
        "differing_pixels": differing,
        "differing_ratio": round(differing / total, 6),
        "diff_bbox": list(bbox_of(mask)) if bbox_of(mask) else None,
        "mean_abs_diff": round(mean_abs_diff(mask), 3),
        "threshold": DIFF_THRESHOLD,
        "side_by_side": side_path.name,
        "diff_image": diff_path.name,
        "note": "只给统计，不给结论；字体/抗锯齿差异需人工判断。",
    }
    (out_dir / f"{label}_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--editor", type=Path, required=True,
                        help="编辑器样例图（render_paint_samples.py 的产物）")
    parser.add_argument("--game", type=Path, required=True,
                        help="真机截图（建议与样例同尺寸裁剪）")
    parser.add_argument("--out", type=Path, required=True, help="输出目录")
    parser.add_argument("--label", default=None, help="文件名前缀（默认取样例名）")
    args = parser.parse_args(argv)

    try:
        report = compare(args.editor, args.game, args.out, args.label)
    except (OSError, ValueError) as exc:
        print(f"比对失败：{exc}", file=sys.stderr)
        return 2
    print(f"{report['label']}：尺寸{'一致' if report['sizes_match'] else '不一致'}"
          f"（编辑器 {report['editor_size']} / 真机 {report['game_size']}）")
    print(f"  差异像素 {report['differing_pixels']}"
          f"（{report['differing_ratio'] * 100:.2f}%），"
          f"平均绝对差 {report['mean_abs_diff']}，"
          f"差异包围盒 {report['diff_bbox']}")
    print(f"  并排图：{args.out / report['side_by_side']}")
    print(f"  差异图：{args.out / report['diff_image']}")
    print("  结论请人工填进 ui_editor/docs/PAINT_CHECKLIST.md"
          "（没核对过的格子留空）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
