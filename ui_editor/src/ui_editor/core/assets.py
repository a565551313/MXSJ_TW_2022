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
import re
from pathlib import Path

from PySide6.QtGui import QImage

from . import dlg_codec, sprite
from .catalog import known_layout_hashes, known_layout_paths
from .errors import DlgError
from .pack import FlsPack
from .pack_build import unpack_packed_text  # noqa: F401  转发
from .styles import StyleBook

__all__ = ["AssetResolver", "unpack_packed_text"]

_MEDIA_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".tga", ".gif",
               ".igs", ".wav", ".mp3", ".ogg")


_QUOTED_STR_RE = re.compile(r'"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\'')


def _scan_media_in_text(text: str) -> set[str]:
    """从 .dlg 明文里扒引号中的媒体路径（反斜杠先反转义回单写）。"""
    out: set[str] = set()
    for match in _QUOTED_STR_RE.finditer(text):
        value = match.group(1) if match.group(1) is not None \
            else match.group(2)
        value = value.replace("\\\\", "\\")
        if _looks_media(value):
            out.add(value)
    return out


def _looks_media(text: str) -> bool:
    return (("\\" in text or "/" in text)
            and text.lower().endswith(_MEDIA_EXTS))


class AssetResolver:
    """多包 + 散装目录的资源查找器（带缓存）。"""

    def __init__(self) -> None:
        self._packs: list[FlsPack] = []
        self._loose_dirs: list[Path] = []
        self._bytes_cache: dict[str, bytes | None] = {}
        self._image_cache: dict[str, list[QImage] | None] = {}
        self._media_cache: list[str] | None = None
        self._session_layouts: dict[int, str] = {}  # 用户明确给出的路径；仅本会话
        self._staged: dict[str, bytes] = {}  # 选图窗新加、待随包写入

    # -- 挂载 -----------------------------------------------------
    def mount_pack(self, path: str | Path, *, priority: bool = False) -> FlsPack:
        pack = FlsPack(path)
        if priority:
            self._packs.insert(0, pack)
        else:
            self._packs.append(pack)
        self._bytes_cache.clear()
        self._image_cache.clear()
        self._media_cache = None
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
            self._media_cache = None

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
        return pack.matched_paths(known_layout_hashes() | self._session_layouts)

    def remember_layout(self, name: str) -> None:
        """只登记用户提供的真实路径；重启不会反推 0SLF 无名条目。"""
        from .layout_import import validate_layout_path
        from .mxhash import mx_hash

        name = validate_layout_path(name)
        self._session_layouts[mx_hash(name.encode("gbk"))] = name
        self._media_cache = None

    def fetch_pack_dlg(self, pack_path: str | Path, name: str):
        """锁定树节点对应的包；同名布局不从其它包/散装目录冒取。"""
        pack = self.pack_for(pack_path)
        if pack is None:
            return None
        data = pack.read_named(name)
        if data is None:
            return None
        try:
            return dlg_codec.parse_bytes(unpack_packed_text(data))
        except DlgError:
            return None

    def missing_layouts(self, pack_path: str | Path) -> list[str]:
        """目录中被引用、但该包里没有的布局（死引用/热更新候选）。"""
        found = set(self.scan_layouts(pack_path))
        return [p for p in known_layout_paths() if p not in found]

    @property
    def has_sources(self) -> bool:
        return bool(self._packs or self._loose_dirs)

    def resource_exists(self, name: str) -> bool:
        """只查当前挂载来源与待入包图；不解码负载，供静态诊断使用。"""
        return self._staged_lookup(name) is not None or self._exists(name)

    def _exists(self, name: str) -> bool:
        """资源是否真在某个包/散装目录里（只查索引与文件存在性）。"""
        for pack in self._packs:
            if pack.contains(name):
                return True
        rel = Path(name.replace("\\", os.sep).replace("/", os.sep))
        return any((root / rel).is_file() for root in self._loose_dirs)

    # -- 待入包图片（选图窗"添加到包"挂账） ----------------------
    def stage_image(self, res_path: str, data: bytes) -> None:
        """登记一张新图：预览立即可见，保存回资源包时一并写入。"""
        self._staged[res_path] = data
        for key in (res_path, res_path.replace("/", "\\"),
                    res_path.replace("\\", "/")):
            cache_key = key.replace("/", "\\")
            self._bytes_cache.pop(cache_key, None)
            self._image_cache.pop(cache_key, None)

    def staged_images(self) -> dict[str, bytes]:
        """全部待入包图片 {资源路径: 原始字节}（拷贝）。"""
        return dict(self._staged)

    def discard_staged(self, res_paths) -> None:
        """写包成功后销账，避免下次保存重复写入。"""
        for path in res_paths:
            self._staged.pop(path, None)

    def _staged_lookup(self, name: str) -> bytes | None:
        for key in (name, name.replace("/", "\\"),
                    name.replace("\\", "/")):
            if key in self._staged:
                return self._staged[key]
        return None

    def media_candidates(self) -> list[str]:
        """包内可选媒体资源路径清单（供"从资源包选择"对话框）。

        0SLF 包不存文件名，能列出的名字来自已知布局：逐个解开
        已命名的 .dlg，把里面引用的图片/音频路径扒出来，再只留
        挂载的包/目录里真有的。首次构建需解开全部已命名布局
        （一次性，结果缓存；挂载变化自动失效）。
        """
        if self._media_cache is not None:
            return self._media_cache
        found: set[str] = set()
        for pack in self._packs:
            layouts = pack.matched_paths(known_layout_hashes() | self._session_layouts)
            for layout in layouts:
                data = pack.read_named(layout)
                if data is None:
                    continue
                # 只做文本扫描（不完整解析布局），大包也够快
                text = unpack_packed_text(data).decode(
                    "gb18030", "surrogateescape")
                found.update(_scan_media_in_text(text))
        self._media_cache = sorted(
            path for path in found if self._exists(path))
        return self._media_cache

    def candidates_with_staged(self) -> list[str]:
        """选图窗清单：包内候选 + 已挂账待入包的新图。"""
        return sorted(set(self.media_candidates()) | set(self._staged))

    @property
    def summary(self) -> str:
        return f"已挂载 {len(self._packs)} 个资源包、{len(self._loose_dirs)} 个散装目录"

    # -- 查找 -----------------------------------------------------
    def fetch_bytes(self, name: str) -> bytes | None:
        """按资源路径取原始字节（待入包图片优先，其次包/散装目录）。"""
        if not name or not name.strip("\\/ "):
            return None
        staged = self._staged_lookup(name)
        if staged is not None:
            return staged
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
