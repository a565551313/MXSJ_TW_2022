# mxmain.dll —— DuoyiProtect 脱壳（Windows 实机动调）

> 用 **Windows 实机 + 原生 Win32 调试器**把 `mxmain.dll`（== `mx.exe`）的 DuoyiProtect 壳脱掉，
> 进原本加密的 `_dyprot0`/`_dyprot1` 段。结论：**壳是 anti-dump 段替换 + 入口 VM 化**，不是单纯加密。
> 配套脚本与产物在 `tools/unpack/`。
>
> - 工具链：IDA 9.4（`D:/IDA9.4/IDA9.4/ida.exe`）、32 位 Python（`D:/Python315-32/python.exe`）+ ctypes
> - 二进制：`D:/MXSJ_TW_2022/mx.exe`（与 `mxmain.dll` 逐字节相同，MD5 `2609423fe7fadd5446eb2425ab894ac8`）
> - 日期：2026-10-27
> - 修正了 `client_binary_reversibility.md` §2 的"54% 静态进不去"假设（见 §3）

## 1. 打法（4 步，脚本可复用）

1. **侦察** `tools/unpack/pe_recon.py`：`mxmain.dll` 入口 RVA `0x8ba0ae`（→ VA `0xcba0ae`，落在 `_dyprot1`）、
   导入表 RVA `0x9a4a78`（落在 `_dyprot0`）、**无 TLS 回调**、subsystem=GUI(2)。
2. **探针** `tools/unpack/unpack_probe.py`：把 `mx.exe` 拉到原生调试器下，确认进程能跑、入口在加密段、
   壳用自定义异常 `0x406D1388` 驱动控制流（SEH/VEH 控制流混淆）。
3. **脱壳转储** `tools/unpack/unpack_dump.py`：
   - `DEBUG_ONLY_THIS_PROCESS` 拉起；基础 anti-anti-debug：清 `PEB.BeingDebugged` + 伪装调试端口(`ProcessDebugPort`/`ProcessDebugFlags`)。
   - 主线程下**硬件执行断点 DR0 = OEP `0xcba0ae`**（硬件断点扛得住壳对代码段的解密/覆盖；软件 `0xCC` 会被覆盖）。
   - 全程把异常当 `DBG_EXCEPTION_HANDLED` 放行，让壳自己的 SEH 跑。
   - OEP 处 `EXCEPTION_SINGLE_STEP` 命中 → `VirtualQueryEx`+`ReadProcessMemory` 平铺转储整镜像 → `tools/unpack/mx_unpacked.bin`（10.4 MB）。
4. **重建 PE** `tools/unpack/rebuild_pe.py`：把每段 `PointerToRawData` 改为 `(VirtualAddress-ImageBase)`、
   清 import/IAT/delay-import 目录（保留 export）、**把 `.text/.rdata/.data/.rsrc` 诱饵段清零，只留解密后的 `_dyprot0/_dyprot1`** → `tools/unpack/mx_unpacked_rebuilt.exe`。
   然后用 IDA 打开（会话 `8e7e8963`，IDB `mx_unpacked_rebuilt.exe.i64`）分析。

## 2. 脱壳校验：段替换 / 诱饵（核心发现）

转储里各段熵（磁盘 vs 内存）：

| 段 | 磁盘熵 | 转储熵 | 判读 |
|---|---|---|---|
| `.text` | 6.64 | **7.84** | 磁盘明文真代码；**内存里被壳原位加密成诱饵** |
| `.rdata` | 5.99 | **7.72** | 同上（磁盘明文 RTTI/字符串已被静态拿到） |
| `.data` | 5.10 | **0.00** | 被清空 |
| `_dyprot0` | 7.85 | **6.31** | **解密成功（真代码）** |
| `_dyprot1` | 7.72 | **4.86** | **解密成功（含 OEP；低熵=大量结构化指令/字节）** |
| `.rsrc` | 5.15 | 7.88 | 诱饵 |

⇒ DuoyiProtect 用的是**段替换 + anti-dump**：磁盘上 `.text` 是真代码（静态可反汇编），`_dyprot` 是加密载荷；
**运行时壳把真代码解密进 `_dyprot`、把原位 `.text` 加密成废段**，使内存 dump 里 `.text` 失效。
验证：`sub_9C399C`（解密段）与 `sub_5C399C`（`.text`）逐字相同（都调 `sub_9DA632`、回退 `unk_8217C8`）——
**解密后的 `_dyprot` 就是 `.text` 真代码的重定位副本**。

## 3. 对旧结论的修正（重要）

`client_binary_reversibility.md` §2 称"`_dyprot` 两段共 5.2 MB ≈ 54%，静态读不进去、静态只能覆盖剩馀"。
实测修正：**那 54% 主要是 `.text` 真代码的 anti-dump 副本，逻辑早已在可读的 `.text` 里（第一轮机静态分析已拿到 JSON 编解码器、原生→脚本桥、引擎服务等）**。
真正"静态进不去"的是**入口/启动逻辑**，它在 `_dyprot1` 且被 **VM 虚拟化**（见 §4），不是因为加密。

## 4. OEP 是被 VM 化的启动代码（唯一真正新拿到、但不可直接反编译的部分）

- OEP `0xcba0ae` 字节 `eb 08 … e9 ba 09 15 00` = `JMP +8` 跳过 8 字节数据 + `JMP rel32` 到 `0xe0aa77`（跳板）。
- `0xe0aa77` 字节 `68 … e8 … fe 90 … 64 8b 11(mov edx,[fs:ecx]) … 81 ef … 02 c1 f8 66 …`：非标准函数头，而是
  **VM 字节码/句柄特征**（从 `fs:`（TEB）读数据、不规则 `inc/dec [reg]`、夹杂派发）→ 入口/启动逻辑被 DuoyiProtect 代码虚拟化。
- Hex-Rays 在 `0xcba0ae`/`0xe0aa77` 均"Decompilation failed"——因为那是 VM handler 解释的字节码，不是可反编译的原生码。
- 解密段里还看到 `sub_9DA22F`（dispatcher，15 个 callee）等疑似 VM 派发器，是后续 devirtualization 的切入点。

## 5. 产物与下一步

- 产物（本地，未入库，体积大）：`tools/unpack/mx_unpacked.bin`、`tools/unpack/mx_unpacked_rebuilt.exe`、
  解密 IDB `tools/unpack/mx_unpacked_rebuilt.exe.i64`、明文 IDB `mxmain.dll.i64`。
- **下一步 A（推荐，低投入）**：把第一轮机（`.text` 真代码）的锚点重命名写回 `mxmain.dll.i64`，并枚举 `.rdata` 里 `(...)` 格式串整理原生↔脚本方法签名表——逻辑早已可拿，只是命名/清单化。
- **下一步 B（人年级，慎入）**：对 `0xe0aa77`/`sub_9DA22F` 一带做 **VM devirtualization**（DuoyiProtect 代码虚拟化还原），才能把入口启动逻辑反编译成可读源码。
- **下一步 C**：用解密 IDB（会话 `8e7e8963`）对 `_dyprot` 里 5,205 个函数做差异分析，确认是否与 `.text` 完全重复，或藏有 `.text` 没有的额外逻辑。
