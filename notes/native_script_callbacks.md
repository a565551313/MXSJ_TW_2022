# 原生 → 脚本回调清单（mxmain.dll，静态核查结案）

> 分支 `arena/4d3d51ac-mxsj-tw-2022`｜日期 2026-10-26｜输入 `mxmain.dll`
> （9,698,712 B，SHA-256 `637331b5…be424d`，全程只读）
>
> 本文是 [`mxmain_rtti_class_map.md`](mxmain_rtti_class_map.md) §6「延伸发现」的结案：
> 把「名字 + 签名串」候选逐条核 xref，做出**原生按名字调用脚本方法**的完整清单，
> 并顺带把反方向（脚本 → 原生）的规模量清。全部结论来自明文 `.text` / `.rdata`，
> 不启动客户端、不连网、不碰 `data/*.fls`。

## 1. 结论摘要

1. 桥函数只有一个：`0x4576b0`，签名是
   `int bridge(PyObject *obj, const char *name, const char *ret_fmt, void *ret_slot, const char *arg_fmt, ...)`。
   `obj` 上按 `name` 取方法（`0x4d7240`），取到就按 `arg_fmt` 组参调用（`0x457e60`），
   取不到就报 `"{} 函数无法获取"`（`0x6b2434`）/`"Can't get method:{}"`（`0x6b2448`）并返回 `-1`。
2. `.text` 里指向 `0x4576b0` 的 `E8` 调用**恰好 16 个**（穷举，不是一个子集），
   全部实名，分属 **12 处宿主位置 / 2 个簇**（其中 8 处入口能由 `0xCC` 填充确认，4 处在无填充的热/冷块里）。
3. 16 个调用点只对应 **8 个脚本方法名**：`CSetDirection`、`Stop`、`IsWalk`、
   `OnServerCmd`、`OnSpecialServerCmd`、`OnError`、`OnConnectFail`、`OnConnected`。
4. 宿主一半是渲染对象（`CWalkerObject` 家族，`CSetDirection` 就是它的**虚表槽 22**），
   另一半是网络层（`CNet` 事件分发，事件码 **10001–10004**，`0x2714` 正是 `OnServerCmd` 那一路）。
5. 反方向：镜像里 **82 处 `Py_InitModule4`（`0x4e4850`）**，其中 **21 个是引擎自有模块** `C_*`，
   共 **322 个脚本可调原生方法**；其余 61 处是内嵌 CPython 2.5 标准库模块。
6. 两个方向**在代码上是分离的**：没有任何一个 `PyMethodDef` 实现函数在 1 跳内直连桥；
   只有 `C_net` 一侧的 `Process` / `ProcessServerCmd` / `Replay` 在 1–2 跳内会走进回调。

## 2. 桥函数 `0x4576b0` 的契约（字节级）

`0x4576b0` 的入口（`objdump -d --start-address=0x4576b0 --stop-address=0x4577c0`）：

```asm
4576b0: 55              push ebp
4576b1: 8b ec           mov  ebp,esp
4576b3: 56              push esi
4576b4: ff 75 0c        push DWORD PTR [ebp+0xc]   ; name
4576b7: ff 75 08        push DWORD PTR [ebp+0x8]   ; obj
4576ba: e8 81 fb 07 00  call 0x4d7240             ; PyObject 上按名字取方法
4576bf: 8b f0           mov  esi,eax               ; 方法句柄（引用计数块）
4576c1: 83 c4 08        add  esp,0x8
4576c4: 85 f6           test esi,esi
4576c6: 75 49           jne  0x457711              ; 取到 → 组参调用
4576c8: e8 a3 cd ff ff  call 0x454470              ; 取不到 → 先问「是否在调试」
...
4576d3: 68 34 24 6b 00  push 0x6b2434              ; "{} 函数无法获取"
4576da: e8 61 08 00 00  call 0x457f40
...
4576fe: 68 48 24 6b 00  push 0x6b2448              ; "Can't get method:{}"
457703: e8 38 08 00 00  call 0x457f40
45770b: 83 c8 ff        or   eax,0xffffffff        ; 失败统一返回 -1
...
457711: 8d 45 1c        lea  eax,[ebp+0x1c]        ; 可变参数区
457715: 50              push eax
457716: ff 75 18        push DWORD PTR [ebp+0x18]  ; arg_fmt
457719: ff 75 14        push DWORD PTR [ebp+0x14]  ; ret_slot
45771c: ff 75 10        push DWORD PTR [ebp+0x10]  ; ret_fmt
45771f: 56              push esi
457720: e8 3b 07 00 00  call 0x457e60             ; 按格式取参 + 调 Python
```

