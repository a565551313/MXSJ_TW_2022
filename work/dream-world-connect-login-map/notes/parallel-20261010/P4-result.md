# P4 结果：脚本层连接后的发送顺序与 H1

## 1. 执行者与会话

- 执行者：Arena.ai Agent，P4 独立静态分析会话。
- 开始记录时间：2026-10-10T10:22:25+00:00（UTC；首次显式时间记录，任务书及协调表已先完整阅读）。
- 结束分析、生成结果时间：2026-10-10T10:26:25+00:00（UTC）。
- 实际工作分支：`arena/3aec5bd4-mxsj-tw-2022`；HEAD：`52ef64db1f41dded659c0ced141edb17662926d5`。会话固定在此分支，未切换到用户提及的 `arena/febc1561-mxsj-tw-2022`；前者从该基点派生。
- 范围：本地只读静态分析；未运行游戏、未连接任何网络地址、未启动监听服务、未提交或推送。

## 2. 输入校验

下表为本次读取内容的全部仓库文件，路径相对于仓库根目录。目录枚举不算读取其中每个文件的内容；未读取游戏可执行文件或 DLL，故不虚列这些文件的哈希。工具导入使用 `PYTHONDONTWRITEBYTECODE=1`，不生成缓存。

| 输入路径 | SHA-256 |
|---|---|
| `work/dream-world-connect-login-map/notes/parallel-20261010/brief-P4-login-flow.md` | `3920be30952299cb1a2043cab69e38caf2307ca459ad8600108afe6ae9f21ce6` |
| `work/dream-world-connect-login-map/notes/parallel-20261010/README.md` | `d801c3cb79d8f5e936faeb8d38a01403e26ad9fd47da4bb611184436f8d80b28` |
| `work/dream-world-connect-login-map/notes/task-b-脚本分析/artifacts/fullrun/decode-results-final.jsonl` | `25781bd230432d03b9870440cf76b96c792d09282b3f2721c8fe6f5bf3e3f03f` |
| `work/dream-world-connect-login-map/notes/co_code_analysis/netserver_py_decompiled.md` | `0fe4c39cc36b0721fdf18dcc331527826483b2c43163ff1efb96459f2fcba8b4` |
| `work/dream-world-connect-login-map/notes/script-analysis-complete.md` | `6700ad325278171227aa87c91517f4892ad8be45dc8ee521ea0e417f317f8a6a` |
| `work/dream-world-connect-login-map/notes/protocol-commands-values.md` | `35276f1da0f4cb02aac12c1a2177f03c23bd01896c73f2619de46f05d2a7663b` |
| `work/dream-world-connect-login-map/notes/co_code_analysis/任务A深入-Connect函数破解报告.md` | `4f51522a900130ae37034b9dfdbf4eea0171dee209002df3baa499e2a73920b5` |
| `work/dream-world-connect-login-map/notes/co_code_analysis/code_objects.json` | `ee5f9ef62d65139fc39e30486acfa835d917f8a0cd43a46438270b8574417aaf` |
| `work/dream-world-connect-login-map/notes/co_code_analysis/decoded_functions_v2.json` | `8ef7cacb01d9dfaa1250e3176ea2be8dee63a5cec0df79d00a43f0397c794ca2` |
| `work/dream-world-connect-login-map/notes/co_code_analysis/decoded_results.json` | `bea14f2ef9b9e70023465fefe34fe73e8c117743038dc2402502b83d9484c792` |
| `work/dream-world-connect-login-map/notes/co_code_analysis/mapping_table_v4.json` | `6b6d3c281c9af835a35a25e0779e1b20b87aad78fdad8b96f7d076fe2ff96d37` |
| `work/dream-world-connect-login-map/notes/loopback-test-plan-20261010.md` | `b7c17d725351ec735a303e8370efcff774cdf73b75be942ae01859f527fac574` |
| `work/dream-world-connect-login-map/notes/task-b-脚本分析/artifacts/t516/entry516.marshal.bin` | `59b8d64760ce26728c6a8e39f37e7509973310efd61c8150ea0b0e70ce6ff6b9` |
| `work/dream-world-connect-login-map/notes/task-b-脚本分析/artifacts/t516/entry516.info.json` | `00e6449fed835fd876b9a23d4274a54bde69b4d3cb7da73e13c4fbc53129e15e` |
| `work/dream-world-connect-login-map/notes/decoder-artifacts/entry516-five-xor-marshal.bin` | `956b10875b586d47810315a489c7a43afcaee9f29d0864fbde2354306877b736` |
| `tools/pymarshal_dis.py` | `e959aabd017736c431763a3ea5e6c662910692a44ee72349ea77f85a96ebdd34` |
| `tools/fls_batch_decoder.py` | `eaadba011aeb45bd976b25ddf2c234ca20e8ad8dc89c20144a53ef44e6df721f` |
| `data/script.fls` | `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72` |

