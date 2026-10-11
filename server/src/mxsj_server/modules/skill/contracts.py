"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from mxsj_server.contracts.common import RequestContext, CommandReceipt

@dataclass(frozen=True, slots=True, kw_only=True)
class LearnedSkillView:
    skill_id: int
    level: int

class SkillAPI(Protocol):
    async def list_learned(self, ctx: RequestContext) -> tuple[LearnedSkillView, ...]: ...
    async def learn(self, ctx: RequestContext, *, skill_id: int) -> CommandReceipt: ...
