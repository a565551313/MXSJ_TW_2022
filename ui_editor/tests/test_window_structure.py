"""主窗口职责分组护栏；纯 AST 检查不依赖 Qt 运行环境。"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

UI_DIR = Path(__file__).resolve().parents[1] / "src" / "ui_editor" / "ui"
GROUPS = {
    "main_window.py": "MainWindow",
    "clipboard.py": "ClipboardMixin",
    "commands.py": "EditingCommandsMixin",
    "save_mode.py": "SaveModeMixin",
    "save_targets.py": "SaveTargetsMixin",
    "save_workflows.py": "SaveWorkflowsMixin",
    "tab_menu.py": "TabMenuMixin",
    "replace_layout.py": "ReplaceLayoutMixin",
    "import_queue.py": "ImportQueueMixin",
    "workflows.py": "FileWorkflowsMixin",
    "source_actions.py": "SourceActionsMixin",
    "window_setup.py": "WindowSetupMixin",
}


def class_node(filename: str) -> ast.ClassDef:
    text = (UI_DIR / filename).read_text(encoding="utf-8")
    tree = ast.parse(text)
    return next(node for node in tree.body
                if isinstance(node, ast.ClassDef)
                and node.name == GROUPS[filename])


class WindowStructureTests(unittest.TestCase):
    def test_window_modules_stay_within_size_limit(self):
        for filename in GROUPS:
            with self.subTest(module=filename):
                text = (UI_DIR / filename).read_text(encoding="utf-8")
                self.assertLessEqual(len(text.splitlines()), 600)

    def test_method_names_are_not_shadowed_across_groups(self):
        owners: dict[str, str] = {}
        for filename in GROUPS:
            for node in class_node(filename).body:
                if isinstance(node, ast.FunctionDef):
                    self.assertNotIn(node.name, owners,
                                     f"{node.name}: {filename} shadows {owners}")
                    owners[node.name] = filename

    def test_mixins_do_not_take_over_qobject_initialization(self):
        window = class_node("main_window.py")
        self.assertEqual([base.id for base in window.bases], [
            "AssetBrowserMixin", "BusyHostMixin", "ClipboardMixin",
            "EditingCommandsMixin", "FileWorkflowsMixin",
            "ImportQueueMixin", "SaveModeMixin", "SaveTargetsMixin",
            "SaveWorkflowsMixin", "SourceActionsMixin", "TabMenuMixin",
            "ReplaceLayoutMixin", "WindowSetupMixin", "QMainWindow",
        ])
        for filename in GROUPS:
            if filename == "main_window.py":
                continue
            node = class_node(filename)
            self.assertFalse(node.bases)
            self.assertNotIn("__init__", [method.name for method in node.body
                                         if isinstance(method, ast.FunctionDef)])


if __name__ == "__main__":
    unittest.main()
