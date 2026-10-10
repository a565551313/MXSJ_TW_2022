# P2 结果：发包路径（静态分析）

> 范围：离线、只读静态分析。没有启动游戏、没有连接任何网络地址。除本新建结果文件外，不修改任何二进制、配置、工具代码或既有文档。

## 记录要求（七项）

### 1. 执行者与会话
- 执行者：Arena.ai Agent Mode（当前会话；独立 session ID 未提供）。
- 时区：UTC。
- 开始：`2026-10-10T10:26:04Z`（本轮可取得的首个 UTC 时间记录点；工具未提供更早的会话启动时间）。
- 结束：`2026-10-10T10:31:39Z`（最终工作区/输入哈希校验时间）。

### 2. 输入校验
下表列出本结果直接使用或引用的文件及其 SHA-256。`mx.exe` 与 `mxmain.dll` 逐字节相同，因此只反汇编 `mx.exe`。`server.ini` 只计算哈希作只读校验，没有分析其内容。

| 文件路径 | SHA-256 | 备注 |
|---|---|---|
| `work/dream-world-connect-login-map/notes/parallel-20261010/brief-P2-send-path.md` | `a4c62e78a723fa4712c4a4805129ff378fa182602c979b28742d48c730fe6171` | P2 任务书 |
| `work/dream-world-connect-login-map/notes/parallel-20261010/README.md` | `d801c3cb79d8f5e936faeb8d38a01403e26ad9fd47da4bb611184436f8d80b28` | 协调表及通用规则 |
| `work/dream-world-connect-login-map/notes/loopback-test-plan-20261010.md` | `b7c17d725351ec735a303e8370efcff774cdf73b75be942ae01859f527fac574` | H1–H3 来源 |
| `IMProtocol.dll` | `bc356c88a6470d761b8976f8c027056b8c0e0f483ca2f59cf5c42542e112c82c` | MD5 `5db0412c3c3a2142f723baf930cc8593` |
| `mx.exe` | `637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d` | MD5 `2609423fe7fadd5446eb2425ab894ac8` |
| `mxmain.dll` | `637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d` | 与 `mx.exe` SHA-256/MD5 均相同；未重复反汇编 |
| `server.ini` | `9ead627548a2e6705166a68598c3854ba8646fa16bb8f9d20a351aee95ab59a3` | 仅哈希校验，未读配置内容 |
| `work/dream-world-connect-login-map/evidence/mx.exe.json` | `ad2280dd69245b054af71e25a7b9491f943d6d9b1a4731ec92b6b52f9866acf7` | PE 导入表静态记录 |
| `work/dream-world-connect-login-map/evidence/rea-ghidra-improtocol-20261009-1235.json` | `565cd417bedcefc433c520291753168785e6b1fdd91c216736dbb6e19b47a311` | 保留的 Ghidra 静态分析记录 |
| `work/dream-world-connect-login-map/evidence/rea-ghidra-improtocol-20261009-1244.json` | `7cb2d0a19b0bb0fa3798a2a7287e3a2f86e0618fcd7c1c5b1d0c7a343c5ec898` | 保留的连接路径静态记录 |
| `work/dream-world-connect-login-map/evidence/rea-ghidra-mx-exe-20261009-1241.json` | `f8233806f418140f0c8d00679ad5e375be9a4d48a84b90f480387d6ce24a54a4` | 保留的主映像 IAT xref 查询 |
| `work/dream-world-connect-login-map/evidence/rea-ghidra-mx-exe-20261009-1402.json` | `cd9d6743124a53caf55e23cae2a83e7693e7f76172e054928173cde66180143a` | 保留的主映像函数分析记录 |
| `work/dream-world-connect-login-map/evidence/E-IDA-007.md` | `30eb03d7c36a7d023f636972a44e5a8fb2b24dcd4fbd7dada399a3f7a7d71d31` | 主映像导入表观察及限制 |
| `work/dream-world-connect-login-map/evidence/E-REA-002.md` | `836b6fe24b00390652a34c771be2ac5a9e82d3be6ac0355196073f949b0eaa78` | `IMP_ConnectNsServer` 静态链及通道角色限制 |
| `work/dream-world-connect-login-map/evidence/E-LOOPBACK-001.md` | `fb7d73f1d085f4ea0a01f3b45222e3774d750caa4126f962bad507a03441cfc2` | 10-09 回环捕获记录 |
| `work/dream-world-connect-login-map/evidence/E-LOOPBACK-002.md` | `267f29f9131a0838d013f58583db6edf026e7377e015b54e2f6ad83be9b9527e` | 10-09 Established/0 字节记录 |
| `work/dream-world-connect-login-map/evidence/E-LOOPBACK-003.md` | `a67019554f3a939a2c11acfe7256a0e8aeac526729b02051cf1c8e4e646023f7` | 10-10 用户报告及限制 |
| `work/dream-world-connect-login-map/evidence/E-IDA-DYN-004.md` | `9a58f9342797ed17cd2a4e68be89f8e146cfbe061f91a1bd0dd332236f5e97a3` | `00 02` 回环探针的既有动态记录 |

