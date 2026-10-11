"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from mxsj_server.contracts.common import RequestContext, CommandReceipt

@dataclass(frozen=True, slots=True, kw_only=True)
class CurrencyBalance:
    currency_id: int
    amount: int

@dataclass(frozen=True, slots=True, kw_only=True)
class ApplyReward:
    """仅限可信内部调用；计划与领取资格必须来自服务端，不接受客户端资产明细。"""
    reward_plan_id: str
    beneficiary_character_id: int
    claim_key: str
    reason: str

class EconomyAPI(Protocol):
    async def balances(self, ctx: RequestContext) -> tuple[CurrencyBalance, ...]: ...
    async def apply_reward(self, ctx: RequestContext, request: ApplyReward) -> CommandReceipt: ...
