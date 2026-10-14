"""零 Qt 的布局改动清单与待入包图片筛选。未知字段同样参加比较。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LayoutChange:
    operation: str
    path: tuple[int, ...]
    name: str
    field: str
    before: str
    after: str


def path_label(path: tuple[int, ...]) -> str:
    return "/".join(str(index + 1) for index in path)


def _flatten(roots: list[dict], parent: tuple[int, ...] = ()) -> dict:
    result = {}
    for index, data in enumerate(roots):
        path = (*parent, index)
        result[path] = {key: value for key, value in data.items() if key != "lChildren"}
        result.update(_flatten(data.get("lChildren", []), path))
    return result


def layout_changes(before: list[dict], after: list[dict]) -> list[LayoutChange]:
    """按树位置比较；重排/移动会表现为相应位置的字段与增删差异。"""
    old, new = _flatten(before), _flatten(after)
    changes = []
    for path in sorted(old.keys() | new.keys()):
        left, right = old.get(path), new.get(path)
        if left is None or right is None:
            data = right if left is None else left
            changes.append(
                LayoutChange(
                    "新增控件" if left is None else "删除控件",
                    path,
                    str(data.get("sName", "")),
                    "*",
                    "—" if left is None else repr(left),
                    "—" if right is None else repr(right),
                )
            )
            continue
        for key in sorted(left.keys() | right.keys()):
            if key in left and key in right and repr(left[key]) == repr(right[key]):
                continue
            changes.append(
                LayoutChange(
                    "修改字段",
                    path,
                    str(right.get("sName", "")),
                    key,
                    repr(left[key]) if key in left else "（不存在）",
                    repr(right[key]) if key in right else "（不存在）",
                )
            )
    return changes


def referenced_staged_images(
    roots: list[dict], staged: dict[str, bytes]
) -> dict[str, bytes]:
    """与原写包策略一致：匹配任意字符串属性，未知原生字段不漏掉。"""
    texts: set[str] = set()
    stack: list = [roots]
    while stack:
        value = stack.pop()
        if isinstance(value, str):
            texts.add(value.replace("/", "\\").lower())
        elif isinstance(value, dict):
            stack.extend(value.values())
        elif isinstance(value, (list, tuple)):
            stack.extend(value)
    return {
        path: data
        for path, data in staged.items()
        if path.replace("/", "\\").lower() in texts
    }
