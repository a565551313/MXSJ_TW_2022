# mxmain 给脚本的原生接口：静态能拿到多少（类型 + 方法 + 使用率）

> 分支 `arena/4d3d51ac-mxsj-tw-2022`｜日期 2026-10-26｜输入 `mxmain.dll`（只读）
>
> 前两篇：[`mxmain_rtti_class_map.md`](mxmain_rtti_class_map.md)（305 类 / 305 虚表）、
> [`native_script_callbacks.md`](native_script_callbacks.md)（原生→脚本 16 个调用点）。
> 这篇回答缺的那半边：**引擎到底把哪些「类」和「方法」交给了脚本**，以及
> **哪些拿得到、哪些静态拿不到**。

## 1. 摘要

1. 原生给脚本的接口有**三条通道**，价值依次递减：
   ① `Py_InitModule4` 注册的**函数模块**（82 处，上一轮已解）；
   ② `.rdata` 里的**静态 `PyTypeObject`**（本篇新解，189 个骨架，其中 **9 个是引擎类**）；
   ③ **运行期构造**的类与模块（`tp_name` / `tp_methods` 指向 `.data` 未初始化区，文件里是 0，静态拿不到名字）。
2. 9 个引擎原生类型，静态可数方法表的 6 个：`CNetClient`(36)、`CIMShare`(19)、`CServerCommand`(9)、
   `CShadowObject`(1)、`CObjectCommand`(1)，加 `CWwiseEngine`（方法表在 `.data` 运行期区，数量未知）；
   `CCefObject`/`CPopen`/`CPreloadObject` 确无方法。这是**脚本能继承的原生类型**里唯一能静态确认的一批。
3. 紧挨着 `CShadowObject` 有 **27 个形状相同、名字为空的类型骨架**（`0x7df7a0`–`0x7e0b20`，步长 `0xc0`），
   几乎可以肯定是 `interface` 模块的对象类表，但 `tp_name` / `tp_methods` 都在
   `.data` 尾部（文件里全 0）⇒ **名字和方法名要运行期才有**。
4. 上一轮说的「21 个原生模块 / 322 个方法」是**下界**：脚本里还 `import` 了
   `C_slot` / `C_sharemem` / `C_math` 三个模块，它们的名字在明文里 **0 命中** ⇒ 同一类运行期构造。
5. 322 个方法里，681 个已反编译脚本只**按限定名**用到了 **81 个（283 次调用）**，
   241 个在语料中零引用 —— 这是判断「哪些原生 API 值得写文档/写 mock」的第一手依据。
6. **勘误（推翻上一轮两处）**：`Process` / `ProcessServerCmd` / `Replay` 不是 `C_net` 模块的方法，
   而是 **`CNetClient` 类型的方法**；`CNetClient` 的 36 个方法里**没有 `OnServerCmd`** ⇒
   上一轮担心的「脚本 `OnServerCmd` 调回原生同名方法会造成重入」**不存在**，那是一次纯 Python 的父类调用。

## 2. 三条通道

| 通道 | 形态 | 规模 | 静态可得 | 例 |
|---|---|---|---|---|
| A. 函数模块 | `push name → push PyMethodDef[] → call Py_InitModule4(0x4e4850)` | 82 处 | 名字 + 全部方法名 + 实现地址 | `C_sys.GetTime`、`C_audio.PlayFile` |
| B. 静态类型 | `.rdata` 里的 `PyTypeObject`，`+0x0c`=tp_name，`+0x74`=tp_methods | 189 个骨架 / 9 个引擎 | 名字 + 方法名（6 个引擎类方法与表同静态） | `CNetClient`、`CServerCommand` |
| C. 运行期构造 | 同样的骨架，但 `tp_name`/`tp_methods` 指向 `.data` 尾部（文件内为 0） | 27 个 `interface` 类 + ≥3 个模块 | **不可得**（只有骨架与 `tp_init`） | `interface.CMapWalkerObject`、`C_slot` |

判定通道 B/C 的可靠指纹（CPython 2.5 的字段偏移，已在 `CNetClient` 上自证）：
`+0x0c`=tp_name、`+0x10`=tp_basicsize、`+0x14`=tp_itemsize(=0)、`+0x18`=tp_dealloc(代码)、
`+0x54`=tp_flags(引擎类恒 `0x205eb`)、`+0x74`=tp_methods、`+0x94`=tp_init、`+0x9c`=tp_new。
`CNetClient` 的 `tp_dealloc=0x466ef0` 与它 36 个方法地址全落在 `0x467090`–`0x468400`，
`tp_methods=0x7e0e00` 正是上一轮标为「第二类方法表、无主」的那张表。

