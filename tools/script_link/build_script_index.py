#!/usr/bin/env python3
"""生成「布局 ⇄ 脚本」联动索引（UI 编辑器脚本联动的数据来源）。

对 `data/script.fls` 全部条目做基线转译（复用
`tools/decompiler/batch_decompile.py` 的 Py2.5 转译器，不跑反编译），
再解析标准 Python 2.5 marshal 与字节码，静态挖出三类关联：

- 哪个模块的哪个类加载了哪个 ``.dlg``（字符串常量）；
- 脚本按名字取了哪些控件（``GetObject('name')`` 调用模式），
  其中哪些是读位置的占位锚点（紧接着 ``.GetPos()``）；
- 代码现造按钮用的皮肤（``*Button*(self, 'skin.igs', x, y, '文字', 号)``
  调用模式），并把皮肤配给同函数内最近的占位锚点。

产物是 JSON，写进 `ui_editor/src/ui_editor/data/script_index.json`，
编辑器运行时只查表，不碰解密与反编译。静态分析有硬边界：动态拼
的名字、变量传参的路径挖不到；索引里 `stats` 会如实记录覆盖率。

用法：
    python3 tools/script_link/build_script_index.py [--workers 8]
        [--limit N] [--out PATH] [--script-fls PATH]
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import re
import struct
import sys
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "decompiler"))

import batch_decompile as bd  # noqa: E402

# ---------------------------------------------------------------------------
# Python 2.5 marshal 解析（只有 interned 字符串进引用表，与 CPython 2.5 一致）
# ---------------------------------------------------------------------------


class MarshalError(Exception):
    """marshal 流结构非法。"""


class Code:
    """一个 Py2.5 code object（只保留挖掘需要的字段）。"""

    __slots__ = ("name", "consts", "names", "code", "children")

    def __init__(self) -> None:
        self.name = b""
        self.consts: tuple = ()
        self.names: tuple = ()
        self.code = b""
        self.children: list[Code] = []


class _Reader:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self._pos = 0
        self._refs: list = []

    def _byte(self) -> int:
        byte = self._data[self._pos]
        self._pos += 1
        return byte

    def _peek(self) -> str:
        return chr(self._data[self._pos] & 0x7F)

    def _take(self, count: int) -> bytes:
        chunk = self._data[self._pos:self._pos + count]
        self._pos += count
        return chunk

    def _i32(self) -> int:
        return struct.unpack("<i", self._take(4))[0]

    def object(self):  # noqa: C901 - marshal 类型分发，拆散反而难读
        kind = chr(self._byte() & 0x7F)
        slot = None
        if kind == "t":  # 只有 interned 字符串进引用表（CPython 2.5 语义）
            slot = len(self._refs)
            self._refs.append(None)
        if kind == "N":
            value = None
        elif kind == "F":
            value = False
        elif kind == "T":
            value = True
        elif kind == "S":
            value = StopIteration
        elif kind == ".":
            value = Ellipsis
        elif kind == "0":
            value = None
        elif kind == "i":
            value = self._i32()
        elif kind == "I":
            value = struct.unpack("<q", self._take(8))[0]
        elif kind == "l":
            count = self._i32()
            negative = count < 0
            value = 0
            for i in range(abs(count)):
                value |= struct.unpack("<H", self._take(2))[0] << (i * 15)
            value = -value if negative else value
        elif kind == "f":
            value = float(self._take(self._byte()).decode("ascii"))
        elif kind == "g":
            value = struct.unpack("<d", self._take(8))[0]
        elif kind in ("s", "t", "u"):
            value = self._take(self._i32())  # 原始字节，解码留给使用方
        elif kind == "R":
            index = self._i32()
            if not 0 <= index < len(self._refs):
                raise MarshalError(f"引用越界 {index}")
            value = self._refs[index]
        elif kind == "(":
            value = tuple(self.object() for _ in range(self._i32()))
        elif kind == "[":
            value = [self.object() for _ in range(self._i32())]
        elif kind == "{":
            value = {}
            while True:
                if self._peek() == "0":
                    self._byte()
                    break
                key = self.object()
                value[key] = self.object()
        elif kind == "c":
            value = self._code()
        else:
            raise MarshalError(f"未知 marshal 类型 {kind!r} @ {self._pos - 1}")
        if slot is not None:
            self._refs[slot] = value
        return value

    def _code(self) -> Code:
        code = Code()
        self._i32()  # argcount
        self._i32()  # nlocals
        self._i32()  # stacksize
        self._i32()  # flags
        code.code = self.object()
        code.consts = self.object()
        code.names = self.object()
        self.object()  # varnames
        self.object()  # freevars
        self.object()  # cellvars
        self.object()  # filename
        code.name = self.object()
        self._i32()  # firstlineno
        self.object()  # lnotab
        code.children = [c for c in code.consts if isinstance(c, Code)]
        return code


def parse_pyc(pyc: bytes) -> Code:
    """解析标准 Py2.5 .pyc（8 字节头 + marshal 根 code object）。"""
    if len(pyc) < 9 or pyc[4:8] == b"":
        raise MarshalError("pyc 太短")
    return _Reader(pyc[8:]).object()


def decode_text(raw) -> str:
    """脚本字节串多为 Big5（繁体域），GBK 兜底，最后 latin1 保底。"""
    if isinstance(raw, str):
        return raw
    if not isinstance(raw, (bytes, bytearray)):
        return ""
    for encoding in ("big5", "gbk"):
        try:
            return bytes(raw).decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return bytes(raw).decode("latin1")


# ---------------------------------------------------------------------------
# 字节码模式挖掘（标准 Py2.5 opcode；只解释关心的几条，步进靠 HAVE_ARGUMENT）
# ---------------------------------------------------------------------------

_HAVE_ARGUMENT = 90
_LOAD_CONST = 100
_LOAD_NAME = 101
_LOAD_ATTR = 105
_LOAD_GLOBAL = 116
_CALL_FUNCTION = 131
_LOADERS = (_LOAD_NAME, _LOAD_ATTR, _LOAD_GLOBAL)
_SKIN_SUFFIXES = (".igs", ".png", ".jpg", ".bmp")
_FACTORY_RE = re.compile(r"(Button|Btn)$")


def iter_ops(code: Code):
    """产出 (offset, opcode, arg|None)；未知 opcode 按有无参数步进。"""
    bytecode = code.code if isinstance(code.code, bytes) else b""
    pos = 0
    while pos < len(bytecode):
        op = bytecode[pos]
        if op >= _HAVE_ARGUMENT:
            if pos + 2 >= len(bytecode):
                return
            yield pos, op, bytecode[pos + 1] | (bytecode[pos + 2] << 8)
            pos += 3
        else:
            yield pos, op, None
            pos += 1


def walk_codes(code: Code, path: tuple[str, ...] = ()):
    """深度优先遍历 code 树，产出 (限定路径, code)。"""
    here = path + (decode_text(code.name),)
    yield here, code
    for child in code.children:
        yield from walk_codes(child, here)


def _const_str(code: Code, index):
    if index is None or index >= len(code.consts):
        return None
    value = code.consts[index]
    return decode_text(value) if isinstance(value, (bytes, bytearray)) else None


def _name_str(code: Code, index) -> str:
    if index is None or index >= len(code.names):
        return ""
    return decode_text(code.names[index])


class CodeFacts:
    """一个 code object 内挖到的关联事实。"""

    def __init__(self) -> None:
        self.dlgs: list[str] = []
        self.objects: list[dict] = []  # {name, anchor}
        self.skins: list[dict] = []    # {factory, skin, text, msgid, anchor}


def mine_code(code: Code) -> CodeFacts:
    facts = CodeFacts()
    ops = list(iter_ops(code))
    last_anchor: str | None = None
    for pos, (_offset, op, arg) in enumerate(ops):
        if op == _LOAD_CONST:
            text = _const_str(code, arg)
            if text and text.lower().endswith(".dlg"):
                facts.dlgs.append(text.replace("\\", "/"))
            continue
        if op not in _LOADERS or arg is None:
            continue
        attr = _name_str(code, arg)
        if attr == "GetObject":
            target = None
            for _off2, op2, arg2 in ops[pos + 1:pos + 6]:
                if op2 == _LOAD_CONST:
                    target = _const_str(code, arg2)
                    break
                if op2 == _CALL_FUNCTION:
                    break
            if target:
                is_anchor = any(
                    op3 in _LOADERS and _name_str(code, arg3) == "GetPos"
                    for _o, op3, arg3 in ops[pos + 1:pos + 10])
                facts.objects.append(
                    {"name": target, "anchor": is_anchor})
                if is_anchor:
                    last_anchor = target
        elif _FACTORY_RE.search(attr):
            skin = None
            text = None
            msgid = None
            for _off2, op2, arg2 in ops[pos + 1:pos + 16]:
                if op2 == _CALL_FUNCTION:
                    break
                if op2 != _LOAD_CONST:
                    continue
                value = code.consts[arg2] if arg2 is not None \
                    and arg2 < len(code.consts) else None
                if isinstance(value, (bytes, bytearray)):
                    string = decode_text(value)
                    if string.lower().endswith(_SKIN_SUFFIXES) \
                            and skin is None:
                        skin = string.replace("\\", "/")
                    elif string and text is None:
                        text = string
                elif isinstance(value, int) and not isinstance(value, bool):
                    msgid = value
            if skin is not None:
                facts.skins.append({
                    "factory": attr, "skin": skin, "text": text or "",
                    "msgid": msgid, "anchor": last_anchor,
                })
    return facts


# ---------------------------------------------------------------------------
# 模块级聚合：类的各方法挖到的关联归给该类加载的布局
# ---------------------------------------------------------------------------


def mine_module(entry: int, module: str, pyc: bytes) -> dict:
    """挖一个模块，产出 {entry, module, layouts: {dlg: {...}}}。"""
    return _aggregate(entry, module, parse_pyc(pyc))


def _aggregate(entry: int, module: str, root: Code) -> dict:
    per_code: list[tuple[tuple[str, ...], CodeFacts]] = []
    class_dlgs: dict[str, list[str]] = {}
    module_dlgs: list[str] = []
    for path, code in walk_codes(root):
        facts = mine_code(code)
        per_code.append((path, facts))
        for dlg in facts.dlgs:
            if dlg not in module_dlgs:
                module_dlgs.append(dlg)
            if len(path) >= 2:
                owned = class_dlgs.setdefault(path[1], [])
                if dlg not in owned:
                    owned.append(dlg)
    layouts: dict[str, dict] = {}

    def record(dlg: str) -> dict:
        return layouts.setdefault(
            dlg, {"modules": [], "objects": {}, "skins": {}})

    for path, facts in per_code:
        if not (facts.objects or facts.skins):
            continue
        owner_class = path[1] if len(path) >= 3 else ""
        dlgs = class_dlgs.get(owner_class) or module_dlgs
        func = path[-1] if path else ""
        for dlg in dlgs:
            slot = record(dlg)
            ref = {"entry": entry, "module": module,
                   "class": owner_class, "func": func}
            if ref not in slot["modules"]:
                slot["modules"].append(ref)
            for obj in facts.objects:
                slot["objects"].setdefault(obj["name"], []).append(
                    {**ref, "anchor": obj["anchor"]})
            for skin in facts.skins:
                if skin["anchor"]:
                    slot["skins"].setdefault(skin["anchor"], []).append(
                        {**ref, **skin})
    # 只被引用、没有任何取件/皮肤的布局也记下引用关系
    for path, facts in per_code:
        owner_class = path[1] if len(path) >= 2 else ""
        for dlg in facts.dlgs:
            slot = record(dlg)
            ref = {"entry": entry, "module": module,
                   "class": owner_class, "func": path[-1] if path else ""}
            if ref not in slot["modules"]:
                slot["modules"].append(ref)
    return {"entry": entry, "module": module, "layouts": layouts}


# ---------------------------------------------------------------------------
# script.fls 读取与批量驱动
# ---------------------------------------------------------------------------


def read_entries(script_fls: Path):
    """按 0SLF 目录读出 (idx, entry_id, 解压后字节) 列表。"""
    arch = script_fls.read_bytes()
    entry_count = struct.unpack_from("<I", arch, 4)[0]
    index_off = struct.unpack_from("<I", arch, 8)[0]
    for idx in range(entry_count):
        entry_id, r1, r2, r3 = struct.unpack_from(
            "<IIII", arch, index_off + idx * 16)
        length = (((r1 * entry_id + 0x0DF25E) & 0xFFFFFFFF) ^ r2) & 0xFFFFFFFF
        offset = (((r2 * idx * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF)
                  ^ r3) & 0xFFFFFFFF
        try:
            yield idx, entry_id, zlib.decompress(arch[offset:offset + length])
        except zlib.error:
            yield idx, entry_id, None


def _mine_task(task):
    idx, entry_id, exp, keys, bounds = task
    try:
        if exp is None:
            return {"entry": idx, "module": "", "layouts": {},
                    "error": "zlib 解压失败"}
        # 只走基线转译：边界修复依赖反编译器验收，不在挖掘管线里做
        dec = bd._decode_segments(exp, keys, bounds)
        pyc, fname = bd._transpile_once(dec, exp, keys, bounds)
        if pyc is None:
            return {"entry": idx, "module": "", "layouts": {},
                    "error": "基线转译失败（未做边界修复）"}
        module = (fname or f"script/unknown/entry_{idx:04d}.py")
        return mine_module(idx, module.replace("\\", "/"), pyc)
    except Exception as exc:  # 单条失败不拖垮全批，如实记录
        return {"entry": idx, "module": "", "layouts": {},
                "error": f"{type(exc).__name__}: {exc}"}


def build_index(script_fls: Path, keys_db: dict, workers: int,
                limit: int | None) -> dict:
    tasks = []
    entries = list(read_entries(script_fls))
    for idx, entry_id, exp in entries:
        info = keys_db.get(str(idx)) or {}
        tasks.append((idx, entry_id, exp,
                      info.get("keys", []), info.get("bounds", [])))
        if limit and len(tasks) >= limit:
            break
    if workers > 1:
        with mp.Pool(workers) as pool:
            results = pool.map(_mine_task, tasks, chunksize=16)
    else:
        results = [_mine_task(task) for task in tasks]
    layouts: dict[str, dict] = {}
    failed = []
    mined = 0
    for result in results:
        if result.get("error"):
            failed.append({"entry": result["entry"],
                           "error": result["error"]})
            continue
        mined += 1
        for dlg, slot in result["layouts"].items():
            merged = layouts.setdefault(
                dlg, {"modules": [], "objects": {}, "skins": {}})
            for ref in slot["modules"]:
                if ref not in merged["modules"]:
                    merged["modules"].append(ref)
            for name, refs in slot["objects"].items():
                merged["objects"].setdefault(name, []).extend(refs)
            for anchor, refs in slot["skins"].items():
                merged["skins"].setdefault(anchor, []).extend(refs)
    total = len(tasks)
    compact_layouts, modules = _compact(layouts)
    return {
        "version": 1,
        "stats": {
            "modules_total": total,
            "modules_mined": mined,
            "modules_failed": len(failed),
            "layouts_linked": len(layouts),
            "note": "静态字节码挖掘：动态拼名/变量传参挖不到；"
                    "基线转译失败的条目未做边界修复（清单见 failed）。",
            "failed": failed[:200],
        },
        "modules": modules,
        "layouts": compact_layouts,
    }


def _compact(layouts: dict[str, dict]) -> tuple[dict, list]:
    """紧凑编码：模块去重成全局表，引用只存模块序号（控制产物体积）。"""
    module_ids: dict[tuple[int, str], int] = {}
    modules: list[list] = []

    def mid(ref: dict) -> int:
        key = (ref["entry"], ref["module"])
        if key not in module_ids:
            module_ids[key] = len(modules)
            modules.append([ref["entry"], ref["module"]])
        return module_ids[key]

    compact = {}
    for dlg, slot in layouts.items():
        seen: list[int] = []
        for ref in slot["modules"]:
            index = mid(ref)
            if index not in seen:
                seen.append(index)
        objects = {
            name: [[mid(r), r["class"], r["func"], 1 if r["anchor"] else 0]
                   for r in refs]
            for name, refs in slot["objects"].items()
        }
        skins = {
            anchor: [[mid(r), r["class"], r["func"], r["factory"],
                      r["skin"], r["text"], r["msgid"]] for r in refs]
            for anchor, refs in slot["skins"].items()
        }
        out = {"m": seen}
        if objects:
            out["o"] = objects
        if skins:
            out["s"] = skins
        compact[dlg] = out
    return compact, modules


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script-fls", type=Path,
                        default=REPO_ROOT / "data" / "script.fls")
    parser.add_argument("--keys", type=Path,
                        default=REPO_ROOT / "tools" / "decompiler"
                        / "script_fls_keys.json")
    parser.add_argument("--out", type=Path,
                        default=REPO_ROOT / "ui_editor" / "src" / "ui_editor"
                        / "data" / "script_index.json")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    keys_db = json.loads(args.keys.read_text(encoding="utf-8"))
    index = build_index(args.script_fls, keys_db, args.workers, args.limit)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":"),
                   sort_keys=True),
        encoding="utf-8")
    stats = index["stats"]
    print(f"模块 {stats['modules_mined']}/{stats['modules_total']} 挖完，"
          f"失败 {stats['modules_failed']}；关联布局 "
          f"{stats['layouts_linked']} 个 → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
