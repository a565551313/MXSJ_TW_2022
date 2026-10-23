"""按仓库原样重写 runtimes/，修复 Git 换行转换造成的 SHA256 不匹配。

Windows 版 Git 若开启 core.autocrlf，会把 BUILD.json、许可等文本文件从 LF 改成
CRLF，自检就报「runtime文件SHA256不匹配：BUILD.json」。本脚本只对
script_editor/runtimes 做一次不转换换行的 git checkout，然后重新逐文件校验；
不改动其它文件、不改 Git 全局配置、不下载任何东西。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
VMS = ("py25", "py27")


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )


def _verify() -> str | None:
    """用编辑器自己的清单校验器重算一遍；通过返回 None。"""
    sys.path.insert(0, str(HERE / "src"))
    from script_editor.core.compiler.bundles import BundleError, load_bundle

    for vm in VMS:
        try:
            load_bundle(vm, HERE).verify()
        except BundleError as exc:
            return str(exc)
    return None


def main() -> int:
    print("正在按仓库原样重写 runtimes（不改动其它文件）……")
    if not (REPO / ".git").exists():
        print(f"[错误] 上一层不是 Git 仓库根目录：{REPO}")
        print("请把本工具放回 script_editor 文件夹再运行。")
        return 1
    probe = _git("rev-parse", "--is-inside-work-tree")
    if probe.returncode or probe.stdout.strip() != "true":
        print("[错误] 找不到可用的 git 命令。请安装 Git 并加入 PATH。")
        return 1
    checkout = _git(
        "-c", "core.autocrlf=false", "checkout", "--", "script_editor/runtimes"
    )
    if checkout.returncode:
        print("[错误] 还原失败。请先在仓库根目录 git pull 到最新，再运行本工具。")
        detail = (checkout.stderr or checkout.stdout).strip()
        if detail:
            print(detail)
        return 1
    problem = _verify()
    if problem:
        print(f"[失败] 还原后仍不一致：{problem}")
        print("请先 git pull 到最新；仍不行就把这行文字发给维护者。")
        return 2
    print("[通过] 两套编译器的 20 个文件与 manifest.json 完全一致。")
    print("现在双击 检查内置编译器.bat 复查，预期 windows-runtime-smoke-passed。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
