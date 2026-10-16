#!/usr/bin/env python3
"""救回「解密成功但从未落盘」的 script.fls 条目，并把失败原因写成证据。

背景（2026-10-15 诊断）：`batch_decompile.py` 对 script.fls 的 5002 个条目里，有
17 条转译其实已经拿到完整 pyc，却因为两类非算法缺陷被静默丢弃：

1. **落盘命名**：模块自身的 ``co_filename`` 含 ``\\x00`` 等非法字符（历史 5 段 XOR
   边界偏移破坏了它自己的文件名字符串），``write_text`` 抛 ``OSError``；``except``
   分支只返回记录、不写文件，于是连占位产物都没有。（2026-10-15 起 ``except``
   会在 ``script/failed/`` 留一份 ``TRANSMAP FAILED`` 明示标记，条目不再静默
   消失；但真正救回仍要靠本工具的路径清洗与转译梯。）
2. **闸门过严**：``_transpile_with_repair`` 要求「完整转译 **且** uncompyle6 成功」
   才算命中；反编译失败/病态慢（实测 ``script/core/preload/preload_mov.py``
   >900 s 不收敛）时，已解出的密钥与完整 pyc 被整条丢弃。

本工具不改 ``batch_decompile.py``（它的 SHA-256 被
``server/docs/csv_checks/agent_e_reproduction.json`` 钉死），而是以库的形式复用它的
转译与修复管线，并额外提供：

* 逐分量清洗的落盘命名（原名保留在产物头注释与 JSON 报告里，不丢可追溯性）；
* 反编译失败时退回 **marshal 结构摘要**（复用 ``tools/script_link`` 的 Py2.5
  marshal 解析器），至少恢复模块级名字、函数/类名与全部常量；
* 反编译放进**带超时的子进程**，避免个别病态条目拖死整批；
* ``no_output`` / ``decompile_timeout`` 等原因逐项写进报告，失败保持可见。

只读解析：不解压执行、不 ``eval`` 任何恢复出来的模块；原包与密钥库一律不动。

用法::

    python3 tools/decompiler/recover_entries.py --out /path/外置目录 \\
        [--entries 880,1931,... | --missing-report accounting.json] \\
        [--decompile-timeout 120] [--report report.json] [--dry-run]

``--out`` 必须位于仓库之外（或至少不在 ``data/`` 下），且不会覆盖已存在的产物。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
import time
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "decompiler"))

import batch_decompile as bd  # noqa: E402

SCRIPT_FLS = REPO_ROOT / "data" / "script.fls"
KEYS_DB = REPO_ROOT / "tools" / "decompiler" / "script_fls_keys.json"

# Windows 与 POSIX 都非法/危险的字符；控制字符一律替换为下划线。
_ILLEGAL = re.compile(r"[\x00-\x1f<>:\"|?*\x7f]")
_RESERVED = re.compile(r"^(con|prn|aux|nul|com[1-9]|lpt[1-9])$", re.I)


# --------------------------------------------------------------------------
# 落盘命名
# --------------------------------------------------------------------------


def sanitize_component(name: str) -> str:
    """清洗单个路径分量：去掉非法字符、收尾点空格，保留可读性。"""
    cleaned = _ILLEGAL.sub("_", name)
    cleaned = cleaned.strip(" .")
    if not cleaned:
        return ""
    if _RESERVED.match(cleaned.split(".")[0]):
        cleaned = "_" + cleaned
    return cleaned


def sanitize_rel(rel: str) -> str:
    """按分量清洗包内路径；空分量直接丢弃。"""
    parts = [sanitize_component(p) for p in rel.replace("\\", "/").split("/")]
    return "/".join(p for p in parts if p)


def needs_renaming(rel: str) -> bool:
    """判断包内自报文件名是否需要清洗（不碰文件系统，避免误覆盖既有产物）。"""
    parts = [p for p in rel.replace("\\", "/").split("/") if p]
    if not parts or ".." in parts:
        return False
    return any(_ILLEGAL.search(p) or p != p.strip(" .") for p in parts)


# 清洗后仍应像一条正常的包内路径；不像的（co_filename 被同一批字节错误打断）
# 统一收进 script/mangled/，避免在半截目录里散落难以发现的产物。
_PATHLIKE = re.compile(r"^script(/[A-Za-z0-9_.\-]+)+\.py$")


def mangled_rel(idx: int, entry_id: int) -> str:
    return f"script/mangled/entry_{idx:04d}_{entry_id:08x}.py"


def resolve_rel(raw_fn: str | None, idx: int, entry_id: int) -> tuple[str, str]:
    """返回 ``(落盘相对路径, 归类)``；归类 ∈ {ok, renamed, mangled, unknown}。

    ``unknown``（包内没给出文件名）刻意沿用 ``batch_decompile`` 的
    ``script/unknown/entry_*`` 位置，避免同一条目在两个目录里各存一份。
    """
    if not raw_fn:
        return f"script/unknown/entry_{idx:04d}_{entry_id:08x}.py", "unknown"
    rel = sanitize_rel(raw_fn)
    if _PATHLIKE.match(rel):
        same = rel == raw_fn.replace("\\", "/")
        return rel, ("ok" if same else "renamed")
    return mangled_rel(idx, entry_id), "mangled"


# --------------------------------------------------------------------------
# 归档读取与转译
# --------------------------------------------------------------------------


def read_entry(arch: bytes, idx: int) -> tuple[int, int, int, bytes]:
    """返回 ``(entry_id, clen, doff, stored_bytes)``。"""
    count = struct.unpack_from("<I", arch, 4)[0]
    idx_off = struct.unpack_from("<I", arch, 8)[0]
    if not 0 <= idx < count:
        raise ValueError(f"条目号 {idx} 越界（包内共 {count} 条）")
    eid, r1, r2, r3 = struct.unpack_from("<IIII", arch, idx_off + idx * 16)
    clen = (((r1 * eid + 0x0DF25E) & 0xFFFFFFFF) ^ r2) & 0xFFFFFFFF
    doff = (((r2 * idx * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF) ^ r3) & 0xFFFFFFFF
    return eid, clen, doff, arch[doff : doff + clen]


def transpile(exp: bytes, keys: list[int], bounds: list[int], engine: str,
               decode_big5: bool) -> dict:
    """逐级尝试转译，返回中间结果而不做「必须反编译成功」的整条否决。

    与 ``_transpile_with_repair`` 的区别：各级只要拿到 pyc 就交回上层，
    反编译能否成功由调用方单独决定并记录。
    """
    steps = []
    dec = bd._decode_segments(exp, keys, bounds)
    pyc, fname = bd._transpile_once(dec, exp, keys, bounds)
    steps.append(f"baseline:progress={bd._strict_progress(dec)}/{len(exp) + 1}")
    if pyc is not None:
        return {"pyc": pyc, "filename": fname, "keys": keys, "bounds": bounds,
                "repaired": False, "stage": "baseline", "steps": steps}

    # 缝口精修：batch_decompile 只在 solve 之后才用它，但 catalog 密钥常常
    # 已 100% 走通、只差缝位没细化（本仓库 entry 4305 即这一类）。放在最
    # 便宜的一级，命中即免掉后面的移位搜索。
    refined = bd._refine_seams(exp, keys, bounds)
    if refined != list(bounds):
        pyc, fname = bd._transpile_once(
            bd._decode_segments(exp, keys, refined), exp, keys, refined)
        steps.append("refine:hit" if pyc is not None else "refine:miss")
        if pyc is not None:
            return {"pyc": pyc, "filename": fname, "keys": keys,
                    "bounds": refined, "repaired": False, "bounds_refined": True,
                    "stage": "seam_refine", "steps": steps}

    shifted = bd._repair_by_shifting(exp, keys, bounds, engine, decode_big5)
    if shifted is not None:
        return {"pyc": shifted[0], "filename": shifted[1], "keys": shifted[2],
                "bounds": shifted[3], "repaired": True, "stage": "seam_shift",
                "steps": steps + ["shift:hit"]}

    solved = bd._resolve_segments(exp) or bd._beam_resolve(exp)
    if solved is None:
        return {"pyc": None, "filename": None, "keys": keys, "bounds": bounds,
                "repaired": False, "stage": "unresolved",
                "steps": steps + ["shift:miss", "resolve:miss"]}
    sk, sb = solved
    sb = bd._refine_seams(exp, sk, sb)
    pyc, fname = bd._transpile_once(bd._decode_segments(exp, sk, sb), exp, sk, sb)
    if pyc is None:
        return {"pyc": None, "filename": None, "keys": sk, "bounds": sb,
                "repaired": False, "stage": "resolved_transpile_fail",
                "steps": steps + ["resolve:keys_ok", "transpile:fail"]}
    return {"pyc": pyc, "filename": fname, "keys": sk, "bounds": sb,
            "repaired": True, "stage": "resolved",
            "steps": steps + ["resolve:hit", "transpile:ok"]}


def structural_digest(pyc: bytes) -> str:
    """反编译失败时的兜底：从标准 Py2.5 pyc 里挖出结构摘要（非源码）。"""
    link_dir = str(REPO_ROOT / "tools" / "script_link")
    if link_dir not in sys.path:
        sys.path.insert(1, link_dir)
    import build_script_index as bsi

    root = bsi.parse_pyc(pyc)
    lines = ["# marshal 结构摘要（uncompyle6 未产出可用源码时的兜底，非源码）"]
    names = [bsi.decode_text(n) for n in root.names]
    lines.append(f"# co_names({len(names)}): " + ", ".join(names[:40])
                 + (" …" if len(names) > 40 else ""))
    globals_ = sorted({n for n in names if n.isupper()})[:60]
    lines.append(f"# 全局名: {', '.join(globals_)}")
    consts = []
    for c in root.consts:
        if isinstance(c, bytes):
            consts.append(repr(bsi.decode_text(c)))
        elif isinstance(c, (int, float, bool)) or c is None:
            consts.append(repr(c))
        else:
            consts.append(f"<{type(c).__name__}>")
    lines.append(f"# co_consts({len(consts)}): " + ", ".join(consts[:60])
                 + (" …" if len(consts) > 60 else ""))
    subs = [n for n in names if not n.isupper()]
    if subs:
        lines.append(f"# 疑似函数/属性名: {', '.join(sorted(set(subs))[:60])}")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# 反编译（子进程 + 超时）
# --------------------------------------------------------------------------

_CHILD = """
import sys
sys.path.insert(0, {decompiler!r})
import batch_decompile as bd
pyc = open({pyc_path!r}, 'rb').read()
ok, engine, src = bd.decompile_pyc_bytes(pyc, engine={engine!r},
                                         decode_big5={decode_big5!r})
