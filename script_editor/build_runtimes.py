"""Maintainer-only reproducible compiler build; shipped ZIP already contains it.

Build official CPython core source lists for Windows x86 using Zig 0.13.0.
Only Windows/MinGW compatibility guards are patched; compiler, opcode and
marshal implementations are untouched. No game DLL/source/module is consumed.
Install ziglang==0.13.0 in a separate build environment, then invoke this file.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

SOURCES = {
    "2.5.6": (
        "11a859d70dffc8da51d346dabd1fe6a635825ae5",
        "c68b9e84e9a302d120e5ec3ada6ef9fceb84d7768cea63dedb3074c6ed47bcfa",
    ),
    "2.7.13": (
        "9c1426de7521299f70eb5483e7e25d1c2a73dbbd",
        "ae1dc735e2990bf8de8e73c3f77b35d4f69502570957c743a7e8618a652fe08a",
    ),
}


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def source_tree(work, version):
    url = f"https://codeload.github.com/python/cpython/tar.gz/refs/tags/v{version}"
    archive = work / f"{version}.tgz"
    with urllib.request.urlopen(url, timeout=90) as response, archive.open("xb") as f:
        shutil.copyfileobj(response, f)
    if sha(archive) != SOURCES[version][1]:
        raise ValueError("Official source archive SHA256 mismatch")
    with tarfile.open(archive) as tar:
        prefix = f"cpython-{version}/"
        for member in tar:
            if member.isdir() and member.name == prefix.rstrip("/"):
                continue
            if not member.name.startswith(prefix):
                raise ValueError("Source archive root mismatch")
            parts = Path(member.name).parts
            if ".." in parts or member.issym() or member.islnk():
                raise ValueError("Unsafe source archive member")
            target = work / member.name
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as src, target.open("xb") as dst:
                    shutil.copyfileobj(src, dst)
    return work / f"cpython-{version}", url


def patch_platform(source, version):
    patches = []
    for relative in (
        "Modules/posixmodule.c",
        "Python/dynload_win.c",
        "Modules/signalmodule.c",
    ):
        path = source / relative
        old = path.read_bytes()
        text = old.decode("utf-8")
        if relative.endswith("posixmodule.c"):
            text = text.replace(
                "#ifndef _MSC_VER", "#if !defined(_MSC_VER) && !defined(__MINGW32__)"
            )
            text = text.replace(
                "#ifdef _MSC_VER", "#if defined(_MSC_VER) || defined(__MINGW32__)"
            )
            text = text.replace(
                "defined(_MSC_VER) || defined(__WATCOMC__) || defined(__BORLANDC__)",
                "defined(_MSC_VER) || defined(__MINGW32__) || "
                "defined(__WATCOMC__) || defined(__BORLANDC__)",
            )
        elif relative.endswith("dynload_win.c"):
            text = text.replace("strcasecmp", "pybuild_strcasecmp")
        elif version == "2.7.13":
            text = text.replace("<Windows.h>", "<windows.h>")
        new = text.encode("utf-8")
        if new != old:
            path.write_bytes(new)
            patches.append(
                {
                    "path": relative,
                    "before_sha256": hashlib.sha256(old).hexdigest(),
                    "after_sha256": sha(path),
                }
            )
    return patches


def build_one(work, source, version, jobs):
    output = work / f"win-{version}"
    output.mkdir()
    zig = [sys.executable, "-m", "ziglang", "cc", "-target", "x86-windows-gnu"]
    flags = [
        "-std=gnu89",
        "-O2",
        "-fno-strict-aliasing",
        "-fwrapv",
        "-Wno-everything",
        "-DWIN32",
        "-DMS_WINDOWS",
        "-DNDEBUG",
        "-DUSE_DL_EXPORT",
    ]
    flags += [
        "-I" + str(source / p)
        for p in ("PC", "Include", "Modules/zlib", "Modules/_io", "Python")
    ]
    project = source / (
        "PCbuild/pythoncore.vcproj"
        if version == "2.5.6"
        else "PCbuild/pythoncore.vcxproj"
    )
    sources = []
    for element in ET.parse(project).iter():
        name = element.get("RelativePath") or element.get("Include") or ""
        if name.lower().endswith(".c"):
            name = name.replace("\\", "/").replace("../Pc/", "../PC/")
            sources.append((source / "PCbuild" / name).resolve(strict=True))
    if version == "2.5.6":
        sources.append(source / "Modules/getbuildinfo.c")

    def compile_one(path):
        obj = output / f"{path.parent.name}-{path.stem}.o"
        args = zig + flags + ["-c", str(path), "-o", str(obj)]
        result = subprocess.run(
            args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180
        )
        (output / (obj.stem + ".log")).write_bytes(result.stdout)
        if result.returncode:
            raise ValueError(f"Compilation failed for {path}; see {output}")
        return str(obj)

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        objects = list(pool.map(compile_one, sources))
    suffix = "25" if version == "2.5.6" else "27"
    subprocess.run(
        zig
        + [
            "-shared",
            *objects,
            "-o",
            str(output / f"python{suffix}.dll"),
            "-Wl,--out-implib," + str(output / "python.lib"),
            "-lws2_32",
            "-ladvapi32",
            "-lshell32",
            "-luser32",
            "-luuid",
        ],
        check=True,
        timeout=180,
    )
    exe_flags = [flag for flag in flags if flag != "-DUSE_DL_EXPORT"]
    subprocess.run(
        zig
        + exe_flags
        + [
            str(source / "Modules/python.c"),
            str(output / "python.lib"),
            "-o",
            str(output / "python.exe"),
        ],
        check=True,
        timeout=180,
    )
    print(
        f"{version}: built {len(objects)} official core translation units", flush=True
    )
    return output


def package_one(destination, source, binary, version, url, patches, zig_home):
    suffix = "25" if version == "2.5.6" else "27"
    vm = "py" + suffix
    root = destination / vm / "win-x86"
    root.mkdir(parents=True)
    for name in ("python.exe", f"python{suffix}.dll"):
        shutil.copyfile(binary / name, root / name)
    with zipfile.ZipFile(
        root / f"python{suffix}.zip", "w", compression=zipfile.ZIP_STORED
    ) as archive:
        for path in sorted((source / "Lib").rglob("*.py")):
            relative = path.relative_to(source / "Lib")
            if set(relative.parts) & {"test", "tests", "lib-tk", "idlelib"}:
                continue
            info = zipfile.ZipInfo(
                relative.as_posix(), date_time=(2026, 10, 15, 0, 0, 0)
            )
            archive.writestr(info, path.read_bytes())
    license_files = {
        "CPython": (source / "LICENSE", "LICENSE-CPython.txt"),
        "Zig": (zig_home / "LICENSE", "LICENSE-Zig.txt"),
        "MinGW-w64 CRT": (zig_home / "lib/libc/mingw/COPYING", "LICENSE-MinGW.txt"),
        "LLVM runtime": (zig_home / "lib/libunwind/LICENSE.TXT", "LICENSE-LLVM.txt"),
        "zlib": (source / "Modules/zlib/README", "LICENSE-zlib.txt"),
    }
    licenses = []
    for component, (path, name) in license_files.items():
        shutil.copyfile(path, root / name)
        licenses.append({"component": component, "path": name})
    build = {
        "toolchain": "Zig 0.13.0; x86-windows-gnu; compiler-only CPython",
        "target_os": "Windows 10/11 (system UCRT)",
        "source_patches": patches,
        "compiler_marshal_opcode_source": "unmodified official CPython",
        "native_windows_execution": "must be verified separately",
    }
    (root / "BUILD.json").write_text(json.dumps(build, indent=2), encoding="utf-8")
    return {
        "vm": vm,
        "platform": "win32",
        "version": version,
        "bits": 32,
        "magic": "b3f20d0a" if suffix == "25" else "03f30d0a",
        "root": f"{vm}/win-x86",
        "executable": f"{vm}/win-x86/python.exe",
        "source": {
            "url": url,
            "revision": SOURCES[version][0],
            "archive_sha256": SOURCES[version][1],
        },
        "licenses": licenses,
        "files": {p.name: sha(p) for p in sorted(root.iterdir())},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work", type=Path, required=True, help="New work directory, must not exist"
    )
    parser.add_argument(
        "--destination", type=Path, required=True, help="New runtimes directory"
    )
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args(argv)
    if not 1 <= args.jobs <= 16:
        parser.error("--jobs must be between 1 and 16")
    spec = importlib.util.find_spec("ziglang")
    if spec is None:
        parser.error(
            "Maintainer rebuild needs ziglang==0.13.0; normal users need not rebuild"
        )
    tool = subprocess.check_output(
        [sys.executable, "-m", "ziglang", "version"], text=True
    ).strip()
    if tool != "0.13.0":
        parser.error("Only pinned Zig 0.13.0 is accepted")
    if args.destination.exists():
        parser.error("Destination already exists; refusing to replace it")
    args.work = args.work.absolute()
    args.destination = args.destination.absolute()
    args.work.mkdir(parents=True, exist_ok=False)
    if hasattr(os, "sched_setaffinity"):
        os.sched_setaffinity(0, set(sorted(os.sched_getaffinity(0))[: args.jobs]))
    results = []
    for version in SOURCES:
        source, url = source_tree(args.work, version)
        patches = patch_platform(source, version)
        binary = build_one(args.work, source, version, args.jobs)
        results.append((source, binary, version, url, patches))
    args.destination.mkdir(parents=True, exist_ok=False)
    items = [
        package_one(args.destination, *result, Path(spec.origin).parent)
        for result in results
    ]
    (args.destination / "manifest.json").write_text(
        json.dumps({"schema": 2, "compilers": items}, indent=2), encoding="utf-8"
    )
    print(
        f"Built real Windows x86 compilers at {args.destination}; "
        "execution verification is separate."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
