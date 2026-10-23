from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_workflow import make_state

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.services.bundled_catalog import (
    audit_catalogs,
    bundled_catalog,
    stage_catalogs,
)


class BundledCatalogTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="mx-bundled-catalog-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.state = make_state(self.root)
        self.ref = self.state.catalogs[0]
        (self.root / "decoding").mkdir()
        self.asset = self.root / "decoding" / "script-original.json"
        self.asset.write_bytes(self.ref.path.read_bytes())
        self.rules = {self.ref.fingerprint: (self.asset.name, self.ref.sha256)}
        self.patcher = patch(
            "script_editor.core.services.bundled_catalog.BUNDLED_CATALOGS", self.rules
        )
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_exact_full_digest_only_no_filename_or_directory_guess(self):
        with ArchiveDocument(self.ref.archive) as archive:
            ref = bundled_catalog(archive, self.root)
            self.assertEqual(ref.path, self.asset)
            ref.verify(archive)
            self.rules.clear()
            self.rules["0" * 64] = (self.asset.name, self.ref.sha256)
            self.assertIsNone(bundled_catalog(archive, self.root))
        data = self.root / "data"
        data.mkdir()
        state = make_state(data, "py27")
        with ArchiveDocument(state.bindings[0].archive) as archive:
            self.assertIsNone(bundled_catalog(archive, self.root / "missing"))

    def test_missing_or_tampered_asset_never_used(self):
        with ArchiveDocument(self.ref.archive) as archive:
            self.asset.write_bytes(b"{}")
            with self.assertRaisesRegex(ValueError, "SHA256"):
                bundled_catalog(archive, self.root)
            self.asset.unlink()
            with self.assertRaises(FileNotFoundError):
                bundled_catalog(archive, self.root)

    def test_stage_rechecks_pins_and_refuses_existing_output(self):
        target = self.root / "staged"
        target.mkdir()
        expected = audit_catalogs(self.root)
        self.assertEqual(stage_catalogs(self.root, target), expected)
        self.assertEqual(audit_catalogs(target), expected)
        with self.assertRaises(FileExistsError):
            stage_catalogs(self.root, target)
        self.asset.write_bytes(b"{}")
        fresh = self.root / "fresh"
        fresh.mkdir()
        with self.assertRaises(ValueError):
            stage_catalogs(self.root, fresh)
        self.assertFalse((fresh / "decoding").exists())

    def test_registered_test_digest_reaches_strict_recovery_not_missing_xor_gate(self):
        from script_editor.core.services.module_browser import read_module

        registered = "c7276deb0af7142c1b249d24299b884cd7320c0e84375cc6ac55f166df1d9ed1"
        self.rules[registered] = (self.asset.name, self.ref.sha256)
        with (
            ArchiveDocument(self.ref.archive) as archive,
            patch.object(archive, "fingerprint", return_value=registered),
            patch(
                "script_editor.core.services.module_browser.discover_pycdc",
                return_value=None,
            ),
            patch(
                "script_editor.core.services.module_browser._recover_primary",
                return_value={
                    "source": "counter = 1\n",
                    "complete": True,
                    "diagnostics": [],
                    "disassembly": "",
                },
            ) as engine,
        ):
            # Controlled SHA simulation; native fixture decode is NOT mocked.
            ref = bundled_catalog(archive, self.root)
            self.assertEqual(ref.fingerprint, registered)
            report = read_module(archive, 0, ref)
            engine.assert_called_once()
            self.assertIn("counter = 1", report.source)
            self.assertFalse(report.metadata()["compiled_and_reviewed"])
            self.assertFalse(
                any(
                    "请选择" in note or "选择并确认XOR" in note
                    for note in report.diagnostics
                )
            )

    def test_registered_test_digest_does_not_bypass_damaged_payload_validation(self):
        import zlib

        from fixtures import script_bytes

        from script_editor.core.services.module_browser import read_module

        registered = "c7276deb0af7142c1b249d24299b884cd7320c0e84375cc6ac55f166df1d9ed1"
        self.rules[registered] = (self.asset.name, self.ref.sha256)
        self.ref.archive.write_bytes(script_bytes(zlib.compress(bytes(65536))))
        with (
            ArchiveDocument(self.ref.archive) as archive,
            patch.object(archive, "fingerprint", return_value=registered),
            patch(
                "script_editor.core.services.module_browser._recover_primary"
            ) as engine,
        ):
            ref = bundled_catalog(archive, self.root)
            report = read_module(archive, 0, ref)
            engine.assert_not_called()
            self.assertFalse(report.source)
            self.assertTrue(report.diagnostics)
            self.assertNotIn("选择并确认XOR", " ".join(report.diagnostics))


