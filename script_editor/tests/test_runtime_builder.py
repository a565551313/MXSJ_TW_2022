"""Source extraction rules only; never claims Windows execution."""

from __future__ import annotations

import importlib.util
import io
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "runtime_builder", Path(__file__).resolve().parents[1] / "build_runtimes.py"
)
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class SourceArchiveTests(unittest.TestCase):
    def extract(self, name, kind=None):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture = root / "fixture.tgz"
            with tarfile.open(fixture, "w:gz") as archive:
                entry = tarfile.TarInfo("cpython-2.5.6")
                entry.type = tarfile.DIRTYPE
                archive.addfile(entry)
                entry = tarfile.TarInfo(name)
                if kind:
                    entry.type = kind
                    entry.linkname = "../../outside"
                    archive.addfile(entry)
                else:
                    data = b"official source fixture"
                    entry.size = len(data)
                    archive.addfile(entry, io.BytesIO(data))
            work = root / "work"
            work.mkdir()
            with patch.dict(
                builder.SOURCES, {"2.5.6": ("fixture", builder.sha(fixture))}
            ):
                with patch.object(
                    builder.urllib.request,
                    "urlopen",
                    return_value=io.BytesIO(fixture.read_bytes()),
                ):
                    result, _ = builder.source_tree(work, "2.5.6")
            return (result / "README").read_bytes()

    def test_tar_root_directory_without_trailing_slash_is_valid(self):
        self.assertEqual(
            self.extract("cpython-2.5.6/README"), b"official source fixture"
        )

    def test_tar_parent_escape_and_other_roots_are_rejected(self):
        for name in ["cpython-2.5.6/../../outside", "other/README"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.extract(name)

    def test_tar_links_are_rejected(self):
        for kind in (tarfile.SYMTYPE, tarfile.LNKTYPE):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.extract("cpython-2.5.6/README", kind)
