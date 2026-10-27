"""Read original filename as raw bytes; never guess UTF8/GBK or execute a module."""

from __future__ import annotations

import zlib

from ..policy import require_module_allowed
from ..vm.compression import inflate
from ..vm.marshal_tree import parse
from ..vm.py25 import codec as py25
from ..vm.py25.keys import inflate_script, load_profile
from ..vm.py27 import codec as py27


def inspect_module(archive, index, catalog=None):
    require_module_allowed(archive.vm, index)
    if (
        type(index) is not int
        or not 0 <= index < len(archive.entries)
        or archive.entries[index].directory
    ):
        raise ValueError("不是脚本条目")
    stored = archive.read_stored(index)
    profile = None
    if archive.vm == "py25":
        if catalog is None:
            raise ValueError(
                "这个 script 包还没有可用的五段 XOR 解码参数："
                "内置参数会在打开包时自动匹配；未登记的新包需要外部参数文件"
            )
        catalog.verify(archive)
        profile = load_profile(
            archive,
            index,
            catalog.path,
            archive_sha256=archive.fingerprint(),
            catalog_sha256=catalog.sha256,
        )
        standard = py25.decode(
            profile.crypt(inflate_script(archive, index)), padding=True
        )
    else:
        span = archive.index.spans[index]
        if archive.index.metas[index].w1 != 8:
            raise ValueError("不支持的data压缩方法")
        native = inflate(stored, raw=True)
        if len(native) != span.usize or zlib.crc32(native) & 0xFFFFFFFF != span.crc:
            raise ValueError("原条目CRC/长度不符")
        standard = py27.decode(native)
    filename = parse(standard[8:]).fields[5].value
    if (
        not isinstance(filename, bytes)
        or not filename
        or len(filename) > 8192
        or b"\0" in filename
    ):
        raise ValueError("原模块嵌入文件名无法无损读取")
    return standard, filename, profile
