# P1 结果：会话密钥计算链（静态分析）

## 记录要求（7 项）

### 1. 执行者与会话
- **执行者**：Arena Agent Mode 当前会话；工具接口未提供可核验的 session ID。
- **工作分支**：`arena/70f1f176-mxsj-tw-2022`（开始和结束时均未切换分支）。
- **开始时间**：2026-10-10（UTC）；平台没有向本会话暴露收到任务的时分秒，故精确开始时刻未记录，不能补猜。
- **结束时间**：2026-10-10T10:28:32Z（UTC，结果写入并完成状态校验时记录）。

### 2. 输入校验（SHA-256）
下列是直接分析、对照或核对的输入文件；路径均相对于仓库根目录。`mx.exe` 与 `mxmain.dll` 的哈希相同，表明这两个文件在此工作区字节一致。

| 文件 | SHA-256 |
|---|---|
| `IMProtocol.dll` (187,216 B) | `bc356c88a6470d761b8976f8c027056b8c0e0f483ca2f59cf5c42542e112c82c` |
| `mx.exe` (9,698,712 B) | `637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d` |
| `mxmain.dll` (9,698,712 B) | `637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d` |
| `server.ini` (267 B) | `9ead627548a2e6705166a68598c3854ba8646fa16bb8f9d20a351aee95ab59a3` |
| `mx.ini` (138 B) | `43d7ee95cbf1dd00ea5f1b4ff463cf8de5c4747aba9738b0684c7f0b736a992f` |
| `mxbak.ini` (138 B) | `da164288af42eb76c90b5d3fdb9d32002e971ff84bb291588403df0b08355ea8` |
| `GameTmpData.ini` (65 B) | `6f9c0c89dca3c26d930fc7e244f2533c1c579e54bf4e7fc95bc8f3feba7a6608` |
| `HitRat.ini` (376 B) | `3f792e261ed89bcd65da567b0c3a85cd9077ea843d9eb0f9ed2408ecb8dd11e7` |
| `update.ini` (1,310 B) | `5c6d4a94f93379cb3f1092f27ca5ae05a1af9d403ea25262e89490bf2edd3059` |
| `work/dream-world-connect-login-map/notes/parallel-20261010/brief-P1-key-chain.md` | `d330c4ae73e645c3d5d3a57182e664b55696c028a2b9a0d327120a476f9dffa3` |
| `work/dream-world-connect-login-map/notes/parallel-20261010/README.md` | `d801c3cb79d8f5e936faeb8d38a01403e26ad9fd47da4bb611184436f8d80b28` |
| `work/dream-world-connect-login-map/notes/protocol-artifacts/im_crypto.py` | `721b19fd0462f081fd056488542fb5a7aaa0f34e48c2b80dc54b69f7b12c1d27` |
| `work/dream-world-connect-login-map/notes/protocol-artifacts/README.md` | `899cda73049e719041fd4d182a99cc4105d9289852a376dab325f3e8413c6725` |
| `work/dream-world-connect-login-map/notes/protocol-artifacts/key_sbox_0.bin` | `c08cc8a7483d1e4fd0965b35bb7648615fbb6028e4790a1e6ce2d2fc40c04801` |
| `work/dream-world-connect-login-map/notes/protocol-artifacts/key_sbox_1.bin` | `ac0c9fb70a0bc3e6996c1e2fdd32ef3bd4a85903497a7f8f2e7526b2a86197bb` |
| `work/dream-world-connect-login-map/notes/protocol-artifacts/key_sbox_2.bin` | `5519a2d56b0924f78d47cb6b16a4e2173c4d7bfd8e8e3c7fd4b0d3ad6d57a3ca` |
| `work/dream-world-connect-login-map/notes/protocol-artifacts/key_sbox_3.bin` | `c58b35c3d6348cc22d9addc5f17e46544652c7eeb81cbd71de47a83ec4eaecca` |
| `work/dream-world-connect-login-map/notes/protocol-artifacts/key_sbox_4.bin` | `fb8758c432138b7ea12b1509ef35e5d3fb973d876ef509c3b1222a9448cb71f2` |
| `work/dream-world-connect-login-map/notes/protocol-artifacts/key_sbox_5.bin` | `53688e2446a4ffc47b4548a0822d7d0c392cec4716b2d32ddc266a0f97a6a9f2` |
| `work/dream-world-connect-login-map/notes/protocol-artifacts/key_sbox_6.bin` | `e57e265d6a134b995e06a3ca2a5e7fa3200b2b39382d4810563b114cbe7646fe` |
| `work/dream-world-connect-login-map/notes/protocol-artifacts/key_sbox_7.bin` | `3996908fa1856ca57c8ed3fb03bfbf9bd1c5462c2f82a58ffd60daf692e07265` |
| `work/dream-world-connect-login-map/evidence/E-CRYPTO-001.md` | `e6fac3df8e7d3390fe4736dbdaa365ec9d8fb340f46252d9a13258836f68ed06` |
| `work/dream-world-connect-login-map/evidence/E-IDA-007.md` | `30eb03d7c36a7d023f636972a44e5a8fb2b24dcd4fbd7dada399a3f7a7d71d31` |
| `work/dream-world-connect-login-map/evidence/E-SCRIPT-001.md` | `decfd798ce3fef1e9323e631efee3e921cb39ac283e85be8123f3629bd1cb00a` |
| `work/dream-world-connect-login-map/evidence/mx.exe.json` | `ad2280dd69245b054af71e25a7b9491f943d6d9b1a4731ec92b6b52f9866acf7` |
| `work/dream-world-connect-login-map/evidence/rea-ghidra-mx-exe-20261009-1402.json` | `cd9d6743124a53caf55e23cae2a83e7693e7f76172e054928173cde66180143a` |
| `work/dream-world-connect-login-map/notes/crypto-analysis-complete.md` | `abb2b29e4c925d7bd29a6a0fc420c00b374a7721479838e20a2595a7e8b1fe04` |
| `work/dream-world-connect-login-map/notes/ida-protocol-interface.md` | `065f9798a2cd320a61210d5f013c86e00b1b952476756bff552d0d46903c3faf` |
| `work/dream-world-connect-login-map/notes/script-analysis-complete.md` | `6700ad325278171227aa87c91517f4892ad8be45dc8ee521ea0e417f317f8a6a` |
| `work/dream-world-connect-login-map/notes/agent-protocol-frame.md` | `1d6c0f94ba0a78918b077f5e3552c7cc1453feabfd985b62185b1dcd2d7ab1b2` |
| `work/dream-world-connect-login-map/notes/co_code_analysis/analysis_report.md` | `a3619df4a8c64d674b519024670c61a325d7141f7e772401fa3203bdcc70c93a` |
| `work/dream-world-connect-login-map/notes/co_code_analysis/cross_references.json` | `5ea5079d17b7601fbfaf8d410578d500692f025040a68c6c9c4a85cb6caa3396` |
| `work/dream-world-connect-login-map/notes/co_code_analysis/decoded_OnServerCmd.bin` | `a89755a6ad5269e50779cfc97ed8e7e8513df030aee583f557a5602b9fd4d904` |

