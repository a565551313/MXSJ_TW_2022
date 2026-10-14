"""「布局 ⇄ 脚本」联动索引的只读查询层（零 Qt）。

数据来自 `tools/script_link/build_script_index.py` 对 script.fls 的
静态字节码挖掘（随包 `data/script_index.json`）：哪个模块的哪个类
加载了哪个 .dlg、脚本按名取了哪些控件、代码现造按钮用的皮肤。
静态挖掘覆盖不了动态拼名/变量传参，结果只作编辑参考，不是运行时
事实；界面上引用时须注明「静态索引（推断）」。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

__all__ = [
    "LayoutLink",
    "ObjectRef",
    "ScriptIndex",
    "SkinRef",
    "get_default_index",
]


@dataclass(frozen=True)
class ObjectRef:
    """脚本按名取用一个控件的一次引用。"""

    module: str
    entry: int
    cls: str
    func: str
    anchor: bool  # 取后紧接着读位置：占位锚点（代码在原地另造控件）


@dataclass(frozen=True)
class SkinRef:
    """代码现造按钮的一次创建（皮肤/文字/消息号）。"""

    module: str
    entry: int
    cls: str
    func: str
    factory: str
    skin: str
    text: str
    msgid: int | None


@dataclass
class LayoutLink:
    """一个布局与脚本的全部静态关联。"""

    path: str
    modules: list[tuple[int, str]] = field(default_factory=list)
    objects: dict[str, list[ObjectRef]] = field(default_factory=dict)
    skins: dict[str, list[SkinRef]] = field(default_factory=dict)


def _normalize(path: str) -> str:
    return path.replace("\\", "/").strip().lstrip("/").lower()


class ScriptIndex:
    """联动索引：按布局路径查关联（路径归一后大小写不敏感）。"""

    def __init__(self, data: dict | None) -> None:
        self._data = data or {}
        self._modules: list[list] = self._data.get("modules", [])
        self._layouts: dict[str, dict] = {}
        for path, slot in (self._data.get("layouts") or {}).items():
            self._layouts[_normalize(path)] = slot
        self.stats: dict = self._data.get("stats", {})

    # -- 加载 ------------------------------------------------------
    @classmethod
    def load_default(cls) -> ScriptIndex:
        """读随包的 data/script_index.json；缺失时返回空索引。"""
        path = (Path(__file__).resolve().parent.parent
                / "data" / "script_index.json")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return cls(None)
        return cls(data)

    def __bool__(self) -> bool:
        return bool(self._layouts)

    @property
    def layout_paths(self) -> list[str]:
        return sorted(self._layouts)

    # -- 查询 ------------------------------------------------------
    def _module(self, index: int) -> tuple[int, str]:
        if 0 <= index < len(self._modules):
            entry, module = self._modules[index]
            return int(entry), str(module)
        return -1, ""

    def for_layout(self, path: str | None) -> LayoutLink | None:
        """按布局路径取关联；找不到返回 None。"""
        if not path:
            return None
        slot = self._layouts.get(_normalize(path))
        if slot is None:
            return None
        link = LayoutLink(path=_normalize(path))
        for index in slot.get("m", []):
            ref = self._module(int(index))
            if ref not in link.modules:
                link.modules.append(ref)
        for name, refs in (slot.get("o") or {}).items():
            link.objects[name] = [
                ObjectRef(module=self._module(int(r[0]))[1],
                          entry=self._module(int(r[0]))[0],
                          cls=str(r[1]), func=str(r[2]),
                          anchor=bool(r[3]))
                for r in refs
            ]
        for anchor, refs in (slot.get("s") or {}).items():
            link.skins[anchor] = [
                SkinRef(module=self._module(int(r[0]))[1],
                        entry=self._module(int(r[0]))[0],
                        cls=str(r[1]), func=str(r[2]),
                        factory=str(r[3]), skin=str(r[4]),
                        text=str(r[5]),
                        msgid=(int(r[6]) if len(r) > 6
                               and isinstance(r[6], int) else None))
                for r in refs
            ]
        return link

    def skin_bindings(self, path: str | None) -> dict[str, SkinRef]:
        """布局内「占位名 -> 代码皮肤」绑定（同名多处取第一条）。"""
        link = self.for_layout(path)
        if link is None:
            return {}
        return {name: refs[0] for name, refs in link.skins.items() if refs}

    def match_loose_path(self, fs_path: str | None) -> str | None:
        """散装 .dlg 的磁盘路径反查索引中的布局路径（后缀匹配）。"""
        if not fs_path:
            return None
        norm = _normalize(fs_path)
        if norm in self._layouts:
            return norm
        suffix = [p for p in self._layouts if norm.endswith("/" + p)]
        if suffix:
            return max(suffix, key=len)
        base = norm.rsplit("/", 1)[-1]
        same = [p for p in self._layouts if p.rsplit("/", 1)[-1] == base]
        return same[0] if len(same) == 1 else None


_DEFAULT: ScriptIndex | None = None


def get_default_index() -> ScriptIndex:
    """进程内单例的随包索引。"""
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = ScriptIndex.load_default()
    return _DEFAULT
