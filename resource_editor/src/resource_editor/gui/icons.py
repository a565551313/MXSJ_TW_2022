"""工具栏图标：一组运行时现画的彩色小图标（28x28，无外部素材）。

用 QPainter 画简单形状，与系统主题无关，深浅色下都认得出。
每个函数返回 QIcon。风格与 UI 编辑器的 ui/icons.py 保持一致。
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

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


def icon_workspace() -> QIcon:
    """设定工作目录：黄色文件夹。"""
    pixmap, p = _begin()
    p.setPen(_pen("#7a4d12"))
    p.setBrush(QColor("#c47f28"))
    p.drawRoundedRect(QRectF(4, 10.5, 20, 12.5), 2, 2)
    p.setBrush(QColor("#f2b04a"))
    path = QPainterPath()
    path.moveTo(3.5, 12)
    path.lineTo(9, 12)
    path.lineTo(11.5, 15.5)
    path.lineTo(23.5, 15.5)
    path.lineTo(23.5, 23)
    path.lineTo(3.5, 23)
    path.closeSubpath()
    p.drawPath(path)
    return _end(pixmap, p)


def icon_open_pack() -> QIcon:
    """打开资源包：蓝色箱子。"""
    pixmap, p = _begin()
    p.setPen(_pen("#274b73"))
    p.setBrush(QColor("#7fb3e8"))
    p.drawRoundedRect(QRectF(5, 8, 18, 15), 2, 2)
    p.setBrush(QColor("#4a86c5"))
    p.drawRect(QRectF(5, 8, 18, 4.5))
    p.setPen(_pen("#274b73", 1.4))
    p.drawLine(QPointF(14, 8), QPointF(14, 12.5))
    return _end(pixmap, p)


def icon_refresh() -> QIcon:
    """刷新目录：绿色环形箭头。"""
    pixmap, p = _begin()
    p.setPen(_pen("#2e7d32", 2.2))
    p.drawArc(QRectF(6.5, 6.5, 15, 15), 40 * 16, 270 * 16)
    p.setBrush(QColor("#2e7d32"))
    path = QPainterPath()
    path.moveTo(21.5, 3.5)
    path.lineTo(22.8, 9.5)
    path.lineTo(17.2, 8.2)
    path.closeSubpath()
    p.drawPath(path)
    return _end(pixmap, p)


def icon_save() -> QIcon:
    """保存：蓝色软盘。"""
    pixmap, p = _begin()
    p.setPen(_pen("#274b73"))
    p.setBrush(QColor("#4a86c5"))
    p.drawRoundedRect(QRectF(5, 5, 18, 18), 2, 2)
    p.setBrush(QColor("#dceefc"))
    p.drawRect(QRectF(8.5, 5.8, 11, 7))
    p.setBrush(QColor("#f5f9ff"))
    p.drawRect(QRectF(8.5, 15.5, 11, 7.5))
    p.setPen(_pen("#7fb3e8", 1.2))
    p.drawLine(QPointF(10.5, 18.5), QPointF(17.5, 18.5))
    return _end(pixmap, p)


def icon_save_as() -> QIcon:
    """另存为：软盘 + 铅笔。"""
    pixmap, p = _begin()
    p.setPen(_pen("#274b73"))
    p.setBrush(QColor("#4a86c5"))
    p.drawRoundedRect(QRectF(4, 6, 16, 16), 2, 2)
    p.setBrush(QColor("#dceefc"))
    p.drawRect(QRectF(7, 6.8, 9.5, 6))
    p.setBrush(QColor("#f5f9ff"))
    p.drawRect(QRectF(7, 15, 9.5, 6.5))
    p.setPen(_pen("#b3540e", 2.0))
    p.drawLine(QPointF(17, 21), QPointF(22.5, 12.5))
    p.setPen(_pen("#e08a2e", 1.2))
    p.drawLine(QPointF(22.5, 12.5), QPointF(23.8, 16.5))
    p.drawLine(QPointF(23.8, 16.5), QPointF(20.2, 15.8))
    return _end(pixmap, p)


def icon_export() -> QIcon:
    """导出：图片 + 向外箭头。"""
    pixmap, p = _begin()
    p.setPen(_pen("#5d4037"))
    p.setBrush(QColor("#aed6a5"))
    p.drawRoundedRect(QRectF(4, 7, 15, 14), 2, 2)
    p.setBrush(QColor("#5b8c4e"))
    path = QPainterPath()
    path.moveTo(5.5, 19.5)
    path.lineTo(10.5, 13.5)
    path.lineTo(13.5, 17)
    path.lineTo(15.5, 15)
    path.lineTo(18.5, 19.5)
    path.closeSubpath()
    p.drawPath(path)
    p.setPen(_pen("#b3540e", 2.1))
    p.drawLine(QPointF(15, 6), QPointF(23.5, 6))
    p.drawLine(QPointF(23.5, 6), QPointF(23.5, 14.5))
    p.drawLine(QPointF(23.5, 6), QPointF(18, 11.5))
    return _end(pixmap, p)


def icon_import_path() -> QIcon:
    """按路径导入：标签 + 向内箭头。"""
    pixmap, p = _begin()
    p.setPen(_pen("#4a2d73"))
    p.setBrush(QColor("#b39ddb"))
    path = QPainterPath()
    path.moveTo(6, 5)
    path.lineTo(15, 5)
    path.lineTo(22, 12)
    path.lineTo(13, 21)
    path.lineTo(6, 14)
    path.closeSubpath()
    p.drawPath(path)
    p.setBrush(QColor("#ede7f6"))
    p.drawEllipse(QPointF(10.5, 9.5), 1.8, 1.8)
    p.setPen(_pen("#33691e", 2.1))
    p.drawLine(QPointF(23.5, 16), QPointF(15, 16))
    p.drawLine(QPointF(15, 16), QPointF(19, 12))
    p.drawLine(QPointF(15, 16), QPointF(19, 20))
    return _end(pixmap, p)


def icon_import_sprite() -> QIcon:
    """帧图转精灵导入：胶片格。"""
    pixmap, p = _begin()
    p.setPen(_pen("#373737"))
    p.setBrush(QColor("#5a5a5a"))
    p.drawRoundedRect(QRectF(5, 5, 18, 18), 2, 2)
    p.setBrush(QColor("#cfd8dc"))
    for y in (8.5, 15.5):
        p.drawRect(QRectF(8, y, 12, 5))
    p.setBrush(QColor("#eceff1"))
    for i in range(3):
        p.drawEllipse(QPointF(6.8, 8.5 + i * 5.5), 0.8, 0.8)
        p.drawEllipse(QPointF(21.2, 8.5 + i * 5.5), 0.8, 0.8)
    return _end(pixmap, p)


def icon_delete() -> QIcon:
    """删除条目：红色垃圾桶。"""
    pixmap, p = _begin()
    p.setPen(_pen("#7b1f1f", 1.8))
    p.drawLine(QPointF(5, 9), QPointF(23, 9))
    p.drawLine(QPointF(11, 9), QPointF(11.8, 5.5))
    p.drawLine(QPointF(11.8, 5.5), QPointF(16.2, 5.5))
    p.drawLine(QPointF(16.2, 5.5), QPointF(17, 9))
    p.setBrush(QColor("#d66"))
    p.setPen(_pen("#7b1f1f", 1.4))
    path = QPainterPath()
    path.moveTo(7.5, 10.5)
    path.lineTo(20.5, 10.5)
    path.lineTo(19.3, 22.5)
    path.lineTo(8.7, 22.5)
    path.closeSubpath()
    p.drawPath(path)
    p.setPen(_pen("#7b1f1f", 1.3))
    p.drawLine(QPointF(11.5, 13), QPointF(12, 20))
    p.drawLine(QPointF(16.5, 13), QPointF(16, 20))
    return _end(pixmap, p)
