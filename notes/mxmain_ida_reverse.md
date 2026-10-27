# mxmain.dll —— IDA Pro MCP 逆向反编译快照

> 本文件记录用 **IDA Pro MCP**（headless worker，Hex-Rays 已初始化）对 `mxmain.dll`
> 做的定点反编译结果。目的是把"能用 IDA 白拿到什么"钉下来，补 `client_binary_reversibility.md`
> 里"静态只能到伪 C"那一档的具体证据。
>
> - 工具：`mcp__ida-pro-mcp__*`，会话 `e05fd3ee`，IDB 落盘 `D:\MXSJ_TW_2022\mxmain.dll.i64`
> - 输入：`D:\MXSJ_TW_2022\mxmain.dll`（MD5 `2609423fe7fadd5446eb2425ab894ac8`，与 `mx.exe` 逐字节相同）
> - 日期：2026-10-27
> - 范围：只覆盖可读段（`.text`/`.rdata`/`.data`）。`_dyprot0`/`_dyprot1` 两段约 5.2 MB（≈全镜像 54%）
>   受 DuoyiProtect 壳保护，无法静态反编译。

## 1. 二进制总览（survey_binary）

| 指标 | 值 |
|---|---|
| 架构 / 基址 | x86-32 / `0x400000` |
| 镜像大小 | `0xa5c000`（10.9 MB） |
| 函数总数 | **12,279**（命名 392，库函数 22，未命名 11,865） |
| 字符串总数 | 17,514 |
| 段数 | 7 |
| 导出 | 仅两个具名：`?JSON_DecodeObject@@...`（ord 1, `0x40b1c0`）、`?JSON_EncodeObject@@...`（ord 2, `0x40c2a0`） |
| DLL 入口 | `start` @ `0xcba0ae`（落在 `_dyprot1` 受保护段内 ⇒ DllMain 不可静态读） |

段布局（可读段 vs 受保护段）：

| 段 | 范围 | 权限 | 说明 |
|---|---|---|---|
| `.text` | `0x401000`–`0x6b0000` | rx | 明文 x86 码，可反汇编/反编译 |
| `.rdata` | `0x6b0000`–`0x7db000` | r | 明文数据 + RTTI 名 + 字符串表 |
| `.data` | `0x7db000`–`0x947000` | rw | — |
| `_dyprot0` | `0x947000`–`0xc5e000` | rx | 加密/压缩载荷（壳） |
| `_dyprot1` | `0xc5e000`–`0xe1b000` | rx | 加密/压缩载荷（壳）；入口也在此 |
| `.idata` | `0xe1b000`–`0xe1be00` | rx | 导入表 |
| `_dyprot1` | `0xe1be00`–`0xe42000` | rx | 壳（续） |

导入按类别：crypto（`CertLib`、`IMProtocol` 加解密）、network（`dgw.HttpSend`、`libcurl`、`libcef`）、
file_io（`ResLib.UpdateFile`、`wwise` 音频、`CrashRpt`）、process（`WINMM` 定时器、`IMM32` 输入法、`KERNEL32`）、
registry（`USER32` 窗口类、`wwise` 注册）。**无任何 `python2x.dll`** ⇒ Python 解释器是内嵌定制的（与双 VM 结论一致）。

## 2. 内嵌 CPython 的正向证据（字符串）

`.rdata` 中明文命中 CPython 内部串（非"strings 搜不到"式否定推断，而是正面证据）：

- `exceptions bootstrapping error.`（xref 49）、`Module dictionary insertion problem.`（xref 47）
- `GC object already tracked`（xref 24）、`GC object already untracked`（xref 23）
- `__dict__`（xref 20）、`__builtin__`（xref 18）、`strop functions are obsolete; use string methods`（xref 18）
- `bad allocation`（xref 17）

⇒ 内核是定制 CPython（2.5/2.7 风格），字符串层脚本跑在它上面。

## 3. 两个导出 = 手写 JSON 编解码器（唯一白拿的源码级信息）

### 3.1 `JSON_DecodeObject` @ `0x40b1c0`
```
int __cdecl JSON_DecodeObject(struct __JSONObjectDecoder *a1, const char *a2, unsigned int a3)
```
入口配置 decoder 的若干字段（`a1+16`=错误码、`a1+17`=错误行、`a1+19` 暂存），调用 `sub_40B090` 做顶层值解析，
再 `sub_40A5C0` 跳过尾部空白；若仍有剩余字节而 `sub_40B090` 成功，则置 `a1+16="Trailing data"` 返回 0。
decoder 用虚函数指针表（偏移 `+12`=回调、`+14`=清理、`+16`=错误串、`+17`=错误行）承载解析状态。