以上文档及已有分析文件只作交叉核对；关于计算链的结论以本次读取的 PE 导出表、反汇编和字节为主。全树 `find` / 关键词检索仅用于定位，不将未逐项复核的匹配结果当作证据。

### 3. 工具与版本
- Python **3.11.2**（内联只读检查/哈希核对）。
- GNU `objdump` **Binutils 2.40**（PE 元数据、导出/导入表及 x86 反汇编）。
- GNU `sha256sum` **coreutils 9.1**。
- Capstone：当前 Python 环境中未安装；`/tmp/pevenv/bin/python` 不存在，因此**未使用 Capstone**。`file` 命令也未安装；PE 格式由 `objdump -f/-p` 核验。
- 未运行 Ghidra、游戏或任何网络客户端；未连接任何网络地址。没有运行 `im_crypto.py` 测试，也没有计算具体种子/密钥。

### 4. 执行步骤（只读，按实际顺序归纳）
1. 完整阅读本任务书 `brief-P1-key-chain.md` 和协调表 `README.md`；检查 `git status --short --branch` 与当前分支。
2. 对二进制、配置、任务书、参考代码、S 盒文件及相关已有证据计算 SHA-256；确认 `mx.exe` 与 `mxmain.dll` 哈希相同。
3. 用 `objdump -f IMProtocol.dll`、`objdump -p IMProtocol.dll` 核对 PE32/i386、ImageBase 和导出表；用 `objdump -D -Mintel --start-address=0x10002e80 --stop-address=0x10003220 IMProtocol.dll` 检查导出实现及初步提到的辅助地址。
4. 用 `objdump -D -Mintel --start-address=0x10001770 --stop-address=0x10001a80 IMProtocol.dll` 和 `--start-address=0x10005b00 --stop-address=0x10005c90` 复核字符串解析、上下文初始化及密钥派生；用 `objdump -s --start-address=0x10021650 --stop-address=0x100216c0 IMProtocol.dll` 核对格式字符串字节。
5. 用 `objdump -p mx.exe` 检查 IMProtocol 导入；以 `objdump -D -Mintel mx.exe`、对 IAT VA 的文本检索及内联 Python 原始字节扫描寻找直接调用引用。该负向检索只用于说明“未定位到”，不作为“绝无调用者”的证明。
6. 只读查看 `server.ini`、`mx.ini` 等配置，以及 `im_crypto.py` 和关联分析文档；逐一比较 `key_sbox_0.bin`—`key_sbox_7.bin` 与 `IMProtocol.dll` 中 `0x10026448` 起的 8 个 256 字节表，八组均逐字节相同。
7. 未保存任何临时分析脚本；未对仓库文件执行写入、删除、重命名或移动。