## 3. 9 个能静态确认的引擎原生类型

9 个全部有明文 `tp_name`（都在 `.rdata` 的 `0x6bxxxx` 段），`tp_flags` 恒 `0x205eb`。
注意 `CWwiseEngine` 的方法表指针也落在 `.data` 运行期区——**同一个「名字/表在运行期填」的机制，
连具名类型也会用到**：

| 类型 | PyTypeObject | tp_name 串 | basicsize | tp_dealloc | tp_methods | 方法数 |
|---|---|---|---|---|---|---|
| `CShadowObject` | `0x7df6b8` | `0x6b489c` | 12 | `0x465b00` | `0x7df698` | 1 |
| `CNetClient` | `0x7e0be0` | `0x6b4a64` | 12 | `0x466ef0` | `0x7e0e00` | **36** |
| `CServerCommand` | `0x7e0d40` | `0x6b4b38` | 12 | `0x467040` | `0x7e0ca0` | 9 |
| `CWwiseEngine` | `0x7e1af8` | `0x6b5b00` | 12 | `0x46a8f0` | `0x833f80`（运行期填） | ? |
| `CIMShare` | `0x7e2928` | `0x6b7928` | 12 | `0x47ed10` | `0x7e27e8` | 19 |
| `CCefObject` | `0x7e40a8` | `0x6bb478` | 16 | `0x4af270` | 0 | 0 |
| `CPopen` | `0x7e4168` | `0x6bbb08` | 20 | `0x4b4600` | 0 | 0 |
| `CPreloadObject` | `0x7e4298` | `0x6bbdd0` | 16 | `0x4b5780` | 0 | 0 |
| `CObjectCommand` | `0x7e4378` | `0x6bbe84` | 12 | `0x4b7d70` | `0x7e4358` | 1 |

189 个骨架的构成：**9 个引擎类**（上表）+ **56 个 CPython 标准类型**（`dict`/`list`/`unicode`/`file`/`set`/
`Struct`/`MultibyteCodec`…，名字都在 `.rdata` 里能读出来）+ **27 个 §4 的 interface 骨架** + **97 个无名骨架**
（`0x7e6xxx`–`0x7fxxxx` 的 CPython 区，多为 structseq / 子类型，名字同样运行期填）。

56 个标准类型能整齐命中，本身就是扫描器的自证：口径错了的话 `dict`/`list`/`file`
这些不可能同时读出名字和正确的方法表。

### 3.1 `CNetClient`（36 个方法，完整）

```
CreateRecordFile  CloseRecordFile  WriteRecordFile  Replay  Process  ProcessServerCmd
Connect  Disconnect  GetCmdLen  UnpackString  UnpackBinaryString  UnpackInt
PreUnpackInt  PreUnpackString  UnpackLong  UnpackSignedChar  UnpackBit  PacketPrepare
PacketAddL  PacketAddI  PacketAddS  PacketAddBinaryS  PacketSend  NakedSend
GetPacketData  GetNotProcessDataBytes  IsSent  GetLastErrInfo  GetErrCode
SetMaxLenBytes  SetSeed  SetSeed2  SetRecvCache  SetSendCache
SetProcessSvrCmdNumPerFrame  Pause
```

**没有 `OnServerCmd`。** 这条直接解决上一轮 §3 里那个「同名两层会不会重入」的担心——
脚本侧的 `net.CNet.OnServerCmd(self, icmd)` 是 Python 父类调用，不是回调进原生。

### 3.2 `CServerCommand`（9 个方法，完整）

`GetCmd`、`GetCmdLen`、`UnpackString`、`PreUnpackString`、`UnpackBinaryString`、
`UnpackInt`、`PreUnpackInt`、`UnpackSignedChar`、`UnpackBit`

这正是原生→脚本回调 `OnServerCmd(int)` 里那个 `int` 的来源对象：
桥在 `0x4ab790` 等处只把 `[cmd+4]` 的一个字节传过去，脚本要真读包得靠这个类型的方法。

### 3.3 与回调链的拼合（现在闭环了）

```
CNetClient::ProcessServerCmd        (0x467070，脚本每帧调)
   └─ 0x4ab870  取 [this+0xc] 命令链，读 [cmd+4] 命令号
        └─ bridge 0x4576b0 → obj.OnServerCmd(byte)      ← 脚本层 CNet.OnServerCmd
             └─ 脚本按 cmd 分发 → CServerCommand.GetCmd/Unpack*   ← 读包体
```

