#!/usr/bin/env python3
"""从原生改密页派生四字段注册表单，另逐字拷贝服务条款布局。

显示文字是 Big5 字节，资源路径是 GBK 字节。以 latin-1 无损承载原始
字符串，序列化时只转义 ASCII 控制字节/引号/反斜杠，不将高位字节
转成 Unicode 或夹杂 repr 的 \\xXX 转义，避免皮肤路径、文字被重编码。

勾选框使用 .dlg 的 CBox 锚点和游戏原生 CIMGCHECKBOX 工厂，不造图片。
"""

from __future__ import annotations

import ast
import copy
import hashlib
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "templates" / "chgpwd.dlg"
DST = HERE / "regform.dlg"


def b5(text: str) -> str:
    """繁体文案 -> Big5 原字节，以 latin-1 字符串无损承载。"""
    return text.encode("big5").decode("latin-1")


def load_ui(path: Path) -> list[dict]:
    text = path.read_bytes().decode("latin-1")
    match = re.search(r"UI_INFO\s*=\s*(\[.*\])\s*$", text, re.S)
    if match is None:
        raise ValueError(f"UI_INFO missing: {path}")
    result = ast.literal_eval(match.group(1))
    if not isinstance(result, list) or not all(isinstance(w, dict) for w in result):
        raise ValueError(f"UI_INFO must be a list of widget dictionaries: {path}")
    return result


def _raw_literal(value: object, depth: int = 0) -> str:
    """保留混合编码的字节形态；输出游戏可读取的字面量，不执行数据。"""
    if isinstance(value, str):
        chars = ['"']
        for char in value:
            if char in ('"', "\\"):
                chars.append("\\" + char)
            elif ord(char) < 32 or ord(char) == 127:
                chars.append(f"\\x{ord(char):02x}")
            else:
                chars.append(char)
        return "".join(chars) + '"'
    if isinstance(value, dict):
        lines = ["{"]
        for key, item in value.items():
            lines.append(
                "\t" * (depth + 1)
                + _raw_literal(key)
                + ": "
                + _raw_literal(item, depth + 1)
                + ", "
            )
        return "\n".join(lines + ["\t" * depth + "}"])
    if isinstance(value, (list, tuple)):
        opening, closing = ("[", "]") if isinstance(value, list) else ("(", ")")
        if not value:
            return opening + closing
        lines = [opening]
        lines.extend(
            "\t" * (depth + 1) + _raw_literal(item, depth + 1) + ", " for item in value
        )
        return "\n".join(lines + ["\t" * depth + closing])
    if value is None or isinstance(value, (bool, int, float)):
        return repr(value)
    raise ValueError(f"unsupported layout value: {type(value).__name__}")


def serialize_ui(widgets: list[dict]) -> bytes:
    body = "UI_INFO = " + _raw_literal(widgets) + "\n"
    raw = body.encode("latin-1")
    digest = hashlib.md5(raw).hexdigest()
    return f"# -*- coding: gbk -*-\n# MD5: {digest}\n\n".encode("ascii") + raw


