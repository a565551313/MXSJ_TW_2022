"""图片导出路径保护，不依赖 Qt，帧保存用可观测的测试替身。"""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ui_editor.ui.image_export import export_image_files


class TestImageExportSafety(unittest.TestCase):
    def test_raw_export_rejects_source_and_hardlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.fls"
            source.write_bytes(b"original")
            alias = root / "alias.png"
            os.link(source, alias)
            for target in [source, alias]:
                with self.subTest(target=target), self.assertRaises(ValueError):
                    export_image_files(
                        "image.png", b"\x89PNG\r\n\x1a\nDATA", None,
                        root, target.name, protected_paths=[source])
                self.assertEqual(source.read_bytes(), b"original")

    def test_frames_are_all_checked_before_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.fls"
            source.write_bytes(b"original")
            os.link(source, root / "hero-1.png")
            frame = mock.Mock()
            with self.assertRaises(ValueError):
                export_image_files("hero.igs", b"I0", [frame, frame], root,
                                   protected_paths=[source])
            frame.save.assert_not_called()
            self.assertFalse((root / "hero-0.png").exists())
            self.assertEqual(source.read_bytes(), b"original")

    def test_dest_name_cannot_escape_export_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(ValueError):
                export_image_files("a.png", b"\x89PNG\r\n\x1a\nDATA", None,
                                   root / "out", "../escape.png")
            self.assertFalse((root / "escape.png").exists())
