"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from mxsj_local_server.core.contracts.common import CommandReceipt, RequestContext


@dataclass(frozen=True, slots=True, kw_only=True)
class CompensationRequest:
    target_character_id: int
    approved_reward_plan_id: str
    approval_reference: str
    reason: str


class AdministrationAPI(Protocol):
    async def compensate(
        self, ctx: RequestContext, request: CompensationRequest
    ) -> CommandReceipt: ...
    async def ban_account(
        self, ctx: RequestContext, *, account_id: int, until_ms: int, reason: str
    ) -> CommandReceipt: ...