参数语义（由「调用点压栈顺序」与「函数体读取顺序」双向确认，压栈从右往左）：

| # | 参数 | 含义 | 证据 |
|---|---|---|---|
| 1 | `PyObject *obj` | 脚本对象；多数调用点取 `[this+4]` / `[this]`，即 C++ 对象里挂的 Python 侧句柄 | `push [ebp+8]` 直接进 `0x4d7240` |
| 2 | `const char *name` | 脚本方法名 | 同上 |
| 3 | `const char *ret_fmt` | 返回值转换格式，`""`＝丢弃返回值，`"i"`＝把整数写回 `ret_slot` | `0x4ab7d0`：`ret_fmt="i"` + `ret_slot=&ebp-4`，随后 `cmp [ebp-4],0` 判返回值 |
| 4 | `void *ret_slot` | 返回值落点（`ret_fmt` 为空时传 `0`） | 同上 |
| 5 | `const char *arg_fmt` | 实参格式，`"()"`＝无参，`"(i)"` / `"(s)"` ＝ 1 个整数 / 1 个字符串 | `0x49d550`：`arg_fmt="()"`，调用后 `cmp [esp+0x20],0` 读结果；`0x4ac030`：`arg_fmt="(i)"` |
| 6+ | `...` | 实参本体，个数/类型由 `arg_fmt` 决定 | `lea [ebp+0x1c]` 取变参区交给 `0x457e60` |

配套地址（同一 `0x457xxx` 族，未逐个展开）：

- `0x4d7240` —— 取方法句柄：`(obj, name)`；返回的结构在 `0` 处是引用计数、`+4` 是类型指针（桥尾 `dec [esi]` / `call [[esi+4]+0x18]` 是标准 `Py_DECREF`）。
- `0x457e60` —— 组参并调用：`(callable, ret_fmt, ret_slot, arg_fmt, va_list)`。
- `0x457f40` / `0x458330` —— 两条报错路径（前者带格式化，后者直接抛/记）；`0x454470` 用来判断进程是否在调试器下。
- `0x457740` —— 同族的薄包装（少一个 `obj` 参数版本），本文 16 个调用点**没有**用它。

**报错串位置勘误**：上一轮笔记把它写成「`0x6b2434` 起是 `Can't get method:{}`」，实际是两个相邻槽——
`0x6b2434 = "{} 函数无法获取"`（GBK）、`0x6b2448 = "Can't get method:{}"`（ASCII），
前者在「取不到方法」的常规分支，后者在其后的兜底分支。

## 3. 16 个调用点全表

`.text` 内所有 `E8` 目标等于 `0x4576b0` 的位置（按地址排序，`call` 指令所在地址）：