校验补充：`decode-results-final.jsonl` 实数为 **5002 条，ok 4484、fail 272、suspect 246**。它仅含模块、函数名、解码参数及状态等元数据，**不含函数指令正文**；不能凭 `status=ok` 断言完整控制流已恢复。

为取得直接字节依据，只读 `data/script.fls`，按 final JSONL 中指定的边界和密钥在内存中恢复以下记录；没有重跑自动搜索、没有写回解码结果或新 artifacts：

| final `index`（零基）/ JSONL 行号（一基） | 模块 | 压缩数据在 script.fls 内的十进制文件偏移 / 长度 | 内存 marshal 长度 / 代码对象数 | 内存 marshal SHA-256 |
|---|---|---|---|---|
| 516 / 517 | `script\login\netserver.py` | 16321274 / 7690 | 17234 / 59 | `59b8d64760ce26728c6a8e39f37e7509973310efd61c8150ea0b0e70ce6ff6b9` |
| 4082 / 4083 | `script\login\netlogin.py` | 20157783 / 13869 | 33671 / 71 | `596bbc2895d32b8d916ff97cd4fbf2e5fa2d1942006a6b8543285c04d9f62fef` |
| 4844 / 4845 | `script\login\selectserver.py` | 20775075 / 18932 | 42611 / 67 | `7400b379ff8802084c69864d8200ff88fc8d04261309d34a2e38310f298ab714` |
| 4076 / 4077 | `script\login\dgwconnecttest.py` | 11191098 / 8331 | 19342 / 64 | `fb2a2ad9abd4f848efb63134ffcd2cb93fedab2bc6855a518d052216968db171` |

上述记录均为 `ok`，marshal 解析耗尽完整输入。DGW 只检查了相关函数名表和元数据，不把其完整发包行为写成结论。entry 516 的内存输出与 `artifacts/t516/entry516.marshal.bin` **逐字节相同**。

旧 `decoder-artifacts/entry516-five-xor-marshal.bin` 与 t516 **不相同**；旧 `code_objects.json` 中 59 个对象的 `co_code_hex`，只有对象 #27 `S2CServerRoleInfo` 与 t516 不同，其余一致。该对象从 co_code 偏移 21 起已有差异。本报告使用与 final 参数匹配的 t516 / 内存输出，不拿旧对象 #27 的损坏指令作结论。

## 3. 工具与版本

