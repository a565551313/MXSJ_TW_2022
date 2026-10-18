"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from mxsj_local_server.core.contracts.common import CommandReceipt, RequestContext


@dataclass(frozen=True, slots=True, kw_only=True)
class AppearanceView:
    unlocked_template_ids: tuple[int, ...]
    equipped_template_ids: tuple[int, ...]
    revision: int


class AppearanceAPI(Protocol):
    async def owned(self, ctx: RequestContext) -> AppearanceView: ...
    async def equip(
        self, ctx: RequestContext, *, appearance_template_id: int, slot_id: int
    ) -> CommandReceipt: ...