`Process` / `Replay` 是同一模式的另两个入口（`Process` 还会在状态码 `6`/`8` 时回
`OnConnectFail` / `OnError`）。**签名、方向、谁调谁，全部有地址。**

## 4. 27 个「拿不到名字」的 `interface` 类型骨架

`0x7df7a0` 起，步长 `0xc0`，共 27 个，形状完全一致：

| 字段 | 值 | 说明 |
|---|---|---|
| `tp_basicsize` | `0x10` | 只有 4 个指针宽：C++ 对象指针、引用计数、以及两个保留位 |
| `tp_new` | `0x4659c0`（全部相同） | 统一分配器，内部再按类型调 `tp_init` |
| `tp_dealloc` | `0x4659f0` | 统一释放 |
| `tp_init` | **每类不同**（`0x465be0`、`0x465ca0`、`0x465c40`…） | 每个 init 只做一件事：调本类的 C++ 构造/绑定函数 |
| `tp_name` | → `0x82b4e0`, `0x82ba00`, … 步长 `0x520` | **`0x82xxxx` 是 `.data` 的未初始化尾部，文件里是 0** |
| `tp_methods` | → `0x82b530` … 同区 | 同上，运行期才填 |

`va_to_offset()` 对 `0x82b4e0` 返回 `None`（超出 `.data` 的 raw 大小、落在 vsize 内），
就是「这块内存文件里没有内容、加载后才写」的硬证据。对照：`CNetClient` 的 `tp_name`
`0x6b4a64` 在 `.rdata` 里，能直接读出字符串 `CNetClient`。

**所以「`interface.CMapWalkerObject` 这类名字在哪」的静态答案是**：
不在文件里。它在启动时被写进 `0x82b4e0` 起的缓冲区——最可能的来源是 RTTI 类型名
（`CMapWalkerObject` 全镜像只在 `. ?AVCMapWalkerObject@@` 里出现 1 次，没有独立明文副本），
但**这一步没有直接证据，属于推断**。

可留作运行期核对的锚点（27 个 `tp_init`，按骨架地址升序）：

```
0x465be0 0x465ca0 0x465c40 0x465d60 0x466000 0x465e20 0x465c10 0x465d30 0x466090
0x465d00 0x466060 0x465cd0 0x465e50 0x465fd0 0x466030 0x465eb0 0x4660c0 0x465f10
0x465ee0 0x465df0 0x465f70 0x465dc0 0x465e80 0x465c70 0x465fa0 0x465f40 0x465d90
```

## 5. 322 个原生方法，脚本到底用了多少

统计口径：`tools/decompiler/output/` 下 **681 个已反编译 `.py`**（13.6 MB 文本），
按 `C_<模块>.<方法名>` 的**限定名做文本匹配**。所以下表数的是**限定名出现的次数**，
不是「实际调用语句数」——赋值 `f = C_sys.GetTime`、把方法当参数传、以及注释里提到
都算一次。要精确到调用表达式得另外解析 AST，本表没做（有意保守：
任何一次出现都说明脚本在用这个名字）。语料只是 5,135 个脚本条目的一部分，
所以「零引用」只代表**这批语料里没出现**，不等于游戏里没调用。

| 模块 | 方法数 | 被引用的方法数 | 限定名出现次数 | 高频项 |
|---|---|---|---|---|
| `C_sys` | 130 | 41 | 200 | `GetTime`×53、`GetObjects`×21、`IsKeyDown`×21、`LoadFile`×19 |
| `C_cert` | 6 | 6 | 26 | `DYCERT_Init`×5、`DYCERT_GetPCInfo`×5 |
| `C_sound` | 11 | 7 | 16 | `SetMusicVolume`×4、`StopSample`×4 |
| `C_dgw` | 13 | 9 | 11 | `StopEcho`×2、`GetDelay`×2 |
| `C_wwise` | 24 | 4 | 9 | `SoundEngine_GetIDFromString`×5 |
| `C_log` | 5 | 4 | 6 | `FileLog`×2、`GetPyLogPath`×2 |
| `C_debug` | 7 | 2 | 5 | `ColorPrint`×3 |
| `C_audio` | 42 | 4 | 4 | `PlayFile`、`PausePlayFile`、`StopPlayFile` |
| `C_marshal` | 5 | 1 | 3 | `loads`×3 |
| `C_misc` | 14 | 2 | 2 | `CreateShareMemory`、`DestoryShareMemory` |
| `C_net` | 3 | 1 | 1 | `DownloadFile` |
| `C_object` / `C_imnet` / `C_cef` / `C_graphic` / `C_asyncloader` / `C_scan` / `C_maze` / `C_imshare` | 62 | 0 | 0 | — |
| **合计** | **322**（下界） | **81** | **283** | **241 个零引用** |

