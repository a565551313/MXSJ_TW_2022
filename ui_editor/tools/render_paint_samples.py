#!/usr/bin/env python3
"""渲染 38 类控件的绘制样例（给「编辑器 vs 真机」人工对照用）。

用法（仓库根目录）：

```bash
python3 ui_editor/tools/render_paint_samples.py --out /tmp/paint_samples
python3 ui_editor/tools/render_paint_samples.py --out /tmp/paint_samples \\
        --pack data/magicres5.fls        # 用真实资源再渲一套
python3 ui_editor/tools/render_paint_samples.py --checklist-md \\
        ui_editor/docs/PAINT_CHECKLIST.md   # 重新生成对照清单骨架
```

产出（写到 ``--out`` 目录，**默认不落进仓库**）：每个类型一张 PNG、
带类型名标注的 ``contact_sheet.png``、以及 ``manifest.json``（尺寸 + 每个
文件的 SHA256 + 该类型走哪个绘制函数）。清单与规矩见
``ui_editor/docs/PAINT_CHECKLIST.md``。

这里不判断「画得对不对」——那是一定要人工看真机截图的事
（`notes`/分析报告 P2-4 的结论：继续堆单测收益有限）。
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
SRC = REPO_ROOT / "ui_editor" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# 无显示器环境（Linux 沙箱 / CI）也要能渲：先于 Qt 导入设置
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QGuiApplication  # noqa: E402

from ui_editor.ui.paint_samples import (  # noqa: E402
    CHECKLIST_PATH,
    render_checklist_markdown,
    sample_specs,
    write_samples,
)


def default_out_dir() -> Path:
    """默认输出目录：系统临时目录下（仓库外，符合生成物不入库的约定）。"""
    return Path(tempfile.gettempdir()) / "ui_editor_paint_samples"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=None,
                        help=f"输出目录（默认 {default_out_dir()}）")
    parser.add_argument("--pack", type=Path, default=None,
                        help="挂载真实资源包（.fls）；界面图在 interface.fls 里，"
                             "仓库内没有它时不加 --assets-dir/--image 仍是占位分支")
    parser.add_argument("--assets-dir", type=Path, default=None,
                        help="挂载散装资源目录（解开的客户端资源）")
    parser.add_argument("--image", default=None,
                        help="填进图片字段的资源路径（默认占位路径；指到真实"
                             "资源时才走图片/精灵解码）")
    parser.add_argument("--scale", type=float, default=1.0,
                        help="输出缩放（默认 1.0；放大便于肉眼比对）")
    parser.add_argument("--no-contact-sheet", action="store_true",
                        help="不生成联络表")
    parser.add_argument("--checklist-md", type=Path, nargs="?",
                        const=CHECKLIST_PATH, default=None,
                        help="只（重新）生成对照清单 Markdown，不渲染样例")
    args = parser.parse_args(argv)

    if args.checklist_md is not None:
        text = render_checklist_markdown()
        args.checklist_md.parent.mkdir(parents=True, exist_ok=True)
        args.checklist_md.write_text(text, encoding="utf-8")
        print(f"已写入对照清单：{args.checklist_md}"
              f"（{len(sample_specs())} 类控件）")
        return 0

    app = QGuiApplication.instance() or QGuiApplication([])
    out_dir = args.out or default_out_dir()
    pack = args.pack
    if pack is not None and not pack.is_file():
        print(f"找不到资源包：{pack}", file=sys.stderr)
        return 2
    if args.assets_dir is not None and not args.assets_dir.is_dir():
        print(f"找不到资源目录：{args.assets_dir}", file=sys.stderr)
        return 2
    manifest = write_samples(out_dir, pack=pack, assets_dir=args.assets_dir,
                             image_path=args.image, scale=args.scale,
                             contact=not args.no_contact_sheet)
    print(f"已渲染 {len(manifest['items'])} 类控件样例：{out_dir}")
    print(f"  联络表：{(out_dir / 'contact_sheet.png')}"
          if "contact_sheet" in manifest else "  （未生成联络表）")
    print(f"  图片字段：{manifest['image_path']}"
          f"（{'真实资源，命中' if manifest['image_found'] else '占位分支，未命中'}）")
    print(f"  清单：{manifest['note']}")
    print("  下一步：在 Windows 真机上对同尺寸截图，再用 "
          "ui_editor/tools/paint_compare.py 比对，结论填回 "
          "ui_editor/docs/PAINT_CHECKLIST.md")
    del app
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
