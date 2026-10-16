"""N1 隔离重放与外部读审计（辅助验证工具；只读原包，不执行任何游戏代码）。

用法（仓库根目录；--work 必须位于仓库之外且尚不存在）：
    python3 script_manual/inventory/n1_replay_audit.py --work <仓库外新目录> \
        --report <输出路径>.json.template

对每棵隔离树（默认两棵）：复制固定输入与复用工具，写入 cc5c1ba 的冻结
20 种子（核对摘要与 tasks.json 身份），再以子进程依次运行
extract_inventory.py --sample 与 --full。子进程在运行提取器之前给
FileReader.read_at 与 ArchiveDocument.read_stored 装记录器（先登记、再委托），
把底层读取按调用栈分为 fingerprint（整包 SHA）、read_stored（定点负载）、
index（目录解析）三类，并计算与 entry 1288 目录区间的重叠。最后比较各树
产物是否逐字节一致，并把新目录与基线提交里的目录逐条对比。
报告是辅助机器报告（.json.template），不是注释，手册加载器不读取它。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
EXTRACTOR_REL = "script_manual/inventory/extract_inventory.py"
MODULES_REL = "script_manual/inventory/modules.jsonl"
SEED_COMMIT = "cc5c1bad7a806078794eca1ab7482230a18ef9d5"
SEED_SHA = "de75ec619cf61e8a71098bd74f746081547b1423c6d28bd8595039f6a8e3483b"
BASELINE_REF = "9b0dea799768aaacbb967ffc59f45753970752be"
COPIES = (
    "data/script.fls",
    "data/data.fls",
    "tools/decompiler/script_fls_keys.json",
    "server/docs/catalog/script_entries.jsonl",
    "script_manual/coordination/tasks.json",
    EXTRACTOR_REL,
)
PINNED = COPIES[:3]
OUTPUTS = ("modules.jsonl", "sample_regression.json", "B_extraction_receipt.json")
EXCLUDED = 1288
SLOT = re.compile(r"\.[0-9]+")
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_show(ref: str, rel: str) -> bytes:
    proc = subprocess.run(
        ["git", "-C", str(REPO), "show", f"{ref}:{rel}"],
        check=True,
        capture_output=True,
    )
    return proc.stdout


def jsonl(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode("utf-8").split("\n") if line]


# ---------------------------------------------------------------- 子进程：单次运行


def caller_kind() -> str:
    frame = sys._getframe(2)
    while frame is not None:
        name = frame.f_code.co_name
        if name in ("fingerprint", "read_stored"):
            return name
        if name in ("parse_index", "__init__") and "archives" in (
            frame.f_code.co_filename
        ):
            return "index"
        frame = frame.f_back
    return "other"


def child(tree: Path, mode: str, out: Path) -> int:
    mode = f"--{mode}"  # 经 argparse 传入时不带 --，避免被当成选项
    sys.path.insert(0, str(tree / "script_editor" / "src"))
    from script_editor.core.archives import document, readers

    reads: list[tuple[str, int, int, str]] = []
    stored: Counter = Counter()
    names: dict[int, str] = {}
    orig_init = readers.FileReader.__init__
    orig_read_at = readers.FileReader.read_at
    orig_read_stored = document.ArchiveDocument.read_stored

    def init(self, path):
        orig_init(self, path)
        names[id(self)] = Path(path).name

    def read_at(self, offset, size):
        reads.append((names.get(id(self), "?"), offset, size, caller_kind()))
        return orig_read_at(self, offset, size)

    def read_stored(self, index):
        stored[(self.path.name, index)] += 1  # 先登记，再委托
        return orig_read_stored(self, index)

    readers.FileReader.__init__ = init
    readers.FileReader.read_at = read_at
    document.ArchiveDocument.read_stored = read_stored

    before = {rel: sha256_file(tree / rel) for rel in PINNED}
    sys.argv = [str(tree / EXTRACTOR_REL), mode]
    start = time.perf_counter()
    exit_code = 0
    try:
        runpy.run_path(str(tree / EXTRACTOR_REL), run_name="__main__")
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1
    elapsed = time.perf_counter() - start
    read_log, stored_log = list(reads), Counter(stored)  # 探针自身读取不计入

    probe = document.ArchiveDocument(tree / "data/script.fls")
    span = probe.index.spans[EXCLUDED]  # 目录元数据，不是负载
    low, high = span.offset, span.offset + span.length
    probe.close()
    overlap = Counter(
        kind
        for name, offset, size, kind in read_log
        if name == "script.fls" and offset < high and offset + size > low
    )
    by_kind = Counter((name, kind) for name, _o, _s, kind in read_log)
    script = {i: c for (n, i), c in stored_log.items() if n == "script.fls"}
    data = {i: c for (n, i), c in stored_log.items() if n == "data.fls"}
    report = {
        "mode": mode,
        "extractor_exit_code": exit_code,
        "elapsed_seconds": round(elapsed, 1),
        "python": sys.version.split()[0],
        "extractor_sha256": sha256_file(tree / EXTRACTOR_REL),
        "pinned_inputs_sha256": before,
        "pinned_inputs_unchanged_after": before
        == {rel: sha256_file(tree / rel) for rel in PINNED},
        "script_read_stored_calls": sum(script.values()),
        "script_read_stored_distinct_entries": len(script),
        "script_read_stored_entry_1288": script.get(EXCLUDED, 0),
        "data_read_stored_calls": sum(data.values()),
        "data_read_stored_distinct_entries": len(data),
        "read_at_calls_by_archive_and_caller": {
            f"{name}:{kind}": count for (name, kind), count in sorted(by_kind.items())
        },
        "entry_1288_directory_span": {"offset": low, "length": span.length},
        "script_read_at_overlapping_1288_span_by_caller": dict(overlap),
    }
    report["passed"] = (
        exit_code == 0
        and report["script_read_stored_entry_1288"] == 0
        and set(overlap) <= {"fingerprint"}
        and report["pinned_inputs_unchanged_after"]
    )
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0 if report["passed"] else 1


# ---------------------------------------------------------------- 父进程：建树/比对


def build_tree(tree: Path) -> dict:
    for rel in COPIES:
        target = tree / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, target)
    shutil.copytree(
        REPO / "script_editor/src",
        tree / "script_editor/src",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    seeds = git_show(SEED_COMMIT, MODULES_REL)
    if sha256_bytes(seeds) != SEED_SHA:
        raise SystemExit("frozen seed digest mismatch")
    rows = jsonl(seeds)
    tasks = json.loads(
        (REPO / "script_manual/coordination/tasks.json").read_text(encoding="utf-8")
    )["tasks"]
    seed_ids = sorted((r["archive_sha256"], r["entry_index"]) for r in rows)
    task_ids = sorted((t["archive_sha256"], t["entry_index"]) for t in tasks)
    if seed_ids != task_ids or len(rows) != 20:
        raise SystemExit("frozen seed identities differ from tasks.json")
    (tree / MODULES_REL).write_bytes(seeds)
    return {
        "frozen_seed": {
            "commit": SEED_COMMIT,
            "sha256": sha256_bytes(seeds),
            "rows": len(rows),
            "identities_equal_tasks_json": True,
            "all_historical": all(r["path_status"] == "historical" for r in rows),
        },
        "tree_inputs_sha256": {rel: sha256_file(tree / rel) for rel in COPIES},
        "prior_sample_regression_present": (
            tree / "script_manual/inventory/sample_regression.json"
        ).exists(),
    }


def classify_signature_change(old: str | None, new: str | None) -> str:
    tokens = old[1:-1].split(", ") if old and old != "()" else []
    if "*" in tokens:
        fixed = "(" + ", ".join(t for t in tokens if t != "*") + ")"
        return "bare_star_removed" if new == fixed else "other"
    if new is None and any(SLOT.fullmatch(t.lstrip("*")) for t in tokens):
        return "internal_slot_to_null"
    if new is None and any(not IDENT.fullmatch(t.lstrip("*")) for t in tokens):
        return "non_identifier_to_null"
    return "other"


def compare_inventories(old_rows: list[dict], new_rows: list[dict]) -> dict:
    result = {
        "rows_old": len(old_rows),
        "rows_new": len(new_rows),
        "identities_equal_in_order": [
            (r["archive_sha256"], r["entry_index"]) for r in old_rows
        ]
        == [(r["archive_sha256"], r["entry_index"]) for r in new_rows],
    }
    row_changes: Counter = Counter()
    changes: Counter = Counter()
    examples: dict[str, list] = {}
    functions = [0, 0]
    for old, new in zip(old_rows, new_rows, strict=True):
        for key in ("path", "vm", "path_status"):
            row_changes[key] += old[key] != new[key]
        functions[0] += len(old["functions"])
        functions[1] += len(new["functions"])
        if len(old["functions"]) != len(new["functions"]):
            row_changes["function_count"] += 1
            continue
        for before, after in zip(old["functions"], new["functions"], strict=True):
            if (before["name"], before["kind"]) != (after["name"], after["kind"]):
                row_changes["function_name_or_kind"] += 1
            if before["signature"] == after["signature"]:
                changes["unchanged"] += 1
                continue
            kind = classify_signature_change(before["signature"], after["signature"])
            changes[kind] += 1
            bucket = examples.setdefault(kind, [])
            if len(bucket) < 3:
                bucket.append(
                    {
                        "archive_sha256": old["archive_sha256"],
                        "entry_index": old["entry_index"],
                        "name": before["name"],
                        "old": before["signature"],
                        "new": after["signature"],
                    }
                )
    result.update(
        {
            "row_field_changes": {
                key: row_changes[key]
                for key in (
                    "path",
                    "vm",
                    "path_status",
                    "function_count",
                    "function_name_or_kind",
                )
            },
            "function_records_old": functions[0],
            "function_records_new": functions[1],
            "signature_changes": dict(changes),
            "signature_change_examples": examples,
        }
    )
    return result


def run_child(tree: Path, mode: str, out: Path, work: Path) -> dict:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    proc = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            "--child",
            str(tree),
            mode,
            str(out),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    redact = str(work)
    return {
        "mode": f"--{mode}",
        "child_exit_code": proc.returncode,
        "extractor_stdout": [
            line.replace(redact, "<work>") for line in proc.stdout.splitlines()
        ],
        "stderr_tail": [
            line.replace(redact, "<work>") for line in proc.stderr.splitlines()[-20:]
        ],
        "audit": json.loads(out.read_text(encoding="utf-8")) if out.exists() else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--trees", type=int, default=2)
    parser.add_argument("--baseline-ref", default=BASELINE_REF)
    parser.add_argument("--child", nargs=3, metavar=("TREE", "MODE", "OUT"))
    args = parser.parse_args()
    if args.child:
        tree, mode, out = args.child
        return child(Path(tree), mode, Path(out))
    if args.work is None or args.report is None:
        parser.error("--work and --report are required")
    work = args.work.resolve()
    if work.exists() or work.is_relative_to(REPO):
        raise SystemExit("--work must be a new directory outside the repository")
    trees = []
    for number in range(1, args.trees + 1):
        tree = work / f"tree{number}"
        info = build_tree(tree)
        runs = [
            run_child(tree, mode, work / f"tree{number}-{mode}.audit.json", work)
            for mode in ("sample", "full")
        ]
        outputs = {
            name: sha256_file(tree / "script_manual/inventory" / name)
            for name in OUTPUTS
        }
        trees.append(
            {"tree": f"tree{number}", **info, "runs": runs, "outputs_sha256": outputs}
        )
    first = trees[0]["outputs_sha256"]
    baseline = jsonl(git_show(args.baseline_ref, MODULES_REL))
    replayed = jsonl((work / "tree1" / MODULES_REL).read_bytes())
    report = {
        "kind": "N1 auxiliary machine report (not an annotation; not loaded by the "
        "manual)",
        "harness": {
            "path": "script_manual/inventory/n1_replay_audit.py",
            "sha256": sha256_file(Path(__file__)),
            "python": sys.version.split()[0],
        },
        "extractor_sha256_in_repository": sha256_file(REPO / EXTRACTOR_REL),
        "work_directory_outside_repository": True,
        "trees": trees,
        "all_runs_passed": all(
            run["child_exit_code"] == 0 and run["audit"] and run["audit"]["passed"]
            for tree in trees
            for run in tree["runs"]
        ),
        "outputs_identical_across_trees": all(
            tree["outputs_sha256"] == first for tree in trees
        ),
        "delivered_outputs_sha256": {
            name: sha256_file(HERE / name) for name in OUTPUTS
        },
        "delivered_equal_replay": all(
            sha256_file(HERE / name) == first[name] for name in OUTPUTS
        ),
        "baseline_ref": args.baseline_ref,
        "baseline_modules_jsonl_sha256": sha256_bytes(
            git_show(args.baseline_ref, MODULES_REL)
        ),
        "inventory_diff_vs_baseline": compare_inventories(baseline, replayed),
        "interpretation": "read_stored is the only per-entry payload read; overlap "
        "of the entry 1288 span only by fingerprint means its bytes were hashed as "
        "part of the whole-archive SHA-256, never targeted, inflated, decrypted or "
        "parsed",
    }
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "all_runs_passed",
                    "outputs_identical_across_trees",
                    "delivered_equal_replay",
                )
            }
        )
    )
    return 0 if report["all_runs_passed"] and report["delivered_equal_replay"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