两个读法：

- `C_sys` 是真正的主 API（占全部限定名出现次数的 71%），`C_imshare`（27 个方法）/`C_asyncloader`（9 个）
  虽然方法多，但语料里一次都没按限定名出现过 —— 大概率是**引擎内部**或**运行期按名导入**（见 §1 第 4 条）。
- 但 `C_object` 完全是另一种情况：脚本里 **163 处**用到它，却**没有一处**是 `C_object.<方法>`，
  因为它的属性是**类型**——`C_object.CTextObject`、`CBaseObject`、`CRichTextObject`、
  `CImagesObject`、`CDisplayLinkDirector`、`CSpriteFrameCache`、`CBoxObject`……
  这些类不在任何 `PyMethodDef` 表里，189 个静态骨架里也没有可读的同名类型 ⇒
  与 §4 同一类（名字运行期填，可能就在那 97 个无名骨架里）。

## 6. 静/动态的边界（本篇最重要的结论）

> **能在静态确定的**：21 个 `C_*` 函数模块的模块名/方法名/方法地址；9 个引擎原生类型里
> 6 个的类型名与全部方法表（`CNetClient` 36、`CIMShare` 19、`CServerCommand` 9、
> `CShadowObject` 1、`CObjectCommand` 1）；以及这些方法谁调谁、什么时候调。
> **静态确定不了 / 只是下界**：`CWwiseEngine` 的方法表指针落在 `.data` 运行期区；
> 27 个 `interface` 类型对象的名字与方法、`C_slot`/`C_sharemem`/`C_math` 三个模块的内容、
> 以及 `C_object` 暴露的那批类；`C_http`/`C_RenderAgent` 的方法表没定位。
> 它们共享同一个机制：**名字在 `.data` 尾部、启动时写入**。

这条边界比「再多挖几个地址」有用：它告诉后来者**该在哪里停手**——想拿这部分，
只能改成「运行期在客户端进程里 dump `interface.__dict__` / 各模块 `dir()`」，
纯静态再挖下去收益接近 0。

## 7. 复现

```bash
# 1) 扫静态 PyTypeObject 骨架（按 CPython 2.5 字段偏移 + tp_flags 指纹）
python3 - <<'PY'
import struct, sys
sys.path.insert(0, 'tools/data-parser')
import mxmain_rtti as M
img = M.PeImage(open('mxmain.dll', 'rb').read())
d = img.data
FLAGS = {0x205eb, 0x205fb, 0x201eb, 0x241eb, 0x245eb, 0x245fb, 0x241fb}
def code(v): return v and img.section_role(v) == 'code'
hits = []
for sec in img.sections:
    if sec.role not in ('rtti', 'type_descriptors'):
        continue
    for at in range(sec.raw_offset, sec.raw_offset + sec.raw_size - 0xA0, 4):
        va = img.offset_to_va(at)
        if (img.u32(va + 0x14) == 0 and code(img.u32(va + 0x18))
                and img.u32(va + 0x54) in FLAGS and 0 < (img.u32(va + 0x10) or 0) < 0x20000):
            nm = img.u32(va + 0x0C)
            name = img.cstring(nm, 64) if img.section_role(nm) in ('rtti', 'type_descriptors') else None
            hits.append((hex(va), name, hex(img.u32(va + 0x74) or 0)))
print(len(hits))            # 期望 189
print([h for h in hits if h[1]][:5])
PY

# 2) 看某个类型对象
objdump -d --start-address=0x467070 --stop-address=0x4670b0 -M intel mxmain.dll   # CNetClient::ProcessServerCmd

# 3) 方法使用率（粗口径）
grep -rhoE '\bC_sys\.[A-Za-z_]+' tools/decompiler/output --include=*.py | sort | uniq -c | sort -rn | head
```

## 8. 边界

- 语料是 5,135 个脚本条目里的 681 个，**「零引用」≠「没用」**。
- 27 个 `interface` 类型与 3 个模块的名字是**推断为运行期构造**，没有直接证据看到写入代码（写入方应在
  `_dyprot*` 保护区内），所以「源自 RTTI 名」只是最省事的解释，**不是结论**。
- 未做：`tp_getset` / `tp_members`（属性访问器）没解——那是下一个可能的增量点。
- 全程静态、只读；未启动客户端、未监听端口。锁定输入按 `sha256sum` 核对过：
  `mxmain.dll` = `637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d`，
  `data/script.fls` = `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`，
  `tools/decompiler/script_fls_keys.json` = `43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb`。
