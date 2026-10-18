"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from mxsj_local_server.core.contracts.common import CommandReceipt, RequestContext


@dataclass(frozen=True, slots=True, kw_only=True)
class MoveRequest:
    map_instance_id: int
    movement_sequence: int
    directions: tuple[int, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class PositionView:
    map_instance_id: int
    map_template_id: int
    x: int
    y: int
    revision: int


class WorldAPI(Protocol):
    async def position(self, ctx: RequestContext) -> PositionView: ...
    async def move(
        self, ctx: RequestContext, request: MoveRequest
    ) -> CommandReceipt: ...
    async def use_portal(
        self, ctx: RequestContext, *, portal_id: int
    ) -> CommandReceipt: ...
