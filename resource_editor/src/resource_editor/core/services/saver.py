"""保存流程：构建 → 全量校验 → 备份原文件 → 临时文件原子替换。"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from ..errors import SaveError
from ..model.document import PackDocument
from .verifier import VerifyReport, verify_rebuilt


def save_document(doc: PackDocument, target: str | Path) -> VerifyReport:
    """把文档保存到 target，返回校验报告。

    校验不通过抛 :class:`SaveError`（报告附在异常 args 中可读文本）。
    若 target 已存在且不是本次新建，先复制一份 ``.bak`` 备份。
    """
    target = Path(target)
    built = doc.build_bytes()
    report = verify_rebuilt(built, [doc.stored(i) for i in range(doc.count)])
    if not report.ok:
        raise SaveError("保存前校验未通过：" + "；".join(report.messages))
    if target.exists():
        shutil.copyfile(target, target.with_suffix(target.suffix + ".bak"))
    tmp = target.with_suffix(target.suffix + ".tmp")
    try:
        tmp.write_bytes(built)
        os.replace(tmp, target)
    except OSError as exc:
        raise SaveError(f"写入文件失败：{exc}") from exc
    doc.mark_saved(target)
    return report
