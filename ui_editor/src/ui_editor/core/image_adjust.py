"""图片批处理的调整核心：缩放、亮度、饱和度（Pillow，零 Qt，0.20.0）。

0.19.0 的实测结论：CButton 等控件在游戏内的尺寸由图片素材自身决定
——想改游戏内观感就得改图。本模块给浏览窗「批量处理…」提供逐张调整
的实现（用户拍板最小三样：缩放 / 亮度 / 饱和度），规则全部可单测：

* 缩放：按百分比或到目标尺寸（可锁纵横比；LANCZOS 重采样；最短 1px）；
* 亮度 / 饱和度：Pillow ``ImageEnhance.Brightness`` / ``Color``。
  **必须拆 alpha**：ImageEnhance 的退化图 alpha=255，直接混合 RGBA 会
  把透明像素的 alpha 拉向 255（游戏精灵全靠透明像素定位，拉坏即位移
  观感全毁），所以只对 RGB 通道增强、alpha 原样合回——有回归测试钉死；
* 普通图片：PNG/JPEG/BMP/TGA 按**原格式**重编码；JPEG 无 alpha、
  重编码固定 quality=90（JPEG 有损，重存必有一损，取高质量端如实告知）；
  GIF（多帧）与其余格式拒收，一句话原因进结果清单；
* ``.igs`` 精灵容器：``decode_sprite`` 逐帧解 RGBA → 逐帧调整 →
  ``encode_frames`` 重编码成**新** .igs（原容器字节不动）。两道保真
  护栏：①任一帧锚点非 (0,0) 拒收——``encode_frames`` 只写 (0,0)，
  硬转等于悄悄挪帧；②魔数不在 I0/T0/I1 拒收——真彩 T4/T5/I4 能解
  不能编。重编码会按调整后像素重建 256 色调色板，颜色有轻微再量化
  属预期（用户本来就在改像素），透明等级不受影响。
"""

from __future__ import annotations

import io
from dataclasses import dataclass

from PIL import Image, ImageEnhance

from . import sprite, sprite_encode

__all__ = ["AdjustError", "AdjustParams", "PLAIN_FORMATS", "adjust_image",
           "adjusted_size", "normalize_mode", "process_plain",
           "process_sprite"]


class AdjustError(ValueError):
    """批处理拒收/失败的一句话原因（进结果清单给用户看）。"""


@dataclass(frozen=True)
class AdjustParams:
    """一次批处理的全部参数（不可变，可整体进测试断言）。"""

    scale_mode: str = "none"      # none | percent | target
    percent: int = 100            # 5..500
    target_w: int = 0             # <=0 = 该维不受限（锁纵横比时按另一边推）
    target_h: int = 0
    keep_aspect: bool = True
    brightness: float = 1.0       # 0..2，1=不变
    saturation: float = 1.0       # 0..2，1=不变（0=灰度化）

    def is_identity(self) -> bool:
        return (self.scale_mode == "none"
                and self.brightness == 1.0 and self.saturation == 1.0)


#: 能按原格式重编码的普通图片：Pillow 格式名 → 常规扩展名。
#: GIF 多帧动画不在最小集（游戏素材里也没有），其余格式一律拒收。
PLAIN_FORMATS = {"PNG": ".png", "JPEG": ".jpg", "BMP": ".bmp", "TGA": ".tga"}


def adjusted_size(width: int, height: int,
                  params: AdjustParams) -> tuple[int, int]:
    """按参数算输出尺寸（纯函数，不碰图像；最短边 1px）。"""
    if width <= 0 or height <= 0:
        raise AdjustError(f"非法图像尺寸 {width}x{height}")
    if params.scale_mode == "percent":
        pct = max(1, int(params.percent))
        return (max(1, round(width * pct / 100)),
                max(1, round(height * pct / 100)))
    if params.scale_mode == "target":
        tw, th = int(params.target_w), int(params.target_h)
        if tw <= 0 and th <= 0:
            return width, height          # 两维都不受限 = 不缩放
        if not params.keep_aspect:
            return (max(1, tw) if tw > 0 else width,
                    max(1, th) if th > 0 else height)
        if tw <= 0:                       # 只给高：按比例推宽
            return max(1, round(width * th / height)), max(1, th)
        if th <= 0:                       # 只给宽：按比例推高
            return max(1, tw), max(1, round(height * tw / width))
        scale = min(tw / width, th / height)   # 装进目标框（fit）
        return max(1, round(width * scale)), max(1, round(height * scale))
    return width, height


