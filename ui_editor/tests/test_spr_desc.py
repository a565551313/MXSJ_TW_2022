"""`.spr` 帧时表解码（`core/spr_desc.py`）——官服 1019 实测格式的回归。

`.spr` = 4 字节 XOR 的 INI（`[frames]` 帧号+时长），同名 `.igs` 供像素。
这里合成已知密钥的样例锁住：确定性解码、帧表解析、帧图候选、
非 `.spr` 不猜。
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core.spr_desc import (  # noqa: E402
    decode_spr_text,
    frame_sources,
    parse_frame_table,
    parse_images,
)


def _xor4(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % 4] for i, b in enumerate(data))


KEY = b"\x2e\xa7\xdd\x80"


class TestSprDesc(unittest.TestCase):
    def test_frames_table_roundtrip(self):
        text = "[frames]\n0 5\n1 5\n2 4\n10 6\n"
        got = decode_spr_text(_xor4(text.encode("ascii"), KEY))
        self.assertEqual(got, text)
        self.assertEqual(parse_frame_table(got),
                         ((0, 5), (1, 5), (2, 4), (10, 6)))

    def test_info_variant_and_whitespace(self):
        text = "[info]\nname x\n[frames]\n0 3\t1 3\n"
        got = decode_spr_text(_xor4(text.encode("ascii"), KEY))
        self.assertIsNotNone(got)
        self.assertEqual(parse_frame_table(got), ((0, 3), (1, 3)))

    def test_unknown_section_bruteforced_for_small_files(self):
        # 首段不在候选表（[wave]）：≤512 字节走可打印前缀穷举
        text = "[wave]\n0 2\n1 2\n"
        got = decode_spr_text(_xor4(text.encode("ascii"), b"\x01\x02\x03\x04"))
        self.assertEqual(got, text)

    def test_binary_garbage_is_not_guessed(self):
        self.assertIsNone(decode_spr_text(b"\x89PNG\r\n\x1a\n" + b"\x00" * 40))
        self.assertIsNone(decode_spr_text(b"short"))
        self.assertIsNone(decode_spr_text(bytes(range(64, 128)) * 4))

    def test_frame_sources_prefers_igs_sibling(self):
        self.assertEqual(frame_sources("a\\b\\烟2_.spr"),
                         ("a\\b\\烟2_.igs", "a\\b\\烟2_.png"))
        self.assertEqual(frame_sources("x.spr"), ("x.igs", "x.png"))

    def test_images_section_external_pointer(self):
        # 及时雨/引天雷 形态：[images] 指向别的包里的文件
        text = ("[images]\nFileName1=magic0307.igs\nPackageName=magic\n"
                "BranchPath=res\\\nPalPro=259 0 0 0 108 292 0 59 0\n"
                "[frames]\n0 3\n1 3\n")
        info = parse_images(text)
        self.assertEqual(info["files"], ("magic0307.igs",))
        self.assertEqual(info["package"], "magic")
        self.assertTrue(info["palpro"].startswith("259"))
        self.assertEqual(parse_images("[frames]\n0 3\n"), {})
        # [images] 记录外部包和分支，候选保留来源，避免同名资源串包。
        got = frame_sources("x.spr", text)
        self.assertEqual(got, ("magic:res\\magic0307.igs", "x.igs", "x.png"))


if __name__ == "__main__":
    unittest.main()
