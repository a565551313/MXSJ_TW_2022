"""按清单重写 runtimes/ 的文本文件，修复换行转换造成的 SHA256 不匹配。

Windows 版 Git（以及 GitHub Desktop 自带的那个 git）在 core.autocrlf 打开时会把
文本文件从 LF 改成 CRLF：`BUILD.json` 由 734 B 变 751 B。清单钉的是 LF 版本的
SHA256，于是自检报「runtime文件SHA256不匹配：BUILD.json」。

本脚本**不调用 git、不联网**：逐个文件算 SHA256，若与清单不符、且「去掉多余回车
后」恰好等于清单值，就写回 LF 版本——哈希相等本身就是恢复正确的证明；仍不符则
原样保留并点名，绝不猜测或覆盖。最后用编辑器自己的校验器复核一遍。
只改动 `runtimes/` 内的文件，不动其它任何东西，也不改 Git 配置。
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VMS = ("py25", "py27")


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_manifest(runtimes: Path) -> dict:
    return json.loads((runtimes / "manifest.json").read_bytes().decode("utf-8-sig"))


def _entries(manifest: dict):
    """展开清单：每项 yield (root, 相对文件名, 期望 SHA256)。"""
    compilers = manifest.get("compilers")
    if not isinstance(compilers, list):
        raise ValueError("manifest.json 缺少 compilers 列表")
    for compiler in compilers:
        root = compiler.get("root")
        files = compiler.get("files")
        if not isinstance(root, str) or not isinstance(files, dict):
            raise ValueError("manifest.json 条目缺少 root/files")
        for name, expected in files.items():
            if not isinstance(name, str) or not isinstance(expected, str):
                raise ValueError("manifest.json 的 files 不是名字到 SHA256 的映射")
            yield root, name, expected


def repair_files(runtimes: Path) -> tuple[list[str], list[str], list[str]]:
    """按清单校字节。

    返回 (已修复, 本来就一致, 无法修复) 三组可读路径。只有「去掉 CR 后哈希恰好
    等于清单值」的文件才会被写回；其余一律不动，交给调用方报告。
    """
    fixed: list[str] = []
    intact: list[str] = []
    broken: list[str] = []
    for root, name, expected in _entries(_load_manifest(runtimes)):
        label = f"{root}/{name}"
        path = runtimes / root / name
        if not path.is_file():
            broken.append(f"{label}：文件不存在")
            continue
        data = path.read_bytes()
        if _digest(data) == expected:
            intact.append(label)
            continue
        candidate = data.replace(b"\r\n", b"\n")
        if candidate != data and _digest(candidate) == expected:
            path.write_bytes(candidate)
            fixed.append(label)
            continue
        broken.append(f"{label}：内容与清单不符，且不属于换行转换")
    return fixed, intact, broken


def _verify(root: Path) -> str | None:
    """用编辑器自己的清单校验器复核；通过返回 None。"""
    sys.path.insert(0, str(root / "src"))
    from script_editor.core.compiler.bundles import BundleError, load_bundle

    for vm in VMS:
        try:
            load_bundle(vm, root).verify()
        except BundleError as exc:
            return str(exc)
    return None


def main() -> int:
    runtimes = HERE / "runtimes"
    if not (runtimes / "manifest.json").is_file():
        print(f"[错误] 找不到清单：{runtimes / 'manifest.json'}")
        print("请把本工具放回 script_editor 文件夹（与 src 同级）再运行。")
        return 1
    print("正在按清单核对 runtimes 的字节（不需要 git，不联网）……")
    try:
        fixed, intact, broken = repair_files(runtimes)
    except (OSError, ValueError) as exc:
        print(f"[错误] 清单读取失败：{exc}")
        return 1
    for label in fixed:
        print(f"  已修复换行：{label}")
    if broken:
        print("[失败] 以下文件无法按清单复原，未做任何覆盖：")
        for line in broken:
            print(f"  {line}")
        print("请重新获取完整仓库（GitHub Desktop 里 Fetch origin 后 Pull）。")
        return 2
    problem = _verify(HERE)
    if problem:
        print(f"[失败] 复核仍未通过：{problem}")
        return 2
    if fixed:
        print(f"[通过] 修复了 {len(fixed)} 个文件；两套编译器与清单完全一致。")
    else:
        print(f"[通过] {len(intact)} 个文件本来就一致，无需修复。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
