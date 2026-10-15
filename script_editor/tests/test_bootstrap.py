from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from script_editor import GUI_VERSION
from script_editor.app import main

SPEC = importlib.util.spec_from_file_location(
    "bootstrap", Path(__file__).resolve().parents[1] / "bootstrap.py"
)
bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bootstrap)


class BootstrapVersionTests(unittest.TestCase):
    def test_incompatible_preinstalled_qt_must_be_repaired(self):
        with patch.dict(
            "sys.modules", {"PySide6": SimpleNamespace(__version__="6.12.0")}
        ):
            self.assertEqual(
                bootstrap.find_missing(), [("PySide6", f"PySide6=={GUI_VERSION}")]
            )

    def test_pinned_qt_is_accepted_and_distribution_declarations_agree(self):
        with patch.dict(
            "sys.modules", {"PySide6": SimpleNamespace(__version__=GUI_VERSION)}
        ):
            self.assertEqual(bootstrap.find_missing(), [])
        root = Path(__file__).resolve().parents[1]
        for name in ("requirements.txt", "pyproject.toml"):
            self.assertIn(
                f"PySide6=={GUI_VERSION}", (root / name).read_text(encoding="utf-8")
            )

    def test_direct_gui_entry_refuses_incompatible_qt_before_window_creation(self):
        with patch.dict(
            "sys.modules", {"PySide6": SimpleNamespace(__version__="6.12.0")}
        ):
            with self.assertRaisesRegex(SystemExit, "bootstrap.py"):
                main([])
