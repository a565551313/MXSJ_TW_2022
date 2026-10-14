"""只读静态布局诊断；不加载 Qt、不执行脚本、不推断运行时真值。"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING

from . import dlg_codec
from .script_index import LayoutLink

if TYPE_CHECKING:
    from .model import LayoutDocument, Widget


@dataclass(frozen=True)
class Diagnostic:
    severity: str
    code: str
    path: tuple[int, ...] | None
    field: str
    message: str


@dataclass(frozen=True)
class ReferenceImpact:
    name: str
    details: tuple[str, ...]


def reference_impacts(
    names: Iterable[str], link: LayoutLink | None
) -> list[ReferenceImpact]:
    """只报告索引中已知的取用/代码皮肤；空结果不代表没有动态引用。"""
    if link is None:
        return []
    result = []
    for name in sorted(set(names)):
        details = []
        for ref in link.objects.get(name, []):
            details.append(
                f"{ref.module} [entry {ref.entry}] "
                f"{ref.cls}.{ref.func} · "
                f"{'位置锚点' if ref.anchor else '按名取用'}"
            )
        for ref in link.skins.get(name, []):
            details.append(
                f"{ref.module} [entry {ref.entry}] "
                f"{ref.cls}.{ref.func} · 代码皮肤 {ref.skin}"
            )
        if details:
            result.append(ReferenceImpact(name, tuple(dict.fromkeys(details))))
    return result


def walk_paths(
    roots: list[Widget], parent: tuple[int, ...] = ()
) -> Iterator[tuple[tuple[int, ...], Widget]]:
    for index, widget in enumerate(roots):
        path = (*parent, index)
        yield path, widget
        yield from walk_paths(widget.children, path)


def widget_at_path(doc: LayoutDocument, path: tuple[int, ...]) -> Widget | None:
    nodes = doc.roots
    found = None
    for index in path:
        if index < 0 or index >= len(nodes):
            return None
        found = nodes[index]
        nodes = found.children
    return found


def _strings(value: object, key: str) -> Iterator[tuple[str, str]]:
    # Mirrors dlg_codec's field inheritance for strings in lists/tuples/dicts.
    if isinstance(value, str):
        yield key, value
    elif isinstance(value, dict):
        for field, item in value.items():
            yield from _strings(item, str(field))
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _strings(item, key)


def diagnose(
    doc: LayoutDocument,
    *,
    link: LayoutLink | None = None,
    resource_exists: Callable[[str], bool] | None = None,
    staged_paths: Iterable[str] = (),
) -> list[Diagnostic]:
    """零尺寸可能由精灵/原生样式决定；越界、缺图与脚本均为静态提示。"""
    issues = []
    entries = list(walk_paths(doc.roots))
    names: dict[str, list[tuple[int, ...]]] = {}
    staged = {p.replace("\\", "/").lower() for p in staged_paths}
    for path, widget in entries:
        if widget.name:
            names.setdefault(widget.name, []).append(path)
        for key, value in widget.props.items():
            for field, text in _strings(value, key):
                codec = (
                    "big5"
                    if field in dlg_codec._BIG5_TEXT_KEYS
                    else "gbk"
                    if field in dlg_codec._GBK_PATH_KEYS
                    else "gb18030"
                )
                try:
                    # Preserve undecodable source bytes just as the codec does.
                    text.encode(codec, "surrogateescape")
                except UnicodeEncodeError:
                    issues.append(
                        Diagnostic(
                            "错误",
                            "ENCODING",
                            path,
                            key,
                            f"{field} 含无法按 {codec.upper()} 编码的字符；"
                            "GB18030 回退不代表原生引擎支持，请修改后再保存。",
                        )
                    )
        for key in ("iX", "iY", "iWidth", "iHeight"):
            value = widget.props.get(key)
            if value is None:
                continue
            if not isinstance(value, int) or isinstance(value, bool):
                issues.append(
                    Diagnostic(
                        "警告",
                        "GEOMETRY_TYPE",
                        path,
                        key,
                        f"{key} 不是原生整数尺寸/坐标。",
                    )
                )
            elif key in ("iWidth", "iHeight"):
                if value < 0:
                    issues.append(
                        Diagnostic(
                            "警告",
                            "NEGATIVE_SIZE",
                            path,
                            key,
                            f"{key} 为负数，请核对原生尺寸。",
                        )
                    )
                elif value == 0:
                    issues.append(
                        Diagnostic(
                            "提示",
                            "AUTO_SIZE",
                            path,
                            key,
                            "零尺寸可能由图片/样式或脚本决定，不直接判作损坏。",
                        )
                    )
        parent = widget.parent
        if parent and all(
            isinstance(node.props.get(key), int)
            and not isinstance(node.props.get(key), bool)
            and node.props[key] > 0
            for node in (widget, parent)
            for key in ("iWidth", "iHeight")
        ):
            if (
                widget.x < 0
                or widget.y < 0
                or widget.x + widget.width > parent.width
                or widget.y + widget.height > parent.height
            ):
                issues.append(
                    Diagnostic(
                        "警告",
                        "OUTSIDE_PARENT",
                        path,
                        "iX/iY/iWidth/iHeight",
                        "静态矩形超出父控件；可能是有意重叠/滚动/脚本定位，"
                        "不是原生裁剪或屏幕边界判定。",
                    )
                )
        for key in dlg_codec._GBK_PATH_KEYS:
            value = widget.props.get(key)
            if not isinstance(value, str) or not value:
                continue
            normalized = value.replace("\\", "/").lower()
            if normalized in staged:
                issues.append(
                    Diagnostic(
                        "提示",
                        "STAGED_RESOURCE",
                        path,
                        key,
                        "当前引用待入包资源：保存新包时一并写入，"
                        "散装 .dlg 不会嵌入图片。",
                    )
                )
            elif resource_exists is not None and not resource_exists(value):
                issues.append(
                    Diagnostic(
                        "警告",
                        "RESOURCE_MISSING",
                        path,
                        key,
                        f"已挂载资源中未找到：{value}；可能在尚未挂载的包/热更新中。",
                    )
                )
    for name, paths in names.items():
        if len(paths) > 1:
            for path in paths:
                issues.append(
                    Diagnostic(
                        "警告",
                        "DUPLICATE_NAME",
                        path,
                        "sName",
                        f"控件名 {name!r} 重复 {len(paths)} 次；"
                        "脚本按名取用可能产生歧义。",
                    )
                )
    if resource_exists is None:
        issues.append(
            Diagnostic(
                "提示",
                "RESOURCES_NOT_CHECKED",
                None,
                "",
                "未挂载资源来源：没有检查缺图/缺音，不能判为完整。",
            )
        )
    if link:
        for name in sorted(set(link.objects) | set(link.skins)):
            if name not in names:
                issues.append(
                    Diagnostic(
                        "警告",
                        "SCRIPT_REFERENCE_MISSING",
                        None,
                        "sName",
                        f"索引引用 {name!r}，当前树中未找到；可能由脚本动态创建。",
                    )
                )
    issues.append(
        Diagnostic(
            "提示",
            "STATIC_ONLY",
            None,
            "",
            "脚本索引为只读静态基线，可能漏动态拼名或版本变化；"
            "未发现引用不等于无引用。布局诊断不能替代游戏实机验收。",
        )
    )
    return issues
