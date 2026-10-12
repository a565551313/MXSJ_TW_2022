"""Two guarantees that matter for shipping an EXE.

1. **Qt isolation.**  Only ``ui/widgets.py`` may import Qt.  The format engine,
   client discovery and view model must stay importable where ``QtWidgets``
   cannot even be loaded — which is exactly the situation in a headless CI box or
   a Linux sandbox missing ``libGL.so.1``.  This is what makes the rest of the
   test suite meaningful here.

2. **The CLI really runs.**  ``main()`` is executed against the real repository,
   so discovery, header parsing, the scene table and JSON export are all
   exercised as one path rather than mocked.
"""
from __future__ import annotations

import ast
import io
import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _paths import PROJECT, SAMPLES                    # noqa: E402

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from map_editor.cli import _bare_double_click_launch, main   # noqa: E402

SRC = PROJECT / "src" / "map_editor"
QT_ALLOWED = {Path("ui") / "widgets.py"}
REPO = SAMPLES.parent
needs_samples = unittest.skipUnless(SAMPLES.is_dir(), f"no samples at {SAMPLES}")


class TestQtIsolation(unittest.TestCase):
    def _qt_imports(self, path: Path) -> list[str]:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        found: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found += [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                found.append(node.module)
        return [m for m in found
                if m.split(".")[0] in {"PySide6", "PyQt5", "PyQt6", "shiboken6"}]

    def test_only_widgets_module_imports_qt(self) -> None:
        offenders: dict[str, list[str]] = {}
        checked = 0
        for path in sorted(SRC.rglob("*.py")):
            rel = path.relative_to(SRC)
            checked += 1
            hits = self._qt_imports(path)
            if hits and rel not in QT_ALLOWED:
                offenders[str(rel)] = hits
        self.assertGreater(checked, 8, "expected to scan the whole package")
        self.assertEqual(offenders, {}, "these modules must not import Qt")

    def test_widgets_module_is_the_only_qt_consumer_and_is_syntactically_valid(self) -> None:
        target = SRC / "ui" / "widgets.py"
        self.assertTrue(target.is_file())
        self.assertTrue(self._qt_imports(target), "widgets.py should import PySide6")
        ast.parse(target.read_text(encoding="utf-8"), filename=str(target))

    def test_core_and_client_import_without_qt_installed(self) -> None:
        """Import the model layer with Qt made unimportable, like a headless box."""
        import importlib
        import subprocess
        src_dir = str(PROJECT / "src")
        code = (
            "import sys\n"
            "class Blocker:\n"
            "    BLOCKED = {'PySide6', 'PyQt5', 'PyQt6', 'shiboken6'}\n"
            "    def find_spec(self, name, path=None, target=None):\n"
            "        if name.split('.')[0] in self.BLOCKED:\n"
            "            raise ImportError('Qt blocked for this test: ' + name)\n"
            "        return None\n"
            "sys.meta_path.insert(0, Blocker())\n"
            f"sys.path.insert(0, {src_dir!r})\n"
            "import map_editor.core, map_editor.client.discovery, map_editor.client.config\n"
            "import map_editor.client.scene_table, map_editor.client.scriptfls\n"
            "import map_editor.ui.viewmodel, map_editor.cli\n"
            "try:\n"
            "    import PySide6\n"
            "    raise SystemExit('Qt was importable; blocker failed')\n"
            "except ImportError:\n"
            "    pass\n"
            "print('MODEL_LAYER_OK')\n"
        )
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertIn("MODEL_LAYER_OK", proc.stdout, proc.stderr)
        importlib.invalidate_caches()


@needs_samples
class TestCliEndToEnd(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="map_editor_cli_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        os.environ["MAP_EDITOR_HOME"] = str(self.tmp / "cfg")
        self.addCleanup(os.environ.pop, "MAP_EDITOR_HOME", None)

    def _main(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_scan_lists_maps_and_finds_fls(self) -> None:
        code, out, _err = self._main("--scan", str(REPO))
        self.assertEqual(code, 0)
        self.assertIn("script.fls", out)
        for key in ("2101", "2111", "2112", "2122", "2303"):
            self.assertIn(key, out)
        self.assertIn("2000x1500", out)

    def test_export_json_writes_a_readable_document(self) -> None:
        dest = self.tmp / "2303.json"
        code, out, err = self._main("--scan", str(SAMPLES),
                                    "--export-json", f"2303:{dest}")
        self.assertEqual(code, 0, err)
        self.assertIn("已导出", out)
        doc = json.loads(dest.read_text(encoding="utf-8"))
        self.assertEqual(doc["scene_key"], "2303")
        self.assertEqual(len(doc["sectors"]), 49)
        self.assertEqual(len(doc["prefix_records"]), 32)

    def test_export_png_matches_header_dimensions(self) -> None:
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow not installed")
        dest = self.tmp / "2101.png"
        code, _out, err = self._main("--scan", str(SAMPLES),
                                     "--export-png", f"2101:{dest}")
        self.assertEqual(code, 0, err)
        with Image.open(dest) as im:
            self.assertEqual(im.size, (2000, 1500))

    def test_missing_root_is_a_usage_error(self) -> None:
        os.environ.pop("MAP_EDITOR_HOME", None)
        code, _out, err = self._main("--scan", str(self.tmp / "does-not-exist"))
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_export_without_path_is_a_usage_error(self) -> None:
        code, _out, err = self._main("--scan", str(SAMPLES), "--export-json", "2101")
        self.assertEqual(code, 2)
        self.assertIn("KEY:PATH", err)

    def test_main_still_errors_in_dev_mode_with_no_arguments(self) -> None:
        """Unpackaged (``python run.py`` with no args) keeps the documented
        CLI-first default -- only a frozen EXE should auto-open the GUI."""
        os.environ.pop("MAP_EDITOR_HOME", None)
        self.assertFalse(getattr(sys, "frozen", False))
        code, _out, err = self._main()
        self.assertEqual(code, 2)
        self.assertIn("错误", err)


class TestBareDoubleClickLaunch(unittest.TestCase):
    """PyInstaller ships MapEditor.exe with ``console=False`` (see
    ``map_editor.spec``): a double-clicked EXE run with no arguments has no
    stdout/stderr at all, so silently falling back to CLI mode and printing
    an invisible "need --scan" error just looks like the app did nothing.
    A frozen, argument-less launch must open the GUI instead."""

    def setUp(self) -> None:
        self._had_frozen = hasattr(sys, "frozen")
        self._old_frozen = getattr(sys, "frozen", None)
        self.addCleanup(self._restore_frozen)

    def _restore_frozen(self) -> None:
        if self._had_frozen:
            sys.frozen = self._old_frozen
        elif hasattr(sys, "frozen"):
            del sys.frozen

    def test_not_frozen_never_defaults_to_gui(self) -> None:
        if hasattr(sys, "frozen"):
            del sys.frozen
        self.assertFalse(_bare_double_click_launch([]))
        self.assertFalse(_bare_double_click_launch(None))

    def test_frozen_with_no_arguments_defaults_to_gui(self) -> None:
        sys.frozen = True
        self.assertTrue(_bare_double_click_launch([]))

    def test_frozen_but_with_explicit_arguments_does_not_override_them(self) -> None:
        sys.frozen = True
        self.assertFalse(_bare_double_click_launch(["--scan", "."]))
        self.assertFalse(_bare_double_click_launch(["--cli"]))

    def test_main_dispatches_to_gui_when_frozen_with_no_arguments(self) -> None:
        """End-to-end through ``main()`` -- without needing Qt installed."""
        calls: list[object] = []
        fake_widgets = types.ModuleType("map_editor.ui.widgets")
        fake_widgets.run = lambda vm: calls.append(vm) or 0  # type: ignore[attr-defined]
        sys.modules["map_editor.ui.widgets"] = fake_widgets
        self.addCleanup(sys.modules.pop, "map_editor.ui.widgets", None)

        home = Path(tempfile.mkdtemp(prefix="map_editor_frozen_"))
        self.addCleanup(shutil.rmtree, home, True)
        os.environ["MAP_EDITOR_HOME"] = str(home)
        self.addCleanup(os.environ.pop, "MAP_EDITOR_HOME", None)

        sys.frozen = True
        code = main([])
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 1)


class TestRunGuiEntryPoint(unittest.TestCase):
    """``runGUI.py``: a second entry point that always opens the window,
    regardless of flags/platform/argv -- unlike ``run.py``, which only opens
    the GUI for ``--gui`` or (since the frozen-EXE fix) a bare double-click.
    """

    def setUp(self) -> None:
        import runGUI
        self.runGUI = runGUI

        self.calls: list[object] = []
        fake_widgets = types.ModuleType("map_editor.ui.widgets")
        fake_widgets.run = lambda vm: self.calls.append(vm) or 0  # type: ignore[attr-defined]
        sys.modules["map_editor.ui.widgets"] = fake_widgets
        self.addCleanup(sys.modules.pop, "map_editor.ui.widgets", None)

        home = Path(tempfile.mkdtemp(prefix="map_editor_rungui_"))
        self.addCleanup(shutil.rmtree, home, True)
        os.environ["MAP_EDITOR_HOME"] = str(home)
        self.addCleanup(os.environ.pop, "MAP_EDITOR_HOME", None)

        # Not frozen and no --gui flag: make sure the GUI still opens, i.e.
        # this does not rely on the frozen-EXE auto-GUI behaviour at all.
        if hasattr(sys, "frozen"):
            del sys.frozen
            self.addCleanup(setattr, sys, "frozen", False)

    def test_bare_call_opens_the_gui(self) -> None:
        code = self.runGUI.main_gui([])
        self.assertEqual(code, 0)
        self.assertEqual(len(self.calls), 1)

    def test_scan_flag_does_not_suppress_the_gui(self) -> None:
        """``--scan`` alone would mean CLI-mode for run.py; runGUI.py always
        wins and still opens the window."""
        code = self.runGUI.main_gui(["--scan", str(SAMPLES)])
        self.assertEqual(code, 0)
        self.assertEqual(len(self.calls), 1)

    def test_client_root_flag_is_still_honoured(self) -> None:
        code = self.runGUI.main_gui(["--client-root", str(SAMPLES)])
        self.assertEqual(code, 0)
        self.assertEqual(len(self.calls), 1)
        (vm,) = self.calls
        self.assertEqual(vm.config.client_root, str(SAMPLES))

    def test_explicit_gui_flag_is_not_duplicated(self) -> None:
        """Passing --gui explicitly must not confuse argparse (no duplicate
        injection)."""
        code = self.runGUI.main_gui(["--gui", "--client-root", str(SAMPLES)])
        self.assertEqual(code, 0)
        self.assertEqual(len(self.calls), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)


@needs_samples
class TestGirbDump(unittest.TestCase):
    """--girb-dump is the low-bandwidth channel: hex text instead of map files."""

    def test_dump_lists_hex_bodies_of_failing_sectors(self) -> None:
        import io
        from contextlib import redirect_stdout
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--scan", str(SAMPLES), "--girb-dump", "1034:2"])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("### 1034", text)
        lines = [l for l in text.splitlines() if l.startswith("s") and " len=" in l]
        self.assertEqual(len(lines), 2)
        hexes = [l for l in text.splitlines()
                 if l and all(c in "0123456789abcdef" for c in l)]
        self.assertEqual(len(hexes), 2)
        for hdr, body in zip(lines, hexes):
            declared = int(hdr.split("len=")[1])
            self.assertEqual(len(body), declared * 2)   # 2 hex chars per byte

    def test_dump_on_a_fully_decoded_map_says_so(self) -> None:
        import io
        from contextlib import redirect_stdout
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--scan", str(SAMPLES), "--girb-dump", "2101"])
        self.assertEqual(code, 0)
        self.assertIn("没有需要排查的扇区", out.getvalue())

    def test_dump_rejects_a_non_integer_limit(self) -> None:
        code = main(["--scan", str(SAMPLES), "--girb-dump", "2101:abc"])
        self.assertEqual(code, 2)
