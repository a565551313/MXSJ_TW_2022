"""Build the optional standalone pycdc from included, SHA-pinned GPL-3.0 source."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
from script_editor.core.services.pycdc_engine import (  # noqa: E402
    SOURCE_COMMIT,
    SOURCE_SHA256,
)


def build(output):
    source = HERE / "third_party" / f"pycdc-{SOURCE_COMMIT}.tar.gz"
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("pycdc source archive SHA256 mismatch")
    if output.exists() or output.is_symlink():
        raise ValueError("output already exists; choose a new directory")
    cmake = shutil.which("cmake")
    if cmake is None:
        raise ValueError(
            "CMake required: install cmake; also provide a native C++ compiler"
        )
    with tempfile.TemporaryDirectory(prefix="mx-build-pycdc-") as temporary:
        root = Path(temporary)
        with tarfile.open(source) as archive:
            members = archive.getmembers()
            for member in members:
                path = Path(member.name)
                if (
                    path.is_absolute()
                    or ".." in path.parts
                    or not (member.isfile() or member.isdir())
                ):
                    raise ValueError("unsafe source archive member")
            archive.extractall(root, members=members)  # checked source; Python 3.10+
        code = root / f"pycdc-{SOURCE_COMMIT}"
        build_dir = root / "build"
        subprocess.run(
            [
                cmake,
                "-S",
                str(code),
                "-B",
                str(build_dir),
                "-DCMAKE_BUILD_TYPE=Release",
            ],
            check=True,
        )
        subprocess.run(
            [
                cmake,
                "--build",
                str(build_dir),
                "--config",
                "Release",
                "--target",
                "pycdc",
                "--parallel",
                "2",
            ],
            check=True,
        )
        name = "pycdc.exe" if os.name == "nt" else "pycdc"
        paths = [build_dir / name, build_dir / "Release" / name]
        executable = next((p for p in paths if p.is_file()), None)
        if executable is None:
            raise ValueError("CMake did not produce the expected executable")
        binary = executable.read_bytes()
        output.mkdir(parents=True, exist_ok=False)
        with (output / name).open("xb") as stream:
            stream.write(binary)
        (output / name).chmod(0o700)
        license_file = next(
            (p for p in code.iterdir() if p.name.lower() in {"license", "license.txt"}),
            None,
        )
        if license_file is None:
            raise ValueError("missing upstream GPL-3.0 license")
        shutil.copyfile(license_file, output / "LICENSE.txt")
        corresponding = output / "corresponding-source"
        corresponding.mkdir()
        shutil.copyfile(source, corresponding / source.name)
        manifest = {
            "schema_version": 1,
            "platform": sys.platform,
            "executable": name,
            "source_commit": SOURCE_COMMIT,
            "source_sha256": SOURCE_SHA256,
            "binary_sha256": hashlib.sha256(binary).hexdigest(),
        }
        with (output / "manifest.json").open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(manifest, indent=2) + "\n")
        return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))


if __name__ == "__main__":
    main()