| # | 调用点 | 宿主函数入口 | 宿主归属 | 脚本方法 | `ret_fmt` | `arg_fmt` | 实参 |
|---|---|---|---|---|---|---|---|
| 1 | `0x49a0e3` | `0x49a000` | **`CWalkerObject` 虚表槽 22**（同时出现在 `CMapWalkerObject`、`CMapHeroObject` 的槽 22） | `CSetDirection` | `""` (`0x6b9c61`) | `(i)` (`0x6ba1bc`) | 唯一的栈参数（`ret 0x4`） |
| 2 | `0x49a30a` | `0x49a2d0` | walker 簇（`0x49axxx`），无虚表槽 | `Stop` | `""` (`0x6b9c62`) | `()` (`0x6ba258`) | 无 |
| 3 | `0x49d225` | `0x49d1xx`（cold block，边界不可靠） | walker 簇 | `Stop` | `""` | `()` | 无 |
| 4 | `0x49d550` | `0x49d1xx`（同上） | walker 簇 | `IsWalk` | `"i"` (`0x6ba050`) | `()` (`0x6ba048`) | 无；返回值存回局部，`cmp …,0` 决定是否继续走 |
| 5 | `0x49d901` | `0x49d6xx` | walker 簇（`IsWalk` 为假的另一分支） | `IsWalk` | `"i"` (`0x6ba084`) | `()` (`0x6ba07c`) | 无；为假则接着调 `0x49a2d0`（`Stop`） |
| 6 | `0x4ab7b2` | `0x4ab790` | 网络簇（`CNet` 事件层） | `OnServerCmd` | `""` (`0x6bb131`) | `(i)` (`0x6bb134`) | `movzx eax,[cmd+4]` 取出来的命令号字节 |
| 7 | `0x4ab7fc` | `0x4ab7d0` | 网络簇 | `OnSpecialServerCmd` | `"i"` (`0x6bb148`) | `(i)` (`0x6bb144`) | 同上；返回值经 `&ebp-4` 回传，非 0 就释放命令对象 |
| 8 | `0x4ab8e9` | `0x4ab870` | 网络簇（`ProcessServerCmd` 主循环） | `OnServerCmd` | `""` | `(i)` | 命令号字节 |
| 9 | `0x4ab949` | `0x4ab870` | 同上（每帧处理数用尽后的尾段） | `OnServerCmd` | `""` | `(i)` | 命令号字节 |
| 10 | `0x4abab1` | `0x4ab9a0` | 网络簇（连接状态机） | `OnError` | `""` (`0x6bb132`) | `()` (`0x6bb160`) | 无；事件码 `8` 时走这条 |
| 11 | `0x4abada` | `0x4ab9a0` | 同上 | `OnConnectFail` | `""` (`0x6bb133`) | `()` (`0x6bb16c`) | 无；事件码 `6` 时走这条 |
| 12 | `0x4abb13` | `0x4abb00` | 网络簇（单条 `OnError` 薄包装，`ecx` 里就是 `this`） | `OnError` | `""` (`0x6bb132`) | `()` (`0x6bb160`) | 无 |
| 13 | `0x4abf15` | `0x4abef0` | 网络簇（`CNet` 构造/复位路径，`0x9347a8` 全局指向当前 `CNet`） | `OnError` | `""` (`0x6bb1a5`) | `(s)` (`0x6bb1a8`) | 常量串 `0x6bb190 = "新CNet实例覆盖旧实例"` |
| 14 | `0x4ac05c` | `0x4ac030` | 网络簇（`OnServerCmd(int)` 的实际发送者） | `OnServerCmd` | `""` (`0x6bb1a6`) | `(i)` (`0x6bb1c4`) | `movzx ax` 后的 16 位值来自 `call ds:0x6b020c`（`.rdata` 里的函数指针槽，运行期填，静态无法解析） |
| 15 | `0x4ac5c3` | `0x4ac590` | 网络簇**事件分发跳表** | `OnConnected` | `""` (`0x6bb1a7`) | `()` (`0x6bb1d4`) | 无 |
| 16 | `0x4ac5ec` | `0x4ac590` | 同上 | `OnError` | `""` (`0x6bb1c3`) | `(s)` (`0x6bb1f4`) | 常量串 `0x6bb1e8 = "连接中断"` |

`0x49a0e3` 那条值得单列：它是**唯一落在虚表槽里的**，而且三个类共用同一份实现——

```asm
49a0d0: 53              push ebx
49a0d1: 68 bc a1 6b 00  push 0x6ba1bc      ; "(i)"
49a0d6: 6a 00           push 0x0
49a0d8: 68 61 9c 6b 00  push 0x6b9c61      ; ""
49a0dd: 68 c8 a1 6b 00  push 0x6ba1c8      ; "CSetDirection"
49a0e2: 50              push eax            ; obj = [this+4]
49a0e3: e8 c8 d5 fb ff  call 0x4576b0
49a0eb: 83 f8 ff        cmp  eax,0xffffffff  ; -1 → 走 0x4615f0
```

