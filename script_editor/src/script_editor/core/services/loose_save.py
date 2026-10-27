"""Decide what a loose save would write, without touching Qt or the disk.

A loose save compiles every binding whose current text does not match the
source that produced the bytes already in the package. "Current text" comes
from the editor buffer when a tab is open and from a strict UTF-8 read
otherwise; both are supplied by the caller, so this module stays a pure
function of its inputs and can be tested without a GUI.
"""

from __future__ import annotations

from dataclasses import dataclass

from .workflow import text_sha

#: Refuse to silently write a huge batch: the confirmation list would become
#: unreadable and one bad binding would spoil the whole run.
MAX_LOOSE_ENTRIES = 64

#: How many entries the confirmation text spells out before summarising.
LISTED_ENTRIES = 20


@dataclass(frozen=True)
class LooseCandidate:
    binding: object
    text: str


@dataclass(frozen=True)
class LooseProblem:
    binding: object
    reason: str


def changed_bindings(bindings, archive, read_text):
    """Return ``(candidates, problems)`` for one package.

    ``read_text(binding)`` returns the current source text or raises
    ``OSError``/``UnicodeDecodeError``; the caller decides where that text comes
    from. A binding is a candidate when its text differs from
    ``built_source_sha256`` — the source that produced the bytes in the package.
    An empty baseline means "never written", which is also a change.
    """
    candidates, problems = [], []
    for binding in bindings:
        if binding.archive != archive.path or binding.vm != archive.vm:
            continue
        try:
            text = read_text(binding)
        except (OSError, UnicodeDecodeError) as exc:
            problems.append(LooseProblem(binding, f"源码无法读取：{exc}"))
            continue
        if binding.built_source_sha256 and text_sha(text) == (
            binding.built_source_sha256
        ):
            continue
        candidates.append(LooseCandidate(binding, text))
    return tuple(candidates), tuple(problems)


def rejection(candidates, problems) -> str:
    """Explain an empty batch; empty string when there is something to write."""
    if candidates:
        return ""
    detail = "".join(f"\n· {p.binding.source.name}：{p.reason}" for p in problems)
    return (
        "这个包里没有「已关联且内容有变动」的条目，未写入任何文件。"
        + (detail or "\n· 若只是要保存 .py，请用「保存项目」，或先把条目关联到源码")
    )


def batch_summary(candidates, problems, name_for) -> str:
    """Human-readable list for the confirmation dialog (caller adds the path)."""
    if len(candidates) > MAX_LOOSE_ENTRIES:
        raise ValueError(
            f"一次要写回 {len(candidates)} 条，超过 {MAX_LOOSE_ENTRIES} 条上限；"
            "请分批保存，避免一次失败影响过多条目"
        )
    lines = [
        f"· #{c.binding.index} {name_for(c.binding)}"
        for c in candidates[:LISTED_ENTRIES]
    ]
    if len(candidates) > LISTED_ENTRIES:
        lines.append(f"… 另有 {len(candidates) - LISTED_ENTRIES} 条")
    if problems:
        lines.append(f"未纳入 {len(problems)} 条（源码不可读等，详见诊断）")
    return "\n".join(lines)