哈希清单仅列直接使用/引用的输入与证据；仓库范围的文本搜索仅用于定位，不将其未列出的命中内容作为结论依据。

### 3. 工具与版本
- Python：`3.11.2`，用于只读解析既有 JSON 记录及扫描 PE 原始字节。
- Capstone：当前环境未安装（`import capstone` 得到 `ModuleNotFoundError`），本次未使用，版本不适用。
- 反汇编器：GNU `objdump`，GNU Binutils `2.40`（PE 导入/导出、节区、x86 反汇编及只读数据查看）。
- 既有分析快照：Ghidra `12.1.4`（仅读取上表中已存在的 JSON；本轮没有启动 Ghidra/REA，也没有重新生成快照）。

### 4. 执行步骤
1. 完整阅读 P2 任务书及协调表；再阅读 H1–H3 所在的 `loopback-test-plan-20261010.md`。
2. 查看当前分支、工作区状态与目标文件大小；对目标二进制、任务文件及所用静态/回环证据计算 SHA-256/MD5。
3. 使用 `objdump -h/-p` 确认 PE 节区、导出 RVA、导入序号与主映像 IMProtocol 导入项。
4. 使用 `objdump -d` 查看 IMProtocol 的导出包装、加密分支、发送路径、连接路径和 Winsock 调用；使用 `objdump -s` 检查 socket 虚表对应的数据。
5. 只读解析现有 Ghidra JSON 的函数记录/xref；对 `mx.exe` 的 `IMP_SendBuffer2NS` IAT 绝对地址做原始字节查找，区分“未找到直接引用”和“程序未调用”。
6. 将反汇编与任务书列出的假设、既有回环观察逐项对照；全程没有执行二进制、启动游戏或建立网络连接。

复现所用主要命令（路径均相对于仓库根目录）：

```sh
python --version
objdump --version
sha256sum mx.exe mxmain.dll IMProtocol.dll server.ini
md5sum mx.exe mxmain.dll IMProtocol.dll
objdump -h IMProtocol.dll
objdump -p IMProtocol.dll
objdump -p mx.exe
objdump -d IMProtocol.dll --start-address=0x10003000 --stop-address=0x10003320
objdump -d IMProtocol.dll --start-address=0x10001720 --stop-address=0x10001b10
objdump -d IMProtocol.dll --start-address=0x10001970 --stop-address=0x10001a10
objdump -d IMProtocol.dll --start-address=0x100020e0 --stop-address=0x10002160
objdump -d IMProtocol.dll --start-address=0x10005f50 --stop-address=0x10006030
objdump -d IMProtocol.dll --start-address=0x10006010 --stop-address=0x10006370
objdump -d IMProtocol.dll --start-address=0x10004560 --stop-address=0x10004700
objdump -d IMProtocol.dll --start-address=0x10004100 --stop-address=0x10004170
objdump -s -j .rdata --start-address=0x10021cf0 --stop-address=0x10021d20 IMProtocol.dll
```

原始 IAT 地址查找使用的只读 Python 逻辑：读取 `mx.exe` 字节，对导入槽虚拟地址 `0x00E1B29C`（`IMP_SendBuffer2NS`）、`0x00E1B2A0`（`IMP_EncryptBuffer`）、`0x00E1B23C`（`IMP_ConnectNsServer`）等打包为 little-endian DWORD 后查找；本次这些地址均没有原始字节命中。该检查只排除相同绝对地址形式的直接引用，不排除间接调用、运行时解包/重定位或动态分发。

### 5. 地址与依据表

