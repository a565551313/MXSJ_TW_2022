"""Module access policy shared by readers, associations and native builders.

One place decides which entries may be opened at all, so callers that need to
tell "policy excluded" apart from "actually broken" (whole-package
verification) do not have to repeat the magic index.
"""

from __future__ import annotations

POLICY_EXCLUDED = {("py25", 1288)}


def module_allowed(vm: str, index: int) -> bool:
    return (vm, index) not in POLICY_EXCLUDED


def require_module_allowed(vm: str, index: int) -> None:
    if not module_allowed(vm, index):
        raise ValueError("excluded_by_policy：1288不读取模块负载、不关联源码或替换")
