"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from mxsj_local_server.core.contracts.common import CommandReceipt, RequestContext


@dataclass(frozen=True, slots=True, kw_only=True)
class QuestProgressView:
    quest_instance_id: int
    quest_template_id: int
    state: str
    objective_counts: tuple[int, ...]
    revision: int


class QuestAPI(Protocol):
    async def list_active(
        self, ctx: RequestContext
    ) -> tuple[QuestProgressView, ...]: ...
    async def accept(
        self, ctx: RequestContext, *, quest_template_id: int
    ) -> CommandReceipt: ...
    async def claim_reward(
        self, ctx: RequestContext, *, quest_instance_id: int
    ) -> CommandReceipt: ...