- Python：**3.11.2**；仅执行本地分析代码，不执行恢复出来的游戏代码。
- capstone：**未安装，未使用**；未安装任何依赖。
- 字节码反汇编：仓库 `tools/pymarshal_dis.py`，无独立发行版本，以本节输入哈希和 HEAD 标识；使用 `tools/fls_batch_decoder.py::MarshalReader` 解析 marshal。
- opcode 映射：`mapping_table_v4.json` 内标注 **`4.3-taskB`**（该文件第 358 行），工具内置 CPython 2.6 编号表；没有把 Python 3 的 `dis` 用于游戏字节码。
- 原生反汇编工具：未使用；本任务不给出原生地址或 Winsock 运行行为结论。
- 工具限制：`pymarshal_dis.py:130–137` 对未知指令默认猜长度，可能造成后续错位；映射仍有不确定项（如 `mapping_table_v4.json:226–231` 的条件跳转、319–325 的多义指令）。因此只采信有原始字节、常量/名字表及栈调用形状相互吻合的局部片段；不能拿未知区段后面的自动输出当成完整 CFG。

## 4. 实际执行步骤

1. `pwd`、`git status --short`，完整 `cat` 任务书及协调表；初始工作树干净。
2. `date --iso-8601=seconds`、`git branch --show-current`、`git rev-parse HEAD`、`python3 --version`；用 `importlib.metadata` 检查 capstone，无安装动作。
3. 用 `hashlib.sha256` 核对必读输入；以 `nl -ba` 阅读三份既有报告，核对其中的推测与证据声明。
4. 用 `json.loads` 扫描全部 final JSONL，统计状态、定位 netserver 及相关模块；用 `find`/`ls` 枚举既有分析产物。未执行枚举出的游戏或网络工具。
5. 读取旧 Connect 报告、旧 JSON 指令结果和 `code_objects.json`，检查旧结论来源；阅读本地 marshal 工具、v4.3 映射及 H1 原始定义。
6. 运行 `PYTHONDONTWRITEBYTECODE=1 python3 tools/pymarshal_dis.py …/t516/entry516.marshal.bin --code-only Connect --consts`，并以同一工具在内存中查看相关函数，发现未知 opcode 导致的错位，不更改工具或映射来掩盖问题。
7. 通过只读 `extract_entry` + final 的 `keys/bounds` 在内存复算四个条目，检查输入耗尽、哈希、对象序号；将 t516 与旧 marshal / code_objects 比较。未调用解码器的批处理写文件入口。
8. 按 `co_firstlineno + co_lnotab` 定位原脚本行号；按局部已对齐的 co_code 字节、名字表和常量表核对构造参数、发包调用、条件检查。核心复现代码见附录。
9. 仅新建本结果文件；最后检查 `git status`/`git diff` 和输入哈希，不提交，由协调者统一处理。

## 5. 地址与依据表

**定位约定**：下表 `E` 是 final 的零基 `index`；`#` 为 `MarshalReader.code_objects` 的一基后序对象序号（entry 516 对应 `code_objects.json` 的 index）；`@` 是该函数 co_code 的**十进制字节偏移，不是虚拟地址或命令字**。脚本行号来自 marshal 的行号表，不是伪代码报告的 Markdown 行号。所有原始数据都可由 §2 文件哈希及附录复现。

