"""Module access policy shared by readers, associations and native builders."""

from __future__ import annotations


def require_module_allowed(vm: str, index: int) -> None:
    if vm == "py25" and index == 1288:
        raise ValueError("excluded_by_policy：1288不读取模块负载、不关联源码或替换")
