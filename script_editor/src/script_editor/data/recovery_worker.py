# SPDX-License-Identifier: GPL-3.0-or-later
# Standalone standard-pyc reader. No imports from the editor; file-based CLI only.
# Distributed without warranty; see licenses/recovery/GPL-3.0.txt.
"""Read/disassemble/decompile legacy pyc DATA. Never execute the target code."""

from __future__ import annotations

import argparse
import contextlib
import importlib.metadata
import io
import json
import sys
import tokenize
import traceback
from pathlib import Path

#: Per-product text budgets. The offline corpus path already accepted 8 MiB
#: artifacts; two real modules (entries 1945 and 1182) decompile into 4.0-4.2 MB
#: of source, which used to blow the old 2 MiB ceiling and turn a *successful*
#: engine run into a 310-character "failed" draft. Truncation is now explicit
#: instead of fatal, and the two products are budgeted separately.
LIMIT = 8 * 1024 * 1024
SOURCE_LIMIT = LIMIT
DISASSEMBLY_LIMIT = LIMIT

ENGINE_PROTOCOL = "mxsj-recovery/3"
SOURCE_SHA256 = "9e60958d4b0386e3976331ba6236ef2a1a986b2a162f3ddb9a8db424ae2e4d87"


def validate_engine():
    versions = {
        "uncompyle6": "3.9.4.dev0",
        "xdis": "6.3.0",
        "spark-parser": "1.9.0",
        "six": "1.17.0",
        "click": "8.5.0",
    }
    for name, version in versions.items():
        if importlib.metadata.version(name) != version:
            raise ValueError(
                "恢复引擎依赖版本不符，请运行新版bootstrap或完整重新构建EXE：" + name
            )
    info = importlib.metadata.distribution("uncompyle6").read_text("direct_url.json")
    data = json.loads(info or "{}")
    if data.get("archive_info", {}).get("hashes", {}).get("sha256") != SOURCE_SHA256:
        raise ValueError("恢复引擎源码来源摘要不符，请重新运行新版启动器安装固定源码")


class BoundedText(io.StringIO):
    """Text sink with a hard budget that records truncation instead of raising.

    Raising used to destroy the whole recovery result: the engine had already
    produced megabytes of usable source, but the caller only saw an exception
    comment. Here the tail is dropped, ``truncated`` is set, and the caller can
    still show and edit what was produced.
    """

    def __init__(self, limit: int = LIMIT):
        super().__init__()
        self.limit = limit
        self.truncated = False

    def write(self, value):
        remaining = self.limit - self.tell()
        if remaining <= 0:
            if value:
                self.truncated = True
            return 0
        if len(value) > remaining:
            self.truncated = True
            value = value[:remaining]
        return super().write(value)


def source_syntax(text, vm):
    """Rendering-only compatibility, never modify bytecode/opcodes or strings."""
    tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    offsets = [0]
    for line in text.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    edits, notes = [], []
    if vm == "py25":
        for token in tokens:
            if token.type != tokenize.STRING:
                continue
            prefix = token.string[
                : len(token.string) - len(token.string.lstrip("bBrRuU"))
            ]
            if "b" in prefix.lower():
                start = offsets[token.start[0] - 1] + token.start[1]
                edits.append(
                    (
                        start,
                        start + len(prefix),
                        prefix.replace("b", "").replace("B", ""),
                    )
                )
        if edits:
            notes.append(
                "Python2.5不支持b前缀；仅移除字符串token前缀的b，字符串内容不变。"
            )
    significant = [
        t
        for t in tokens
        if t.type
        not in (
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.COMMENT,
            tokenize.ENDMARKER,
            tokenize.DEDENT,
        )
    ]
    # Some legacy modules use LOAD_NAME None for their implicit module epilogue.
    # uncompyle6 renders an illegal top-level bare return. Only omit that exact
    # final statement; never remove returns inside functions or return values.
    if significant:
        last = significant[-1]
        candidate = last
        if last.string == "None" and len(significant) > 1:
            candidate = significant[-2]
        if (
            candidate.string == "return"
            and candidate.start[1] == 0
            and last.start[0] == candidate.start[0]
        ):
            start = offsets[candidate.start[0] - 1]
            end = offsets[last.end[0] - 1] + last.end[1]
            edits.append((start, end, "# implicit module return None"))
            notes.append(
                "省略反编译器生成的模块末尾隐式return None；不处理函数内return。"
            )
    for start, end, value in sorted(edits, reverse=True):
        text = text[:start] + value + text[end:]
    return (
        "# coding: utf-8\n"
        "# MXSJ-RECOVERED-DRAFT: not original source; review before publishing\n"
        f"# MXSJ-RECOVERY-VM: {vm}\n" + text,
        notes,
    )


def install_legacy_long_reader():
    """xdis6.3 reads the signed marshal-long digit count as unsigned.

    Compatibility adapter in this isolated GPL worker only. Preserve every
    integer value/sign; do not alter the input pyc, opcodes or game constants.
    CPython2 marshal.c uses a signed 32-bit count and unsigned 15-bit digits.
    """
    import xdis.unmarshal

    class SignedLongUnmarshaller(xdis.unmarshal.VersionIndependentUnmarshaller):
        def t_long(self, save_ref, bytes_for_s=False):
            count = self.read_int32()
            if abs(count) > 32 * 1024 * 1024:
                raise ValueError("marshal long exceeds input safety limit")
            value = 0
            for index in range(abs(count)):
                digit = self.read_int16()
                if not 0 <= digit < 32768:
                    raise ValueError("invalid marshal long digit")
                value += digit << (index * 15)
            return self.r_ref(-value if count < 0 else value, save_ref)

    xdis.unmarshal.VersionIndependentUnmarshaller = SignedLongUnmarshaller