| 结论编号 | 结论与分级 | 文件、函数、行号 / 字节定位 |
|---|---|---|
| E1 | 有依据：`loginhello` 在 Connect 中是导入模块；`TEST_HELLO` / `RESELECT_HELLO` 是构造器 `iType` 参数来源，不是此处的 PacketSend 调用 | `netserver.py:376–377,392`，E516 #46 @0–23、221–244；`:443–444,457`，#52 @18–29、255–278 |
| E2 | 有依据：CMXNet 构造器把类型存入 `m_NetType`，并调用 `net.CNet.__init__` | `netserver.py:241–243`，E516 #29 @0–34 |
| E3 | 有依据：可见直接连接调用；代理路径也出现 Connect 和随后 NakedSend；连接成功后的真实第一包未证实 | `netserver.py:403,406,409`，E516 #46 @368–401、436–464、550–565；`:473,476,479`，#52 @467–500、535–563、649–664 |
| E4 | 有依据：显式选服构包/发送三步，且该函数无收包检查 | `netserver.py:233–237`，E516 #28 @0–54；特别 @9–24、25–40、41–50 |
| E5 | 有依据：TransferServer 调用选服发包后显示连接提示；不是在此等待后再发 | `netserver.py:200–202`，E516 #24 @83–109 |
| E6 | 有依据：OnServerCmd 检查属性存在性，非 `m_Hello` 真值；ProcessServerCmd 另查失败状态和 hello 真值 | `netserver.py:250–251`，E516 #31 @0–42；`:511–516`，#58 @0–75，@75 的后续控制语义未完全恢复 |
| E7 | 有依据：S2CHello 先解包 seed，再 SetSeed，再设置 `m_Hello=True`；后有裸发送调用锚点，完整表达式未证实 | `netlogin.py:338,340–345,349`，E4082 #25 @0–97、135–205 |
| E8 | 有依据：角色信息处理与条件转服链有调用锚点；不等同于“服务器地址列表” | `netserver.py:224,227–230`，E516 #27 @0–14、40–69、84–97；`:158,160–164`，#19 @24–136 |
| E9 | 有依据：候选列表检查、刷新和提前返回；E3 条件跳转极性未证实 | `netserver.py:378–385`，E516 #46 @24–90；`selectserver.py:96–103`，E4844 #7 @12–85；`:262–263`，#11 @0–35 |
| E10 | 有依据：失败置位与超时回调重试；不能据此证明现场超时或确切时长 | `netserver.py:254,257,262,265`，E516 #32/#33；`:412`，#46 @592–601；`:421–423`，#48 @9–72；`:419`，#47 @0–13 |
| E11 | 有依据：重连/快速登录回调含 `IsSent()` 检查；不是首次发送前的收包判断 | `netlogin.py:357–359`，E4082 #22 @0–51；`:370–373`，#23 @0–66 |
| E12 | 有依据：其他连接入口也只见构造、置 hello 状态、Connect；未提供成功后首包实现 | `selectserver.py:234–235,240,247–249`，E4844 #10 @63–86、140–155、313–331 |
| E13 | 有依据：既有六步总流程不是可直接采纳的完整反编译 | `notes/co_code_analysis/netserver_py_decompiled.md:256–265`；`notes/script-analysis-complete.md:118–140` 自称推测；旧 Connect 报告 `:26–44,97–99,127–128` 与 E1 的 IMPORT_NAME / 关键字参数证据冲突 |
| E14 | 有依据：H1 原文为“收到服务端数据后才发送 loginhello”；该必要前提仍缺证据 | `notes/loopback-test-plan-20261010.md:15`；final JSONL 全部 5002 行无文件名尾部为 `net.py` 或 `loginhello.py` 的记录，E516 #29 在基类处形成缺口 |

## 6. 未完成与未证实清单

1. **H1 未证实，结论：无法判断。** 缺少 `net.CNet` 的构造/Connect/连接成功回调/OnServerCmd 实现、`loginhello` 模块实现，以及它们与实际网络发送的调用关系。final 中没有这些文件名的记录不代表它们不存在：可能未恢复、位于别处或在原生层；具体归属未证实。
2. **连接成功后的第一条 C→S 消息及其发送函数未证实。** 不能把构造参数、模块名或“脚本中找到的某个 PacketSend”当成线上第一包；还缺连接完成、接收、发包的完整跨层时序。
3. **首发前是否必等服务器数据未证实。** 已见的 `hasattr`、`m_Hello`、`IsSent` 各在不同上下文；尚无证据把它们接到“首包发送”之前。需上述缺失实现的控制流/调用图。已有离线运行轨迹若能覆盖这些事件也可用于验证，本任务不采集运行数据。
4. **完整登录全序、S2CHello / S2CServerRoleInfo 的命令分发表绑定未证实。** 缺完整分发器、回调来源及对不同连接对象的归属证明；这两个处理函数不能强行排成同一连接上的固定先后顺序。
5. **“卡住”的现场原因、是否永久等待、超时数值未证实。** 本报告只列静态可见检查点；缺对应状态变化、计时器实现/值、现场分支和收发记录。
6. **未知 opcode、条件极性和部分后续控制流未证实。** 特别是 E3 跳转、S2CHello 裸发送表达式中的运算、ProcessServerCmd @75 之后；需可靠映射及完整栈/跳转校验，不能借旧伪代码补齐。
7. **S2CServerRoleInfo 的完整容器赋值、线上字段格式及其是否构成强制选服门槛未证实。** 有 UnpackInt 和 SetServerRoleInfo 调用，但部分 opcode 未解；需完整恢复和分发/调用证据。
8. **所有 C→S 命令数值、裸发送对应的命令名、实际发送成功与加密行为未证实。** 本文只用符号名，不采用旧协议表的数值或缺失样本；需要命令定义/赋值来源、底层实现或有出处的原始证据。

