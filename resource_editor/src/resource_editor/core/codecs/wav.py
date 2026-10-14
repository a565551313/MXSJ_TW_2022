"""RIFF WAV 条目识别与头信息解析（sound.fls 整份存入的标准音频）。

包里存的就是一份完整 ``.wav`` 文件：``RIFF`` 头、``fmt `` 编码
描述、``data`` 波形，个别条目尾巴还带 ``fact``/``LIST``/``smpl``
等制作软件留下的块。本模块只读头算时长，不解码波形（播放交给
系统的多媒体后端，导出则原字节落 ``.wav``）。
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

_TAG_NAMES = {
    1: "PCM",
    17: "IMA-ADPCM",
    49: "GSM 6.10",
    85: "MP3",
}


def is_wav(content: bytes) -> bool:
    """内容是否为 RIFF WAV 文件。"""
    return len(content) >= 12 and content[:4] == b"RIFF" \
        and content[8:12] == b"WAVE"


@dataclass(frozen=True)
class WavInfo:
    """WAV 头信息汇总（解析不出时字段为 None）。"""

    tag: int
    channels: int
    sample_rate: int
    bits: int
    samples: int | None = None

    @property
    def tag_name(self) -> str:
        return _TAG_NAMES.get(self.tag, f"tag {self.tag}")

    @property
    def duration(self) -> float | None:
        if self.samples is None or not self.sample_rate:
            return None
        return self.samples / self.sample_rate

    def describe(self) -> str:
        parts = [f"WAV（{self.tag_name}）",
                 f"{self.channels} 声道",
                 f"{self.sample_rate} Hz"]
        if self.bits:
            parts.append(f"{self.bits} bit")
        if self.duration is not None:
            parts.append(f"约 {self.duration:.2f} 秒")
        return "，".join(parts)


def parse_wav_info(content: bytes) -> WavInfo | None:
    """解析 WAV 的 fmt/fact/data 块算出样本数；非 WAV 返回 None。

    样本数口径：PCM 按 data 字节数除以每样本字节数；IMA-ADPCM /
    GSM 按块对齐与每块样本数（fmt 附加字段）乘块数；两者都算不出
    时回退 fact 块的自报值（个别制作工具的 fact 与实际块数对不
    上，故只作兜底）。
    """
    if not is_wav(content):
        return None
    fmt: tuple | None = None
    fact_samples: int | None = None
    data_size: int | None = None
    pos = 12
    while pos + 8 <= len(content):
        cid = content[pos:pos + 4]
        size = struct.unpack_from("<I", content, pos + 4)[0]
        body = pos + 8
        if cid == b"fmt " and size >= 16:
            fmt = struct.unpack_from("<HHIIHH", content, body)
            per_block = None
            if size >= 20:
                # fmt 附加区：cbSize 后跟每块样本数（ADPCM/GSM）
                per_block = struct.unpack_from(
                    "<H", content, body + 18)[0]
            fmt = (*fmt, per_block)
        elif cid == b"fact" and size >= 4:
            fact_samples = struct.unpack_from("<I", content, body)[0]
        elif cid == b"data":
            data_size = size
            break
        pos += 8 + size + (size & 1)
    if fmt is None:
        return None
    tag, channels, rate, _byterate, block_align, bits, per_block = fmt
    samples = _count_samples(tag, channels, bits, block_align,
                             per_block, data_size)
    if samples is None:
        samples = fact_samples
    return WavInfo(tag=tag, channels=channels, sample_rate=rate,
                   bits=bits, samples=samples)


def _count_samples(tag: int, channels: int, bits: int,
                   block_align: int, samples_per_block: int | None,
                   data_size: int | None) -> int | None:
    if data_size is None or channels <= 0:
        return None
    if tag == 1:  # PCM：每样本 bits/8 字节
        per_sample = max(1, bits // 8) * channels
        return data_size // per_sample
    if samples_per_block and block_align > 0:
        # IMA-ADPCM / GSM：整块数 × 每块样本数
        return (data_size // block_align) * samples_per_block
    return None
