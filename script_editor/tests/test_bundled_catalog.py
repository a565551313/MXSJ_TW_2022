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