class RegisteredPackagePinTests(unittest.TestCase):
    registered = "c7276deb0af7142c1b249d24299b884cd7320c0e84375cc6ac55f166df1d9ed1"
    original = "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72"

    def archive_stub(self, fingerprint):
        from types import SimpleNamespace

        return SimpleNamespace(
            vm="py25",
            path=Path("script.fls").resolve(),
            fingerprint=lambda: fingerprint,
        )

    def test_actual_production_map_registers_exact_user_digest_and_unknown_stays_off(
        self,
    ):
        from script_editor.core.services.bundled_catalog import BUNDLED_CATALOGS

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            BUNDLED_CATALOGS[self.registered], BUNDLED_CATALOGS[self.original]
        )
        archive = self.archive_stub(self.registered)
        ref = bundled_catalog(archive, root)
        ref.verify(archive)
        self.assertEqual(ref.fingerprint, self.registered)
        self.assertIsNone(
            bundled_catalog(self.archive_stub(self.registered[:-1] + "2"), root)
        )

    def test_shared_asset_stages_once_with_both_package_pins_intact(self):
        import shutil

        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            with patch(
                "script_editor.core.services.bundled_catalog.shutil.copyfile",
                wraps=shutil.copyfile,
            ) as copy:
                report = stage_catalogs(root, target)
            self.assertEqual(
                {r["archive_sha256"] for r in report},
                {
                    self.original,
                    self.registered,
                    "4bf116d0a6e62848bc1724ddfc67877c5a9db95a52768e8fa1d6f6d520318678",
                    # 2026-10-23 注册脚本派生包（r5）；四个指纹共用同一份
                    # script-original.json，所以只拷贝一次。
                    "a45e0e49ed336367a1bf00b5377229c5c48de2c30ac2b61f9bf7d67549a445b9",
                },
            )
            self.assertEqual(copy.call_count, 1)
            self.assertEqual(audit_catalogs(target), report)

    def test_user_accepted_direct_package_also_auto_associates_exact_digest(self):
        from script_editor.core.services.bundled_catalog import BUNDLED_CATALOGS

        digest = "4bf116d0a6e62848bc1724ddfc67877c5a9db95a52768e8fa1d6f6d520318678"
        self.assertEqual(BUNDLED_CATALOGS[digest], BUNDLED_CATALOGS[self.original])
        root = Path(__file__).resolve().parents[1]
        self.assertIsNotNone(bundled_catalog(self.archive_stub(digest), root))
        self.assertIsNone(bundled_catalog(self.archive_stub(digest[:-1] + "9"), root))

    def test_registered_alias_rejects_missing_or_tampered_asset(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "decoding").mkdir()
            archive = self.archive_stub(self.registered)
            with self.assertRaises(FileNotFoundError):
                bundled_catalog(archive, root)
            (root / "decoding/script-original.json").write_bytes(b"{}")
            with self.assertRaisesRegex(ValueError, "SHA256"):
                bundled_catalog(archive, root)


class RegisteredDerivativeTests(unittest.TestCase):
    """已登記的派生包指紋必須指向同一份已授權參數表。"""

    def test_registration_build_pin(self):
        from script_editor.core.services.bundled_catalog import BUNDLED_CATALOGS

        self.assertEqual(
            BUNDLED_CATALOGS.get(
                "a45e0e49ed336367a1bf00b5377229c5c48de2c30ac2b61f9bf7d67549a445b9"
            ),
            (
                "script-original.json",
                "43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb",
            ),
        )

    def test_known_broken_r4_build_is_not_registered(self):
        """r4 的填充区按研究目錄边界加密，4007 打不开，不能登记成可用。"""
        from script_editor.core.services.bundled_catalog import BUNDLED_CATALOGS

        self.assertNotIn(
            "9cf8c5cd9cef340db3e3f49405e385a3713ee0cb28c137e4d3acd7a5cddd6bf6",
            BUNDLED_CATALOGS,
        )
