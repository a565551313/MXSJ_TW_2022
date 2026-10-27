from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from native_fixtures import script_fixture

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.project.storage import CatalogRef
from script_editor.core.services.module_paths import (
    display_module_path,
    index_script_paths,
    scan_script_paths,
)


class ModulePathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def archive(self, filename=b"script\\login\\register.py", two_modules=True):
        payload, rows = script_fixture(filename=filename, two_modules=two_modules)
        path, catalog = self.root / "script.fls", self.root / "catalog.json"
        path.write_bytes(payload)
        catalog.write_text(json.dumps(rows), encoding="utf-8")
        archive = ArchiveDocument(path)
        self.addCleanup(archive.close)
        ref = CatalogRef(
            archive.path,
            archive.fingerprint(),
            catalog,
            hashlib.sha256(catalog.read_bytes()).hexdigest(),
        )
        return archive, ref

    def test_all_paths_without_decompiler_and_bad_entries_are_independent(self):
        archive, ref = self.archive()
        before = archive.path.read_bytes()
        with patch(
            "script_editor.core.services.module_browser.read_module",
            side_effect=AssertionError("path indexing must not decompile"),
        ):
            paths, errors = scan_script_paths(archive, ref)
        self.assertEqual(
            paths, {0: "script/login/register.py", 1: "script/login/register.py"}
        )
        self.assertEqual(set(errors), {2})
        self.assertEqual(archive.path.read_bytes(), before)

    def test_names_do_not_depend_on_opcode_translation(self):
        archive, ref = self.archive()
        with patch(
            "script_editor.core.vm.py25.codec.decode",
            side_effect=AssertionError("names must not need opcode translation"),
        ):
            paths, _ = scan_script_paths(archive, ref)
        self.assertEqual(paths[0], "script/login/register.py")

    def test_missing_parameters_are_explicit_not_fake_paths(self):
        archive, _ = self.archive()
        paths, errors = scan_script_paths(archive, None)
        self.assertFalse(paths)
        self.assertEqual(len(errors), 3)
        self.assertIn("XOR", errors[0])

    def test_catalog_tamper_rejects_whole_index(self):
        archive, ref = self.archive()
        ref.path.write_bytes(ref.path.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "发生变化"):
            scan_script_paths(archive, ref)
        index_script_paths(archive, ref)
        self.assertFalse(archive.module_paths)
        self.assertIn("发生变化", archive.module_path_errors[0])

    def test_wrong_archive_pin_is_not_used(self):
        archive, ref = self.archive()
        from dataclasses import replace

        with self.assertRaisesRegex(ValueError, "过期"):
            scan_script_paths(archive, replace(ref, fingerprint="0" * 64))

    def test_catalog_read_count_is_constant_not_once_per_entry(self):
        archive, ref = self.archive()
        from script_editor.core.vm.py25.keys import clear_catalog_cache, read_catalog

        clear_catalog_cache()
        with (
            patch(
                "script_editor.core.project.storage.read_catalog", wraps=read_catalog
            ) as verify,
            patch(
                "script_editor.core.vm.py25.keys.read_catalog", wraps=read_catalog
            ) as snapshot,
        ):
            scan_script_paths(archive, ref)
        self.assertEqual(verify.call_count, 2)
        # One parsed snapshot serves the whole scan; the catalog is never read
        # once per entry (the scan has more entries than this read count).
        self.assertEqual(snapshot.call_count, 1)

    def test_raw_paths_are_not_repr_or_falsely_renamed_pyo(self):
        self.assertEqual(display_module_path(b"script\\x.py"), "script/x.py")
        self.assertEqual(display_module_path(b"script\\x.pyo"), "script/x.pyo")
        self.assertEqual(display_module_path(b"script\\\xff.py"), "script/\\xff.py")
        for value in (b"", b"x\n.py", b"x\0.py", b"x\t.py", b"x" * 8193):
            with self.subTest(value=value[:20]), self.assertRaises(ValueError):
                display_module_path(value)

    def test_rejected_filename_does_not_hide_other_entries(self):
        archive, ref = self.archive(filename=b"script\\x\n.py")
        paths, errors = scan_script_paths(archive, ref)
        self.assertFalse(paths)
        self.assertEqual(len(errors), 3)
        self.assertIn("控制字符", errors[0])

    def test_bad_compressed_entry_with_catalog_row_does_not_hide_valid_paths(self):
        from dataclasses import replace

        archive, ref = self.archive()
        rows = json.loads(ref.path.read_text(encoding="utf-8"))
        rows["2"] = rows["0"]
        ref.path.write_text(json.dumps(rows), encoding="utf-8")
        ref = replace(ref, sha256=hashlib.sha256(ref.path.read_bytes()).hexdigest())
        paths, errors = scan_script_paths(archive, ref)
        self.assertEqual(len(paths), 2)
        self.assertEqual(set(errors), {2})

    def test_catalog_change_mid_scan_rejects_all_collected_names(self):
        from script_editor.core.vm.marshal_tree import parse

        archive, ref = self.archive()

        def change_after_parse(*args, **kwargs):
            tree = parse(*args, **kwargs)
            ref.path.write_bytes(ref.path.read_bytes() + b" ")
            return tree

        with (
            patch(
                "script_editor.core.services.module_paths.parse",
                side_effect=change_after_parse,
            ),
            self.assertRaisesRegex(ValueError, "发生变化"),
        ):
            scan_script_paths(archive, ref)
        self.assertFalse(archive.module_paths)
