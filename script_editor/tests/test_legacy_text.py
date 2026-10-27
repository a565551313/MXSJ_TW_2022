"""Display-only decoding of legacy Big5/GBK byte literals.

These tests pin the two things that matter: the reading must be exact (or
absent), and nothing may produce source text that a caller could save.
"""

from __future__ import annotations

import unittest

from script_editor.core.inspection.legacy_text import (
    CODECS,
    DISPLAY_ONLY,
    MAX_RECORDS,
    clamp,
    decode_bytes,
    format_hint,
    hint_for_position,
    line_previews,
    literal_bytes,
    previews,
    readable_literal,
    readings,
    report_text,
    split_literal,
    summary,
)

QT_ERROR = ""
try:
    from PySide6.QtWidgets import QApplication, QPushButton

    from script_editor.gui.literal_preview import LiteralReportDialog
except ImportError as exc:  # pragma: no cover - depends on the host
    QT_ERROR = str(exc)


#: Real constant recovered from entry 4007 (script/login/register.py).
BIG5_MESSAGE = r"'\xa5u\xaf\xe0\xa8\xcf\xa5\xce\xbc\xc6\xa6r\xa9\xce\xa6r\xa5\xc0'"
#: Path constant from the same module: valid as Big5 *and* as GBK.
MIXED_PATH = r"'combdialog/\xd4\xd3\xcd\xbc/\xcd\xac\xd2\xe2\xcc\xf5\xbf\xee.igs'"


class LiteralBytesTests(unittest.TestCase):
    def test_escaped_bytes_and_ascii_are_one_byte_stream(self):
        self.assertEqual(literal_bytes(r"\xa5u\xaf"), b"\xa5u\xaf")
        self.assertEqual(literal_bytes("abc"), b"abc")

    def test_simple_escapes_are_single_bytes(self):
        self.assertEqual(literal_bytes(r"\n\t\\\'"), b"\n\t\\'")

    def test_unicode_octal_and_raw_text_are_refused(self):
        for body in (r"\u4e2d", r"\101", "只能", r"\N{BULLET}", r"\x4"):
            with self.subTest(body=body):
                self.assertIsNone(literal_bytes(body))

    def test_empty_body_has_no_claim(self):
        self.assertIsNone(literal_bytes(""))


class ReadingTests(unittest.TestCase):
    def test_big5_message_reads_back_as_taiwan_text(self):
        found = readings(BIG5_MESSAGE)
        self.assertEqual(found[0].codec, "cp950")
        self.assertEqual(found[0].text, "'只能使用數字或字母'")
        self.assertEqual([item.codec for item in found], ["cp950"])

    def test_same_bytes_can_have_two_exact_readings(self):
        found = readings(MIXED_PATH)
        self.assertEqual([item.codec for item in found], ["cp950", "gbk"])
        self.assertIn("杂图", found[1].text)
        self.assertIn("同意条款", found[1].text)
        # Two readings, both exact: the module must not pick a winner silently.
        self.assertNotEqual(found[0].text, found[1].text)

    def test_ascii_only_escapes_are_not_claimed(self):
        self.assertEqual(readings(r"'\x41\x42'"), ())

    def test_undecodable_run_is_not_claimed(self):
        # 0x80 is not a valid lead byte; 0xFF never starts a CP950 or GBK pair.
        self.assertEqual(readings(r"'\x80\x80'"), ())
        self.assertEqual(readings(r"'\xff\xff'"), ())

    def test_raw_and_unicode_literals_are_not_claimed(self):
        self.assertEqual(readings(r"r'\xa5u\xaf\xe0'"), ())
        self.assertEqual(readings(r"u'\u4e2d\xa5u'"), ())

    def test_escaped_quote_survives_requoting(self):
        found = readings(r"'\xa5u\''")
        self.assertIsNotNone(found)
        self.assertTrue(found[0].text.endswith("\\''"), found[0].text)

    def test_triple_quoted_literal_keeps_its_delimiters(self):
        found = readings("'''\\xa5u\\xaf\\xe0'''")
        self.assertEqual(found[0].text, "'''只能'''")

    def test_decode_bytes_deduplicates_identical_text(self):
        self.assertEqual(decode_bytes(b"\xa5u\xaf\xe0", CODECS)[0].codec, "cp950")
        self.assertEqual(decode_bytes(b"abc"), ())

    def test_readable_literal_returns_empty_when_nothing_applies(self):
        self.assertIsNone(readable_literal("'plain'"))
        self.assertIsNone(readable_literal("1234"))

    def test_split_literal_understands_prefixes(self):
        self.assertEqual(split_literal("ur'abc'"), ("ur", "'", "abc"))
        self.assertIsNone(split_literal("not a literal"))


