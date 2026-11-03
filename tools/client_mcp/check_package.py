"""双击检查：仓库里的 data/script.fls 到底是哪一个包。

只读，不改任何文件。用法：双击同目录 ``检查当前客户端包.bat``。

输出刻意写得非常直白：一句话结论 + 游戏能不能启动 + 会不会写报告。
"""

from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
DEFAULT_PACKAGE = REPO_ROOT / "data" / "script.fls"
MASK = 0xFFFFFFFF

# 历史出现过、并且可能被误认的包。值为 (一句话名字, 游戏能否启动, 是否写报告)。
KNOWN_PACKAGES = {
    "e25f2bae01e94f2c48c4bf06bf5161a982ed5bcb36a15d5a9508c838a6076ecb": (
        "常驻探针版 —— 当前版本，启动后每秒刷新报告",
        "能启动（全部包在 try/except 里）",
        "会写报告，并每秒更新（真正的存活心跳）",
    ),
    "7ebcbac7a0fe5e0f7fa0a444e6069158df33dff045e4f876d2f76a4d767622dd": (
        "初版钩子 —— 只在启动时写一次报告",
        "能启动",
        "会写一次报告，之后不再更新",
    ),
    "1d6b21529e8fc651f5a1af18788090f7e61955914f2a1d00cd8c655b3ea3074a": (
        "无钩子版 —— 加钩子之前你在 Windows 上用的那个",
        "能启动",
        "不会写报告",
    ),
    "068b4972050af4ffa98bf74016c5b97c66ac939e748ac991c1eb0f196da24dcf": (
        "受保护钩子版（当时做过，但没在你机器上验证通过）",
        "未验证",
        "应该会写报告",
    ),
    "585040f9417ad8199d925a1fe3979891cf9d24e4c341c2cab7ecbd04fc547048": (
        "修复中间产物（已作废）",
        "未验证",
        "不会写报告",
    ),
    "2914a4edfb4adb33f0661bba1297a827ebdc055b788673a9e25717b563f61a3d": (
        "坏包（启动会报错，已作废）",
        "不能启动",
        "不会写报告",
    ),
    "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72": (
        "原始基线（5002 条，没有探针）",
        "能启动",
        "不会写报告",
    ),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def check_structure(path: Path) -> tuple[int, list[str]]:
    """Return (entry_count, problems) after a read-only 0SLF walk."""
    problems: list[str] = []
    size = path.stat().st_size
    with path.open("rb") as stream:
        header = stream.read(12)
        if len(header) != 12 or header[:4] != b"0SLF":
            return 0, ["文件开头不是 0SLF，不是脚本包"]
        count, directory = struct.unpack_from("<II", header, 4)
        if not 0 < count <= 1_000_000:
            problems.append(f"条目数不合理：{count}")
            return count, problems
        if directory < 12 or directory + count * 16 > size:
            problems.append("目录位置超出文件范围")
            return count, problems
        stream.seek(directory)
        records = stream.read(count * 16)
    if len(records) != count * 16:
        problems.append("目录被截断")
        return count, problems
    previous = None
    out_of_bounds = 0
    for index, (entry_id, r1, r2, r3) in enumerate(
        struct.iter_unpack("<IIII", records)
    ):
        if previous is not None and entry_id <= previous:
            problems.append("目录没有按 ID 升序排（客户端可能找不到条目）")
            break
        previous = entry_id
        length = (((r1 * entry_id + 0x0DF25E) & MASK) ^ r2) & MASK
        offset = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK) ^ r3) & MASK
        if offset > size or length > size - offset:
            out_of_bounds += 1
    if out_of_bounds:
        problems.append(f"{out_of_bounds} 条载荷越界（目录长度字是错的）")
    return count, problems


def inspect(path: Path | str = DEFAULT_PACKAGE) -> dict:
    """Collect everything the window needs; never raises for a missing file."""
    package = Path(path)
    if not package.is_file():
        return {"exists": False, "path": package}
    digest = _sha256(package)
    count, problems = check_structure(package)
    label, starts, reports = KNOWN_PACKAGES.get(
        digest, ("未知包 —— 不是我给过你的任何一个版本", "不确定", "不确定")
    )
    return {
        "exists": True,
        "path": package,
        "size": package.stat().st_size,
        "sha256": digest,
        "known": digest in KNOWN_PACKAGES,
        "label": label,
        "starts": starts,
        "reports": reports,
        "entry_count": count,
        "problems": problems,
    }


def render(info: dict) -> str:
    line = "=" * 60
    if not info["exists"]:
        return "\n".join(
            [
                line,
                " 没有找到 data/script.fls",
                f" 预期位置：{info['path']}",
                " 说明仓库不完整，请把这张截图发给开发者。",
                line,
            ]
        )
    rows = [
        line,
        " 当前客户端包检查",
        "-" * 60,
        f" 文件：{info['path']}",
        f" 大小：{info['size']:,} 字节",
        f" SHA-256：{info['sha256']}",
        "",
        f" 结论：{info['label']}",
        f" 游戏：{info['starts']}",
        f" 报告：{info['reports']}",
        "",
    ]
    if info["problems"]:
        rows.append(" 包结构有问题：")
        rows.extend(f"   - {item}" for item in info["problems"])
    else:
        rows.append(f" 包结构：正常（{info['entry_count']} 条，目录没有越界）")
    if not info["known"]:
        rows.append("")
        rows.append(" 这个包我不认识，请把这张窗口截图发给开发者。")
    rows.append(line)
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    target = Path(args[0]) if args else DEFAULT_PACKAGE
    info = inspect(target)
    print(render(info))
    if not info["exists"]:
        return 2
    return 0 if info["known"] and not info["problems"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