即「渲染对象设朝向」这个原生动作里，带一次**脚本侧回调**，脚本可以拦截/响应；
失败（脚本没实现 `CSetDirection`）不致命，只是转为走 `0x4615f0` 的报错汇总。

## 4. 宿主归属与触发时机

### 4.1 walker 簇（`0x49a000`–`0x49d9xx`）

`0x49a000` 是 `0x6ba3e0` 虚表的第 22 槽，而 `0x6ba3e0` 被
`CWalkerObject` / `CMapWalkerObject` / `CMapHeroObject` 三个类共用（RTTI 侧已核，
见 RTTI 笔记 §4）。这一簇的回调语义：

- **`CSetDirection(dir)`** —— `this` 的朝向被原生改掉时调用；`dir` 就是新朝向。
- **`IsWalk()`** —— 原生问脚本「现在还该继续走吗」；返回真就继续，假就 `Stop`。
- **`Stop()`** —— 原生停步后通知脚本。

这正是「脚本驱动行走、原生询问状态」的双向协作形态，也解释了这 5 个调用点为什么
全挤在 `CWalkerObject` 的移动/朝向代码里。

> 边界说明：`0x49d1xx`–`0x49d9xx` 是 MSVC `/O2` 的热/冷块布局，块之间**没有 `0xCC` 填充**，
> 所以「函数入口」不能靠填充推断（`mxmain_rtti._function_start` 在这里会向上漂）。
> 本文只断言「落在 walker 簇」，不硬指定函数名；`0x49a000` 是唯一有虚表佐证的精确入口。

### 4.2 网络簇（`0x4ab790`–`0x4ac590`）与事件码

`0x4ac590` 是个**跳表分发器**：

```asm
4ac593: 8b 45 08        mov  eax,[ebp+8]        ; 事件码
4ac596: 8b 0d a8 47 93 00  mov ecx,ds:0x9347a8  ; 当前 CNet 单例
4ac59c: 05 ef d8 ff ff  add  eax,0xffffd8ef     ; -= 0x2711 (10001)
4ac5a1: 83 f8 03        cmp  eax,3
4ac5a4: 77 70           ja   0x4ac616          ; 不在 10001..10004 → 丢弃
4ac5a6: ff 24 85 1c c6 4a 00  jmp [eax*4+0x4ac61c]
```

跳表（`0x4ac61c`，4 个 dword）：

| 事件码 | 目标 | 脚本回调 |
|---|---|---|
| `10001` (`0x2711`) | `0x4ac5ad` | `OnConnected()` |
| `10002` (`0x2712`) | `0x4ac5cf` | `OnError("连接中断")` |
| `10003` (`0x2713`) | `0x4ac5f8` | 不调脚本，走 `call ds:0x6b0228`（同样是运行期函数指针槽） |
| `10004` (`0x2714`) | `0x4ac60e` → `call 0x4ac030` | `OnServerCmd(int)` |

**这条把 2026-10-09 交接里的「`0x2714` → `OnServerCmd(int)` 桥接」钉死了**：
`0x2714` 是事件码而不是包 opcode，处理体就是 `0x4ac030`，它把命令对象存到
`[this+0xc]` 之后回一次脚本。

其余 4 个网络簇调用点（`0x4ab7b2`/`0x4ab8e9`/`0x4ab949`/`0x4ab7fc`）在**命令队列消费**路径上：
取出命令对象（`[this+0xc]` 的链表头），读它 `+4` 的字节当命令号，调脚本；
脚本返回非 0（`OnSpecialServerCmd`）就把命令对象释放掉，否则留在链上（`0x4ab822` 起的
插入/计数逻辑说明是「未消费则回队」）。`0x4ab9a0` 是连接状态机，按状态码 `6` / `8`
分别回调 `OnConnectFail` / `OnError`。

### 4.3 谁会触发网络簇（直接 `E8` 调用者，全列）