### 5. 地址与依据表

| 地址 / 文件 | 直接观察 | 证据与界限 |
|---|---|---|
| `IMProtocol.dll` 导出表；ImageBase `0x10000000` | `IMP_RefreshCryptKey` 的导出 RVA 为 `0x3110`，VA 为 `0x10003110`；`0x100030d0` 对应 `IMP_UnConnectNsServer`。 | `objdump -p IMProtocol.dll` 的 Export Address/Name Pointer 表。故旧参考脚本中 `0x100030d0` 的刷新密钥映射不正确。 |
| `0x10003110`–`0x10003146` | 首参数从栈取出并作 NUL 结尾长度扫描；随后把指针和长度交给 `0x10002eb0`，构造/赋值内部字符串对象。 | `IMProtocol.dll` 反汇编；入口处 `mov edx,[esp+0x20]`（函数已保留本地栈，等价于首栈参数），长度扫描在 `0x1000312d`–`0x1000313b`，调用在 `0x10003141`。 |
| `0x10003172`、`0x1000317d` | 长度 `< 8` 跳过刷新；长度 `>= 8` 时以内部字符串对象地址调用 `0x10001770`。 | `IMProtocol.dll`：`cmp [esp+0x1c],8` / `jb` / `lea ecx,[esp+8]` / `call 0x10001770`。这是代码中的最小长度门槛，不等于已经证实完整解析了 8 个字节。 |
| `0x10001770`、`0x10021678` | 函数接收字符串对象（ECX）；依据容量从内联区或堆指针取字符串；格式串是八个连续的 `%02X`，解析结果的低 8 位依次拷入 8 字节临时种子。 | `IMProtocol.dll` 反汇编 `0x100017a0`–`0x100017de`、拷贝循环 `0x100017f0`–`0x100017fe`；`.rdata` 地址 `0x10021678` 的字节为 `%02X` 重复八次。未看到解析成功计数被检验后才使用这 8 个槽位。 |
| `0x10001900`–`0x10001964`；`0x10028b2c`、`0x10028b30` | 两次以 `0x0c` 为尺寸调用分配 helper；两次都把同一临时种子传给 `0x10005b80`，返回对象分别写入两个全局指针，最终 AL 返回 `1`。 | `IMProtocol.dll` 反汇编：两次 `push 0xc`/调用分配 helper、两次 `call 0x10005b80`（`0x10001911`、`0x10001931`），全局写入在 `0x1000191c`、`0x1000193a`。两个上下文分别承担何种方向仍未证实。 |
| `0x10005b80`；`0x10026448`–`0x10026b48` | 初始化 12 字节上下文状态为 0，把 8 字节输入复制到偏移 4；第 0 字节直接查 S-box 0，后续第 i 字节按 `S_i[previous_derived XOR seed[i]]` 链式替换。 | `IMProtocol.dll` 反汇编 `0x10005b80`–`0x10005c1b`；8 张表地址由指令中的绝对地址直接给出。逐字节比较确认参考目录 8 个 256 B 文件与 DLL 对应表相同。 |
| `0x1000314b`–`0x10003170`；`0x10028b8c` | 导出函数确实有受 `0x10028b8c` 标志保护的一次性分支，置标志并调用 `0x1000857c`。这属于一次性 helper/初始化路径，不是密钥派生本身。 | `IMProtocol.dll` 反汇编。`0x1000857c` 的内部语义本次未继续确认。`0x100083f8` 在堆存储释放分支中被调用，具体堆实现不影响密钥公式。 |
| `mx.exe` PE 导入表；IAT RVA `0x00a1b238` / VA `0x00e1b238` | 主映像静态导入 `IMP_RefreshCryptKey`；`mx.exe` 与 `mxmain.dll` 完全相同。未解析到可信的实际调用函数或参数生产点。 | `objdump -p mx.exe`；`evidence/mx.exe.json:872-879`（导入项名称与 VA）；`E-IDA-007.md:21-31` 也明确导入表不证明调用、参数或时序。对直接 IAT call 形式的静态搜索未得到可验证调用点，且受保护段/间接调用可能性使负向结果不充分。 |
| 脚本与配置 | 已有脚本 API 汇总列出 `RefreshCryptKey(key)` 到原生导入的映射，但这不是实际调用点；来源与交换时机仍列为未解决。配置读到服务器地址/端口等，没有发现可直接指认为会话密钥的字段。 | `notes/script-analysis-complete.md:273-293`（尤其 `:282`、`:292`）；`server.ini:1-10`、`mx.ini:1-10`。配置未出现明文字段只属有限的未发现，不证明没有间接配置或服务器来源。 |

