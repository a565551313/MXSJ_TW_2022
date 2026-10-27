"""Display-only decoding of legacy Big5/GBK byte literals.

These tests pin the two things that matter: the reading must be exact (or
absent), and nothing may produce source text that a caller could save.
"""

from __future__ import annotations

import time
import unittest
from types import SimpleNamespace

from script_editor.core.inspection.legacy_text import (
    CODECS,
    DISPLAY_ONLY,
    MAX_RECORDS,
    RESTORED_NOTE,
    ScanResult,
    clamp,
    decode_bytes,
    format_hint,
    hint_for_position,
    line_previews,
    literal_bytes,
    previews,
    readable_literal,
    readings,
    rendered_bytes,
    report_text,
    scan,
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

    def test_unicode_literals_are_not_claimed(self):
        # u'...' holds code points, not the MBCS bytes the client compares.
        self.assertEqual(readings(r"u'\u4e2d\xa5u'"), ())
        self.assertEqual(readings(r"u'\xa5u\xaf\xe0'"), ())

    def test_raw_literal_gets_a_marked_restored_reading(self):
        """``r'\xa5u'`` has no MBCS bytes — but the decompiler's intent can be read.

        The value of a raw string is the backslash text itself, so this reading
        is explicitly marked ``restored`` and the hint says so.
        """
        found = readings(r"r'\xa5u\xaf\xe0'")
        self.assertEqual([r.codec for r in found], ["cp950"])
        self.assertTrue(all(r.restored for r in found))
        self.assertEqual(found[0].text, "r'只能'")

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

    def test_escaped_quote_does_not_end_the_literal_early(self):
        """Hover and highlight must agree on where the literal stops."""
        source = r"""x = '\xa5u\''"""
        found = line_previews(source)
        self.assertEqual(len(found), 1)
        # Same column either way; the old pattern closed the string at the
        # escaped quote and hover found nothing at the highlight position.
        records = previews(source)
        self.assertEqual([record.column for record in records], [found[0].column])

    def test_unicode_prefixed_literal_gets_no_reading(self):
        # u'...' is already text; decoding its body as cp950 would invent a
        # reading that never ships in the package.
        self.assertEqual(readings(r"""u'\xa5u\xaf\xe0'"""), ())
        self.assertEqual(previews(r"""u'\xa5u\xaf\xe0'"""), ())

    def test_pathological_line_stays_linear(self):
        """A long line of escaped quotes used to be quadratic (0.8 s / 16 KB).

        Hovering one physical line must never freeze the editor, so this pins
        the scanner's cost rather than its output. The bound is deliberately
        loose (200 KB in well under a second); the quadratic version needed
        minutes at this size.
        """
        line = "x = '" + ("aaa\\'") * 50_000
        self.assertGreater(len(line), 200_000)
        started = time.perf_counter()
        self.assertEqual(line_previews(line), ())
        self.assertLess(time.perf_counter() - started, 1.0)

    def test_raw_literal_with_ascii_result_is_still_not_claimed(self):
        # ESC + "[0m" carries no non-ASCII text, so there is nothing to show.
        self.assertEqual(readings(r"r'\x1b[0m'"), ())

    def test_decompiler_docstring_rendering_reads_as_the_original_text(self):
        # Real shape from the recovered corpus (script/login/dgw.py): uncompyle6
        # decodes a py2 str as UTF-8 with backslash escapes, so a Big5 docstring
        # comes back as r-triple-quoted text mixing \xNN escapes with the byte
        # pairs that happened to be valid UTF-8 (here "Ϊ", "Ⱦ", "榡", "и").
        literal = (
            r'r"""\xc0\xf2\xa8\xfa\xa5i\xa5ΪA\xb0Ⱦ\xb9\xa6C\xaa\xed\xa1A'
            r'\xae榡\xac\xb0[(\xa9и\xb9, \xb7~\xb0ȪA\xa6a\xa7}, udpPort"""'
        )
        found = readings(literal)
        self.assertEqual(len(found), 1)
        self.assertTrue(found[0].restored)
        self.assertIn("獲取可用服務器列表", found[0].text)
        self.assertIn("房號", found[0].text)

    def test_hint_marks_restored_readings_and_explains_why(self):
        plain = SimpleNamespace(readings=readings(r"'\xa5u\xaf\xe0'"))
        self.assertNotIn("反推候选", format_hint(plain))
        restored = SimpleNamespace(readings=readings(r"r'\xa5u\xaf\xe0'"))
        hint = format_hint(restored)
        self.assertIn("（反推候选）", hint)
        self.assertIn("反编译器", hint)
        self.assertIn("候选而不是逐字节证明", RESTORED_NOTE)

    def test_big5_trail_byte_0x5c_is_one_byte_not_an_escape(self):
        """Corpus shape from ``script/login/dgw.py:118``.

        ``成功連線`` is ``A6 A8 A5 5C B3 73``. uncompyle6 copies the payload's
        0x5C through as a *single* backslash, so the rendering reads
        ``\\xa5`` + one ``\\`` + ``\\xb3``. Treating the adjacent pair as an escaped
        backslash swallowed the ``\xb3`` and produced ``成功xb3s`` — a wrong
        reading presented as if it were proven.
        """
        payload = "成功連上遊戲服務器".encode("cp950")
        body = "".join(
            "\\" if byte == 0x5C else f"\\x{byte:02x}" for byte in payload
        )
        found = readings('r"""' + body + '"""')
        self.assertEqual(len(found), 1)
        self.assertTrue(found[0].restored)
        self.assertIn("成功連上遊戲服務器", found[0].text)
        self.assertEqual(rendered_bytes(body), payload)

    def test_backslash_runs_survive_verbatim(self):
        # 0x5C 0x5C in the payload renders as ``\\``: two bytes, not one.
        self.assertEqual(rendered_bytes("\\\\"), bytes.fromhex("5c5c"))
        self.assertEqual(len(rendered_bytes("\\\\")), 2)

    def test_plain_literals_are_not_marked_restored(self):
        self.assertFalse(any(r.restored for r in readings(r"'\xa5u\xaf\xe0'")))

    def test_ansi_escape_is_never_decoded_as_text(self):
        # \033 is octal ESC; it used to be read as NUL + "33[0m" and turn into
        # a fake reading containing terminal junk.
        self.assertEqual(readings(r"'\xa5\xaf\033[0m'"), ())
        self.assertIsNone(literal_bytes(r"'\xa5\xaf\033[0m'"))

    def test_control_bytes_are_shown_escaped_not_raw(self):
        # A lone \t is a real byte in the packet, so the reading is legitimate,
        # but the hint must never carry a raw control character into a tooltip.
        found = readings(r"'\xa5\xaf\t'")
        self.assertTrue(found)
        for reading in found:
            self.assertNotIn("\t", reading.text)

    def test_nul_escape_with_octal_digits_is_refused_not_guessed(self):
        # \012 is an octal newline, not NUL followed by the text "12".
        self.assertIsNone(literal_bytes(r"\012"))
        self.assertEqual(readings(r"'\012'"), ())

    def test_bare_nul_escape_still_works(self):
        self.assertEqual(literal_bytes(r"'a\0b'"), b"'a\x00b'")

    def test_clamp_keeps_hints_short_and_single_line(self):
        self.assertEqual(clamp("a\nb", 10), "a b")
        self.assertEqual(len(clamp("x" * 50, 10)), 10)


class ScanResultTests(unittest.TestCase):
    def test_complete_scan_reports_no_reason(self):
        result = scan(SAMPLE_SOURCE)
        self.assertIsInstance(result, ScanResult)
        self.assertTrue(result.complete)
        self.assertEqual(result.reason, "")
        self.assertEqual(len(result.records), 2)

    def test_unparsable_source_is_incomplete_but_keeps_earlier_records(self):
        result = scan("s = " + BIG5_MESSAGE + "\nif True:\n    s = (\n")
        self.assertFalse(result.complete)
        self.assertTrue(result.reason)
        self.assertEqual([record.line for record in result.records], [1])

    def test_limit_is_reported_as_incomplete(self):
        source = "\n".join(f"x{i} = {BIG5_MESSAGE}" for i in range(MAX_RECORDS + 5))
        result = scan(source)
        self.assertFalse(result.complete)
        self.assertIn(str(MAX_RECORDS), result.reason)
        self.assertEqual(len(result.records), MAX_RECORDS)

    def test_previews_forwards_the_records_only(self):
        self.assertEqual(
            [r.line for r in previews(SAMPLE_SOURCE)],
            [r.line for r in scan(SAMPLE_SOURCE).records],
        )


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
