"""控件绘制样例：给「编辑器里好看 ≠ 游戏里一样」提供可复现的比对对象。

分析报告 P2-4 的结论是：`painters.py` 是全项目最像游戏、却验证最少的一层
（覆盖率 42%），继续堆单测收益有限——**真机外观只能人工核对**。所以这一层
不再假装能用测试证明「画得对」，而是产出三样东西：

1. **可复现样例**：38 类控件各渲一张 PNG（默认模板 + 可选真实资源包），
   同一命令在任何机器上给出同样字节（见 `manifest.json` 的 SHA256）；
2. **对照清单**：`ui_editor/docs/PAINT_CHECKLIST.md` 每个类型一行，游戏侧
   各列**留空等真机截图**（谁核对谁填，不预填「一致」）；
3. **差异辅助**：`tools/paint_compare.py` 把样例与真机截图配对比对，
   只给统计，不给「通过」结论。

本模块只负责渲染与清单数据；命令行入口在
`ui_editor/tools/render_paint_samples.py`，机检在
`ui_editor/tests/test_paint_samples.py`（全类型渲染冒烟 + 清单与代码一致）。
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QImage, QPainter

from ..core import defaults_data, painters
from ..core.assets import AssetResolver
from ..core.model import Widget

__all__ = [
    "CHECKLIST_PATH",
    "IMAGE_FIELDS",
    "SAMPLE_IMAGE",
    "SampleSpec",
    "checklist_rows",
    "contact_sheet",
    "dependencies_of",
    "editor_note",
    "painter_name",
    "render_checklist_markdown",
    "render_sample",
    "sample_specs",
    "write_samples",
]

PACKAGE_ROOT = Path(__file__).resolve().parents[3]  # …/ui_editor
CHECKLIST_PATH = PACKAGE_ROOT / "docs" / "PAINT_CHECKLIST.md"

#: 控件里表示图片资源的字段（默认模板里为空；样例会给它们填一个占位路径，
#: 这样「有图但缺资源」的占位框与文件名标注也能进对照清单）
IMAGE_FIELDS = ("sFileName", "sBgFileName", "sBarFileName")
SAMPLE_IMAGE = "images/paint_sample.png"

#: 每个绘制函数一句话说明（清单的「编辑器画什么」列）
_PAINTER_NOTES = {
    "_paint_main_frame": "整窗底板：底图/边框 + 子控件由场景分别绘制",
    "_paint_frame": "矩形底板（有图用图，缺图按占位框 + 文件名标注）",
    "_paint_image": "图片控件：画首帧，按 iWidth/iHeight 拉伸",
    "_paint_nine": "九宫格：源图**固定三分**近似（边角不拉伸，切割线不可配）",
    "_paint_button": "按钮：底图/样式底色 + 居中 sText；多状态按预览开关近似",
    "_paint_text_button": "文字按钮：按 ui.lst TBStyle 着色 + sText",
    "_paint_text": "文字：按 iFont 取字体表字号/字色，居中或多行",
    "_paint_hotbox": "热区：半透明提示框（编辑用，游戏里不可见）",
    "_paint_edit": "输入框：边框 + sText 或提示字",
    "_paint_grid": "网格类：表头/行列线与单元格文字（按行列推算尺寸）",
    "_paint_table": "表格：表头 + 网格 + 单元格文字",
    "_paint_list": "列表：行分隔线 + 行文字",
    "_paint_progress": "进度条：轨道 + 按 iValue 比例填充",
    "_paint_scrollbar": "滚动条：轨道 + 滑块（按 iValue 位置）",
    "_paint_fallback": "未登记的控件类型：画占位框 + 类型名（说明该类型没有专用绘制）",
}

#: 逐类型补充说明（覆盖通用说明里说不清的点）
_TYPE_NOTES = {
    "CPngNineFrame": "固定三分近似；游戏切法未比对",
    "CPngList": "按行网格近似；游戏列表项样式未比对",
    "CPngTable": "表格近似；真机列宽/表头样式未比对",
    "CTableView": "可滚动表格的近似；滚动与裁剪未比对",
    "CTitleTableView": "带标题栏表格的近似",
    "CCombCheckButton": "组合勾选按钮：按栅格近似，勾选态未比对",
    "CBox": "容器：画边框与栅格间距，不画子控件本身",
    "CHPageButton": "翻页按钮：按样式底色 + 文字近似",
    "CVPageButton": "翻页按钮：按样式底色 + 文字近似",
    "CHPagePngButton": "翻页按钮（图片皮肤）：与九宫格切法相关，未比对",
    "CVPagePngButton": "翻页按钮（图片皮肤）：与九宫格切法相关，未比对",
    "CProgress": "轨道用图或底色，填充比例按 iValue（0–100 假设）",
    "CVScrollBar": "滑块位置按 iValue 线性映射，游戏手感未比对",
    "CVPngScrollBar": "图片皮肤滚动条：拉伸方式未比对",
    "CImagesFrame": "按 iRow/iCol 平铺首帧，间距 iHSpace/iVSpace",
    "CSpriteFrame": "精灵首帧（多帧动画只画第 0 帧）",
    "CBitmapFrame": "位图控件：拉伸整图（与九宫格不同）",
    "CEdit": "输入框：编辑态外观，游戏焦点态未比对",
    "CHotBox": "热区在游戏里不可见；这里画半透明框仅为编辑",
    "CRichTextFrame": "富文本按纯文本近似（不解析标签）",
    "CTextFrameEx": "扩展文本：多行与对齐按纯文本近似",
}


@dataclass(frozen=True)
class SampleSpec:
    """一个类型的样例：默认模板 + 被填的图片字段。"""

    wtype: str
    props: dict
    image_fields: tuple[str, ...] = field(default_factory=tuple)


def sample_specs(image_path: str = SAMPLE_IMAGE) -> list[SampleSpec]:
    """38 类控件的样例规格（按类型名排序，保证每次输出顺序一致）。

    ``image_path`` 是填进图片字段的资源路径：默认是个**不存在**的占位路径
    （走缺资源分支，能看出占位框与文件名标注）；用 ``--image`` 指到真实
    客户端资源时，样例才真正走图片/精灵解码那条路。
    """
    specs: list[SampleSpec] = []
    for wtype in sorted(defaults_data.DEFAULT_PROPS):
        props = dict(defaults_data.DEFAULT_PROPS[wtype])
        props["sName"] = wtype
        faked = tuple(name for name in IMAGE_FIELDS if name in props)
        for name in faked:
            props[name] = image_path
        specs.append(SampleSpec(wtype, props, faked))
    return specs


def painter_name(wtype: str) -> str:
    """该类型实际走哪个绘制函数（未登记的类型会走兜底）。"""
    func = painters._PAINTERS.get(wtype, painters._paint_fallback)
    return getattr(func, "__name__", str(func))


def dependencies_of(wtype: str, props: dict) -> str:
    """该类型绘制时依赖什么（图片/样式/字体/网格），由字段推断。"""
    deps: list[str] = []
    if any(name in props for name in IMAGE_FIELDS):
        deps.append("图片资源")
    if any(key in props for key in ("iStyle", "TBStyle", "sStyle", "iSkin")):
        deps.append("ui.lst 样式")
    if "iFont" in props or wtype.startswith("CText"):
        deps.append("字体表 iFont")
    if wtype in ("CTable", "CTableView", "CTitleTableView", "CPngTable",
                 "CList", "CPngList", "CBox", "CCombCheckButton",
                 "CImagesFrame"):
        deps.append("行列参数")
    return "、".join(deps) if deps else "无（纯几何）"


def editor_note(wtype: str) -> str:
    """清单「编辑器画什么」列：绘制函数通用说明 + 逐类型补充。"""
    note = _PAINTER_NOTES.get(painter_name(wtype), "（未登记说明）")
    extra = _TYPE_NOTES.get(wtype)
    return f"{note}；{extra}" if extra else note


def render_sample(spec: SampleSpec, ctx: painters.PaintContext) -> QImage:
    """按控件实际尺寸渲染一张样例图（透明背景，与画布一致）。"""
    widget = Widget(spec.props)
    width, height = painters.effective_size(widget, ctx)
    width = max(1, int(width))
    height = max(1, int(height))
    image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(QColor(0, 0, 0, 0))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    try:
        painters.paint_widget(painter, widget, ctx)
    finally:
        painter.end()
    return image


def contact_sheet(samples: list[tuple[str, QImage]], *,
                  columns: int = 5, cell: tuple[int, int] = (260, 190),
                  padding: int = 10) -> QImage:
    """把全部样例拼成一张带类型名标注的联络表（便于逐行核对）。"""
    rows = (len(samples) + columns - 1) // columns
    cell_w, cell_h = cell
    width = columns * cell_w + padding
    height = rows * cell_h + padding
    sheet = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    sheet.fill(QColor(250, 250, 250, 255))
    painter = QPainter(sheet)
    painter.setPen(QColor(90, 90, 90))
    for index, (wtype, image) in enumerate(samples):
        column, row = index % columns, index // columns
        x = padding + column * cell_w
        y = padding + row * cell_h
        painter.drawText(QRect(x, y, cell_w - 8, 16),
                         Qt.AlignmentFlag.AlignLeft, f"{index + 1}. {wtype}")
        area = QRect(x, y + 18, cell_w - 14, cell_h - 30)
        scaled = image.scaled(area.width(), area.height(),
                              Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.FastTransformation)
        painter.drawImage(area.x(), area.y(), scaled)
    painter.end()
    return sheet


def checklist_rows() -> list[dict]:
    """对照清单的数据行（游戏侧各列一律留空——那是真机截图后人工填的）。"""
    rows: list[dict] = []
    for spec in sample_specs():
        rows.append({
            "wtype": spec.wtype,
            "painter": painter_name(spec.wtype),
            "note": editor_note(spec.wtype),
            "dependencies": dependencies_of(spec.wtype, spec.props),
            "game_expected": "",
            "game_screenshot": "",
            "difference": "",
        })
    return rows


def render_checklist_markdown() -> str:
    """生成对照清单 Markdown（提交进仓库的那份就是它）。"""
    rows = checklist_rows()
    lines = [
        "# 控件绘制对照清单（编辑器 vs 真机）",
        "",
        "> 由 `ui_editor/src/ui_editor/ui/paint_samples.py` 生成（`python3 "
        "ui_editor/tools/render_paint_samples.py --checklist-md "
        "ui_editor/docs/PAINT_CHECKLIST.md`）。",
        "> 类型集合与 `defaults_data.DEFAULT_PROPS` 一致，由 "
        "`ui_editor/tests/test_paint_samples.py` 机检。",
        "",
        "## 这份清单解决什么问题",
        "",
        "`painters.py` 是全项目最像游戏、却验证最少的一层：它只能近似，"
        "而「编辑器里好看 ≠ 游戏里一样」。单测能证明「不崩、尺寸对」，"
        "**证明不了外观一致**——所以这里把判断交给人，但把材料准备好：",
        "",
        "1. 生成样例：`python3 ui_editor/tools/render_paint_samples.py --out "
        "<仓库外目录>`（可加 `--pack data/xxx.fls` 用真实资源再渲一套）；",
        "2. 在 Windows 真机上打开对应界面截图（同尺寸裁剪，别缩放）；",
        "3. 用 `python3 ui_editor/tools/paint_compare.py --editor <样例.png> "
        "--game <真机截图.png> --out <目录>` 得到并排图与像素差异统计；",
        "4. 把结论填回本表：**没做过真机核对的格子必须留空**，"
        "不要预填「一致」；发现差异先记录，再决定改绘制还是改用法。",
        "",
        "## 规矩",
        "",
        "* 只对「看得出差异会误导用户」的项目较真；纯抗锯齿/字体渲染差异"
        "（系统字体不同）可以记「环境差异」而不改代码。",
        "* 结论一旦从「有差异」变成「已修」，要在"
        "`docs/STATUS.md` 写明版本与证据（截图路径）。",
        "* 本表不替代进游戏验收：`AGENTS.md` §0「能运行 ≠ 正确」同样适用。",
        "",
        "| # | 类型 | 绘制函数 | 编辑器画什么 | 依赖 | "
        "游戏侧期望外观 | 真机截图 | 差异 | 结论 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for index, row in enumerate(rows, start=1):
        lines.append(
            f"| {index} | `{row['wtype']}` | `{row['painter']}` | "
            f"{row['note']} | {row['dependencies']} |  |  |  |  |")
    lines += [
        "",
        f"共 **{len(rows)}** 类控件；样例图与 SHA256 见渲染命令输出的 "
        "`manifest.json`。",
        "",
    ]
    return "\n".join(lines)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_samples(out_dir: Path, *, pack: Path | None = None,
                  assets_dir: Path | None = None,
                  image_path: str | None = None,
                  scale: float = 1.0, contact: bool = True) -> dict:
    """渲染全部样例到 ``out_dir``，返回 manifest（含每个文件的 SHA256）。

    ``pack`` / ``assets_dir`` 用来挂载真实客户端资源；``image_path`` 是填进
    图片字段的资源路径（默认占位路径）。两者一起用才走真实图片解码——
    仓库里的 `data/*.fls` **没有界面图**（界面在未入库的 `interface.fls`），
    所以 ``--pack`` 单独用时 manifest 会如实记 ``image_found: false``。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    resolver = AssetResolver()
    if pack is not None:
        resolver.mount_pack(pack)
    if assets_dir is not None:
        resolver.add_loose_dir(assets_dir)
    chosen_image = image_path or SAMPLE_IMAGE
    image_found = resolver.resource_exists(chosen_image)
    ctx = painters.PaintContext(assets=resolver)
    ctx.styles = resolver.fetch_styles() or ctx.styles
    items: list[dict] = []
    images: list[tuple[str, QImage]] = []
    for spec in sample_specs(chosen_image):
        image = render_sample(spec, ctx)
        if scale != 1.0:
            image = image.scaled(
                max(1, int(image.width() * scale)),
                max(1, int(image.height() * scale)),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
        filename = f"{spec.wtype}.png"
        path = out_dir / filename
        if not image.save(str(path)):
            raise OSError(f"无法写入样例图：{path}")
        items.append({
            "wtype": spec.wtype,
            "painter": painter_name(spec.wtype),
            "note": editor_note(spec.wtype),
            "dependencies": dependencies_of(spec.wtype, spec.props),
            "width": image.width(),
            "height": image.height(),
            "file": filename,
            "sha256": _sha256(path),
            "image_fields_faked": list(spec.image_fields),
        })
        images.append((spec.wtype, image))
    manifest = {
        "generated_by": "ui_editor/tools/render_paint_samples.py",
        "pack": str(pack) if pack is not None else None,
        "assets_dir": str(assets_dir) if assets_dir is not None else None,
        "image_path": chosen_image,
        "image_found": image_found,
        "real_resources": bool(image_found),
        "styles_loaded": bool(getattr(ctx.styles, "loaded", False)),
        "scale": scale,
        "image_placeholder": SAMPLE_IMAGE,
        "note": (
            "样例只证明编辑器**画出了什么**；与游戏是否一致必须人工核对，"
            "见 ui_editor/docs/PAINT_CHECKLIST.md。"
            + (" 图片字段用的真实资源："
               f"{chosen_image}" if image_found else
               " 本次图片字段指向的资源不存在（未给 --image 或该路径不在"
               "挂载的包/目录里）：走的是缺资源占位分支，样例只能核对占位"
               "框与排版，不能核对图片解码。")),
        "items": items,
    }
    if contact:
        sheet = contact_sheet(images)
        sheet_path = out_dir / "contact_sheet.png"
        if not sheet.save(str(sheet_path)):
            raise OSError(f"无法写入联络表：{sheet_path}")
        manifest["contact_sheet"] = {
            "file": sheet_path.name,
            "sha256": _sha256(sheet_path),
            "columns": 5,
        }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    return manifest
