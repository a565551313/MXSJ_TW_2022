"""WAV 条目识别与头解析：sound.fls 三种编码的时长口径。

样本按真实条目的块布局手工拼装（PCM / GSM 6.10 / IMA-ADPCM），
样本数必须与 libsndfile 对真实文件的解码结果一致（GSM 每
65 字节块 320 样本、IMA 每 1024 字节块 2041 样本）。
"""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from resource_editor.core.codecs import detect, wav  # noqa: E402


def _wav(tag: int, data_size: int, *, rate: int = 44100,
         channels: int = 1, bits: int = 16, block_align: int = 2,
         per_block: int | None = None,
         fact: int | None = None) -> bytes:
    fmt = struct.pack("<HHIIHH", tag, channels, rate,
                      rate * block_align, block_align, bits)
    if per_block is not None:
        fmt += struct.pack("<HH", 2, per_block)
    out = bytearray(b"RIFF\x00\x00\x00\x00WAVE")
    out += b"fmt " + struct.pack("<I", len(fmt)) + fmt
    if fact is not None:
        out += b"fact" + struct.pack("<II", 4, fact)
    out += b"data" + struct.pack("<I", data_size)
    out += b"\x00" * data_size
    struct.pack_into("<I", out, 4, len(out) - 8)
    return bytes(out)


class TestWavInfo(unittest.TestCase):
    def test_pcm(self):
        content = _wav(1, 88200)  # 44100 个 16 位单声道样本
        info = wav.parse_wav_info(content)
        self.assertIsNotNone(info)
        assert info is not None
        self.assertEqual(info.tag_name, "PCM")
        self.assertEqual(info.samples, 44100)
        self.assertAlmostEqual(info.duration or 0, 1.0)
        self.assertIs(detect.sniff(content), detect.EntryKind.AUDIO)

    def test_gsm_block_count(self):
        # 真实 sound_0011：56 个 65 字节块 × 320 样本 = 17920
        content = _wav(49, 56 * 65, bits=0, block_align=65,
                       per_block=320, fact=17920)
        info = wav.parse_wav_info(content)
        assert info is not None
        self.assertEqual(info.tag_name, "GSM 6.10")
        self.assertEqual(info.samples, 17920)

    def test_ima_block_count_beats_fact(self):
        # 真实 sound_0044：34 个 1024 字节块 × 2041 = 69394，
        # 文件尾 fact 自报 70164 与块结构对不上，以块为准
        content = _wav(17, 34 * 1024, bits=4, block_align=1024,
                       per_block=2041, fact=70164)
        info = wav.parse_wav_info(content)
        assert info is not None
        self.assertEqual(info.tag_name, "IMA-ADPCM")
        self.assertEqual(info.samples, 69394)
        self.assertAlmostEqual(info.duration or 0, 69394 / 44100)

    def test_not_wav(self):
        self.assertIsNone(wav.parse_wav_info(b"I0\x01\x00garbage"))
        self.assertFalse(wav.is_wav(b"RIFF\x00\x00\x00\x00AVI "))


if __name__ == "__main__":
    unittest.main()
