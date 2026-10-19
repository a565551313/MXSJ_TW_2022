"""识别资源真实格式，并按原样导出控件用到的素材（零 Qt）。

「什么格式就什么格式」：包里存的字节是什么格式，导出文件就是什么格式，
扩展名按**内容**判定而不是照抄资源路径——很多 `.png` 实际存的是游戏精灵
（I0/T0/I1/T1/T4/T5），也有 `.igs` 存真 PNG 的历史情况。

- 真图片/音频（PNG/JPEG/GIF/BMP/TGA/WAV/OGG/MP3）：用嗅探到的标准扩展名；
- 游戏精灵容器：沿用资源路径原来的扩展名（游戏就按这个名字加载它），
  拿不到可用扩展名时退回 ``.igs``；
- 认不出来：沿用原扩展名，字节原样写出，不假装转换。

`.spr` 不是图片而是 XOR 过的帧时表，控件实际显示的是它指名的帧图；
导出 `.spr` 时连带导出这些帧图源文件。
"""

from __future__ import annotations

from pathlib import Path

from .spr_desc import decode_spr_text, frame_sources
from .sprite_format import is_sprite

__all__ = [
    "asset_paths_of", "detect_extension", "is_audio_name",
    "export_targets", "export_raw_assets", "unique_target",
]

# 控件里可能指向素材的属性（顺序即导出顺序）
ASSET_KEYS = ("sFileName", "sBgFileName", "sBarFileName", "sSoundPath")


def asset_paths_of(widget) -> list[tuple[str, str]]:
    """控件引用的素材：[(属性名, 资源路径)]，去重保序。"""
    seen: set[str] = set()
    found: list[tuple[str, str]] = []
    for key in ASSET_KEYS:
        value = widget.props.get(key)
        if not isinstance(value, str) or not value.strip("\\/ "):
            continue
        normalised = value.replace("/", "\\")
        if normalised in seen:
            continue
        seen.add(normalised)
        found.append((key, value))
    return found


def _name_ext(name: str) -> str:
    """资源路径的扩展名（含点，小写）；没有则空串。"""
    base = name.replace("\\", "/").rstrip("/").split("/")[-1]
    dot = base.rfind(".")
    return base[dot:].lower() if dot > 0 else ""


def is_audio_name(name: str) -> bool:
    return _name_ext(name) in (".wav", ".mp3", ".ogg")


def detect_extension(data: bytes | None, name: str = "") -> str:
    """按内容判定扩展名；认不出时沿用资源路径的扩展名。"""
    original = _name_ext(name)
    if not data:
        return original
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"GIF8"):
        return ".gif"
    if data.startswith(b"BM"):
        return ".bmp"
    if data.startswith(b"RIFF") and data[8:12] == b"WAVE":
        return ".wav"
    if data.startswith(b"OggS"):
        return ".ogg"
    if data.startswith(b"ID3") or data[:2] in (b"\xff\xfb", b"\xff\xf3"):
        return ".mp3"
    if len(data) > 18 and data[-18:-2] == b"TRUEVISION-XFILE":
        return ".tga"
    if is_sprite(data):
        # 游戏精灵容器：保持资源路径原本的名字（.igs/.png…），游戏按此加载
        return original or ".igs"
    return original


def unique_target(dest_dir, filename: str) -> Path:
    """目标目录里重名时加 ``-2``、``-3``…，不覆盖已有文件。"""
    dest = Path(dest_dir)
    target = dest / filename
    if not target.exists():
        return target
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    index = 2
    while True:
        candidate = dest / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def _basename(name: str) -> str:
    base = name.replace("\\", "/").rstrip("/").split("/")[-1]
    return base or "asset"


def export_targets(assets, name: str) -> list[tuple[str, bytes]]:
    """一个资源路径要导出的全部文件：[(建议文件名, 原始字节)]。

    `.spr` 帧时表连带它指名的帧图源文件（同一个包里读得到才带）。
    """
    data = assets.fetch_bytes(name)
    if data is None:
        return []
    base = _basename(name)
    stem = base[:base.rfind(".")] if "." in base[1:] else base
    targets = [(f"{stem}{detect_extension(data, name)}", data)]
    if name.lower().endswith(".spr"):
        text = decode_spr_text(data) or ""
        for source in frame_sources(name, text):
            sibling = assets.fetch_bytes(source)
            if sibling is None:
                continue
            source_base = _basename(source)
            source_stem = (source_base[:source_base.rfind(".")]
                           if "." in source_base[1:] else source_base)
            targets.append((f"{source_stem}{detect_extension(sibling, source)}",
                            sibling))
    return targets


def export_raw_assets(assets, widget, dest_dir,
                      protected_paths=()) -> tuple[list[Path], list[str]]:
    """把控件用到的素材**按原格式**写到 dest_dir。

    返回 ``(写出的文件, 找不到的资源路径)``。文件名按内容判定扩展名，
    重名自动加序号；写入前走 ``guard_output`` 防覆盖源资源/符号链接。
    """
    from .output_paths import guard_output

    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    missing: list[str] = []
    sources = list(protected_paths)
    for _key, name in asset_paths_of(widget):
        targets = export_targets(assets, name)
        if not targets:
            missing.append(name)
            continue
        for filename, data in targets:
            out = unique_target(dest, filename)
            guard_output(out, sources, dest)
            out.write_bytes(data)
            written.append(out)
    return written, missing