### 3.2 `JSON_EncodeObject` @ `0x40c2a0`
```
char *__cdecl JSON_EncodeObject(void *a1, struct __JSONObjectEncoder *a2, char *a3, unsigned int n0x8000_1)
```
配置 encoder 虚表（`+12`=分配器 `sub_5C2486`、`+13`=追加 `sub_5CCF7C`、`+14`= `sub_5C244E`）。
未传入缓冲区时默认用引擎堆分配 **32 KB**（`0x8000`）可增长缓冲；末尾补 `\0` 返回字符串指针。
⇒ 编码器走的是引擎的自定义堆（`dword_93C5F8`），不是 CRT `malloc`。

### 3.3 解析核心与子例程（全在 `.text`，可静态读）

| 地址 | 角色 | 说明 |
|---|---|---|
| `0x40B090` | `json_parse_value` | 顶层值分发器，按首字节 `-9` 后 switch |
| `0x40ADD0` | `json_parse_object` | `{` |
| `0x40AC40` | `json_parse_array`  | `[` |
| `0x40A610` | `json_parse_string` | `"` |
| `0x40A0D0` | `json_parse_number` | `-` / 数字（`0x24`+`0x27..0x30` 段） |
| `0x40A4D0` | `json_parse_true`   | `t`(`0x6B`) |
| `0x40A520` | `json_parse_false`  | `f`(`0x5D`) |
| `0x40A570` | `json_parse_null`   | `n`(`0x65`) |
| `0x40A5C0` | `json_skip_ws`      | 跳过空白（`0x19/0x17/0/1/4` 段） |

`sub_40B090` 的分发键是 `**this - 9`：映射 `0x22('"')→0x19`、`0x2D('-')→0x24`、`0x30..0x39('0'..'9')→0x27..0x30`、
`0x5B('[')→0x52`、`0x66('f')→0x5D`、`0x6E('n')→0x65`、`0x74('t')→0x6B`、`0x7B('{')→0x72`，
default/越界 → `a1+8+68` 置 `"Expected object or value"`。是一份**干净的手写 JSON 递归下降解析器**。

## 4. 引擎核心运行时服务（按 xref 数排序，均为 `.text` 内高频锚点）

| 地址 | xref | 分类 | 推断角色（含反编译证据） |
|---|---|---|---|
| `0x44BA20` | 1179 | complex | **一次性初始化 + 锁/访问器**：`dword_829C50&1` 未置时置位并 `sub_44BB80(&unk_829BA0)`、`sub_5C0A45(sub_6AE6F0)`，随后 `sub_454760`/`sub_44BC00`/`sub_454780` 成"获取-返回"形。是全局单例/锁访问器；`sub_402560`（668 xref）是其纯转发别名。 |
| `0x4D3100` | 1092 | leaf | **树/层级包含判定**：`a1[21]&0x100==0` 时仅判 `a2==a1 || a2==&dword_7E4880`；否则沿 `a1[32]`(父指针) 链上溯，或遍历 `a1[43]`(子数组，长度 `*a1[43]+8`，元素 `@a1[43]+12`) 查 `a2`。典型的 UI 窗口树"是否祖先/自身"判定。 |
| `0x4E1830` | 979 | complex | **引用计数指针释放/转移**：`sub_4FD360(a2)`（INCREF）后 `sub_4E1800(a1,v2)`；若 `(*v2)--==1` 调 `v2[1]+24` 的虚析构。引擎智能指针/句柄释放原语。 |
| `0x4E1D50` | 691 | wrapper | 三参薄包装：`sub_4E3AD0(a1,a2,&a3,0)`（把 `char` 按值收成指针传），疑为日志/追踪类调用。 |
| `0x402560` | 668 | wrapper | `return sub_44BA20(a1)` — `0x44BA20` 的纯别名。 |
| `0x5C244E` | 641 | complex | **全局注册表插入**：`MEMORY[0x3D9098](dword_93C5F8,0,a1)` 查重，未命中则 `sub_5C399C()`+`sub_5C39AF` 分配并写入。 |
| `0x5C08F8` | 594 | noreturn | **致命退出/abort**：取 `MEMORY[0x3D8D96](dword_93C4E4)` 清理函数调用，再 `sub_5CD81B`/`sub_5CD83A`。OOM/不可恢复错误路径。 |
| `0x5C399C` | 549 | wrapper | **堆/分配器上下文的 TLS 访问器**：`sub_5DA632()` 返回 TLS 基址则 `+8` 返回，否则回退 `&unk_8217C8`。 |
| `0x4E4830` | 480 | wrapper | 高频薄包装（未展开）。 |
| `0x5C1520` | 437 | leaf | **引擎自带的 SSE2 `memcpy`**：重叠感知（dst∈[src,src+n) 时反向拷贝），按 `dword_93C358`/`dword_821908` 特性位走 SSE2 或 `qmemcpy` 回退，跳表 `loc_5C18F4`/`loc_5C1768`/`loc_5C1868`。不是 CRT 的 memcpy。 |

