"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from mxsj_server.contracts.common import RequestContext, CommandReceipt

@dataclass(frozen=True, slots=True, kw_only=True)
class CraftRequest:
    recipe_id: int
    material_item_ids: tuple[int, ...]
    target_item_id: int | None = None

class CraftingAPI(Protocol):
    async def craft(self, ctx: RequestContext, request: CraftRequest) -> CommandReceipt: ...
