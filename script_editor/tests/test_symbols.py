from __future__ import annotations

import unittest

from script_editor.core.inspection.symbols import outline


class OutlineTests(unittest.TestCase):
    def test_python2_nested_symbols_without_execution_or_string_false_positives(self):
        text = '''# def ignored():
text = """class NotReal:
 def fake(): pass
"""
class Panel:
 def show(self):
  print 'Python 2 syntax'
  def nested(): pass
raise RuntimeError('must never execute')
'''
        self.assertEqual(
            [(s.kind, s.name, s.line, s.column) for s in outline(text)],
            [("class", "Panel", 5, 0), ("def", "show", 6, 1), ("def", "nested", 8, 2)],
        )

    def test_partial_buffer_keeps_symbols_but_is_not_syntax_validation(self):
        self.assertEqual(
            [s.name for s in outline("def ready():\n pass\ntext = '''")], ["ready"]
        )
