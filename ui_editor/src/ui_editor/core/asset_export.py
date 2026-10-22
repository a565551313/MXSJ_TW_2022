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

``sFileName`` 等以 ``\\``/``/`` 结尾的是**目录型基路径**（包里没有这个条目，
客户端运行时才拼出 ``0l.png``、``top/left.png`` 这些子图）：导出时按
:mod:`.dir_base` 的拼名族展开成**每块子图**，文件名保留族内相对路径
（``top-left.png``），否则九片的 ``top/left`` 与 ``bottom/left`` 会撞名。
拼不出整族时说明「拼不出子图族」，而不是让路径校验器抛出
「不能以目录分隔符结尾」——那句话对用户没有意义。
"""

from __future__ import annotations

from pathlib import Path

from . import dir_base
from .spr_desc import decode_spr_text, frame_sources
from .sprite_format import is_sprite

__all__ = [
    "asset_paths_of", "detect_extension", "is_audio_name",
    "dir_base_pieces", "dir_piece_name", "dir_piece_stem", "export_paths",
    "export_targets", "export_raw_assets", "family_prefixes", "source_key",
    "unique_target", "unexported_label",
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


def source_key(name: str) -> str:
    """资源路径的比较键：只统一分隔符与首尾空白，不折叠大小写。

    包内路径是否区分大小写由引擎决定，这里不做猜测；批量导出只把
    **完全同一个资源路径**当成重复，「同名不同目录」仍按两份素材导出。
    """
    return name.replace("/", "\\").strip()


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


def dir_base_pieces(assets, name: str) -> tuple[str, ...] | None:
    """目录型基路径拼出的子图路径；非目录型或拼不出整族返回 None。

    数据来源与画布/诊断同一个 :func:`dir_base.plan`：整族齐装才算命中，
    所以「拼不出」通常意味着缺块，而不是路径写错。
    """
    if not dir_base.is_dir_base(name):
        return None
    exists = getattr(assets, "resource_exists", None)
    if not callable(exists):
        return None
    try:
        chosen = dir_base.plan(name, exists)
    except ValueError:
        return None
    if chosen is None or not chosen.pieces:
        return None
    return chosen.pieces


def export_paths(assets, name: str) -> list[str]:
    """一条控件引用真正要导出的资源路径。

    目录型基路径展开成拼名族里的每一块子图；其余就是它自己。拼不出整族
    时返回空列表，调用方用 :func:`unexported_label` 说明原因。
    """
    if not dir_base.is_dir_base(name):
        return [name]
    return list(dir_base_pieces(assets, name) or ())


def dir_piece_stem(piece: str, base: str, prefix: str = "") -> str:
    """目录型子图的导出文件名主干（``…\\登录按钮\\0l.png`` → ``0l``）。

    取**族内相对路径**并用 ``-`` 连接：九片的 ``top/left`` 与 ``bottom/left``
    都叫 ``left.png``，只取 basename 会互相覆盖、加序号成 ``left-2.png``，
    看不出是哪一块。

    ``prefix`` 是批量导出时区分不同拼名族的前缀（见 :func:`family_prefixes`）：
    两个按钮族都产出 ``0l.png``，加前缀后是 ``登录按钮-0l.png`` /
    ``注册按钮-0l.png``，文件名自己说明是哪一族。
    """
    rel = piece[len(base):] if base and piece.startswith(base) else piece
    rel = rel.replace("\\", "/").strip("/")
    if not rel:
        return f"{prefix}{_basename(piece)}"
    head, _, tail = rel.rpartition("/")
    if "." in tail[1:]:
        tail = tail[:tail.rfind(".")]
    if not tail:
        return f"{prefix}{_basename(piece)}"
    stem = f"{head}-{tail}" if head else tail
    return f"{prefix}{stem}"


def dir_piece_name(piece: str, base: str, prefix: str = "") -> str:
    """目录型子图在「转成图片」导出时的文件名（保留原扩展名）。

    内容是真 PNG 时 ``export_image_files`` 直接用它；是精灵时按它取主干
    拼 ``-0/-1`` 帧名；解不出时也照这个名字原样写字节。
    """
    return f"{dir_piece_stem(piece, base, prefix)}{_name_ext(piece)}"


def family_prefixes(names) -> dict[str, str]:
    """批量导出里区分不同拼名族的文件名前缀（``{比较键: 前缀}``）。

    只有同一批出现**两个以上不同基路径**时才需要前缀；单族批次返回空字典，
    文件名保持 ``0l.png`` 原样。前缀取能把这些基路径彼此区分开的**最短尾部
    路径段**，用 ``-`` 连接并补尾缀：``…\\登录按钮\\`` → ``登录按钮-``；
    两个族恰好同名（都叫 ``登录按钮``）时自动退到上一级
    （``三态按钮-登录按钮-``），避免前缀自己也撞名。
    """
    bases: list[str] = []
    for name in names:
        key = source_key(name)
        if key not in bases:
            bases.append(key)
    if len(bases) < 2:
        return {}
    parts = {base: [seg for seg in base.split("\\") if seg] for base in bases}
    longest = max(len(segs) for segs in parts.values())
    for depth in range(1, longest + 1):
        tails = {base: "-".join(segs[-depth:]) for base, segs in parts.items()}
        if len(set(tails.values())) == len(bases):
            return {base: f"{tails[base]}-" for base in bases}
    # 整条路径都分不开（同一个基路径不会走到这里）：退回完整路径。
    return {base: base.replace("\\", "-").strip("-") + "-" for base in bases}


def unexported_label(assets, name: str) -> str:
    """没导出时的状态栏标签：目录型要说明是「拼不出族」而不是「找不到」。"""
    if dir_base.is_dir_base(name):
        return f"{name}（目录型基路径：包里拼不出整族子图）"
    return name


def _dir_base_targets(assets, name: str,
                      unavailable: list[str] | None = None,
                      prefix: str = "",
                      ) -> list[tuple[str, bytes, str]]:
    """目录型基路径：族内每块子图各一个导出目标（原字节、原语义文件名）。

    ``unavailable`` 传了就收集**读不出**的子图（取不到字节或被路径校验拒绝），
    让批量导出能在状态栏点名缺了哪一块，而不是把残族当成完整导出。
    """
    targets: list[tuple[str, bytes, str]] = []
    for piece in dir_base_pieces(assets, name) or ():
        try:
            data = assets.fetch_bytes(piece)
        except ValueError:
            if unavailable is not None:
                unavailable.append(piece)
            continue
        if data is None:
            if unavailable is not None:
                unavailable.append(piece)
            continue
        stem = dir_piece_stem(piece, name, prefix)
        targets.append((f"{stem}{detect_extension(data, piece)}", data, piece))
    return targets


def export_targets(assets, name: str,
                   unavailable: list[str] | None = None,
                   prefix: str = "",
                   ) -> list[tuple[str, bytes, str]]:
    """一个资源路径要导出的全部文件：[(建议文件名, 原始字节, 来源资源路径)]。

    `.spr` 帧时表连带它指名的帧图源文件（同一个包里读得到才带）。第三个
    元素是这份字节真正来自哪个资源路径，批量导出靠它做跨控件去重——
    两个 `.spr` 指向同一张帧图时只导一次。

    目录型基路径（结尾 ``\\``/``/``）展开成拼名族的每块子图：包里没有基路径
    这个条目，直接 ``fetch_bytes`` 会被路径校验拒绝。
    """
    if dir_base.is_dir_base(name):
        return _dir_base_targets(assets, name, unavailable, prefix)
    try:
        data = assets.fetch_bytes(name)
    except ValueError:
        # 0.11.0 起 resolver 对绝对路径/非法段/符号链接越界直接拒绝；
        # 导出不能因此中断整个批次，按「取不到」处理并在状态栏点名。
        return []
    if data is None:
        return []
    base = _basename(name)
    stem = base[:base.rfind(".")] if "." in base[1:] else base
    targets = [(f"{stem}{detect_extension(data, name)}", data, name)]
    if name.lower().endswith(".spr"):
        text = decode_spr_text(data) or ""
        for source in frame_sources(name, text):
            try:
                sibling = assets.fetch_bytes(source)
            except ValueError:
                continue
            if sibling is None:
                continue
            source_base = _basename(source)
            source_stem = (source_base[:source_base.rfind(".")]
                           if "." in source_base[1:] else source_base)
            targets.append((f"{source_stem}{detect_extension(sibling, source)}",
                            sibling, source))
    return targets


def export_raw_assets(assets, widget, dest_dir, protected_paths=(),
                      seen: set[str] | None = None,
                      rejected: list[tuple[str, str]] | None = None,
                      family_prefixes: dict[str, str] | None = None,
                      ) -> tuple[list[Path], list[str]]:
    """把控件用到的素材**按原格式**写到 dest_dir。

    返回 ``(写出的文件, 找不到的资源路径)``。文件名按内容判定扩展名，
    重名自动加序号；写入前走 ``guard_output`` 防覆盖源资源/符号链接。

    ``seen`` / ``rejected`` 供批量导出共用（一次导出多控件时必传）：

    * ``seen``  已导出的资源路径集合，同一个资源只导一次——多选里几个控件
      共用一张背景图，不会再产出 ``bg-2.png`` 这种副本；
    * ``rejected`` 收集被 ``guard_output`` 拒绝的目标，``(资源路径, 原因)``。
      传了就**跳过该目标继续导剩下的**而不是整批中止，并且抛出前已写出的
      文件仍然在返回值里；不传则维持旧行为直接抛。
    * ``family_prefixes`` 批量导出多个拼名族时的文件名前缀（见
      :func:`family_prefixes`）；同一族里的子图读不出时也会进 ``missing``，
      不把残族当成完整导出。
    """
    from .output_paths import guard_output

    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    missing: list[str] = []
    sources = list(protected_paths)
    prefixes = dict(family_prefixes or {})
    for _key, name in asset_paths_of(widget):
        if seen is not None and source_key(name) in seen:
            continue
        unreadable: list[str] = []
        targets = export_targets(assets, name, unreadable,
                                 prefixes.get(source_key(name), ""))
        if unreadable:
            missing.extend(f"{piece}（子图读取失败）" for piece in unreadable)
        if not targets:
            if seen is not None:
                seen.add(source_key(name))
            # 整族都读不出时逐块点过名了，不再笼统说「拼不出整族」。
            if not unreadable:
                missing.append(unexported_label(assets, name))
            continue
        if seen is not None:
            # .spr 连带导出的帧图可能是另一个控件已经导过的同一个资源。
            targets = [item for item in targets
                       if source_key(item[2]) not in seen]
            seen.update(source_key(item[2]) for item in targets)
            if not targets:
                continue
        for filename, data, source in targets:
            out = unique_target(dest, filename)
            try:
                guard_output(out, sources, dest)
                out.write_bytes(data)
            except (OSError, ValueError) as exc:
                if rejected is None:
                    raise
                # 记**真正被拒的那份来源**：`.spr` 连带帧图被拒时主资源
                # 其实已经写出去了，报 .spr 会让用户以为它没导出。
                rejected.append((source, str(exc)))
                continue
            written.append(out)
    return written, missing