| 编号 | 结论/事项 | 地址或文件依据 |
|---|---|---|
| A1 | 导出映射：`IMP_ConnectNsServer` RVA `0x3000` / VA `0x10003000`；`IMP_EncryptBuffer` RVA `0x31F0` / VA `0x100031F0`；`IMP_SendBuffer2NS` RVA `0x3240` / VA `0x10003240`。 | `IMProtocol.dll` SHA-256 见上表；`objdump -p IMProtocol.dll` Export Address/Name Pointer Tables。 |
| A2 | `IMP_SendBuffer2NS` 的包装在 `0x10003270` tail-jump 到 `0x10001AA0`。`0x10001AA0` 检查描述符非空（`0x10001AA4–0x10001AA6`）、数据指针非空（`0x10001AA8–0x10001AAE`）、长度严格大于 2（`0x10001AAF–0x10001AB5`）；若首 16 位为 0，则在 `0x10001AB7–0x10001AC7` 写入经 `htons` 转换的长度。 | `objdump -d IMProtocol.dll` 对应地址；Ghidra 快照 `rea-ghidra-improtocol-20261009-1235.json` record 26（`0x10003240`）、record 0（`0x10001AA0`）。 |
| A3 | 后续 `0x10001AD8` 调用 `0x10005F80`。该路径在 `0x10005FBA` 检查 session 的 socket-object 指针（Ghidra 名称 `m_pNsSock`）；空指针分支记录错误并在 `0x10005FF5–0x10005FF8` 返回 `-1`。非空时经对象 vtable `+0x18` 分发。 | `objdump -d IMProtocol.dll`; Ghidra 快照 `rea-ghidra-improtocol-20261009-1235.json` record 34（`0x10005F80`）。 |
| A4 | socket 对象构造在 `0x10006130` 写入 vtable 地址 `0x10021CF0`；`0x10021D08`（vtable `+0x18`）的 DWORD 是 `0x100061E0`。该方法在 `0x10006200` 调用 `WS2_32.dll` 导入槽 `0x1001F1A8`（ordinal 19，`send`）。调用参数形态为 socket、buffer、length、flags；上层 `0x10005F80` 传 flags 0。 | `objdump -d/-s IMProtocol.dll`；Ghidra 快照 `rea-ghidra-improtocol-20261009-1235.json` record 3（`0x100061E0`）；`objdump -p IMProtocol.dll` 的 WS2_32 ordinal 导入表。 |
| A5 | 发送返回 `-1` 后，`0x10006211` 取 Winsock 错误；错误值 `0x2733` 走待发队列分支（`0x10006219–0x10006293`），其他错误走记录错误的分支。正数但小于原长度时，`0x100062DD–0x10006354` 保存剩余字节。上述路径没有检查“已收到服务端数据”或应用层连接完成标志。 | `objdump -d IMProtocol.dll` `0x100061E0–0x1000635E`；同上 Ghidra record 3。 |
| A6 | 加密导出 `0x100031F0` 在输入指针非空时跳到 `0x10001970`。该函数在 `0x100019A5–0x100019B1` 检查全局加密状态指针 `0x10028B2C`；指针为 0 时返回 `AL=0`，不进入 `0x10005C20` 加密核心。状态存在时才在 `0x10001A04` 调用该核心。 | `objdump -d IMProtocol.dll` `0x100031F0–0x10003230`、`0x10001970–0x10001A0E`；`IMP_RefreshCryptKey` 导出 `0x10003110` 的长度分支在 `0x10003172–0x10003182`。 |
| A7 | IMProtocol 的 `IMP_SendBuffer2NS → 0x10001AA0 → 0x10005F80 → 0x100061E0` 内部链没有调用 `IMP_EncryptBuffer`/`0x10001970`/`0x10005C20`；但调用者是否在外部先行加密，不能由此得出。 | 上述地址的完整相关反汇编；`mx.exe` 侧 xref 限制见 A8。 |
| A8 | `mx.exe` 的导入表确有 `IMP_SendBuffer2NS`，IAT VA 为 `0x00E1B29C`（`mx.exe.json` 行 1001–1003）；保留 Ghidra 查询 `rea-ghidra-mx-exe-20261009-1241.json` record 1 对 `0xE1B29C` 的 xref 结果为空，record 8 的名称 xref 未解析。原始绝对地址查找也无命中。不能据此断言运行时没有调用。 | `mx.exe.json:1001–1003`；`E-IDA-007.md:21–31`；Ghidra bundle record 1/8；主映像 SHA-256 见上表。 |
| A9 | 连接路径建立 socket 后经虚表 `+0x10` 进入 `0x10004920`；数字地址路径调用 `connect` 导入。`0x10004A60` 通过 WS2_32 ordinal 101 注册 `context+0x503`、mask `0x3F` 的异步事件。此处证明有异步 socket 事件设置，不证明 `IMP_SendBuffer2NS` 必须等首个服务器 payload。 | `0x10005CB0`、`0x10005D3B`、`0x10004920`、`0x100049FE`、`0x10004A60–0x10004A8D`；`E-REA-002.md:23–31`；Ghidra bundle `rea-ghidra-improtocol-20261009-1244.json` records 0/2/5/6。 |
| A10 | 历史回环记录显示连接到本机 listener 后捕获为 0 字节；10-10 文件与日志未附，本次条目是用户报告。静态存在 `send` 能力既不证明本次调用，也不与 0 字节观察冲突。 | `E-LOOPBACK-001.md:18–24`、`E-LOOPBACK-002.md:17–27`、`E-LOOPBACK-003.md:8–19`。 |
| A11 | `00 02` 首帧探针导致既有运行记录停在 `KernelBase.dll!RaiseException+0x62`；这只证明该输入影响解析/错误路径，不证明客户端必须先收包才发送 loginhello。 | `E-IDA-DYN-004.md:11–19`；假设定义见 `loopback-test-plan-20261010.md:15`。 |
| A12 | H1–H3 的原假设措辞及其 v4/未复核限制。 | `work/dream-world-connect-login-map/notes/loopback-test-plan-20261010.md:9–17`。 |

