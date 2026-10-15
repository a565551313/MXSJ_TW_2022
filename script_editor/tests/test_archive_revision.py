"""File revisions must not compare Windows stat and fstat namespaces."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fixtures import script_bytes

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.archives.readers import FileReader
from script_editor.core.errors import ContainerError


class ArchiveRevisionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-revision-")
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "脚本 source.fls"
        self.path.write_bytes(script_bytes())

    def test_path_stat_and_fstat_differences_do_not_reject_unchanged_package(self):
        real_fstat = os.fstat
        for variant in ("ctime", "identity"):
            with self.subTest(variant=variant):

                def descriptor_stat(fd, variant=variant):
                    info = real_fstat(fd)
                    return SimpleNamespace(
                        st_dev=info.st_dev + (17 if variant == "identity" else 0),
                        st_ino=info.st_ino + (2**96 if variant == "identity" else 0),
                        st_size=info.st_size,
                        st_mtime_ns=info.st_mtime_ns,
                        st_ctime_ns=info.st_ctime_ns + 10_000_000_000,
                    )

                # Model differing Win32 path/handle APIs, not a changed file.
                with patch("os.fstat", side_effect=descriptor_stat):
                    with ArchiveDocument(self.path) as doc:
                        self.assertEqual(doc.read_stored(0), b"stored-script")
                        self.assertEqual(doc.fingerprint(), doc.fingerprint())
                        self.assertEqual(doc.entry_metadata(0)["index"], 0)

    def test_path_identity_change_refuses_even_with_identical_size_and_times(self):
        with ArchiveDocument(self.path) as doc:
            doc.fingerprint()
            original = doc.reader.revision
            changed = (original[0], original[1] ^ 1, *original[2:])
            with patch.object(FileReader, "path_revision", return_value=changed):
                for operation in (
                    lambda: doc.read_stored(0),
                    doc.fingerprint,
                    lambda: doc.entry_metadata(0),
                ):
                    with self.assertRaises(ContainerError):
                        operation()

    def test_open_handle_change_refuses_even_if_path_snapshot_matches(self):
        with ArchiveDocument(self.path) as doc:
            original = doc.reader.revision
            self.path.write_bytes(script_bytes(b"changed length"))
            with patch.object(FileReader, "path_revision", return_value=original):
                with self.assertRaises(ContainerError):
                    doc.read_stored(0)

    def test_change_after_reader_open_before_document_init_is_not_rebaselined(self):
        real_init = FileReader.__init__

        def open_then_change(reader, path):
            real_init(reader, path)
            stamp = Path(path).stat()
            Path(path).write_bytes(script_bytes(b"X" * len(b"stored-script")))
            os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns + 1_000_000_000))

        with patch.object(FileReader, "__init__", open_then_change):
            with self.assertRaises(ContainerError):
                ArchiveDocument(self.path)

    def test_path_snapshot_error_closes_temporary_descriptor(self):
        real_open, real_fstat = os.open, os.fstat
        descriptors = []

        def remember_open(*args):
            fd = real_open(*args)
            descriptors.append(fd)
            return fd

        with patch("os.open", side_effect=remember_open):
            with patch("os.fstat", side_effect=OSError("snapshot unavailable")):
                with self.assertRaisesRegex(OSError, "snapshot unavailable"):
                    FileReader.path_revision(self.path)
        self.assertEqual(len(descriptors), 1)
        with self.assertRaises(OSError):
            real_fstat(descriptors[0])
