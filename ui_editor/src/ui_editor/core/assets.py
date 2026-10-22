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
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

from PySide6.QtCore import QRect
from PySide6.QtGui import QImage, QPainter

from . import animation, dir_base, dlg_codec, slicing, spr_desc, sprite
from .catalog import known_layout_hashes, known_layout_paths
from .errors import DlgError, ResourceIssue
from .pack import FlsPack
from .pack_build import unpack_packed_text  # noqa: F401  转发
from .styles import StyleBook

__all__ = ["AssetResolver", "SliceRecipe", "unpack_packed_text"]

_MEDIA_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".tga", ".gif",
               ".igs", ".spr", ".wav", ".mp3", ".ogg")


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
    """像媒体引用：带目录的文件名，或目录型基路径（结尾分隔符）。

    目录型基路径（``…\\登录按钮\\``）没有扩展名，但确实是控件引用的
    素材——客户端运行时在其下拼子图。少了这一支，拼名族永远进不了
    「从资源包选择」的候选清单。
    """
    if dir_base.is_dir_base(text):
        return True
    return (("\\" in text or "/" in text)
            and text.lower().endswith(_MEDIA_EXTS))


def _stitch_row(images: list[QImage]) -> QImage:
    """横拼：等高画布，逐块原尺寸、垂直居中（近似横框预览）。"""
    height = max(img.height() for img in images)
    width = sum(img.width() for img in images)
    out = QImage(width, height, QImage.Format.Format_RGBA8888)
    out.fill(0)
    painter = QPainter(out)
    try:
        x = 0
        for img in images:
            painter.drawImage(x, (height - img.height()) // 2, img)
            x += img.width()
    finally:
        painter.end()
    return out


def _stitch_column(images: list[QImage]) -> QImage:
    """竖拼：等宽画布，逐块原尺寸、水平居中（近似竖框预览）。"""
    width = max(img.width() for img in images)
    height = sum(img.height() for img in images)
    out = QImage(width, height, QImage.Format.Format_RGBA8888)
    out.fill(0)
    painter = QPainter(out)
    try:
        y = 0
        for img in images:
            painter.drawImage((width - img.width()) // 2, y, img)
            y += img.height()
    finally:
        painter.end()
    return out


def _stitch_grid(images: list[QImage], columns: int) -> QImage:
    """九片拼装：行列规整化，每块拉伸填满格（近似九宫格预览）。"""
    rows = len(images) // columns
    col_w = [
        max(images[r * columns + c].width() for r in range(rows))
        for c in range(columns)
    ]
    row_h = [
        max(images[r * columns + c].height() for c in range(columns))
        for r in range(rows)
    ]
    out = QImage(sum(col_w), sum(row_h), QImage.Format.Format_RGBA8888)
    out.fill(0)
    painter = QPainter(out)
    try:
        y = 0
        for r in range(rows):
            x = 0
            for c in range(columns):
                target = QRect(x, y, col_w[c], row_h[r])
                painter.drawImage(target, images[r * columns + c])
                x += col_w[c]
            y += row_h[r]
    finally:
        painter.end()
    return out


@dataclass(frozen=True)
class SliceRecipe:
    """一套可切片的资源：族名、各块（路径+像素）、哪些块全透明。

    ``kind`` 与 :mod:`ui_editor.core.dir_base` 同族（h_slice/v_slice/
    nine_slice）；切片尺寸直接来自这些文件的真实像素——这是切割线的
    唯一证据来源，不按控件尺寸反推。
    """

    kind: str
    names: tuple[str, ...]
    images: tuple[QImage, ...]
    blank: frozenset[int] = frozenset()

    def plan(self):
        """转成纯几何的 :class:`ui_editor.core.slicing.SlicePlan`。"""
        pieces = tuple(slicing.Piece(image.width(), image.height())
                       for image in self.images)
        if self.kind == "h_slice":
            return slicing.h_slice(*pieces)
        if self.kind == "v_slice":
            return slicing.v_slice(*pieces)
        return slicing.nine_slice(pieces)


def image_is_blank(image: QImage) -> bool:
    """整张图全透明？用于「透明切片不绘制」的判定。"""
    if image.isNull():
        return True
    alpha = image.convertToFormat(QImage.Format.Format_Alpha8)
    data = bytes(alpha.constBits())
    return not data or max(data) == 0


class AssetResolver:
    """多包 + 散装目录的资源查找器（带缓存）。"""

    def __init__(self) -> None:
        self.text_encoding = "big5"
        self._packs: list[FlsPack] = []
        self._loose_dirs: list[Path] = []
        self._bytes_cache: dict[str, bytes | None] = {}
        self._image_cache: dict[str, list[QImage] | None] = {}
        self._animation_cache: dict[str, animation.AnimationAsset | None] = {}
        self._slice_cache: dict[str, SliceRecipe | None] = {}
        self._media_cache: list[str] | None = None
        # 目录型基路径的拼名方案：选图窗一屏几百个族、每次刷新都要问
        # 一遍「这族拼得出来吗」，729 个族一次 0.4 s；缓存后是查字典。
        self._family_plans: dict[str, dir_base.DirBasePlan | None] = {}
        self._family_pieces: dict[str, tuple[str, ...]] = {}
        self._session_layouts: dict[int, str] = {}  # 用户明确给出的路径；仅本会话
        self._staged: dict[str, bytes] = {}  # 选图窗新加、待随包写入
        self._issues: list[ResourceIssue] = []

    # -- 挂载 -----------------------------------------------------
    def mount_pack(self, path: str | Path, *, priority: bool = False) -> FlsPack:
        normalized = Path(path).resolve()
        for index, existing in enumerate(self._packs):
            if existing.path.resolve() == normalized:
                if priority and index != 0:
                    self._packs.insert(0, self._packs.pop(index))
                return existing
        pack = FlsPack(normalized)
        if priority:
            self._packs.insert(0, pack)
        else:
            self._packs.append(pack)
        self._bytes_cache.clear()
        self._image_cache.clear()
        self._animation_cache.clear()
        self._slice_cache.clear()
        self._media_cache = None
        self._family_plans.clear()
        self._family_pieces.clear()
        return pack

    def mount_dir(self, dirpath: str | Path, *,
                  progress: Callable[[int, int, str], None] | None = None
                  ) -> int:
        """挂载一个目录：其中的 *.fls 全部打开，目录本身作散装根。

        ``progress(done, total, text)`` 回报逐包挂载进度（忙碌遮罩用）。
        """
        root = Path(dirpath)
        fls_files = sorted(root.glob("*.fls")) + sorted(root.glob("*.FLS"))
        count = 0
        total = max(len(fls_files), 1)
        for done, fls in enumerate(fls_files, 1):
            if progress is not None:
                progress(done - 1, total, f"挂载 {fls.name}（{done}/{total}）…")
            try:
                self.mount_pack(fls)
                count += 1
            except Exception as exc:
                self._record_issue("RESOURCE_PACK_CORRUPT", str(fls), str(exc))
                continue  # 非 0SLF 的包（如 data.fls）跳过
        if progress is not None:
            progress(total, total, "登记散文件目录…")
        self.add_loose_dir(root)
        return count

    def add_loose_dir(self, dirpath: str | Path) -> None:
        root = Path(dirpath).resolve()
        if root not in self._loose_dirs:
            self._loose_dirs.append(root)
            self._media_cache = None
            self._family_plans.clear()
            self._family_pieces.clear()
            self._animation_cache.clear()
            self._slice_cache.clear()

    @property
    def pack_paths(self) -> list[Path]:
        return [pack.path for pack in self._packs]

    @property
    def issues(self) -> tuple[ResourceIssue, ...]:
        """当前来源解析问题，供状态栏/诊断面板展示。"""
        return tuple(self._issues)

    def _record_issue(self, code: str, path: str, message: str) -> None:
        issue = ResourceIssue(code, path, message)
        if issue not in self._issues:
            self._issues.append(issue)

    def pack_for(self, path: str | Path) -> FlsPack | None:
        """按路径取已挂载的包（未挂载返回 None）。"""
        target = Path(path).resolve()
        for pack in self._packs:
            if pack.path.resolve() == target:
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
        self._family_plans.clear()
        self._family_pieces.clear()

    def fetch_pack_dlg_bytes(self, pack_path: str | Path, name: str) -> bytes:
        """从指定包取得解密后的布局字节，不转码、不重排字段。"""
        pack = self.pack_for(pack_path)
        data = None if pack is None else pack.read_named(name)
        if data is None:
            raise FileNotFoundError(f"包内找不到布局：{name}")
        return unpack_packed_text(data)

    def reloaded(self, resource_dirs=()) -> AssetResolver:
        """事务式重开来源，丢掉读取缓存，保留路径登记与待入包图片。"""
        fresh = AssetResolver()
        fresh.text_encoding = self.text_encoding
        fresh._session_layouts = dict(self._session_layouts)
        fresh._staged = dict(self._staged)
        try:
            for path in self.pack_paths:
                fresh.mount_pack(path)
            for root in self._loose_dirs:
                if not root.is_dir():
                    raise FileNotFoundError(f"来源目录不存在：{root}")
                fresh.add_loose_dir(root)
            for root in resource_dirs:
                for path in sorted(Path(root).iterdir()):
                    if path.suffix.lower() == ".fls" and fresh.pack_for(path) is None:
                        try:
                            fresh.mount_pack(path)
                        except Exception as exc:
                            fresh._record_issue(
                                "RESOURCE_PACK_CORRUPT", str(path), str(exc))
                            continue  # 与首次挂载一样跳过非 0SLF 格式
        except Exception:
            fresh.close()
            raise
        return fresh

    def fetch_pack_dlg(self, pack_path: str | Path, name: str):
        """锁定树节点对应的包；同名布局不从其它包/散装目录冒取。"""
        pack = self.pack_for(pack_path)
        if pack is None:
            return None
        data = pack.read_named(name)
        if data is None:
            return None
        try:
            return dlg_codec.parse_bytes(
                unpack_packed_text(data), text_encoding=self.text_encoding)
        except DlgError:
            return None

    def missing_layouts(self, pack_path: str | Path) -> list[str]:
        """目录中被引用、但该包里没有的布局（死引用/热更新候选）。"""
        found = set(self.scan_layouts(pack_path))
        return [p for p in known_layout_paths() if p not in found]

    @property
    def has_sources(self) -> bool:
        return bool(self._packs or self._loose_dirs)

    @staticmethod
    def _resource_name(name: str, *, allow_directory: bool = False) -> str:
        """校验并规范化包内/散装资源路径。"""
        if not isinstance(name, str):
            raise ValueError("资源路径必须是字符串")
        value = name.strip().replace("\\", "/")
        if not value or PureWindowsPath(value).drive \
                or PureWindowsPath(value).is_absolute() \
                or value.startswith("/"):
            raise ValueError(f"资源路径必须是包内相对路径：{name!r}")
        trailing = value.endswith("/")
        parts = value.split("/")
        if trailing:
            parts.pop()
        if (not parts or any(not part or part in (".", "..")
                             or any(ord(char) < 32 for char in part)
                             or any(char in '<>:\\"|?*' for char in part)
                             for part in parts)):
            raise ValueError(f"资源路径含非法段：{name!r}")
        if trailing and not allow_directory:
            raise ValueError(f"资源路径不能以目录分隔符结尾：{name!r}")
        normalized = "/".join(parts) + ("/" if trailing else "")
        try:
            normalized.encode("gbk")
        except UnicodeEncodeError as exc:
            raise ValueError(f"资源路径含 GBK 不可编码字符：{name!r}") from exc
        return normalized

    @staticmethod
    def _loose_candidate(root: Path, name: str) -> Path:
        root_resolved = root.resolve()
        candidate = (root / name.replace("/", os.sep)).resolve()
        try:
            candidate.relative_to(root_resolved)
        except ValueError as exc:
            raise ValueError(f"资源路径越出挂载目录：{name!r}") from exc
        return candidate

    def resource_exists(self, name: str) -> bool:
        """只查当前挂载来源与待入包图；不解码负载，供静态诊断使用。"""
        try:
            normalized = self._resource_name(name)
        except ValueError as exc:
            self._record_issue("RESOURCE_INVALID_PATH", str(name), str(exc))
            return False
        return (self._staged_lookup(normalized) is not None
                or self._exists(normalized))

    def _exists(self, name: str) -> bool:
        """资源是否真在某个包/散装目录里（只查索引与文件存在性）。"""
        try:
            normalized = self._resource_name(name)
        except ValueError as exc:
            self._record_issue("RESOURCE_INVALID_PATH", str(name), str(exc))
            return False
        for pack in self._packs:
            if pack.contains(normalized):
                return True
        for root in self._loose_dirs:
            try:
                if self._loose_candidate(root, normalized).is_file():
                    return True
            except ValueError as exc:
                self._record_issue("RESOURCE_INVALID_PATH", normalized,
                                   str(exc))
        return False

    # -- 待入包图片（选图窗"添加到包"挂账） ----------------------
    def stage_image(self, res_path: str, data: bytes) -> None:
        """登记一张新图：预览立即可见，保存回资源包时一并写入。"""
        try:
            res_path = self._resource_name(res_path)
        except ValueError as exc:
            self._record_issue("RESOURCE_INVALID_PATH", str(res_path), str(exc))
            raise
        self._staged[res_path] = data
        self._forget_piece_caches(res_path)

    def staged_images(self) -> dict[str, bytes]:
        """全部待入包图片 {资源路径: 原始字节}（拷贝）。"""
        return dict(self._staged)

    def discard_staged(self, res_paths) -> None:
        """写包成功后销账，避免下次保存重复写入。"""
        for path in res_paths:
            # 挂账时路径已规范化成 "/"；调用方传 "\\" 写法也要能销账。
            try:
                normalized = self._resource_name(path)
            except (TypeError, ValueError):
                normalized = path
            self._staged.pop(normalized, None)
            self._staged.pop(path, None)
            self._forget_piece_caches(path)

    def _forget_piece_caches(self, res_path: str) -> None:
        """挂账/销账后清掉这块图**以及它所在各层目录**的缓存。

        目录型基路径的合成图与切片是按**目录**缓存的。只清子图自己的键不够：
        同一个族重新挂账（换图）后，画布还会拿回旧的那张；销账后也会继续
        显示已经不存在的族。``_media_cache`` 不用清——挂账的图不在里面，
        候选清单每次都会把 ``staged_families()`` 现算进去，清它反而要重扫
        全部布局（几百个族约 0.5 s）。
        """
        key = str(res_path).replace("/", "\\")
        parts = key.split("\\")[:-1]
        parents = {"\\".join(parts[:depth]) + "\\"
                   for depth in range(1, len(parts) + 1)}
        self._bytes_cache.pop(key, None)
        for cache in (self._image_cache, self._slice_cache):
            for name in list(cache):
                # 切片键是「目录路径#态号」，按 # 前面比较。
                stem = name.split("#", 1)[0]
                if name == key or stem in parents:
                    cache.pop(name, None)
        # 挂账可能把半套族补成整族（也可能换掉某一块），拼名方案与
        # 子图清单都要按目录重算。
        for cache in (self._family_plans, self._family_pieces):
            for name in list(cache):
                if name in parents or name == key:
                    cache.pop(name, None)

    def _staged_lookup(self, name: str) -> bytes | None:
        for key in (name, name.replace("/", "\\"),
                    name.replace("\\", "/")):
            if key in self._staged:
                return self._staged[key]
        return None

    def media_candidates(
        self, progress: Callable[[int, int, str], None] | None = None
    ) -> list[str]:
        """包内可选媒体资源路径清单（供"从资源包选择"对话框）。

        0SLF 包不存文件名，能列出的名字来自已知布局：逐个解开
        已命名的 .dlg，把里面引用的图片/音频路径扒出来，再只留
        挂载的包/目录里真有的。首次构建需解开全部已命名布局
        （一次性，结果缓存；挂载变化自动失效）。完整客户端两千
        多条布局是重活：``progress(done, total, text)`` 回报进度。
        """
        if self._media_cache is not None:
            return self._media_cache
        found: set[str] = set()
        todo = []
        for pack in self._packs:
            layouts = pack.matched_paths(
                known_layout_hashes() | self._session_layouts)
            todo.extend((pack, layout) for layout in layouts)
        total = len(todo)
        # 两段合成一条 0→100 的进度。以前第一段报自己的 done/total，走完
        # 是 100%，第二段（核对 2,783 个名字、729 个族要逐块探）没有进度，
        # 进度条停在 100% 好一会儿——用户看到的就是「到 100% 卡住」。
        for done, (pack, layout) in enumerate(todo, 1):
            if progress is not None and (done == 1 or done == total
                                         or done % 16 == 0):
                share = int(done * 50 / total) if total else 0
                progress(share, 100,
                         f"整理包内资源清单 {done}/{total}（第 1 步：读布局）")
            data = pack.read_named(layout)
            if data is None:
                continue
            # 只做文本扫描（不完整解析布局），大包也够快
            text = unpack_packed_text(data).decode(
                "gb18030", "surrogateescape")
            found.update(_scan_media_in_text(text))
        # 第二段：核对这些名字在不在包里。目录型基路径要按拼名族逐块问
        # （729 个族约 0.4 s，Windows 机械盘上更久）。
        names = sorted(found)
        total = len(names)
        kept: list[str] = []
        for done, path in enumerate(names, 1):
            if progress is not None and total and (
                    done == total or done % 32 == 0):
                progress(50 + int(done * 50 / total), 100,
                         f"核对资源是否在包内 {done}/{total}"
                         "（第 2 步：查包内有没有）")
            if self._media_available(path):
                kept.append(path)
        if progress is not None:
            progress(100, 100, f"清单整理完成：{len(kept)} 个可用资源")
        self._media_cache = kept
        return self._media_cache

    def _media_available(self, path: str) -> bool:
        """候选能不能用：普通资源看条目在不在，目录型基路径看拼不拼得出整族。

        目录型基路径在包里**没有**这个条目（客户端运行时才拼），拿
        :meth:`_exists` 判会把它一律滤掉；这里改用与画布同一个
        :func:`dir_base.plan` 判「整族齐装」。
        """
        if not dir_base.is_dir_base(path):
            return self._exists(path)
        return self.family_plan(path) is not None

    def family_plan(self, name: str) -> dir_base.DirBasePlan | None:
        """目录型基路径的拼名方案（按路径缓存）。

        选图窗每开一次、每敲一个字、每挂账一张图都要重算一遍「这族拼得
        出来吗」。729 个族每次约 0.4 s；缓存后第二次打开是查字典。
        挂载/散装目录/挂账变化时由 :meth:`_forget_piece_caches` 与挂载
        路径一并清掉。
        """
        if not dir_base.is_dir_base(name):
            return None
        key = name.replace("/", "\\")
        if key in self._family_plans:
            return self._family_plans[key]
        try:
            plan = dir_base.plan(name, self.resource_exists)
        except ValueError:
            plan = None
        self._family_plans[key] = plan
        return plan

    def family_pieces(self, name: str) -> tuple[str, ...]:
        """这族里**实际有哪些子图**（完整路径；带缓存）。

        拼得成整族就按族给；拼不成则拿候选名逐个探——即使命名规则认
        不出来，也能把目录里真有的文件列给用户看。整族都没图返回空。
        """
        if not dir_base.is_dir_base(name):
            return ()
        key = name.replace("/", "\\")
        if key in self._family_pieces:
            return self._family_pieces[key]
        plan = self.family_plan(name)
        if plan is not None:
            pieces = plan.pieces
        else:
            try:
                pieces = tuple(name + rel
                               for rel in dir_base.probe_pieces(
                                   name, self.resource_exists))
            except ValueError:
                pieces = ()
        self._family_pieces[key] = pieces
        return pieces

    def staged_families(self) -> dict[str, list[str]]:
        """已挂账的图里能拼成**整族**的：``{目录型基路径: [子图路径…]}``。

        新建族是一次挂账多张子图（``…\\登录按钮\\0l.png`` …），布局里只
        引用目录路径；清单里列族本身而不是一堆子图，用户才看得懂。
        只看已挂账的图，且要整族齐装——半套不算族。
        """
        # 每级祖先目录都算候选：九片的子图挂在 面板/top/ 下，族基路径却是 面板/。
        candidates: set[str] = set()
        for path in self._staged:
            parts = path.replace("\\", "/").split("/")[:-1]
            for depth in range(1, len(parts) + 1):
                candidates.add("/".join(parts[:depth]))
        families: dict[str, list[str]] = {}
        claimed: set[str] = set()
        # 先浅后深：九片的 top/ 目录自己也能拼成横三片，必须让外层先认领。
        for parent in sorted(candidates, key=lambda item: item.count("/")):
            base = parent.replace("/", "\\") + "\\"

            def exists(name: str) -> bool:
                # plan 传进来的是拼好的**完整**子图路径，直接查挂账表。
                return self._staged_lookup(name) is not None

            chosen = dir_base.plan(base, exists)
            if chosen is None:
                continue
            members = {path for path in self._staged
                      if path.replace("\\", "/").startswith(parent + "/")}
            if members <= claimed:
                continue          # 已经被外层的族认领（九片的每一行）
            # 多出来的块（半套的第二态等）不算整族：折叠掉用户就看不到它们了。
            pieces = {piece.replace("\\", "/") for piece in chosen.pieces}
            if pieces != members:
                continue
            families[base] = sorted(members)
            claimed |= members
        return families

    def candidates_with_staged(
        self, progress: Callable[[int, int, str], None] | None = None
    ) -> list[str]:
        """选图窗清单：包内候选 + 已挂账的新图（新建的族只列目录路径）。"""
        families = self.staged_families()
        pieces = {piece for group in families.values() for piece in group}
        return sorted(
            set(self.media_candidates(progress)) | set(self._staged) - pieces
            | set(families))

    @property
    def summary(self) -> str:
        return f"已挂载 {len(self._packs)} 个资源包、{len(self._loose_dirs)} 个散装目录"

    # -- 查找 -----------------------------------------------------
    def fetch_bytes(self, name: str) -> bytes | None:
        """按资源路径取原始字节（待入包图片优先，其次包/散装目录）。"""
        try:
            normalized = self._resource_name(name)
        except ValueError as exc:
            self._record_issue("RESOURCE_INVALID_PATH", str(name), str(exc))
            raise
        staged = self._staged_lookup(normalized)
        if staged is not None:
            return staged
        cache_key = normalized.replace("/", "\\")
        if cache_key in self._bytes_cache:
            return self._bytes_cache[cache_key]
        data: bytes | None = None
        for pack in self._packs:
            try:
                data = pack.read_named(normalized)
            except Exception as exc:
                self._record_issue("RESOURCE_READ_ERROR", normalized, str(exc))
                raise
            if data is not None:
                break
        if data is None:
            for root in self._loose_dirs:
                try:
                    candidate = self._loose_candidate(root, normalized)
                except ValueError as exc:
                    self._record_issue("RESOURCE_INVALID_PATH", normalized,
                                       str(exc))
                    continue
                if candidate.is_file():
                    try:
                        data = candidate.read_bytes()
                    except OSError as exc:
                        self._record_issue("RESOURCE_READ_ERROR", normalized,
                                           str(exc))
                        raise
                    break
        self._bytes_cache[cache_key] = data
        return data

    def fetch_dlg(self, name: str) -> tuple[list[dict], str | None] | None:
        """按路径取包内 .dlg 并解密解析，失败返回 None。"""
        data = self.fetch_bytes(name)
        if data is None:
            return None
        try:
            return dlg_codec.parse_bytes(
                unpack_packed_text(data), text_encoding=self.text_encoding)
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

    def fetch_animation(self, name: str) -> animation.AnimationAsset | None:
        """读取 .spr 的帧号/时长和对应像素，保留非连续帧号。"""
        try:
            normalized = self._resource_name(name)
        except ValueError as exc:
            self._record_issue("RESOURCE_INVALID_PATH", str(name), str(exc))
            return None
        cache_key = normalized.replace("/", "\\")
        if cache_key in self._animation_cache:
            return self._animation_cache[cache_key]
        data = self.fetch_bytes(normalized)
        text = spr_desc.decode_spr_text(data) if data is not None else None
        if data is None or text is None:
            self._record_issue("RESOURCE_DECODE_ERROR", normalized,
                               ".spr 描述符无法解码")
            self._animation_cache[cache_key] = None
            return None
        table = spr_desc.parse_frame_table(text)
        images: list[QImage] | None = None
        package = ""
        branch = ""
        info = spr_desc.parse_images(text)
        if info:
            package = str(info.get("package", "") or "")
            branch = str(info.get("branch", "") or "")
        for candidate in spr_desc.frame_sources(normalized, text):
            sibling = self._fetch_sprite_source(candidate)
            if sibling is None:
                continue
            images = self._decode_frames(sibling)
            if images:
                break
        if images is None:
            self._record_issue("RESOURCE_MISSING", normalized,
                               "找不到 .spr 对应的精灵帧资源")
            self._animation_cache[cache_key] = None
            return None
        asset = animation.build_animation(
            normalized, table, images, package=package, branch=branch)
        self._animation_cache[cache_key] = asset
        if not asset.complete:
            self._record_issue("RESOURCE_FRAME_MISSING", normalized,
                               "帧表中有帧号没有对应像素")
        return asset

    def _fetch_sprite_source(self, name: str) -> bytes | None:
        """按 ``package:branch/path`` 解析 .spr 的外部包指针。"""
        if ":" not in name:
            return self.fetch_bytes(name)
        package, resource = name.split(":", 1)
        resource = resource.replace("\\", "/")
        for pack in self._packs:
            if pack.path.stem.casefold() == package.casefold():
                data = pack.read_named(resource)
                if data is not None:
                    return data
        self._record_issue("RESOURCE_PACKAGE_MISSING", name,
                           f"未挂载 .spr 指定资源包：{package}")
        return None

    def fetch_image(self, name: str) -> list[QImage] | None:
        """按路径取图片帧：PNG/JPG 单帧，精灵多帧；失败返回 None。"""
        try:
            normalized = self._resource_name(name, allow_directory=True)
        except ValueError as exc:
            self._record_issue("RESOURCE_INVALID_PATH", str(name), str(exc))
            return None
        cache_key = normalized.replace("/", "\\")
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]
        frames = self._load_image(normalized)
        self._image_cache[cache_key] = frames
        return frames

    def _load_image(self, name: str) -> list[QImage] | None:
        if dir_base.is_dir_base(name):
            return self._compose_dir_base(name)
        if name.lower().endswith(".spr"):
            return self._load_spr(name)
        data = self.fetch_bytes(name)
        frames = self._decode_frames(data) if data is not None else None
        if frames is not None:
            return frames
        if data is not None:
            self._record_issue("RESOURCE_DECODE_ERROR", name,
                               "资源字节不是可识别的图片或精灵格式")
        return None

    def _load_spr(self, name: str) -> list[QImage] | None:
        asset = self.fetch_animation(name)
        if asset is None:
            return None
        return [image for image in asset.images if image is not None]

    @staticmethod
    def _decode_frames(data: bytes) -> list[QImage] | None:
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

    def _piece_exists(self, name: str) -> bool:
        return self._staged_lookup(name) is not None or self._exists(name)

    def _compose_dir_base(self, name: str) -> list[QImage] | None:
        """目录型基路径：按拼名族合成预览帧（规则见 :mod:`.dir_base`）。

        序号帧族逐文件成帧（按钮态预览可用）；三态横片族每个状态拼一行
        成帧（帧号 = 状态号，按钮状态预览直接取帧）；横/竖/九片族拼成一
        张近似预览图。拼不出任何整族时返回 None，走原占位框。
        """
        chosen = dir_base.plan(name, self._piece_exists)
        if chosen is None:
            return None
        frames = [self._load_single_image(piece) for piece in chosen.pieces]
        if not frames or any(img is None for img in frames):
            return None
        images = [img for img in frames if img is not None]
        if chosen.kind in ("frames", "single"):
            return images
        if chosen.kind == "h_state":
            return [_stitch_row(images[index * 3:index * 3 + 3])
                    for index in range(chosen.states)]
        if chosen.kind == "h_slice":
            return [_stitch_row(images)]
        if chosen.kind == "v_slice":
            return [_stitch_column(images)]
        return [_stitch_grid(images, 3)]

    def fetch_slice(self, name: str) -> SliceRecipe | None:
        """目录型基路径的切片资源（三态横片/横三片/竖三片/九片）。

        三态横片返回**0 号态**的三块（常态），几何同样是横三片；其它状态
        由 :meth:`fetch_slice_state` 给出。序号帧族与单图族不属于切片
        （前者是多状态整图、后者是一张图），返回 None。
        """
        return self.fetch_slice_state(name, 0)

    def fetch_slice_state(self, name: str, index: int = 0) -> SliceRecipe | None:
        """某一按钮态的切片（帧号 = 态号，仅三态横片族有真态）。

        ``index`` 越界或该族没有真实态时返回 None——调用方据此决定是
        画常态再加模拟效果，还是直接画该态的真切片。
        """
        if not dir_base.is_dir_base(name):
            return None
        index = max(0, int(index))
        cache_key = name.replace("/", "\\") + (f"#{index}" if index else "")
        if cache_key in self._slice_cache:
            return self._slice_cache[cache_key]
        chosen = dir_base.plan(name, self._piece_exists)
        recipe: SliceRecipe | None = None
        if chosen is not None and chosen.kind in ("h_state", "h_slice",
                                                  "v_slice", "nine_slice"):
            if chosen.kind != "h_state" and index:
                pieces: tuple[str, ...] | None = None
            elif chosen.kind == "h_state" and index >= chosen.states:
                pieces = None
            else:
                pieces = chosen.state_pieces(index)
            images = ([self._load_single_image(piece) for piece in pieces]
                      if pieces is not None else [])
            if images and all(image is not None for image in images):
                kept = [image for image in images if image is not None]
                blank = frozenset(cell for cell, image in enumerate(kept)
                                  if image_is_blank(image))
                kind = "h_slice" if chosen.kind == "h_state" else chosen.kind
                recipe = SliceRecipe(kind, pieces, tuple(kept), blank)
        self._slice_cache[cache_key] = recipe
        return recipe

    def _load_single_image(self, name: str) -> QImage | None:
        frames = self._load_image(name)
        return frames[0] if frames else None

    def close(self) -> None:
        for pack in self._packs:
            pack.close()
        self._packs.clear()
