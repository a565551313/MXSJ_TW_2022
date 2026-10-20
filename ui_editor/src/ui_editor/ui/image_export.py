"""把包内图片导出为电脑上的文件（选图窗「导出」按钮用）。

- 本来就是真图片格式（PNG/JPG/GIF/BMP 字节）→ 原样写出；
- 游戏精灵格式（内容是 I0/T0/I1 精灵）→ 逐帧存成 PNG，能直接
  打开看、改，改完可通过「添加新图到包」放回去（音效等非图
  数据原样写出）；
- 既认不出也解不出 → 仍把原始字节写出，不假装丢失。

批量导出请传 ``used_names``（本批已占用名字集合）：同名资源改写成
``btn-2.png``，不再静默覆盖本批中先写出的文件。
"""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from ..core.output_paths import guard_output

_REAL_MAGICS = (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"GIF8", b"BM")


def _basename(path: str) -> str:
    name = path.replace("\\", "/").rstrip("/").split("/")[-1]
    return name or "image"


def _frame_names(name: str, count: int) -> list[str]:
    """一个资源会写出的文件名（不落盘）：单帧一张，多帧 ``-0``、``-1``…"""
    stem = name.rsplit(".", 1)[0] if "." in name else name
    if count <= 1:
        return [f"{stem}.png"]
    return [f"{stem}-{index}.png" for index in range(count)]


def _suffixed(filename: str, index: int) -> str:
    """``btn.png`` → ``btn-2.png``（index=2）；index<=1 原样返回。"""
    if index <= 1:
        return filename
    stem, dot, suffix = filename.rpartition(".")
    if not dot or not stem:
        return f"{filename}-{index}"
    return f"{stem}-{index}.{suffix}"


def _reserve_names(names: list[str], used: set[str] | None) -> list[str]:
    """在批量导出里为一批目标占名，重名整体加序号，绝不覆盖本批已写出的。"""
    if used is None:
        return names
    index = 1
    while True:
        candidate = [_suffixed(name, index) for name in names]
        if not any(name.lower() in used for name in candidate):
            used.update(name.lower() for name in candidate)
            return candidate
        index += 1


def export_image_files(res_path: str, data: bytes | None,
                       frames, dest_dir, dest_name: str | None = None,
                       protected_paths: Iterable[str | Path] = (),
                       used_names: set[str] | None = None,
                       ) -> list[Path]:
    """导出一个资源，返回实际写出的文件列表（可能多帧多个）。

    frames 是解码好的 QImage 列表（调用方从解析器取）；data 为
    原始字节。dest_name 只在单文件导出时生效（保存框选的名字）。

    ``used_names`` 供**批量**导出共用：本批已占用的输出文件名（小写）。
    传了就保证不覆盖本批先写出的同名文件（``a/btn.png`` 与 ``b/btn.png``
    导出成 ``btn.png`` / ``btn-2.png``）；不传则保持单次导出的原行为
    （同名覆盖磁盘上的旧文件）。
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    name = dest_name or _basename(res_path)
    sources = list(protected_paths)
    if data is not None and data.startswith(_REAL_MAGICS):
        [name] = _reserve_names([name], used_names)
        out = dest / name
        guard_output(out, sources, dest)
        out.write_bytes(data)
        return [out]
    if frames:
        names = _reserve_names(_frame_names(name, len(frames)), used_names)
        paths = [dest / item for item in names]
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
        # 解不出帧的精灵/实在认不出的字节：原样留一份，同样参与批量占名。
        [fallback] = _reserve_names([dest_name or _basename(res_path)],
                                    used_names)
        out = dest / fallback
        guard_output(out, sources, dest)
        out.write_bytes(data)
        return [out]
    return []
