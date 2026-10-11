"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from mxsj_server.contracts.common import RequestContext, CommandReceipt

@dataclass(frozen=True, slots=True, kw_only=True)
class CreateCharacter:
    name: str
    appearance_template_id: int
    school_id: int

@dataclass(frozen=True, slots=True, kw_only=True)
class CharacterView:
    character_id: int
    name: str
    level: int
    school_id: int
    revision: int

class CharacterAPI(Protocol):
    async def list_characters(self, ctx: RequestContext) -> tuple[CharacterView, ...]: ...
    async def create(self, ctx: RequestContext, request: CreateCharacter) -> CharacterView: ...
    async def enter_world(self, ctx: RequestContext, *, character_id: int) -> CommandReceipt: ...