open({out_path!r}, 'w', encoding='utf-8').write(src)
print('OK' if ok else 'FAIL', engine)
"""


def decompile_isolated(pyc: bytes, engine: str, decode_big5: bool,
                       timeout: int) -> tuple[str | None, str]:
    """把 uncompyle6 放进带超时的子进程；返回 (源码或 None, 状态)。"""
    import tempfile

    with tempfile.TemporaryDirectory(prefix="mxsj-dec-") as td:
        tmp = Path(td)
        pyc_path, out_path = tmp / "in.pyc", tmp / "out.py"
        pyc_path.write_bytes(pyc)
        code = _CHILD.format(decompiler=str(REPO_ROOT / "tools" / "decompiler"),
                             pyc_path=str(pyc_path), out_path=str(out_path),
                             engine=engine, decode_big5=decode_big5)
        try:
            proc = subprocess.run([sys.executable, "-c", code],
                                  capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return None, "decompile_timeout"
        if proc.returncode != 0:
            return None, f"decompile_crash:{proc.stderr.strip()[:120]}"
        src = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
        first = (proc.stdout or "").strip().splitlines()
        verdict = first[0] if first else ""
        if verdict.startswith("FAIL") or "Decompilation failed" in src:
            return (src or None), "decompile_fail"
        return (src or None), "decompile_ok"


# --------------------------------------------------------------------------
# 输出与守卫
# --------------------------------------------------------------------------


def assert_out_dir_ok(out: Path) -> None:
    """拒绝写进仓库的输入资源区，避免覆盖原包（AGENTS §4 第 1 条）。"""
    resolved = out.resolve()
    data_dir = (REPO_ROOT / "data").resolve()
    if resolved == data_dir or data_dir in resolved.parents:
        raise SystemExit(f"拒绝写入原包目录: {resolved}")
    if resolved == REPO_ROOT:
        raise SystemExit(f"拒绝把产物写进仓库根目录: {resolved}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def recover(idx: int, arch: bytes, db: dict, out: Path, engine: str,
             decode_big5: bool, timeout: int, dry_run: bool) -> dict:
    """处理单个条目，返回一条证据记录。"""
    rec: dict = {"entry_index": idx}
    eid, clen, doff, blob = read_entry(arch, idx)
    rec.update(entry_id=eid, clen=clen, doff=doff,
               stored_sha256=hashlib.sha256(blob).hexdigest()[:16])
    info = db.get(str(idx))
    if info is None:
        rec["status"] = "no_key_in_db"
        return rec
    try:
        exp = zlib.decompress(blob)
    except zlib.error as exc:
        rec["status"] = f"zlib_fail:{exc}"
        return rec
    rec["exp_len"] = len(exp)

    got = transpile(exp, info["keys"], info["bounds"], engine, decode_big5)
    rec.update(stage=got["stage"], repaired=got["repaired"],
               bounds_refined=got.get("bounds_refined", False),
               steps=got["steps"],
               keys_used=got["keys"], bounds_used=got["bounds"])
    pyc = got["pyc"]
    if pyc is None:
        rec["status"] = "untranspilable"
        return rec
    rec["pyc_len"] = len(pyc)

    raw_fn = got["filename"]
    rel, path_class = resolve_rel(raw_fn, idx, eid)
    rec.update(co_filename=raw_fn, rel_path=rel,
               renamed=path_class != "ok", path_class=path_class)

    src, dstate = (None, "skipped") if dry_run else decompile_isolated(
        pyc, engine, decode_big5, timeout)
    rec["decompile"] = dstate
    out_py = out / rel

    if dry_run:
        rec["status"] = "dry_run"
        return rec

    out_py.parent.mkdir(parents=True, exist_ok=True)
    if out_py.exists():
        rec["status"] = "exists_skipped"
        return rec

    head = [f"# MXSJ 恢复产物 · script.fls entry {idx} (id=0x{eid:08x})",
            f"# co_filename(原始)={raw_fn!r}",
            f"# 转译阶段={got['stage']}  密钥修复={got['repaired']}",
            f"# keys={got['keys']} bounds={got['bounds']}",
            f"# 生成时间={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
            f"# 输入 sha256={sha256(SCRIPT_FLS)}", ""]
    if src and dstate == "decompile_ok":
        body = src
        kind = "source"
    elif src:
        body = src + "\n" + structural_digest(pyc)
        kind = "source_partial+digest"
    else:
        body = structural_digest(pyc)
        kind = "digest_only"
    if path_class != "ok":
        head.append(f"# 注意：包内自报文件名已清洗（{path_class}）；原名见上文。")
    out_py.write_text("\n".join(head) + body, encoding="utf-8")
    if not src:  # 反编译没产出源码时保留 pyc，供后续工具重试
        out_py.with_suffix(".pyc").write_bytes(pyc)
    rec["status"] = "recovered"
    rec["kind"] = kind
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True, help="产物目录（仓库外）")
    ap.add_argument("--entries", help="逗号分隔条目号；缺省用 --missing-report")
    ap.add_argument("--missing-report", type=Path, help="清点 JSON 的 missing 列表")
    ap.add_argument("--script-fls", type=Path, default=SCRIPT_FLS)
    ap.add_argument("--keys-db", type=Path, default=KEYS_DB)
    ap.add_argument("--engine", default="uncompyle6",
                    choices=["auto", "uncompyle6", "pycdc"])
    ap.add_argument("--decompile-timeout", type=int, default=120)
    ap.add_argument("--no-big5", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="只判定不落盘")
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()

    if args.entries:
        want = [int(x) for x in re.split(r"[,\s]+", args.entries.strip()) if x]
    elif args.missing_report:
        want = [int(x) for x in json.loads(
            args.missing_report.read_text(encoding="utf-8"))["missing"]]
    else:
        ap.error("需要 --entries 或 --missing-report")
        return 2

    assert_out_dir_ok(args.out)
    args.out.mkdir(parents=True, exist_ok=True)
    arch = args.script_fls.read_bytes()
    db = json.loads(args.keys_db.read_text(encoding="utf-8"))

    t0 = time.time()
    results = [recover(i, arch, db, args.out, args.engine,
                       not args.no_big5, args.decompile_timeout, args.dry_run)
               for i in want]
    by = {}
    for r in results:
        by[r["status"]] = by.get(r["status"], 0) + 1
    print(f"处理 {len(results)} 条，用时 {time.time() - t0:.1f}s → {by}")
    for r in results:
        shown = r.get("rel_path") or r.get("co_filename") or "-"
        print(f"  entry {r['entry_index']:>5}  {r['status']:<18} "
              f"{r.get('kind', ''):<22} {shown}")
    if args.report:
        args.report.write_text(json.dumps(
            {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
             "script_fls_sha256": sha256(args.script_fls),
             "out_dir": str(args.out), "dry_run": args.dry_run,
             "counts": by, "entries": results},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"报告: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
