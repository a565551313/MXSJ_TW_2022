"""重打包结果校验：重新解析新包并逐条比对、试解码全部精灵。"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from ..codecs import detect
from ..codecs.sprite import decode_sprite
from ..containers import open_archive, open_archive_path
from ..errors import ContainerError


@dataclass
class VerifyReport:
    """校验结果。ok 为 False 时 messages 给出全部问题。"""

    ok: bool = True
    messages: list[str] = field(default_factory=list)
    sprite_checked: int = 0
    # 原包自带、本机解码器覆盖外的精灵数（字节未动，只提示不拦截）
    sprite_undecodable: int = 0


_MAX_MESSAGES = 50


def _check_archive(archive, count: int,
                   expected_stored: Callable[[int], bytes],
                   changed: set[int] | None = None) -> VerifyReport:
    """对已重解析的 archive 逐条比对存储字节并试解码精灵。

    存储字节逐字一致是硬闸门。试解码只是启发式：原包自带的精灵
    若超出本机解码器覆盖（游戏能读、只是我们没覆盖那种变体）而
    本次又未改动它（index 不在 ``changed`` 里），不应拦下整包
    保存——记入 ``sprite_undecodable`` 提示即可；被改动/新增的
    精灵解不开才算问题。``changed=None`` 时全部按在检处理
    （内存重组校验维持旧严格度）。
    """
    report = VerifyReport()
    problems = 0

    def complain(text: str) -> None:
        nonlocal problems
        report.ok = False
        problems += 1
        if problems <= _MAX_MESSAGES:
            report.messages.append(text)

    if archive.orig_count != count:
        complain(f"条目数不一致：重解析 {archive.orig_count}，期望 {count}")
        return report
    for index in range(count):
        got = archive.read_stored(index)
        if got != expected_stored(index):
            complain(f"条目 {index} 负载与预期不一致")
    # 逐条试解码精灵（sprite 只存在于 0SLF 包，负载即内容视图）
    for index in range(count):
        head = archive.stored_head(index, 512)
        if detect.sniff_prefix(head) is detect.EntryKind.SPRITE:
            try:
                decode_sprite(archive.read_stored(index))
                report.sprite_checked += 1
            except Exception as exc:  # 解码器异常统一汇报
                if changed is not None and index not in changed:
                    report.sprite_undecodable += 1  # 原样保留，不拦截
                else:
                    complain(f"条目 {index} 精灵解码失败：{exc}")
    if problems > _MAX_MESSAGES:
        report.messages.append(
            f"…另有 {problems - _MAX_MESSAGES} 处问题（已省略）")
    return report


def verify_rebuilt(built: bytes, expected_payloads: list[bytes]) -> VerifyReport:
    """校验构建出的包字节：可重解析、条目数/负载一致、精灵可解码。"""
    try:
        archive = open_archive(built)
    except ContainerError as exc:
        return VerifyReport(ok=False, messages=[f"重解析失败：{exc}"])
    try:
        return _check_archive(
            archive, len(expected_payloads), expected_payloads.__getitem__)
    finally:
        archive.close()


def verify_saved(path: str | Path, count: int,
                 expected_stored: Callable[[int], bytes],
                 changed: set[int] | None = None) -> VerifyReport:
    """流式校验已写出的包文件（惰性重开索引，逐条按需比对）。

    ``changed`` 为本次改动/新增的条目下标：只有这些条目的精灵
    试解码失败才拦截保存，未改动的原始精灵只提示（见
    :func:`_check_archive`）。
    """
    try:
        archive = open_archive_path(path)
    except ContainerError as exc:
        return VerifyReport(ok=False, messages=[f"重解析失败：{exc}"])
    try:
        return _check_archive(archive, count, expected_stored,
                              changed=changed)
    finally:
        archive.close()
