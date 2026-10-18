"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from mxsj_local_server.core.contracts.common import CommandReceipt, RequestContext


class ChatChannel(str, Enum):  # noqa: UP042  # 保留原契约的 str(Enum) 行为。
    NEARBY = "nearby"
    PARTY = "party"
    GUILD = "guild"
    WORLD = "world"
    PRIVATE = "private"


@dataclass(frozen=True, slots=True, kw_only=True)
class SendChat:
    channel: ChatChannel
    text: str
    recipient_character_id: int | None = None


class SocialAPI(Protocol):
    async def send_chat(
        self, ctx: RequestContext, request: SendChat
    ) -> CommandReceipt: ...
    async def request_friend(
        self, ctx: RequestContext, *, target_character_id: int
    ) -> CommandReceipt: ...
