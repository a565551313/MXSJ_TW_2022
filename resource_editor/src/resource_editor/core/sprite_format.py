# 自动生成，请勿手改：由 tools/devkit/vendor_core.py 从
# mx_common/sprite_format.py 复制（字节相同）。
# 改共享逻辑：改 mx_common/sprite_format.py → --write；校验：--check
# 详细说明见 mx_common/README.md。
"""精灵格式（``I0``/``T0``/``I1``/``T1``/``T4``/``T5``）的共享常量与换算。

**唯一真源**：编辑器与工具里的解码/编码实现（`ui_editor/core/sprite.py`、
`ui_editor/core/sprite_encode.py`、`resource_editor/core/codecs/sprite.py`）
各自保留自己的落点（一个输出 RGBA 字节喂 `QImage`、一个输出 Pillow 图），
但**格式常量与 alpha 折算只能有一份**——它们曾经是各写一遍的私有副本
（见 `docs/analysis/ui_editor_analysis_20261016.md` P1-2）。

格式规格：`tools/data-parser/I0_SPRITE_FORMAT.md`、`tools/data-parser/
i0_sprite.py`（Pillow 参考实现）。

布局：14 字节头 ``<2sHHHHHH``（魔数、版本、帧数、画布宽高、中心点）；
帧目录每帧 ``<HHHH``（关键点 x/y、帧宽高）；u32 总行数；行长表
（I0/T0/T4 用 u8，I1/T1/T5 用 u16）；调色板（T0/T1 为 256×RGB888，
I0/I1 为 256×RGB565；T4/T5 无调色板，token 后跟 3 字节 RGB）。

``T1`` = ``T0`` 的 u16 行长变体（与 I0→I1、T4→T5 同构）；2026-10-19 在
interface.fls 的 .spr 姊媚精灵（烟2_.igs 等 21 例）上按「Σ行长=像素流长」定版。

行内算子按高位分段：``0x00`` 行尾；``0x01–0x1F`` RUN（计数 5 位，
后跟 alpha 等级与索引）；``0x20–0x3F`` SINGLE（alpha 等级在 token
里）；``0x40–0x7F`` LIT（不透明字面序列，计数 6 位）；``0x80–0xBF``
REP（不透明单色重复，计数 6 位）；``0xC0–0xFF`` SKIP（透明跳过，
计数 6 位）。透明等级 5 位，``alpha8 = level * 255 // 31``。
"""

from __future__ import annotations

__all__ = [
    "ALPHA_LEVELS",
    "DIRECT_MAGICS",
    "FRAME_DIR_ENTRY_SIZE",
    "FRAME_STRUCT",
    "HEADER_SIZE",
    "HEADER_STRUCT",
    "MAGICS",
    "MAX_LIT_COUNT",
    "MAX_RUN_COUNT",
    "MIN_SIZE",
    "OPAQUE",
    "PALETTE_COLORS",
    "PALETTE_MAGICS",
    "ROW_ALIGN",
    "ROW_LEN_U8_MAX",
    "alpha_to_level",
    "is_sprite",
    "level_to_alpha",
]

MAGICS: tuple[bytes, ...] = (b"I0", b"T0", b"I1", b"T1", b"T4", b"T5")
#: 真彩变体：无调色板，行内 token 之后是 3 字节 RGB 像素
DIRECT_MAGICS: tuple[bytes, ...] = (b"T4", b"T5")
#: 带调色板的变体（T0/T1 为 RGB888，I0/I1 为 RGB565）
PALETTE_MAGICS: tuple[bytes, ...] = (b"I0", b"T0", b"I1", b"T1")

HEADER_STRUCT = "<2sHHHHHH"
FRAME_STRUCT = "<HHHH"
HEADER_SIZE = 14
FRAME_DIR_ENTRY_SIZE = 8
#: 最短合法精灵 = 头 + 一帧目录 + 行长/调色板之类的最小尾巴（与既有实现一致）
MIN_SIZE = 26

PALETTE_COLORS = 256

#: 不透明标记：alpha 等级满值单独表示「不透明」，编码时用 LIT/REP
OPAQUE = 255
#: 半透明等级数：5 位
ALPHA_LEVELS = 31

#: RUN/SINGLE 的计数位宽（token 低 5 位，与 alpha 等级共用）
MAX_RUN_COUNT = 0x1F
#: LIT/REP/SKIP 的计数位宽（6 位）
MAX_LIT_COUNT = 0x3F

#: 每帧像素流按 4 字节对齐，填充计入末行行长
ROW_ALIGN = 4
#: I0/T0 行长表为 u8：单行编码后不得超过 255 字节（I1/T5 用 u16）
ROW_LEN_U8_MAX = 255


def is_sprite(data: bytes) -> bool:
    """按魔数与最小长度判断是否为精灵字节（不做完整解析）。"""
    return len(data) >= MIN_SIZE and data[:2] in MAGICS


def level_to_alpha(level: int) -> int:
    """5 位透明等级 → 8 位 alpha（``level * 255 // 31``）。"""
    return level * 255 // ALPHA_LEVELS


def alpha_to_level(alpha: int) -> int:
    """8 位 alpha 折回 0–31 级；``>= 255`` 视为不透明（返回 :data:`OPAQUE`）。

    与两个编辑器原先各写一遍的实现逐点等值（0/1/254/255 与
    ``whole31`` 折算均已用测试钉住）。
    """
    if alpha >= OPAQUE:
        return OPAQUE
    if alpha <= 0:
        return 0
    level = round(alpha * ALPHA_LEVELS / OPAQUE)
    return max(1, min(ALPHA_LEVELS - 1, level))