| 回调小函数 | 直接 `call` 点 → 所在函数 | 说明 |
|---|---|---|
| `0x4ab790`（`OnServerCmd` 单条） | `0x467432` → `0x467270` | `C_net.Replay`：回放录制的服务器命令也走脚本回调 |
| `0x4ab7d0`（`OnSpecialServerCmd`） | `0x4ab985` → `0x4ab870` | 队列消费主循环 |
| `0x4ab870`（含 2 个 `OnServerCmd`） | `0x467079` → `0x467070` | `C_net.ProcessServerCmd` |
| `0x4ab9a0`（`OnError` / `OnConnectFail`） | `0x4674bf` → `0x467490`；`0x4ab873` → `0x4ab870` | `C_net.Process` + 队列循环 |
| `0x4abef0`（`OnError("新CNet实例…")`） | `0x4693f8` → `0x4693f0`；`0x469426` → `0x469420` | `C_imnet` 一侧的连接重置 |
| `0x4abb00`（`OnError` 薄包装） | **无直接 `E8` 调用者** | 只可能经函数指针/内联残块，静态未见入口 |
| `0x4ac030`（`OnServerCmd(int)`） | `0x4ac611` → `0x4ac590` | 事件码 `0x2714` 分支 |
| `0x4ac590`（跳表分发） | **无直接 `E8` 调用者** | 经单例 `0x9347a8` 的回调槽间接进入 |
| `0x49a000`（`CSetDirection`） | **无直接 `E8` 调用者** | 纯虚表槽（槽 22），只经虚调用进入 |
| `0x49a2d0`（`Stop`） | `0x49d2bc` / `0x49d32c` → `0x49ce40`；`0x49d6a9` → `0x49d670`；`0x49d916` → `0x49d6ac`；`0x49da10` → `0x49d9d0`；`0x49db72` → `0x49da20` | 全在 walker 簇内部（行走状态机 / 加载 / 构造路径） |

## 5. 反方向：脚本 → 原生（`Py_InitModule4` 的规模）

`Py_InitModule4` 在 `0x4e4850`，调用序列固定为
`push 0x3f5(=1013, PYTHON_API_VERSION) → push 0 → push 0 → push methods → push name → call`。
全镜像 **82 处**，其中 21 个是引擎模块（`C_*`），方法表直接可解：

| 模块 | 方法数 | 方法表 | 代表方法 |
|---|---|---|---|
| `C_sys` | 130 | `0x7db030` | `GetLibraryError`、`GetWindowHandle`、`CreateStretchFont`、`HotKeyEnable`、`WaitForVerticalBlank` |
| `C_audio` | 42 | `0x7e2508` | `InitAudio`、`PlayAudio`、`RecordAudio`、`IsAudioPlaying` |
| `C_imshare` | 27 | `0x7e29e8` | `InitAgent`、`InitAgentWithIds`、`HasShareValue` |
| `C_wwise` | 24 | `0x7e1968` | `SoundEngine_LoadBank`、`SoundEngine_SetPosition` |
| `C_imnet` | 14 | `0x7e10f8` | `Connect`、`SetCryptKey`、`PacketPrepare`、`PacketAddI/S`、`PacketSend`、`UnpackInt` |
| `C_misc` | 14 | `0x7e20e0` | `Snapshot`、`Switch`、`InitGLConfigInfo`、`CreateShareMemory` |
| `C_dgw` | 13 | `0x7e1888` | `GetVersion`、`AccessRequest`、`HttpSend` |
| `C_sound` | 11 | `0x7e2308` | `PlayMusic`、`PlaySample`、`SetMusicVolume` |
| `C_asyncloader` | 9 | `0x7e2260` | `AsyncLoadIgs`、`AsyncLoadPackage` |
| `C_debug` | 7 | `0x7db890` | `Print`、`ColorPrint`、`ReloadModule`、`CommandStat` |
| `C_cert` | 6 | `0x7e23c8` | `DYCERT_Init`、`DYCERT_CheckP12` |
| `C_scan` | 6 | `0x7e2438` | `SetScanRules`、`ScanPlugIn` |
| `C_log` | 5 | `0x7e21d0` | `FlushEngineLog`、`FileLog` |
| `C_marshal` | 5 | `0x7e24a8` | `dump`、`load`、`dumps`、`loads` |
| `C_net` | 3 | `0x7e1050` | `Ping`、`GetPingResult`、`DownloadFile` |
| `C_graphic` | 2 | `0x7e2230` | `LoadPlist`、`GetRealPath` |
| `C_maze` | 2 | `0x7e27b8` | `Create`、`Random` |
| `C_object` | 1 | `0x7df77c` | `EnumObjects` |
| `C_cef` | 1 | `0x7e1e6c` | `InitSettings` |
| `C_http` | 表未定位 | — | 名字串 `0x7e16a0` 存在，方法表不在 `Py_InitModule4` 参数里 |
| `C_RenderAgent` | 表未定位 | — | 名字串 `0x7e1fb8`，同上 |
| **合计** | **322** | | 最后两行方法表未定位，按 0 计 |

