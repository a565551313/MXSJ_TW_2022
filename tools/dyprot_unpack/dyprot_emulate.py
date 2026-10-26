#!/usr/bin/env python3
"""在 Unicorn 裡跑 mxmain.dll 的 `DuoyiProtect` 入口，觀察它做了什麼。

**狀態：實驗性，尚未解出載荷。** 這個工具目前能穩定做到：

1. 按 `ImageBase` 映射整個 `SizeOfImage`，把 TEB/PEB 放在位址 0
   （unicorn 的 32 位模式忽略 `FS` 段基址，`fs:[x]` 實際讀 `[x]`）；
2. 給 859 個導入槽接上 Python 樁，並合成 kernel32 / ntdll / user32 /
   advapi32 的**假 PE 映像**（含可解析的匯出表）——殼是走「解析匯出表」
   這條路拿 API 的，不給它表它不往下走；
3. 從 PE 入口跑到指令／時間預算用完，記錄呼叫了哪些 API、有沒有回頭改寫
   映像、以及失控時停在哪。

實測（`mxmain.dll`，`637331b5…`）：殼會把 **859/896 個 IAT 槽重綁**到假匯出表
的位址（整張 IAT 有 3,430 個位元組被改寫，其餘映像零改動），之後**沒有解密任何載荷**
（`.data` 運行期尾部 `0x93C180` 仍是 0），最終跳進未映射位址。所以本工具
現在的價值是**證偽與定位**（殼要什麼環境、卡在哪一步），不是脫殼成品。

邊界：只讀 `mxmain.dll`、不載入 Windows DLL、不調用系統、不連網、不寫原檔；
`--json` / `--snapshot` 的目標路徑不許指向輸入映像。
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import struct
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

try:  # 可選依賴，缺了要給人能看懂的提示，而不是 ImportError 堆疊
    import pefile
    from unicorn import (
        UC_ARCH_X86,
        UC_HOOK_CODE,
        UC_HOOK_MEM_WRITE,
        UC_MODE_32,
        UC_PROT_ALL,
        Uc,
        UcError,
    )
    from unicorn.x86_const import (
        UC_X86_REG_EAX,
        UC_X86_REG_EIP,
        UC_X86_REG_ESP,
    )
except ImportError as exc:  # pragma: no cover - 取決於環境
    sys.stderr.write(
        f"需要 pefile 與 unicorn（見 tools/DEPENDENCIES.md）：{exc}\n"
        "  python -m pip install pefile==2024.8.26 unicorn==2.1.4\n"
    )
    raise SystemExit(2) from exc

class UnknownArity(Exception):
    """碰到既沒實作、也不在 `ARG_COUNTS` 裡的導入名——補表再跑。"""

    def __init__(self, name: str):
        super().__init__(name)
        self.name = name


@dataclass
class Result:
    image: str = ""
    sha256: str = ""
    imports: int = 0
    exports: int = 0
    calls: dict = field(default_factory=dict)
    unimplemented: dict = field(default_factory=dict)
    stopped: str = ""
    eip: int = 0
    seconds: float = 0.0
    changed_regions: list = field(default_factory=list)
    rebinding: dict = field(default_factory=dict)


class Runtime:
    """一個夠殼跑起來的 i386 Windows-lite 執行環境（只做記憶體與 API 語意）。"""

    def __init__(self, image: Path):
        self.path = Path(image)
        self.pe = pefile.PE(str(self.path), fast_load=False)
        self.uc = Uc(UC_ARCH_X86, UC_MODE_32)
        self.calls: collections.Counter = collections.Counter()
        self.unimplemented: collections.Counter = collections.Counter()
        self.writes: collections.Counter = collections.Counter()
        self.writes_total = 0
        self._heap_ptr = HEAP
        self._next_stub = STUB + 0x20000
        self.slot_of: dict[int, str] = {}
        self.name_addr: dict[str, int] = {}
        self.procs: dict[str, object] = {}
        self.raw = self.path.read_bytes()
        self._map_image()
        self._install_hooks()
        self.import_count = 0
        self.exports: dict[str, int] = {}
        self.generic = STUB + 0x3FFF0

    def prepare(self) -> Runtime:
        """先裝 API 實作，再造假匯出表、綁導入——順序不能顛倒。"""
        install_api(self)
        self._install_fake_modules()
        self._bind_imports()
        return self

    # ---------------------------------------------------------------- 記憶體
    def _map_image(self) -> None:
        uc = self.uc
        size = (self.pe.OPTIONAL_HEADER.SizeOfImage + 0xFFF) & ~0xFFF
        self.original = bytes(self.pe.get_memory_mapped_image())
        uc.mem_map(BASE, size, UC_PROT_ALL)
        uc.mem_write(BASE, self.original)
        # unicorn 32 位忽略 FS 基址 → 把 TEB/PEB 放到 0，讓 fs:[0x30] 讀得到
        uc.mem_map(0, 0x10000, UC_PROT_ALL)
        uc.mem_map(STACK, STACK_SIZE, UC_PROT_ALL)
        uc.mem_map(HEAP, HEAP_SIZE, UC_PROT_ALL)
        uc.mem_map(STUB, STUB_SIZE, UC_PROT_ALL)
        uc.mem_write(STUB, b"\xC3" * STUB_SIZE)
        uc.mem_write(0x00, struct.pack("<I", SENTINEL))  # SEH 鏈尾
        uc.mem_write(0x04, struct.pack("<I", STACK + STACK_SIZE))
        uc.mem_write(0x08, struct.pack("<I", STACK))
        uc.mem_write(0x18, struct.pack("<I", 0))  # TEB->Self（放在 0 就是 0）
        uc.mem_write(0x30, struct.pack("<I", PEB))
        uc.mem_write(PEB + 0x08, struct.pack("<I", BASE))
        uc.mem_write(PEB + 0x18, struct.pack("<I", HEAP))
        uc.mem_write(PEB + 0x20, struct.pack("<I", 1))

    def alloc(self, size: int, align: int = 16) -> int:
        size = max(int(size), 1)
        addr = self._heap_ptr
        self._heap_ptr = (addr + size + align - 1) & ~(align - 1)
        if self._heap_ptr > HEAP + HEAP_SIZE:
            raise RuntimeError("fake heap exhausted")
        return addr

    def read_str(self, addr: int, wide: bool = False) -> str:
        if not addr:
            return ""
        out = bytearray()
        step, zero = (2, b"\x00\x00") if wide else (1, b"\x00")
        while True:
            chunk = bytes(self.uc.mem_read(addr, step))
            if chunk == zero:
                break
            out += chunk
            addr += step
            if len(out) > 512:
                break
        return bytes(out).decode("utf-16-le" if wide else "latin-1", "replace")

    # ------------------------------------------------------------ 假 DLL 映像
    def stub_for(self, name: str) -> int:
        if name not in self.name_addr:
            addr = self._next_stub
            self._next_stub += 0x10
            self.name_addr[name] = addr
            self.slot_of[addr] = name
        return self.name_addr[name]

    def _install_fake_modules(self) -> None:
        # 匯出表要把「這個映像自己導入的每一個名字」都擺進去：殼是拿名字去
        # 匯出表裡查的，查不到就只能拿到通用樁，行為會跟真的 Windows 不同。
        names = set(EXTRA_EXPORTS) | set(self.procs) | set(self._imported_names())
        for name in sorted(names):
            self.stub_for(name)
        self.exports = {n: self.name_addr[n] for n in self.name_addr}
        self.generic = self._next_stub
        self._next_stub += 0x10
        for dll, base in MODULE_BASE.items():
            self._write_module(base, dll)

    def _write_module(self, base: int, dll: str) -> None:
        image = build_module(dll, self.exports, self.generic)
        try:
            self.uc.mem_map(base, (len(image) + 0xFFF) & ~0xFFF, UC_PROT_ALL)
        except UcError:
            pass
        self.uc.mem_write(base, image)

    def module_base(self, dll: str) -> int:
        key = dll.lower()
        if key not in MODULE_BASE:
            MODULE_BASE[key] = 0x54000000 + 0x20000 * len(MODULE_BASE)
        base = MODULE_BASE[key]
        self._write_module(base, key)
        return base

    # ------------------------------------------------------------------ API
    def _register(self, fn_name: str, fn, argc: int | None = None) -> None:
        if argc is not None:
            fn.argc = argc
        self.procs[fn_name] = fn

    def _imported_names(self) -> list[str]:
        out = []
        for entry in self.pe.DIRECTORY_ENTRY_IMPORT:
            for imp in entry.imports:
                if imp.name:
                    out.append(imp.name.decode("latin-1"))
        return out

    # -------------------------------------------------------------- 導入綁定
    def _bind_imports(self) -> None:
        count = 0
        for entry in self.pe.DIRECTORY_ENTRY_IMPORT:
            for imp in entry.imports:
                name = (
                    imp.name.decode("latin-1")
                    if imp.name
                    else f"ord_{imp.ordinal}"
                )
                self.uc.mem_write(imp.address, struct.pack("<I", self.stub_for(name)))
                count += 1
        self.import_count = count

    # ------------------------------------------------------------------ 鉤子
    def _install_hooks(self) -> None:
        self.uc.hook_add(
            UC_HOOK_CODE, self._on_code, begin=STUB, end=STUB + STUB_SIZE
        )
        self.uc.hook_add(UC_HOOK_MEM_WRITE, self._on_write)

    def _on_write(self, uc, access, address, size, value, user) -> None:
        self.writes_total += 1
        self.writes[address & ~0xFFFF] += 1

    def _on_code(self, uc, address, size, user) -> None:
        if not STUB <= address < STUB + STUB_SIZE:
            return
        name = self.slot_of.get(address)
        if name is None:
            return
        self.calls[name] += 1
        esp = uc.reg_read(UC_X86_REG_ESP)
        ret = struct.unpack("<I", uc.mem_read(esp, 4))[0]
        fn = self.procs.get(name)
        argc = getattr(fn, "argc", None) if fn else ARG_COUNTS.get(name)
        if argc is None:
            # 不知道參數個數就清不了棧；靠猜只會讓後面全部歪掉，寧可停下來報名字。
            raise UnknownArity(name)
        if fn is None:
            self.unimplemented[name] += 1
            uc.reg_write(UC_X86_REG_EAX, 0)
            uc.reg_write(UC_X86_REG_ESP, esp + 4 + 4 * argc)
            uc.reg_write(UC_X86_REG_EIP, ret)
            return
        args = struct.unpack("<" + "I" * argc, uc.mem_read(esp + 4, 4 * argc))
        try:
            value = fn(*args)
        except ProcessExit:
            raise
        except Exception as exc:  # 樁壞掉不該炸掉整個 run，記錄下來回 0
            self.unimplemented[f"{name}(error: {exc})"] += 1
            value = 0
        uc.reg_write(UC_X86_REG_EAX, (value or 0) & 0xFFFFFFFF)
        uc.reg_write(UC_X86_REG_ESP, esp + 4 + 4 * argc)
        uc.reg_write(UC_X86_REG_EIP, ret)

    # ------------------------------------------------------------------ 執行
    def run(self, seconds: float = 30.0, max_insn: int = 200_000_000) -> Result:
        if not self.import_count:
            self.prepare()
        uc = self.uc
        esp = STACK + STACK_SIZE - 0x100
        uc.reg_write(UC_X86_REG_ESP, esp)
        uc.mem_write(esp, struct.pack("<I", SENTINEL))
        entry = BASE + self.pe.OPTIONAL_HEADER.AddressOfEntryPoint
        started = time.time()
        stopped = ""
        try:
            uc.emu_start(
                entry, SENTINEL, timeout=int(seconds * 1_000_000), count=max_insn
            )
            stopped = "budget"
        except ProcessExit as exc:
            stopped = str(exc)
        except UnknownArity as exc:
            stopped = f"unknown argc: {exc.name}（把它加進 win32_env.ARG_COUNTS 再跑）"
        except UcError as exc:
            stopped = f"fault: {exc}"
        result = Result(
            image=self.path.name,
            sha256=hashlib.sha256(self.raw).hexdigest(),
            imports=self.import_count,
            exports=len(self.exports),
            calls=dict(self.calls.most_common()),
            unimplemented=dict(self.unimplemented.most_common()),
            stopped=stopped,
            eip=uc.reg_read(UC_X86_REG_EIP),
            seconds=round(time.time() - started, 2),
        )
        result.changed_regions = self._changed_regions()
        result.rebinding = self._rebinding(result.changed_regions)
        return result

    def _changed_regions(self, gap: int = 32) -> list:
        snap = bytes(self.uc.mem_read(BASE, len(self.original)))
        diffs = [
            i
            for i, (a, b) in enumerate(zip(snap, self.original, strict=False))
            if a != b
        ]
        if not diffs:
            return []
        regions = []
        start = prev = diffs[0]
        for index in diffs[1:]:
            if index - prev > gap:
                regions.append({"va": hex(BASE + start), "size": prev - start + 1})
                start = index
            prev = index
        regions.append({"va": hex(BASE + start), "size": prev - start + 1})
        return regions

    def _rebinding(self, regions: list) -> dict:
        """IAT 有沒有被殼重寫（這是目前唯一穩定的正向訊號）。"""
        iat = next(
            (
                d
                for d in self.pe.OPTIONAL_HEADER.DATA_DIRECTORY
                if d.name == "IMAGE_DIRECTORY_ENTRY_IAT"
            ),
            None,
        )
        if iat is None or not iat.VirtualAddress:
            return {}
        hit = [
            r
            for r in regions
            if int(r["va"], 16) <= BASE + iat.VirtualAddress + iat.Size
            and BASE + iat.VirtualAddress <= int(r["va"], 16) + r["size"]
        ]
        return {
            "iat_va": hex(BASE + iat.VirtualAddress),
            "iat_size": iat.Size,
            "regions_touching_iat": hit,
        }

    def snapshot(self) -> bytes:
        return bytes(self.uc.mem_read(BASE, len(self.original)))


sys.path.insert(0, str(Path(__file__).resolve().parent))
from fake_modules import build_module  # noqa: E402
from win32_env import (  # noqa: E402
    ARG_COUNTS,
    BASE,
    EXTRA_EXPORTS,
    HEAP,
    HEAP_SIZE,
    MODULE_BASE,
    PEB,
    SENTINEL,
    STACK,
    STACK_SIZE,
    STUB,
    STUB_SIZE,
    ProcessExit,
    install_api,
)


def _aliases_input(target: Path, image: Path) -> bool:
    """輸出路徑是不是就是輸入映像（同路徑 / symlink / 硬連結）。"""
    try:
        if target.resolve() == image.resolve():
            return True
        return target.exists() and image.exists() and target.samefile(image)
    except OSError:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="在 Unicorn 裡跑 mxmain.dll 的保護殼入口（只讀、實驗性）"
    )
    parser.add_argument(
        "image",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "mxmain.dll",
        help="輸入 PE（預設倉庫根 mxmain.dll）",
    )
    parser.add_argument("--seconds", type=float, default=30.0, help="時間預算（秒）")
    parser.add_argument("--max-insn", type=int, default=200_000_000)
    parser.add_argument("--json", type=Path, help="把結果寫成 JSON（不含映像內容）")
    parser.add_argument("--snapshot", type=Path, help="把跑完的映像快照寫到這裡")
    args = parser.parse_args(argv)

    if not args.image.is_file():
        parser.error(f"找不到輸入映像：{args.image}")
    for target in (args.json, args.snapshot):
        if target is not None and _aliases_input(target, args.image):
            parser.error(f"輸出路徑不能指向輸入映像：{target}")

    rt = Runtime(args.image).prepare()
    result = rt.run(seconds=args.seconds, max_insn=args.max_insn)

    print(f"輸入：{result.image}  {result.sha256}")
    print(
        f"導入 {result.imports} 槽 / 假匯出 {result.exports} 名 / "
        f"{result.seconds:.1f} s / 停因：{result.stopped}（eip={result.eip:#x}）"
    )
    print("被調用的 API：", result.calls)
    if result.unimplemented:
        print("未實作（回 0）：", result.unimplemented)
    print("映像被改寫的區間：", result.changed_regions or "無")
    if result.rebinding.get("regions_touching_iat"):
        print("IAT 重綁：", result.rebinding)
    else:
        print("IAT 重綁：未觀察到")
    hottest = [(hex(addr), count) for addr, count in rt.writes.most_common(3)]
    print(f"寫入次數：{rt.writes_total}，最熱目標：{hottest}")

    if args.snapshot:
        args.snapshot.write_bytes(rt.snapshot())
        print("快照 →", args.snapshot)
    if args.json:
        args.json.write_text(
            json.dumps(result.__dict__, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print("JSON →", args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
