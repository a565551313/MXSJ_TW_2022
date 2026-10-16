"""N1 签名/回执纯元数据回归（不打开原包、不执行任何游戏代码）。

运行（仓库根目录）：
    python3 -m unittest discover -s script_manual/inventory -p 'test_*.py' -v

分三层：
1. 合成码对象：普通、仅 *args、仅 **kwargs（有/无位置形参）、两者都有、
   编译器内部槽（生成器表达式 .0 / 匿名 tuple 形参 .N）、乱码形参；
2. 独立口径：CPython 自己编译的函数（无仅关键字形参时布局与 Python 2 一致）
   交给 inspect.signature 渲染，作为与实现无关的对照；真实生成器表达式提供 .0；
3. 交付数据：modules.jsonl / 回执 / 回归报告互相核对，并对照 A 的 BDF 机器收据
   （若存在）逐条复核 70 条裸 * 与 48 条内部槽。
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import inspect
import json
import re
import struct
import sys
import unittest
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRIPT_SHA = "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72"
DATA_SHA = "5f96bdb23d4555c8014ac4a4a65819f48a3251b95a8cc94dff09ee7e2cc0a12c"
BDF_RECEIPT = ROOT / "docs/evidence/script_manual_BDF_A_validation_20261016.json"
OLD_CATALOG = ROOT / "server/docs/catalog/script_entries.jsonl"
WELLFORMED_TOKEN = re.compile(r"(\*\*|\*)?[A-Za-z_][A-Za-z0-9_]*")


def _load_extractor():
    name = "mxsj_inventory_extract_inventory_under_test"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            name, HERE / "extract_inventory.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module  # dataclass 解析注解时按模块名回查
        spec.loader.exec_module(module)
    return sys.modules[name]


xi = _load_extractor()  # 只加载函数定义；main() 不会运行
mt = importlib.import_module("script_editor.core.vm.marshal_tree")

CO_OPTIMIZED_NEWLOCALS = 0x03
CO_VARARGS = 0x04
CO_VARKEYWORDS = 0x08
CO_GENERATOR = 0x20
# Python 2 标准操作码（data 侧传入 classify_children 前即为标准码）
POP_TOP, BUILD_CLASS, STORE_NAME = 1, 89, 90
LOAD_CONST, CALL_FUNCTION, MAKE_FUNCTION = 100, 131, 132


def name_atom(value: bytes | str):
    raw = value if isinstance(value, bytes) else value.encode("utf-8")
    return mt.Atom(b"t", b"", raw)


def make_code(
    argcount: int,
    flags: int,
    varnames,
    *,
    name: str = "f",
    consts=(),
    code: bytes = b"",
):
    """只含元数据的合成码对象；字节码默认为空（签名判定不读字节码）。"""
    group = mt.Group(b"(", tuple(name_atom(v) for v in varnames))
    empty = mt.Group(b"(", ())
    fields = (
        mt.Group(b"(", tuple(consts)),
        empty,
        group,
        empty,
        empty,
        name_atom("synthetic.py"),
        name_atom(name),
    )
    header = struct.pack("<iiii", argcount, len(varnames), 1, flags)
    return mt.Code(header, code, fields, b"\0\0\0\0", b"")


def op(opcode: int, arg: int | None = None) -> bytes:
    if arg is None:
        return bytes([opcode])
    return bytes([opcode, arg & 0xFF, arg >> 8])


def tokens(signature: str) -> list[str]:
    inner = signature[1:-1]
    return inner.split(", ") if inner else []


class FiveClassSignatureTest(unittest.TestCase):
    """任务卡要求的五类：普通、*args、**kwargs、两者、内部槽。"""

    def check(self, node, expected, status, counter_key=None):
        counter = Counter()
        self.assertEqual(xi.signature_of(node, counter), expected)
        self.assertEqual(xi.check_signature(node).status, status)
        if counter_key:
            self.assertEqual(counter[counter_key], 1)
        if expected is not None:
            self.assertTrue(xi.signature_is_wellformed(expected))
        return counter

    def test_ordinary(self):
        node = make_code(2, CO_OPTIMIZED_NEWLOCALS, ["a", "b", "local"])
        counter = self.check(node, "(a, b)", "confirmed")
        self.assertEqual(sum(counter.values()), 0)

    def test_varargs_only(self):
        node = make_code(2, 0x03 | CO_VARARGS, ["a", "b", "args", "t"])
        counter = self.check(node, "(a, b, *args)", "confirmed")
        self.assertEqual(counter["signature_kwargs_only"], 0)

    def test_kwargs_only_with_positional_has_no_bare_star(self):
        node = make_code(2, 0x03 | CO_VARKEYWORDS, ["self", "path", "dct"])
        self.check(node, "(self, path, **dct)", "confirmed", "signature_kwargs_only")

    def test_kwargs_only_without_positional_has_no_bare_star(self):
        node = make_code(0, 0x03 | CO_VARKEYWORDS, ["kwargs"])
        self.check(node, "(**kwargs)", "confirmed", "signature_kwargs_only")

    def test_varargs_and_kwargs(self):
        node = make_code(
            2, 0x03 | CO_VARARGS | CO_VARKEYWORDS, ["a", "b", "args", "kw", "x"]
        )
        counter = self.check(node, "(a, b, *args, **kw)", "confirmed")
        self.assertEqual(counter["signature_kwargs_only"], 0)
        node = make_code(0, 0x03 | CO_VARARGS | CO_VARKEYWORDS, ["args", "kw"])
        self.check(node, "(*args, **kw)", "confirmed")

    def test_internal_slot_generator_expression(self):
        node = make_code(1, 0x03 | CO_GENERATOR, [".0", "x"], name="<genexpr>")
        self.check(node, None, "rejected", "signature_rejected_compiler_internal_slot")
        check = xi.check_signature(node)
        self.assertEqual(check.raw, "(.0)")
        self.assertEqual(check.slot_names, (".0",))
        self.assertEqual(check.reason, "compiler_internal_slot")

    def test_internal_slot_tuple_parameters(self):
        # inspect.BlockFinder.tokeneater(self, type, token, (srow, scol), ...)
        names = ["self", "type", "token", ".3", ".4", "line", "srow", "scol"]
        node = make_code(6, 0x03, names)
        self.check(node, None, "rejected", "signature_rejected_compiler_internal_slot")
        check = xi.check_signature(node)
        self.assertEqual(check.raw, "(self, type, token, .3, .4, line)")
        self.assertEqual(check.slot_names, (".3", ".4"))
        # 带 **kw 的内部槽同样置 null，不因 kwargs 规则被放行
        node = make_code(2, 0x03 | CO_VARKEYWORDS, ["self", ".1", "kw"])
        self.check(node, None, "rejected", "signature_rejected_compiler_internal_slot")


class RejectedParameterNameTest(unittest.TestCase):
    def assert_rejected(self, varnames, argcount, reason="non_identifier_parameter"):
        node = make_code(argcount, 0x03, varnames)
        counter = Counter()
        self.assertIsNone(xi.signature_of(node, counter))
        check = xi.check_signature(node)
        self.assertEqual((check.status, check.reason), ("rejected", reason))
        self.assertEqual(counter[f"signature_rejected_{reason}"], 1)
        return check

    def test_seam_garbled_bytes_keep_raw_clue(self):
        check = self.assert_rejected([b"\x89elf", b"x"], 2)
        self.assertEqual(check.raw, "(\\x89elf, x)")
        self.assertEqual(check.non_identifier, (("\\x89elf", "89656c66"),))

    def test_control_characters_and_punctuation(self):
        self.assert_rejected(["self", "1\x17($6", "pContext"], 3)
        self.assert_rejected(["self", "pSkillM24:cDlg"], 2)

    def test_trailing_newline_is_not_an_identifier(self):
        # re.match(r"^...$") 会放过结尾换行；形参判定必须 fullmatch
        self.assert_rejected(["self\n"], 1)

    def test_non_ascii_letters_are_not_python2_identifiers(self):
        self.assert_rejected(["数据"], 1)

    def test_empty_name(self):
        self.assert_rejected([""], 1)

    def test_slot_wins_over_garbled_reason(self):
        check = self.assert_rejected([".0", "\x01x"], 2, "compiler_internal_slot")
        self.assertEqual(check.slot_names, (".0",))
        self.assertEqual(len(check.non_identifier), 1)


class InconsistentMetadataTest(unittest.TestCase):
    def test_argcount_exceeds_varnames(self):
        counter = Counter()
        self.assertIsNone(xi.signature_of(make_code(3, 0x03, ["a"]), counter))
        self.assertEqual(counter["signature_unavailable"], 1)

    def test_flags_without_names(self):
        for flags in (CO_VARARGS, CO_VARKEYWORDS, CO_VARARGS | CO_VARKEYWORDS):
            counter = Counter()
            node = make_code(1, 0x03 | flags, ["a"])
            self.assertIsNone(xi.signature_of(node, counter))
            self.assertEqual(counter["signature_unavailable"], 1)

    def test_negative_argcount(self):
        self.assertEqual(
            xi.check_signature(make_code(-1, 0x03, ["a"])).status, "unavailable"
        )


def _f_ordinary(a, b):
    local = a
    return local


def _f_varargs(a, b, *args):
    return args


def _f_kwargs(a, b, **kwargs):
    return kwargs


def _f_kwargs_alone(**kwargs):
    return kwargs


def _f_both(a, b, *args, **kwargs):
    return args, kwargs


def _f_both_alone(*args, **kwargs):
    return args, kwargs


def _f_empty():
    return None


class IndependentOracleTest(unittest.TestCase):
    """对照 CPython 编译器 + inspect.signature，不复用被测实现的任何逻辑。"""

    FUNCTIONS = (
        _f_ordinary,
        _f_varargs,
        _f_kwargs,
        _f_kwargs_alone,
        _f_both,
        _f_both_alone,
        _f_empty,
    )

    @staticmethod
    def as_metadata(code):
        return make_code(
            code.co_argcount, code.co_flags, list(code.co_varnames), name=code.co_name
        )

    def test_layout_matches_cpython_inspect(self):
        for func in self.FUNCTIONS:
            code = func.__code__
            with self.subTest(func=func.__name__):
                self.assertEqual(code.co_kwonlyargcount, 0)  # Python 2 公共子集
                self.assertEqual(code.co_posonlyargcount, 0)
                expected = str(inspect.signature(func))
                got = xi.signature_of(self.as_metadata(code), Counter())
                self.assertEqual(got, expected)
                self.assertNotIn("*", tokens(expected))

    def test_real_generator_expression_slot_is_rejected(self):
        generator = (item for item in ())
        code = generator.gi_code
        self.assertEqual(code.co_varnames[: code.co_argcount], (".0",))
        check = xi.check_signature(self.as_metadata(code))
        self.assertEqual(
            (check.status, check.reason), ("rejected", "compiler_internal_slot")
        )
        self.assertEqual(check.raw, "(.0)")


class ExtractFunctionsRecordTest(unittest.TestCase):
    """被拒签名只把 signature 置 null：函数记录、限定名与 kind 全部保留。"""

    def build_module(self):
        genexpr = make_code(1, 0x03 | CO_GENERATOR, [".0", "x"], name="<genexpr>")
        func = make_code(
            1,
            0x03 | CO_VARKEYWORDS,
            ["a", "kw"],
            name="f",
            consts=(genexpr,),
            code=op(LOAD_CONST, 0) + op(MAKE_FUNCTION, 0) + op(POP_TOP),
        )
        method = make_code(2, 0x03, ["self", ".1", "x", "y"], name="m")
        body = make_code(
            0,
            0x02,
            [],
            name="C",
            consts=(method,),
            code=op(LOAD_CONST, 0) + op(MAKE_FUNCTION, 0) + op(STORE_NAME, 0),
        )
        module_code = (
            op(LOAD_CONST, 0)
            + op(MAKE_FUNCTION, 0)
            + op(CALL_FUNCTION, 0)
            + op(BUILD_CLASS)
            + op(STORE_NAME, 0)
            + op(LOAD_CONST, 1)
            + op(MAKE_FUNCTION, 0)
            + op(STORE_NAME, 1)
        )
        return make_code(
            0, 0x00, [], name="<module>", consts=(body, func), code=module_code
        )

    def test_records_kept_and_audited(self):
        counter = Counter()
        sink = []
        records = xi.extract_functions(self.build_module(), "py27", counter, sink)
        by_name = {r["name"]: r for r in records}
        self.assertEqual(
            by_name,
            {
                "C": {"name": "C", "signature": None, "kind": "class"},
                "C.m": {"name": "C.m", "signature": None, "kind": "method"},
                "f": {"name": "f", "signature": "(a, **kw)", "kind": "function"},
                "f.<genexpr>": {
                    "name": "f.<genexpr>",
                    "signature": None,
                    "kind": "function",
                },
            },
        )
        self.assertEqual(counter["kind_fallback"], 0)
        self.assertEqual(counter["signatures"], 1)
        self.assertEqual(counter["signature_rejected_compiler_internal_slot"], 2)
        self.assertEqual(counter["signature_kwargs_only"], 1)
        audited = {(name, kind, check.status, check.raw) for name, kind, check in sink}
        self.assertEqual(
            audited,
            {
                ("C.m", "method", "rejected", "(self, .1)"),
                ("f", "function", "confirmed", "(a, **kw)"),
                ("f.<genexpr>", "function", "rejected", "(.0)"),
            },
        )


class WellformedHelperTest(unittest.TestCase):
    def test_accepts_python2_lists(self):
        for sig in ("()", "(a)", "(a, *b)", "(a, **c)", "(*b, **c)", "(a, b, *c, **d)"):
            self.assertTrue(xi.signature_is_wellformed(sig), sig)

    def test_rejects_defects(self):
        for sig in (
            "(a, *, **c)",
            "(*, **c)",
            "(.0)",
            "(a, .1)",
            "(\\x89elf)",
            "(**c, a)",
            "(*b, *c)",
            "(**c, *b)",
            "(a,b)",
            "a, b",
        ):
            self.assertFalse(xi.signature_is_wellformed(sig), sig)


class RejectedFallbackTest(unittest.TestCase):
    SHA = "0" * 64

    def test_clean_value_is_used(self):
        row = {"index_filename": "script\\a\\b.py", "historical_filename": "x.py"}
        self.assertEqual(xi.rejected_fallback(row, self.SHA), ("script/a/b.py", None))

    def test_precedence_and_empty(self):
        row = {"index_filename": "", "historical_filename": "script/h.py"}
        self.assertEqual(xi.rejected_fallback(row, self.SHA), ("script/h.py", None))
        self.assertEqual(xi.rejected_fallback({}, self.SHA), ("", None))

    def test_control_characters_record_original(self):
        original = "script/reddotsys/redpoint\rool/x.py"
        used, record = xi.rejected_fallback({"index_filename": original}, self.SHA)
        self.assertEqual(used, "")
        self.assertEqual(record["original_value"], original)
        self.assertEqual(record["field"], "index_filename")
        self.assertEqual(record["source_sha256"], self.SHA)
        self.assertEqual(
            record["control_characters"], [{"offset": 25, "codepoint": "U+000D"}]
        )
        self.assertEqual(
            bytes.fromhex(record["original_value_utf8_hex"]).decode(), original
        )
        self.assertIn("\\r", json.dumps(record["original_value"]))


class AuditedArchiveRefusalTest(unittest.TestCase):
    def test_excluded_entry_is_logged_then_refused(self):
        archive = xi.AuditedArchive.__new__(xi.AuditedArchive)  # 不打开任何文件
        archive.excluded = frozenset({1288})
        archive.read_stored_calls = Counter()
        with self.assertRaises(PermissionError):
            archive.read_stored(1288)
        self.assertEqual(archive.read_stored_calls[1288], 1)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DeliveredInventoryTest(unittest.TestCase):
    """交付的 modules.jsonl 与回执/回归报告互相一致；只读 JSON，不读原包。"""

    @classmethod
    def setUpClass(cls):
        cls.rows = []
        with (HERE / "modules.jsonl").open(encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    cls.rows.append(json.loads(line))
        cls.receipt = json.loads(
            (HERE / "B_extraction_receipt.json").read_text(encoding="utf-8")
        )
        cls.by_key = defaultdict(list)
        for row in cls.rows:
            for func in row["functions"]:
                key = (row["archive_sha256"], row["entry_index"], func["name"])
                cls.by_key[key].append(func["signature"])

    def test_identities_and_record_counts(self):
        keys = [(r["archive_sha256"], r["entry_index"]) for r in self.rows]
        self.assertEqual(len(keys), 5135)
        self.assertEqual(len(set(keys)), 5135)
        self.assertEqual(sum(len(r["functions"]) for r in self.rows), 128382)
        status = Counter((r["archive_sha256"], r["path_status"]) for r in self.rows)
        self.assertEqual(
            status,
            Counter(
                {
                    (SCRIPT_SHA, "structurally_read"): 4950,
                    (SCRIPT_SHA, "historical"): 37,
                    (SCRIPT_SHA, "unreadable"): 14,
                    (SCRIPT_SHA, "excluded_by_policy"): 1,
                    (DATA_SHA, "structurally_read"): 121,
                    (DATA_SHA, "directory"): 12,
                }
            ),
        )
        excluded = next(
            r for r in self.rows if r["path_status"] == "excluded_by_policy"
        )
        self.assertEqual(
            excluded,
            {
                "archive_sha256": SCRIPT_SHA,
                "entry_index": 1288,
                "path": None,
                "vm": "py25",
                "path_status": "excluded_by_policy",
                "functions": [],
            },
        )

    def test_every_signature_is_wellformed(self):
        bad = [
            (row["entry_index"], func["name"], func["signature"])
            for row in self.rows
            for func in row["functions"]
            if func["signature"] is not None
            and not all(
                WELLFORMED_TOKEN.fullmatch(t) for t in tokens(func["signature"])
            )
        ]
        self.assertEqual(bad, [])
        for row in self.rows:
            for func in row["functions"]:
                if func["signature"] is not None:
                    self.assertTrue(xi.signature_is_wellformed(func["signature"]))
                if func["kind"] == "class":
                    self.assertIsNone(func["signature"])

    def test_receipt_digests_match_delivered_files(self):
        self.assertEqual(
            self.receipt["modules_jsonl_sha256"], _sha256(HERE / "modules.jsonl")
        )
        self.assertEqual(
            self.receipt["sample_regression"]["sha256"],
            _sha256(HERE / "sample_regression.json"),
        )
        self.assertEqual(
            self.receipt["tools"]["extractor"]["sha256"],
            _sha256(HERE / "extract_inventory.py"),
        )
        sample = json.loads(
            (HERE / "sample_regression.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            sample["extractor_sha256"], _sha256(HERE / "extract_inventory.py")
        )
        self.assertTrue(sample["all_paths_match_seed"])
        self.assertTrue(sample["seed_source"]["is_frozen_seed_file"])
        self.assertEqual(
            sample["seed_source"]["seed_paths_from_prior_sample_regression"], 0
        )

    def test_receipt_self_checks(self):
        checks = self.receipt["self_checks"]
        self.assertEqual(checks["functions_total"], 128382)
        self.assertEqual(checks["bare_star_signatures"], 0)
        self.assertEqual(checks["internal_slot_signatures"], 0)
        self.assertTrue(checks["all_signatures_wellformed_python2"])
        self.assertTrue(checks["seed20_paths_preserved"])
        self.assertTrue(checks["seed_file_is_frozen_20_seed"])
        self.assertEqual(checks["excluded_1288_read_stored_calls"], 0)
        reads = self.receipt["read_audit"]["script"]
        self.assertEqual(reads["excluded_read_stored_calls"], 0)
        self.assertEqual(reads["distinct_entries_read"], 5001)

    def test_signature_audit_matches_inventory(self):
        audit = self.receipt["signature_audit"]
        for item in audit["rejected"]:
            key = (item["archive_sha256"], item["entry_index"], item["name"])
            self.assertIn(None, self.by_key[key], key)
            self.assertFalse(xi.signature_is_wellformed(item["raw_signature"]))
        for item in audit["kwargs_only_rendered"]:
            key = (item["archive_sha256"], item["entry_index"], item["name"])
            self.assertIn(item["signature"], self.by_key[key], key)
            self.assertNotIn("*", tokens(item["signature"]))
        reasons = Counter(item["reason"] for item in audit["rejected"])
        counts = audit["counts"]
        self.assertEqual(
            reasons["compiler_internal_slot"],
            counts["script"]["rejected_compiler_internal_slot"]
            + counts["data"]["rejected_compiler_internal_slot"],
        )
        self.assertEqual(
            len(audit["kwargs_only_rendered"]),
            counts["script"]["kwargs_only_confirmed"]
            + counts["data"]["kwargs_only_confirmed"],
        )

    def test_rejected_fallbacks_keep_originals(self):
        failures = {f["entry_index"]: f for f in self.receipt["script_failures"]}
        self.assertEqual(
            self.receipt["rejected_fallback_entries"], [880, 2310, 3078, 3122]
        )
        old = {}
        if OLD_CATALOG.exists():
            with OLD_CATALOG.open(encoding="utf-8") as stream:
                for line in stream:
                    if line.strip():
                        row = json.loads(line)
                        old[row["entry_index"]] = row
        rows = {
            r["entry_index"]: r for r in self.rows if r["archive_sha256"] == SCRIPT_SHA
        }
        for index in (880, 2310, 3078, 3122):
            record = failures[index]["fallback_rejected"]
            self.assertEqual(failures[index]["fallback"], "")
            self.assertTrue(record["original_value"])
            self.assertTrue(any(ord(ch) < 32 for ch in record["original_value"]))
            self.assertEqual(
                bytes.fromhex(record["original_value_utf8_hex"]).decode("utf-8"),
                record["original_value"],
            )
            self.assertEqual(
                (rows[index]["path"], rows[index]["path_status"]), (None, "unreadable")
            )
            if old:
                self.assertEqual(record["original_value"], old[index][record["field"]])

    def test_against_bdf_machine_receipt(self):
        if not BDF_RECEIPT.exists():
            self.skipTest("A 的 BDF 机器收据不在本树中（如打包产物）")
        bdf = json.loads(BDF_RECEIPT.read_text(encoding="utf-8"))["B"]
        audit = self.receipt["signature_audit"]
        expected_fixed = Counter(
            (
                r["archive_sha256"],
                r["entry_index"],
                r["name"],
                "(" + ", ".join(t for t in tokens(r["signature"]) if t != "*") + ")",
            )
            for r in bdf["affected_signatures"]
        )
        self.assertEqual(sum(expected_fixed.values()), 70)
        rendered = Counter(
            (i["archive_sha256"], i["entry_index"], i["name"], i["signature"])
            for i in audit["kwargs_only_rendered"]
        )
        self.assertEqual(rendered, expected_fixed)
        for (sha, index, name, sig), count in expected_fixed.items():
            self.assertGreaterEqual(self.by_key[(sha, index, name)].count(sig), count)
        expected_slots = Counter(
            (r["archive_sha256"], r["entry_index"], r["name"], r["signature"])
            for r in bdf["internal_argument_signatures"]
        )
        self.assertEqual(sum(expected_slots.values()), 48)
        rejected = Counter(
            (i["archive_sha256"], i["entry_index"], i["name"], i["raw_signature"])
            for i in audit["rejected"]
            if i["reason"] == "compiler_internal_slot"
        )
        self.assertEqual(rejected, expected_slots)
        for (sha, index, name, _sig), count in expected_slots.items():
            self.assertGreaterEqual(self.by_key[(sha, index, name)].count(None), count)
        originals = {
            item["entry_index"]: item["fallback_rejected"]["original_value"]
            for item in self.receipt["script_failures"]
            if "fallback_rejected" in item
        }
        expected_originals = {
            item["entry_index"]: item["original_historical_path"]
            for item in bdf["rejected_fallback_originals_missing_from_B_receipt"]
        }
        self.assertEqual(originals, expected_originals)


if __name__ == "__main__":
    unittest.main()
