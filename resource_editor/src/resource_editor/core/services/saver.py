"""保存流程：流式构建 → 重解析校验 → 备份原文件 → 临时文件原子替换。

构建与校验都是流式的：未改动条目从源文件整段拷贝，内存占用
与包大小无关（1GB 级包亦可）；校验在临时文件上完成，通过后
才动原文件。
"""
from __future__ import annotations

import os
import shutil
from collections.abc import Callable
from pathlib import Path

from ..errors import SaveError
from ..model.document import PackDocument
from .verifier import VerifyReport, verify_saved


def save_document(
    doc: PackDocument,
    target: str | Path,
    progress: Callable[[int, int], None] | None = None,
) -> VerifyReport:
    """把文档保存到 target，返回校验报告。

    校验不通过抛 :class:`SaveError`（报告附在异常 args 中可读文本）。
    若 target 已存在且不是本次新建，先复制一份 ``.bak`` 备份。
    """
    target = Path(target)
    tmp = target.with_suffix(target.suffix + ".tmp")
    try:
        with open(tmp, "wb") as out:
            doc.write_to(out, progress)
    except OSError as exc:
        raise SaveError(f"写入临时文件失败：{exc}") from exc
    report = verify_saved(tmp, doc.count, doc.stored,
                          changed=doc.changed_indexes())
    if not report.ok:
        tmp.unlink(missing_ok=True)
        raise SaveError("保存前校验未通过：" + "；".join(report.messages))
    try:
        if target.exists():
            shutil.copyfile(target, target.with_suffix(target.suffix + ".bak"))
    except OSError as exc:
        raise SaveError(f"写入文件失败：{exc}") from exc
    # Windows 上 target 若还被文档的惰性读句柄占着，os.replace 会
    # 报 PermissionError（POSIX 无此限制，所以 Linux 测不出来）：
    # 先释放源句柄再替换；替换失败则按原路径重开，编辑状态保留，
    # 成功后由 mark_saved 以新文件重建基线。
    doc.close()
    try:
        os.replace(tmp, target)
    except OSError as exc:
        try:
            doc.reopen_source()
        except Exception:
            pass  # 重开失败也不掩盖真正的保存错误
        raise SaveError(f"写入文件失败：{exc}") from exc
    doc.mark_saved(target)
    return report