## 7. 修改记录

- 唯一新增文件：`work/dream-world-connect-login-map/notes/parallel-20261010/P4-result.md`。
- 未修改任何游戏文件、`data/script.fls`、已解码 artifacts（尤其 `decode-results-final.jsonl`）、工具代码或已有文档；未更新协调表、workitems、timeline、evidence 或其他任务结果。
- 没有删除、移动、重命名文件；未创建分支、提交或推送。
- 内存复算和反汇编输出仅显示在终端；未保存额外脚本或中间文件。
- 结束核验：18 个输入文件 SHA-256 全部与 §2 一致；`git diff --exit-code` 通过，`git status --short` 仅列本新增结果文件；复现 Python 代码通过语法检查。

---

## 8. 四个问题的直接回答

### 8.1 连接成功后第一条消息是什么，由谁发出？

**未证实，不能给出确定的“首条消息符号名 + 发送函数”。**

有依据的最接近事实是：

- 随机测试对象的构造为 `CMXNet(ip, port, iType=loginhello.TEST_HELLO)`；重选对象为 `CMXNet(ip, port, iType=loginhello.RESELECT_HELLO)`（E1）。原始调用的两个位置参数加一个关键字参数，以及常量 `'iType'`，排除了旧报告的“配置字典 + 多个位置参数”说法。**这里只能证实类型选择，不证明已发送这些符号对应的包。**
- 可完整还原的显式带命令符号发包是 `C2STransferServer`（E4），但它属于选服，**不是已经证明的连接后第一包**：

```python
# netserver.py:233–237；E516 #28；仅表示脚本 API 调用，不是底层已发送成功
# 2 是 PacketAddI 的第二个参数，不是命令字数值；其底层含义不在本任务断言。
def C2STransferServer(serverid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_SELECT_SERVER)
    netobj.PacketAddI(serverid, 2)
    netobj.PacketSend()
```

旧报告省略了 `PacketAddI` 的第二个参数，并把 `netobj` 写进函数形参；marshal 显示该函数 `argcount=1`，`netobj` 是局部变量。以字节和参数表为准；不修改旧文档（待协调者核对）。

### 8.2 首发前是否判断“等待服务器数据”？

**全局答案未证实**；不能由一个局部函数没有检查推导整个客户端不等待。

1. `C2STransferServer` 全长 55 字节中没有条件分支、Unpack、接收或等待检查，直接构造并调用发送（E4）。这仅回答“进入该函数之后”的局部顺序。
2. `CMXNet.OnServerCmd` 的判断是 `hasattr(self, 'm_Hello')`（E6），不是 `if not self.m_Hello: wait`。初始化已写入 `m_Hello=False`，属性存在与其真值是两回事；此处又是命令回调，不是已经证明的首发入口。
3. 外层 `ProcessServerCmd` 先检查 `m_IsFail == False`，再调用对象的 `ProcessServerCmd()`，之后检查 hello 属性/真值（E6）。所以不能将后面的 hello 检查改述成“所有发包必须先等待 hello”。
4. `netlogin.S2CHello` 确有 **UnpackInt → SetSeed → m_Hello=True → 后续 NakedSend 调用锚点**（E7），说明该处理路径存在依赖解包数据的后续动作。这是“某些后续动作依赖输入”的证据，**不是“连接建立后没有任何先发消息”的证据**。其完整裸发送参数表达式和分发触发点未证实。
5. `DelayConnect` / `DelayQuickLogin` 查询的是 `IsSent()`（E11），不能解释成 `IsReceived()`；它们还是 S2CHello 内建立的后续回调，不是初次建立连接的完整入口。

