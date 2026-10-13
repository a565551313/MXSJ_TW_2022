"""检查结果的数据模型：严重级别、规则表、Finding。"""

from __future__ import annotations

import enum
from dataclasses import dataclass


class Severity(enum.IntEnum):
    """严重级别。ERROR = 到 Windows 上必坏；WARNING = 很可能出问题；INFO = 提示。"""

    INFO = 0
    WARNING = 1
    ERROR = 2


# 规则代码 → (默认级别, 一句话说明)。WIN1xx 文件名，WIN2xx 批处理，WIN3xx Python 源码，
# CONVxxx 为项目约定（见 docs/PYTHON_TOOL_CONVENTIONS.md），不是 Windows 本身的限制。
RULES: dict[str, tuple[Severity, str]] = {
    "WIN101": (
        Severity.ERROR,
        '文件名含 Windows 非法字符（< > : " | ? * 或控制字符）',
    ),
    "WIN102": (
        Severity.ERROR,
        "文件名是 Windows 保留设备名（CON/PRN/AUX/NUL/COM1-9/LPT1-9）",
    ),
    "WIN103": (Severity.ERROR, "文件名以空格或句点结尾（Windows 会静默去掉）"),
    "WIN104": (
        Severity.ERROR,
        "同一目录下存在仅大小写不同的路径（Windows 不区分大小写）",
    ),
    "WIN105": (
        Severity.WARNING,
        "相对路径过长（>200 字符；Windows MAX_PATH=260 还要算上盘符与上级目录）",
    ),
    "WIN106": (
        Severity.ERROR,
        "符号链接（Windows 默认无权限创建，git 会把它降级成文本文件）",
    ),
    "WIN201": (
        Severity.WARNING,
        ".bat/.cmd 使用 LF 行尾（cmd 需要 CRLF，goto/标签会出错）",
    ),
    "WIN202": (
        Severity.WARNING,
        ".bat/.cmd 含非 ASCII 字符但之前没有 chcp 65001（中文会乱码）",
    ),
    "WIN203": (
        Severity.ERROR,
        ".bat/.cmd 带 UTF-8 BOM（cmd 会把首行当成未知命令）",
    ),
    "WIN301": (
        Severity.WARNING,
        "open() 文本模式未显式指定 encoding（Windows 默认 GBK）",
    ),
    "WIN302": (
        Severity.WARNING,
        "read_text()/write_text() 未显式指定 encoding（Windows 默认 GBK）",
    ),
    "WIN303": (Severity.ERROR, "导入仅 POSIX 可用的模块（Windows 上 ImportError）"),
    "WIN304": (
        Severity.ERROR,
        "调用仅 POSIX 可用的 os/signal API（Windows 上 AttributeError）",
    ),
    "WIN305": (Severity.WARNING, "硬编码 POSIX 绝对路径（/tmp、/home …）"),
    "WIN306": (
        Severity.WARNING,
        "以字面量 python/python3 启动子进程（Windows 常无 python3，用 sys.executable）",
    ),
    "WIN307": (Severity.INFO, "Python 文件无法解析或解码，已跳过"),
    "CONV001": (Severity.ERROR, "GUI 框架不是 PySide6（约定：GUI 一律 PySide6）"),
}

#: 行内豁免标记：源码行里出现它（不区分大小写）时，该行的所有发现都被忽略。
SUPPRESS_MARKER = "win-ok"


@dataclass(frozen=True, order=True)
class Finding:
    """一条检查发现。

    ``path`` 为相对检查根目录的 POSIX 风格路径；``line`` 为 0 表示与行无关。
    """

    path: str
    line: int
    code: str
    severity: Severity
    message: str

    def format(self) -> str:
        location = f"{self.path}:{self.line}" if self.line else self.path
        return f"{location}: {self.code} {self.severity.name} {self.message}"

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "line": self.line,
            "code": self.code,
            "severity": self.severity.name,
            "message": self.message,
        }


def make_finding(
    path: str,
    line: int,
    code: str,
    detail: str = "",
    *,
    severity: Severity | None = None,
) -> Finding:
    """按规则表生成 Finding。

    ``detail`` 追加在规则说明之后，``severity`` 可覆盖规则的默认级别。
    """
    default_severity, title = RULES[code]
    message = f"{title}：{detail}" if detail else title
    return Finding(path, line, code, severity or default_severity, message)
