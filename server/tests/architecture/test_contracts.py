"""Architecture smoke tests only; no gameplay or network implementation is tested."""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, is_dataclass
import hashlib
import importlib
import inspect
import json
from pathlib import Path
import sys
import typing
import unittest

SERVER = Path(__file__).resolve().parents[2]
REPO = SERVER.parent
SRC = SERVER / "src"
sys.path.insert(0, str(SRC))
from mxsj_server.contracts.common import CommandSource, RequestContext

MODULES = {
    "account", "character", "economy", "inventory", "crafting", "world", "npc",
    "battle", "skill", "pet", "children", "quest", "party", "guild", "social",
    "mail", "trade", "housing", "activity", "appearance", "administration",
}


def import_violations(source: str, current_module: str, is_domain: bool) -> list[str]:
    """Small static check, not a sandbox; dynamic imports require code review."""
    errors = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                errors.append("relative imports require explicit review; use absolute imports")
                continue
            names = [node.module or ""]
            # Also catch `from mxsj_server.modules.other import application`.
            names.extend(f"{node.module}.{a.name}" for a in node.names)
        else:
            continue
        for name in names:
            prefix = "mxsj_server.modules."
            if name.startswith(prefix):
                tail = name[len(prefix):].split(".")
                if tail[0] != current_module and (len(tail) < 2 or tail[1] != "contracts"):
                    # The bare module part of `from other.contracts import DTO` is allowed;
                    # `from other import contracts` is intentionally not accepted.
                    errors.append(f"private cross-module import: {name}")
            if is_domain and (
                name.split(".")[0] in {"sqlalchemy", "asyncpg", "fastapi", "socket", "pygame"}
                or name.startswith(("mxsj_server.transport", "mxsj_server.persistence", "mxsj_server.protocol"))
            ):
                errors.append(f"infrastructure import in domain: {name}")
    return errors


class ContractTests(unittest.TestCase):
    def test_module_directories(self):
        actual = {p.name for p in (SRC / "mxsj_server/modules").iterdir() if p.is_dir() and not p.name.startswith("_")}
        self.assertEqual(actual, MODULES)
        for name in MODULES:
            base = SRC / "mxsj_server/modules" / name
            for path in ["README.md", "contracts.py", "domain/__init__.py", "application/__init__.py", "adapters/__init__.py"]:
                self.assertTrue((base / path).is_file(), (name, path))
            self.assertTrue((SERVER / "tests/modules" / name).is_dir())

    def test_all_python_files_compile(self):
        for path in SERVER.rglob("*.py"):
            with self.subTest(path=path):
                compile(path.read_text(encoding="utf-8"), str(path), "exec")

    def test_public_contracts_import_and_resolve_types(self):
        for name in MODULES:
            mod = importlib.import_module(f"mxsj_server.modules.{name}.contracts")
            protocols = []
            for value in vars(mod).values():
                if not inspect.isclass(value) or value.__module__ != mod.__name__:
                    continue
                typing.get_type_hints(value)
                if is_dataclass(value):
                    self.assertTrue(value.__dataclass_params__.frozen)
                    for field in fields(value):
                        hint = typing.get_type_hints(value)[field.name]
                        self.assertIsNot(hint, typing.Any, (name, field.name))
                if getattr(value, "_is_protocol", False):
                    protocols.append(value)
                    methods = [v for k, v in vars(value).items() if not k.startswith("_") and inspect.isfunction(v)]
                    self.assertTrue(methods)
                    for method in methods:
                        self.assertTrue(inspect.iscoroutinefunction(method))
                        self.assertIn("return", typing.get_type_hints(method))
            self.assertTrue(protocols, name)

    def test_context_is_frozen(self):
        ctx = RequestContext(operation_id="op-test", trace_id="trace-test", realm_id=1,
                             account_id=1, character_id=2, session_epoch=1, source=CommandSource.CLIENT)
        with self.assertRaises(FrozenInstanceError):
            ctx.realm_id = 2

    def test_credential_repr_redaction(self):
        from mxsj_server.modules.account.contracts import LoginRequest, LoginResult
        self.assertNotIn("do-not-log-this", repr(LoginRequest(account_name="a", credential=b"do-not-log-this", protocol_version="legacy")))
        self.assertNotIn("do-not-log-this", repr(LoginResult(account_id=1, session_ticket="do-not-log-this", expires_at_ms=1)))

    def test_battle_view_has_no_internal_secrets(self):
        from mxsj_server.modules.battle.contracts import BattleView
        names = {f.name for f in fields(BattleView)}
        self.assertFalse(names & {"rng_state", "seed", "enemy_commands", "locked_commands"})
        self.assertIn("submitted_own_unit_ids", names)

    def test_static_module_boundaries(self):
        for name in MODULES:
            for p in (SRC / "mxsj_server/modules" / name).rglob("*.py"):
                errors = import_violations(p.read_text(), name, "domain" in p.relative_to(SRC).parts)
                self.assertEqual(errors, [], (str(p), errors))

    def test_boundary_checker_negative_examples(self):
        self.assertTrue(import_violations("from mxsj_server.modules.economy.application import service", "mail", False))
        self.assertTrue(import_violations("from mxsj_server.modules.economy import adapters", "mail", False))
        self.assertTrue(import_violations("import sqlalchemy", "mail", True))
        self.assertEqual(import_violations("from mxsj_server.modules.economy.contracts import EconomyAPI", "mail", False), [])

    def test_source_map_coverage_and_provenance(self):
        data = json.loads((SERVER / "docs/source_map.json").read_text())
        self.assertEqual({m["module"] for m in data["modules"]}, MODULES)
        archive = REPO / data["archive"]
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), data["archive_sha256"],
                         "Archive changed: review/rebuild source provenance before using this map")
        catalog = {r["index"]: r for r in map(json.loads, (REPO / data["catalog"]).read_text().splitlines())}
        for module in data["modules"]:
            self.assertTrue(module["references"])
            for ref in module["references"]:
                self.assertIn(ref["entry_index"], catalog)
                self.assertEqual(ref["historical_decode_status"], catalog[ref["entry_index"]]["status"])
                self.assertEqual(ref["current_check"], "marshal_transpiled_filename_checked")
                self.assertTrue(ref["current_filename"].startswith("script/"))

    def test_no_pygame_dependency(self):
        for p in SRC.rglob("*.py"):
            for node in ast.walk(ast.parse(p.read_text())):
                if isinstance(node, ast.Import):
                    self.assertFalse(any(a.name.split(".")[0] == "pygame" for a in node.names))
                if isinstance(node, ast.ImportFrom):
                    self.assertNotEqual((node.module or "").split(".")[0], "pygame")


if __name__ == "__main__":
    unittest.main()