### 8.3 有几种可能的“卡住”点？

本次区分 **6 类排查点**，不是宣称游戏存在 6 个已证实死锁。第 1、5 类的强制等待关系未证实；其余有相应判断/回调，但是否造成现场停滞一律未证实。

| 类别 | 对应判断或调用 | 可确认内容 / 尚缺证据 |
|---|---|---|
| 1. 首包之前等服务端 | 缺失的 `net.CNet` / `loginhello` 路径；E2、E14 | **未证实**；当前无法定位这样的代码行，不能拿后面的 m_Hello 检查代替。缺完整首发实现。 |
| 2. 服务器/代理候选不足，刷新或返回 | `CRandomConnectMgr.Connect` 中 serverlist、proxylist 检查，Refresh、return；E9 | 检查点和返回存在。E3 极性仍未证实，故不把旧伪代码的 `if serverlist` 当真；也未证明是在等当前 TCP 连接下发服务器列表。相关 `selectserver` 有独立的列表读取/刷新路径。 |
| 3. 连接失败或超时重试 | `m_IsFail` 置位、外层跳过失败对象；`SetTimeOutCmd`、`nexttest`；E6、E10 | 状态与重试调用有依据。何时触发、多久切换、是否关闭旧连接及现场命中情况未证实。 |
| 4. hello 状态/分发进展未完成 | `hasattr(m_Hello)`、`m_Hello` 真值检查；`S2CHello` 写 True；E6、E7 | 检查与赋值有依据。不同对象间的归属、外层检查后的完整退出行为、是否影响首发均未证实。 |
| 5. 角色信息或选服条件未满足 | `S2CServerRoleInfo → SetServerRoleInfo`；后者检查 `m_ServerInfo`、禁入列表、角色信息成员资格，再可能调用 `TransferServer`；E8、E5 | 调用及比较锚点有依据，自动转服的完整布尔表达式受 E3 限制；强制等待关系、UI 是否实际卡住未证实。不要称它为“收到服务器地址列表后才首发”。 |
| 6. 重连/快速登录的发送状态检查 | `DelayConnect` / `DelayQuickLogin` 的 `IsSent()` 与返回路径；E11 | 后续检查存在，但 E3 极性及调度器如何重复调用未证实。不能归因于等待服务器首包。 |

### 8.4 H1：支持 / 反对 / 无法判断？

**选择：无法判断（H1 未证实）。**

H1 原文是“客户端在收到服务端数据后才发送 loginhello（服务端先发）”。证明它需要覆盖初始连接、底层成功回调、首个发送点及此前全部前置条件。当前 `netserver.py` 在 `CMXNet.__init__` 的 `net.CNet.__init__`（242 行）与对象 `Connect`（403/409、473/479 行）处跨入未提供的实现，且 final 无 `net.py` / `loginhello.py` 文件名记录，证据链在此中断。

- **不能支持为事实**：`S2CHello`（`netlogin.py:338–349`）的先解包后续动作，不排除它是客户端已经发过握手之后收到的响应；也不能证明这就是该连接的服务端首包。
- **不能反对为事实**：选服函数（`netserver.py:234–237`）无接收判断，不代表它的调用前没有前置握手；类型构造（392/457 行）更不是实际先发证据。
- 因此，旧六步流程里的“Connect 发送 loginhello/TEST_HELLO”以及从中推导“客户端一定先发”均为**未证实**。本任务也不把 H1 改写为已经成立的“服务端一定先发”。