### 6. 未完成与未证实清单
1. **真实调用者/调用点未证实**：确认了 `mx.exe` 导入该 API，但没有确认 `mx.exe` 中哪个函数实际调用、谁构造首参数，或脚本是否在运行路径中调用它。需要能解析受保护主映像的函数级 xref/反编译，或可信的运行时调用栈证据。
2. **参数来源未证实**：不能区分本地常量、配置/脚本值、网络服务端数据；要区分需追踪 `0x10003110` 的 caller-side 参数数据流，或仅在获准的本地测试环境对入口参数做记录。当前未做动态分析。
3. **服务器首包时序未证实**：未找到实际 caller 与收包路径的连接关系，因此不能写成“首包之后调用”或“首包之前调用”。
4. **输入完整性边界未证实**：导出层的长度门槛为 8，但格式有 8 个 `%02X` 转换（完整 8 字节通常需 16 个十六进制字符）；本次静态片段未见转换数/解析返回值校验。长度为 8–15、含非十六进制字符或解析不完整时的种子内容不作推断。
5. **会话密钥值未证实且未计算**：没有得到真实传入字符串或其解析种子；本结果不猜测、不生成、不记录任何实际密钥值。
6. 两个全局上下文指针的发送/接收角色以及 0x1000857c 的完整内部语义均未确认。

### 7. 修改记录
- **本次唯一写入**是本任务要求的新产物 `work/dream-world-connect-login-map/notes/parallel-20261010/P1-result.md`。
- 未修改 `mx.exe`、`mxmain.dll`、`IMProtocol.dll`、`server.ini`、任何 `tools/` 下工具代码或任何已有文档；未删除、重命名或移动文件。未运行游戏、未访问/连接任何网络地址；未提交 Git commit。

---

## 结论摘要

**结论摘要（已证实 / 未证实）**：已证实 `IMP_RefreshCryptKey`（`0x10003110`）把调用者传入的 NUL 结尾字符串经八组 `%02X` 转成 8 字节种子，再经 8 张 Key S-box 的链式 XOR 替换初始化两个独立上下文；调用者、种子来源及其是否来自服务器首包均未证实，故不报告实际密钥值。

## 密钥计算链与伪代码

### 已证实的计算顺序

1. `IMP_RefreshCryptKey` 首参数是调用者提供的 NUL 结尾字符串指针。入口计算 `strlen`，将指针与长度交给 `0x10002eb0` 建立内部字符串对象。
2. 内部字符串长度小于 8 时不调用刷新子程序；达到 8 时，调用 `0x10001770`。这里的 8 是代码门槛，不是对 8 个完整字节输入的充分验证。
3. `0x10001770` 取字符串数据并按地址 `0x10021678` 的格式串 `%02X%02X%02X%02X%02X%02X%02X%02X` 解析到 8 个整型临时槽，再将每槽低字节拷到 8 字节临时种子。解析调用后未见检查成功转换个数。
4. 子程序对同一临时种子创建两个 12 字节缓冲区；每个缓冲区状态字段为 0，偏移 4–11 是派生后的 8 字节密钥。两次派生分别存入 `0x10028b2c` 与 `0x10028b30`。
5. `0x10005b80` 的查表链为：
   - `derived[0] = KeySbox[0][seed[0]]`
   - `derived[i] = KeySbox[i][derived[i-1] XOR seed[i]]`，`i = 1..7`

### 伪代码（输入有效且 8 个转换均成功时）

