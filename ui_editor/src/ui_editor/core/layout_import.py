"""只读布局导入预检：相对 GBK 路径、结构、编码和目标类型。"""

from __future__ import annotations

from pathlib import PureWindowsPath

from . import dlg_codec
from .diagnostics import diagnose
from .errors import PackError
from .model import LayoutDocument
from .pack import FlsPack
from .pack_build import unpack_packed_text


def validate_layout_path(value: str) -> str:
    value = value.strip().replace("\\", "/")
    if (
        not value
        or PureWindowsPath(value).drive
        or PureWindowsPath(value).is_absolute()
        or any(ord(char) < 32 or char in '<>:"|?*' for char in value)
        or any(part in ("", ".", "..") for part in value.split("/"))
        or not value.lower().endswith(".dlg")
    ):
        raise ValueError("布局地址必须是包内相对 .dlg 路径，如 login/regform.dlg。")
    value.encode("gbk")
    return value


def _check_import_encoding(value, key=None) -> None:
    if isinstance(value, dict):
        for field, child in value.items():
            _check_import_encoding(child, field)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _check_import_encoding(child, key)
    elif isinstance(value, str):
        codec = (
            "big5"
            if key in dlg_codec._BIG5_TEXT_KEYS
            else "gbk"
            if key in dlg_codec._GBK_PATH_KEYS
            else None
        )
        if codec:
            try:
                value.encode(codec)
            except UnicodeEncodeError as exc:
                raise ValueError(
                    f"导入字段 {key} 不是有效的 {codec.upper()} 文本。"
                ) from exc


def prepare_layout_import(
    pack: FlsPack, path: str, data: bytes
) -> tuple[LayoutDocument, bool]:
    """验证后返回编辑文档与是否替换；不写源包、不执行布局源码。"""
    path = validate_layout_path(path)
    dicts, md5 = dlg_codec.parse_bytes(data)
    _check_import_encoding(dicts)
    doc = LayoutDocument.from_dicts(dicts, md5)
    errors = [issue for issue in diagnose(doc) if issue.code == "ENCODING"]
    if errors:
        raise ValueError("布局字段编码错误：" + "；".join(i.message for i in errors))
    replacing = pack.contains(path)
    previous = []
    if replacing:
        try:
            previous, old_md5 = dlg_codec.parse_bytes(
                unpack_packed_text(pack.read_named(path))
            )
            LayoutDocument.from_dicts(previous, old_md5)
        except Exception as exc:
            raise PackError("目标编号已有非布局资源，拒绝覆盖。") from exc
    doc.begin_pack_import(previous)
    return doc, replacing
