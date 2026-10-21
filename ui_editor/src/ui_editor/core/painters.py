"""控件绘制规则（编辑器画布用的近似渲染）。

目标是让布局在编辑器里「所见即所得」到可对照的程度：图片类
控件画精灵首帧，按钮画底图加文字，文字类按 ui.lst 的字体与
颜色画，表格画表头与网格。客户端内部的精确绘制仍是近似：
`CPngNineFrame` 按**源图固定三分**做九宫格（边角不拉伸、边与中心
拉伸），切割线不可配置、与游戏的切法未做比对（M3.3 的切割线编辑
仍未做）；按钮多状态只按预览开关给近似态。找不到图片时画占位框
并标注文件名，便于检查引用。

尺寸约定：``iWidth/iHeight`` 为正用之；为 0 时取图片首帧尺寸
（网格类按行列推算），再不行用兜底尺寸。坐标由场景按父子关系
处理，本模块只在控件本地 (0,0) 起画。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen, QPixmap

from . import fidelity, runtime_state, slicing
from .assets import AssetResolver
from .model import Widget
from .styles import StyleBook

__all__ = ["PaintContext", "effective_size", "paint_widget"]


@dataclass
class PaintContext:
    """绘制上下文：资源、样式、占位标注开关与图片缓存。"""

    assets: AssetResolver
    styles: StyleBook = field(default_factory=StyleBook)
    show_names: bool = True
    button_state: str = "normal"  # 按钮状态预览：normal/pressed/hover/disabled
    animation_frame: int = 0  # .spr/精灵画布预览帧（仅预览，不写回）
    # 代码皮肤绑定：控件名 -> SkinRef（脚本在原地现造的按钮，静态推断）
    code_skins: dict = field(default_factory=dict)
    _pixmaps: dict[tuple[str, int], QPixmap] = field(default_factory=dict)
    # 右下角保真度角标（原生/近似/模拟），可关。放最后：不能插进
    # button_state 等既有字段之前，否则外部按位置构造会静默错位。
    show_badges: bool = True

    def pixmap(self, name: str, frame: int | None = None) -> QPixmap | None:
        if frame is None:
            frame = self.animation_frame if name.lower().endswith(".spr") else 0
        key = (name.replace("/", "\\"), frame)
        if key in self._pixmaps:
            return self._pixmaps[key]
        result: QPixmap | None = None
        if name.lower().endswith(".spr"):
            asset = self.assets.fetch_animation(name)
            animation_frame = asset.frame(frame) if asset is not None else None
            image = (animation_frame.image
                     if animation_frame is not None else None)
            if image is not None:
                result = QPixmap.fromImage(image)
        else:
            frames = self.assets.fetch_image(name)
            if frames and 0 <= frame < len(frames):
                result = QPixmap.fromImage(frames[frame])
        self._pixmaps[key] = result
        return result

    def slice_pixmap(self, name: str, index: int, image,
                     state: int = 0) -> QPixmap:
        """切片块转 QPixmap 并缓存：拖动/缩放时不再逐帧重复上传。

        ``state`` 必须进键：三态横片的每个态是不同文件，但 cell 下标
        都是 0..2；只按 ``(name, index)`` 缓存会让先画的常态图一直顶替
        按下/悬停态（0.12.7 初版的真实缺陷）。
        """
        key = (name.replace("/", "\\") + f"#slice{state}", index)
        cached = self._pixmaps.get(key)
        if cached is None:
            cached = QPixmap.fromImage(image)
            self._pixmaps[key] = cached
        return cached

    def frame_size(self, name: str) -> tuple[int, int] | None:
        pixmap = self.pixmap(name, 0)
        if pixmap is None:
            return None
        return pixmap.width(), pixmap.height()


# ------------------------------------------------------------------
# 尺寸与公共取值
# ------------------------------------------------------------------

_IMAGE_KEY_BY_TYPE = {"CProgress": "sBgFileName"}


def _image_key(widget: Widget) -> str:
    return _IMAGE_KEY_BY_TYPE.get(widget.wtype, "sFileName")


def _int(widget: Widget, key: str, default: int = 0) -> int:
    value = widget.props.get(key, default)
    return value if isinstance(value, int) and not isinstance(value, bool) \
        else default


def effective_size(widget: Widget, ctx: PaintContext, *,
                   fallback: bool = True) -> tuple[int, int]:
    """控件的有效像素尺寸（见模块头注的约定）。

    ``fallback=False`` 时不用兜底尺寸：两项都测不出来就保留 <=0 的
    「未知」。几何夹取要用这个模式——兜底尺寸只是编辑器画占位框时的
    视觉尺寸，不能当成真实的父边界（见 ``snap.clamp_in_parent``）。
    """
    width, height = widget.width, widget.height
    if width > 0 and height > 0:
        return width, height
    name = str(widget.props.get(_image_key(widget), "") or "")
    size = ctx.frame_size(name) if name else None
    if size is not None:
        fw, fh = size
        if widget.wtype == "CImagesFrame":
            cols = max(1, _int(widget, "iCol", 1))
            rows = max(1, _int(widget, "iRow", 1))
            fw = cols * fw + (cols - 1) * _int(widget, "iHSpace")
            fh = rows * fh + (rows - 1) * _int(widget, "iVSpace")
        if width <= 0:
            width = fw
        if height <= 0:
            height = fh
    if fallback:
        if width <= 0:
            width = 120 if widget.wtype == "CMainFrame" else 80
        if height <= 0:
            height = 90 if widget.wtype == "CMainFrame" else 24
    return width, height


def _color_from_value(value: object, default: QColor) -> QColor:
    """把 .dlg 里五花八门的颜色值解析为 QColor。

    支持：单个打包整数 ``0xRRGGBB``、[r, g, b] 序列、
    [打包整数] 单元素序列。
    """
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return QColor((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)
    if isinstance(value, (list, tuple)) and value:
        nums = [v for v in value
                if isinstance(v, int) and not isinstance(v, bool)]
        if len(nums) >= 3 and all(0 <= n <= 255 for n in nums[:3]):
            return QColor(nums[0], nums[1], nums[2])
        if nums:
            return _color_from_value(nums[0], default)
    return default


def _color_from_style(text: str, default: QColor) -> QColor:
    """解析 ui.lst 中的颜色串（空格分隔整数，取前三个为 RGB）。"""
    try:
        nums = [int(tok) for tok in text.split()]
    except ValueError:
        return default
    if len(nums) >= 3 and all(0 <= n <= 255 for n in nums[:3]):
        return QColor(nums[0], nums[1], nums[2])
    return default


def _font(widget: Widget, ctx: PaintContext, pixel_size: int = 13) -> QFont:
    """按 iFont（或文字按钮样式的 ButtonFont）取字体，取不到用默认。"""
    font_def = None
    if widget.wtype == "CTextButton":
        style = ctx.styles.tbstyle(_int(widget, "iStyle"))
        try:
            font_def = ctx.styles.font(int(style.get("ButtonFont", "")))
        except (TypeError, ValueError):
            font_def = None
    if font_def is None:
        font_def = ctx.styles.font(_int(widget, "iFont"))
    font = QFont()
    if font_def is not None:
        font.setFamily(font_def.name)
        font.setPixelSize(max(8, font_def.size or pixel_size))
        font.setWeight(QFont.Weight(font_def.weight)
                       if 100 <= font_def.weight <= 900
                       else QFont.Weight.Normal)
    else:
        font.setPixelSize(pixel_size)
    return font


_RICH_CODE_RE = re.compile(r"#[0-9a-fA-F]{6}|#[a-zA-Z]")


def _plain_text(widget: Widget) -> str:
    text = widget.props.get("sText") or widget.props.get("sTitle") or ""
    return str(text)


def _draw_text(p: QPainter, rect: QRectF, text: str, font: QFont,
               color: QColor, align: int = 0, rich: bool = False) -> None:
    if not text:
        return
    if rich:
        text = _RICH_CODE_RE.sub("", text)
    flags = Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignTop
    if align == 1:
        flags |= Qt.AlignmentFlag.AlignHCenter
    elif align == 2:
        flags |= Qt.AlignmentFlag.AlignRight
    else:
        flags |= Qt.AlignmentFlag.AlignLeft
    p.setFont(font)
    p.setPen(color)
    p.drawText(rect.adjusted(3, 2, -3, -2), flags, text)


def _placeholder(p: QPainter, rect: QRectF, label: str, ctx: PaintContext,
                 color: QColor | None = None) -> None:
    if color is None:
        color = QColor(255, 170, 80)
    p.setPen(QPen(color, 1, Qt.PenStyle.DashLine))
    p.setBrush(QColor(255, 170, 80, 24))
    p.drawRect(rect)
    if ctx.show_names and label:
        p.setPen(color)
        p.setFont(_small_font())
        p.drawText(rect.adjusted(2, 1, -2, -1),
                   Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                   label)


def _small_font() -> QFont:
    font = QFont()
    font.setPixelSize(10)
    return font


def _name_label(w: Widget) -> str:
    return f"{w.wtype}\n{w.name}" if w.name else w.wtype


# ------------------------------------------------------------------
# 各类控件绘制（均在本地坐标 (0,0) 起画）
# ------------------------------------------------------------------

def _rect(w: Widget, ctx: PaintContext) -> QRectF:
    width, height = effective_size(w, ctx)
    return QRectF(0, 0, width, height)


def _draw_slice(p: QPainter, w: Widget, ctx: PaintContext, name: str,
                state: int = 0) -> bool:
    """目录型基路径的切片：按**资源切片自己的像素**当切割线贴合控件。

    ``state`` 是按钮态序号（0 = 常态）：三态横片族有真态切片，其余族
    没有，取不到就返回 False 交给调用方。

    返回 True 表示已按切片画完（含「切片取不到」的 False 交给调用方）。
    全透明的切片不画：底下内容照常露出，不铺白底。切片图转 QPixmap
    走 :meth:`PaintContext.slice_pixmap` 缓存，拖动/缩放时不重复上传。
    """
    recipe = ctx.assets.fetch_slice_state(name, state)
    if recipe is None:
        return False
    rect = _rect(w, ctx)
    plan = recipe.plan()
    for cell in slicing.layout(plan, rect.width(), rect.height(),
                               recipe.blank):
        image = recipe.images[cell.index]
        pixmap = ctx.slice_pixmap(name, cell.index, image, state)
        p.drawPixmap(QRectF(*cell.dst), pixmap, QRectF(*cell.src))
    return True


def _runtime_hidden(w: Widget) -> str:
    """"hidden"/"not_loaded"/其他。画布要把它和「资源加载失败」分开。"""
    state = runtime_state.state_of(w)
    return state if state in (runtime_state.HIDDEN,
                              runtime_state.NOT_LOADED) else ""


def _paint_runtime_note(p: QPainter, w: Widget, ctx: PaintContext,
                        state: str) -> None:
    """运行时隐藏/不加载的角标：虚线框 + 中文说明（近似预览仍画在下面）。"""
    rect = _rect(w, ctx)
    p.save()
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor(224, 168, 60), 1, Qt.PenStyle.DashLine))
    p.drawRect(rect.adjusted(0.5, 0.5, -0.5, -0.5))
    label = ("运行时隐藏 bShow=0" if state == runtime_state.HIDDEN
             else "bLoad=0 可能不加载")
    font = _small_font()
    p.setFont(font)
    text_w = p.fontMetrics().horizontalAdvance(label) + 10
    chip = QRectF(2, max(0.0, rect.height() - 16), text_w, 14)
    p.fillRect(chip, QColor(224, 168, 60, 210))
    p.setPen(QColor(40, 30, 10))
    p.drawText(chip, Qt.AlignmentFlag.AlignCenter, label)
    p.restore()


def _paint_main_frame(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    rect = _rect(w, ctx)
    gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
    gradient.setColorAt(0, QColor(66, 80, 106))
    gradient.setColorAt(1, QColor(41, 50, 68))
    p.setBrush(gradient)
    p.setPen(QPen(QColor(150, 170, 205), 1))
    p.drawRect(rect.adjusted(0.5, 0.5, -0.5, -0.5))
    title_h = min(26.0, rect.height())
    p.setBrush(QColor(84, 102, 134))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(QRectF(1, 1, rect.width() - 2, title_h - 1))
    title = _plain_text(w) or w.name
    p.setPen(QColor(235, 240, 250))
    font = _font(w, ctx, 13)
    font.setBold(True)
    p.setFont(font)
    p.drawText(QRectF(8, 0, rect.width() - 16, title_h),
               Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
               title)


def _paint_frame(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    rect = _rect(w, ctx)
    name = str(w.props.get("sFileName", "") or "")
    if name and _draw_slice(p, w, ctx, name):
        return
    pixmap = ctx.pixmap(name) if name else None
    if pixmap is not None:
        p.drawPixmap(rect, pixmap, QRectF(pixmap.rect()))
        return
    p.setBrush(QColor(255, 255, 255, 16))
    p.setPen(QPen(QColor(200, 210, 230, 90), 1))
    p.drawRect(rect.adjusted(0.5, 0.5, -0.5, -0.5))
    if ctx.show_names:
        p.setPen(QColor(180, 190, 210, 160))
        p.setFont(_small_font())
        p.drawText(rect.adjusted(3, 2, -3, -2),
                   Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                   _name_label(w))


def _paint_image(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    rect = _rect(w, ctx)
    name = str(w.props.get("sFileName", "") or "")
    if name and _draw_slice(p, w, ctx, name):
        return
    pixmap = ctx.pixmap(name) if name else None
    if pixmap is None:
        _placeholder(p, rect, name.replace("\\", "/").split("/")[-1]
                     or _name_label(w), ctx)
        return
    p.drawPixmap(rect, pixmap, QRectF(pixmap.rect()))


def _paint_nine(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    """九宫格：**单图**按固定三分切（切割线未与客户端核实，近似）。

    目录型九片资源不走这里——那是 :func:`_draw_slice` 按资源切片尺寸拼，
    属于原生。这里是 ``CPngNineFrame`` 只有一张图的情形：三分线是编辑器
    的近似，边角不拉伸、边与中心拉伸。
    """
    rect = _rect(w, ctx)
    name = str(w.props.get("sFileName", "") or "")
    if name and _draw_slice(p, w, ctx, name):
        return
    pixmap = ctx.pixmap(name) if name else None
    if pixmap is None:
        _placeholder(p, rect, name.replace("\\", "/").split("/")[-1]
                     or _name_label(w), ctx)
        return
    for src, dst in slicing.nine_thirds_cells(
            pixmap.width(), pixmap.height(), rect.width(), rect.height()):
        p.drawPixmap(QRectF(*dst), pixmap, QRectF(*src))


def _paint_grid(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    """网格图片（CImagesFrame/CPngList/CCombCheckButton）：逐格画帧。"""
    rect = _rect(w, ctx)
    name = str(w.props.get("sFileName", "") or "")
    cols = max(1, _int(w, "iCol", 1))
    rows = max(1, _int(w, "iRow", 1))
    hspace = _int(w, "iHSpace")
    vspace = _int(w, "iVSpace")
    cell_w = (rect.width() - (cols - 1) * hspace) / cols
    cell_h = (rect.height() - (rows - 1) * vspace) / rows
    frames = ctx.assets.fetch_image(name) if name else None
    for index in range(rows * cols):
        row, col = divmod(index, cols)
        cell = QRectF(col * (cell_w + hspace), row * (cell_h + vspace),
                      cell_w, cell_h)
        pixmap = None
        if frames:
            image = frames[index % len(frames)]
            pixmap = QPixmap.fromImage(image)
        if pixmap is not None:
            p.drawPixmap(cell, pixmap, QRectF(pixmap.rect()))
        else:
            _placeholder(p, cell,
                         name.replace("\\", "/").split("/")[-1]
                         or _name_label(w), ctx,
                         QColor(140, 180, 255))


# -- 按钮多状态（M3.2：精灵帧 / 竖条多态 / 模拟三路） ----------------
_BUTTON_STATE_INDEX = fidelity.BUTTON_STATE_INDEX  # 顺序未核实，见 fidelity


def state_slice(img_w: int, img_h: int, widget_w: int, widget_h: int,
                frame_count: int, state_idx: int):
    """判定非正常态画哪一块。

    返回 ("frame", 帧序号) —— 精灵帧够数；或 ("strip",
    (x, y, w, h)) —— 单图高度至少是控件高两倍时按等分竖条切
    （按钮图常见的一图多态排法）；都不满足返回 None（走模拟）。
    """
    if state_idx <= 0:
        return None
    if frame_count > state_idx:
        return ("frame", state_idx)
    if widget_h > 0 and img_h >= widget_h * 2:
        parts = img_h // widget_h
        if 2 <= parts <= 8 and state_idx < parts:
            return ("strip", (0, state_idx * widget_h, img_w, widget_h))
    return None


def _button_state_pixmap(ctx: PaintContext, name: str, w: Widget):
    """按当前 button_state 取 (pixmap, 源矩形)；正常态返回 None。"""
    state = ctx.button_state
    if state == "normal" or state not in _BUTTON_STATE_INDEX:
        return None
    idx = _BUTTON_STATE_INDEX[state]
    frames = ctx.assets.fetch_image(name) or []
    base = ctx.pixmap(name, 0)
    if base is None:
        return None
    found = state_slice(base.width(), base.height(),
                        w.width, w.height, len(frames), idx)
    if found is None:
        return None
    kind, payload = found
    if kind == "frame":
        pixmap = ctx.pixmap(name, payload)  # type: ignore[arg-type]
        if pixmap is not None:
            return pixmap, QRectF(pixmap.rect())
        return None
    return base, QRectF(*payload)  # type: ignore[operator]


def _simulate_state_overlay(p: QPainter, rect: QRectF,
                            ctx: PaintContext) -> None:
    """切不出真状态时的近似预览（压暗/提亮/灰化），仅供编辑参考。"""
    state = ctx.button_state
    if state == "pressed":
        p.fillRect(rect, QColor(0, 0, 0, 70))
        p.setPen(QPen(QColor(0, 0, 0, 120), 1))
        p.drawLine(rect.topLeft(), rect.topRight())
    elif state == "hover":
        p.fillRect(rect, QColor(255, 255, 255, 45))
    elif state == "disabled":
        p.fillRect(rect, QColor(128, 128, 128, 110))


#: 绘制来源：画布实际用哪条路画出来的（角标与诊断据此判定，不再各算一套）
SOURCE_CODE_SKIN = "code_skin"          # 脚本现造按钮的皮肤图
SOURCE_SLICE = "slice"                  # 目录型基路径的横/竖/九片（常态）
SOURCE_SLICE_STATE = "slice_state"      # 三态横片里该按钮态的真切片
SOURCE_IMAGE = "image"                  # 单图或 .spr 帧
SOURCE_DLG_COLOR = "dlg_color"          # CTextButton 的 lNormalColor 底色
SOURCE_STYLE_SKIN = "style_skin"        # ui.lst 里 iStyle 指定的按钮皮肤
SOURCE_BUTTON_STYLE = "button_style"    # 按控件类型画的按钮底色（无 iStyle）
SOURCE_EDITOR_DEFAULT = "editor_default"  # 编辑器默认配色（进度条等）
SOURCE_PLACEHOLDER = "placeholder"      # 只有占位框
SOURCE_NONE = "none"                    # 这类控件本来就不画图

#: 会去查图片的控件类型（其余类型按样式/文字画，不涉及缺图）
IMAGE_TYPES = frozenset({
    "CFrame", "CHFrame", "CVFrame", "CBorder", "CBox",
    "CBitmapFrame", "CBitmapHFrame", "CBitmapVFrame", "CSpriteFrame",
    "CHPngFrame", "CVPngFrame", "CPngNineFrame",
    "CImagesFrame", "CPngList", "CCombCheckButton",
    "CButton", "CHPageButton", "CVPageButton",
    "CHPagePngButton", "CVPagePngButton", "CTextButton",
    "CProgress",
})

#: 图片取不到时按 ui.lst 的 iStyle 画按钮底色的类型
STYLE_BUTTON_TYPES = frozenset({
    "CTextButton", "CButton", "CHPageButton", "CVPageButton",
    "CHPagePngButton", "CVPagePngButton",
})


def style_button_color(w: Widget, ctx: PaintContext) -> QColor | None:
    """`iStyle` 在 ui.lst 里查到的按钮常态色；查不到返回 None（不猜）。"""
    style = ctx.styles.tbstyle(_int(w, "iStyle"))
    if not style:
        return None
    return _color_from_style(style.get("ButtonNormalColor", ""), None)


def _code_skin_pixmap(w: Widget, ctx: PaintContext):
    binding = ctx.code_skins.get(w.name)
    if binding is None:
        return None
    return ctx.pixmap(binding.skin, 0)


def resolve_source(w: Widget, ctx: PaintContext) -> str:
    """这件控件**实际**会用哪条路画（与 :func:`paint_widget` 同源判定）。

    顺序与各 painter 内一致：代码皮肤 → 切片 → 图/精灵帧 → iStyle 样式
    按钮 → 占位框。角标、状态栏、诊断都读这一个结果，避免「画的是皮肤、
    标的是占位」这种自相矛盾。
    """
    if w.wtype not in IMAGE_TYPES:
        return SOURCE_NONE
    if _code_skin_pixmap(w, ctx) is not None:
        return SOURCE_CODE_SKIN
    name = str(w.props.get(_image_key(w), "") or "")
    if name:
        state = _BUTTON_STATE_INDEX.get(ctx.button_state, 0)
        if (state and w.wtype in STYLE_BUTTON_TYPES
                and ctx.assets.fetch_slice_state(name, state) is not None):
            return SOURCE_SLICE_STATE
        if ctx.assets.fetch_slice(name) is not None:
            return SOURCE_SLICE
        if ctx.pixmap(name) is not None:
            return SOURCE_IMAGE
    if w.wtype in STYLE_BUTTON_TYPES:
        # _paint_text_button 先看 lNormalColor，再看 iStyle 的常态色。
        if (w.wtype == "CTextButton"
                and w.props.get("lNormalColor")
                and _color_from_value(w.props.get("lNormalColor"), None)
                is not None):
            return SOURCE_DLG_COLOR
        if style_button_color(w, ctx) is not None:
            return SOURCE_STYLE_SKIN
        return SOURCE_BUTTON_STYLE   # 有兜底底色，不会是占位框
    if w.wtype == "CProgress":
        # 底图取不到时画的是深色底 + 绿色填充条，不是占位框
        return SOURCE_EDITOR_DEFAULT
    return SOURCE_PLACEHOLDER


def _paint_code_skin(p: QPainter, w: Widget, ctx: PaintContext) -> bool:
    """脚本在占位控件原地现造按钮时，按代码皮肤画（静态索引推断）。

    布局里这类控件只是锚点：游戏里真按钮由脚本用皮肤图现造。索引
    给了绑定且皮肤图取得到才接管绘制，取不到图时回落原画法。
    """
    binding = ctx.code_skins.get(w.name)
    pixmap = _code_skin_pixmap(w, ctx)
    if binding is None or pixmap is None:
        return False
    rect = _rect(w, ctx)
    p.drawPixmap(rect, pixmap, QRectF(pixmap.rect()))
    _simulate_state_overlay(p, rect, ctx)
    if binding.text:
        _draw_text(p, rect, binding.text, _font(w, ctx, 13),
                   QColor(245, 247, 252), 1)
    return True


def _paint_button(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    rect = _rect(w, ctx)
    if _paint_code_skin(p, w, ctx):
        return
    name = str(w.props.get("sFileName", "") or "")
    state = _BUTTON_STATE_INDEX.get(ctx.button_state, 0)
    if name:
        if state and _draw_slice(p, w, ctx, name, state):
            return  # 该态有真切片：横三片按资源尺寸拼，不是模拟
        if _draw_slice(p, w, ctx, name):
            # 目录型按钮没有该态切片时，至少让「按下/悬停/禁用」有可见反馈，
            # 与普通整图按钮的模拟口径一致；角标据此报「模拟」。
            _simulate_state_overlay(p, rect, ctx)
            return
    pixmap = ctx.pixmap(name) if name else None
    if pixmap is not None:
        stated = _button_state_pixmap(ctx, name, w) if name else None
        if stated is not None:
            p.drawPixmap(rect, stated[0], stated[1])
        else:
            p.drawPixmap(rect, pixmap, QRectF(pixmap.rect()))
            _simulate_state_overlay(p, rect, ctx)
        return
    # 图取不到时用 ui.lst 的 iStyle 底色（有就按样式画，没有才用编辑器默认色）
    base = style_button_color(w, ctx) or QColor(108, 124, 152)
    gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
    gradient.setColorAt(0, base.lighter(115))
    gradient.setColorAt(1, base)
    p.setBrush(gradient)
    p.setPen(QPen(base.lighter(150), 1))
    p.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), 3, 3)
    if ctx.show_names:
        _draw_text(p, rect, w.name, _small_font(), QColor(230, 236, 248), 1)


def _paint_text_button(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    rect = _rect(w, ctx)
    if _paint_code_skin(p, w, ctx):
        return
    name = str(w.props.get("sFileName", "") or "")
    state = _BUTTON_STATE_INDEX.get(ctx.button_state, 0)
    if name:   # 目录型基路径同样按切片拼；有真态切片就画真态
        if state and _draw_slice(p, w, ctx, name, state):
            _paint_text_overlay(p, w, ctx, rect)
            return
        if _draw_slice(p, w, ctx, name):
            _simulate_state_overlay(p, rect, ctx)
            _paint_text_overlay(p, w, ctx, rect)
            return
    pixmap = ctx.pixmap(name) if name else None
    if pixmap is not None:
        stated = _button_state_pixmap(ctx, name, w) if name else None
        if stated is not None:
            p.drawPixmap(rect, stated[0], stated[1])
        else:
            p.drawPixmap(rect, pixmap, QRectF(pixmap.rect()))
            _simulate_state_overlay(p, rect, ctx)
    else:
        style = ctx.styles.tbstyle(_int(w, "iStyle"))
        color = _color_from_value(w.props.get("lNormalColor"), None) \
            if w.props.get("lNormalColor") else None
        if color is None:
            color = _color_from_style(style.get("ButtonNormalColor", ""),
                                      QColor(96, 112, 140))
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0, color.lighter(115))
        gradient.setColorAt(1, color)
        p.setBrush(gradient)
        p.setPen(QPen(color.darker(140), 1))
        p.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), 3, 3)
    _paint_text_overlay(p, w, ctx, rect)


def _paint_text_overlay(p: QPainter, w: Widget, ctx: PaintContext,
                        rect: QRectF) -> None:
    """文字按钮的文字（含 tTextOffset 偏移）。"""
    offset = w.props.get("tTextOffset")
    dx = dy = 0.0
    if isinstance(offset, (list, tuple)) and len(offset) >= 2:
        dx, dy = float(offset[0]), float(offset[1])
    text_rect = rect.translated(dx, dy)
    _draw_text(p, text_rect, _plain_text(w), _font(w, ctx),
               QColor(245, 247, 252), 1)


def _paint_text(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    rect = _rect(w, ctx)
    color = _color_from_value(w.props.get("lColor"), QColor(225, 232, 244))
    _draw_text(p, rect, _plain_text(w), _font(w, ctx), color,
               _int(w, "iAlign"), rich=w.wtype == "CRichTextFrame")


def _paint_hotbox(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    rect = _rect(w, ctx)
    if ctx.show_names:
        _placeholder(p, rect, _name_label(w), ctx, QColor(160, 160, 255))


def _paint_table(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    rect = _rect(w, ctx)
    p.setBrush(QColor(24, 29, 40, 210))
    p.setPen(QPen(QColor(120, 135, 165), 1))
    p.drawRect(rect.adjusted(0.5, 0.5, -0.5, -0.5))
    widths = [v for v in (w.props.get("lSubWidth") or [])
              if isinstance(v, int) and v > 0]
    cols = len(widths) if widths else 3
    if not widths:
        widths = [int(rect.width() // cols)] * cols
    titles = str(w.props.get("sTitles", "")).split("\n")
    header_h = min(22.0, rect.height())
    p.setBrush(QColor(58, 70, 94))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(QRectF(1, 1, rect.width() - 2, header_h - 1))
    font = _font(w, ctx, 12)
    x = 0.0
    p.setPen(QPen(QColor(110, 124, 152), 1))
    for col in range(cols):
        col_w = widths[col] if col < len(widths) else widths[-1]
        if col > 0:
            p.drawLine(int(x), 0, int(x), int(rect.height()))
        if col < len(titles) and titles[col]:
            _draw_text(p, QRectF(x, 0, col_w, header_h), titles[col],
                       font, QColor(232, 238, 250), 1)
        x += col_w
    rows = max(1, _int(w, "iRow", 6))
    body_h = rect.height() - header_h
    row_h = body_h / rows if rows else body_h
    p.setPen(QPen(QColor(255, 255, 255, 26), 1))
    for row in range(1, rows + 1):
        y = header_h + row * row_h
        if y < rect.height():
            p.drawLine(1, int(y), int(rect.width()) - 1, int(y))


def _paint_list(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    rect = _rect(w, ctx)
    p.setBrush(QColor(24, 29, 40, 200))
    p.setPen(QPen(QColor(120, 135, 165), 1))
    p.drawRect(rect.adjusted(0.5, 0.5, -0.5, -0.5))
    p.setPen(QPen(QColor(255, 255, 255, 22), 1))
    y = 20.0
    while y < rect.height():
        p.drawLine(2, int(y), int(rect.width()) - 2, int(y))
        y += 20.0
    if ctx.show_names:
        p.setPen(QColor(170, 182, 205, 150))
        p.setFont(_small_font())
        p.drawText(rect.adjusted(4, 2, -2, -2),
                   Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                   w.name)


def _paint_edit(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    rect = _rect(w, ctx)
    p.setBrush(QColor(238, 240, 244))
    p.setPen(QPen(QColor(110, 120, 140), 1))
    p.drawRect(rect.adjusted(0.5, 0.5, -0.5, -0.5))
    _draw_text(p, rect, _plain_text(w) or w.name, _font(w, ctx),
               QColor(90, 96, 110), 0)


def _paint_progress(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    rect = _rect(w, ctx)
    bg_name = str(w.props.get("sBgFileName", "") or "")
    bg = ctx.pixmap(bg_name) if bg_name else None
    if bg is not None:
        p.drawPixmap(rect, bg, QRectF(bg.rect()))
    else:
        p.setBrush(QColor(30, 36, 48))
        p.setPen(QPen(QColor(110, 124, 152), 1))
        p.drawRect(rect.adjusted(0.5, 0.5, -0.5, -0.5))
    fill = QRectF(rect.x() + 1, rect.y() + 1,
                  max(0.0, (rect.width() - 2) * 0.65), rect.height() - 2)
    bar_name = str(w.props.get("sBarFileName", "") or "")
    bar = ctx.pixmap(bar_name) if bar_name else None
    if bar is not None:
        p.drawPixmap(fill, bar, QRectF(bar.rect()))
    else:
        p.setBrush(QColor(110, 190, 120))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRect(fill)


def _paint_scrollbar(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    rect = _rect(w, ctx)
    p.setBrush(QColor(30, 36, 48, 200))
    p.setPen(QPen(QColor(110, 124, 152), 1))
    p.drawRect(rect.adjusted(0.5, 0.5, -0.5, -0.5))
    thumb_h = max(14.0, rect.height() / 3.0)
    p.setBrush(QColor(120, 138, 170))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(QRectF(rect.x() + 2, rect.y() + 2,
                      rect.width() - 4, thumb_h))


def _paint_fallback(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    rect = _rect(w, ctx)
    _placeholder(p, rect, _name_label(w), ctx, QColor(255, 130, 160))


_PAINTERS = {
    "CMainFrame": _paint_main_frame,
    "CAutoDlgBase": _paint_main_frame,
    "CFrame": _paint_frame,
    "CHFrame": _paint_frame,
    "CVFrame": _paint_frame,
    "CBorder": _paint_frame,
    "CBox": _paint_frame,
    "CBitmapFrame": _paint_image,
    "CBitmapHFrame": _paint_image,
    "CBitmapVFrame": _paint_image,
    "CSpriteFrame": _paint_image,
    "CHPngFrame": _paint_image,
    "CVPngFrame": _paint_image,
    "CPngNineFrame": _paint_nine,
    "CImagesFrame": _paint_grid,
    "CPngList": _paint_grid,
    "CCombCheckButton": _paint_grid,
    "CButton": _paint_button,
    "CHPageButton": _paint_button,
    "CVPageButton": _paint_button,
    "CHPagePngButton": _paint_button,
    "CVPagePngButton": _paint_button,
    "CTextButton": _paint_text_button,
    "CTextFrame": _paint_text,
    "CTextFrameEx": _paint_text,
    "CRichTextFrame": _paint_text,
    "CBoxWithTips": _paint_text,
    "CHotBox": _paint_hotbox,
    "CTable": _paint_table,
    "CTableView": _paint_table,
    "CTitleTableView": _paint_table,
    "CPngTable": _paint_table,
    "CList": _paint_list,
    "CEdit": _paint_edit,
    "CProgress": _paint_progress,
    "CVScrollBar": _paint_scrollbar,
    "CVPngScrollBar": _paint_scrollbar,
}


def paint_widget(p: QPainter, w: Widget, ctx: PaintContext) -> None:
    """把一个控件画在本地 (0,0) 处（子控件由场景的父子图元处理）。

    运行时隐藏（``bShow=0``）或 ``bLoad=0`` 的控件**照常画**（布局里确实
    有它），但压暗 + 虚线框 + 角标说明——与「资源加载失败」的红色占位框
    在视觉上完全不同，避免把两种问题混为一谈。
    """
    state = _runtime_hidden(w)
    if not state:
        _PAINTERS.get(w.wtype, _paint_fallback)(p, w, ctx)
        return
    p.save()
    p.setOpacity(0.45)
    _PAINTERS.get(w.wtype, _paint_fallback)(p, w, ctx)
    p.restore()
    _paint_runtime_note(p, w, ctx, state)