另外还有**第二类方法表**：`0x7e0ca0`（9 条：`GetCmd`/`GetCmdLen`/`UnpackString`/`UnpackBinaryString`…）
与 `0x7e0e00`（36 条：`CreateRecordFile`/`WriteRecordFile`/`Replay`/`Process`/`PacketSend`…）。
它们**不出现在任何 `Py_InitModule4` 的压栈序列里**，只被 `.rdata` 里 `0x7e0c54` / `0x7e0db4`
这样的位置（一个几乎全 0 的结构，`+0x54` 处）引用，判为运行期填充的**自定义类型/对象描述**
（`CNet` 包装对象那一侧）。没确证是标准 `PyTypeObject`——CPython 2.5 里 `tp_methods` 在 `+0x74`，
不是 `+0x54`，所以不硬套结构名。

## 6. 两个方向的交叉点

对全镜像里所有「名字 + 代码指针 + flags + doc」形状的记录（1,587 个不同实现函数）做了
**向下调用图**搜索（`E8` 目标 + 虚表槽当函数边界），看谁能走到 `0x4576b0`：

- **1 跳：0 条**。没有任何 `PyMethodDef` 实现直接调桥。
- **2 跳：3 条**（逐个反汇编核过）：
  - `CNetClient.ProcessServerCmd`（`0x467070`）→ `0x4ab870` → `OnServerCmd(int)` × 2
  - `CNetClient.Process`（`0x467490`）→ `0x4ab9a0` → `OnError()` / `OnConnectFail()`
  - `CNetClient.Replay`（`0x467270`）→ `0x4ab790` → `OnServerCmd(int)`

  （这三个不是 `C_net` 模块的函数，而是原生类型 `CNetClient` 的方法表条目——
  见 [mxmain_python_types.md](mxmain_python_types.md) §3.1。另：该类型 36 个方法里**没有**
  `OnServerCmd`，所以「脚本 `OnServerCmd` 调回原生同名方法」不存在，无重入。）
- 更深跳数会出现大量假阳性（函数边界一放大就把邻居的 call 算进来），**不采信**。
  尤其 `0x49bxxx` 那批 `SetAlpha`/`NextFrame`/`GetDirection` 名字，来自 §5 末尾说的
  「第二类方法表」被误当 `PyMethodDef` 的情形，已排除。

⇒ 结论：**脚本调原生（322 个方法）与原生回调脚本（8 个名字）是两条独立通道**。
想在脚本里挂引擎事件，只能盯这 8 个名字；想调引擎能力，看 §5 的模块表。
两者不重叠——没有「调用某个原生方法会同步回调同名脚本方法」的隐藏耦合。

## 7. 与既有材料的对照与更正

