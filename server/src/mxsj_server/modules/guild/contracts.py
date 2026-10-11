"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from mxsj_server.contracts.common import RequestContext, CommandReceipt

@dataclass(frozen=True, slots=True, kw_only=True)
class GuildView:
    guild_id: int
    name: str
    leader_character_id: int
    member_count: int
    revision: int

class GuildAPI(Protocol):
    async def current(self, ctx: RequestContext) -> GuildView | None: ...
    async def apply_to_join(self, ctx: RequestContext, *, guild_id: int) -> CommandReceipt: ...
    async def review_application(self, ctx: RequestContext, *, application_id: int, approve: bool) -> CommandReceipt: ...
