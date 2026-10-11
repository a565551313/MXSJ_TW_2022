"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from mxsj_server.contracts.common import RequestContext, CommandReceipt

@dataclass(frozen=True, slots=True, kw_only=True)
class MoveItem:
    item_id: int
    destination_container_id: int
    destination_slot: int
    expected_revision: int

@dataclass(frozen=True, slots=True, kw_only=True)
class ItemView:
    item_id: int
    template_id: int
    quantity: int
    container_id: int
    slot: int
    bound: bool
    revision: int

class InventoryAPI(Protocol):
    async def list_items(self, ctx: RequestContext, *, container_id: int) -> tuple[ItemView, ...]: ...
    async def move(self, ctx: RequestContext, request: MoveItem) -> CommandReceipt: ...
    async def use(self, ctx: RequestContext, *, item_id: int, quantity: int, target_id: int | None) -> CommandReceipt: ...
