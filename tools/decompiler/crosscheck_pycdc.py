#!/usr/bin/env python3
"""用第二反编译引擎 ``pycdc`` 交叉复核 ``uncompyle6`` 失败或病态的条目。

背景（2026-10-15）：``tools/decompiler/batch_decompile.py`` 的验收要求「完整转译 **且**
uncompyle6 成功」，于是 **547** 个条目虽然已经拿到完整 pyc，却只留下 52 字节的失败
占位；另有 2 个条目（``script/core/preload/preload_mov.py`` = entry 2371、
``script/data/wingtypeposdata.py`` = entry 2679）会让 uncompyle6 在 scanner/parser
里空转 >900 s。这些都不是归档解密失败——是**单一反编译引擎的能力边界**。

实测对照：同一条 pyc，uncompyle6 跑 900 s 不收敛，``pycdc`` 用 **5 ms** 就产出源码。
所以本工具把 pycdc 接成第二引擎，只读地复核那批「有字节码、没源码」的条目，并把
结果按引擎分开记账，绝不覆盖 uncompyle6 已经产出的文件。

* 目标清单来自 ``accounting.json``（``--class failed`` 即 547 条占位），也可
  ``--entries`` 手点；
* 转译复用 ``recover_entries.transpile``（``--ladder`` 才会跑完整的密钥修复梯）；
* pycdc 一律放进**带超时的子进程**，崩溃/挂死只损失这一条；
* ``--write`` 只写进 ``<out>/pycdc/`` 这棵独立目录树，已存在就跳过；
* ``--keep-pyc`` 可把复核到的 pyc 另存，供 ``pycdas`` 或以后换引擎重跑。

pycdc 的构建不需要 flex/bison（纯 C++，仅需 cmake）；沙箱内可用的最小配方见
``notes/opcode_mapping_and_decompilation.md`` §4.6。本工具不写 ``data/``、不改
``script_fls_keys.json``、不改 ``batch_decompile.py``。

用法::

    python3 tools/decompiler/crosscheck_pycdc.py --out <外置语料目录> \
        [--accounting accounting.json --class failed | --entries 2371,2679] \
        [--pycdc /path/to/build/pycdc] [--timeout 20] [--jobs 4] \
        [--write] [--keep-pyc <目录>] [--ladder] [--report crosscheck.json]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "decompiler"))

import recover_entries as rc  # noqa: E402  (同目录复用命名/转译逻辑)

# pycdc 自己写在输出里的「没解完」标记；带它就说明只拿到部分源码。
INCOMPLETE_MARK = "# WARNING: Decompyle incomplete"
# pycdc 读不动 pyc 时的典型措辞（大小写不敏感子串）。
FATAL_MARKS = ("unsupported", "couldn't", "invalid", "error:", "magic")


def classify_pycdc(stdout: str, returncode: int, stderr: str = "") -> str:
    """把一次 pycdc 运行归成四类，供报告与统计使用。

    ``pycdc_reject`` 与 ``pycdc_error`` 要分开：前者是「这份 pyc 它读不动」，
    属于引擎能力问题、不影响归档解密结论；后者才是需要回头看的地方。
    """
    body = stdout.strip()
    if returncode != 0 or not body:
        heads = [ln for ln in (body.splitlines() + (stderr or "").splitlines())
                 if ln.strip()]
        head = heads[0].lower() if heads else ""
        if any(mark in head for mark in FATAL_MARKS):
            return "pycdc_reject"
        return "pycdc_error"
    if INCOMPLETE_MARK in body:
        return "pycdc_incomplete"
    return "pycdc_ok"


def uncompyle6_state(path: Path) -> str:
    """看现有产物判断 uncompyle6 的成色，用于「谁该被复核」的判定。"""
    if not path.exists():
        return "absent"
    text = path.read_text(encoding="utf-8", errors="replace")
    if "Decompilation failed" in text:
        return "stub"
    if "uncompyle6 version" in text:
        return "full"
    if "MXSJ 恢复产物" in text:
        return "recovered"
    return "unknown"


def target_entries(accounting: dict, cls: str) -> list[int]:
    """从清点 JSON 里取一类条目的条目号（``failed`` 即 547 个占位）。"""
    raw = accounting.get(cls)
    if raw is None:
        raise SystemExit(
            f"清点文件里没有 {cls!r} 这一类；可用类别: "
            f"{sorted(k for k in accounting if isinstance(accounting[k], list))}"
        )
    return sorted({int(i) for i in raw})


def plan_write(out: Path, rel: str) -> tuple[Path, bool]:
    """返回 ``(目标路径, 是否可写)``；已存在的产物永远不覆盖。"""
    dest = out / "pycdc" / rel
    return dest, not dest.exists()


# 沙箱/常见安装位置；测试可注入别的候选，避免依赖本机是否真装了 pycdc。
FALLBACK_CANDIDATES = (REPO_ROOT.parent / "pycdc" / "build" / "pycdc",
                       Path("/usr/local/bin/pycdc"))


def resolve_pycdc(explicit: str | None,
                  candidates: tuple[Path, ...] = FALLBACK_CANDIDATES) -> Path:
    """按 --pycdc → PATH → 常见位置 的顺序找 pycdc 可执行文件。"""
    if explicit:
        p = Path(explicit)
        if not p.exists():
            raise SystemExit(f"找不到 pycdc: {p}")
        return p
    found = shutil.which("pycdc")
    if found:
        return Path(found)
    for cand in candidates:
        if cand.exists():
            return cand
    raise SystemExit(
        "没有 pycdc 可执行文件。用 --pycdc 指定，或按 §4.6 自建：\n"
        "  pip install cmake && git clone https://github.com/zrax/pycdc \\\n"
        "  && cmake -S pycdc -B pycdc/build && cmake --build pycdc/build -j4"
    )


def decode_engine_output(raw: bytes) -> tuple[str, bool]:
    """把引擎输出统一成合法 UTF-8 文本，返回 ``(文本, 是否发生转义)``。

    pycdc 不像 uncompyle6 那样转义字符串常量里的字节，遇到 GBK 写的 docstring
    会直接吐裸字节；用 ``text=True`` 会让整批在 ``UnicodeDecodeError`` 上崩掉。
    转义成 ``\\xNN`` 保住可读性与可追溯性，并把这件事如实记进报告。
    """
    if not raw:
        return "", False
    try:
        return raw.decode("utf-8"), False
    except UnicodeDecodeError:
        return raw.decode("utf-8", "backslashreplace"), True


def run_engine(pycdc: Path, pyc: bytes, idx: int,
               timeout: int) -> tuple[str, int, list[str], float, str, bool]:
    """把一段 pyc 交给外部引擎子进程。

    返回 ``(状态, 行数, stderr 首行, 耗时秒, 输出文本, 是否转义过)``。引擎崩溃或
    挂死只影响这一条：归档解密与转译结果已经拿到手，绝不因为外部工具而丢证据。
    """
    with tempfile.TemporaryDirectory() as td:
        pycf = Path(td) / f"entry_{idx}.pyc"
        pycf.write_bytes(pyc)
        t0 = time.monotonic()
        try:
            done = subprocess.run([str(pycdc), str(pycf)],  # noqa: S603
                                  capture_output=True, timeout=timeout,
                                  stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            secs = round(time.monotonic() - t0, 3)
            return "pycdc_timeout", 0, [], secs, "", False
    secs = round(time.monotonic() - t0, 3)
    text, escaped = decode_engine_output(done.stdout)
    err_raw, _ = decode_engine_output(done.stderr)
    err = err_raw.strip().splitlines()[:1]
    return (classify_pycdc(text, done.returncode, err_raw), len(
        text.splitlines()), err, secs, text, escaped)


# --------------------------------------------------------------------------
# 单条复核（子进程友好：模块级状态由 _init 注入，避免反复传 62 MB 归档）
# --------------------------------------------------------------------------

_ARCH: bytes = b""
_DB: dict = {}
_OPTS: dict = {}


def _init(arch_path: str, keys_path: str, opts: dict) -> None:
    global _ARCH, _DB, _OPTS
    _ARCH = Path(arch_path).read_bytes()
    _DB = json.loads(Path(keys_path).read_text(encoding="utf-8"))
    _OPTS = opts


def crosscheck_one(idx: int) -> dict:
    """解一条 → 交给 pycdc → 记成一条证据。失败保持可见，不做美化。"""
    o = _OPTS
    rec: dict = {"entry_index": idx}
    eid, _clen, _doff, blob = rc.read_entry(_ARCH, idx)
    rec["entry_id"] = eid
    info = _DB.get(str(idx))
    if info is None:
        rec["status"] = "no_key_in_db"
        return rec
    try:
        exp = zlib.decompress(blob)
    except zlib.error as exc:
        rec["status"] = f"zlib_fail:{exc}"
        return rec
    rec["exp_len"] = len(exp)

    if o.get("ladder"):
        got = rc.transpile(exp, info["keys"], info["bounds"],
                           "uncompyle6", True)
    else:
        # 占位那一类的密钥本来就是对的，直接走 baseline，省掉修复梯。
        pyc, fname = rc.bd._transpile_once(
            rc.bd._decode_segments(exp, info["keys"], info["bounds"]),
            exp, info["keys"], info["bounds"])
        got = {"pyc": pyc, "filename": fname, "stage": "baseline"}
    rec["stage"] = got["stage"]
    pyc = got["pyc"]
    # 成色要在这一步就记：即使本条没拿到 pyc（转译失败），磁盘上也可能已经有
    # 更早一轮救出的产物，漏记会让「零源码」被高估。
    raw_fn = got["filename"]
    rel, path_class = (("", "no_path") if raw_fn is None and pyc is None
                       else rc.resolve_rel(raw_fn, idx, eid))
    rec.update(rel_path=rel or "", path_class=path_class,
               uncompyle6=uncompyle6_state(Path(o["out"]) / rel) if rel else "unknown")
    if pyc is None:
        rec["status"] = "no_pyc"
        return rec
    rec["pyc_len"] = len(pyc)

    state, lines, err_head, secs, text, escaped = run_engine(
        Path(o["pycdc"]), pyc, idx, o["timeout"])
    rec.update(status=state, lines=lines, secs=secs, stderr_head=err_head,
               escaped_bytes=bool(escaped))

    if state in ("pycdc_ok", "pycdc_incomplete"):
        if o.get("keep_pyc"):
            kp = Path(o["keep_pyc"]) / rel
            kp.parent.mkdir(parents=True, exist_ok=True)
            kp.with_suffix(".pyc").write_bytes(pyc)
        if o.get("write"):
            dest, writable = plan_write(Path(o["out"]), rel)
            if writable:
                dest.parent.mkdir(parents=True, exist_ok=True)
                head = [f"# pycdc 交叉复核产物 · script.fls entry {idx}",
                        f"# co_filename(原始)={got['filename']!r}",
                        f"# uncompyle6 状态={rec['uncompyle6']}"
                        f"  转译阶段={got['stage']}",
                        f"# 生成时间="
                        f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
                        f"# 输入 sha256={rc.sha256(rc.SCRIPT_FLS)}"]
                if rec.get("escaped_bytes"):
                    head.append("# 注：引擎原样输出的非 UTF-8 字节已转义为 \\xNN。")
                head.append("")
                dest.write_text("\n".join(head) + text.rstrip() + "\n",
                                encoding="utf-8")
                rec["written"] = str(dest.relative_to(o["out"]))
            else:
                rec["written"] = "skipped_exists"
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True,
                    help="现有语料目录；用于判断 uncompyle6 成色，"
                         "--write 时产物写其下 pycdc/ 独立树")
    ap.add_argument("--accounting", type=Path, help="清点 JSON（含 failed 列表）")
    ap.add_argument("--class", dest="cls", default="failed",
                    help="清点 JSON 里取哪一类（默认 failed = 52 字节占位）")
    ap.add_argument("--entries", help="逗号分隔条目号；给了就优先于 --accounting")
    ap.add_argument("--script-fls", type=Path, default=rc.SCRIPT_FLS)
    ap.add_argument("--keys-db", type=Path, default=rc.KEYS_DB)
    ap.add_argument("--pycdc", help="pycdc 可执行文件路径")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--ladder", action="store_true",
                    help="baseline 转译失败时也跑完整修复梯（慢，但对无解条目更公平）")
    ap.add_argument("--write", action="store_true",
                    help="把 pycdc 产出写进 <out>/pycdc/（已存在不覆盖）")
    ap.add_argument("--keep-pyc", type=Path, help="另存复核到的 pyc 的目录")
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()

    rc.assert_out_dir_ok(args.out)
    if args.write:
        (args.out / "pycdc").mkdir(parents=True, exist_ok=True)

    if args.entries:
        idxs = sorted({int(x) for x in args.entries.replace(" ", "").split(",")})
    elif args.accounting:
        idxs = target_entries(
            json.loads(args.accounting.read_text(encoding="utf-8")), args.cls)
    else:
        raise SystemExit("要用 --accounting <清点.json> 或 --entries 指定条目")

    pycdc = resolve_pycdc(args.pycdc)
    opts = {"out": str(args.out), "pycdc": str(pycdc), "timeout": args.timeout,
            "ladder": args.ladder, "write": args.write,
            "keep_pyc": str(args.keep_pyc) if args.keep_pyc else ""}
    # 归档内容必须先确认存在，避免 workers 里重复报错。
    _init(str(args.script_fls), str(args.keys_db), opts)

    t0 = time.monotonic()
    if args.jobs > 1:
        with ProcessPoolExecutor(
                max_workers=args.jobs, initializer=_init,
                initargs=(str(args.script_fls), str(args.keys_db), opts)) as ex:
            recs = list(ex.map(crosscheck_one, idxs))
    else:
        recs = [crosscheck_one(i) for i in idxs]
    secs = round(time.monotonic() - t0, 1)

    tally: dict[str, int] = {}
    for r in recs:
        tally[r["status"]] = tally.get(r["status"], 0) + 1
    print(f"复核 {len(idxs)} 条，用时 {secs}s → {tally}")
    for key, label in (("pycdc_ok", "pycdc 完整解出（uncompyle6 没做到）"),
                       ("pycdc_incomplete", "pycdc 也只拿到部分"),
                       ("no_pyc", "连转译都没过（需 --ladder 再试）")):
        hits = [r for r in recs if r["status"] == key]
        if not hits:
            continue
        print(f"\n--- {label}: {len(hits)} 条 ---")
        for r in hits[:12]:
            print(f"  entry {r['entry_index']:4d} "
                  f"{r.get('lines', 0):>5} 行  {r.get('uncompyle6','?'):9s} "
                  f"{r.get('rel_path','(无路径)')}")
        if len(hits) > 12:
            print(f"  … 其余 {len(hits) - 12} 条见报告")
    if args.report:
        args.report.write_text(
            json.dumps({"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                        time.gmtime()),
                        "pycdc": str(pycdc), "secs": secs, "tally": tally,
                        "entries": recs},
                       ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(f"\n报告: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
