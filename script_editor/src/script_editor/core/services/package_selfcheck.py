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

import time
from dataclasses import dataclass, field
from pathlib import Path

from ..policy import module_allowed
from ..project.storage import CatalogRef
from ..vm.py25.keys import catalog_snapshot
from .module_paths import scan_script_paths
from .verdict_cache import PackageVerdict, policy_fingerprint

#: Share of policy-allowed entries that must decode strictly before the
#: parameters are treated as belonging to this package. One damaged entry in a
#: healthy 5002-entry package stays accepted and is reported individually; a
#: catalog from another build fails almost everywhere and stays refused.
MIN_ACCEPTED_RATIO = 0.99

#: How many entry failures to spell out before summarising the rest.
MAX_REPORTED_FAILURES = 8

#: A mismatched catalog fails almost everywhere, so a bounded probe can refuse
#: it in well under a second instead of decoding every entry first. The probe
#: may only ever *refuse*: accepting parameters still needs the complete pass.
PROBE_ENTRIES = 96
PROBE_FAILURE_RATIO = 0.5

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
    probed: int = 0
    cached: bool = False

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

    @property
    def refused_early(self) -> bool:
        """True when a bounded probe refused the parameters without a full pass."""
        return bool(self.probed) and not self.accepted

    def summary(self) -> str:
        skips = f"，{self.excluded} 条按策略跳过" if self.excluded else ""
        seconds = f"{self.elapsed:.1f} 秒"
        if self.cached:
            seconds += "，来自同一包的既有判定缓存"
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

    def verdict(self, archive, tool_version: str) -> PackageVerdict:
        """Describe this verdict so an identical input can reuse it later."""
        return PackageVerdict(
            archive_sha256=archive.fingerprint(),
            catalog_sha256=self.ref.sha256 if self.ref is not None else "",
            tool_version=str(tool_version),
            policy=policy_fingerprint(),
            vm=archive.vm,
            entries=len(archive.entries),
            accepted=self.accepted,
            passed=self.passed,
            failures=tuple(self.failures),
            paths=dict(self.paths),
            errors=dict(self.errors),
            elapsed=self.elapsed,
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
            if self.refused_early:
                lines.append(
                    f"（已用前 {self.probed} 条探测判定，未扫描全包；"
                    "参数确实相同时才会走完整校验。）"
                )
        return "\n".join(lines)


def _reason(text: str) -> str:
    return text[len(_PREFIX) :] if text.startswith(_PREFIX) else text


def _check_from_verdict(
    verdict: PackageVerdict, archive, catalog: Path
) -> PackageCheck:
    ref = CatalogRef(
        archive.path,
        verdict.archive_sha256,
        Path(catalog).resolve(),
        verdict.catalog_sha256,
    )
    return PackageCheck(
        ref=ref,
        paths=dict(verdict.paths),
        errors=dict(verdict.errors),
        passed=verdict.passed,
        excluded=len(archive.entries) - len(verdict.paths) - len(verdict.errors),
        failures=tuple(verdict.failures),
        elapsed=verdict.elapsed,
        cached=True,
    )


def verify_with_catalog(
    archive, catalog: Path, *, probe: bool | None = None, progress=None
) -> PackageCheck:
    """Decode every allowed entry of ``archive`` with ``catalog``.

    Runs a full strict decode pass (seconds, not milliseconds): call it from a
    worker thread, never the GUI thread. Raises ValueError/OSError only for
    catalog-level problems (unreadable, wrong digest pin, not a script
    container); per-entry failures are reported, not raised.

    ``probe=True`` first decodes a bounded sample so obviously wrong parameters
    are refused in a fraction of a second; ``probe=False`` always scans fully.
    ``progress(done, total)`` may be called from this thread.
    """
    if archive.vm != "py25" or archive.kind != "0slf":
        raise ValueError("只有 py2.5 script 包需要五段 XOR 参数")
    started = time.monotonic()
    path = Path(catalog).resolve(strict=True)
    _, digest = catalog_snapshot(path)
    ref = CatalogRef(archive.path, archive.fingerprint(), path, digest)
    allowed_total = sum(
        1 for e in archive.entries if module_allowed(archive.vm, e.index)
    )
    excluded = len(archive.entries) - allowed_total

    should_probe = allowed_total > PROBE_ENTRIES if probe is None else probe
    if should_probe and allowed_total > PROBE_ENTRIES:
        paths, errors = scan_script_paths(archive, ref, limit=PROBE_ENTRIES)
        broken = sum(
            1 for index in errors if module_allowed(archive.vm, index)
        )
        if broken > PROBE_ENTRIES * PROBE_FAILURE_RATIO:
            failures = tuple(
                (index, _reason(reason)) for index, reason in sorted(errors.items())
            )
            return PackageCheck(
                ref=ref,
                paths=paths,
                errors=errors,
                passed=len(paths),
                excluded=excluded,
                failures=failures,
                elapsed=time.monotonic() - started,
                probed=PROBE_ENTRIES,
            )
    paths, errors = scan_script_paths(archive, ref, progress=progress)
    failures = tuple(
        (index, _reason(reason))
        for index, reason in sorted(errors.items())
        if module_allowed(archive.vm, index)
    )
    return PackageCheck(
        ref=ref,
        paths=paths,
        errors=errors,
        passed=len(paths),
        excluded=excluded,
        failures=failures,
        elapsed=time.monotonic() - started,
    )


def verified_with_cache(
    archive,
    catalog: Path,
    cache=None,
    *,
    tool_version: str,
    probe: bool | None = None,
    progress=None,
) -> PackageCheck:
    """``verify_with_catalog`` plus reuse of an identical earlier verdict.

    A cache hit skips recomputation only: both the package and the parameter
    table are addressed by digest and the verdict carries the tool version and
    exclusion policy it was produced under, so a hit reproduces exactly what a
    fresh scan of the same inputs would have concluded.
    """
    path = Path(catalog).resolve(strict=True)
    _, digest = catalog_snapshot(path)
    if cache is not None:
        verdict = cache.load(archive, digest)
        if verdict is not None:
            check = _check_from_verdict(verdict, archive, path)
            check.apply(archive)
            return check
    check = verify_with_catalog(archive, path, probe=probe, progress=progress)
    if cache is not None and check.ref is not None and not check.refused_early:
        cache.store(archive, check.verdict(archive, tool_version))
    return check
