"""B 包全量目录结构提取（只读，不执行游戏脚本，不反编译）。

方法：复用 script_editor 已审计的容器/密文/marshal 结构读取代码，
直接从两固定原包的 marshal 码对象树读取 co_filename、co_name、
co_varnames 与头字段，并用父码对象标准字节码中的
LOAD_CONST/MAKE_FUNCTION/BUILD_CLASS 序列区分 class 与 function。
不导入、不执行任何游戏模块；不读取 entry 1288 的负载字节。

旧 catalog（server/docs/catalog/script_entries.jsonl）仅作两件事：
1) 结构读取失败时的 historical 路径回退（函数一律留空）；含控制字符的
   回退值被拒绝，原值以 JSON 转义写进回执 script_failures[].fallback_rejected；
2) 20 条样板回归的对照统计。其函数名不写入本轮结果。

签名口径（N1 修订，依据 CPython v2.5.6 Lib/inspect.py getargs/formatargspec）：
前 co_argcount 个 co_varnames 为位置形参，CO_VARARGS 时下一个为 *名，
CO_VARKEYWORDS 时再下一个为 **名；Python 2 没有仅关键字形参，不输出裸 *。
任一形参名不是 Python 2 标识符时签名记 null：.N 为编译器内部槽（匿名 tuple
形参 / 生成器表达式迭代器），其余多为接缝乱码；原渲染只作审阅线索写进回执
signature_audit.rejected，不猜 tuple 形状、不从旧 catalog 补。

隔离要求：本脚本按自身位置推出 ROOT（上两级），--sample 写
ROOT/script_manual/inventory/sample_regression.json，--full 写同目录的
modules.jsonl 与 B_extraction_receipt.json。复现时先把它复制到仓库外的隔离树，
inventory 里只放冻结 20 种子（cc5c1ba 的 modules.jsonl），不放旧回归报告，
跑完再把三份产物拷回；不要在含其他未保存工作的目录里直接运行。

用法（隔离树根目录）：
    python3 script_manual/inventory/extract_inventory.py --sample
    python3 script_manual/inventory/extract_inventory.py --full
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "script_editor" / "src"))

from script_editor.core.archives import flsdata  # noqa: E402
from script_editor.core.archives.document import ArchiveDocument  # noqa: E402
from script_editor.core.services.module_paths import (  # noqa: E402
    display_module_path,
)
from script_editor.core.vm.compression import inflate  # noqa: E402
from script_editor.core.vm.marshal_tree import Code, Group  # noqa: E402
from script_editor.core.vm.marshal_tree import parse as marshal_parse  # noqa: E402
from script_editor.core.vm.py25.codec import map_code as py25_to_standard  # noqa: E402
from script_editor.core.vm.py25.keys import KeyProfile, read_catalog  # noqa: E402
from script_editor.core.vm.py27.codec import decode as py27_to_standard  # noqa: E402

SCRIPT_SHA = "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72"
DATA_SHA = "5f96bdb23d4555c8014ac4a4a65819f48a3251b95a8cc94dff09ee7e2cc0a12c"
CATALOG_SHA = "43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb"
EXCLUDED_SCRIPT = {1288}
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SPECIAL_NAMES = {"<lambda>", "<module>"}

# CPython 2 Include/code.h；Lib/inspect.py getargs 按此布局读 co_varnames。
CO_VARARGS = 0x04
CO_VARKEYWORDS = 0x08
# 形参名判定一律 fullmatch（$ 会放过结尾换行）。Python 2 标识符仅 ASCII。
PY2_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# symtable.c symtable_implicit_arg 生成的 ".%d" 内部槽名。
INTERNAL_SLOT = re.compile(r"\.[0-9]+")
SIGNATURE_TOKEN = re.compile(r"(\*\*|\*)?([A-Za-z_][A-Za-z0-9_]*)")
SIGNATURE_REFERENCES = [
    "CPython v2.5.6 Include/code.h:31-36 CO_VARARGS=0x0004, CO_VARKEYWORDS=0x0008",
    "CPython v2.5.6 Lib/inspect.py:672-728 getargs: varargs=co_varnames[nargs] if "
    "CO_VARARGS, then varkw; :689 names starting with '' or '.' are anonymous "
    "tuple arguments",
    "CPython v2.5.6 Lib/inspect.py:769-793 formatargspec: '*'+varargs only when "
    "present, '**'+varkw only when present; no bare '*'",
    "CPython v2.5.6 Python/symtable.c:1216-1218 '.%d' implicit args; :1243-1246 "
    "tuple parameter i; :1412-1413 generator expression iterator '.0'",
]

OLD_CATALOG = "server/docs/catalog/script_entries.jsonl"
# 任务卡指定的真实 20 种子：cc5c1ba 的 modules.jsonl（20 行 historical）。
FROZEN_SEED_COMMIT = "cc5c1bad7a806078794eca1ab7482230a18ef9d5"
FROZEN_SEED_SHA = "de75ec619cf61e8a71098bd74f746081547b1423c6d28bd8595039f6a8e3483b"

TOOL_FILES = [
    "script_editor/src/script_editor/core/archives/document.py",
    "script_editor/src/script_editor/core/archives/fls0slf.py",
    "script_editor/src/script_editor/core/archives/flsdata.py",
    "script_editor/src/script_editor/core/archives/readers.py",
    "script_editor/src/script_editor/core/services/module_paths.py",
    "script_editor/src/script_editor/core/vm/compression.py",
    "script_editor/src/script_editor/core/vm/marshal_tree.py",
    "script_editor/src/script_editor/core/vm/tables.py",
    "script_editor/src/script_editor/core/vm/py25/codec.py",
    "script_editor/src/script_editor/core/vm/py25/keys.py",
    "script_editor/src/script_editor/core/vm/py27/codec.py",
    "script_editor/src/script_editor/core/vm/py27/forward.py",
    "script_editor/src/script_editor/core/vm/py27/inverse.py",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_text(raw: bytes | None) -> str:
    if raw is None:
        return ""
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("ascii", errors="backslashreplace")


class AuditedArchive(ArchiveDocument):
    """只读审计包装：每次定点负载读取先登记再委托；策略排除条目在读前拒绝。

    fingerprint() 首次调用会按 1MiB 块顺序读完整个文件做 SHA-256，必然经过
    排除条目所在区间的字节；那只是整包指纹，不解压、不解密、不解析，回执
    据实区分「定点 read_stored」与「整包哈希」。
    """

    def __init__(self, path: Path, *, excluded: frozenset[int]):
        super().__init__(path)
        self.excluded = excluded
        self.read_stored_calls: Counter = Counter()
        self.fingerprint_calls = 0
        self.fingerprint_full_passes = 0

    def read_stored(self, index: int) -> bytes:
        self.read_stored_calls[index] += 1  # 先登记，再判断，杜绝漏记
        if index in self.excluded:
            raise PermissionError(f"policy-excluded entry {index}: read refused")
        return super().read_stored(index)

    def fingerprint(self) -> str:
        self.fingerprint_calls += 1
        if self._fingerprint is None:
            self.fingerprint_full_passes += 1
        return super().fingerprint()

    def read_summary(self) -> dict:
        excluded_spans = []
        for index in sorted(self.excluded):
            span = self.index.spans[index]  # 目录元数据，不是负载
            if self.kind == "0slf":
                offset, length = span.offset, span.length
            else:
                offset, length = span.data_offset, span.csize
            excluded_spans.append(
                {"entry_index": index, "offset": offset, "length": length}
            )
        return {
            "read_stored_calls": sum(self.read_stored_calls.values()),
            "distinct_entries_read": len(self.read_stored_calls),
            "entries_in_archive": len(self.entries),
            "excluded_entries": sorted(self.excluded),
            "excluded_read_stored_calls": sum(
                self.read_stored_calls[index] for index in self.excluded
            ),
            "excluded_directory_spans": excluded_spans,
            "fingerprint_calls": self.fingerprint_calls,
            "fingerprint_full_file_passes": self.fingerprint_full_passes,
            "archive_bytes_hashed_per_pass": self.reader.size,
            "note": "read_stored is the only per-entry payload read; whole-file "
            "SHA-256 fingerprinting reads every byte (including excluded spans) "
            "only to hash it",
        }


def walk_standard(code: bytes) -> list[tuple[int, int, int | None]]:
    """把标准 Python2 字节码线性拆为 (偏移, 操作码, 参数)。"""
    ops: list[tuple[int, int, int | None]] = []
    pos = 0
    while pos < len(code):
        op = code[pos]
        if op >= 90:
            if pos + 2 >= len(code):
                raise ValueError("truncated standard bytecode")
            ops.append((pos, op, code[pos + 1] | (code[pos + 2] << 8)))
            pos += 3
        else:
            ops.append((pos, op, None))
            pos += 1
    return ops


def classify_children(parent: Code, vm: str, counter: Counter) -> dict[int, str] | None:
    """用父码对象字节码判定每个子码对象是 class 还是 function。

    判定只依赖已审计的原生->标准操作码转换；父字节码不可解时返回
    None，调用方改用码对象头标志回退，并计数登记，不静默猜测。
    """
    try:
        if vm == "py25":
            standard = py25_to_standard(parent.code, inverse=True)
        else:
            standard = parent.code  # data 侧传入前已整包转标准码
        ops = walk_standard(standard)
    except Exception:
        counter["parent_bytecode_undecodable"] += 1
        return None
    consts = (
        parent.fields[0].items if isinstance(parent.fields[0], Group) else ()
    )
    result: dict[int, str] = {}
    for at, (_pos, op, arg) in enumerate(ops):
        if op != 100 or arg is None or arg >= len(consts):
            continue
        child = consts[arg]
        if not isinstance(child, Code):
            continue
        made = None
        for nxt in range(at + 1, min(at + 9, len(ops))):
            if ops[nxt][1] in (132, 134):  # MAKE_FUNCTION / MAKE_CLOSURE
                made = nxt
                break
            nxt_arg = ops[nxt][2]
            if (
                ops[nxt][1] == 100
                and nxt_arg is not None
                and nxt_arg < len(consts)
                and isinstance(consts[nxt_arg], Code)
            ):
                break
        if made is None:
            continue
        kind = "function"
        for nxt in range(made + 1, min(made + 6, len(ops))):
            if ops[nxt][1] == 89:  # BUILD_CLASS
                kind = "class"
                break
            if ops[nxt][1] in (90, 91, 92, 95, 125, 126, 127):
                break
        result[id(child)] = kind
    return result


def signature_parts(node: Code) -> list[tuple[str, str, bytes]] | None:
    """按 CPython 2 co_varnames 布局取形参 [(前缀, 文本, 原字节)]；元数据不一致回 None。

    前 co_argcount 个是位置形参；CO_VARARGS 时下一个是 *名，CO_VARKEYWORDS
    时再下一个是 **名（inspect.getargs）。只有 **名 时直接接在位置形参后，
    不存在裸 *。默认值对象不渲染，带默认值的形参仍以裸名出现。
    """
    argcount, _nlocals, _stack, flags = struct.unpack("<iiii", node.header)
    varnames_node = node.fields[2]
    if not isinstance(varnames_node, Group):
        return None
    raw_names = [
        item.value if isinstance(item.value, bytes) else b""
        for item in varnames_node.items
    ]
    if argcount < 0 or len(raw_names) < argcount:
        return None
    parts = [("", decode_text(raw), raw) for raw in raw_names[:argcount]]
    cursor = argcount
    for flag, prefix in ((CO_VARARGS, "*"), (CO_VARKEYWORDS, "**")):
        if flags & flag:
            if cursor >= len(raw_names):
                return None
            raw = raw_names[cursor]
            parts.append((prefix, decode_text(raw), raw))
            cursor += 1
    return parts


def render_signature(parts: list[tuple[str, str, bytes]]) -> str:
    return "(" + ", ".join(prefix + text for prefix, text, _raw in parts) + ")"


@dataclass(frozen=True)
class SignatureCheck:
    """单个码对象的签名判定；rejected 时 raw 只是审阅线索，不是源码签名。"""

    status: str  # confirmed / unavailable / rejected
    signature: str | None = None
    raw: str | None = None
    reason: str | None = None
    slot_names: tuple[str, ...] = ()
    non_identifier: tuple[tuple[str, str], ...] = ()  # (文本, 原字节hex)
    kwargs_only: bool = False


def check_signature(node: Code) -> SignatureCheck:
    parts = signature_parts(node)
    if parts is None:
        return SignatureCheck("unavailable")
    raw = render_signature(parts)
    slots = tuple(text for _p, text, _r in parts if INTERNAL_SLOT.fullmatch(text))
    bad = tuple(
        (text, data.hex())
        for _p, text, data in parts
        if not INTERNAL_SLOT.fullmatch(text) and not PY2_IDENTIFIER.fullmatch(text)
    )
    if slots or bad:
        reason = "compiler_internal_slot" if slots else "non_identifier_parameter"
        return SignatureCheck("rejected", None, raw, reason, slots, bad)
    prefixes = {prefix for prefix, _t, _r in parts}
    return SignatureCheck(
        "confirmed", raw, raw, kwargs_only="**" in prefixes and "*" not in prefixes
    )


def count_signature(check: SignatureCheck, counter: Counter) -> None:
    if check.status == "unavailable":
        counter["signature_unavailable"] += 1
    elif check.status == "rejected":
        counter[f"signature_rejected_{check.reason}"] += 1
    elif check.kwargs_only:
        counter["signature_kwargs_only"] += 1


def signature_of(node: Code, counter: Counter) -> str | None:
    """可确认签名；元数据不足或形参名不可确认时返回 None（见 check_signature）。"""
    check = check_signature(node)
    count_signature(check, counter)
    return check.signature


def signature_is_wellformed(signature: str) -> bool:
    """Python 2 形参表外形：标识符…, 可选 *名, 可选 **名；没有裸 *、内部槽或乱码。"""
    if not (signature.startswith("(") and signature.endswith(")")):
        return False
    inner = signature[1:-1]
    if not inner:
        return True
    stage = 0  # 0=位置形参, 1=已见 *名, 2=已见 **名
    for token in inner.split(", "):
        match = SIGNATURE_TOKEN.fullmatch(token)
        if match is None:
            return False
        want = {None: 0, "*": 1, "**": 2}[match.group(1)]
        if want < stage or (want == stage and want != 0):
            return False
        stage = want
    return True


def extract_functions(
    root: Code, vm: str, counter: Counter, audit_sink: list | None = None
) -> list[dict]:
    """先序遍历码对象树（不含根 <module>），生成库存函数元数据。

    audit_sink 收集 (限定名, kind, SignatureCheck)：被拒签名与仅 **名 签名，
    供回执逐条列出；函数记录本身无论签名是否可确认都保留。
    """
    records: list[dict] = []

    def visit(node: Code, qualified: str, parent_kind: str) -> None:
        kinds = classify_children(node, vm, counter)
        consts = node.fields[0].items if isinstance(node.fields[0], Group) else ()
        for child in consts:
            if not isinstance(child, Code):
                continue
            raw_name = decode_text(child.fields[6].value)
            name = raw_name if raw_name else "<unnamed>"
            if name not in SPECIAL_NAMES and not IDENT.match(name):
                counter["suspect_names"] += 1
            child_qualified = name if qualified == "<module>" else f"{qualified}.{name}"
            if kinds is not None and id(child) in kinds:
                kind = kinds[id(child)]
            else:
                # 回退信号：类体码对象未优化且无形参；其余按函数处理。
                argcount, _n, _s, flags = struct.unpack("<iiii", child.header)
                kind = (
                    "class"
                    if (flags & 1) == 0 and argcount == 0
                    else "function"
                )
                counter["kind_fallback"] += 1
            if kind == "function" and parent_kind == "class":
                kind = "method"
            signature = None
            if kind != "class":
                check = check_signature(child)
                count_signature(check, counter)
                signature = check.signature
                if audit_sink is not None and (
                    check.status == "rejected" or check.kwargs_only
                ):
                    audit_sink.append((child_qualified, kind, check))
            if signature is not None:
                counter["signatures"] += 1
            counter[f"kind_{kind}"] += 1
            records.append(
                {"name": child_qualified, "signature": signature, "kind": kind}
            )
            visit(child, child_qualified, kind)

    visit(root, "<module>", "module")
    return records


def load_old_catalog() -> tuple[dict[int, dict], str]:
    """读旧 catalog；同一份字节既算 SHA 又解析，回执里的摘要即实际所用输入。"""
    raw = (ROOT / OLD_CATALOG).read_bytes()
    rows: dict[int, dict] = {}
    # 只按 \n 分行：splitlines() 还会在 U+2028/U+0085 等处断开 JSON 字符串
    for line in raw.decode("utf-8").split("\n"):
        if line.strip():
            row = json.loads(line)
            rows[row["entry_index"]] = row
    return rows, sha256_bytes(raw)


def new_audit() -> dict:
    """回执用逐条审计：被拒签名、仅 **名 签名清单与两包读取统计。"""
    return {"signature_rejected": [], "kwargs_only_rendered": [], "reads": {}}


def note_signatures(
    audit: dict, archive_sha: str, index: int, path: str, sink: list
) -> None:
    for name, kind, check in sink:
        base = {
            "archive_sha256": archive_sha,
            "entry_index": index,
            "path": path,
            "name": name,
            "kind": kind,
        }
        if check.status == "rejected":
            audit["signature_rejected"].append(
                {
                    **base,
                    "raw_signature": check.raw,
                    "reason": check.reason,
                    "slot_names": list(check.slot_names),
                    "non_identifier_names": [
                        {"text": text, "bytes_hex": data}
                        for text, data in check.non_identifier
                    ],
                }
            )
        else:
            audit["kwargs_only_rendered"].append(
                {**base, "signature": check.signature}
            )


def rejected_fallback(old_row: dict, old_sha: str) -> tuple[str, dict | None]:
    """按原优先级取旧 catalog 回退路径；含控制字符则拒绝并返回可回查原值。

    返回 (采用的回退, 拒绝记录)。被拒时采用值为空串，只表示「未采用任何
    回退」，不是原值；原值在拒绝记录里由 JSON 序列化转义控制字符。
    """
    field = next(
        (
            name
            for name in ("index_filename", "historical_filename")
            if old_row.get(name)
        ),
        None,
    )
    original = old_row.get(field) if field else None
    fallback = (original or "").replace("\\", "/")
    controls = [
        {"offset": pos, "codepoint": f"U+{ord(ch):04X}"}
        for pos, ch in enumerate(fallback)
        if ord(ch) < 32 or ord(ch) == 127
    ]
    if not controls:
        return fallback, None
    return "", {
        "source": OLD_CATALOG,
        "source_sha256": old_sha,
        "field": field,
        "original_value": original,
        "original_value_utf8_hex": original.encode("utf-8").hex(),
        "control_characters": controls,
        "disposition": "rejected: not written to modules.jsonl; entry registered "
        "as unreadable with path=null",
    }


def script_records(
    catalog_path: Path, old: dict[int, dict], old_sha: str, audit: dict
) -> tuple[list[dict], Counter, list[dict]]:
    raw_catalog = read_catalog(catalog_path)
    if sha256_bytes(raw_catalog) != CATALOG_SHA:
        raise SystemExit("XOR catalog SHA mismatch; refusing to extract")
    catalog_rows = json.loads(raw_catalog.decode("utf-8-sig"))
    counter: Counter = Counter()
    failures: list[dict] = []
    records: list[dict] = []
    doc = AuditedArchive(
        ROOT / "data/script.fls", excluded=frozenset(EXCLUDED_SCRIPT)
    )
    try:
        if doc.fingerprint() != SCRIPT_SHA or len(doc.entries) != 5002:
            raise SystemExit("script.fls pin mismatch; refusing to extract")
        for entry in doc.entries:
            index = entry.index
            if index in EXCLUDED_SCRIPT:
                records.append(
                    {
                        "archive_sha256": SCRIPT_SHA,
                        "entry_index": index,
                        "path": None,
                        "vm": "py25",
                        "path_status": "excluded_by_policy",
                        "functions": [],
                    }
                )
                counter["excluded_by_policy"] += 1
                continue  # 不读取该条负载字节
            try:
                info = catalog_rows[str(index)]
                stored = doc.read_stored(index)
                expanded = inflate(stored)
                profile = KeyProfile(
                    SCRIPT_SHA,
                    index,
                    entry.identity,
                    sha256_bytes(stored),
                    CATALOG_SHA,
                    tuple(info["keys"]),
                    tuple(info["bounds"]),
                    len(expanded),
                )
                profile.validate(doc, index)
                tree = marshal_parse(profile.crypt(expanded), zero_padding=True)
                path = display_module_path(tree.fields[5].value).replace("\\", "/")
                if not path:
                    raise ValueError("empty co_filename")
                if "\\x" in path:
                    counter["suspect_paths"] += 1
                sink: list = []
                functions = extract_functions(tree, "py25", counter, sink)
                counter["structurally_read"] += 1
                counter["functions_total"] += len(functions)
                records.append(
                    {
                        "archive_sha256": SCRIPT_SHA,
                        "entry_index": index,
                        "path": path,
                        "vm": "py25",
                        "path_status": "structurally_read",
                        "functions": functions,
                    }
                )
                note_signatures(audit, SCRIPT_SHA, index, path, sink)
            except Exception as exc:  # 单条失败不拖垮全量，逐条登记
                # 旧回退路径本身含控制字符（同为接缝乱码）时不写入目录、条目改判
                # 不可读；原值经 JSON 转义另存 failures[].fallback_rejected。
                fallback, rejected = rejected_fallback(old.get(index) or {}, old_sha)
                if rejected is not None:
                    counter["fallback_rejected_control_chars"] += 1
                reason = f"{type(exc).__name__}: {exc}"
                failure = {"entry_index": index, "reason": reason, "fallback": fallback}
                if rejected is not None:
                    failure["fallback_rejected"] = rejected
                failures.append(failure)
                if fallback:
                    counter["historical"] += 1
                    records.append(
                        {
                            "archive_sha256": SCRIPT_SHA,
                            "entry_index": index,
                            "path": fallback,
                            "vm": "py25",
                            "path_status": "historical",
                            "functions": [],
                        }
                    )
                else:
                    counter["unreadable"] += 1
                    records.append(
                        {
                            "archive_sha256": SCRIPT_SHA,
                            "entry_index": index,
                            "path": None,
                            "vm": "py25",
                            "path_status": "unreadable",
                            "functions": [],
                        }
                    )
    finally:
        audit["reads"]["script"] = doc.read_summary()
        doc.close()
    return records, counter, failures


def data_records(audit: dict) -> tuple[list[dict], Counter, list[dict]]:
    counter: Counter = Counter()
    failures: list[dict] = []
    records: list[dict] = []
    doc = AuditedArchive(ROOT / "data/data.fls", excluded=frozenset())
    try:
        if doc.fingerprint() != DATA_SHA or len(doc.entries) != 133:
            raise SystemExit("data.fls pin mismatch; refusing to extract")
        for entry in doc.entries:
            index = entry.index
            path = entry.identity.replace("\\", "/")
            if entry.directory:
                counter["directory"] += 1
                records.append(
                    {
                        "archive_sha256": DATA_SHA,
                        "entry_index": index,
                        "path": path,
                        "vm": "py27",
                        "path_status": "directory",
                        "functions": [],
                    }
                )
                continue
            try:
                content = flsdata.inflate(doc.read_stored(index))
                if content[:4] != bytes.fromhex("03f30d0a"):
                    raise ValueError("bad py27 magic")
                standard = py27_to_standard(content)
                tree = marshal_parse(standard[8:], native27=False)
                embedded = decode_text(tree.fields[5].value).replace("\\", "/")
                base = path.rsplit("/", 1)[-1].removesuffix(".pyo") + ".py"
                counter["embedded_filename_match" if embedded.endswith(base)
                        else "embedded_filename_mismatch"] += 1
                sink: list = []
                functions = extract_functions(tree, "py27", counter, sink)
                counter["structurally_read"] += 1
                counter["functions_total"] += len(functions)
                records.append(
                    {
                        "archive_sha256": DATA_SHA,
                        "entry_index": index,
                        "path": path,
                        "vm": "py27",
                        "path_status": "structurally_read",
                        "functions": functions,
                    }
                )
                note_signatures(audit, DATA_SHA, index, path, sink)
            except Exception as exc:
                counter["unreadable"] += 1
                failures.append(
                    {
                        "entry_index": index,
                        "reason": f"{type(exc).__name__}: {exc}",
                        "fallback": path,
                    }
                )
                records.append(
                    {
                        "archive_sha256": DATA_SHA,
                        "entry_index": index,
                        "path": path,
                        "vm": "py27",
                        "path_status": "unreadable",
                        "functions": [],
                    }
                )
    finally:
        audit["reads"]["data"] = doc.read_summary()
        doc.close()
    return records, counter, failures


def sample_report(
    script: list[dict], old: dict[int, dict], audit: dict | None = None
) -> dict:
    seed_path = ROOT / "script_manual/inventory/modules.jsonl"
    seeds = {}
    seed_sha = None
    if seed_path.exists():
        raw = seed_path.read_bytes()  # 同一份字节既算 SHA 又取种子
        seed_sha = sha256_bytes(raw)
        for line in raw.decode("utf-8").split("\n"):
            if line.strip():
                row = json.loads(line)
                if row["archive_sha256"] == SCRIPT_SHA and row.get(
                    "path_status"
                ) == "historical":
                    seeds[row["entry_index"]] = row["path"]
    seeds_from_modules = len(seeds)
    task_indices = {
        task["entry_index"]
        for task in json.loads(
            (ROOT / "script_manual/coordination/tasks.json").read_text(
                encoding="utf-8"
            )
        )["tasks"]
    }
    if not task_indices.issubset(seeds):
        # 全量已覆盖种子文件时，复用既有回归报告中保存的种子路径，
        # 保证 --sample 可重复运行且口径不变。
        prior_path = ROOT / "script_manual/inventory/sample_regression.json"
        if prior_path.exists():
            prior = json.loads(prior_path.read_text(encoding="utf-8"))
            for row in prior.get("entries", []):
                if row.get("seed_path"):
                    seeds.setdefault(row["entry_index"], row["seed_path"])
    tasks = json.loads(
        (ROOT / "script_manual/coordination/tasks.json").read_text(encoding="utf-8")
    )["tasks"]
    by_index = {row["entry_index"]: row for row in script}
    rejected_by_index = Counter(
        item["entry_index"]
        for item in (audit or {}).get("signature_rejected", [])
        if item["archive_sha256"] == SCRIPT_SHA
    )
    rows = []
    for task in tasks:
        index = task["entry_index"]
        got = by_index[index]
        old_names = [
            n
            for n in (old.get(index, {}).get("historical_function_names") or [])
            if n != "<module>"
        ]
        flat = [f["name"].rsplit(".", 1)[-1] for f in got["functions"]]
        rows.append(
            {
                "entry_index": index,
                "seed_path": seeds.get(index),
                "extracted_path": got["path"],
                "path_matches_seed": seeds.get(index) == got["path"],
                "path_status": got["path_status"],
                "extracted_functions": len(got["functions"]),
                "classes": sum(f["kind"] == "class" for f in got["functions"]),
                "methods": sum(f["kind"] == "method" for f in got["functions"]),
                "plain_functions": sum(
                    f["kind"] == "function" for f in got["functions"]
                ),
                "signatures": sum(
                    f["signature"] is not None for f in got["functions"]
                ),
                "signatures_rejected_null": rejected_by_index[index],
                "historical_function_names_excl_module": len(old_names),
                "flat_name_multiset_matches_historical": Counter(flat)
                == Counter(old_names),
                "only_in_extraction": sorted(
                    (Counter(flat) - Counter(old_names)).elements()
                )[:20],
                "only_in_historical": sorted(
                    (Counter(old_names) - Counter(flat)).elements()
                )[:20],
            }
        )
    return {
        "scope": "tasks.json 20 pilot entries, script.fls only",
        "method": "same code path as --full; old catalog compared, never copied",
        "entries": rows,
        "all_paths_match_seed": all(r["path_matches_seed"] for r in rows),
        "seed_source": {
            "modules_jsonl_sha256_at_read": seed_sha,
            "frozen_seed_commit": FROZEN_SEED_COMMIT,
            "frozen_seed_sha256": FROZEN_SEED_SHA,
            "is_frozen_seed_file": seed_sha == FROZEN_SEED_SHA,
            "historical_seed_rows_in_modules_jsonl": seeds_from_modules,
            "seed_paths_from_prior_sample_regression": len(seeds) - seeds_from_modules,
            "task_identities": len(task_indices),
        },
        "extractor_sha256": sha256_file(Path(__file__)),
        "read_audit": (audit or {}).get("reads", {}).get("script"),
    }


def signature_counts(counter: Counter) -> dict:
    return {
        "confirmed": counter["signatures"],
        "kwargs_only_confirmed": counter["signature_kwargs_only"],
        "rejected_compiler_internal_slot": counter[
            "signature_rejected_compiler_internal_slot"
        ],
        "rejected_non_identifier_parameter": counter[
            "signature_rejected_non_identifier_parameter"
        ],
        "unavailable_metadata": counter["signature_unavailable"],
    }


def loaded_script_editor_modules() -> dict[str, str]:
    """运行时实际加载的全部 script_editor 模块（含 __init__），不只手列清单。"""
    base = (ROOT / "script_editor" / "src").resolve()
    found = {}
    for module in list(sys.modules.values()):
        name = getattr(module, "__file__", None)
        if not name:
            continue
        path = Path(name).resolve()
        if path.is_relative_to(base):
            found[path.relative_to(ROOT).as_posix()] = sha256_file(path)
    return dict(sorted(found.items()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sample", action="store_true", help="只跑20条样板回归")
    group.add_argument("--full", action="store_true", help="跑两包全量并写交付")
    args = parser.parse_args()

    for rel, want in (
        ("data/script.fls", SCRIPT_SHA),
        ("data/data.fls", DATA_SHA),
        ("tools/decompiler/script_fls_keys.json", CATALOG_SHA),
    ):
        if sha256_file(ROOT / rel) != want:
            raise SystemExit(f"pinned input mismatch: {rel}")

    old, old_sha = load_old_catalog()
    audit = new_audit()
    script, script_counter, script_failures = script_records(
        ROOT / "tools/decompiler/script_fls_keys.json", old, old_sha, audit
    )
    print(f"script: {dict(script_counter)} failures={len(script_failures)}")

    if args.sample:
        report = sample_report(script, old, audit)
        out = ROOT / "script_manual/inventory/sample_regression.json"
        out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"sample written: {out} all_paths={report['all_paths_match_seed']}")
        print(f"seed_source: {report['seed_source']}")
        return 0

    data, data_counter, data_failures = data_records(audit)
    print(f"data: {dict(data_counter)} failures={len(data_failures)}")
    # 种子路径必须在覆盖 modules.jsonl 之前核对
    seed_report = sample_report(script, old, audit)
    seed_check = seed_report["all_paths_match_seed"]
    records = script + data
    assert len(records) == 5135 and len(
        {(r["archive_sha256"], r["entry_index"]) for r in records}
    ) == 5135
    dup_paths = [
        item for item in Counter(r["path"] for r in records if r["path"]).items()
        if item[1] > 1
    ]
    out = ROOT / "script_manual/inventory/modules.jsonl"
    with out.open("w", encoding="utf-8", newline="\n") as stream:
        for row in records:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"inventory written: {out} rows={len(records)}")

    sample_path = ROOT / "script_manual/inventory/sample_regression.json"
    suspect_examples = []
    duplicate_names = []
    for row in records:
        seen: Counter = Counter()
        for func in row["functions"]:
            leaf = func["name"].rsplit(".", 1)[-1]
            if leaf not in SPECIAL_NAMES and not IDENT.match(leaf):
                if len(suspect_examples) < 20:
                    suspect_examples.append(
                        {"entry_index": row["entry_index"], "name": func["name"]}
                    )
            seen[func["name"]] += 1
        for name, count in seen.items():
            if count > 1:
                duplicate_names.append(
                    {
                        "entry_index": row["entry_index"],
                        "name": name,
                        "count": count,
                    }
                )
    excluded_row = next(
        r for r in records if r["entry_index"] == 1288
        and r["archive_sha256"] == SCRIPT_SHA
    )
    self_checks = {
        "total_records_5135": len(records) == 5135,
        "unique_keys": len(
            {(r["archive_sha256"], r["entry_index"]) for r in records}
        )
        == 5135,
        "excluded_1288_exact": excluded_row
        == {
            "archive_sha256": SCRIPT_SHA,
            "entry_index": 1288,
            "path": None,
            "vm": "py25",
            "path_status": "excluded_by_policy",
            "functions": [],
        },
        "no_control_char_paths": all(
            r["path"] is None
            or not any(ord(c) < 32 or ord(c) == 127 for c in r["path"])
            for r in records
        ),
        "max_functions_per_entry": max(len(r["functions"]) for r in records),
        "seed20_paths_preserved": seed_check,
        "seed_file_is_frozen_20_seed": seed_report["seed_source"][
            "is_frozen_seed_file"
        ],
        "functions_total": sum(len(r["functions"]) for r in records),
    }
    signatures = [
        func["signature"]
        for row in records
        for func in row["functions"]
        if func["signature"] is not None
    ]
    both = script_counter + data_counter
    rejected_fallbacks = [
        item["entry_index"] for item in script_failures if "fallback_rejected" in item
    ]
    self_checks.update(
        {
            "bare_star_signatures": sum(
                "*" in sig[1:-1].split(", ") for sig in signatures
            ),
            "internal_slot_signatures": sum(
                any(
                    INTERNAL_SLOT.fullmatch(token.lstrip("*"))
                    for token in sig[1:-1].split(", ")
                )
                for sig in signatures
            ),
            "all_signatures_wellformed_python2": all(
                signature_is_wellformed(sig) for sig in signatures
            ),
            "signature_rejections_listed_equal_counters": len(
                audit["signature_rejected"]
            )
            == sum(v for k, v in both.items() if k.startswith("signature_rejected_")),
            "kwargs_only_listed_equal_counters": len(audit["kwargs_only_rendered"])
            == both["signature_kwargs_only"],
            "rejected_fallbacks_with_original_value": [
                item["entry_index"]
                for item in script_failures
                if item.get("fallback_rejected", {}).get("original_value")
            ],
            "excluded_1288_read_stored_calls": audit["reads"]["script"][
                "excluded_read_stored_calls"
            ],
        }
    )
    receipt = {
        "agent": "N1",
        "logical_owner": "B",
        "session": "new N1 Arena session on its own fixed branch; not the "
        "original B session",
        "task": "full inventory extraction for two pinned archives",
        "revision_note": "N1 fixes per docs/evidence/"
        "script_manual_BDF_A_review_20261016.md: no bare '*' for **kwargs-only "
        "signatures; '.N' compiler slots and non-identifier parameter names -> "
        "signature null with raw clue in signature_audit.rejected; rejected "
        "fallback originals recorded in script_failures[].fallback_rejected",
        "baseline_analysis_id": "mxsj-original-20261015-v1",
        "inputs": {
            "script_fls": {"path": "data/script.fls", "sha256": SCRIPT_SHA},
            "data_fls": {"path": "data/data.fls", "sha256": DATA_SHA},
            "xor_catalog": {
                "path": "tools/decompiler/script_fls_keys.json",
                "sha256": CATALOG_SHA,
                "also_at": "script_editor/decoding/script-original.json (same sha)",
            },
            "historical_catalog_fallback_only": {
                "path": OLD_CATALOG,
                "sha256": old_sha,
                "role": "historical path fallback + sample comparison only; "
                "its function names were never copied into results",
            },
            "frozen_seed": {
                "commit": FROZEN_SEED_COMMIT,
                "path": "script_manual/inventory/modules.jsonl",
                "sha256": FROZEN_SEED_SHA,
                "rows": 20,
                "role": "the only modules.jsonl present in the isolated tree "
                "before --sample/--full; the current 5135-row inventory is "
                "never used as seed",
            },
            "decompiled_corpus": "not used; marshal metadata is read directly "
            "from originals, PR34 corpus stays external_reference_not_loaded",
        },
        "tools": {
            "python": sys.version.split()[0],
            "extractor": {
                "path": "script_manual/inventory/extract_inventory.py",
                "sha256": sha256_file(Path(__file__)),
            },
            "reused_modules_sha256": {
                rel: sha256_file(ROOT / rel) for rel in TOOL_FILES
            },
            "loaded_script_editor_modules_sha256": loaded_script_editor_modules(),
        },
        "commands": [
            "git show "
            f"{FROZEN_SEED_COMMIT}:script_manual/inventory/modules.jsonl "
            "> <isolated-tree>/script_manual/inventory/modules.jsonl",
            "python3 <isolated-tree>/script_manual/inventory/extract_inventory.py "
            "--sample",
            "python3 <isolated-tree>/script_manual/inventory/extract_inventory.py "
            "--full",
            "PYTHONPATH=script_manual/src python3 -m mxsj_manual validate "
            "--verify-evidence --require-full-inventory --repository .",
            "python3 -m unittest discover -s script_manual/inventory "
            "-p 'test_*.py' -v",
        ],
        "isolation": "ROOT = parents[2] of this script; --sample writes "
        "sample_regression.json and --full writes modules.jsonl plus this "
        "receipt under ROOT/script_manual/inventory. Runs happen in a copy "
        "outside the repository whose inventory holds only the frozen 20-seed "
        "modules.jsonl (no prior sample_regression.json); the three outputs "
        "are then copied back unchanged",
        "method": {
            "script": "0SLF index -> inflate -> pinned 5-segment XOR -> bounded "
            "marshal tree; path=co_filename, names from nested code objects",
            "data": "FLS0 central directory names are the registered paths; "
            "payload inflated, native VM27 converted with audited inverse, "
            "then same marshal walk; directories keep directory status",
            "kind": "parent standard bytecode LOAD_CONST + MAKE_FUNCTION/"
            "MAKE_CLOSURE, BUILD_CLASS within window => class; class child "
            "function => method; undecodable parent => header-flag fallback",
            "signature": "CPython 2 co_varnames layout: co_argcount positional "
            "names, then *name if CO_VARARGS, then **name if CO_VARKEYWORDS; no "
            "bare '*' (Python 2 has no keyword-only parameters); emitted only "
            "when every name is a Python 2 identifier, otherwise null with the "
            "raw rendering kept in signature_audit.rejected; class signature "
            "always null; default values not rendered",
            "excluded_1288": "never targeted by read_stored (audited, see "
            "read_audit.script); payload never decompressed, decrypted or "
            "parsed; whole-file SHA-256 fingerprinting reads its bytes only to "
            "hash the archive; only the policy meta-record is emitted",
            "execution": "no game module imported/executed; no decompiler run",
        },
        "script_counts": dict(script_counter),
        "data_counts": dict(data_counter),
        "script_failures": script_failures,
        "data_failures": data_failures,
        "rejected_fallback_entries": rejected_fallbacks,
        "duplicate_paths_kept": [
            {"path": path, "entries": count} for path, count in sorted(dup_paths)
        ],
        "self_checks": self_checks,
        "seed_source": seed_report["seed_source"],
        "read_audit": audit["reads"],
        "signature_audit": {
            "policy": "a signature is a confirmed parameter list only if the "
            "co_varnames layout is consistent and every name is a Python 2 "
            "identifier; rejected raw renderings are review clues, never "
            "source signatures; tuple parameter shapes are not reconstructed "
            "and nothing is copied from the historical catalog",
            "references": SIGNATURE_REFERENCES,
            "counts": {
                "script": signature_counts(script_counter),
                "data": signature_counts(data_counter),
            },
            "kwargs_only_rendered": audit["kwargs_only_rendered"],
            "rejected": audit["signature_rejected"],
        },
        "suspect_name_examples": suspect_examples,
        "duplicate_qualified_names": duplicate_names[:50],
        "duplicate_qualified_name_count": len(duplicate_names),
        "cross_check_note": "script_editor 0.6 evidence reports 4951 readable "
        "paths on this archive without the manual policy exclusion; this run "
        "reports 4950 structurally_read plus the excluded 1288 meta-record, a "
        "difference of exactly one, consistent with never reading the 1288 "
        "payload (inference, not a re-read of 1288)",
        "modules_jsonl_sha256": sha256_file(out),
        "sample_regression": {
            "path": "script_manual/inventory/sample_regression.json",
            "sha256": sha256_file(sample_path) if sample_path.exists() else None,
        },
        "known_limits": [
            "kind fallback entries are counted in kind_fallback, not hidden",
            "suspect_names counts identifiers failing ^[A-Za-z_][A-Za-z0-9_]*$ "
            "(possible marshal seam garbling near XOR bounds); bytes are kept "
            "as read and never repaired from the historical catalog",
            "that legacy function-name check uses re.match with $, which also "
            "accepts a trailing newline; no current function name ends with one",
            "signatures omit default-value expressions",
            "signature null covers class bodies, inconsistent metadata, '.N' "
            "compiler slots (anonymous tuple parameters, generator-expression "
            "iterators) and non-identifier parameter names; null means unknown, "
            "not 'no parameters'",
            "garbling that still yields a valid identifier cannot be detected "
            "by the identifier rule; confirmed signatures are structural "
            "metadata, not semantically reviewed source",
            "duplicate qualified names are preserved (e.g. repeated <lambda>)",
            "structural read proves names/paths exist in the pinned archive; "
            "it does not prove decompiled behavior or runtime correctness",
        ],
    }
    receipt_path = ROOT / "script_manual/inventory/B_extraction_receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"receipt written: {receipt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
