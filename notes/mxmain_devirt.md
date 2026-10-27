# mx.exe（DuoyiProtect）入口 VM 去虚拟化 — 阶段性结案笔记

> 范围：仅针对 **`mx.exe` 被 DuoyiProtect 虚拟化的入口区**。
> 状态：**架构与内存布局已实测确认；交接点（真实入口）尚未最终锁定。**
> 原则（见 AGENTS.md）：能展示 ≠ 能运行，能运行 ≠ 正确。下文严格区分 **【已确认】** 与 **【待证/已撤回】**。

## 0. 结论速览

| 项目 | 结果 | 状态 |
|---|---|---|
| OEP / VM 入口 | `0xCBA0AE`（VA，基址 `0x400000`） | 【已确认】每次调试稳定命中 |
| VM / 壳代码区 | `[0x947000, 0xE42000)` | 【已确认】 |
| 真实引擎代码区 | 原始 `.text` `[0x401000, 0x6B0000)` | 【已确认】真实 MSVC 代码 |
| 解密区 RWX | `[0x7DB000, 0x821000)` + `[0x822000, 0x947000)` | 【已确认存在，内容见下】 |
| 真实入口（交接点） | **未锁定** | 【待证】 |
| PAGE_GUARD 方案 | 不可用 | 【已证否】 |
| 硬件执行断点方案 | 可用（但覆盖度不足） | 【已确认可用】 |

## 1. 工具（均在 `tools/unpack/`）

| 脚本 | 作用 |
|---|---|
| `unpack_hwbp.py` | OEP 门控 + 硬件执行断点找交接（**推荐继续用**） |
| `unpack_stack.py` | OEP 后自由跑→挂起主线程→回溯调用栈（`stack_walk.txt`） |
| `diag_mem2.py` | OEP 时刻网格探测内存区域/保护（**布局证据来源**） |
| `unpack_handoff.py` | PAGE_GUARD 方案（**已证否，保留作反面记录**） |
| `unpack_trace.py` | TF 单步追踪（可跑但太慢，见 §5） |
| `dump_entry.py` | IDAPython：把 chunk 映射回 VA 再反汇编（产 `entry_asm.txt`） |

IDA 批调用要点（踩过的坑）：
- `-S` 脚本路径**必须用反斜杠**（正斜杠会报 `unknown file extension`）；
- IDA 9.4 段模块名是 **`ida_segment`**，不是 `ida_segm`；
- 不要直接对 10MB flat PE 跑 `-A` 全量分析（极慢）；改为**喂 16KB chunk，脚本内 `add_segm` 映射回真实 VA**。

## 2. 【已确认】OEP 与内存布局

`diag_mem2.py` 在 OEP 命中瞬间实测（非推测）：

```
0x400000 +0x1000    RW      PE header
0x401000 +0x2AF000  ER  EXEC   ← 原始 .text（真实代码，非零率 90.1%）
0x6B0000 +0x12B000  RW          .rdata/.data（83.7%）
0x7DB000 +0x046000  RWX         ← 解密区 A（非零率 70.7%）
0x821000 +0x001000  RW          gap（21.1%）
0x822000 +0x125000  RWX         ← 解密区 B（非零率 2.1%，几乎全零）
0x947000 +0x4FB000  ER  EXEC   ← VM / 壳代码（96.7%），含 OEP 0xCBA0AE
0xE42000 +0x01A000  RW
```

**关键修正**：先前笔记里"VM ≥ `0xC50000`、真实代码 < `0xB00000`"的二分是**错的**。
实测 VM 区是 `[0x947000, 0xE42000)`，起点 `0x947000` 比 `0xC50000` 低得多。

## 3. 【已确认】真实代码为真

`entry_asm.txt`（IDA 反汇编 `0x401000` 起 16KB）显示标准 MSVC `/GS` 产物：
`push ebp / mov ebp,esp / push ecx / xor eax,eax / mov [ebp-1],al / mov esp,ebp / pop ebp / retn`，
后随 `int3` 对齐填充与真实 `call`。**原始 `.text` 未被破坏，是完好真实代码。**

## 4. 【已证否 / 已撤回】

