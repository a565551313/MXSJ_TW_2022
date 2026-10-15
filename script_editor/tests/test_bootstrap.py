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
                bootstrap.find_missing(bootstrap.GUI_REQUIREMENTS),
                [("PySide6", f"PySide6=={GUI_VERSION}")],
            )

    def test_pinned_qt_is_accepted_and_distribution_declarations_agree(self):
        with patch.dict(
            "sys.modules", {"PySide6": SimpleNamespace(__version__=GUI_VERSION)}
        ):
            self.assertEqual(bootstrap.find_missing(bootstrap.GUI_REQUIREMENTS), [])
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


class RecoveryBootstrapTests(unittest.TestCase):
    def test_same_version_wrong_source_is_not_accepted(self):
        from script_editor.recovery_dependencies import RECOVERY_VERSIONS

        with (
            patch.object(
                bootstrap, "installed_recovery_source_matches", return_value=False
            ),
            patch.object(
                bootstrap.importlib.metadata,
                "version",
                side_effect=lambda name: RECOVERY_VERSIONS[name.replace("-", "_")],
            ),
        ):
            self.assertEqual(
                bootstrap.find_missing(bootstrap.RECOVERY_REQUIREMENTS),
                [bootstrap.RECOVERY_REQUIREMENTS[0]],
            )

    def test_legacy_xdis_is_detected_not_left_with_new_engine(self):
        from script_editor.recovery_dependencies import RECOVERY_VERSIONS

        with (
            patch.object(
                bootstrap, "installed_recovery_source_matches", return_value=True
            ),
            patch.object(
                bootstrap.importlib.metadata,
                "version",
                side_effect=lambda name: (
                    "6.1.8"
                    if name == "xdis"
                    else RECOVERY_VERSIONS[name.replace("-", "_")]
                ),
            ),
        ):
            self.assertEqual(
                bootstrap.find_missing(bootstrap.RECOVERY_REQUIREMENTS),
                [("xdis", "xdis==6.3.0")],
            )

    def test_engine_install_failure_does_not_block_gui_dependency_gate(self):
        with (
            patch.object(
                bootstrap,
                "find_missing",
                side_effect=[[], bootstrap.RECOVERY_REQUIREMENTS],
            ),
            patch.object(bootstrap, "install_packages", return_value=False) as install,
        ):
            self.assertTrue(bootstrap.ensure_dependencies())
            pins = install.call_args.args[0]
            self.assertIn("#sha256=" + bootstrap.SOURCE_SHA256, pins[0])
            self.assertIn("xdis==6.3.0", pins)
            self.assertEqual(install.call_args.args[1], bootstrap.RECOVERY_REQUIREMENTS)

    def test_qt_install_failure_still_blocks_gui_with_specific_diagnostic(self):
        with (
            patch.object(
                bootstrap, "find_missing", return_value=bootstrap.GUI_REQUIREMENTS
            ),
            patch.object(bootstrap, "install_packages", return_value=False),
        ):
            self.assertFalse(bootstrap.ensure_dependencies())

    def test_corrupt_upstream_source_is_refused_before_install(self):
        import tempfile

        from script_editor.recovery_dependencies import (
            SOURCE_FILENAME,
            checked_recovery_source,
        )

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "third_party").mkdir()
            (root / "third_party" / SOURCE_FILENAME).write_bytes(
                b"not the tested source"
            )
            with self.assertRaisesRegex(ValueError, "摘要"):
                checked_recovery_source(root)

    def test_python314_normal_start_reaches_app_without_recovery_dependency(self):
        with (
            patch.object(bootstrap.sys, "version_info", (3, 14, 7)),
            patch.object(bootstrap, "ensure_dependencies", return_value=True),
            patch.dict("sys.modules", {"PySide6.QtWidgets": SimpleNamespace()}),
            patch("script_editor.app.main", return_value=17) as app,
        ):
            self.assertEqual(bootstrap.main([]), 17)
            app.assert_called_once_with([])

    def test_full_check_does_not_claim_pass_when_engine_missing(self):
        with (
            patch.object(bootstrap, "ensure_dependencies", return_value=True),
            patch.dict("sys.modules", {"PySide6.QtWidgets": SimpleNamespace()}),
            patch.object(
                bootstrap, "find_missing", return_value=bootstrap.RECOVERY_REQUIREMENTS
            ),
        ):
            self.assertEqual(bootstrap.main(["--check-only"]), 2)

    def test_install_only_returns_failure_if_engine_missing_without_opening_gui(self):
        with (
            patch.object(bootstrap, "ensure_dependencies", return_value=True),
            patch.object(
                bootstrap, "find_missing", return_value=bootstrap.RECOVERY_REQUIREMENTS
            ),
            patch("script_editor.app.main") as app,
        ):
            self.assertEqual(bootstrap.main(["--install-only"]), 2)
            app.assert_not_called()
