"""批处理脚本（``.bat`` / ``.cmd``）检查：行尾、BOM、代码页。

cmd.exe 按**当前控制台代码页**解析批处理文件本身：中文 Windows 默认是 936（GBK），
一个保存为 UTF-8 的 bat 里只要有中文就会乱码，`chcp 65001` 之前的中文尤其如此；
LF 行尾在含 `goto`/标签的脚本里会出现跳转错位；UTF-8 BOM 会让第一行变成未知命令。
"""

from __future__ import annotations

from wincompat.model import Finding, make_finding

UTF8_BOM = b"\xef\xbb\xbf"
BATCH_SUFFIXES = frozenset({".bat", ".cmd"})


def _first_bare_lf_line(data: bytes) -> int:
    """返回第一处“LF 前面不是 CR”的行号；没有则返回 0。"""
    position = 0
    line = 1
    while True:
        index = data.find(b"\n", position)
        if index < 0:
            return 0
        if index == 0 or data[index - 1 : index] != b"\r":
            return line
        position = index + 1
        line += 1


def check_batch_file(rel: str, data: bytes) -> list[Finding]:
    findings: list[Finding] = []
    if data.startswith(UTF8_BOM):
        findings.append(make_finding(rel, 1, "WIN203"))
        data = data[len(UTF8_BOM) :]

    bare_lf_line = _first_bare_lf_line(data)
    if bare_lf_line:
        findings.append(make_finding(rel, bare_lf_line, "WIN201"))

    chcp_seen = False
    for number, raw in enumerate(data.split(b"\n"), start=1):
        lowered = raw.lower()
        if b"chcp" in lowered and b"65001" in lowered:
            chcp_seen = True
        if not chcp_seen and any(byte > 0x7F for byte in raw):
            findings.append(make_finding(rel, number, "WIN202"))
            break
    return findings
