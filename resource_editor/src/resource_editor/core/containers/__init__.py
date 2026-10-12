"""资源包容器层：按魔数分发到 0SLF / FLS\\x00 两种实现。"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..errors import ContainerError
from . import fls0slf, flsdata

KIND_0SLF = "0slf"
KIND_FLSDATA = "flsdata"


@dataclass
class Archive:
    """统一容器视图：条目存储字节 + 构建自身所需的状态。"""

    kind: str
    payloads: list[bytes]
    source0slf: fls0slf.Fls0SlfArchive | None = None
    source_data: flsdata.FlsDataArchive | None = None
    extra_metas: list = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.payloads)

    def build(self, payloads: list[bytes]) -> bytes:
        """用新的存储字节列表重建整个包字节（条目数可增减）。"""
        if self.kind == KIND_0SLF:
            return fls0slf.build(payloads, self.extra_metas)
        return flsdata.build(self._data_with_metas(), payloads)

    def _data_with_metas(self) -> flsdata.FlsDataArchive:
        assert self.source_data is not None
        return flsdata.FlsDataArchive(
            header=self.source_data.header,
            payloads=[],
            metas=self.extra_metas,
        )


def open_archive(data: bytes) -> Archive:
    """按魔数解析包字节，返回统一 :class:`Archive`。"""
    if data[:4] == fls0slf.MAGIC:
        parsed = fls0slf.parse(data)
        return Archive(
            kind=KIND_0SLF,
            payloads=list(parsed.payloads),
            source0slf=parsed,
            extra_metas=list(parsed.metas),
        )
    if data[:4] == flsdata.MAGIC:
        parsed = flsdata.parse(data)
        return Archive(
            kind=KIND_FLSDATA,
            payloads=list(parsed.payloads),
            source_data=parsed,
            extra_metas=list(parsed.metas),
        )
    raise ContainerError(f"未知资源包魔数：{data[:4]!r}")
