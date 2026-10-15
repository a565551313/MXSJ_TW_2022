from __future__ import annotations

import ast
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fixtures import data_bytes, script_bytes

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.errors import ContainerError
from script_editor.core.inspection.encoding import byte_literal
from script_editor.core.project.document import Binding, load_project, save_project
from script_editor.core.services.files import atomic_write, read_source, save_source


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mxscript-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / "script.fls"
        self.archive.write_bytes(script_bytes())
        self.source = self.root / "自己的源码.py"
        self.source.write_text("# coding: utf-8\nx=1\n", encoding="utf-8")

    def binding(self):
        with ArchiveDocument(self.archive) as doc:
            return Binding.associate(doc, 0, self.source)

    def test_script_lazy_identity_and_stored_bytes(self):
        with ArchiveDocument(self.archive) as doc:
            self.assertEqual(doc.vm, "py25")
            self.assertEqual(doc.entries[0].identity, "00000FA7")
            self.assertEqual(doc.read_stored(0), b"stored-script")
            self.assertIn("只读", doc.entry_metadata(0)["source_status"])

    def test_data_directory_is_not_source_module(self):
        path = self.root / "data.fls"
        path.write_bytes(data_bytes())
        with ArchiveDocument(path) as doc:
            self.assertEqual(doc.vm, "py27")
            self.assertEqual(len(doc.entries), 2)
            self.assertTrue(doc.entries[0].directory)
            with self.assertRaises(ValueError):
                Binding.associate(doc, 0, self.source)
            self.assertEqual(doc.entries[1].identity, "check\\sample.pyc")

    def test_unknown_magic(self):
        self.archive.write_bytes(b"NOTFLS")
        with self.assertRaises(ContainerError):
            ArchiveDocument(self.archive)

    def test_truncated_directory(self):
        self.archive.write_bytes(script_bytes()[:-1])
        with self.assertRaises(ContainerError):
            ArchiveDocument(self.archive)

    def test_payload_crossing_directory(self):
        data = bytearray(script_bytes())
        directory = struct.unpack_from("<I", data, 8)[0]
        struct.pack_into("<I", data, directory + 12, 0xD59D16C ^ directory)
        self.archive.write_bytes(data)
        with self.assertRaises(ContainerError):
            ArchiveDocument(self.archive)

    def test_bad_data_trailer(self):
        self.archive.write_bytes(data_bytes()[:-1] + b"X")
        with self.assertRaises(ContainerError):
            ArchiveDocument(self.archive)

    def test_bad_data_name_length(self):
        data = bytearray(data_bytes())
        cd = struct.unpack_from("<I", data, len(data) - 8)[0]
        struct.pack_into("<H", data, cd + 26, 65535)
        self.archive.write_bytes(data)
        with self.assertRaises(ContainerError):
            ArchiveDocument(self.archive)

    def test_bad_data_local_length(self):
        data = bytearray(data_bytes())
        struct.pack_into("<I", data, 74, 10000)
        self.archive.write_bytes(data)
        with self.assertRaises(ContainerError):
            ArchiveDocument(self.archive)

    def test_bad_data_central_length(self):
        data = bytearray(data_bytes())
        cd = struct.unpack_from("<I", data, len(data) - 8)[0]
        struct.pack_into("<I", data, cd + 14, 10000)
        self.archive.write_bytes(data)
        with self.assertRaises(ContainerError):
            ArchiveDocument(self.archive)

    def test_bounds(self):
        with ArchiveDocument(self.archive) as doc:
            for index in (-1, 1):
                with self.assertRaises(IndexError):
                    Binding.associate(doc, index, self.source)
                with self.assertRaises(IndexError):
                    doc.read_stored(index)

    def test_open_archive_mutated_in_place_refuses_stale_index(self):
        with ArchiveDocument(self.archive) as doc:
            doc.fingerprint()
            self.archive.write_bytes(script_bytes(b"changed"))
            with self.assertRaises(ContainerError):
                Binding.associate(doc, 0, self.source)
            with self.assertRaises(ContainerError):
                doc.read_stored(0)

    def test_open_archive_replaced_at_path_refuses_stale_index(self):
        with ArchiveDocument(self.archive) as doc:
            other = self.root / "replacement.fls"
            other.write_bytes(script_bytes(b"new contents"))
            try:
                os.replace(other, self.archive)
            except PermissionError:
                self.skipTest("Windows may lock open source file against replacement")
            with self.assertRaises(ContainerError):
                Binding.associate(doc, 0, self.source)

    def test_literal_big5_and_gbk(self):
        for codec, text in [("big5", "測試文字"), ("gbk", "界面\\路径")]:
            literal = byte_literal(text, codec)
            # Parse only a self-authored escaped literal in tests; never game data.
            self.assertEqual(
                ast.literal_eval(literal).encode("latin1"), text.encode(codec)
            )
        self.assertEqual(byte_literal("'\\\n", "gbk"), "'\\x27\\x5c\\x0a'")

    def test_bad_codec_or_unencodable(self):
        with self.assertRaises(ValueError):
            byte_literal("x", "utf-8")
        with self.assertRaises(UnicodeEncodeError):
            byte_literal("😀", "big5")

    def test_utf8_bom_read_and_save(self):
        self.source.write_bytes(b"\xef\xbb\xbf" + "文案".encode())
        self.assertEqual(read_source(self.source), "文案")
        save_source(self.source, "新文案")
        self.assertEqual(self.source.read_bytes(), "新文案".encode())

    def test_non_utf8_source_rejected(self):
        self.source.write_bytes("測試".encode("big5"))
        with self.assertRaises(UnicodeDecodeError):
            read_source(self.source)

    def test_no_fls_writes(self):
        before = self.archive.read_bytes()
        with self.assertRaises(ValueError):
            atomic_write(self.archive, b"bad")
        self.assertEqual(self.archive.read_bytes(), before)
        with self.assertRaises(ValueError):
            save_source(self.root / "x.txt", "text")

    def test_hardlink_protected(self):
        alias = self.root / "alias.py"
        os.link(self.archive, alias)
        with self.assertRaises(ValueError):
            save_source(alias, "bad", [self.archive])
        self.assertEqual(self.archive.read_bytes(), script_bytes())

    def test_symlink_rejected(self):
        alias = self.root / "alias.py"
        try:
            alias.symlink_to(self.source)
        except OSError:
            self.skipTest("symlink privilege unavailable")
        with self.assertRaises(ValueError):
            save_source(alias, "bad")

    def test_failed_publication_preserves_output_and_cleans_temp(self):
        before = self.source.read_bytes()
        with patch("script_editor.core.services.files.os.replace", side_effect=OSError):
            with self.assertRaises(OSError):
                save_source(self.source, "changed")
        self.assertEqual(self.source.read_bytes(), before)
        self.assertFalse(list(self.root.glob(".mxscript-*")))

    def test_portable_project_and_mutated_archive(self):
        project = self.root / "project.mxscript.json"
        save_project(project, [self.binding()])
        row = json.loads(project.read_text(encoding="utf-8"))["bindings"][0]
        self.assertFalse(Path(row["source"]).is_absolute())
        moved = self.root / "moved"
        moved.mkdir()
        for path in (self.archive, self.source, project):
            shutil.copy2(path, moved / path.name)
        loaded = load_project(moved / project.name)
        self.assertEqual(loaded[0].source, moved / self.source.name)
        (moved / self.archive.name).write_bytes(script_bytes(b"different"))
        with self.assertRaises(ValueError):
            load_project(moved / project.name)

    def test_bad_project_identity_and_duplicate(self):
        project = self.root / "p.mxscript.json"
        save_project(project, [self.binding()])
        doc = json.loads(project.read_text(encoding="utf-8"))
        doc["bindings"].append(doc["bindings"][0])
        project.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_project(project)
        doc["bindings"] = doc["bindings"][:1]
        doc["bindings"][0]["identity"] = "wrong"
        project.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_project(project)

    def test_project_cannot_overwrite_source_alias(self):
        target = self.root / "alias.mxscript.json"
        os.link(self.source, target)
        with self.assertRaises(ValueError):
            save_project(target, [self.binding()])

    def test_independent_copy_core_has_no_qt_or_sibling_imports(self):
        # Isolated interpreter, cwd outside repository, only this tool copied.
        source_root = Path(__file__).resolve().parents[1] / "src"
        copied = self.root / "standalone-src"
        shutil.copytree(source_root, copied)
        script = (
            "import sys,pkgutil,importlib;sys.path.insert(0,sys.argv[1]);"
            "import script_editor.core as c;"
            "[importlib.import_module(m.name) for m in "
            "pkgutil.walk_packages(c.__path__,c.__name__+'.')];"
            "assert not any(n.startswith(('PySide6','resource_editor','ui_editor',"
            "'tools.')) for n in sys.modules)"
        )
        result = subprocess.run(
            [sys.executable, "-I", "-c", script, str(copied)],
            cwd=self.root,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
