"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from mxsj_server.contracts.common import RequestContext, CommandReceipt

@dataclass(frozen=True, slots=True, kw_only=True)
class ActivitySummary:
    activity_instance_id: int
    activity_template_id: int
    name: str
    starts_at_ms: int
    ends_at_ms: int

class ActivityAPI(Protocol):
    async def available(self, ctx: RequestContext) -> tuple[ActivitySummary, ...]: ...
    async def join(self, ctx: RequestContext, *, activity_instance_id: int) -> CommandReceipt: ...
    async def claim_reward(self, ctx: RequestContext, *, activity_instance_id: int, reward_tier_id: int) -> CommandReceipt: ...
