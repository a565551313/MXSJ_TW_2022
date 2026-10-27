"""Project snapshot limits: what a big recovered draft costs to save.

Measured facts these tests pin (Linux, 2026-10-27):

* one field = 8 MiB + 4096 **UTF-8 bytes** (``MAX_TEXT``);
* one project = 48 MiB of editor payload, 64 MiB of JSON on disk;
* a recovered tab stores its text *and* the original recovered source *and*
  the disassembly, so a 4 MB module costs far more than 4 MB.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from script_editor.core.project.storage import (
    PROJECT_BUDGET,
    PROJECT_FILE_LIMIT,
    save_state,
)
from script_editor.core.project.workspace import MAX_TEXT, EditorState, text

MIB = 1024 * 1024


def editor(name: str, size: int) -> EditorState:
    return EditorState(
        path=Path(f"/tmp/{name}.py"),
        vm="py25",
        source_kind="recovered-draft",
        text="#" * size,
        modified=True,
        draft_saved=True,
    )


class FieldLimitTests(unittest.TestCase):
    def test_limit_counts_utf8_bytes_not_characters(self):
        self.assertEqual(text("#" * MAX_TEXT), "#" * MAX_TEXT)
        with self.assertRaises(ValueError) as caught:
            text("#" * (MAX_TEXT + 1))
        message = str(caught.exception)
        self.assertIn("超过8MiB", message)
        self.assertIn(str(MAX_TEXT), message)

    def test_chinese_text_hits_the_limit_at_a_third_of_the_characters(self):
        # 3 bytes per CJK character: ~2.8 M characters already exceed 8 MiB.
        characters = MAX_TEXT // 3 + 10
        with self.assertRaises(ValueError) as caught:
            text("中" * characters)
        self.assertIn("UTF-8", str(caught.exception))

    def test_non_text_is_rejected_with_a_type_message(self):
        for value in (None, 12, b"bytes", ["x"]):
            with self.subTest(value=value):
                with self.assertRaises(ValueError) as caught:
                    text(value)
                self.assertIn("必须是文本", str(caught.exception))

    def test_the_limit_is_frozen_at_eight_mib_plus_one_page(self):
        self.assertEqual(MAX_TEXT, 8 * MIB + 4096)


class ProjectBudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mxscript-budget-")
        self.path = Path(self.temp.name) / "p.mxscript.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_a_single_four_mib_draft_still_fits(self):
        # 4,014,213 characters is the largest real recovered source measured.
        save_state(self.path, (), (), editors=(editor("big", 4_014_213),))
        self.assertLess(self.path.stat().st_size, 8 * MIB)

    def test_budget_rejection_names_the_cost_and_keeps_the_edits(self):
        oversized = tuple(
            editor(f"big{i}", MAX_TEXT) for i in range(PROJECT_BUDGET // MAX_TEXT + 1)
        )
        with self.assertRaises(ValueError) as caught:
            save_state(self.path, (), (), editors=oversized)
        message = str(caught.exception)
        self.assertIn("超过 48 MiB 上限", message)
        self.assertIn("编辑文本 + 原恢复源码 + 反汇编", message)
        self.assertIn("编辑仍保留", message)
        self.assertFalse(self.path.exists())

    def test_project_file_limit_is_64_mib(self):
        self.assertEqual(PROJECT_FILE_LIMIT, 64 * MIB)


if __name__ == "__main__":
    unittest.main()
