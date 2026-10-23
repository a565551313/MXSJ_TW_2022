"""Decide whether a set of XOR parameters really decodes this exact package.

A pin table can only ever list packages it has already seen, and every rebuild
changes the whole-package fingerprint. So instead of asking "is this package on
the list", this module answers the question the list was standing in for:
*do these parameters decode this package?*

Every entry the policy allows is decoded with the same strict path the entry
browser uses (strict zlib -> native boundary calibration -> strict marshal
parse). If essentially all of them decode, the parameters fit the package and
are adopted automatically; if a large share fails, the parameters belong to a
different package and are refused. A handful of failures inside an otherwise
perfect package is reported entry by entry instead of hiding the whole package.

Nothing here guesses keys or boundaries: the candidate parameters come from an
authorized catalog file, and only the verdict is derived from the data.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path

from ..policy import module_allowed
from ..project.storage import CatalogRef
from ..vm.py25.keys import read_catalog
from .module_paths import scan_script_paths

#: Share of policy-allowed entries that must decode strictly before the
#: parameters are treated as belonging to this package. One damaged entry in a
#: healthy 5002-entry package stays accepted and is reported individually; a
#: catalog from another build fails almost everywhere and stays refused.
MIN_ACCEPTED_RATIO = 0.99

#: How many entry failures to spell out before summarising the rest.
MAX_REPORTED_FAILURES = 8

_PREFIX = "路径读取失败："


@dataclass(frozen=True)
class PackageCheck:
    """Result of decoding every allowed entry with one catalog."""

    ref: CatalogRef | None
    paths: dict = field(default_factory=dict)
    errors: dict = field(default_factory=dict)
    passed: int = 0
    excluded: int = 0
    failures: tuple = ()
    elapsed: float = 0.0

    @property
    def total(self) -> int:
        """Entries the strict check actually tried (policy exclusions aside)."""
        return self.passed + len(self.failures)

    @property
    def accepted(self) -> bool:
        return self.total > 0 and self.passed >= self.total * MIN_ACCEPTED_RATIO

    def apply(self, archive) -> None:
        """Adopt the verified names on the document (worker thread only)."""
        archive.module_paths = dict(self.paths)
        archive.module_path_errors = dict(self.errors)

    def summary(self) -> str:
        skips = f"，{self.excluded} 条按策略跳过" if self.excluded else ""
        seconds = f"{self.elapsed:.1f} 秒"
        if not self.failures:
            return (
                f"内置解码参数自检通过：{self.passed} 条逐条严格解码全部成功"
                f"{skips}（{seconds}）。"
            )
        if self.accepted:
            return (
                f"内置解码参数自检通过：{self.passed}/{self.total} 条严格解码成功"
                f"{skips}，{len(self.failures)} 条失败（{seconds}）。"
            )
        return (
            f"内置解码参数与这个包不匹配：只有 {self.passed}/{self.total} 条能解码"
            f"{skips}（{seconds}）。"
        )

    def report(self) -> str:
        """Human-facing multi-line verdict: what happened and why."""
        lines = [self.summary()]
        if self.failures:
            lines.append("以下条目无法用这套参数解码：")
            for index, reason in self.failures[:MAX_REPORTED_FAILURES]:
                lines.append(f"  · 条目 #{index}：{reason}")
            hidden = len(self.failures) - MAX_REPORTED_FAILURES
            if hidden > 0:
                lines.append(f"  · …另有 {hidden} 条")
        if self.accepted and self.failures:
            lines.append(
                "参数本身与包相符；上面这些条目是它们自己的数据解不干净，"
                "其余条目不受影响。"
            )
        elif not self.accepted:
            lines.append(
                "失败面太大，说明这套参数属于另一个包（或另一个版本）。未套用，"
                "请选择与此包匹配的 XOR 参数文件。"
            )
        return "\n".join(lines)


def _reason(text: str) -> str:
    return text[len(_PREFIX) :] if text.startswith(_PREFIX) else text


def verify_with_catalog(archive, catalog: Path) -> PackageCheck:
    """Decode every allowed entry of ``archive`` with ``catalog``.

    Runs a full strict decode pass (seconds, not milliseconds): call it from a
    worker thread, never the GUI thread. Raises ValueError/OSError only for
    catalog-level problems (unreadable, wrong digest pin, not a script
    container); per-entry failures are reported, not raised.
    """
    if archive.vm != "py25" or archive.kind != "0slf":
        raise ValueError("只有 py2.5 script 包需要五段 XOR 参数")
    started = time.monotonic()
    path = Path(catalog).resolve(strict=True)
    ref = CatalogRef(
        archive.path,
        archive.fingerprint(),
        path,
        hashlib.sha256(read_catalog(path)).hexdigest(),
    )
    paths, errors = scan_script_paths(archive, ref)
    failures = tuple(
        (index, _reason(reason))
        for index, reason in sorted(errors.items())
        if module_allowed(archive.vm, index)
    )
    excluded = len(errors) - len(failures)
    return PackageCheck(
        ref=ref,
        paths=paths,
        errors=errors,
        passed=len(paths),
        excluded=excluded,
        failures=failures,
        elapsed=time.monotonic() - started,
    )
