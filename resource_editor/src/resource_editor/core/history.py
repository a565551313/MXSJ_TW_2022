"""有界增量撤销时间线：只保留修改过的字节与条目，不快照整个包。"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class Action:
    """一个已经执行的可逆增量操作。"""

    undo: Callable[[], None]
    redo: Callable[[], None]
    byte_cost: int = 0


@dataclass
class Step:
    label: str
    actions: list[Action]

    @property
    def byte_cost(self) -> int:
        return sum(action.byte_cost for action in self.actions)


class History:
    """最多 50 步/64 MiB（单个超大步骤保留一条），批量操作算一步。"""

    def __init__(self, limit: int = 50, byte_limit: int = 64 * 1024 * 1024):
        self.limit = limit
        self.byte_limit = byte_limit
        self.applied: list[Step] = []
        self.undone: list[Step] = []
        self._groups: list[Step] = []

    def clear(self) -> None:
        self.applied.clear()
        self.undone.clear()

    @property
    def in_group(self) -> bool:
        return bool(self._groups)

    @property
    def can_undo(self) -> bool:
        return bool(self.applied) and not self._groups

    @property
    def can_redo(self) -> bool:
        return bool(self.undone) and not self._groups

    @property
    def undo_label(self) -> str:
        return self.applied[-1].label if self.applied else ""

    @property
    def redo_label(self) -> str:
        return self.undone[-1].label if self.undone else ""

    def _append(self, step: Step) -> None:
        self.undone.clear()
        self.applied.append(step)
        while len(self.applied) > 1 and (
            len(self.applied) > self.limit
            or sum(s.byte_cost for s in self.applied) > self.byte_limit
        ):
            self.applied.pop(0)

    def record(self, label: str, action: Action) -> None:
        if self._groups:
            self._groups[-1].actions.append(action)
        else:
            self._append(Step(label, [action]))

    @contextmanager
    def group(self, label: str) -> Iterator[None]:
        """成功的批量操作提交一步；异常回滚本组，保留原重做分支。"""
        step = Step(label, [])
        self._groups.append(step)
        try:
            yield
        except BaseException:
            for action in reversed(step.actions):
                action.undo()
            raise
        else:
            if step.actions:
                if len(self._groups) > 1:
                    self._groups[-2].actions.extend(step.actions)
                else:
                    self._append(step)
        finally:
            self._groups.pop()

    def undo(self) -> bool:
        if not self.can_undo:
            return False
        step = self.applied.pop()
        for action in reversed(step.actions):
            action.undo()
        self.undone.append(step)
        return True

    def redo(self) -> bool:
        if not self.can_redo:
            return False
        step = self.undone.pop()
        for action in step.actions:
            action.redo()
        self.applied.append(step)
        return True
