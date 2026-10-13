"""导出服务：把条目导出为 PNG（精灵逐帧/画布合成）或原始文件。"""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

from ..codecs import detect
from ..codecs.sprite import Sprite, decode_sprite
from ..model.document import PackDocument
from ..names import unpack_dlg_text


def export_sprite_frames(sprite: Sprite, out_dir: Path, stem: str) -> list[Path]:
    """导出精灵全部帧为 ``<stem>_fNN.png``。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for fi in range(sprite.frame_count):
        path = out_dir / f"{stem}_f{fi:02d}.png"
        sprite.render_frame(fi).save(path)
        paths.append(path)
    return paths


def export_entry(doc: PackDocument, index: int, out_dir: Path) -> list[Path]:
    """按条目类型导出单个条目，返回生成的文件列表。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    kind = doc.entry_kind(index)
    stem = f"{Path(doc.path).stem if doc.path else 'pack'}_{index:04d}"
    content = doc.content(index)
    if kind is detect.EntryKind.SPRITE:
        return export_sprite_frames(decode_sprite(content), out_dir, stem)
    if kind is detect.EntryKind.PNG:
        path = out_dir / f"{stem}.png"
        Image.open(io.BytesIO(content)).save(path)
        return [path]
    ext = {detect.EntryKind.JSON: ".json", detect.EntryKind.TEXT: ".txt"}
    path = out_dir / f"{stem}{ext.get(kind, '.bin')}"
    path.write_bytes(content)
    return [path]


def export_all_sprites(doc: PackDocument, out_dir: Path) -> int:
    """导出包内全部精灵条目，返回导出的精灵个数。"""
    count = 0
    for index in range(doc.count):
        if doc.entry_kind(index) is detect.EntryKind.SPRITE:
            export_entry(doc, index, out_dir)
            count += 1
    return count


_KIND_EXT = {
    detect.EntryKind.PNG: ".png",
    detect.EntryKind.JSON: ".json",
    detect.EntryKind.TEXT: ".txt",
}
_BAD_FILENAME_CHARS = '<>:"|?*'


def _safe_parts(name: str) -> list[str]:
    """把真名拆成安全的相对路径段（防穿越/防 Windows 非法字符）。"""
    parts = []
    for part in name.replace("\\", "/").split("/"):
        part = part.strip().strip(".")
        part = "".join("_" if c in _BAD_FILENAME_CHARS else c
                       for c in part)
        if part:
            parts.append(part)
    return parts


def export_entries(doc: PackDocument, indexes: list[int],
                   out_dir: Path) -> dict:
    """按真名目录树批量导出条目（导出选中/导出该页共用）。

    有真名的按原路径建子目录：精灵导成 ``<名>_fNN.png`` 逐帧图，
    其余按类型写原文件（真名带扩展名时尊重真名）；没真名的落
    ``unnamed/<包名>_<序号>``。同名冲突自动加序号后缀。单个条目
    失败不中断整批，结果以 {"entries", "files", "failed"} 汇报。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    pack_stem = Path(doc.path).stem if doc.path else "pack"
    used: set[Path] = set()
    files = 0
    done = 0
    failed: list[int] = []
    for index in indexes:
        try:
            kind = doc.entry_kind(index)
            content = doc.content(index)
            name = doc.true_name(index)
            if name and name.lower().endswith(".dlg"):
                plain = unpack_dlg_text(content)  # 布局导出明文
                if plain is not None:
                    content = plain
            parts = _safe_parts(name) if name else []
            if parts:
                parent = out_dir.joinpath(*parts[:-1])
                leaf = parts[-1]
            else:
                parent = out_dir / "unnamed"
                leaf = f"{pack_stem}_{index:04d}"
            parent.mkdir(parents=True, exist_ok=True)
            if kind is detect.EntryKind.SPRITE:
                stem = leaf.rsplit(".", 1)[0] if "." in leaf else leaf
                target = parent / f"{stem}_f00.png"
                if target in used:
                    stem = f"{stem}_{index:04d}"
                paths = export_sprite_frames(
                    decode_sprite(content), parent, stem)
                used.update(paths)
                files += len(paths)
            else:
                ext = _KIND_EXT.get(kind, ".bin")
                filename = leaf if "." in leaf else leaf + ext
                target = parent / filename
                if target in used:
                    target = parent / f"{target.stem}_{index:04d}{target.suffix}"
                target.write_bytes(content)
                used.add(target)
                files += 1
            done += 1
        except Exception:
            failed.append(index)
    return {"entries": done, "files": files, "failed": failed}