def normalize_mode(img: Image.Image) -> Image.Image:
    """统一成 RGBA（带透明信息）或 RGB，后续步骤只面对这两种模式。"""
    if img.mode in ("RGBA", "LA", "PA"):
        return img if img.mode == "RGBA" else img.convert("RGBA")
    if img.mode == "P" and "transparency" in img.info:
        return img.convert("RGBA")
    if img.mode == "RGB":
        return img
    return img.convert("RGB")


def _enhance(img: Image.Image, params: AdjustParams) -> Image.Image:
    """亮度→饱和度；RGBA 拆出 alpha 只增强 RGB（模块 docstring 的坑）。"""
    brightness = float(params.brightness)
    saturation = float(params.saturation)
    if brightness == 1.0 and saturation == 1.0:
        return img                        # 恒等参数零扰动
    alpha = None
    if img.mode == "RGBA":
        red, green, blue, alpha = img.split()
        rgb = Image.merge("RGB", (red, green, blue))
    else:
        rgb = img
    if brightness != 1.0:
        rgb = ImageEnhance.Brightness(rgb).enhance(brightness)
    if saturation != 1.0:
        rgb = ImageEnhance.Color(rgb).enhance(saturation)
    if alpha is not None:
        rgb = rgb.convert("RGBA")
        rgb.putalpha(alpha)               # alpha 原样合回，一个等级不动
    return rgb


def adjust_image(img: Image.Image, params: AdjustParams) -> Image.Image:
    """单帧调整：模式归一 → 缩放（LANCZOS）→ 亮度 → 饱和度。"""
    img = normalize_mode(img)
    size = adjusted_size(img.width, img.height, params)
    if size != (img.width, img.height):
        img = img.resize(size, Image.Resampling.LANCZOS)
    return _enhance(img, params)


def process_plain(data: bytes, params: AdjustParams) -> bytes:
    """普通图片字节 → 调整后字节（按原格式重编码，PNG/JPEG/BMP/TGA）。"""
    try:
        with Image.open(io.BytesIO(data)) as img:
            fmt = (img.format or "").upper()
            if fmt not in PLAIN_FORMATS:
                raise AdjustError(
                    f"格式 {fmt or '未知'} 不在批处理范围"
                    "（PNG/JPEG/BMP/TGA）")
            # PIL 惰性加载：恒等参数时 adjust_image 原样返回懒图对象，
            # with 块一关源流，save 再读像素就炸（空消息异常）——
            # 先把像素落进内存。
            img.load()
            out = adjust_image(img, params)
    except AdjustError:
        raise
    except Exception as exc:   # PIL 打不开/解不动的花样很多，统一一句话
        raise AdjustError(f"无法识别的图片：{exc}") from exc
    save_kwargs: dict = {"format": fmt}
    if fmt == "JPEG":
        out = out.convert("RGB")          # JPEG 没有 alpha
        save_kwargs["quality"] = 90
    buf = io.BytesIO()
    out.save(buf, **save_kwargs)
    return buf.getvalue()


def process_sprite(data: bytes, params: AdjustParams) -> bytes:
    """.igs 字节 → 逐帧调整重编码的**新** .igs 字节（I0/T0/I1）。

    保真护栏（模块 docstring）：帧锚点非 (0,0)、魔数不可重编码、空帧
    都拒收；行长超上限等编码失败也转成一句话 ``AdjustError``。
    """
    try:
        # 先用同一解析器检查帧关键点：重编码只支持左上锚点，提前拒收；
        # 格式知识只在 sprite.py 一处维护，这里不手抄头部布局。
        parser = sprite._SpriteParser(data)
    except AdjustError:
        raise
    except Exception as exc:
        raise AdjustError(f"不是可解码的精灵：{exc}") from exc
    if any((kx, ky) != (0, 0) for kx, ky, _fw, _fh in parser.frame_dims):
        raise AdjustError(
            "帧锚点不是 (0,0)：重编码会丢帧定位，拒收（忠实优先）")
    try:
        spr = sprite.decode_sprite(data)
    except Exception as exc:
        raise AdjustError(f"精灵解码失败：{exc}") from exc
    if spr.magic not in ("I0", "T0", "I1"):
        raise AdjustError(
            f"魔数 {spr.magic} 能解码但编辑器只能编码 I0/T0/I1，拒收")
    frames = []
    for frame in spr.frames:
        if frame.width <= 0 or frame.height <= 0:
            raise AdjustError(
                f"含空帧（{frame.width}x{frame.height}），拒收")
        frames.append(Image.frombytes(
            "RGBA", (frame.width, frame.height), frame.rgba))
    adjusted = [adjust_image(frame, params) for frame in frames]
    try:
        return sprite_encode.encode_frames(adjusted, spr.magic)
    except Exception as exc:
        raise AdjustError(f"重编码失败：{exc}") from exc
