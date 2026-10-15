"""B 包全量目录结构提取（只读，不执行游戏脚本，不反编译）。

方法：复用 script_editor 已审计的容器/密文/marshal 结构读取代码，
直接从两固定原包的 marshal 码对象树读取 co_filename、co_name、
co_varnames 与头字段，并用父码对象标准字节码中的
LOAD_CONST/MAKE_FUNCTION/BUILD_CLASS 序列区分 class 与 function。
不导入、不执行任何游戏模块；不读取 entry 1288 的负载字节。

旧 catalog（server/docs/catalog/script_entries.jsonl）仅作两件事：
1) 结构读取失败时的 historical 路径回退（函数一律留空）；
2) 20 条样板回归的对照统计。其函数名不写入本轮结果。

用法（仓库根目录）：
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


def signature_of(node: Code, counter: Counter) -> str | None:
    """由 argcount/varnames/flags 构造可确认签名；信息不足返回 None。

    默认值对象是常量，不安全渲染为源码文本，故只登记形参名与
    *args/**kwargs；带默认值的形参仍以裸名出现，限制写在回执中。
    """
    argcount, _nlocals, _stack, flags = struct.unpack("<iiii", node.header)
    varnames_node = node.fields[2]
    if not isinstance(varnames_node, Group):
        counter["signature_unavailable"] += 1
        return None
    varnames = [decode_text(item.value) for item in varnames_node.items]
    if argcount < 0 or len(varnames) < argcount:
        counter["signature_unavailable"] += 1
        return None
    params = list(varnames[:argcount])
    cursor = argcount
    if flags & 0x04:  # CO_VARARGS
        if cursor >= len(varnames):
            counter["signature_unavailable"] += 1
            return None
        params.append("*" + varnames[cursor])
        cursor += 1
    elif flags & 0x08:
        params.append("*")
    if flags & 0x08:  # CO_VARKEYWORDS
        if cursor >= len(varnames):
            counter["signature_unavailable"] += 1
            return None
        params.append("**" + varnames[cursor])
    return "(" + ", ".join(params) + ")"


def extract_functions(root: Code, vm: str, counter: Counter) -> list[dict]:
    """先序遍历码对象树（不含根 <module>），生成库存函数元数据。"""
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
            signature = None if kind == "class" else signature_of(child, counter)
            if signature is not None:
                counter["signatures"] += 1
            counter[f"kind_{kind}"] += 1
            records.append(
                {"name": child_qualified, "signature": signature, "kind": kind}
            )
            visit(child, child_qualified, kind)

    visit(root, "<module>", "module")
    return records


def load_old_catalog() -> dict[int, dict]:
    path = ROOT / "server/docs/catalog/script_entries.jsonl"
    rows: dict[int, dict] = {}
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                row = json.loads(line)
                rows[row["entry_index"]] = row
    return rows


def script_records(
    catalog_path: Path, old: dict[int, dict]
) -> tuple[list[dict], Counter, list[dict]]:
    raw_catalog = read_catalog(catalog_path)
    if sha256_bytes(raw_catalog) != CATALOG_SHA:
        raise SystemExit("XOR catalog SHA mismatch; refusing to extract")
    catalog_rows = json.loads(raw_catalog.decode("utf-8-sig"))
    counter: Counter = Counter()
    failures: list[dict] = []
    records: list[dict] = []
    doc = ArchiveDocument(ROOT / "data/script.fls")
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
                functions = extract_functions(tree, "py25", counter)
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
            except Exception as exc:  # 单条失败不拖垮全量，逐条登记
                old_row = old.get(index) or {}
                fallback = (
                    old_row.get("index_filename")
                    or old_row.get("historical_filename")
                    or ""
                ).replace("\\", "/")
                if any(ord(ch) < 32 or ord(ch) == 127 for ch in fallback):
                    # 旧回退路径本身含控制字符（同为接缝乱码），不写入目录；
                    # 原样保留在 failures 清单中供 A 审阅，条目改判不可读。
                    counter["fallback_rejected_control_chars"] += 1
                    fallback = ""
                reason = f"{type(exc).__name__}: {exc}"
                failures.append(
                    {"entry_index": index, "reason": reason, "fallback": fallback}
                )
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
        doc.close()
    return records, counter, failures


def data_records() -> tuple[list[dict], Counter, list[dict]]:
    counter: Counter = Counter()
    failures: list[dict] = []
    records: list[dict] = []
    doc = ArchiveDocument(ROOT / "data/data.fls")
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
                functions = extract_functions(tree, "py27", counter)
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
        doc.close()
    return records, counter, failures


def sample_report(script: list[dict], old: dict[int, dict]) -> dict:
    seed_path = ROOT / "script_manual/inventory/modules.jsonl"
    seeds = {}
    if seed_path.exists():
        with seed_path.open(encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    row = json.loads(line)
                    if row["archive_sha256"] == SCRIPT_SHA and row.get(
                        "path_status"
                    ) == "historical":
                        seeds[row["entry_index"]] = row["path"]
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
    }


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

    old = load_old_catalog()
    script, script_counter, script_failures = script_records(
        ROOT / "tools/decompiler/script_fls_keys.json", old
    )
    print(f"script: {dict(script_counter)} failures={len(script_failures)}")

    if args.sample:
        report = sample_report(script, old)
        out = ROOT / "script_manual/inventory/sample_regression.json"
        out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"sample written: {out} all_paths={report['all_paths_match_seed']}")
        return 0

    data, data_counter, data_failures = data_records()
    print(f"data: {dict(data_counter)} failures={len(data_failures)}")
    # 种子路径必须在覆盖 modules.jsonl 之前核对
    seed_check = sample_report(script, old)["all_paths_match_seed"]
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
    }
    receipt = {
        "agent": "B",
        "task": "full inventory extraction for two pinned archives",
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
                "path": "server/docs/catalog/script_entries.jsonl",
                "sha256": sha256_file(
                    ROOT / "server/docs/catalog/script_entries.jsonl"
                ),
                "role": "historical path fallback + sample comparison only; "
                "its function names were never copied into results",
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
        },
        "commands": [
            "python3 script_manual/inventory/extract_inventory.py --sample",
            "python3 script_manual/inventory/extract_inventory.py --full",
            "PYTHONPATH=script_manual/src <venv>/python -m mxsj_manual "
            "validate --require-full-inventory",
        ],
        "method": {
            "script": "0SLF index -> inflate -> pinned 5-segment XOR -> bounded "
            "marshal tree; path=co_filename, names from nested code objects",
            "data": "FLS0 central directory names are the registered paths; "
            "payload inflated, native VM27 converted with audited inverse, "
            "then same marshal walk; directories keep directory status",
            "kind": "parent standard bytecode LOAD_CONST + MAKE_FUNCTION/"
            "MAKE_CLOSURE, BUILD_CLASS within window => class; class child "
            "function => method; undecodable parent => header-flag fallback",
            "signature": "argcount/varnames/flags only; null when unconfirmed; "
            "class signature always null; default values not rendered",
            "excluded_1288": "payload bytes never read, decrypted or parsed; "
            "only the policy meta-record is emitted",
            "execution": "no game module imported/executed; no decompiler run",
        },
        "script_counts": dict(script_counter),
        "data_counts": dict(data_counter),
        "script_failures": script_failures,
        "data_failures": data_failures,
        "duplicate_paths_kept": [
            {"path": path, "entries": count} for path, count in sorted(dup_paths)
        ],
        "self_checks": self_checks,
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
            "signatures omit default-value expressions",
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