## 9. 有依据的流程偏序图（不虚构完整时序）

### A. 随机测试 / 重选连接准备

1. `RandomConnect()` 创建 `CRandomConnectMgr` 并调用 `Connect()`（E516 #54，`netserver.py:483–486`，@0–18）。
2. `CRandomConnectMgr.Connect` 导入模块、取 serverlist/proxylist、检查候选并可能刷新或返回（E1、E9）。
3. 构造 `CMXNet(..., iType=loginhello.TEST_HELLO)`，写 `m_Hello=False` / `m_IsFail=False`；重选分支改用 `RESELECT_HELLO`（E1、E2）。
4. 可见直接 `Connect(ip, port)` 的片段；代理侧另有 Connect 与 NakedSend 片段（E3）。这些都是 API 调用顺序，不是“连接成功事件已到达”的证据。裸发送不能强行命名为 loginhello，也不能与直接连接分支串成一条必经路径。
5. **缺口：底层如何完成连接、是否自动握手、第一条线上消息是什么。未证实。**
6. 外层处理命令和状态；随机连接路径安排超时回调，再次 Connect（E6、E10）。

### B. 角色信息到选服发送的局部链

1. 进入 `S2CServerRoleInfo` 后，解包 cnt、serverid、rolenum；尾部调用 `SetServerRoleInfo(roleinfo)`（E8；对象 #27 @84–97 为独立对齐调用片段）。
2. `SetServerRoleInfo` 保存信息并检查 `net.g_Net` 是否有 `m_ServerInfo`；后有禁入/角色成员比较及 `TransferServer(..., autoenterselrole=True)` 的条件调用，其他路径进入登录 UI 相关调用（E8）。完整布尔极性未证实。
3. `TransferServer` 保存选择状态，调用 `C2STransferServer(serverid)`，再 `ShowConnectingDlg()`（E5）。
4. `C2STransferServer`：`PacketPrepare(C2GS_SELECT_SERVER) → PacketAddI(serverid, 2) → PacketSend()`（E4）。

此链证明某些角色信息处理路径可导致选服发送，**不证明所有选服入口必须先收到该信息，也不证明它在 A 的第一次 TCP 连接上发生**。

### C. hello 处理后的局部链

1. `netlogin.S2CHello` 解包 seed 等值（E4082 #25，338、340、341 行）。
2. `net.g_Net.SetSeed(seed)` → `net.g_Net.m_Hello=True`（344–345 行）。
3. 349 行有 `netobj.NakedSend` 调用锚点；完整参数运算及对应协议名称未证实，不生成猜测的首包。
4. 后续检查重连、快速登录属性，建立对应延迟回调；通常 UI 路径调用 `selectserver.Show(False)`、隐藏提示、`loginin.ShowLogin()`（379–386 行）。回调中再检查 `IsSent()`（E11）。

**B 与 C 的先后以及它们与 A 的对象绑定，未证实；不能拼接成一张假装完整的线性登录图。**

## 10. 与旧文档冲突的待核对项（不覆盖旧证据）

- 旧报告 `netserver_py_decompiled.md:259–264` 把 `showlogin` 当起点；实际 marshal 显示它是 `ShowConnectingDlg` 的嵌套函数，并在显示消息框时作为回调传入（E516 #26，@48–54、81–99）。其全部闭包语义仍有未知项，不能仅凭函数名断言它启动初次连接。
- 旧 Connect 报告用字典构造解释 `selectserver/loginhello`；v4.3 的 IMPORT_NAME 与参数表显示是模块导入和属性读取（E1）。
- 旧 `m_Hello=是否已发送hello` 解释（旧 Connect 报告 180 行）不够：`S2CHello` 解包后也写该状态（E7）。不能赋予此属性唯一的“已发”或“已收”协议含义。
- `S2CServerRoleInfo` 读取 serverid / rolenum，不可直接改名“服务器地址列表”。`selectserver.GetServerInfo` 另见 `g_ServerList` / `ServerInfo()` / `Refresh(None)`，且 `ServerInfo` 对象名表包含 OpenFile/read/SERVERINI（E4844 #6，起始 76 行）。列表具体来源及分支全解未完成，但足以要求区分两类信息。
- 不采用旧报告的 NakedSend 端口字节顺序来判断 H1。可见代理连接片段与直接连接片段不是单一无分支流程，未知运算和底层发送时机需要 P3/原生层另行核对。