- **PAGE_GUARD 不可用**：壳解密时会 `VirtualProtect` 改写页保护，把预置的 GUARD 位清掉。
  实测 `unpack_handoff.py` 在 `[0x401000,0xC50000)` 只成功保护 **2 页**，随后陷入 30 万次
  数据读误触发风暴，始终等不到交接。→ 改用硬件执行断点（CPU 级、不受 `VirtualProtect` 影响）。
- **撤回"`0x401000` 是交接点"**：`unpack_hwbp.py` 命中 `0x401000`，但反汇编证明它只是
  一个 **12 字节空桩函数**（置一个局部字节即 `ret`），语义上**不可能是程序入口**。
  它更可能是 **VM 运行过程中调用了原始 `.text` 里的辅助桩函数，随后返回 VM**，
  而非 VM→真实的永久交接。此结论已撤回，不可写进对外结论。

## 5. 【待证】交接点尚未锁定 — 当前卡点与证据

- VM 区搜不到字面量 `0x00401000`，说明交接目标是**运行时计算**的（非硬编码跳转）。
- `unpack_stack.py`：OEP 后自由跑 12s，挂起时 `EIP=0x771C361C`（ntdll，线程阻塞于系统调用），
  `ESP=0x19FD5C`。栈上**最早（地址最高）**两个指向镜像的槽位：
  - `[0x1C1148] = 0x9467F5`
  - `[0x1C1144] = 0x93FD98`
  两者都落在"解密区 B"。**但解密区 B 在静态 dump 里非零率仅 2.1%（几乎全零）**，
  且 `0x9467F5` 前 16KB 内**找不到任何函数序言**。故这两个值**无法静态证实**是返回地址，
  也可能是未初始化栈上的陈旧垃圾值。**不作结论。**
- 其余栈槽多为 UTF-16 字符串数据（如 `0x69004D` = "Mi"…），非返回地址，属误报。

### 卡点根因
真实代码是**运行时渐进解密**的：静态 dump（OEP+8s 抓的 `mx_unpacked_post.bin`）
里解密区 B 还是全零，而运行时该区才被填入代码。因此**任何单张静态 dump 都抓不全**，
静态反汇编该区不可行。

## 6. 下一步建议（按性价比排序）

1. **运行时定点 dump**：OEP 门控 + 在候选地址下硬件执行断点，**命中的瞬间**立刻
   `SuspendThread` 并把解密区整块 dump 出来——此时代码必已解密，可静态反汇编。
   （比"事后抓 dump"可靠，直接解决 §5 根因。）
2. **加判据的硬件断点**：命中候选后不立即停，改为**短程 TF 单步 ~200 步**，
   若 EIP 回到 VM 区 `[0x947000,0xE42000)` 则判为"VM 调用"（非交接）并继续放跑；
   若持续留在真实区则判为交接。解决 §4 的 `0x401000` 误判。
3. **长程 TF 单步**（兜底）：从 OEP 单步至首次进入真实区且不返回 VM。
   代价：Python ctypes 每次 ~1–3ms，若 VM 有 10^5–10^6 条指令，需 20min–1h。

**不建议**在本轮继续投入：完整 VM 去虚拟化（还原每个 handler 语义、重建字节码）
属人年级工作量，超出单次会话范围。

## 7. 复现命令

```bash
# 内存布局（OEP 时刻）
/d/Python315-32/python.exe tools/unpack/diag_mem2.py "D:/MXSJ_TW_2022/mx.exe"
# OEP 门控 + 硬件执行断点
/d/Python315-32/python.exe tools/unpack/unpack_hwbp.py "D:/MXSJ_TW_2022/mx.exe" tools/unpack/handoff.txt
# 自由跑 + 栈回溯
/d/Python315-32/python.exe tools/unpack/unpack_stack.py "D:/MXSJ_TW_2022/mx.exe" 12 tools/unpack/stack_walk.txt
# IDA 反汇编真实入口 chunk
cd /d/IDA9.4/IDA9.4 && ./idat.exe -A -S"D:\MXSJ_TW_2022\tools\unpack\dump_entry.py" "C:\chunk_entry.bin"
```
