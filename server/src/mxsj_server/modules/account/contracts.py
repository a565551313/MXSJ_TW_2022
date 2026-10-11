"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol
from mxsj_server.contracts.common import RequestContext, CommandReceipt

@dataclass(frozen=True, slots=True, kw_only=True)
class LoginRequest:
    account_name: str
    credential: bytes = field(repr=False)
    protocol_version: str

@dataclass(frozen=True, slots=True, kw_only=True)
class LoginResult:
    account_id: int
    session_ticket: str = field(repr=False)
    expires_at_ms: int

class AccountAPI(Protocol):
    async def authenticate(self, request: LoginRequest) -> LoginResult: ...
    async def revoke_sessions(self, ctx: RequestContext, *, account_id: int, reason: str) -> CommandReceipt: ...