def build_form(template: Path = SRC) -> list[dict]:
    ui = load_ui(template)
    by_type_name = {(w.get("sWidgetType"), w.get("sName")): w for w in ui}
    by_type_name[("CFrame", "noname3")]["iHeight"] = 316

    # 四行标签，行距与输入框一致（17px 字体 + 23px 行间距）。
    label = by_type_name[("CTextFrame", "noname7")]
    label["sText"] = b5("輸入帳號\n輸入密碼\n確認密碼\n電子郵箱")
    label["iY"] = 258
    label["iSpace"] = 23
    ui.remove(by_type_name[("CTextFrame", "noname8")])

    # 四个输入外框，保留母版原生皮肤。
    frames = [w for w in ui if w.get("sWidgetType") == "CHFrame"]
    assert len(frames) == 3
    extra = copy.deepcopy(frames[2])
    extra["sName"] = "noname20"
    ui.insert(ui.index(frames[2]) + 1, extra)
    frames.append(extra)
    for widget, y in zip(frames, (250, 290, 330, 370), strict=True):
        widget["iY"] = y

    # 三个原生登陆按钮：确认、上一步、返回首页。
    buttons = [w for w in ui if w.get("sWidgetType") == "CButton"]
    assert len(buttons) == 2
    extra = copy.deepcopy(buttons[0])
    extra["sName"] = "noname21"
    ui.insert(ui.index(buttons[-1]) + 1, extra)
    buttons.append(extra)
    for widget, (y, msgid) in zip(buttons, ((400, 2), (457, 1), (514, 3)), strict=True):
        widget["iY"] = y
        widget["iMsgId"] = msgid

    texts = [
        w
        for w in ui
        if w.get("sWidgetType") == "CTextFrame"
        and w.get("sName") in ("noname12", "noname13")
    ]
    assert len(texts) == 2
    extra = copy.deepcopy(texts[1])
    extra["sName"] = "noname22"
    ui.insert(ui.index(texts[-1]) + 1, extra)
    texts.append(extra)
    for widget, (text, x, y) in zip(
        texts,
        (("確認註冊", 667, 411), ("上一步", 674, 468), ("返回首頁", 667, 525)),
        strict=True,
    ):
        widget.update(sText=b5(text), iX=x, iY=y)

    # 四个 CBox 编辑锚点，原生 CEDIT 工厂会按名认领。
    boxes = {w["sName"]: w for w in ui if w.get("sWidgetType") == "CBox"}
    edits = [boxes["old"], boxes["new"], boxes["new2"]]
    extra = copy.deepcopy(boxes["new2"])
    extra["sName"] = "email"
    ui.insert(ui.index(boxes["new2"]) + 1, extra)
    edits.append(extra)
    for widget, (name, y) in zip(
        edits,
        (("account", 254), ("pwd", 294), ("pwd2", 334), ("email", 374)),
        strict=True,
    ):
        widget.update(sName=name, iY=y)

    # 顶部提示区随单账号/五账号模式切换。
    boxes["txt"].update(iY=176, iHeight=64)

    # 原生勾选框锚点覆盖方框和旁边文字，二者都可以点击。
    checkbox = copy.deepcopy(edits[0])
    checkbox.update(sName="chk_five", iX=328, iY=410, iWidth=224, iHeight=24)
    ui.append(checkbox)
    caption = copy.deepcopy(label)
    caption.update(sName="lbl_five", sText=b5("註冊五個帳號"), iX=360, iY=414, iSpace=0)
    ui.append(caption)
    return ui


def main() -> int:
    ui = build_form()
    DST.write_bytes(serialize_ui(ui))
    assert load_ui(DST) == ui, "layout raw-byte round trip failed"
    names = [widget.get("sName") for widget in ui]
    assert len(set(names)) == len(names), "duplicate widget names"
    for name in ("account", "pwd", "pwd2", "email", "txt", "chk_five", "lbl_five"):
        assert name in names, name
    msgids = sorted(w["iMsgId"] for w in ui if w.get("sWidgetType") == "CButton")
    assert msgids == [1, 2, 3], msgids

    # 协议页必须和用户回传的服务条款布局逐字节一致，连 MD5 注释也不改。
    terms = (HERE / "templates" / "service.dlg").read_bytes()
    (HERE / "regterms.dlg").write_bytes(terms)
    service_ui = load_ui(HERE / "regterms.dlg")
    assert any(w.get("sName") == "loc_msg" for w in service_ui)
    service_msgids = sorted(w["iMsgId"] for w in service_ui if "iMsgId" in w)
    assert service_msgids == [1, 2], service_msgids
    print(f"[+] regform.dlg: {len(ui)} widgets; button msgids={msgids}; checkbox=4")
    print("[+] regterms.dlg: byte-identical copy of templates/service.dlg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
