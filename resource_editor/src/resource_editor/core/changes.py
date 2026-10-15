"""资源包保存前的增量清单（不解码/不读取未修改负载）。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceChange:
    operation: str
    identity: str
    name: str
    before_size: int | None
    after_size: int | None


def counts(changes: list[ResourceChange]) -> dict[str, int]:
    return {
        kind: sum(change.operation == kind for change in changes)
        for kind in ("新增", "修改", "删除")
    }
