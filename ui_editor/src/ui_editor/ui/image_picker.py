"""从资源包选择媒体资源的对话框。

包内资源按引用路径列出（清单由 AssetResolver.media_candidates
从已命名布局扒取），支持子串搜索、缩略图懒加载（分批填充，
大包不卡死）、双击确认。选到的路径本来就在包里，布局保存
回资源包后游戏按路径哈希即可找到，不会丢图。对话框同时
保留"从外部文件…"入口，选外部图仍是旧行为（只填文件名，
图本身不进包）。
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QBuffer, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from ..core import dir_base
from ..core.errors import Cancelled
from .busy import BusyHostMixin, run_busy_or_plain

_ROLE_PATH = Qt.ItemDataRole.UserRole
_THUMB_BATCH = 24

#: 新建族可选的拼名类型（顺序即下拉框顺序）。
#: 每种都写明"一张图是按钮的多少"——用户最容易在这里选错：
#: 按钮横片的每张只是**三分之一**，整图多态要用序号帧。
_FAMILY_KINDS = (
    ("h_state", "按钮横片：每张只是按钮的 1/3（0l 左片、0c 中片、0r 右片拼成"
                "一个状态）"),
    ("frames", "序号帧：每张都是完整的按钮图，0 / 1 / 2… 就是第 1/2/3 个状态"),
    ("nine_slice", "九宫格边框：9 张，上/中/下 × 左/中/右"),
    ("h_slice", "横向三片边框：左 + 中（拉伸）+ 右"),
    ("v_slice", "纵向三片边框：上 + 中（拉伸）+ 下"),
    ("single", "单张图：整个目录就一张"),
)


#: 只表示"位置"的类型：左/中/右 这类名字既能当横三片的块，也能当按钮横片
#: 的左中右片——到底写哪个名字由控件决定。
_POSITION_KINDS = frozenset({"h_slice", "v_slice"})


def choose_family_kind(names, widget_type: str | None = None) -> str | None:
    """新建族时预选类型：**文件名的结构 > 位置的别名 > 控件默认 > 张数**。

    文件名已经说明结构时听文件名的——``0/1/2.png`` 是一张一整图（序号帧），
    ``0l/0c/0r.png`` 才是按钮横片。旧实现无条件按控件来，把"导出 3 张
    整图再导回来"变成了 0l/0c/0r，三张整图各取三分之一拼成一条——
    这正是用户报的"三张图拼在一起"。

    只有 ``left/middle/right`` 这种**位置词**才让控件作主：它们既能是
    横三片的块，也能是按钮的左中右片，游戏要哪套名字由控件决定。
    """
    items = [str(name) for name in names]
    if not items:
        return None
    stems = [Path(name).stem for name in items]
    matched = dir_base.match_kind(items)
    widget_kind = dir_base.WIDGET_KINDS.get(widget_type or "")
    default_kind = dir_base.WIDGET_DEFAULT_KINDS.get(widget_type or "")

    def usable(kind: str | None) -> bool:
        return kind is not None and dir_base.piece_names(
            kind, len(items)) is not None

    if usable(matched):
        if (matched in _POSITION_KINDS and usable(widget_kind)
                and dir_base.map_stems_to_pieces(stems, widget_kind)
                is not None):
            return widget_kind
        return matched
    # 名字认不出：按真包多数派（按钮多是一整张一态），再退到位置词选择。
    if usable(default_kind):
        return default_kind
    if usable(widget_kind):
        return widget_kind
    return dir_base.guess_kind(len(items), widget_type)


def _ancestor_dirs(res_path: str) -> list[str]:
    """资源路径的各级父目录（以分隔符结尾，``dir_base`` 的基路径写法）。

    ``a/b/c/0.png`` → ``["a\\", "a\\b\\", "a\\b\\c\\"]``（按原串分隔符）。
    """
    sep = "\\" if "\\" in res_path else "/"
    parts = res_path.replace("\\", "/").split("/")[:-1]
    return [sep.join(parts[:depth]) + sep for depth in range(1, len(parts) + 1)]


def _basename(path: str) -> str:
    return path.replace("\\", "/").rstrip("/").split("/")[-1]


def _natural_key(name: str):
    """按文件名自然排序：``2.png`` 排在 ``10.png`` 前面。"""
    parts = re.split(r"(\d+)", Path(name).name)
    return [(0, int(part)) if part.isdigit() else (1, part.lower())
            for part in parts]


def _stem(path: str) -> str:
    name = _basename(path)
    return name[:name.rfind(".")] if "." in name[1:] else name


def suggest_free_base(base: str, conflicts) -> str:
    """给一个不与包里已有条目相撞的族目录（``…\\登录按钮\\`` → ``…\\登录按钮_2\\``）。

    ``conflicts(candidate_base)`` 返回该目录下已存在的条目数；0 就算空闲。
    用来给「不想覆盖原按钮」的用户一键换个新目录。
    """
    base = base.strip().replace("/", "\\")
    if not base:
        return ""
    if not base.endswith("\\"):
        base += "\\"
    stem = base.rstrip("\\")
    for index in range(0, 51):
        candidate = base if index == 0 else f"{stem}_{index + 1}\\"
        if not conflicts(candidate):
            return candidate
    return base


def prepare_family_payloads(files: list[str]) -> tuple[dict[str, bytes], str]:
    """读取一族图片并统一扩展名：整组 ``.igs`` 原样，其余统一转 PNG。

    拼名族按"整组同扩展名"探测，混着写进包就拼不出来；普通图片统一转
    PNG 是因为游戏只认 ``.png``/``.igs``（jpg/bmp 原样写进去等于坏图）。
    真 PNG 字节原样保留，不重新编码。
    """
    paths = [Path(name) for name in files]
    igs = [path for path in paths if path.suffix.lower() == ".igs"]
    if igs and len(igs) != len(paths):
        raise ValueError(
            "不能把 .igs 和普通图片混成一族：整族要用同一种扩展名。")
    # 键用**调用方原样的字符串**：`_stage_family` 拿 QFileDialog 给的路径来取。
    # 用 `str(Path(name))` 会在 Windows 上把 `C:/x/0l.png` 变成 `C:\x\0l.png`，
    # 两边的键对不上就是 KeyError（新建族整条流程挂掉）。
    payloads: dict[str, bytes] = {}
    for name, path in zip(files, paths, strict=True):
        data = path.read_bytes()
        if path.suffix.lower() == ".igs" or data[:4] == b"\x89PNG":
            payloads[name] = data
            continue
        image = QImage(str(path))
        if image.isNull():
            raise ValueError(f"{path.name} 读不出图片（不是支持的图片格式）。")
        buffer = QBuffer()
        buffer.open(QBuffer.OpenModeFlag.WriteOnly)
        if not image.save(buffer, "PNG"):
            raise ValueError(f"{path.name} 转成 PNG 失败。")
        payloads[name] = bytes(buffer.data())
    return payloads, (".igs" if igs else ".png")


class FamilyImportDialog(QDialog):
    """把一组图变成"一个按钮/边框"：目录型基路径 + 族内拼名。

    文件名本身能对上族内命名时（例如刚导出的 ``0l/0c/0r``、``top-left`` …）
    按**名字**对应，与选择顺序无关；对不上才按顺序分配，界面上逐条列出来
    让用户能看出错位。
    """

    def __init__(self, parent, files: list[str], base: str, kind: str | None,
                 ext: str, exists=None):
        super().__init__(parent)
        self.setWindowTitle("新建拼名族（多张图 = 一个按钮/边框）")
        self.resize(700, 480)
        self._files = list(files)
        self.ext = ext
        self._exists = exists
        self._matched = dir_base.match_kind([Path(f).name for f in self._files])
        self.base_path = ""
        self.pairs: list[tuple[str, str]] = []
        self.order_rule = "name"      # name / alias / natural
        self._picture_key: tuple | None = None   # 预览缓存键

        self._base = QLineEdit(base, self)
        self._base.setPlaceholderText(
            "这一族的目录路径，结尾带斜杠，如 "
            "combdialog4\\新登陆界面\\三态按钮\\登录按钮\\")
        self._base.textChanged.connect(self._refresh)

        self._kind = QComboBox(self)
        for value, label in _FAMILY_KINDS:
            self._kind.addItem(label, value)
        if kind:
            index = self._kind.findData(kind)
            if index >= 0:
                self._kind.setCurrentIndex(index)
        self._kind.currentIndexChanged.connect(self._refresh)

        self._hint = QLabel(self)
        self._hint.setWordWrap(True)
        self._summary = QLabel(self)
        self._summary.setWordWrap(True)
        # 拼出来的样子：用户报"效果不对"就是因为只在保存后才能看见结果。
        self._pic_caption = QLabel(
            "按当前族类型拼出来是这样（左边那一小块就是预览）：", self)
        self._pic_caption.setWordWrap(True)
        self._pic = QLabel(self)
        self._pic.setMinimumHeight(96)
        self._pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pic.setStyleSheet(
            "background: #eceff3; border: 1px solid #c7ccd4; border-radius: 4px;")
        self._preview = QPlainTextEdit(self)
        self._preview.setReadOnly(True)
        self._preview.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._note = QLabel(self)
        self._note.setWordWrap(True)
        # 覆盖警示：目录已经是别的按钮的素材时，必须说清楚会替换什么。
        self._warning = QLabel(self)
        self._warning.setWordWrap(True)
        self._warning.setStyleSheet("color: #b3261e;")

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel, parent=self)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)
        self._free_btn = QPushButton("换个新目录（不覆盖）", self)
        self._free_btn.setToolTip(
            "自动挑一个包里还没用过的目录名，例如 登录按钮_2")
        self._free_btn.clicked.connect(self._use_free_base)
        self._buttons.addButton(
            self._free_btn, QDialogButtonBox.ButtonRole.ActionRole)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"选了 {len(self._files)} 张图：", self))
        layout.addWidget(self._hint)
        layout.addWidget(QLabel("族类型：", self))
        layout.addWidget(self._kind)
        layout.addWidget(self._summary)
        layout.addWidget(self._pic_caption)
        layout.addWidget(self._pic)
        layout.addWidget(QLabel(
            "这一族的目录路径：新按钮就写一个新目录名；"
            "写已有目录 = 替换那个按钮的图。", self))
        layout.addWidget(self._base)
        layout.addWidget(self._warning)
        layout.addWidget(QLabel("写进包的条目：", self))
        layout.addWidget(self._preview, 1)
        layout.addWidget(self._note)
        layout.addWidget(self._buttons)
        self._refresh()

    # ------------------------------------------------------------ 映射 ----
    def summary_text(self) -> str:
        """当前族类型 + 张数的白话说明（用户最容易在这里犯迷糊）。"""
        kind = self._kind.currentData()
        count = len(self._files)
        if kind == "h_state":
            if count % 3:
                return (f"{count} 张不是 3 的倍数：按钮横片是每 3 张拼成"
                        "一个状态，要按 3、6、9… 张来选。")
            states = count // 3
            if states == 1:
                return ("3 张 = 按钮的 1 个状态：每张只是按钮的三分之一"
                        "（0l 左片 + 0c 中片 + 0r 右片，中片会被拉伸）。\n"
                        "如果这 3 张各自都是一整个按钮（三个状态），"
                        "把族类型改成「序号帧」，不要用这个。")
            return (f"{count} 张 = {states} 个状态 × 每态三片：0 号是常态，"
                    "后面的序号是悬停/按下等（哪个序号对应哪种，未与客户端"
                    "核实）。\n每张只是按钮的三分之一——不是一张一整图。")
        if kind == "nine_slice":
            return ("9 张 = 上/中/下 × 左/中/右：四角不动，四条边和中心会被拉伸。"
                    if count == 9 else f"{count} 张：九宫格必须正好 9 张。")
        if kind in ("h_slice", "v_slice"):
            which = "左 + 中 + 右" if kind == "h_slice" else "上 + 中 + 下"
            return (f"3 张 = {which}：两边固定、中间那片拉伸填满。"
                    if count == 3 else f"{count} 张：这种边框必须正好 3 张。")
        if kind == "frames":
            return (f"{count} 张 = {count} 个状态（帧）：每张都是完整的按钮图，"
                    "按 0、1、2… 编号——0 是常态，1/2 是悬停/按下等"
                    "（哪个序号对应哪种，未与客户端核实）。\n"
                    "导出回来的 0.png/1.png/2.png 就是这种。")
        if kind == "single":
            return "1 张 = 整个目录只有这一张图。" if count == 1 else "单图只能 1 张。"
        return ""

    def _family_pairs(self) -> tuple[list[tuple[str, str]], str | None]:
        """[(族内相对名, 本地文件)] 与错误说明。"""
        kind = self._kind.currentData()
        names = dir_base.piece_names(kind, len(self._files))
        if names is None:
            return [], (f"{len(self._files)} 张图对不上这种族；"
                        "换个族类型，或调整要导入的图片数量。")
        if self._matched == kind:
            by_name = {_stem(path).replace("-", "/"): path
                       for path in self._files}
            if set(by_name) == set(names):
                self.order_rule = "name"
                return [(name, by_name[name]) for name in names], None
        # 自己起的名字（左/中/右、tl/左上、left/middle/right…）也认
        pieces = dir_base.map_stems_to_pieces(
            [_stem(path) for path in self._files], kind)
        if pieces is not None and set(pieces) == set(names):
            by_piece = dict(zip(pieces, self._files, strict=True))
            self.order_rule = "alias"
            return [(name, by_piece[name]) for name in names], None
        # 认不出：按文件名自然排序后依次对应（至少比"选择的先后"可预期）
        ordered = sorted(self._files, key=_natural_key)
        self.order_rule = "natural"
        return list(zip(names, ordered, strict=True)), None

    def _normalised_base(self) -> tuple[str, str | None]:
        value = self._base.text().strip().replace("/", "\\")
        if not value:
            return "", "先填这一族的目录路径。"
        if not value.endswith("\\"):
            if value.lower().endswith((".png", ".igs", ".jpg", ".bmp")):
                return "", "这是文件名，不是目录：请填到目录为止并补上结尾斜杠。"
            value += "\\"
        if not dir_base.is_dir_base(value):
            return "", "目录路径要相对包内，并用结尾斜杠表示这是一个目录。"
        return value, None

    @staticmethod
    def _montage(images: list[QImage], columns: int,
                 max_height: int = 110,
                 max_width: int = 480) -> QPixmap | None:
        """把若干张图按 ``columns`` 列排成一张预览（等比缩放，宽高都设上限）。

        只限高是不够的：三张 1000×40 的横片并排后会得到 3000 像素宽的
        pixmap，``QLabel`` 把它当最小宽度，对话框会被撑得比屏幕还宽。
        """
        if not images:
            return None
        tallest = max(image.height() for image in images) or 1
        widest = 0
        for start in range(0, len(images), columns):
            row = images[start:start + columns]
            widest = max(widest, sum(image.width() for image in row))
        scale = min(1.0, max_height / tallest,
                    max_width / widest if widest else 1.0)
        scaled = [image.scaled(
            max(1, int(image.width() * scale)),
            max(1, int(image.height() * scale)),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
            for image in images]
        rows = (len(scaled) + columns - 1) // columns
        width = max(sum(cell.width() for cell in scaled[row * columns:
                                                       (row + 1) * columns])
                    for row in range(rows))
        height = sum(max(cell.height() for cell in scaled[row * columns:
                                                          (row + 1) * columns])
                     for row in range(rows))
        canvas = QPixmap(max(1, width), max(1, height))
        canvas.fill(QColor(236, 239, 243))
        painter = QPainter(canvas)
        y = 0
        for row in range(rows):
            cells = scaled[row * columns:(row + 1) * columns]
            x = 0
            for cell in cells:
                painter.drawPixmap(x, y, QPixmap.fromImage(cell))
                x += cell.width()
            y += max(cell.height() for cell in cells)
        painter.end()
        return canvas

    def _update_picture(self, pairs, kind: str) -> None:
        """按当前族类型把选中的图拼一下，让用户**保存前**就看见结果。

        这是"效果不对"最直接的补救：按钮横片的 3 张是拼成一条，
        序号帧只显示第 0 帧——两者一眼就能分辨，不用等保存回包。

        结果按 ``(族类型, 文件清单)`` 缓存：改目录路径时 ``_refresh`` 每个
        按键都会重来一次，但图片没变，不必重新解码（多张大图时肉眼可见
        地卡）。缺图不能拼半张——九片少一块会让后面每格都错位。
        """
        key = (kind, tuple(path for _rel, path in pairs))
        if key == self._picture_key:
            return
        self._picture_key = key
        if not pairs:
            self._pic.clear()
            self._pic_caption.setText("")
            self._pic.setText("（图片数量与族类型对不上，无法预览）")
            return
        images: list[QImage] = []
        failed = 0
        for _rel, path in pairs:
            image = QImage(str(path))
            if image.isNull():
                failed += 1
                continue
            images.append(image)
        if failed:
            self._pic.clear()
            self._pic_caption.setText("")
            self._pic.setText(
                "（.igs 精灵没法在这里预览，保存后看画布）" if not images else
                "（这一族里有图片读不出来，没拼；保存后看画布）")
            return
        if kind == "frames":
            pixmap = self._montage(images[:1], 1)
            note = "序号帧：画布上显示第 0 帧（完整一张图）"
        elif kind == "h_state":
            pixmap = self._montage(images[:3], 3)
            note = "按钮横片：三片拼成一条（中间那片会被拉伸）"
        elif kind == "h_slice":
            pixmap = self._montage(images[:3], 3)
            note = "横三片：左 + 中 + 右拼成一条"
        elif kind == "v_slice":
            pixmap = self._montage(images[:3], 1)
            note = "竖三片：上 + 中 + 下竖着拼"
        elif kind == "nine_slice":
            pixmap = self._montage(images[:9], 3)
            note = "九片：3 × 3 拼起来"
        else:
            pixmap = self._montage(images[:1], 1)
            note = "单图"
        if pixmap is None:
            self._pic.clear()
            self._pic_caption.setText("")
            return
        self._pic.setPixmap(pixmap)
        self._pic_caption.setText(
            f"按当前族类型拼出来是这样（{note}）。对不上就换族类型：")

    def _existing_pieces(self, base: str, pairs) -> list[str]:
        """这个目录里已经有的同名子图（**不管扩展名**）。

        只看 ``self.ext`` 会漏掉另一种格式：目录里已经有一组 ``.igs`` 按钮、
        用户导入的却是 PNG，看起来"没有冲突"，保存后目录里同时有 ``.png``
        和 ``.igs``——而 ``dir_base`` 先试 ``.png``，原按钮的图就被顶掉了。
        「换个新目录」也得把这些目录算成占用，否则会"换"到一个并不空的目录。
        """
        if self._exists is None:
            return []
        found: list[str] = []
        for rel, _path in pairs:
            stem = base + rel.replace("/", "\\")
            if any(self._exists(stem + ext) for ext in dir_base.EXTS):
                found.append(rel)
        return found

    def _existing_family_plan(self, base: str):
        """这个目录里已经拼得成的一族（``dir_base.plan`` 的判定）。"""
        if self._exists is None or not base:
            return None
        try:
            return dir_base.plan(base, self._exists)
        except ValueError:
            return None

    def _shadowing_plan(self, base: str, pairs, ext: str):
        """写完这一族后仍会优先命中的**别的**族；没有就返回 None。

        ``dir_base.plan`` 按固定优先级取第一个齐装的族：往已有
        ``0l/0c/0r`` 的目录里再写 ``0/1/2.png``，保存后游戏仍按按钮横片
        拼——新图写进去了却没人用，画布和游戏都不会变。这里把「新写的
        几张」并进存在性判断，模拟保存后的 ``plan``：命中的不是这一族，
        就说明这次写入会被旧族盖住。
        """
        if self._exists is None or not base or not pairs:
            return None
        target = {base + rel.replace("/", "\\") + ext for rel, _path in pairs}

        def exists(name: str) -> bool:
            return name.replace("/", "\\") in target or bool(self._exists(name))

        try:
            chosen = dir_base.plan(base, exists)
        except ValueError:
            return None
        if chosen is None:
            return None
        same = {piece.replace("/", "\\") for piece in chosen.pieces} == target
        return None if same else chosen

    def _refresh(self) -> None:
        pairs, error = self._family_pairs()
        base, base_error = self._normalised_base()
        valid_base = bool(base) and not error and not base_error
        existing = (self._existing_pieces(base, pairs)
                    if valid_base else [])
        existing_plan = self._existing_family_plan(base) if valid_base else None
        shadowed = (self._shadowing_plan(base, pairs, self.ext)
                    if valid_base else None)
        self._summary.setText(self.summary_text())
        lines = []
        for rel, path in pairs:
            mark = "  （替换）" if rel in existing else ""
            lines.append(
                f"{rel.replace('/', chr(92))}{self.ext}   ←   "
                f"{Path(path).name}{mark}")
        self._preview.setPlainText("\n".join(lines))
        kind = self._kind.currentData()
        self._update_picture(pairs, kind)
        notes = []
        if error is None:
            if self.order_rule == "name":
                notes.append("文件名就是族内命名，按名字对应"
                             "（与选择顺序无关）。")
            elif self.order_rule == "alias":
                notes.append("按文件名认出左右/上下/中（中英都行），"
                             "按名字对应（与选择顺序无关）。")
            else:
                notes.append("文件名认不出左右/上下，已按文件名排序依次对应"
                             "（见下图；对不上就改个名或调顺序）。")
            notes.append(dir_base.naming_hint(kind, len(self._files)))
            if self._matched is not None and self._matched != kind:
                matched_label = dir_base.KIND_LABELS.get(
                    self._matched, self._matched)
                kind_label = dir_base.KIND_LABELS.get(kind, kind)
                notes.append(
                    f"注：文件名更像【{matched_label}】，但控件是"
                    f"【{kind_label}】，按后者写入；要改就在上面切换类型。")
        problem = error or base_error
        if problem:
            notes.append(problem)
        self._hint.setText("\n".join(notes))
        self._note.setText(f"族目录：{base or '（未填）'}" if base else "")
        warnings = []
        if existing:
            warnings.append(
                f"⚠ 这个目录里已经有 {len(existing)} 张同名图（{base}）。\n"
                "继续并保存回包会替换它们——原来那个按钮的图就变了。\n"
                "要做「新」按钮：换个没用过的目录名（点下面「换个新目录」），"
                "控件会自动指向新目录。")
        if shadowed is not None:
            warnings.append(
                f"⚠ 这个目录里已经有一族【{dir_base.describe(shadowed)}】，"
                "游戏的拼名规则会先按它来；\n"
                f"这次写的 {len(pairs)} 张不会生效。请点「换个新目录」，"
                "或先删掉旧那族多余的子图。")
        elif existing_plan is not None and pairs:
            target = {base + rel.replace("/", "\\") + self.ext
                      for rel, _path in pairs}
            same = ({piece.replace("/", "\\")
                     for piece in existing_plan.pieces} == target)
            if not same:
                warnings.append(
                    f"注意：这个目录里原有的【{dir_base.describe(existing_plan)}】"
                    "保存后不会再被用到（新族排在它前面）。")
        if warnings:
            self._warning.setText("\n".join(warnings))
            self._warning.show()
        else:
            self._warning.clear()
            self._warning.hide()
        ok = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok.setText(f"替换 {len(existing)} 张" if existing else "写入新族")
        self._free_btn.setVisible(
            (bool(existing) or shadowed is not None)
            and self._exists is not None)
        ok.setEnabled(not problem and shadowed is None)

    def _use_free_base(self) -> None:
        pairs, _error = self._family_pairs()
        base, _base_error = self._normalised_base()
        if not base or self._exists is None:
            return

        def conflicts(candidate: str) -> int:
            count = len(self._existing_pieces(candidate, pairs))
            if count:
                return count
            # 目录里已有一族（名字完全不同）也不算空闲：再写进去可能
            # 被旧族盖住，或把旧族顶掉。
            return 1 if self._existing_family_plan(candidate) else 0

        new_base = suggest_free_base(base, conflicts)
        if new_base and new_base != base:
            self._base.setText(new_base)
        else:
            self._base.setText(base)

    def accept(self) -> None:
        base, error = self._normalised_base()
        pairs, pair_error = self._family_pairs()
        if error or pair_error:
            self._refresh()
            return
        if self._shadowing_plan(base, pairs, self.ext) is not None:
            # 旧族优先级更高，写进去也不会生效；红字已说明原因。
            self._refresh()
            self._base.setFocus()
            return
        self.base_path = base
        self.pairs = pairs
        super().accept()


class ResourcePickerDialog(BusyHostMixin, QDialog):
    """包内资源选择窗：搜索过滤 + 网格缩略图 + 单选确认。"""

    def __init__(self, parent, title: str, paths: list[str],
                 current: str = "",
                 thumb_provider: Callable[[str], object] | None = None,
                 on_stage: Callable[[str, bytes], None] | None = None,
                 export_handler: Callable[[list[str], object], None] | None = None,
                 family_label: Callable[[str], str | None] | None = None,
                 widget_type: str | None = None,
                 exists: Callable[[str], bool] | None = None,
                 family_pieces: Callable[[str], list[str] | None] | None = None,
                 family_kind: Callable[[str], str | None] | None = None,
                 browse_only: bool = False,
                 save_staged: Callable[[], bool] | None = None,
                 staged_count: Callable[[], int] | None = None,
                 fetch_bytes: Callable[[str], bytes | None] | None = None):
        super().__init__(parent)
        # 浏览模式（工具栏「资源」按钮）：没有目标属性，确定＝关闭，
        # 双击条目也只关闭，不写任何东西；导出/放进包/拼名族照旧。
        self._browse_only = browse_only
        # 浏览窗「保存新资源（N）」按钮（0.18.0）：宿主写包回调 +
        # 挂账计数回调（写的是**全部**挂账，不只本窗挂的）。
        self._save_staged_handler = save_staged
        self._staged_count_provider = staged_count
        self._save_staged_btn: QPushButton | None = None
        self.setWindowTitle(title)
        self.resize(760, 540)
        self.external_requested = False
        self._thumb_provider = thumb_provider
        self._on_stage = on_stage
        self._export_handler = export_handler
        # 目录型基路径（拼名族）的一句话说明：回调返回 None 表示不是族。
        self._family_label = family_label
        # 这个目录里到底有哪些子图（悬停提示用）：回调返回 None 表示不是族。
        self._family_pieces = family_pieces
        # 这个目录按哪种方式拼（按钮横片/序号帧…），给选中后的说明用。
        self._family_kind = family_kind
        self._widget_type = widget_type      # 新建族时按控件类型预选族类型
        self._exists = exists                # 判断包里是否已有同名条目
        # 浏览窗「批量处理…」取包内字节用（0.20.0）；没给回调不出按钮。
        self._fetch_bytes = fetch_bytes
        self._staged_paths: set[str] = set()
        # 族标签要探文件系统（plan 会逐个查子图在不在）。搜索框每敲一个字
        # 都会走一遍 _refilter，几百个族时就是几百毫秒的卡顿；标签在对话框
        # 生命周期内不会变，缓存起来，挂账新图（可能补全一个族）时清空。
        self._family_notes: dict[str, str | None] = {}
        all_paths = list(paths)
        if current and current not in all_paths:
            all_paths.insert(0, current)  # 当前值不在清单也置顶可见
        self._all_paths = all_paths

        self._search = QLineEdit(self)
        self._search.setPlaceholderText("输入关键字过滤，如 底板800")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._refilter)
        self._only_families = QCheckBox("只看拼名族", self)
        self._only_families.setToolTip(
            "目录型基路径（按钮 0/1/2 或 0l/0c/0r、边框 left/middle/right、"
            "九宫格 top/left …）：包里没有这个条目，游戏运行时在其下拼子图。\n"
            "选中它会把这个目录路径写进属性。")
        self._only_families.toggled.connect(self._refilter)
        self._only_families.setVisible(
            any(dir_base.is_dir_base(path) for path in all_paths))
        self._count = QLabel(self)
        # 选中一个目录型基路径时，直接说清"里面是什么、游戏怎么用"。
        self._detail = QLabel(self)
        self._detail.setWordWrap(True)
        self._detail.setTextFormat(Qt.TextFormat.PlainText)
        self._detail.setStyleSheet(
            "background: #f4f6f8; border: 1px solid #ccd2da; "
            "border-radius: 4px; padding: 6px;")
        self._detail.hide()

        self._list = QListWidget(self)
        self._list.setViewMode(QListWidget.ViewMode.IconMode)
        self._list.setIconSize(QSize(72, 72))
        self._list.setGridSize(QSize(110, 118))
        self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._list.setMovement(QListWidget.Movement.Static)
        self._list.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection)
        self._list.itemDoubleClicked.connect(lambda _i: self.accept())
        self._list.currentItemChanged.connect(
            lambda current, _prev: self._show_detail(
                str(current.data(_ROLE_PATH)) if current is not None else ""))

        self._thumb_timer = QTimer(self)
        self._thumb_timer.setInterval(30)
        self._thumb_timer.timeout.connect(self._fill_thumbs)
        # 只给**当前看得到的那几行**解缩略图：真包 2,758 条全解一遍
        # 要 14 秒，窗口看着就像死了。滚到哪补到哪。
        self._thumb_done: set[str] = set()
        self._blank_icon = QIcon(QPixmap(72, 72))
        self._family_total = 0
        self._list.verticalScrollBar().valueChanged.connect(
            self._schedule_thumbs)
        self._list.horizontalScrollBar().valueChanged.connect(
            self._schedule_thumbs)

        if browse_only:
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Close, parent=self)
            buttons.clicked.connect(self.accept)
        else:
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok
                | QDialogButtonBox.StandardButton.Cancel, parent=self)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)

        bottom = QHBoxLayout()
        if self._export_handler is not None:
            export_btn = QPushButton("导出副本…", self)
            export_btn.setToolTip(
                "把选中图片存到电脑上（可 Ctrl/Shift 多选批量导出；"
                "精灵格式会转成能打开看的 PNG）")
            export_btn.clicked.connect(self._choose_export)
            bottom.addWidget(export_btn)
        if self._on_stage is not None:
            add_btn = QPushButton("把图片放进包…", self)
            add_btn.setToolTip(
                "从电脑选图片、给它写游戏里的名字；选完能直接用，"
                "保存回资源包时连图一起写进包")
            add_btn.clicked.connect(self._choose_add)
            bottom.addWidget(add_btn)
            family_btn = QPushButton("几张图组成按钮（拼名族）…", self)
            family_btn.setToolTip(
                "把几张图合成一个按钮/边框：3 张 = 一个按钮（0l/0c/0r），"
                "6 张 = 两个状态，9 张 = 九宫格。\n"
                "图片按族内命名写进包（保存回包时一并写入），"
                "属性直接填成这一族的目录路径")
            family_btn.clicked.connect(self._choose_family)
            bottom.addWidget(family_btn)
            if self._browse_only and self._save_staged_handler is not None:
                self._save_staged_btn = QPushButton("", self)
                self._save_staged_btn.setToolTip(
                    "把全部挂账新资源写进资源包（目标跟随保存模式："
                    "严格=编辑器输出包，宽松=原包），\n"
                    "不改动任何布局条目；校验通过后才原子替换并清挂账，"
                    "失败时目标包一个字节不动。")
                self._save_staged_btn.clicked.connect(
                    self._save_staged_clicked)
                bottom.addWidget(self._save_staged_btn)
                self._refresh_save_staged_btn()
        elif not self._browse_only:
            # 浏览模式没有目标属性，「只填包外文件名」是写属性路径的
            # 入口，不露面。
            external_btn = QPushButton("只填包外文件名…", self)
            external_btn.setToolTip(
                "不改包：只把文件名填进属性，图片本身不会写进资源包。\n"
                "想连图一起写进包，请用「把图片放进包」")
            external_btn.clicked.connect(self._choose_external)
            bottom.addWidget(external_btn)
        if self._browse_only and self._fetch_bytes is not None:
            batch_btn = QPushButton("批量处理…", self)
            batch_btn.setToolTip(
                "把选中的图片整批调整：缩放、亮度、饱和度（Pillow）。\n"
                "结果写到磁盘目录（永不覆盖现有文件），或挂账成资源\n"
                "（同名＝保存时替换包内原资源）。.igs 自动逐帧解码调整\n"
                "再重编码；处理前有首图前后对比预览和输出清单确认。")
            batch_btn.clicked.connect(self._batch_process)
            bottom.addWidget(batch_btn)
        bottom.addStretch(1)
        bottom.addWidget(buttons)

        layout = QVBoxLayout(self)
        layout.addWidget(self._search)
        layout.addWidget(self._only_families)
        layout.addWidget(self._count)
        layout.addWidget(self._list, 1)
        layout.addWidget(self._detail)
        layout.addLayout(bottom)

        self._refilter()
        if current:
            for row in range(self._list.count()):
                item = self._list.item(row)
                if item.data(_ROLE_PATH) == current:
                    self._list.setCurrentItem(item)
                    break

    # ---------------------------------------------------------- 结果 ----
    def selected_path(self) -> str | None:
        item = self._list.currentItem()
        return str(item.data(_ROLE_PATH)) if item is not None else None

    def _choose_external(self) -> None:
        self.external_requested = True
        self.reject()

    def chosen_paths(self) -> list[str]:
        """导出目标：多选中的条目（没有多选时退回当前条目）。"""
        selected = [item.data(_ROLE_PATH)
                    for item in self._list.selectedItems()]
        if selected:
            return [path for path in selected if path]
        current = self.selected_path()
        return [current] if current else []

    def _choose_export(self) -> None:
        if self._export_handler is None:
            return
        paths = self.chosen_paths()
        if paths:
            # 第二参数 = 忙碌遮罩宿主（本对话框），批量导出在遮罩后跑。
            self._export_handler(paths, self)

    def add_staged_path(self, res_path: str) -> None:
        """把一张刚加进来的新图并入列表并选中它。

        不再整张列表重建：真包 2,758 行重建一次要 0.2 s 以上，新建一族
        只多一行图，没必要把整张表推倒。只插这一行，顺手刷新它的各级
        父目录行（新图可能把半套族补成整族，父行标签要跟着变）。
        """
        self._family_notes.clear()   # 新图可能把半套族补成整族
        self._staged_paths.add(res_path)
        if res_path not in self._all_paths:
            self._all_paths.insert(0, res_path)
        if self._search.text().strip():
            self._search.setText("")   # 触发 _refilter（新行已在 _all_paths 里）
        else:
            if self._row_of(res_path) < 0:
                item, _note = self._make_item(res_path)
                self._list.insertItem(0, item)
            else:
                self._refresh_row(res_path)
            for parent in _ancestor_dirs(res_path):
                self._refresh_row(parent)
            self._update_count()
        self._select_path(res_path)
        self._schedule_thumbs()
        self._refresh_save_staged_btn()

    def _row_of(self, path: str) -> int:
        for row in range(self._list.count()):
            item = self._list.item(row)
            if item is not None and item.data(_ROLE_PATH) == path:
                return row
        return -1

    def _select_path(self, path: str) -> None:
        row = self._row_of(path)
        if row >= 0:
            self._list.setCurrentItem(self._list.item(row))

    def _refresh_row(self, path: str) -> None:
        """就地刷新一行（标签/提示变了，不重建整张表）。

        路径本身可能换了内容（替换包里已有同名图、重挂同一族），所以缩略图
        也要作废重解：``_thumb_done`` 里还留着它的话，``_fill_thumbs`` 会
        跳过，列表一直显示旧图，直到下次过滤。
        """
        row = self._row_of(path)
        if row < 0:
            return
        item = self._list.item(row)
        fresh, _note = self._make_item(path)
        if item is None:
            return
        item.setText(fresh.text())
        item.setToolTip(fresh.toolTip())
        self._thumb_done.discard(path)
        item.setIcon(self._blank_icon)
        self._schedule_thumbs()

    def _update_count(self) -> None:
        families = sum(1 for row in range(self._list.count())
                       if self._list.item(row) is not None
                       and self._family_note(
                           str(self._list.item(row).data(_ROLE_PATH))))
        self._family_total = families
        note = f"，含 {families} 个拼名族" if families else ""
        self._count.setText(
            f"共 {self._list.count()} 个资源{note}"
            "（包内已有，选完保存回包不丢图）")

    def _refresh_save_staged_btn(self) -> None:
        """「保存新资源（N）」：N = 全部挂账数；没有挂账就禁用（0.18.0）。"""
        if self._save_staged_btn is None:
            return
        count = (self._staged_count_provider()
                 if self._staged_count_provider is not None
                 else len(self._staged_paths))
        self._save_staged_btn.setText(f"保存新资源（{count}）")
        self._save_staged_btn.setEnabled(count > 0)

    def _save_staged_clicked(self) -> None:
        """宿主负责写包；成功后清掉挂账标记并刷新列表与按钮。"""
        if self._save_staged_handler is None:
            return
        # 宿主 run_busy 会转嵌套事件循环，其输入屏障只罩主窗口：本窗
        # 必须自己禁用，否则第二次点击会让两次写包赛跑同一个目标包，
        # 写途中改挂账也会被旧快照销账（PR #89 审查复核属实项）。
        self.setEnabled(False)
        try:
            ok = bool(self._save_staged_handler())
        finally:
            self.setEnabled(True)
        if ok:
            # 挂账已进包：列表里的「待入包」标记该摘了，整表重过滤一遍。
            self._staged_paths.clear()
            self._refilter()
            self._schedule_thumbs()
        self._refresh_save_staged_btn()

    def _suggested_path(self, filename: str) -> str:
        """新名字的建议值：沿用当前选中项的目录 + 新文件名。"""
        current = self.selected_path()
        if current:
            sep = "\\" if "\\" in current else "/"
            parts = current.replace("\\", "/").split("/")
            if len(parts) > 1:
                return sep.join(parts[:-1]) + sep + filename
        return filename

    def _ask_new_image(self, default_path: str, multi: bool,
                       can_convert: bool) -> tuple[str, bool] | None:
        """问新图的名字与是否转精灵，返回 (资源路径, 转精灵)。"""
        dialog = QDialog(self)
        dialog.setWindowTitle("这张图在游戏里的名字")
        path_edit = QLineEdit(default_path, dialog)
        convert_box = QCheckBox(
            "转成游戏精灵格式（多张图 = 多帧动画，按文件名顺序成帧）",
            dialog)
        convert_box.setChecked(multi)
        convert_box.setEnabled(can_convert)
        note = QLabel(
            "游戏靠这个名字找图，如 combdialog4\\新登陆界面\\我的图.png。\n"
            "不转精灵则按原文件存（适合本来就是真 PNG 的图）。", dialog)
        note.setWordWrap(True)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("资源路径：", dialog))
        layout.addWidget(path_edit)
        layout.addWidget(convert_box)
        layout.addWidget(note)
        layout.addWidget(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        res_path = path_edit.text().strip()
        if not res_path:
            return None
        return res_path, convert_box.isChecked()

    def _stage_one(self, res_path: str, data: bytes, *,
                   confirm_same_name: bool = True) -> bool:
        """登记一张新图（包里已有同名时先确认会在保存时替换）。

        返回是否**真的挂上了**：无回调、用户取消同名替换、名字被资源层
        拒绝都返回 False——多张 .igs 的「已挂账 N 个」要按真值计数
        （PR #89 审查复核属实项）。批量处理（0.20.0）传
        ``confirm_same_name=False``：同名替换已在批处理窗的输出清单里
        一次性确认过，执行时不再逐张打断。
        """
        if self._on_stage is None:
            return False
        if (confirm_same_name and res_path in self._all_paths
                and res_path not in self._staged_paths):
            answer = QMessageBox.question(
                self, "这个名字已在包里",
                f"{res_path} 包里已经有了。\n"
                "继续的话，保存回资源包时会用新图替换它，确定吗？")
            if answer != QMessageBox.StandardButton.Yes:
                return False
        try:
            self._on_stage(res_path, data)
        except ValueError as exc:
            # 0.11.0 起资源层直接拒绝绝对路径/`..`/GBK 不可编码等名字；
            # 必须在这里说出来，否则用户只看到「点确定没反应」。
            QMessageBox.warning(
                self, "这个名字不能用",
                f"{res_path}\n\n{exc}\n\n"
                "请换一个只用中文、英文、数字、下划线的包内相对路径。")
            return False
        self.add_staged_path(res_path)
        return True

    def _suggested_family_path(self) -> str:
        """族目录的建议值：已选中族就沿用，否则用当前条目所在目录。"""
        current = self.selected_path()
        if not current:
            return ""
        if dir_base.is_dir_base(current):
            return current.replace("/", "\\")
        parts = current.replace("\\", "/").split("/")[:-1]
        return "\\".join(parts) + "\\" if parts else ""

    def _choose_family(self) -> None:
        """新建拼名族：几张图 → 一个按钮/边框（目录型基路径）。"""
        if self._on_stage is None:
            return
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择这一族的图片（3 张 = 一个按钮，9 张 = 九宫格）", "",
            "图片 (*.png *.jpg *.jpeg *.bmp *.tga *.gif *.igs);;"
            "所有文件 (*)")
        if not files:
            return
        try:
            payloads, ext = prepare_family_payloads(files)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "读图失败", str(exc))
            return
        # 先看文件名说明的结构（0/1/2 = 序号帧、0l/0c/0r = 按钮横片），
        # 再看控件默认。详见 choose_family_kind。
        kind = choose_family_kind(files, self._widget_type)
        dialog = FamilyImportDialog(
            self, files, self._suggested_family_path(), kind, ext, self._exists)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._stage_family(dialog.base_path, dialog.pairs, payloads, dialog.ext)

    def _stage_family(self, base: str, pairs: list[tuple[str, str]],
                      payloads: dict[str, bytes], ext: str) -> None:
        """把一族子图逐张挂账，并把这个目录路径选中（确定后写进属性）。"""
        if self._on_stage is None:
            return
        staged, failed = [], []
        for rel, path in pairs:
            res_path = base + rel.replace("/", "\\") + ext
            try:
                self._on_stage(res_path, payloads[path])
            except ValueError as exc:
                failed.append(f"{res_path}：{exc}")
                continue
            staged.append(res_path)
        if failed:
            QMessageBox.warning(
                self, "有些图没能挂账",
                "下面这些没写进待入包清单：\n\n" + "\n".join(failed[:5]))
        if not staged:
            return
        self.add_staged_path(base)
        self._count.setText(
            f"已挂账 {len(staged)} 张子图，组成族：{base}（保存回包时写入）")

    def _batch_process(self) -> None:
        """浏览窗「批量处理…」：选中项 → 参数窗 → 按计划执行（0.20.0）。

        选中项先过分筛（拼名族目录 / 范围外后缀 / 包内读不到字节的
        拒收并给一句话原因），能处理的一起进参数窗；参数窗确认后才
        执行（run_batch），失败逐项进清单、不中断整批。
        """
        if self._fetch_bytes is None:
            return
        selected = [str(item.data(_ROLE_PATH))
                    for item in self._list.selectedItems()]
        if not selected:
            QMessageBox.information(
                self, "还没选图片",
                "先在列表里选中要处理的图片（Ctrl/Shift 可多选），\n"
                "再点「批量处理…」。")
            return
        items: list[tuple[str, str, bytes]] = []
        rejected: list[str] = []
        for path in selected:
            if dir_base.is_dir_base(path):
                rejected.append(f"{path}：拼名族目录——请改选族里的单张子图")
                continue
            suffix = Path(path).suffix.lower()
            if suffix == ".igs":
                kind = "igs"
            elif suffix in (".png", ".jpg", ".jpeg", ".bmp", ".tga"):
                kind = "image"
            else:
                rejected.append(
                    f"{path}：{suffix or '无后缀'} 不在批处理范围"
                    "（PNG/JPG/BMP/TGA/.igs）")
                continue
            data = self._fetch_bytes(path)
            if data is None:
                rejected.append(f"{path}：包内读不到字节")
                continue
            items.append((path, kind, data))
        if not items:
            QMessageBox.warning(
                self, "选中的都不能批处理", "\n".join(rejected[:8]))
            return
        from .image_batch import ImageBatchDialog, run_batch
        dialog = ImageBatchDialog(
            self, items, suggested_dir=self._suggested_path(""),
            can_stage=self._on_stage is not None)
        if dialog.exec() != QDialog.DialogCode.Accepted or \
                dialog.plan is None:
            return
        plan = dialog.plan
        stage = (None if plan.mode != "stage"
                 else lambda name, data: self._stage_one(
                     name, data, confirm_same_name=False))
        ok, failed = run_batch(items, plan, stage=stage)
        failed.extend(rejected)
        if failed:
            QMessageBox.warning(
                self, "有些没能处理",
                "下面这些没有批处理成功：\n\n" + "\n".join(failed[:8]))
        if ok:
            where = (f"写入 {plan.out_dir}" if plan.mode == "disk"
                     else "已挂账（保存进包时写入）")
            self._count.setText(f"批量处理完成 {len(ok)} 张：{where}")

    def _pair_spr(self, src_file: str, res_path: str,
                  spr_data: bytes) -> None:
        """``.spr`` 的像素搭档：磁盘同目录同名 ``.igs``/``.png`` 连带挂账。

        ``.spr`` 只是 XOR4 加密的 INI 帧时表，游戏内像素来自同目录同名
        ``.igs``（官服 56 例中 53 例走同名搭档；另 2 例 ``[images]``
        变体把像素指到外部 .fls 包，本次导入带不上，只在标签里点明）。
        找不到搭档只挂 ``.spr``，把后果写清楚（0.19.0，用户拍板自动连带）。
        """
        src = Path(src_file)
        base = (res_path[:-4] if res_path.lower().endswith(".spr")
                else res_path)
        pair_src = next((cand for cand in (src.with_suffix(".igs"),
                                           src.with_suffix(".png"))
                         if cand.is_file()), None)
        if pair_src is None:
            note = "磁盘上未找到同名 .igs/.png：游戏里将有帧表而无像素。"
        else:
            target = f"{base}{pair_src.suffix}"
            if target in self._staged_paths:
                note = f"像素搭档 {target} 已挂账。"
            elif target in self._all_paths:
                note = f"包内已有 {target}，像素现成。"
            else:
                note = f"像素搭档 {pair_src.name} 读取失败，未挂上。"
                try:
                    pdata = pair_src.read_bytes()
                except OSError:
                    pdata = None
                if pdata is not None:
                    note = (f"连带挂账像素搭档 {target}。"
                            if self._stage_one(target, pdata)
                            else f"像素搭档 {target} 未挂上。")
        try:
            from ..core import spr_desc
            info = spr_desc.parse_images(
                spr_desc.decode_spr_text(spr_data) or "")
            if info.get("files"):
                pkg = str(info.get("package") or "")
                note += ("注意：这份 .spr 的像素指向外部包"
                         f"{'『' + pkg + '』' if pkg else ''}，不随本次导入。")
        except Exception:  # noqa: BLE001 解码失败不拦挂账主流程
            pass
        self._count.setText(f"已挂账 {res_path}。{note}")

    def _stage_many_raws(self, files: list[str]) -> None:
        """多个 .igs/.spr 一次选、逐张挂账：目录前缀 + 原文件名（0.18.0）。

        ``.spr`` 连带磁盘上的同名 ``.igs``/``.png`` 像素搭档；搭档已在
        本批选择里、已挂过账或包里已有同名条目时不连带（0.19.0）。
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("把这些 .igs/.spr 放进包")
        # 默认前缀 = 当前选中项所在目录（没有选中就是空 = 包根目录）；
        # 清单逐张列出最终包内路径，确认后才挂账。
        prefix = QLineEdit(self._suggested_path(""), dialog)
        note = QLabel(
            ".igs/.spr 按原字节挂账（不转换）。每项的包内路径 =\n"
            "下面前缀 + 原文件名；.spr 连带磁盘上的同名 .igs/.png\n"
            "（像素搭档；已在本批选择里或包里已有时不连带）；\n"
            "同名已有条目会在保存时替换。", dialog)
        note.setWordWrap(True)
        listing = QListWidget(dialog)
        listing.setMaximumHeight(160)

        def pair_of(f: str):
            """.spr → 磁盘上的像素搭档源文件（.igs 优先，其次 .png）。"""
            if not f.lower().endswith(".spr"):
                return None
            src = Path(f)
            return next((c for c in (src.with_suffix(".igs"),
                                     src.with_suffix(".png"))
                         if c.is_file()), None)

        chosen = {str(Path(f)) for f in files}
        entries = []
        for f in files:
            p = pair_of(f)
            if p is not None and str(p) in chosen:
                p = None      # 搭档就在本批选择里，不重复挂
            entries.append((f, p))

        def refresh() -> None:
            head = prefix.text().strip().replace("/", "\\")
            if head and not head.endswith("\\"):
                head += "\\"
            listing.clear()
            for f, p in entries:
                listing.addItem(f"{head}{Path(f).name}")
                if p is not None:
                    listing.addItem(f"{head}{p.name}（连带像素搭档）")
        prefix.textChanged.connect(lambda _t: refresh())
        refresh()
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel, parent=dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        box = QVBoxLayout(dialog)
        box.addWidget(note)
        box.addWidget(QLabel("目录前缀：", dialog))
        box.addWidget(prefix)
        box.addWidget(QLabel("将挂账为：", dialog))
        box.addWidget(listing)
        box.addWidget(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        head = prefix.text().strip().replace("/", "\\")
        if head and not head.endswith("\\"):
            head += "\\"
        done = 0
        for f, p in entries:
            try:
                data = Path(f).read_bytes()
            except OSError as exc:
                QMessageBox.warning(self, "读取失败", f"{f}\n{exc}")
                continue
            if self._stage_one(f"{head}{Path(f).name}", data):
                done += 1
            if p is None:
                continue
            target = f"{head}{p.name}"
            if target in self._staged_paths or target in self._all_paths:
                continue          # 已挂过 / 包里像素现成，不连带
            try:
                pdata = p.read_bytes()
            except OSError:
                continue
            if self._stage_one(target, pdata):
                done += 1
        if done:
            self._count.setText(
                f"已挂账 {done} 个 .igs/.spr 资源（保存进包时写入）")

    def _choose_add(self) -> None:
        """添加新图：选文件 → 问名字/是否转精灵 → 挂账待写入。

        选多张图 = 一个多帧精灵（一份资源）；选一张则可选转成
        单帧精灵或按原文件存。``.igs`` 是游戏精灵容器：单张按原字节
        挂账（绝不二次转换）；多张 ``.igs`` 一次选、逐张挂账
        （0.18.0）。``.spr``（界面特效帧时表，XOR4 加密 INI、不是图）
        同按原字节规矩，挂账时自动连带磁盘上的同名 ``.igs``/``.png``
        像素搭档；多选/混选规则与 .igs 一致（0.19.0，用户拍板）。
        """
        if self._on_stage is None:
            return
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择要加进包的图片（多选 = 多帧精灵）", "",
            "图片 (*.png *.jpg *.jpeg *.bmp *.tga *.gif *.igs *.spr);;"
            "所有文件 (*)")
        if not files:
            return
        image_exts = (".png", ".jpg", ".jpeg", ".bmp", ".tga", ".gif")
        raws = [f for f in files
                if Path(f).suffix.lower() in (".igs", ".spr")]
        if raws and len(raws) != len(files):
            QMessageBox.warning(
                self, "不能混选",
                ".igs/.spr 是游戏自有格式（按原字节挂账）、普通图片是\n"
                "待转换的素材，一次只能选其中一种。")
            return
        if len(raws) > 1:
            self._stage_many_raws(raws)
            return
        can_convert = all(
            Path(f).suffix.lower() in image_exts for f in files)
        multi = len(files) > 1
        result = self._ask_new_image(
            self._suggested_path(Path(files[0]).name), multi, can_convert)
        if result is None:
            return
        res_path, convert = result
        if convert:
            from ..core import sprite_encode

            def work(h):
                return sprite_encode.sprite_bytes_from_files(
                    files, progress=h.report, cancelled=lambda: h.cancelled)

            try:
                data, count = run_busy_or_plain(
                    self, "多帧精灵转换…", work,
                    cancellable=True, cancellable_text="取消转换")
            except Cancelled:
                self._count.setText("已取消转换，未挂账任何文件。")
                return
            except Exception as exc:
                QMessageBox.warning(self, "转精灵失败", str(exc))
                return
            self._stage_one(res_path, data)
            self._count.setText(
                f"已把 {count} 帧转成精灵挂账：{res_path}"
                "（保存回资源包时写入）")
            return
        if multi:
            QMessageBox.information(
                self, "多张图需要转精灵",
                "一次选多张图时请勾选「转成游戏精灵格式」合成一个"
                "动画资源；不想转的话请一次只选一张。")
            return
        try:
            data = Path(files[0]).read_bytes()
        except OSError as exc:
            QMessageBox.warning(self, "读取失败", str(exc))
            return
        if self._stage_one(res_path, data) \
                and Path(files[0]).suffix.lower() == ".spr":
            self._pair_spr(files[0], res_path, data)

    #: 各族"游戏怎么用这些图"的一句话（选中目录时显示）
    _KIND_USAGE = {
        "h_state": "这 3 张（或每 3 张）拼成按钮的一个状态：左片 0l + "
                   "中片 0c + 右片 0r，中间那片会被拉伸填满按钮。",
        "frames": "每张都是一整张按钮图：0 是常态、1/2 是悬停/按下等，"
                  "画布只显示第 1 张。",
        "nine_slice": "9 张按 3×3 拼：四角不动，四条边和中心被拉伸。",
        "h_slice": "左 + 中 + 右 三片横向拼，中片拉伸。",
        "v_slice": "上 + 中 + 下 三片纵向拼，中片拉伸。",
        "single": "整个目录只有这一张图，直接用。",
    }

    def _show_detail(self, path: str) -> None:
        """选中目录型基路径时，把"里面是什么"写清楚（用户最容易在这里犯迷糊）。"""
        if not path or not dir_base.is_dir_base(path):
            self._detail.hide()
            return
        pieces = None
        if self._family_pieces is not None:
            try:
                pieces = self._family_pieces(path)
            except Exception:
                pieces = None
        kind = None
        if self._family_kind is not None:
            try:
                kind = self._family_kind(path)
            except Exception:
                kind = None
        lines = [path.rstrip("\\/").replace("/", "\\").rsplit("\\", 1)[-1]
                 + "\\ 这个目录"]
        if pieces:
            lines.append("里面查到 " + str(len(pieces)) + " 张：" +
                         "、".join(pieces))
            if kind is None:
                lines.append("这几张按工具的命名规则拼不成一整族——可能是"
                             "别的写法（缺块、或与实测没见过的新规则），"
                             "画布会显示占位框。")
        else:
            lines.append("按常见写法没查到图：要么这个目录在包里是空的，"
                         "要么子图名是工具没见过的写法。")
        usage = self._KIND_USAGE.get(kind or "")
        if usage:
            lines.append("游戏怎么用：" + usage)
        self._detail.setText("\n".join(lines))
        self._detail.show()

    def _family_note(self, path: str) -> str | None:
        """路径是拼名族时返回一句话说明，否则 None（结果缓存）。"""
        if not dir_base.is_dir_base(path) or self._family_label is None:
            return None
        if path in self._family_notes:
            return self._family_notes[path]
        try:
            note = self._family_label(path)
        except Exception:
            note = None
        self._family_notes[path] = note
        return note

    def _make_item(self, path: str) -> tuple[QListWidgetItem, str | None]:
        """按路径造一行（缩略图留白，稍后按可见范围补）。"""
        text = _basename(path)
        note = self._family_note(path)
        if note:
            text += f"（{note}）"
        if path in self._staged_paths:
            text += "（新）"
        item = QListWidgetItem(text)
        item.setData(_ROLE_PATH, path)
        if dir_base.is_dir_base(path):
            pieces = None
            if self._family_pieces is not None:
                try:
                    pieces = self._family_pieces(path)
                except Exception:
                    pieces = None
            inside = (f"\n里面有 {len(pieces)} 张："
                      + "、".join(pieces[:12])
                      + ("…" if len(pieces) > 12 else "")
                      if pieces else "")
            item.setToolTip(
                f"{path}{inside}\n拼名族：包里没有这个目录条目，"
                "游戏运行时在其下拼子图；选它=把这个目录路径写进属性，"
                "导出时按族展开。")
        else:
            item.setToolTip(path)
        item.setIcon(self._blank_icon)
        return item, note

    def _refilter(self) -> None:
        query = self._search.text().strip().lower()
        only_families = self._only_families.isChecked()
        visible = [p for p in self._all_paths
                   if (not query or query in p.lower())
                   and (not only_families or dir_base.is_dir_base(p))]
        self._thumb_timer.stop()
        self._thumb_done.clear()
        self._list.clear()
        families = 0
        for path in visible:
            item, note = self._make_item(path)
            self._list.addItem(item)
            if note:
                families += 1
        self._family_total = families
        note = f"，含 {families} 个拼名族" if families else ""
        self._count.setText(
            f"共 {len(visible)} 个资源{note}（包内已有，选完保存回包不丢图）")
        self._schedule_thumbs()

    def _first_visible_row(self) -> int:
        """视口里第一行的序号（二分，O(log n)）。

        不用 ``indexAt``：offscreen/部分平台上它一律返回 −1，会把整个
        列表当成「都看得见」，缩略图又退回全量解码。图标模式下行优先
        排布，``visualItemRect`` 的纵坐标随行号单调，可以二分。
        """
        lo, hi = 0, self._list.count() - 1
        while lo < hi:
            mid = (lo + hi) // 2
            rect = self._list.visualItemRect(self._list.item(mid))
            if rect.bottom() < 0:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def _visible_items(self) -> list[QListWidgetItem]:
        """当前视口里看得到的行（看不到的不用解图）。

        列表还没排好版（行高为 0）时退回前 40 行，保证表头先出缩略图。
        """
        count = self._list.count()
        if not count:
            return []
        if self._list.visualItemRect(self._list.item(0)).height() <= 0:
            return [self._list.item(r) for r in range(min(count, 40))
                    if self._list.item(r) is not None]
        height = self._list.viewport().height()
        visible: list[QListWidgetItem] = []
        for row in range(self._first_visible_row(), count):
            item = self._list.item(row)
            if item is None:
                continue
            if self._list.visualItemRect(item).top() > height:
                break
            visible.append(item)
        return visible

    def resizeEvent(self, event) -> None:  # noqa: N802  列表变大要补图
        super().resizeEvent(event)
        self._schedule_thumbs()

    def _schedule_thumbs(self, *_args) -> None:
        """滚动/改窗口大小/重新过滤后：过 30 ms 给新露出来的行补缩略图。"""
        if self._thumb_provider is None:
            return
        if self._thumb_timer.isActive():
            return
        self._thumb_timer.start()

    def _fill_thumbs(self) -> None:
        """给**当前可见**的行补缩略图，一批 24 张（精灵解码不便宜）。"""
        if self._thumb_provider is None:
            self._thumb_timer.stop()
            return
        batch: list[QListWidgetItem] = []
        for item in self._visible_items():
            path = str(item.data(_ROLE_PATH))
            if path in self._thumb_done:
                continue
            batch.append(item)
            if len(batch) >= _THUMB_BATCH:
                break
        if not batch:
            self._thumb_timer.stop()
            return
        for item in batch:
            path = str(item.data(_ROLE_PATH))
            self._thumb_done.add(path)
            try:
                image = self._thumb_provider(path)  # type: ignore[misc]
            except Exception:
                image = None
            if image is not None:
                pixmap = QPixmap.fromImage(image)  # type: ignore[arg-type]
                if not pixmap.isNull():
                    item.setIcon(QIcon(pixmap.scaled(
                        72, 72, Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation)))
        if not self._visible_items_pending():
            self._thumb_timer.stop()

    def _visible_items_pending(self) -> bool:
        return any(str(item.data(_ROLE_PATH)) not in self._thumb_done
                   for item in self._visible_items())