def recover(path, vm, *, disassembly=True):
    validate_engine()
    import xdis.unmarshal as legacy_unmarshal
    from uncompyle6.main import decompile_file
    from uncompyle6.semantics.pysource import SourceWalker
    from xdis.bytecode import Bytecode
    from xdis.cross_types import UnicodeForPython3

    # xdis6.3 defaults to UTF-8 errors=ignore, which silently drops legacy
    # non-UTF8 byte constants. Retain the raw bytes on decode failure, as the
    # older reader did. This process-local input adaptation changes no bytes.
    def lossless_legacy_string(value):
        if isinstance(value, bytes):
            try:
                return value.decode("utf-8")
            except UnicodeDecodeError:
                return value
        return value

    legacy_unmarshal.compat_str = lossless_legacy_string

    # xdis's legacy Unicode repr drops the first two characters and mishandles
    # quotes/non-BMP text. Fix literal RENDERING in this separate process only;
    # never change constants or third-party installed files.
    def unicode_repr(value):
        raw = value.value
        return "u" + ascii(raw.decode("utf-8") if isinstance(raw, bytes) else raw)

    UnicodeForPython3.__repr__ = unicode_repr
    original_load_const = SourceWalker.n_LOAD_CONST

    def load_const(walker, node):
        if isinstance(node.pattr, UnicodeForPython3):
            walker.write(unicode_repr(node.pattr))
            walker.prune()
        else:
            original_load_const(walker, node)

    SourceWalker.n_LOAD_CONST = load_const
    install_legacy_long_reader()
    from xdis.load import load_module
    from xdis.op_imports import get_opcode_module

    if path.stat().st_size > 64 * 1024 * 1024 + 8:
        raise ValueError("standard pyc exceeds 64MiB limit")
    version, _, _, code, implementation, *_ = load_module(str(path))
    if tuple(version[:2]) != {"py25": (2, 5), "py27": (2, 7)}[vm]:
        raise ValueError("standard pyc VM mismatch")
    listing = BoundedText(DISASSEMBLY_LIMIT)
    diagnostics = []

    def walk(co, depth=0):
        if depth > 100:
            raise ValueError("code nesting limit")
        listing.write(f"\n{'  ' * depth}{co.co_name!r}\n")
        listing.write(
            Bytecode(
                co,
                get_opcode_module(
                    version,
                    implementation,
                ),
            ).dis()
        )
        for child in co.co_consts:
            if hasattr(child, "co_code"):
                walk(child, depth + 1)

    if disassembly:
        try:
            walk(code)
        except Exception as exc:
            traceback.print_exc(file=sys.stderr)
            diagnostics.append(
                f"反汇编未完整生成：{type(exc).__name__}: {str(exc)[:300]}"
            )
    source, complete = BoundedText(SOURCE_LIMIT), True
    try:
        decompile_file(str(path), outstream=source)
    except Exception as exc:
        complete = False
        traceback.print_exc(file=sys.stderr)
        diagnostics.append(f"源码恢复未完成：{type(exc).__name__}: {str(exc)[:300]}")
    raw_source = source.getvalue()
    if source.truncated:
        complete = False
        limit_mib = SOURCE_LIMIT // (1024 * 1024)
        diagnostics.append(
            f"源码超过 {limit_mib} MiB 上限，已截断；完整文本请用离线语料路径核对。"
        )
    if listing.truncated:
        listing_mib = DISASSEMBLY_LIMIT // (1024 * 1024)
        diagnostics.append(f"反汇编超过 {listing_mib} MiB 上限，已截断。")
    text = raw_source
    if text.strip():
        try:
            text, notes = source_syntax(text, vm)
            diagnostics.extend(notes)
        except (tokenize.TokenError, IndentationError, SyntaxError) as exc:
            traceback.print_exc(file=sys.stderr)
            complete = False
            diagnostics.append(f"恢复稿词法不完整：{type(exc).__name__}")
    return {
        "source": text,
        "raw_source": raw_source,
        "complete": complete,
        "disassembly": listing.getvalue(),
        "diagnostics": diagnostics,
        "truncated": {
            "source": source.truncated,
            "disassembly": listing.truncated,
        },
        "limits": {"source": SOURCE_LIMIT, "disassembly": DISASSEMBLY_LIMIT},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--vm", required=True, choices=("py25", "py27"))
    parser.add_argument(
        "--no-disassembly",
        action="store_true",
        help="只产出源码；反汇编可按需另起一次运行（大模块首字节时间更短）",
    )
    args = parser.parse_args(argv)
    captured_out = BoundedText(4 * 1024 * 1024)
    captured_err = BoundedText(4 * 1024 * 1024)
    try:
        # Parser debug prints stay inside this process, never global GUI stdout.
        with (
            contextlib.redirect_stdout(captured_out),
            contextlib.redirect_stderr(captured_err),
        ):
            result = recover(
                args.input, args.vm, disassembly=not args.no_disassembly
            )
    except Exception as exc:
        with contextlib.redirect_stderr(captured_err):
            traceback.print_exc()
        result = {
            "source": "",
            "complete": False,
            "disassembly": "",
            "diagnostics": [f"恢复引擎失败：{type(exc).__name__}: {str(exc)[:300]}"],
            "truncated": {"source": False, "disassembly": False},
        }
    result["worker_stdout"] = captured_out.getvalue()
    result["worker_stderr"] = captured_err.getvalue()
    result["engine_protocol"] = ENGINE_PROTOCOL
    args.output.write_text(json.dumps(result, ensure_ascii=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