```text
function IMP_RefreshCryptKey(source_c_string):
    n = strlen(source_c_string)
    text = internal_string_assign(source_c_string, n)   # 0x10002eb0
    if text.length < 8:
        return 0
    return refresh_from_text(text)                       # 0x10001770

function refresh_from_text(text):
    # 直接证实：格式串有八个 %02X，输出参数是八个整型槽。
    parsed[0..7] = scan(text, "%02X" repeated 8 times)
    seed[i] = low_8_bits(parsed[i]) for i in 0..7

    for slot in [global_0x10028b2c, global_0x10028b30]:
        ctx = allocate(0x0c)
        if ctx != NULL:
            ctx.state = 0
            ctx.key[0] = KeySbox[0][seed[0]]
            for i in 1..7:
                ctx.key[i] = KeySbox[i][ctx.key[i - 1] XOR seed[i]]
        slot = ctx

    return 1
```

**边界说明**：伪代码的 `parsed[0..7]` 仅在 8 个扫描转换成功时有完整确定值。虽然 `%02X` 重复八次显示这是“十六进制文本 → 八字节种子”的预期路径，但最小长度仅检查 8，且未见解析返回值校验；不能据此断言任何任意长度不少于 8 的字符串都能产生确定、完整的 8 字节种子。

## 与 `im_crypto.py` 的只读对照

- **派生公式一致（已证实）**：`im_crypto.py:55-85` 的 `derive_key` 使用 12 字节工作区、状态置 0、种子放在偏移 4，并实现相同的首字节 S-box 替换和后续链式 XOR/S-box。对应 DLL 汇编为 `0x10005b80`–`0x10005c1b`；8 张 `key_sbox_*.bin` 与 DLL 的 `0x10026448` 起始表逐字节相同。
- **包装层差异（已证实）**：Python `derive_key(seed)` 接收原始字节种子；DLL 导出先接收字符串，再以八个 `%02X` 解析，且对派生结果各建立一个独立 12 字节上下文。Python 方法本身不覆盖这层文本解析和双上下文重置流程。
- **默认值不是实密钥**：`im_crypto.py:20-28` 将 `bytes(range(8))` 明确作为默认占位值；文件中的示例种子/测试密钥也不是本次获得的游戏参数。本次没有运行这些测试或据此生成密钥。
- **导出地址映射需更正（只报告、不修改）**：`im_crypto.py:188` 将 `IMP_RefreshCryptKey` 写成 `0x100030d0`；本次 PE 导出表确认该 VA 是 `IMP_UnConnectNsServer`，刷新密钥导出实际为 `0x10003110`。`im_crypto.py:207` 的 `derive_key=0x10005b80` 与本次汇编相符；`:211` 的 `init_crypto=0x10001770` 只概括了子程序用途，未体现其文本解析和双上下文处理。

## 调用者与服务器数据依赖判断

- **DLL 内部已定位的调用**：`0x10003110` 在 `0x1000317d` 调用 `0x10001770`；这是导出函数内部调用，不是导出函数的外部调用者。
- **主映像仅证实静态导入**：`mx.exe` 的导入表包含 `IMP_RefreshCryptKey`（IAT RVA `0x00a1b238`；ImageBase `0x00400000` 下 VA `0x00e1b238`）。当前 `mx.exe` / `mxmain.dll` 各自字节相同。反汇编与原始字节的直接 IAT-call 搜索未得到可验证调用点；受保护段和间接调用等可能性意味着这不是“没有调用者”的证明。
- **脚本层仅证实接口映射，不证实实际调用**：已有 `notes/script-analysis-complete.md:282` 列出 `RefreshCryptKey(key)` → `IMP_RefreshCryptKey`，但该表不是脚本字节码调用点；同一文档 `:292` 仍把密钥来源/交换时机列为未解决问题。故脚本是否调用、调用位置与时序均未证实。
- **服务器数据依赖未证实**：DLL 此计算链把 caller-provided string 作为数据输入；未在该导出链中观察到直接收包或读取 `server.ini` 的步骤。但由于 caller 与参数数据流没有恢复，字符串可能由本地或服务器路径提供，不能二选一。也无法判断调用发生在服务器首包前后。
- **配置检查的有限结论**：`server.ini` 可见内容是服务器/端口条目；`mx.ini` 可见内容是客户端选项和最后选择的服务器，没有读到可直接认定为密钥的字段。这只能说明这些已检查文本中没有显式密钥字段，不能排除配置的其他形式或运行时服务器来源。
