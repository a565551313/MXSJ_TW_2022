"""When may a recovered draft become writable source for a package entry?

Three different things are called "the source" in this editor, and they are not
equally trustworthy:

* a draft the bundled engine produced from the package's own bytes;
* a draft produced from an *external corpus*, whose ``.pyc`` may not be the
  bytes this package actually stores;
* a draft the user edited afterwards (still unverified).

Automatic binding (``auto_adopt``) and the manual path both have to apply the
same rule, otherwise the softer path becomes a way around the stricter one. The
rule lives here, without Qt, so both callers and the tests share one copy.
"""

from __future__ import annotations

import hashlib


def standard_sha256(pyc: bytes) -> str:
    return hashlib.sha256(pyc).hexdigest()


def origin_conflict(report, standard: bytes) -> str | None:
    """Reason this report must not be bound to ``standard``, or ``None``.

    ``standard`` is the package entry's own strict standard bytecode, as read by
    :func:`script_editor.core.inspection.native.inspect_module`.
    """
    if report is None:
        return None
    digest = standard_sha256(standard)
    target = getattr(report, "target_archive", None)
    if target is not None and getattr(report, "standard_sha256", ""):
        if digest != report.standard_sha256:
            return (
                "继续采用目标的标准字节码已变化；保留原稿，"
                "请重新打开条目再写包"
            )
    manifest = getattr(report, "corpus_manifest_sha256", "")
    candidate = getattr(report, "candidate_pyc_sha256", "")
    if manifest and not candidate:
        return (
            "外部语料未核验出与原包一致的标准字节码；可编辑草稿，"
            "但不能据此自动绑定或写包"
        )
    if candidate and digest != candidate:
        return (
            "外部语料pyc与原包严格来源不同；可编辑草稿，"
            "但不能据此自动绑定或写包"
        )
    return None