## 附录：核心只读复现命令

以下在仓库根目录执行，仅读输入并打印标准输出；不创建临时文件，不运行游戏代码、不访问网络。`dis_code` 的未知/错位输出必须按 §3 限制人工核对。

```bash
pwd
git status --short
git branch --show-current
git rev-parse HEAD
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 tools/pymarshal_dis.py   work/dream-world-connect-login-map/notes/task-b-脚本分析/artifacts/t516/entry516.marshal.bin   --code-only Connect --consts
```

```python
# 用 PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY' 执行本段，不另存脚本。
import sys, json, hashlib
from pathlib import Path
from collections import Counter
sys.path.insert(0, 'tools')
from fls_batch_decoder import extract_entry, MarshalReader
import pymarshal_dis as dis

b = Path('work/dream-world-connect-login-map/notes')
p = b / 'task-b-脚本分析/artifacts/fullrun/decode-results-final.jsonl'
rows = [json.loads(s) for s in p.read_text().splitlines()]
print(len(rows), Counter(r['status'] for r in rows))
archive = Path('data/script.fls').read_bytes()
selected = {
    516: [19, 24, 26, 27, 28, 29, 31, 32, 33, 46, 47, 48, 52, 54, 58],
    4082: [22, 23, 25],
    4844: [6, 7, 10, 11, 12],
    4076: [15, 34, 47],
}
for index, objects in selected.items():
    row = next(r for r in rows if r['index'] == index)
    entry = extract_entry(archive, index)
    exp = entry['exp']
    bounds = [0] + list(map(int, row['bounds'].split(','))) + [len(exp)]
    keys = bytes.fromhex(row['keys'])
    blob = b''.join(bytes(v ^ k for v in exp[a:z])
                    for a, z, k in zip(bounds, bounds[1:], keys))
    reader = MarshalReader(blob)
    reader.read()
    assert reader.pos == len(blob)
    print(index, entry['doff'], entry['clen'], len(blob),
          hashlib.sha256(blob).hexdigest(), len(reader.code_objects))
    if index == 516:
        assert blob == (b / 'task-b-脚本分析/artifacts/t516/entry516.marshal.bin').read_bytes()
        old = json.loads((b / 'co_code_analysis/code_objects.json').read_text())
        print('different co_code objects:', [a['index'] for a, c in
              zip(old, reader.code_objects) if a['co_code_hex'] != c['code'].hex()])
    for ordinal in objects:
        c = reader.code_objects[ordinal - 1]
        print('E', index, '#', ordinal, c['name'], c['firstlineno'], c['names'])
        if index == 4076:
            continue  # 本次 DGW 仅核对相关函数元数据
        print(dis.dis_code(dis._conv(c)[1], consts=True))
        addr, line = 0, c['firstlineno']
        points = []
        for da, dl in zip(c['lnotab'][::2], c['lnotab'][1::2]):
            addr += da
            line += dl
            points.append((addr, line))
        print('co_lnotab address/line:', points)
        print('co_code:', c['code'].hex())
for name in ['net.py', 'loginhello.py']:
    matches = [r['index'] for r in rows
               if r.get('filename', '').replace('\\', '/').split('/')[-1] == name]
    print(name, matches)
```

本报告不附任何伪造命令号或首包数据，不把不确定反汇编自动升级成已证实协议。
