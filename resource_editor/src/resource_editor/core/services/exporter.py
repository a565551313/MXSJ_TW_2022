"""导出服务：把条目导出为 PNG（精灵逐帧/画布合成）或原始文件。"""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

from ..codecs import detect
from ..codecs.sprite import Sprite, decode_sprite
from ..model.document import PackDocument


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
