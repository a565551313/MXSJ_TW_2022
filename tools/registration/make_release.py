#!/usr/bin/env python3
"""把已备好的发布目录打成可核对的 zip（含 SHA256SUMS 与哈希回显）。

存在的理由：出货包要给用户实机测试，校验清单错一位就会让人白跑一趟。
手工 `find | xargs sha256sum > SHA256SUMS.txt` 会把**空文件自己**也算进去
（重定向先建文件），那份哈希永远校验不过——2026-10-15 的两颗已出货包就踩过，
本工具固定按「排除自身 + 名称排序 + 固定时间戳」生成，产出可复现。

用法：
    python3 tools/registration/make_release.py --stage <目录> --zip <输出.zip>
    python3 tools/registration/make_release.py --check <已经打好的.zip>
"""

from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path

SUMS_NAME = "SHA256SUMS.txt"
# ZIP 规范不支持 1980 年前的时间戳；钉死它，同一份内容两次打包才逐字节相同。
FIXED_ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def list_members(stage: Path) -> list[Path]:
    """返回相对 stage 的文件（排序、排除校验清单本身）。"""
    names = sorted(
        p.relative_to(stage).as_posix()
        for p in stage.rglob("*")
        if p.is_file() and p.name != SUMS_NAME
    )
    return [Path(name) for name in names]


def write_sums(stage: Path, members: list[Path]) -> Path:
    lines = [
        f"{sha256_file(stage / rel)}  {rel.as_posix()}"
        for rel in members
    ]
    path = stage / SUMS_NAME
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path


def build_zip(stage: Path, out: Path) -> list[str]:
    members = list_members(stage)
    if not members:
        raise SystemExit(f"{stage} 里没有可打包的文件")
    write_sums(stage, members)
    names = [rel.as_posix() for rel in members] + [SUMS_NAME]
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, (stage / name).read_bytes())
    return names


def check_zip(out: Path) -> dict[str, str]:
    """按包内 SHA256SUMS.txt 逐条核对（同时 zipfile 自身会验 CRC）。"""
    with zipfile.ZipFile(out) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise SystemExit(f"ZIP 内部 CRC 失败：{bad}")
        if SUMS_NAME not in archive.namelist():
            raise SystemExit(f"{out} 缺少 {SUMS_NAME}，不能交付")
        text = archive.read(SUMS_NAME).decode("utf-8")
        expected = {}
        for line in text.splitlines():
            if not line.strip():
                continue
            digest, _, name = line.partition("  ")
            expected[name.strip()] = digest.strip()
        if SUMS_NAME in expected:
            raise SystemExit(f"{SUMS_NAME} 把自己也算进去了（自指哈希无法校验）")
        actual = {
            info.filename: sha256_bytes(archive.read(info.filename))
            for info in archive.infolist()
            if not info.is_dir() and info.filename != SUMS_NAME
        }
        if set(expected) != set(actual):
            missing = sorted(set(expected) ^ set(actual))
            raise SystemExit(f"清单与包内文件不一致：{missing}")
        for name, digest in sorted(expected.items()):
            if digest != actual[name]:
                raise SystemExit(f"内容不符：{name}")
    return expected


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=Path, help="已备好的发布目录")
    ap.add_argument("--zip", type=Path, help="输出的 zip 路径")
    ap.add_argument("--check", type=Path, help="只核对一个已打好的 zip")
    args = ap.parse_args()

    if args.check:
        files = check_zip(args.check)
        raw = args.check.read_bytes()
        print(
            f"[+] {args.check.name}: {len(raw)} 字节，"
            f"sha256={sha256_bytes(raw)} md5={hashlib.md5(raw).hexdigest()}"
        )
        print(f"[+] {SUMS_NAME} 全部 {len(files)} 条校验通过（含 CRC）")
        return 0

    if not args.stage or not args.zip:
        raise SystemExit("打包需要 --stage 与 --zip（核对用 --check）")
    if args.zip.resolve().is_relative_to(args.stage.resolve()):
        raise SystemExit("zip 不能写在待打包的目录里，否则会把自身打进去")
    names = build_zip(args.stage, args.zip)
    check_zip(args.zip)
    raw = args.zip.read_bytes()
    print(f"[+] 成员 {len(names)} 个：")
    for name in names:
        print(f"    {name}")
    print(
        f"[+] wrote {args.zip} ({len(raw)} bytes) "
        f"sha256={sha256_bytes(raw)} md5={hashlib.md5(raw).hexdigest()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
