"""资源解析：跨多个资源包/散装目录按路径取图片、布局与样式。

控件图片（``sFileName``）、包内 ``.dlg`` 与 ``ui.lst`` 都通过引擎
的路径哈希在 0SLF 包里寻址（见 :mod:`.pack`）。解析器可同时挂载
多个包与散装目录，按挂载顺序查找，找不到的图片由绘制层画占位
框，不影响布局编辑。包内 ``.dlg`` 为逐条目 4 字节 XOR 加密，
取用时按固定文件头反推密钥解开（密钥每条目不同、不可预知，
但文件头 ``# -*`` 已知足够恢复，见仓库结案记录）。
"""

from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtGui import QImage

from . import dlg_codec, sprite
from .catalog import known_layout_hashes, known_layout_paths
from .errors import DlgError
from .pack import FlsPack
from .styles import StyleBook

_KNOWN_HEADER = b"# -*- coding: gbk -*-"
_HEADER_PREFIX4 = b"# -*"

__all__ = ["AssetResolver", "unpack_packed_text"]


def _xor4(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i & 3] for i, b in enumerate(data))


def unpack_packed_text(data: bytes) -> bytes:
    """把包内文本还原为明文字节：明文直接返回，XOR 加密则解开。

    先按已知文件头反推 4 字节密钥；不成再用列频率法恢复（明文
    本身列频率得全零密钥）；都不成时原样返回，交给上层报错。
    """
    if data.startswith(_KNOWN_HEADER[:5]) or data[:1] == b"[":
        return data  # .dlg 明文或 ui.lst（INI）
    key = bytes(a ^ b for a, b in
                zip(data[:4], _HEADER_PREFIX4, strict=False))
    decoded = _xor4(data, key)
    if decoded.startswith(_KNOWN_HEADER):
        return decoded
    return _xor4(data, _recover_key_by_frequency(data))


def _recover_key_by_frequency(data: bytes) -> bytes:
    favourites = set(
        b" etaoinshrdlu=(){}_#'\"0123456789.,:[]\n\t<>")
    key = bytearray(4)
    for r in range(4):
        column = data[r::4][:2048]
        best_score, best = -1, 0
        for cand in range(256):
            score = sum(1 for b in column if (b ^ cand) in favourites)
            if score > best_score:
                best_score, best = score, cand
        key[r] = best
    return bytes(key)


class AssetResolver:
    """多包 + 散装目录的资源查找器（带缓存）。"""

    def __init__(self) -> None:
        self._packs: list[FlsPack] = []
        self._loose_dirs: list[Path] = []
        self._bytes_cache: dict[str, bytes | None] = {}
        self._image_cache: dict[str, list[QImage] | None] = {}

    # -- 挂载 -----------------------------------------------------
    def mount_pack(self, path: str | Path) -> FlsPack:
        pack = FlsPack(path)
        self._packs.append(pack)
        self._bytes_cache.clear()
        self._image_cache.clear()
        return pack

    def mount_dir(self, dirpath: str | Path) -> int:
        """挂载一个目录：其中的 *.fls 全部打开，目录本身作散装根。"""
        root = Path(dirpath)
        count = 0
        for fls in sorted(root.glob("*.fls")) + sorted(root.glob("*.FLS")):
            try:
                self.mount_pack(fls)
                count += 1
            except Exception:
                continue  # 非 0SLF 的包（如 data.fls）跳过
        self.add_loose_dir(root)
        return count

    def add_loose_dir(self, dirpath: str | Path) -> None:
        root = Path(dirpath)
        if root not in self._loose_dirs:
            self._loose_dirs.append(root)

    @property
    def pack_paths(self) -> list[Path]:
        return [pack.path for pack in self._packs]

    def pack_for(self, path: str | Path) -> FlsPack | None:
        """按路径取已挂载的包（未挂载返回 None）。"""
        target = str(path)
        for pack in self._packs:
            if str(pack.path) == target:
                return pack
        return None

    def scan_layouts(self, pack_path: str | Path) -> list[str]:
        """列出已挂载包里实际存在的已知布局路径（哈希相交，很快）。"""
        pack = self.pack_for(pack_path)
        if pack is None:
            return []
        return pack.matched_paths(known_layout_hashes())

    def missing_layouts(self, pack_path: str | Path) -> list[str]:
        """目录中被引用、但该包里没有的布局（死引用/热更新候选）。"""
        found = set(self.scan_layouts(pack_path))
        return [p for p in known_layout_paths() if p not in found]

    @property
    def summary(self) -> str:
        return f"已挂载 {len(self._packs)} 个资源包、{len(self._loose_dirs)} 个散装目录"

    # -- 查找 -----------------------------------------------------
    def fetch_bytes(self, name: str) -> bytes | None:
        """按资源路径取原始字节（包优先，其次散装目录）。"""
        if not name or not name.strip("\\/ "):
            return None
        cache_key = name.replace("/", "\\")
        if cache_key in self._bytes_cache:
            return self._bytes_cache[cache_key]
        data: bytes | None = None
        for pack in self._packs:
            try:
                data = pack.read_named(name)
            except Exception:
                data = None
            if data is not None:
                break
        if data is None:
            rel = Path(name.replace("\\", os.sep).replace("/", os.sep))
            for root in self._loose_dirs:
                candidate = root / rel
                if candidate.is_file():
                    data = candidate.read_bytes()
                    break
        self._bytes_cache[cache_key] = data
        return data

    def fetch_dlg(self, name: str) -> tuple[list[dict], str | None] | None:
        """按路径取包内 .dlg 并解密解析，失败返回 None。"""
        data = self.fetch_bytes(name)
        if data is None:
            return None
        try:
            return dlg_codec.parse_bytes(unpack_packed_text(data))
        except DlgError:
            return None

    def fetch_styles(self) -> StyleBook | None:
        """加载 ui.lst 样式表（包内或散装目录），失败返回 None。"""
        data = self.fetch_bytes("ui.lst")
        if data is None:
            return None
        try:
            return StyleBook.parse_bytes(data)
        except Exception:
            return None

    def fetch_image(self, name: str) -> list[QImage] | None:
        """按路径取图片帧：PNG/JPG 单帧，精灵多帧；失败返回 None。"""
        if not name or not name.strip("\\/ "):
            return None
        cache_key = name.replace("/", "\\")
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]
        frames = self._load_image(name)
        self._image_cache[cache_key] = frames
        return frames

    def _load_image(self, name: str) -> list[QImage] | None:
        data = self.fetch_bytes(name)
        if data is None:
            return None
        if data[:4] == b"\x89PNG" or data[:2] == b"\xff\xd8" \
                or data[:3] == b"GIF" or data[:2] == b"BM":
            image = QImage.fromData(data)
            return [image] if not image.isNull() else None
        if sprite.is_sprite(data):
            try:
                decoded = sprite.decode_sprite(data)
            except Exception:
                return None
            images = []
            for frame in decoded.frames:
                if frame.width <= 0 or frame.height <= 0:
                    continue
                image = QImage(frame.rgba, frame.width, frame.height,
                               frame.width * 4, QImage.Format.Format_RGBA8888)
                images.append(image.copy())
            return images or None
        return None

    def close(self) -> None:
        for pack in self._packs:
            pack.close()
        self._packs.clear()
