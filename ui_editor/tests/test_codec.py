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
        self.assertEqual(self.dicts[0]["sTitle"], "測試對話框")

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
            "sText": "引\"號 與 \\ 反斜線\n換行\t製表",
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


REPO_ROOT = Path(__file__).resolve().parents[2]
#: 仓库内自带的真实布局（注册界面模板）：语料可以缺失，但这批必须恒跑
REPO_CORPUS_DIR = REPO_ROOT / "tools" / "registration"
REPO_CORPUS_MIN = 7
#: 外部大语料只有在给定目录时才跑；低于这个数量只按数量上报，不再判失败
BIG_CORPUS = 2000


def _corpus_roots() -> list[Path]:
    """外部语料目录：只认环境变量，不再硬编码开发沙箱的绝对路径。

    以前这里有 ``/home/user/interface_dlg_decoded`` 兜底，于是「这条硬门槛」
    在别的机器上要么静默跳过、要么因为语料只有 8 篇而 ``assertGreater(2000)``
    直接 FAIL——连那 8 篇都不跑（分析报告 P1-4）。现在拆成两条路：
    仓库内最小语料恒跑，外部语料按数量上报。
    """
    raw = os.environ.get("MXSJ_DLG_CORPUS", "")
    roots = [Path(part) for part in raw.split(os.pathsep) if part.strip()]
    return [root for root in roots if root.is_dir()]


def _roundtrip_failures(files: list[Path]) -> list[str]:
    """解析→序列化→再解析，结构不一致的文件（最多记 5 个）。"""
    failures: list[str] = []
    for path in files:
        dicts, _ = dlg_codec.parse_bytes(path.read_bytes())
        again, _ = dlg_codec.parse_text(dlg_codec.dump_text(dicts))
        if not structures_equal(dicts, again):
            failures.append(str(path))
            if len(failures) >= 5:
                break
    return failures


class TestRepoCorpusRoundTrip(unittest.TestCase):
    """仓库内自带的最小语料：恒跑，缺文件就红，不允许再「静默跳过」。"""

    def test_repo_corpus_roundtrips(self):
        real = sorted(REPO_CORPUS_DIR.rglob("*.dlg"))
        self.assertGreaterEqual(
            len(real), REPO_CORPUS_MIN,
            f"{REPO_CORPUS_DIR} 下真实 .dlg 只有 {len(real)} 篇"
            f"（期望 ≥ {REPO_CORPUS_MIN}）；语料丢了就该修，而不是跳过")
        files = real + [FIXTURE]
        failures = _roundtrip_failures(files)
        self.assertEqual(
            failures, [],
            f"共 {len(files)} 篇（仓库内）结构往返不一致")


class TestCorpusRoundTrip(unittest.TestCase):
    """外部语料：可用多少跑多少，结果按数量上报（不再一刀切 2,000 门槛）。"""

    def test_all_decoded_files_roundtrip(self):
        roots = _corpus_roots()
        if not roots:
            self.skipTest(
                "未提供外部 .dlg 语料库（设置 MXSJ_DLG_CORPUS 指向目录）；"
                "仓库内最小语料已由 TestRepoCorpusRoundTrip 覆盖")
        files = sorted({path for root in roots for path in root.rglob("*.dlg")})
        if not files:
            self.skipTest(f"语料目录里没有 .dlg：{', '.join(map(str, roots))}")
        failures = _roundtrip_failures(files)
        if len(files) < BIG_CORPUS:
            print(f"[codec] 外部语料仅 {len(files)} 篇"
                  f"（< {BIG_CORPUS}）：结论按此数量声明，勿写作全量验证")
        self.assertEqual(failures, [], f"外部语料 {len(files)} 篇中往返不一致")


if __name__ == "__main__":
    unittest.main()
