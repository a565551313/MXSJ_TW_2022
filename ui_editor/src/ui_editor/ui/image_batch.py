"""浏览窗「批量处理…」：缩放 / 亮度 / 饱和度（Pillow 干活，0.20.0）。

用户拍板（ask_user 四决策点）：入口＝浏览窗；操作＝最小三样（缩放、
亮度、饱和度）；范围＝普通图片＋.igs（解码→调整→重编码，保真护栏见
``core.image_adjust``）；预览＝首图前后对比＋输出清单确认。

输出去处二选一（原资源/原文件一律不动）：

* **写到磁盘目录**：输出到用户选的目录、文件名沿用，**永不覆盖**任何
  现有文件（重名加 ``-2``/``-3`` 后缀，``asset_export.unique_target``
  既有规矩）；
* **挂账进包**：输出路径＝原包路径，同名＝保存时替换包内原资源——
  清单逐条标注、本窗一次性确认，挂账走
  ``_stage_one(confirm_same_name=False)``，执行时不逐张打断。
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)

from ..core import image_adjust, sprite
from ..core.asset_export import unique_target
from ..core.image_adjust import AdjustParams
from .status_text import pack_name

__all__ = ["BatchPlan", "ImageBatchDialog", "run_batch"]

_PREVIEW_BOX = 180
#: 预览实际调整所用的有界工作副本边长上限，与预览输出边长上限
#: （PR #90 审查复核属实：磁盘任意图全分辨率逐步重算会卡死对话框）。
_PREVIEW_WORK_BOX = 360
_PREVIEW_OUT_CAP = 1280


@dataclass(frozen=True)
class BatchPlan:
    """参数窗确认下来的批处理计划：参数＋输出去处。"""

    params: AdjustParams
    mode: str                 # "disk" | "stage"
    out_dir: str = ""


def _to_pixmap(img: Image.Image) -> QPixmap:
    """PIL 图 → 预览框里放得下的缩略图（仅显示缩放，不改处理像素）。"""
    img = img.convert("RGBA")
    qimg = QImage(img.tobytes("raw", "RGBA"), img.width, img.height,
                  img.width * 4, QImage.Format.Format_RGBA8888).copy()
    pm = QPixmap.fromImage(qimg)
    if pm.width() > _PREVIEW_BOX or pm.height() > _PREVIEW_BOX:
        pm = pm.scaled(_PREVIEW_BOX, _PREVIEW_BOX,
                       Qt.AspectRatioMode.KeepAspectRatio,
                       Qt.TransformationMode.SmoothTransformation)
    return pm


def _target_exists(target: Path) -> bool:
    try:
        return target.exists()
    except OSError:   # 目录读不了：预演按不存在处理，落盘以 unique_target 为准
        return False


def _first_image(item) -> Image.Image:
    """预览用的首项源图：普通图片直接解，.igs 取第一帧。"""
    _path, kind, data = item
    if kind == "igs":
        spr = sprite.decode_sprite(data)
        frame = spr.frames[0]
        return Image.frombytes(
            "RGBA", (frame.width, frame.height), frame.rgba)
    with Image.open(io.BytesIO(data)) as img:
        return img.convert("RGBA")


class ImageBatchDialog(QDialog):
    """批处理参数确认窗：操作＋首图前后预览＋输出清单。

    本窗不碰任何字节：accept 后把 :attr:`plan` 交给宿主（选图窗）按
    :func:`run_batch` 执行。
    """

    def __init__(self, parent, items, suggested_dir: str = "",
                 can_stage: bool = True):
        super().__init__(parent)
        self._items = list(items)
        self._suggested_dir = suggested_dir
        self._can_stage = can_stage
        self.plan: BatchPlan | None = None
        self.setWindowTitle("批量处理图片（缩放 / 亮度 / 饱和度）")
        first_name = pack_name(self._items[0][0]) if self._items else ""
        self._info = QLabel(
            f"共 {len(self._items)} 项；预览第一项：{first_name}", self)

        self._preview_src: Image.Image | None = None
        self._preview_error = ""
        try:
            self._preview_src = _first_image(self._items[0])
        except Exception as exc:  # 预览失败不拦批处理（清单照常确认）
            self._preview_error = f"预览失败：{exc}"
        # 预览调整在有界工作副本上跑（PR #90 审查复核属实）：独立入口
        # 可从磁盘选任意图，全分辨率 LANCZOS＋全幅 RGBA 拷贝逐步重算
        # 会卡死对话框；before 缩略图与参数无关，一次缓存。仅供显示
        # 对比——实际批处理永远在原像素上执行。
        self._preview_work = self._preview_src
        if self._preview_src is not None and \
                max(self._preview_src.size) > _PREVIEW_WORK_BOX:
            work = self._preview_src.copy()
            work.thumbnail((_PREVIEW_WORK_BOX, _PREVIEW_WORK_BOX),
                           Image.Resampling.LANCZOS)
            self._preview_work = work
        self._preview_before_pm = (_to_pixmap(self._preview_work)
                                   if self._preview_work is not None
                                   else QPixmap())

        layout = QVBoxLayout(self)
        layout.addWidget(self._info)
        body = QHBoxLayout()
        body.addLayout(self._build_controls())
        body.addLayout(self._build_preview())
        layout.addLayout(body)
        layout.addWidget(self._build_output())
        self._listing = QListWidget(self)
        self._listing.setMaximumHeight(140)
        layout.addWidget(self._listing)
        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel, self)
        ok = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok.setText("处理")
        self._buttons.accepted.connect(self._on_accept)
        self._buttons.rejected.connect(self.reject)
        layout.addWidget(self._buttons)
        self._refresh()

    # -- 控件搭建 -------------------------------------------------------
    def _build_controls(self) -> QVBoxLayout:
        col = QVBoxLayout()
        scale = QGroupBox("缩放", self)
        sv = QVBoxLayout(scale)
        self._mode_combo = QComboBox(scale)
        self._mode_combo.addItems(["不缩放", "按百分比", "到目标尺寸"])
        sv.addWidget(self._mode_combo)
        self._percent_spin = QSpinBox(scale)
        self._percent_spin.setRange(5, 500)
        self._percent_spin.setValue(100)
        self._percent_spin.setSuffix(" %")
        percent_row = QHBoxLayout()
        percent_row.addWidget(QLabel("百分比：", scale))
        percent_row.addWidget(self._percent_spin)
        sv.addLayout(percent_row)
        self._tw_spin = QSpinBox(scale)
        self._tw_spin.setRange(0, 4096)
        self._tw_spin.setSpecialValueText("不限")
        self._th_spin = QSpinBox(scale)
        self._th_spin.setRange(0, 4096)
        self._th_spin.setSpecialValueText("不限")
        if self._preview_src is not None:
            self._tw_spin.setValue(min(4096, self._preview_src.width))
            self._th_spin.setValue(min(4096, self._preview_src.height))
        self._keep_aspect = QCheckBox("保持纵横比", scale)
        self._keep_aspect.setChecked(True)
        target_row = QHBoxLayout()
        target_row.addWidget(QLabel("宽", scale))
        target_row.addWidget(self._tw_spin)
        target_row.addWidget(QLabel("高", scale))
        target_row.addWidget(self._th_spin)
        target_row.addWidget(self._keep_aspect)
        sv.addLayout(target_row)
        col.addWidget(scale)

        tone = QGroupBox("色调（100% = 不变）", self)
        tv = QVBoxLayout(tone)
        self._bright_slider, self._bright_spin = self._factor_row(
            tone, tv, "亮度")
        self._sat_slider, self._sat_spin = self._factor_row(
            tone, tv, "饱和度")
        col.addWidget(tone)
        col.addStretch(1)

        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self._percent_spin.valueChanged.connect(self._refresh_preview)
        self._tw_spin.valueChanged.connect(self._refresh_preview)
        self._th_spin.valueChanged.connect(self._refresh_preview)
        self._keep_aspect.toggled.connect(self._refresh_preview)
        self._apply_mode_enabled(0)     # 初始「不缩放」：两行都禁用
        return col

    def _factor_row(self, box, layout_v, name: str):
        row = QHBoxLayout()
        row.addWidget(QLabel(f"{name}：", box))
        slider = QSlider(Qt.Orientation.Horizontal, box)
        slider.setRange(0, 200)
        slider.setValue(100)
        spin = QSpinBox(box)
        spin.setRange(0, 200)
        spin.setValue(100)
        spin.setSuffix(" %")
        slider.valueChanged.connect(spin.setValue)
        spin.valueChanged.connect(slider.setValue)
        spin.valueChanged.connect(self._refresh_preview)
        row.addWidget(slider, 1)
        row.addWidget(spin)
        layout_v.addLayout(row)
        return slider, spin

    def _build_preview(self) -> QVBoxLayout:
        col = QVBoxLayout()
        row = QHBoxLayout()
        for caption in ("原图", "处理后"):
            cell = QVBoxLayout()
            cell.addWidget(QLabel(caption, self))
            label = QLabel(self)
            label.setMinimumSize(_PREVIEW_BOX + 12, _PREVIEW_BOX + 12)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(
                "background: #f4f6f8; border: 1px solid #ccd2da;"
                " border-radius: 4px;")
            cell.addWidget(label)
            row.addLayout(cell)
            if caption == "原图":
                self._before_label = label
            else:
                self._after_label = label
        col.addLayout(row)
        return col

    def _build_output(self) -> QGroupBox:
        box = QGroupBox("输出去处（原资源 / 原文件一律不动）", self)
        v = QVBoxLayout(box)
        self._radio_disk = QRadioButton(
            "写到磁盘目录（永不覆盖现有文件，重名自动加 -2/-3）", box)
        self._radio_disk.setChecked(True)
        self._dir_edit = QLineEdit(box)
        self._dir_edit.setReadOnly(True)
        self._dir_edit.setPlaceholderText("还没选输出目录")
        self._dir_btn = QPushButton("选目录…", box)
        self._dir_btn.clicked.connect(self._choose_dir)
        dir_row = QHBoxLayout()
        dir_row.addWidget(self._radio_disk)
        dir_row.addWidget(self._dir_edit, 1)
        dir_row.addWidget(self._dir_btn)
        v.addLayout(dir_row)
        self._radio_stage = QRadioButton(
            "挂账进包（输出路径＝原包路径；同名＝保存时替换包内原资源）",
            box)
        self._radio_stage.setEnabled(self._can_stage)
        v.addWidget(self._radio_stage)
        self._radio_disk.toggled.connect(self._refresh_listing)
        self._radio_stage.toggled.connect(self._refresh_listing)
        self._dir_edit.textChanged.connect(self._refresh_listing)
        return box

    # -- 参数 / 刷新 ----------------------------------------------------
    def _params(self) -> AdjustParams:
        mode = ("none", "percent", "target")[self._mode_combo.currentIndex()]
        return AdjustParams(
            scale_mode=mode,
            percent=self._percent_spin.value(),
            target_w=self._tw_spin.value(),
            target_h=self._th_spin.value(),
            keep_aspect=self._keep_aspect.isChecked(),
            brightness=self._bright_spin.value() / 100.0,
            saturation=self._sat_spin.value() / 100.0)

    def _apply_mode_enabled(self, index: int) -> None:
        self._percent_spin.setEnabled(index == 1)
        self._tw_spin.setEnabled(index == 2)
        self._th_spin.setEnabled(index == 2)
        self._keep_aspect.setEnabled(index == 2)

    def _on_mode_changed(self, index: int) -> None:
        self._apply_mode_enabled(index)
        self._refresh_preview()

    def _choose_dir(self) -> None:
        chosen = QFileDialog.getExistingDirectory(
            self, "选批处理输出目录", self._suggested_dir)
        if chosen:
            self._dir_edit.setText(chosen)

    def _refresh(self) -> None:
        self._refresh_preview()
        self._refresh_listing()

    def _refresh_preview(self) -> None:
        if self._preview_src is None:
            text = self._preview_error or "无预览"
            self._before_label.setText(text)
            self._after_label.setText(text)
            return
        self._before_label.setPixmap(self._preview_before_pm)
        params = self._params()
        work = self._preview_work
        out_w, out_h = image_adjust.adjusted_size(work.width, work.height,
                                                  params)
        if max(out_w, out_h) > _PREVIEW_OUT_CAP:
            # 巨大输出（如大图×500%）：预览没有意义（显示框只有
            # 180px），直说真实输出尺寸、略过预览；实际批处理不受影响。
            real_w, real_h = image_adjust.adjusted_size(
                self._preview_src.width, self._preview_src.height, params)
            self._after_label.setPixmap(QPixmap())
            self._after_label.setText(
                f"目标输出 {real_w}×{real_h} 过大，\n预览从略（批处理照常执行）。")
            return
        try:
            out = image_adjust.adjust_image(work, params)
            self._after_label.setPixmap(_to_pixmap(out))
        except image_adjust.AdjustError as exc:
            self._after_label.setPixmap(QPixmap())
            self._after_label.setText(str(exc))
        except MemoryError:  # 有界副本下通常到不了这里；极端环境兜底
            self._after_label.setPixmap(QPixmap())
            self._after_label.setText("预览内存不足（批处理照常执行）。")

    def _refresh_listing(self) -> None:
        stage = self._radio_stage.isChecked()
        out_dir = self._dir_edit.text().strip().rstrip("/\\")
        self._listing.clear()
        reserved: set[str] = set()
        for path, _kind, _data in self._items:
            if stage:
                self._listing.addItem(f"{path}（同名替换包内原资源）")
            elif out_dir:
                # 清单显示真正会落盘的文件名（PR #90 审查复核属实）：
                # run_batch 永不覆盖，重名走 unique_target 变 -2/-3——
                # 这里按同一规则预演（含本批在前项已占用的名字）。执行
                # 时仍以 unique_target 落盘瞬间为准：期间目录内容若变化，
                # 不覆盖优先于预演一致。
                self._listing.addItem(
                    f"{out_dir}\\{self._predicted_name(out_dir, path, reserved)}")
            else:
                self._listing.addItem(
                    f"{pack_name(path)}（选好输出目录后显示完整路径）")

    @staticmethod
    def _predicted_name(out_dir: str, path: str, reserved: set[str]) -> str:
        """按 unique_target 的规则预演确认时的落盘名（含批内占用）。"""
        name = pack_name(path)
        stem, suffix = Path(name).stem, Path(name).suffix
        dest = Path(out_dir)
        candidate, index = name, 2
        while candidate in reserved or _target_exists(dest / candidate):
            candidate = f"{stem}-{index}{suffix}"
            index += 1
        reserved.add(candidate)
        return candidate

    def _on_accept(self) -> None:
        mode = "stage" if self._radio_stage.isChecked() else "disk"
        out_dir = self._dir_edit.text().strip()
        if mode == "disk" and not out_dir:
            QMessageBox.warning(
                self, "还没选输出目录",
                "「写到磁盘目录」要先选好输出目录，\n"
                "或改选「挂账进包」。")
            return
        self.plan = BatchPlan(params=self._params(), mode=mode,
                              out_dir=out_dir)
        self.accept()


def run_batch(items, plan: BatchPlan,
              stage=None) -> tuple[list[str], list[str]]:
    """按计划执行整批：返回 (成功输出路径, 失败「路径：原因」)。

    ``stage`` 是选图窗的 ``_stage_one(confirm_same_name=False)``——同名
    替换的确认已在参数窗清单里一次性问过，执行时不再逐张打断。单项
    失败进清单、不中断整批（与拼名族挂账的既有容错姿势一致）。
    """
    ok: list[str] = []
    failed: list[str] = []
    for path, kind, data in items:
        try:
            if kind == "igs":
                out = image_adjust.process_sprite(data, plan.params)
            else:
                out = image_adjust.process_plain(data, plan.params)
        except image_adjust.AdjustError as exc:
            failed.append(f"{path}：{exc}")
            continue
        except Exception as exc:   # 意外错误也进清单，不中断整批
            failed.append(f"{path}：{exc}")
            continue
        if plan.mode == "disk":
            try:
                dest = Path(plan.out_dir)
                dest.mkdir(parents=True, exist_ok=True)
                target = unique_target(dest, pack_name(path))
                target.write_bytes(out)
            except OSError as exc:
                failed.append(f"{path}：写入失败 {exc}")
                continue
            ok.append(str(target))
        elif stage is None:
            failed.append(f"{path}：没有挂账回调")
        elif stage(path, out):
            ok.append(path)
        else:
            failed.append(f"{path}：未挂账（名字被拒或回调失败）")
    return ok, failed
