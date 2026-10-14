"""导出服务：把条目导出为 PNG（精灵逐帧/画布合成）或原始文件。"""
from __future__ import annotations

import io
from collections.abc import Iterable
from pathlib import Path

from PIL import Image

from ..codecs import detect, wav
from ..codecs.sprite import Sprite, decode_sprite
from ..model.document import PackDocument
from ..names import unpack_dlg_text
from ..output_paths import guard_output


def _source_paths(doc: PackDocument,
                  protected_paths: Iterable[str | Path]) -> list[Path]:
    """保护当前/历史基线及同目录资源包，GUI 可追加其他已打开包。"""
    sources = [*doc.source_paths, *(Path(p) for p in protected_paths)]
    for source in doc.source_paths:
        sources.extend(p for p in source.parent.iterdir()
                       if p.suffix.lower() == ".fls")
    return sources


def _write_bytes(path: Path, data: bytes, root: Path,
                 sources: Iterable[str | Path]) -> None:
    guard_output(path, sources, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    guard_output(path, sources, root)
    path.write_bytes(data)


def export_sprite_frames(sprite: Sprite, out_dir: Path, stem: str,
                         protected_paths: Iterable[str | Path] = (),
                         root: Path | None = None) -> list[Path]:
    """导出全部帧，写第一帧前先检查所有目标，禁止覆盖源资源。"""
    root = root if root is not None else out_dir
    sources = list(protected_paths)
    paths = [out_dir / f"{stem}_f{fi:02d}.png"
             for fi in range(sprite.frame_count)]
    for path in paths:
        guard_output(path, sources, root)
    out_dir.mkdir(parents=True, exist_ok=True)
    for fi, path in enumerate(paths):
        guard_output(path, sources, root)
        sprite.render_frame(fi).save(path)
    return paths


def _dlg_plain(content: bytes) -> bytes | None:
    """内容（无真名时）若为 XOR .dlg 布局，返回解出的明文。

    只认文件头反推后完整命中的明文（首行 ``# -*- coding:``），
    频率法兜底结果不作数，避免把普通二进制误判成布局导出。
    """
    plain = unpack_dlg_text(content)
    if plain is not None and plain.startswith(b"# -*- coding:"):
        return plain
    return None


def _is_wav(content: bytes) -> bool:
    """内容是否为 RIFF WAV（sound.fls 里整份存入的标准音频文件）。"""
    return wav.is_wav(content)


def export_entry(doc: PackDocument, index: int, out_dir: Path,
                 protected_paths: Iterable[str | Path] = ()) -> list[Path]:
    """按条目类型导出单个条目，返回生成的文件列表。

    精灵解码失败时回退导出原始字节 ``.bin``——原包自带、本机
    解码器未覆盖的精灵变体不该连原始数据都拿不出来（样本回传
    定点补解码器就靠这条路）。
    """
    sources = _source_paths(doc, protected_paths)
    out_dir.mkdir(parents=True, exist_ok=True)
    kind = doc.entry_kind(index)
    stem = f"{Path(doc.path).stem if doc.path else 'pack'}_{index:04d}"
    content = doc.content(index)
    plain = _dlg_plain(content)
    if plain is not None:
        path = out_dir / f"{stem}.dlg"
        _write_bytes(path, plain, out_dir, sources)
        return [path]
    if kind is detect.EntryKind.SPRITE:
        try:
            sprite = decode_sprite(content)
        except Exception:
            path = out_dir / f"{stem}.bin"
            _write_bytes(path, content, out_dir, sources)
            return [path]
        return export_sprite_frames(sprite, out_dir, stem, sources)
    if kind is detect.EntryKind.PNG:
        path = out_dir / f"{stem}.png"
        guard_output(path, sources, out_dir)
        Image.open(io.BytesIO(content)).save(path)
        return [path]
    ext = {detect.EntryKind.JSON: ".json", detect.EntryKind.TEXT: ".txt"}
    suffix = ".wav" if _is_wav(content) else ext.get(kind, ".bin")
    path = out_dir / f"{stem}{suffix}"
    _write_bytes(path, content, out_dir, sources)
    return [path]


def export_all_sprites(doc: PackDocument, out_dir: Path,
                       protected_paths: Iterable[str | Path] = ()) -> int:
    """导出包内全部精灵条目，返回导出的精灵个数。"""
    count = 0
    for index in range(doc.count):
        if doc.entry_kind(index) is detect.EntryKind.SPRITE:
            export_entry(doc, index, out_dir, protected_paths)
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
                   out_dir: Path,
                   protected_paths: Iterable[str | Path] = ()) -> dict:
    """按真名目录树批量导出条目（导出选中/导出该页共用）。

    有真名的按原路径建子目录：精灵导成 ``<名>_fNN.png`` 逐帧图，
    其余按类型写原文件（真名带扩展名时尊重真名）；没真名的落
    ``unnamed/<包名>_<序号>``。同名冲突自动加序号后缀。单个条目
    失败不中断整批，结果以 {"entries", "files", "failed"} 汇报。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    sources = _source_paths(doc, protected_paths)
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
            dlg_plain = None
            if name and name.lower().endswith(".dlg"):
                dlg_plain = unpack_dlg_text(content)  # 布局导出明文
            elif not name:
                # 无真名的条目也按内容认布局：路径字典没收录的
                # .dlg（新版布局等）存储字节同样是 XOR 文本
                dlg_plain = _dlg_plain(content)
            if dlg_plain is not None:
                content = dlg_plain
            parts = _safe_parts(name) if name else []
            if parts:
                parent = out_dir.joinpath(*parts[:-1])
                leaf = parts[-1]
            else:
                parent = out_dir / "unnamed"
                leaf = f"{pack_stem}_{index:04d}"
                if dlg_plain is not None:
                    leaf += ".dlg"
            guard_output(parent, sources, out_dir)
            if kind is detect.EntryKind.SPRITE and dlg_plain is None:
                stem = leaf.rsplit(".", 1)[0] if "." in leaf else leaf
                target = parent / f"{stem}_f00.png"
                if target in used:
                    stem = f"{stem}_{index:04d}"
                try:
                    sprite = decode_sprite(content)
                except Exception:
                    # 解不开的原始精灵回退原始字节，不整条丢失
                    target = parent / f"{stem}.bin"
                    if target in used:
                        target = parent / f"{stem}_{index:04d}.bin"
                    _write_bytes(target, content, out_dir, sources)
                    used.add(target)
                    files += 1
                else:
                    paths = export_sprite_frames(
                        sprite, parent, stem, sources, root=out_dir)
                    used.update(paths)
                    files += len(paths)
            else:
                ext = ".wav" if _is_wav(content) else _KIND_EXT.get(
                    kind, ".bin")
                filename = leaf if "." in leaf else leaf + ext
                target = parent / filename
                if target in used:
                    target = parent / f"{target.stem}_{index:04d}{target.suffix}"
                _write_bytes(target, content, out_dir, sources)
                used.add(target)
                files += 1
            done += 1
        except Exception:
            failed.append(index)
    return {"entries": done, "files": files, "failed": failed}
