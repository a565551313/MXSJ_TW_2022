"""Qt 与 Pillow 之间的图像转换小工具。"""
from __future__ import annotations

from PIL import Image
from PySide6.QtGui import QImage


def pil_to_qimage(image: Image.Image) -> QImage:
    """PIL RGBA 图转 QImage（拷贝数据，可安全跨线程传递）。"""
    rgba = image.convert("RGBA")
    data = rgba.tobytes("raw", "RGBA")
    qimg = QImage(data, rgba.width, rgba.height, QImage.Format_RGBA8888)
    return qimg.copy()
