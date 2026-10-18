"""内部公开契约 v0.1 草案；仅类型定义，不能作为已实现或已验证协议。

校验、授权、事务及错误语义见 server/docs/INTERFACES.md。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from mxsj_local_server.core.contracts.common import CommandReceipt, RequestContext


class ActionKind(str, Enum):  # noqa: UP042  # 保留原契约的 str(Enum) 行为。
    ATTACK = "attack"
    SKILL = "skill"
    DEFEND = "defend"
    ITEM = "item"
    SUMMON = "summon"
    PROTECT = "protect"
    CATCH = "catch"
    ESCAPE = "escape"


class BattlePhase(str, Enum):  # noqa: UP042  # 保留原契约的 str(Enum) 行为。
    PREPARING = "preparing"
    COLLECTING = "collecting"
    LOCKED = "locked"
    RESOLVING = "resolving"
    PRESENTING = "presenting"
    SETTLING = "settling"
    CLOSED = "closed"


@dataclass(frozen=True, slots=True, kw_only=True)
class SubmitAction:
    battle_id: int
    round_no: int
    actor_unit_id: int
    action_kind: ActionKind
    target_unit_ids: tuple[int, ...] = ()
    skill_id: int | None = None
    item_id: int | None = None
    summon_id: int | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class BattleUnitView:
    unit_id: int
    position: int
    appearance_id: int
    hp_percent: int
    public_status_ids: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class BattleView:
    """按请求者权限裁剪；不是含随机状态和敌方未公开指令的内部恢复快照。"""

    battle_id: int
    round_no: int
    phase: BattlePhase
    revision: int
    last_event_sequence: int
    deadline_at_ms: int | None
    units: tuple[BattleUnitView, ...]
    submitted_own_unit_ids: tuple[int, ...]


class BattleAPI(Protocol):
    async def submit_action(
        self, ctx: RequestContext, request: SubmitAction
    ) -> CommandReceipt: ...
    async def view(self, ctx: RequestContext, *, battle_id: int) -> BattleView: ...
    async def acknowledge_presentation(
        self, ctx: RequestContext, *, battle_id: int, round_no: int, event_sequence: int
    ) -> CommandReceipt: ...
