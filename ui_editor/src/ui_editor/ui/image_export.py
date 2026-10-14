"""把包内图片导出为电脑上的文件（选图窗「导出」按钮用）。

- 本来就是真图片格式（PNG/JPG/GIF/BMP 字节）→ 原样写出；
- 游戏精灵格式（内容是 I0/T0/I1 精灵）→ 逐帧存成 PNG，能直接
  打开看、改，改完可通过「添加新图到包」放回去（音效等非图
  数据原样写出）；
- 既认不出也解不出 → 仍把原始字节写出，不假装丢失。
"""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from ..core import sprite
from ..core.output_paths import guard_output

_REAL_MAGICS = (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"GIF8", b"BM")


def _basename(path: str) -> str:
    name = path.replace("\\", "/").rstrip("/").split("/")[-1]
    return name or "image"


def export_image_files(res_path: str, data: bytes | None,
                       frames, dest_dir, dest_name: str | None = None,
                       protected_paths: Iterable[str | Path] = (),
                       ) -> list[Path]:
    """导出一个资源，返回实际写出的文件列表（可能多帧多个）。

    frames 是解码好的 QImage 列表（调用方从解析器取）；data 为
    原始字节。dest_name 只在单文件导出时生效（保存框选的名字）。
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    name = dest_name or _basename(res_path)
    sources = list(protected_paths)
    if data is not None and data.startswith(_REAL_MAGICS):
        out = dest / name
        guard_output(out, sources, dest)
        out.write_bytes(data)
        return [out]
    if frames:
        stem = name.rsplit(".", 1)[0] if "." in name else name
        paths = [dest / (f"{stem}.png" if len(frames) == 1
                         else f"{stem}-{index}.png")
                 for index in range(len(frames))]
        for out in paths:
            guard_output(out, sources, dest)
        written = []
        for frame, out in zip(frames, paths, strict=True):
            guard_output(out, sources, dest)
            if frame.save(str(out), "PNG"):
                written.append(out)
        if written:
            return written
    if data is not None:
        if sprite.is_sprite(data):
            # 解不出帧的精灵也把原始字节留给用户
            out = dest / name
        else:
            out = dest / (dest_name or _basename(res_path))
        guard_output(out, sources, dest)
        out.write_bytes(data)
        return [out]
    return []
