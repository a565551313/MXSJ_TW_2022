"""重打包结果校验：重新解析新包并逐条比对、试解码全部精灵。"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..codecs import detect
from ..codecs.sprite import decode_sprite
from ..containers import open_archive
from ..errors import ContainerError


@dataclass
class VerifyReport:
    """校验结果。ok 为 False 时 messages 给出全部问题。"""

    ok: bool = True
    messages: list[str] = field(default_factory=list)
    sprite_checked: int = 0


def verify_rebuilt(built: bytes, expected_payloads: list[bytes]) -> VerifyReport:
    """校验构建出的包字节：可重解析、条目数/负载一致、精灵可解码。"""
    report = VerifyReport()
    try:
        archive = open_archive(built)
    except ContainerError as exc:
        return VerifyReport(ok=False, messages=[f"重解析失败：{exc}"])
    if archive.count != len(expected_payloads):
        report.ok = False
        report.messages.append(
            f"条目数不一致：重解析 {archive.count}，期望 {len(expected_payloads)}"
        )
        return report
    for index, (got, want) in enumerate(
            zip(archive.payloads, expected_payloads, strict=True)):
        if got != want:
            report.ok = False
            report.messages.append(f"条目 {index} 负载与预期不一致")
    # 逐条试解码精灵（sprite 只存在于 0SLF 包，负载即内容视图）
    for index, payload in enumerate(archive.payloads):
        if detect.sniff(payload) is detect.EntryKind.SPRITE:
            try:
                decode_sprite(payload)
                report.sprite_checked += 1
            except Exception as exc:  # 解码器异常统一汇报
                report.ok = False
                report.messages.append(f"条目 {index} 精灵解码失败：{exc}")
    return report
