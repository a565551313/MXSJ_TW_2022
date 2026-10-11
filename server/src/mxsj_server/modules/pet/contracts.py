"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from mxsj_server.contracts.common import RequestContext, CommandReceipt

@dataclass(frozen=True, slots=True, kw_only=True)
class PetView:
    pet_id: int
    template_id: int
    name: str
    level: int
    assigned_to_battle: bool
    revision: int

class PetAPI(Protocol):
    async def list_owned(self, ctx: RequestContext) -> tuple[PetView, ...]: ...
    async def set_active(self, ctx: RequestContext, *, pet_id: int | None) -> CommandReceipt: ...
    async def train(self, ctx: RequestContext, *, pet_id: int, training_plan_id: int) -> CommandReceipt: ...
