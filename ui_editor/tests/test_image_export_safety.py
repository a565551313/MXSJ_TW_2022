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


class TestBatchNameReservation(unittest.TestCase):
    """批量导出共用 used_names：同名素材加序号，绝不静默覆盖本批先写的。"""

    def test_same_basename_gets_suffix_instead_of_overwriting(self):
        first = b"\x89PNG\r\n\x1a\nAAAA"
        second = b"\x89PNG\r\n\x1a\nBBBB"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            used: set[str] = set()
            a = export_image_files("a\\btn.png", first, None, root,
                                   used_names=used)
            b = export_image_files("b\\btn.png", second, None, root,
                                   used_names=used)
            self.assertEqual([p.name for p in a], ["btn.png"])
            self.assertEqual([p.name for p in b], ["btn-2.png"])
            self.assertEqual((root / "btn.png").read_bytes(), first)
            self.assertEqual((root / "btn-2.png").read_bytes(), second)

    def test_frame_names_reserved_per_stem(self):
        frames = [mock.Mock(), mock.Mock()]
        for frame in frames:
            frame.save.return_value = True
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            used: set[str] = set()
            a = export_image_files("a\\hero.igs", b"I0", frames, root,
                                   used_names=used)
            b = export_image_files("b\\hero.igs", b"I0", frames, root,
                                   used_names=used)
            self.assertEqual([p.name for p in a],
                             ["hero-0.png", "hero-1.png"])
            self.assertEqual([p.name for p in b],
                             ["hero-0-2.png", "hero-1-2.png"])

    def test_without_batch_set_keeps_single_export_overwrite(self):
        first = b"\x89PNG\r\n\x1a\nAAAA"
        second = b"\x89PNG\r\n\x1a\nBBBB"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            export_image_files("a\\btn.png", first, None, root)
            out = export_image_files("a\\btn.png", second, None, root)
            self.assertEqual([p.name for p in out], ["btn.png"])
            self.assertEqual((root / "btn.png").read_bytes(), second)

    def test_batch_does_not_overwrite_existing_files_on_disk(self):
        """批量导出也不能覆盖目标文件夹里**已有**的同名文件（README 的承诺）。"""
        old = b"\x89PNG\r\n\x1a\nOLD!"
        first = b"\x89PNG\r\n\x1a\nAAAA"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "btn.png").write_bytes(old)
            out = export_image_files("a\\btn.png", first, None, root,
                                     used_names=set())
            self.assertEqual([p.name for p in out], ["btn-2.png"])
            self.assertEqual((root / "btn.png").read_bytes(), old)
            self.assertEqual((root / "btn-2.png").read_bytes(), first)

    def test_batch_keeps_all_frames_clear_of_existing_files(self):
        frames = [mock.Mock(), mock.Mock()]
        for frame in frames:
            frame.save.return_value = True
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "hero-1.png").write_bytes(b"OLD")
            out = export_image_files("a\\hero.igs", b"I0", frames, root,
                                     used_names=set())
            # 整组一起换名：不会出现 hero-0.png 覆盖、hero-1 改名这种半吊子
            self.assertEqual([p.name for p in out],
                             ["hero-0-2.png", "hero-1-2.png"])
            self.assertEqual((root / "hero-1.png").read_bytes(), b"OLD")
