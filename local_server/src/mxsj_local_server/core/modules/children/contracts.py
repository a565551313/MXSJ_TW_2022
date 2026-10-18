"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from mxsj_local_server.core.contracts.common import CommandReceipt, RequestContext


@dataclass(frozen=True, slots=True, kw_only=True)
class ChildView:
    child_id: int
    name: str
    growth_stage_id: int
    revision: int


class ChildrenAPI(Protocol):
    async def list_owned(self, ctx: RequestContext) -> tuple[ChildView, ...]: ...
    async def cultivate(
        self, ctx: RequestContext, *, child_id: int, plan_id: int
    ) -> CommandReceipt: ...