| 位置 | 原说法 | 本轮结论 |
|---|---|---|
| RTTI 笔记 §6 | `0x6b2434` 起是 `Can't get method:{}` | `0x6b2434 = "{} 函数无法获取"`；`0x6b2448 = "Can't get method:{}"`，相邻两槽 |
| RTTI 笔记 §6 | `OnConnected` 签名 `(i)` | `()`；`(i)` 是它邻居 `OnServerCmd` 的 |
| RTTI 笔记 §6 | 「代码引用点 `0x4ab7ac` 等」 | 那是**压栈**位置；`call` 在 `0x4ab7b2`，本文统一用 call 点 |
| RTTI 笔记 §6 | 已核 8 条名字 | 现在是 16 个调用点 / 8 个名字，且**穷举**（`E8` 全扫） |
| 2026-10-09 交接 | `0x2714` → `OnServerCmd(int)` | 证实；`0x2714` 是事件码，处理体 `0x4ac030`，跳表在 `0x4ac61c` |
| §6 旧标注 | 「`C_net.Process` / `ProcessServerCmd` / `Replay`」 | 是原生类型 **`CNetClient` 的方法**，不是 `C_net` 模块函数；且 `CNetClient` 无 `OnServerCmd` |
| 上一轮 STATUS | 「`KeepAlive`/`ShowWindow` 等同族可 xref」 | `KeepAlive(sI) 0x6bba00` 等的「名字+签名」相邻串里**没有** `call 0x4576b0`，不属于本桥；它们只是 `.rdata` 里的普通字符串/描述 |

## 8. 未解 / 边界

- `0x6b020c`、`0x6b0228` 两个 `.rdata` 函数指针槽：运行期才填，静态解析不出来。
  后者的调用出现在事件码 `10003` 分支，可能决定「是否把命令交给脚本」。
- `0x7e0c00` 一带的自定义类型描述结构：字段布局未确证，只能说「方法表在 `+0x54`」。
- `C_http` / `C_RenderAgent` 的方法表没出现在 `Py_InitModule4` 参数里，规模未知。
- `0x49d1xx`–`0x49d9xx` 的函数边界不可靠（无填充的热/冷块），宿主函数名未定。
- 桥的 `arg_fmt` 只见过 `()`、`(i)`、`(s)` 三种；`0x457e60` 支持哪些格式符未逐条验证。
- 本文**不**声称这 8 个名字是脚本侧必须实现的（缺实现只报一行错，不中断）。
- 不涉及 `_dyprot0/1`（54% 高熵壳区）——那里可能还有调用点，静态看不到。

## 9. 复现

```bash
# 1) 穷举 0x4576b0 的全部直接调用点，并读出压栈的名字/签名串
python3 - <<'PY'
import struct, sys
sys.path.insert(0, 'tools/data-parser')
import mxmain_rtti as M
img = M.PeImage(open('mxmain.dll', 'rb').read())
text = [s for s in img.sections if s.name == '.text'][0]
hits = []
for at in range(text.raw_offset, text.raw_offset + text.raw_size - 5):
    if img.data[at] != 0xE8:
        continue
    tgt = img.offset_to_va(at) + 5 + struct.unpack_from('<i', img.data, at + 1)[0]
    if tgt == 0x4576b0:
        hits.append(img.offset_to_va(at))
for site in hits:                      # 应是 16 条
    o = img.va_to_offset(site)
    strings = []
    for k in range(o - 28, o):         # 往回找 push imm32 的字符串
        if img.data[k] == 0x68:
            va = struct.unpack_from('<I', img.data, k + 1)[0]
            s = img.cstring(va, 64)
            if s:
                strings.append(s)
    print(hex(site), strings)
PY

# 2) 看某个调用点的实参
objdump -d --start-address=0x4ab790 --stop-address=0x4ab7d0 -M intel mxmain.dll

# 3) 看桥本体
objdump -d --start-address=0x4576b0 --stop-address=0x4577c0 -M intel mxmain.dll

# 4) 看事件分发跳表
objdump -d --start-address=0x4ac590 --stop-address=0x4ac620 -M intel mxmain.dll

# 5) 类/虚表侧的佐证（槽 22 属于谁）
python3 tools/data-parser/mxmain_rtti.py mxmain.dll --md /tmp/rtti.md
```

沙箱里没有 `file` / `pefile` / `capstone`，全部用 `struct` + `objdump` 完成；
`objdump` 对 `_dyprot*` 会报 `NOT_PAGED`，与本节结论无关。
