"""保存流程：流式构建 → 重解析校验 → 新包原子落盘，源包不动。

构建与校验都是流式的：未改动条目从源文件整段拷贝，内存占用
与包大小无关（1GB 级包亦可）；校验在临时文件上完成，通过后
才发布新包。
"""
from __future__ import annotations

import os
import tempfile
from collections.abc import Callable, Iterable
from pathlib import Path

from ..errors import SaveError
from ..model.document import PackDocument
from ..output_paths import guard_output
from .verifier import VerifyReport, verify_saved


def save_document(
    doc: PackDocument,
    target: str | Path,
    progress: Callable[[int, int], None] | None = None,
    protected_paths: Iterable[str | Path] = (),
) -> VerifyReport:
    """写入经校验的新包；拒绝任何源包/历史基线及其别名。

    唯一临时文件与目标同目录，失败删除临时文件，旧目标不动。
    已存在的非源输出文件可经校验后原子替换。
    """
    target = Path(target)
    sources = [*doc.source_paths, *protected_paths]
    tmp: Path | None = None
    try:
        with doc.preserve_write_order():
            guard_output(target, sources)
            with tempfile.NamedTemporaryFile(
                prefix=f".{target.name}.", suffix=".tmp",
                dir=target.parent, delete=False,
            ) as out:
                tmp = Path(out.name)
                doc.write_to(out, progress)
                out.flush()
                os.fsync(out.fileno())
            report = verify_saved(tmp, doc.count, doc.stored,
                                  changed=doc.changed_indexes())
            if not report.ok:
                raise SaveError("保存前校验未通过：" + "；".join(report.messages))
            guard_output(target, sources)
            os.replace(tmp, target)
            doc.mark_saved(target)
            return report
    except (OSError, ValueError) as exc:
        raise SaveError(f"写入新包失败：{exc}") from exc
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)
