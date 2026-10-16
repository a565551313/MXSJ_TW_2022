"""Maintainer cross-build of pinned pycdc for Windows x86; no target execution.

Requires ziglang==0.13.0. Normal source-package users receive the built program.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
from script_editor.core.services.pycdc_engine import SOURCE_COMMIT, SOURCE_SHA256  # noqa: E402


def build(work, output, jobs=4):
    if not 1 <= jobs <= 16 or work.exists() or output.exists():
        raise ValueError("Choose new work/output directories and jobs 1..16")
    zig = [sys.executable, "-m", "ziglang"]
    if subprocess.check_output([*zig, "version"], text=True).strip() != "0.13.0":
        raise ValueError("requires Zig 0.13.0")
    source = HERE / "third_party" / f"pycdc-{SOURCE_COMMIT}.tar.gz"
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("pinned source mismatch")
    work.mkdir(parents=True)
    if hasattr(os, "sched_setaffinity"):
        os.sched_setaffinity(0, set(sorted(os.sched_getaffinity(0))[:jobs]))
    with tarfile.open(source) as tar:
        for member in tar.getmembers():
            if (
                Path(member.name).is_absolute()
                or ".." in Path(member.name).parts
                or not (member.isdir() or member.isfile())
            ):
                raise ValueError("unsafe archive")
        tar.extractall(work)  # fixed SHA, checked members, Python3.10+
    code = work / f"pycdc-{SOURCE_COMMIT}"
    cmake = (code / "CMakeLists.txt").read_text(encoding="utf-8")
    files = re.search(r"add_library\(pycxx STATIC(.*?)\)", cmake, re.S).group(1).split()
    files += ["pycdc.cpp", "ASTree.cpp", "ASTNode.cpp"]
    objects = [work / (str(i) + ".obj") for i in range(len(files))]

    def compile_one(item):
        relative, obj = item
        subprocess.run(
            [
                *zig,
                "c++",
                "-target",
                "x86-windows-gnu",
                "-std=c++11",
                "-O2",
                "-I" + str(code),
                "-c",
                str(code / relative),
                "-o",
                str(obj),
            ],
            check=True,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        list(pool.map(compile_one, zip(files, objects, strict=True)))
    executable = work / "pycdc.exe"
    subprocess.run(
        [
            *zig,
            "c++",
            "-target",
            "x86-windows-gnu",
            "-O2",
            "-static",
            *map(str, objects),
            "-o",
            str(executable),
        ],
        check=True,
    )
    output.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(executable, output / "pycdc.exe")
    shutil.copyfile(code / "LICENSE", output / "LICENSE.txt")
    (output / "corresponding-source").mkdir()
    shutil.copyfile(source, output / "corresponding-source" / source.name)
    zig_home = Path(importlib.util.find_spec("ziglang").origin).parent
    notices = [
        "Windows x86 cross-build; Zig 0.13.0; static libc++/MinGW runtime.\n"
        "Not executed on Windows by the maintainer.\n"
        "Full pycdc sources: corresponding-source/" + source.name + "\n"
    ]
    for name in (
        "LICENSE",
        "lib/libc/mingw/COPYING",
        "lib/libcxx/LICENSE.TXT",
        "lib/libcxxabi/LICENSE.TXT",
        "lib/libunwind/LICENSE.TXT",
    ):
        path = zig_home / name
        if not path.is_file():
            raise ValueError("missing runtime notice " + name)
        notices.append(
            "\n===== " + name + " =====\n" + path.read_text(encoding="utf-8")
        )
    notices.append(
        "\n===== Complete build recipe (build_windows_recovery_engine.py) =====\n"
        + Path(__file__).read_text(encoding="utf-8")
    )
    raw = "\n".join(notices).encode("utf8")
    (output / "BUILD-NOTICES.txt").write_bytes(raw)
    manifest = dict(
        schema_version=1,
        platform="win32",
        executable="pycdc.exe",
        source_commit=SOURCE_COMMIT,
        source_sha256=SOURCE_SHA256,
        binary_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),
        build_notices_sha256=hashlib.sha256(raw).hexdigest(),
    )
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    print(
        json.dumps(
            build(args.work.absolute(), args.output.absolute(), args.jobs), indent=2
        )
    )