### 6. 未完成与未证实
- **主客户端实际调用点：未证实。** 导入存在，但直接 xref 未解析；需要可复核的完整 IAT/间接调用分析或运行时断点命中，才能指出 `mx.exe` 中的具体调用者及其条件。
- **外部调用顺序：未证实。** 不能证明客户端是否在 `IMP_SendBuffer2NS` 前调用 `IMP_EncryptBuffer`；需要 caller xref、脚本控制流或命中记录。
- **H1 的脚本层先收后发顺序：未证实。** 当前 DLL 发送路径本身没有收到数据的门槛；但主调用者/脚本控制流未闭合。需要验证后的 v4.3 `Connect` 与 `OnServerCmd` 路径或同步运行时调用序列。
- **`NakedSend` 对应的 native/Winsock 路径：未证实。** P2 证明 `IMP_SendBuffer2NS` 对长度 `<=2` 的输入走错误分支；没有证据把任务书所述单字节 `NakedSend` 映射到该 API 或另一 socket 方法。
- **连接完成状态：未证实。** 已见 socket 创建、connect 与异步事件注册，但本结果未闭合连接完成回调与脚本发送调用的控制流。
- **H2 的 timeout 值、超时触发及候选切换：未证实。** 这些是脚本层问题；本次分析的 native 发包链未显示 `PROXY_CONNECT_TIMEOUT`。既有连接时长与超时相容，但不是因果证据。
- **回环 3134 的业务角色、实际 API 命中、加密密钥状态及发包失败原因：未证实。** 10-10 原始 capture/harness/game log 未随条目提供，且 `E-REA-002` 仍未确认 `NsServer` 是否为主登录通道。

### 7. 修改记录
- 未修改 `mx.exe`、`mxmain.dll`、`IMProtocol.dll`、`server.ini`。
- 未修改 `tools/` 下代码或任何既有文档；未删除文件。
- 本任务唯一新增文件为本结果：`work/dream-world-connect-login-map/notes/parallel-20261010/P2-result.md`。
- 未运行游戏；未连接任何网络地址。

---

## 任务问题与结论

### 1. `IMP_SendBuffer2NS` 在什么条件下走到 `ws2_32!send`？

可证实的 DLL 内部路径是：

```text
IMP_SendBuffer2NS (0x10003240)
  └─ JMP 0x10001AA0
      ├─ buffer descriptor != NULL
      ├─ data pointer != NULL
      ├─ length > 2；若首 16 位为 0，则写入 htons(length)
      └─ 0x10005F80：m_pNsSock != NULL
          └─ socket vtable + 0x18 = 0x100061E0
              └─ WS2_32 ordinal 19 / send (IAT 0x1001F1A8)
```

因此，**IMProtocol 的发送函数不会因缺少服务器首包而在 DLL 内部等待**；它的显式前提是有效 buffer 与非空 socket-object 指针。该检查不等于 TCP 已连接：本结果没有在此路径找到连接完成标志测试。实际调用 Winsock 后的返回/排队行为见地址表 A4–A5。

客户端侧的调用者/调用点仍**未证实**：主映像静态导入 `IMP_SendBuffer2NS` 只能证明接口存在，不证明某次运行调用它；xrefs 为空也不能证明“永不调用”（A8）。

### 2. `IMP_EncryptBuffer` 是否在 `IMP_SendBuffer2NS` 之前调用？没有密钥时怎样？

