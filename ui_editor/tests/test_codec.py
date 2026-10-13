"""编解码测试：样例保真 + 全量语料库往返（结构一致才算过）。"""
import ast
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core import dlg_codec  # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "original_style.dlg"


def structures_equal(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(
            structures_equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(
            structures_equal(x, y) for x, y in zip(a, b, strict=True))
    return a == b


class TestParseFixture(unittest.TestCase):
    def setUp(self):
        self.dicts, self.md5 = dlg_codec.parse_bytes(FIXTURE.read_bytes())

    def test_header_and_roots(self):
        self.assertEqual(self.md5, "0123456789abcdef0123456789abcdef")
        self.assertEqual(len(self.dicts), 4)
        self.assertEqual(self.dicts[0]["sWidgetType"], "CMainFrame")
        self.assertEqual(self.dicts[0]["sTitle"], "测试对话框")

    def test_tuple_and_float_keep_type(self):
        button = self.dicts[1]
        self.assertIsInstance(button["tTextOffset"], tuple)
        self.assertEqual(button["tTextOffset"], (2, 1))
        self.assertIsInstance(button["lNormalColor"], list)
        self.assertIsInstance(self.dicts[3]["fScaleX"], float)

    def test_nested_children(self):
        box = self.dicts[2]
        self.assertEqual(len(box["lChildren"]), 1)
        self.assertEqual(box["lChildren"][0]["sText"], "第一行\n第二行")

    def test_dump_roundtrip(self):
        text = dlg_codec.dump_text(self.dicts, self.md5)
        again, md5 = dlg_codec.parse_text(text)
        self.assertTrue(structures_equal(self.dicts, again))
        self.assertEqual(md5, self.md5)

    def test_dumped_text_is_executable_shape(self):
        # 与原文件同款骨架：头两行 + UI_INFO 字面量赋值
        text = dlg_codec.dump_text(self.dicts, self.md5)
        self.assertTrue(text.startswith("# -*- coding: gbk -*-\n# MD5: "))
        value = ast.literal_eval(text.split("UI_INFO = ", 1)[1])
        self.assertEqual(len(value), 4)


class TestValuesRoundTrip(unittest.TestCase):
    def test_escapes_and_chinese(self):
        dicts = [{
            "sWidgetType": "CTextFrame",
            "sText": "引\"号 与 \\ 反斜杠\n换行\t制表",
            "iX": -3,
            "fRatio": 0.25,
            "bShow": True,
            "lColor": [255, 128, 0],
            "tOff": (1,),
        }]
        data = dlg_codec.dump_bytes(dicts)
        again, _ = dlg_codec.parse_bytes(data)
        self.assertTrue(structures_equal(dicts, again))

    def test_gbk_bytes_on_disk(self):
        data = dlg_codec.dump_bytes(
            [{"sWidgetType": "CBox", "sName": "框一"}])
        self.assertIn("框一".encode("gbk"), data)


def _corpus_root():
    env = os.environ.get("MXSJ_DLG_CORPUS")
    candidates = [env] if env else []
    candidates.append("/home/user/interface_dlg_decoded")
    for cand in candidates:
        if cand and Path(cand).is_dir():
            return Path(cand)
    return None


class TestCorpusRoundTrip(unittest.TestCase):
    """硬门槛：全部已解密 .dlg 经解析→序列化→再解析结构不变。"""

    def test_all_decoded_files_roundtrip(self):
        root = _corpus_root()
        if root is None:
            self.skipTest("没有 .dlg 语料库（设置 MXSJ_DLG_CORPUS）")
        files = sorted(root.rglob("*.dlg"))
        self.assertGreater(len(files), 2000)
        failures = []
        for path in files:
            dicts, _ = dlg_codec.parse_bytes(path.read_bytes())
            again, _ = dlg_codec.parse_text(dlg_codec.dump_text(dicts))
            if not structures_equal(dicts, again):
                failures.append(str(path))
                if len(failures) >= 5:
                    break
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
