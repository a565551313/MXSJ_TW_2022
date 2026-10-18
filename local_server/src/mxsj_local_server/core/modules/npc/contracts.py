"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from mxsj_local_server.core.contracts.common import CommandReceipt, RequestContext


@dataclass(frozen=True, slots=True, kw_only=True)
class DialogueOption:
    option_id: int
    label: str


@dataclass(frozen=True, slots=True, kw_only=True)
class DialogueView:
    dialogue_token: str
    npc_instance_id: int
    text: str
    options: tuple[DialogueOption, ...]
    expires_at_ms: int


class NpcAPI(Protocol):
    async def interact(
        self, ctx: RequestContext, *, npc_instance_id: int
    ) -> DialogueView: ...
    async def select_option(
        self, ctx: RequestContext, *, dialogue_token: str, option_id: int
    ) -> CommandReceipt: ...