- **DLL 内部：没有。** `IMP_SendBuffer2NS` 的上述内部链不调用 `IMP_EncryptBuffer` 或加密核心（A7）。
- **客户端外部调用顺序：未证实。** `mx.exe` 导入了两个 API，但现有 xref 不闭合；不能断言脚本是否先独立加密再发送（A8）。
- **加密 API 无状态时：返回 `0`（false 状态），不是在这段代码里抛异常。** `IMP_EncryptBuffer` 对空输入也返回 0；有输入但全局加密状态指针 `0x10028B2C` 为空时，`0x10001970` 在 `0x100019A5–0x100019B1` 直接返回 `AL=0`，不调用 `0x10005C20`（A6）。
- **对 send 的影响：未证实 caller 行为。** DLL 的 `IMP_SendBuffer2NS` 路径自身不检查该加密状态，也不自动调用加密核心；这不证明调用者会忽略加密失败，也不证明发送内容是明文（A2、A6、A7、A8）。

### 3. 是否有“连接后先等服务器数据”的分支？

- 在 `IMP_SendBuffer2NS` → socket send 的 native 路径中**没有发现**检查 `recv` 结果、已收包标志或“首包已到”状态的分支（A2–A5）。这反对“IMProtocol 发送函数自身必须先收服务器数据”的窄解释。
- **整个客户端 H1 仍未证实。** 高层 caller/脚本是否等 `OnServerCmd` 后再构包/发送未闭合；现有 `00 02` 动态记录只证明该输入进入解析/异常路径，不证明 loginhello 的发送次序（A8、A11）。

### 4. 对 H1 / H2 / H3 的支持或反对

| 假设 | P2 判断 | 依据及边界 |
|---|---|---|
| **H1：收到服务器数据后才发送 loginhello（服务端先发）** | **整体未证实；对“DLL 内部等待”有反对证据。** | `0x10001AA0–0x10001AD8` 的判断只涉及 buffer/length；`0x10005F80–0x100061E0` 检查 socket-object 后直接走 send，没有首包/recv 状态门槛（A2–A5）。但 `mx.exe` 调用者与脚本控制流未闭合（A8）；H1 原文为计划文件第 15 行。`E-IDA-DYN-004.md:11–19` 的异常只证明畸形 `00 02` 影响解析，不证明首包顺序。 |
| **H2：连接后由 `PROXY_CONNECT_TIMEOUT` 关闭并切换候选** | **P2 未证实；本 native send/connect 链既不支持也不反对脚本层 timeout。** | 本次覆盖的 `IMProtocol.dll` 发包/连接地址未显示该脚本常量或 timeout 分支（A2–A5、A9）；假设见计划文件第 16 行。历史连接时长/关闭记录与 timeout 相容，但关闭原因和实际 timeout 值未证实（`E-LOOPBACK-003.md:14–19`）。 |
| **H3：Connect 前 `NakedSend` 的单字节被丢弃，导致握手未开始** | **整体未证实；仅反对“经 `IMP_SendBuffer2NS` 静默吞掉一字节”这一解释。** | 假设来自计划文件第 9、17 行且标注为 v4 待复核。`IMP_SendBuffer2NS` 对 `length <= 2` 在 `0x10001AAF–0x10001AE0` 走错误分支；所以若确实是原样一字节，就不能据此说它经此 API 到达 Winsock。另一路 `NakedSend` 的绑定未证实。对已确认的 `0x100061E0` 路径，Winsock 返回错误会被检查，`0x2733` 会排队，其他错误走错误记录路径（A4–A5），不是无条件静默丢弃。 |

### 5. 与 10-09 的 0 字节捕获是否一致？

**一致，但不解释因果。** 既有回环记录报告 TCP 能建立、完成捕获为 0 字节（`E-LOOPBACK-001.md:18–24`、`E-LOOPBACK-002.md:19–27`）；10-10 条目是无原始文件的用户报告（`E-LOOPBACK-003.md:8–19`）。静态分析确认 DLL 中存在通向 Winsock send 的路径，但不证明 caller 命中；0 字节不能推出“IMP_SendBuffer2NS 没被调用”，也不能推出“必须先有服务器响应”。可能的前置条件、send 错误、调用者没有发起发送或端口/通道身份等仍未证实（A8、A10、A11）。

**一句话结论：** IMProtocol 内部确有满足 buffer/socket 条件后调用 `WS2_32!send` 的发包路径，但主客户端是否实际调用、是否先等服务器数据及 `NakedSend` 是否走同一路径均未证实，因此现有 0 字节捕获与本次静态结果并不矛盾。