### 4.1 自定义堆分配器（`sub_5C2486`）
```
int __cdecl sub_5C2486(unsigned int a1)
```
`a1 > 0xFFFFFFE0` ⇒ OOM（`sub_5DD49D` + 错误码 `12`）。否则惰性初始化 `dword_93C5F8`（堆上下文，经
`sub_5DD06E`/`sub_5DD0CB(30)`/`sub_5CB241(255)`），再 `MEMORY[0x3D908C](dword_93C5F8,0,v1)` 分配。
`MEMORY[0x3D908C/0x3D9098/0x3D8B92/0x3D8D96]` 是经函数指针表的虚分发（引擎对象/堆的方法表）。
JSON 编码器、注册表插入都走它 ⇒ 全引擎统一堆。

## 5. 原生 → 脚本桥（`0x4576b0`，notes §2 预测的"桥函数"）

```
int sub_4576B0(int a1, ...)            // 变参
```
- `v5=va_arg` = 方法名；`sub_4D7240(a1, v5)` 按名解析脚本方法（返回 PyObject 风格句柄 `v1`）。
- 命中则 `sub_457E60(a1, v7, v8, v9, va1)` 调用，结束后 `(*v1)--==1` 触发 `v1[1]+24` 虚析构（同 §4 的引用计数释放）。
- 未命中则 `sub_457F40("Can't get method:{}", va)` + `sub_458330` 记日志并返回 `-1`。

**关键**：这是 `PyArg_ParseTuple` 风格的**带格式串的类型化封送调用**——原生代码用 `"方法名"` + `格式串` + C 实参
把值推给内嵌 CPython。回调名表在**明文 `.rdata`**（如 `"OnServerCmd"` @ `0x6bb138`，被 `sub_4AB790`/`sub_4AB870`/`sub_4AC030` 引用），
印证 notes §2 的结论"名字在不在明文要按用途分开看"。

### 5.1 实例：`OnServerCmd` 回调的注册/分发（`sub_4AB790`）
```
result = sub_4576B0(*this, "OnServerCmd", &unk_6BB131, 0, "(i)", *(uint8*)(member+4));
```
- 第四个实参 `&unk_6BB131` 是紧邻 `"OnServerCmd"` 串的参数描述块；
- 第五个实参 `"(i)"` = **原生签名格式串：一个 int 参数**；
- 第六个实参 = 从成员对象 `+4` 处读的 1 字节 int 值。
⇒ `OnServerCmd` 在脚本侧接收 **1 个整数**。对私服重建：这就是客户端原生层向脚本层派发服务器命令的钩子名与签名。

## 6. 静态够不到的地方（如实记录）

- `_dyprot0`/`_dyprot1`（≈5.2 MB，~54%）受 DuoyiProtect 壳保护，`MEMORY[...]` 虚表与这些段里的代码无法静态还原。
- DLL 入口 / DllMain @ `0xcba0ae` 落在 `_dyprot1`，**进不去**；壳的脱壳/解包属人年级工程（见 `client_binary_reversibility.md` §4 第三路）。
- `MEMORY[0x3D90xx]` 这类虚分发槽的真实目标在受保护段，只能标到"经函数表调用"，不能确定最终实现。

## 7. 建议的下一步（未执行，待确认）

1. **把锚点重命名写回 IDB**，让下一个人直接看到语义：`sub_40B090→json_parse_value`、`sub_40ADD0→json_parse_object`、
   `sub_4576B0→native_call_script_method`、`sub_44BA20→engine_locked_accessor`、`sub_4D3100→ui_tree_contains`、
   `sub_5C1520→engine_memcpy`、`sub_5C2486→engine_heap_alloc`、`sub_5C399C→heap_ctx_tls`。
2. **枚举全部 `(...)` 格式串**（在 `.rdata` 搜 `(` 起、`)` 止的短串）列出原生↔脚本的方法签名表——这是私服协议对齐的高价值清单。
3. 围绕 `sub_4AB790`/`sub_4AB870`/`sub_4AC030` 这类调用点，反推"哪些原生事件会触发哪些脚本回调"。
4. 如需进受保护段：按 `client_binary_reversibility.md` §4 第三路（Ghidra/IDA 全量 + 绕壳），需 Windows 实机。
