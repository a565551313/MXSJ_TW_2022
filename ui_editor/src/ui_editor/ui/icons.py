"""工具栏图标：一组运行时现画的彩色小图标（28x28，无外部素材）。

用 QPainter 画简单形状：文件夹、箱子、软盘、图片、弯箭头等，
与系统主题无关，在深色/浅色下都认得出。每个函数返回 QIcon。
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)

_SIZE = 28


def _begin() -> tuple[QPixmap, QPainter]:
    pixmap = QPixmap(_SIZE, _SIZE)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    return pixmap, painter


def _end(pixmap: QPixmap, painter: QPainter) -> QIcon:
    painter.end()
    return QIcon(pixmap)


def _pen(color: str, width: float = 1.6) -> QPen:
    pen = QPen(QColor(color), width)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    return pen


def icon_open_file() -> QIcon:
    """打开布局文件：黄色文件夹。"""
    pixmap, p = _begin()
    p.setPen(_pen("#7a4d12"))
    p.setBrush(QColor("#c47f28"))
    p.drawRoundedRect(QRectF(4, 10.5, 20, 12.5), 2, 2)  # 后片
    p.setBrush(QColor("#f2b04a"))
    path = QPainterPath()
    path.moveTo(3.5, 12)
    path.lineTo(9, 12)
    path.lineTo(11.5, 15.5)
    path.lineTo(23.5, 15.5)
    path.lineTo(23.5, 23)
    path.lineTo(3.5, 23)
    path.closeSubpath()
    p.drawPath(path)  # 前片带斜口
    return _end(pixmap, p)


def icon_open_pack() -> QIcon:
    """从资源包打开：棕色纸箱。"""
    pixmap, p = _begin()
    p.setPen(_pen("#5e3c14"))
    p.setBrush(QColor("#b07a35"))
    p.drawRect(QRectF(5, 11, 18, 12))  # 箱身
    p.setBrush(QColor("#d29a4b"))
    p.drawRect(QRectF(3.5, 6.5, 21, 5))  # 箱盖
    p.setPen(_pen("#5e3c14", 1.4))
    p.drawLine(QPointF(14, 11), QPointF(14, 23))  # 封箱带
    return _end(pixmap, p)


def icon_save() -> QIcon:
    """保存：蓝色软盘。"""
    pixmap, p = _begin()
    p.setPen(_pen("#274b7a"))
    p.setBrush(QColor("#3f74c9"))
    p.drawRoundedRect(QRectF(5, 4.5, 18, 19), 2.5, 2.5)
    p.setBrush(QColor("#dfe9f7"))
    p.drawRect(QRectF(8.5, 4.8, 11, 6.5))  # 磁盘口
    p.setBrush(QColor("#f5f8fd"))
    p.drawRect(QRectF(8, 14.5, 12, 6.5))  # 标签
    p.setPen(_pen("#274b7a", 1.2))
    p.drawLine(QPointF(16.5, 5.2), QPointF(16.5, 10.8))
    return _end(pixmap, p)


def icon_save_pack() -> QIcon:
    """保存回资源包：箱子 + 绿色向上箭头。"""
    pixmap, p = _begin()
    p.setPen(_pen("#5e3c14"))
    p.setBrush(QColor("#d29a4b"))
    p.drawRect(QRectF(3.5, 8, 21, 4.5))
    p.setBrush(QColor("#b07a35"))
    p.drawRect(QRectF(5, 12.5, 18, 10.5))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#1a9e4b"))
    arrow = QPainterPath()
    arrow.moveTo(19.5, 25.5)
    arrow.lineTo(19.5, 17.5)
    arrow.lineTo(16.8, 17.5)
    arrow.lineTo(21.2, 12.5)
    arrow.lineTo(25.6, 17.5)
    arrow.lineTo(22.9, 17.5)
    arrow.lineTo(22.9, 25.5)
    arrow.closeSubpath()
    p.drawPath(arrow)
    return _end(pixmap, p)


def icon_export_image() -> QIcon:
    """导出 PNG：山水图片 + 指出去的箭头。"""
    pixmap, p = _begin()
    p.setPen(_pen("#3c5a78"))
    p.setBrush(QColor("#e8f1fa"))
    p.drawRoundedRect(QRectF(3.5, 6, 17, 14), 2, 2)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#f2b04a"))
    p.drawEllipse(QRectF(6.5, 8.5, 4.5, 4.5))  # 太阳
    p.setBrush(QColor("#57a773"))
    mountain = QPainterPath()
    mountain.moveTo(4.5, 19)
    mountain.lineTo(10, 12.5)
    mountain.lineTo(13.5, 16)
    mountain.lineTo(16, 13.5)
    mountain.lineTo(19.5, 19)
    mountain.closeSubpath()
    p.drawPath(mountain)
    p.setPen(_pen("#1a9e4b", 2.2))
    p.drawLine(QPointF(17, 24.5), QPointF(24, 17.5))
    p.drawLine(QPointF(19, 17.3), QPointF(24.2, 17.3))
    p.drawLine(QPointF(24.2, 17.3), QPointF(24.2, 22.5))
    return _end(pixmap, p)


def _curved_arrow(flip: bool) -> QIcon:
    pixmap, p = _begin()
    if flip:
        p.translate(_SIZE, 0)
        p.scale(-1, 1)
    p.setPen(_pen("#2f6fb4", 3.0))
    p.setBrush(Qt.BrushStyle.NoBrush)
    arc = QPainterPath()
    arc.arcMoveTo(QRectF(8, 7, 15, 13), 100)
    arc.arcTo(QRectF(8, 7, 15, 13), 100, -230)
    p.drawPath(arc)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#2f6fb4"))
    head = QPainterPath()
    head.moveTo(4.2, 15.5)
    head.lineTo(11.5, 12.8)
    head.lineTo(10.2, 20.5)
    head.closeSubpath()
    p.drawPath(head)
    return _end(pixmap, p)


def icon_undo() -> QIcon:
    """撤销：向左弯箭头。"""
    return _curved_arrow(False)


def icon_redo() -> QIcon:
    """重做：向右弯箭头。"""
    return _curved_arrow(True)


def icon_fit() -> QIcon:
    """适应窗口：四角取景框。"""
    pixmap, p = _begin()
    p.setPen(_pen("#555f6e", 2.0))
    length = 6.0
    for x, y, dx, dy in ((5, 5, 1, 1), (23, 5, -1, 1),
                         (5, 23, 1, -1), (23, 23, -1, -1)):
        p.drawLine(QPointF(x, y), QPointF(x + length * dx, y))
        p.drawLine(QPointF(x, y), QPointF(x, y + length * dy))
    return _end(pixmap, p)


def icon_actual_size() -> QIcon:
    """实际大小：虚线框里写 1:1。"""
    pixmap, p = _begin()
    pen = _pen("#555f6e", 1.6)
    pen.setStyle(Qt.PenStyle.DashLine)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRoundedRect(QRectF(4.5, 7, 19, 14), 2, 2)
    p.setPen(QColor("#333c48"))
    font = QFont()
    font.setPixelSize(10)
    font.setBold(True)
    p.setFont(font)
    p.drawText(QRectF(4.5, 7, 19, 14), Qt.AlignmentFlag.AlignCenter, "1:1")
    return _end(pixmap, p)


def icon_names() -> QIcon:
    """名字标注开关：名字牌。"""
    pixmap, p = _begin()
    p.setPen(_pen("#7a4d12"))
    p.setBrush(QColor("#ffd98a"))
    p.drawRoundedRect(QRectF(4, 8, 20, 12), 3, 3)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#7a4d12"))
    p.drawEllipse(QRectF(7.5, 12, 3.4, 3.4))  # 牌孔
    p.setPen(_pen("#7a4d12", 1.6))
    p.drawLine(QPointF(14, 12.5), QPointF(21.5, 12.5))
    p.drawLine(QPointF(14, 16), QPointF(19.5, 16))
    return _end(pixmap, p)
