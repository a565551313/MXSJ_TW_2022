"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from mxsj_local_server.core.contracts.common import CommandReceipt, RequestContext


@dataclass(frozen=True, slots=True, kw_only=True)
class PartyView:
    party_id: int
    leader_character_id: int
    member_character_ids: tuple[int, ...]
    revision: int


class PartyAPI(Protocol):
    async def current(self, ctx: RequestContext) -> PartyView | None: ...
    async def invite(
        self, ctx: RequestContext, *, target_character_id: int
    ) -> CommandReceipt: ...
    async def respond_invitation(
        self, ctx: RequestContext, *, invitation_id: int, accept: bool
    ) -> CommandReceipt: ...
