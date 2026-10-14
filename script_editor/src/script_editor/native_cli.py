"""Experimental M2 one-module build, intentionally separate from the GUI."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

from .core.archives.document import ArchiveDocument
from .core.compiler.runner import compile_standard, inspect_compiler
from .core.services.files import read_source
from .core.services.native_build import Replacement, build_package, guard_new_package
from .core.vm.py25.keys import load_profile


def main(argv=None):
    parser = argparse.ArgumentParser(description="实验M2单模块新包构建，不是实机验收")
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--archive-sha256", required=True)
    parser.add_argument("--entry-index", type=int, required=True)
    parser.add_argument("--entry-identity", required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--module-filename",
        required=True,
        help="显式指定原模块嵌入文件名，不自动猜模块导入名",
    )
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--vm", choices=("py25", "py27"), required=True)
    parser.add_argument("--keys", type=Path)
    parser.add_argument("--keys-sha256")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--confirm-authored-source",
        action="store_true",
        help="必须确认输入是可信自写/真实源码，而非反编译稿",
    )
    args = parser.parse_args(argv)
    try:
        if not args.confirm_authored_source:
            raise ValueError("必须显式确认源码来源；反编译稿不能用于原生构建")
        protected = (
            args.archive,
            args.source,
            args.compiler,
            *([args.keys] if args.keys else []),
        )
        guard_new_package(args.output, protected)
        profiles = {}
        with ArchiveDocument(args.archive) as archive:
            i = args.entry_index
            if (
                archive.vm != args.vm
                or archive.fingerprint() != args.archive_sha256
                or not 0 <= i < len(archive.entries)
                or archive.entries[i].identity != args.entry_identity
                or archive.entries[i].directory
            ):
                raise ValueError("包指纹/VM/模块身份不匹配")
            if args.vm == "py25":
                if not args.keys or not args.keys_sha256:
                    raise ValueError("VM2.5必须提供外部XOR目录及其SHA256")
                profiles[i] = load_profile(
                    archive,
                    i,
                    args.keys,
                    archive_sha256=args.archive_sha256,
                    catalog_sha256=args.keys_sha256,
                )
        compiler = inspect_compiler(args.compiler, args.vm)
        source = read_source(args.source)
        with tempfile.TemporaryDirectory(prefix="mxscript-native-cli-") as temp:
            standard = Path(temp) / "authored.pyc"
            compile_standard(
                compiler, source, args.module_filename, standard, protected
            )
            report = build_package(
                args.archive,
                args.output,
                source_sha256=args.archive_sha256,
                compiler=compiler,
                profiles=profiles,
                replacements=(
                    Replacement(i, args.entry_identity, standard.read_bytes()),
                ),
                protected=protected,
            )
        result = asdict(report)
        result["output"] = str(report.output)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except Exception as exc:
        print(f"构建拒绝/失败：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