SAMPLE_SOURCE = "\n".join(
    [
        "def register():",
        f"    usermacro.PROMPT_MSG({BIG5_MESSAGE})",
        "    total = 1",
        f"    ui.CImage(self, {MIXED_PATH}, 'interface')",
        "    other = 'plain text'",
        "    unknown = '\\x80\\x80'",
        "    tail = 2",
    ]
)


class SourceScanTests(unittest.TestCase):
    SOURCE = SAMPLE_SOURCE

    def test_previews_report_line_and_column(self):
        records = previews(self.SOURCE)
        self.assertEqual([record.line for record in records], [2, 4])
        self.assertEqual(records[0].column, self.SOURCE.splitlines()[1].index("'"))
        self.assertTrue(records[0].text.startswith("'只能使用"))

    def test_summary_counts_literals_lines_and_codecs(self):
        counts = summary(previews(self.SOURCE))
        self.assertEqual(counts, {"literals": 2, "lines": 2, "codecs": ["cp950"]})

    def test_scan_is_bounded(self):
        source = "\n".join(f"x{i} = {BIG5_MESSAGE}" for i in range(MAX_RECORDS + 5))
        self.assertEqual(len(previews(source)), MAX_RECORDS)
        self.assertEqual(len(previews(source, limit=3)), 3)

    def test_unparsable_tail_does_not_discard_earlier_hints(self):
        source = "s = " + BIG5_MESSAGE + "\nif True:\n    s = (\n"
        self.assertEqual([record.line for record in previews(source)], [1])

    def test_line_previews_serve_hover_scanning(self):
        line = f"    ui.CImage(self, {MIXED_PATH}, 'interface')"
        found = line_previews(line)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].column, line.index("'"))
        self.assertEqual([item.codec for item in found[0].readings], ["cp950", "gbk"])

    def test_clamp_keeps_hints_short_and_single_line(self):
        self.assertEqual(clamp("a\nb", 10), "a b")
        self.assertEqual(len(clamp("x" * 50, 10)), 10)


class ReportTests(unittest.TestCase):
    SOURCE = SAMPLE_SOURCE

    def test_hint_names_every_exact_reading(self):
        hint = hint_for_position(f"x = {MIXED_PATH}", 5)
        self.assertIn(DISPLAY_ONLY, hint)
        self.assertIn("cp950:", hint)
        self.assertIn("gbk:", hint)

    def test_hint_is_empty_away_from_a_literal(self):
        self.assertEqual(hint_for_position(f"x = {MIXED_PATH}", 0), "")

    def test_hint_keeps_the_display_only_warning(self):
        hint = format_hint(previews("s = " + BIG5_MESSAGE)[0])
        self.assertTrue(hint.startswith(DISPLAY_ONLY))

    def test_report_lists_raw_and_every_reading(self):
        text, truncated = report_text(previews(self.SOURCE), "register.py")
        self.assertFalse(truncated)
        self.assertIn("文件：register.py", text)
        self.assertIn("第 2 行", text)
        self.assertIn("原文:", text)
        self.assertIn("cp950:", text)
        self.assertIn("gbk  :", text)
        self.assertIn("不参与编译", text)

    def test_report_is_bounded(self):
        source = "\n".join(f"x{i} = {BIG5_MESSAGE}" for i in range(500))
        text, truncated = report_text(previews(source), "big.py", limit=5000)
        self.assertTrue(truncated)
        self.assertLess(len(text), 8000)

    def test_report_never_contains_a_full_source_copy(self):
        # The report is a listing, not a rewritten module: no statements.
        text, _ = report_text(previews(self.SOURCE), "register.py")
        self.assertNotIn("def register", text)
        self.assertNotIn("usermacro.PROMPT_MSG", text)


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class LiteralReportDialogTests(unittest.TestCase):
    SOURCE = SAMPLE_SOURCE

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_dialog_body_is_read_only_and_copyable(self):
        dialog = LiteralReportDialog(None, previews(self.SOURCE), "register.py")
        try:
            self.assertTrue(dialog.body.isReadOnly())
            self.assertIn("可读对照", dialog.body.toPlainText())
            labels = [button.text() for button in dialog.findChildren(QPushButton)]
            self.assertIn("复制全部", labels)
        finally:
            dialog.deleteLater()

if __name__ == "__main__":
    unittest.main()
