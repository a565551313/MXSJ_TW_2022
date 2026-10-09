# 梦想世界离线静态分析交接

本报告仅覆盖本地只读分析；未启动客户端、未连接外部服务。

### F-001
- title: 当前样本的服务器选择候选指向 203.70.8.205:3134
- severity: info
- category: reverse_algo
- status: candidate
- evidence_ids: [E-001, E-002]
- location: server.ini:2-10; mx.ini:[Login]
- impact: 可从本地配置恢复显示名到 endpoint 的静态映射，但未验证可达性或实际连接。
- confidence: high
- repro_steps: |
    1. 读取 server.ini。
    2. 读取 mx.ini 的 lastserver。
    3. 进行显示名匹配。
- remediation: n/a for pure RE

### F-002
- title: 日志只证明进入登录/选服页面
- severity: info
- category: other
- status: candidate
- evidence_ids: [E-003, E-004]
- location: log/game/gamelog_2026-10-09 09-18-40.txt:17-32
- impact: 未发现成功认证、角色进入、服务端地图下发或地图打开的本地日志证据。
- confidence: high
- repro_steps: |
    1. 搜索 login/mainpage.dlg 和 login/multi_selserver5.dlg。
    2. 检查后续记录是否出现成功连接或地图状态。
- remediation: n/a for pure RE

### F-003
- title: 客户端含连接、分包、服务端命令和地图加载静态接口线索
- severity: info
- category: reverse_algo
- status: candidate
- evidence_ids: [E-004, E-005]
- location: mxmain.dll string offsets 0x2b3778-0x2b9fdc
- impact: 可用于后续离线交叉引用；当前未恢复 opcode、完整字段布局或服务端响应格式。
- confidence: medium
- repro_steps: |
    1. 对 mxmain.dll 做只读字符串扫描。
    2. 记录 Connect、PacketPrepare、PacketSend、OnConnected、OnConnectFail、%04d.map。
- remediation: n/a for pure RE

### P-001
- title: 服务器选择到本地地图资源的候选调用路径
- path_type: callflow
- start: server.ini / mx.ini
- goal: 客户端根据服务端状态加载本地地图
- steps: |
    1. 匹配 lastserver 到服务器 endpoint； evidence: E-001, E-002
    2. 进入登录和选服页面； evidence: E-003
    3. 候选 Connect -> PacketPrepare/PacketAdd* -> PacketSend； evidence: E-004
    4. 候选 OnConnected 或 OnConnectFail/OnError 分支； evidence: E-004
    5. 候选按 %04d.map 读取本地地图； evidence: E-004, E-005
- residual_risks: 无动态调用、服务端响应、opcode、地图 ID 或角色初始坐标样本。


### F-004
- title: 主客户端映像静态导入 IMProtocol 连接与消息 API
- severity: info
- category: reverse_algo
- status: candidate
- evidence_ids: [E-IDA-007, E-REA-001]
- location: `mx.exe` PE import descriptor for `IMProtocol.dll`; sample SHA-256 `637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d`
- impact: 确认主客户端映像与 `IMProtocol.dll` 的静态依赖关系，并列出连接、序列化、加解密和发送 API；尚不能据此确定这些接口的实际调用者或其是否承载游戏登录流量。
- confidence: high for the import relation; unresolved for runtime use and channel role
- repro_steps: |
    1. 核对 `mx.exe`、`mxmain.dll` 与 `IMProtocol.dll` 的 SHA-256。
    2. 对当前离线 `mx.exe` 检查 PE import descriptors (`objdump -p mx.exe`)。
    3. 将 `IMProtocol.dll` 的导入名与既有 `mx.exe.json` 的导入清单交叉核对。
- residual_unknowns: REA native provider unavailable in this session; function-level callers, endpoint/port argument source, and `NsServer` versus game-login channel attribution remain unknown.


### F-005
- title: Ghidra 确认 `IMProtocol.dll` 内 `ConnectNsServer` 可达 Winsock TCP connect 分支
- severity: info
- category: reverse_algo
- status: validated
- evidence_ids: [E-REA-002]
- location: `IMProtocol.dll` VA `0x10003000` -> `0x10001660` -> `0x10005cb0` -> `0x10004920`; Ghidra 12.1.4 bundle `evidence/rea-ghidra-improtocol-20261009-1244.json`
- impact: 直接地址分支构造 IPv4 sockaddr，将端口交给 `htons` 并调用 `connect`；域名分支采用带 `0x502` 消息的异步解析形态，socket 通知使用 `context+0x503`/`0x3f`。这确认的是 DLL 的静态 TCP 能力，未确认主客户端实际调用点、目标地址/端口运行值、服务角色或任何登录协议。
- confidence: high for DLL static connection plumbing and numeric-branch port conversion; unresolved for caller, runtime use, async message completion, and game-login attribution
- repro_steps: |
    1. 核对 `IMProtocol.dll` SHA-256 `bc356c88a6470d761b8976f8c027056b8c0e0f483ca2f59cf5c42542e112c82c`。
    2. 读取 `E-REA-002` 中引用的 Ghidra 12.1.4 Evidence IDs 与 bundle。
    3. 对照 `notes/ida-protocol-interface.md` 中 WS2_32 导入槽映射；主映像 IAT xref 结果见 `evidence/rea-ghidra-mx-exe-20261009-1241.json`。
- supersedes: F-004 中“当前会话原生 provider 不可用”的当前状态表述；该表述是早前时间点记录，E-REA-001 保留为历史诊断。主客户端调用点及通道角色仍然未决。
- residual_unknowns: `mx.exe` 的目标 IAT 槽未取得直接代码 xref；不排除间接分发或覆盖不足。`0x502`/`0x503` 消息处理函数、实际 endpoint/port、NsServer 与登录主通道的关系、登录 opcode/响应与角色/地图状态均未确认。仅有静态代码证据，不代表运行时行为。

### F-006
- title: 选服或点击“下一步”会弹出“连接服务器”对话框；账号凭据登录 UI 尚未确认到达
- severity: info
- category: other
- status: candidate
- evidence_ids: [E-003, E-LOOPBACK-001, E-USER-001]
- location: `log/game/gamelog_2026-10-09 13-43-49.txt`; `tools/captures/server-20261009-134053.log`; direct user observation at 2026-10-09 16:12 (+08:00)
- impact: 用户确认直接选服或点击“下一步”都会打开“连接服务器”对话框，故连接动作已经触发。对话框不等于账号凭据登录 UI、应用层握手、认证成功或地图进入；历史回环捕获只记录 TCP accept，前三条完成的连接未收到客户端应用层字节，且监听器没有发送协议回应。
- confidence: high for the reported UI transition and historical local capture facts; correlation between this report and the earlier capture runs is not established
- repro_steps: |
    1. 在选服页直接选择服务器，或点击“下一步”；用户报告这两种操作都会打开“连接服务器”对话框。
    2. 对照历史日志：`mainpage.dlg` at 13:43:51、`multi_selserver5.dlg` at 13:43:57、关闭于 13:48:59；回环捕获时间为 13:43:59–13:44:39。
- remediation: n/a for pure RE
- residual_unknowns: 对话框打开后是持续等待、超时、报错还是转到账号登录 UI 尚未观察；该对话框与历史四次回环连接的逐次对应关系未知。捕获器没有协议回应，因此等待服务端应用层数据是可检验的可能原因，但现有证据不能证明它是唯一阻塞点。

### F-007
- title: 主客户端静态区分 TCP 连接回调与服务器命令事件
- severity: info
- category: reverse_algo
- status: validated
- evidence_ids: [E-REA-003]
- location: `mx.exe` `FUN_004ac590` and `FUN_004ab9a0`; Ghidra bundle `evidence/rea-ghidra-mx-exe-20261009-1402.json`
- impact: Event `0x2711` dispatches `OnConnected`, while `0x2714` dispatches to `FUN_004ac030`; a separate status path dispatches `OnConnectFail`. A successful transport callback alone does not establish the account-login screen or an authenticated session.
- confidence: high for the static event-to-callback mappings; runtime invocation and UI transition remain unknown
- repro_steps: |
    1. Open the hash-matched `mx.exe` in Ghidra 12.1.4.
    2. Inspect `FUN_004ac590` and `FUN_004ab9a0` in `E-REA-003`.
- remediation: n/a for pure RE
- residual_unknowns: The `0x2714` helper is not proven to be the `ProcessServerCmd` string; account-page resources and S2 -> S3 trigger are not yet identified.


### F-008
- title: `0x2714` 服务端事件通过 `IMP_ReadUInt16` 读取 16 位值后派发到 `OnServerCmd`
- severity: info
- category: reverse_algo
- status: validated
- evidence_ids: [E-REA-004]
- location: `mx.exe` `FUN_004ac590` / `FUN_004ac030`; indirect slot `0x006b020c`; Ghidra 12.1.4
- impact: `OnConnected`（事件 `0x2711`）与服务端命令回调是分离的。`0x2714` 路径将原事件参数保存在对象状态，并将从它读取的 16 位值作为单个整数参数传给脚本 `OnServerCmd`。这把缺口收敛到具体命令和脚本行为，但不等于已经触发账号登录页面。
- confidence: high for the static dispatch and import-name mapping; unknown for runtime invocation and command semantics
- residual_unknowns: `IMP_ReadUInt16` 所读字段是否就是协议 opcode、该值的具体取值、帧/剩余负载布局、`OnServerCmd` 脚本实现及其 S2 -> S3 UI 条件均未确认。

### F-009
- title: `dgw.dll` 的 special-login 回包路径是 HTTP 辅助处理，不能直接充当 3134/TCP 回包
- severity: info
- category: reverse_algo
- status: validated
- evidence_ids: [E-REA-004]
- location: `dgw.dll` `FUN_1004d160` (`HttpAssist.cpp` 路径)、`GetTargetServers` 导出；样本 SHA-256 `388ecde2104d5d94b3afa417b19f6b4cc264d70395006dd72186d995b324e00b`
- impact: `dgw.dll` 有 HTTP response callback，依据 URL 尾段处理 `login`、`delay`、`feedback`，并有 JSON 配置解析与 `GetTargetServers` 导出；主客户端含对应 API 名称。但静态证据没有给出其被当前选服动作调用的时机，亦没有证明它与账号登录 UI 的直接关系。不要把其 HTTP/JSON 数据误作本地 TCP 游戏协议。
- confidence: high for the DLL's static HTTP and export behavior; unresolved for runtime call timing and UI relationship
- residual_unknowns: `GetTargetServers` 在当前运行中是否被调用、HTTP 获取的数据是否参与本次选服、以及该辅助路径与 `OnServerCmd` 的依赖关系尚未知。


### F-010
- title: 历史状态：14:46 工作副本缺少客户端引用的 `data\\script.fls`（已被后续仓库同步取代）
- severity: info
- category: reverse_algo
- status: validated
- evidence_ids: [E-REA-005]
- location: `mx.exe` / 同哈希 `mxmain.dll`、`data/*.fls`、CEF DataPack v4 归档
- impact: 该条只描述 2026-10-09 14:46 的历史工作副本状态，不代表当前文件状态。后续仓库同步已提供 `data/script.fls`，并由 E-REA-006/E-REA-007 完成全量记录解压验证；当前材料仍不能给出选服页的按钮回调、`OnServerCmd` 命令值或 S2 -> S3 条件。
- confidence: high for files and formats observed in the current worktree; moderate that the missing script package contains the relevant UI implementation
- repro_steps: |
    1. 核对 `mx.exe` 中 `data\\script.fls` 字符串及 Ghidra 证据 `ev_4b75...`。
    2. 检查 `data/` 的 FLS 文件名及头部；复核 `FUN_0048ecf0` 的 `0SLF` 目录读取行为。
    3. 扫描 CEF DataPack v4 与本地文件中的 `multi_selserver5.dlg` / `login/mainpage.dlg` 标识。
- residual_unknowns: 用户原 Windows 安装中是否存在 `data/script.fls`；该包是否包含选服/登录页脚本；选服事件对应的服务器命令及应答仍未知。当前会话无可访问 Windows 设备，因此不能直接读取那份安装目录。


### F-011
- title: 报告型结论：entry 516 据交接已恢复 Python 2.7 marshal 树；非标准 opcode 编码仍未揭示登录页切换条件
- severity: info
- category: reverse_algo
- status: candidate
- evidence_ids: [E-REA-006, E-REA-007, E-REA-008]
- location: `data/script.fls` entry 516 (`id=0x183e0854`); `mx.exe` `PY_CODERESOURCE` at VA `0x6c33f4`
- impact: 在已验证全部 5,002 条 FLS zlib 记录的基础上，本次交接更正称 entry 516 经五层 XOR 变换后可完整解析为含 59 个代码对象的 Python 2.7 marshal 树，其中有 `CMXNet.OnServerCmd`、`ProcessServerCmd` 和 `C2STransferServer`。先前解析失败是反编译器参数顺序错误。代码对象的 `co_code` 仍有第二层非标准 opcode 编码，执行前转换层未定位，因此具体命令控制流、原生回调关系和 S2 -> S3 条件仍未恢复。`PY_CODERESOURCE=8` 仍是 Python `imp` 文件/导入类型常量，不是网络命令。
- confidence: 高（FLS 归档与常量结论见 E-REA-006/E-REA-007）；marshal 树恢复细节来自用户提供的分析交接，本轮未独立复跑，故该部分仅作 handoff-only/report-only 线索；运行时执行行为未观察。
- supersedes:
  - E-REA-007 / F-012 中 entry 516 嵌套 marshal 对象解析失败的旧状态
  - F-010 关于当前工作副本缺少 `data/script.fls` 的历史状态
- residual_unknowns: 第二层 `co_code` opcode 转换层、marshal 树与原生 `OnServerCmd(int)` 的实际绑定、具体命令值/分支、连接对话框到账号登录 UI 的条件、帧布局及预期服务端响应均未确认。不可据方法名或常量猜写 TCP 回包。


### F-012
- title: `PY_CODERESOURCE=8` 是内嵌 Python `imp` 模块的文件类型常量，不是服务器命令
- severity: info
- category: reverse_algo
- status: validated
- evidence_ids: [E-REA-007]
- location: `mx.exe` VA `0x4f0442-0x4f044a`, string table `0x6c3388-0x6c3404`; Ghidra 12.1.4
- impact: 客户端以名称 `PY_CODERESOURCE` 和整数 `8` 初始化 `imp` 模块常量；注册函数创建 Python 整数对象并存入模块字典。因此这个数字不能用作 TCP opcode 或响应码。FLS 索引变换及 5,002 条 zlib 记录的独立验证仍有效；entry 516 的后续 marshal 树恢复结论见 E-REA-008。
- confidence: high for the embedded `imp` module constant registration and full FLS zlib validation
- repro_steps: |
    1. 核对 `mx.exe` 中字符串表 `imp` 及其后的 Python `imp` 文件类型名称。
    2. 检查 `0x4f0442` 的整数参数、`0x4f0444` 的 `PY_CODERESOURCE` 字符串地址，以及 `FUN_004f0e50` / `FUN_004e4750` 的模块字典插入路径。
    3. 用 `FUN_0048f170` 解码 FLS 16 字节目录记录，按记录偏移和压缩长度分别调用 zlib；5,002 条均达到流尾，扩展总量 61,940,973 字节。
    4. 该次尝试的失败与后续更正分别见本条历史记录和 E-REA-008；失败原因为反编译器调用参数顺序错误。
- residual_unknowns: `PY_CODERESOURCE` 的具体资源读取路径、第二层 opcode 转换、`ProcessServerCmd` 与原生 `OnServerCmd(int)` 的绑定、账号登录 UI 切换条件、TCP 帧与服务端响应均未确认。不要据值 8 猜写回包。

### F-013
- title: 报告型候选：`render.dll` 的 `Py_Uncompress` / `ResLib.dll` 路径未证实为 entry 516 的脚本加载器
- severity: info
- category: reverse_algo
- status: candidate
- evidence_ids: [E-REA-008]
- location: `render.dll` `Py_Uncompress` 候选路径；`ResLib.dll` ordinal 13/12；`data/script.fls` entry 516
- impact: 用户交接记录称该候选路径与 entry 516 数据头不匹配；局部 PE 字节扫描虽定位 `ReadFls`、`Uncompress`、`LoadFileExtend` 扩展入口名称，但没有建立其处理 entry 516 的调用链。`render.dll` 的宽范围和单函数 Ghidra 反编译均超时，后续采用的字节扫描不足以确认实际加载器。
- confidence: handoff-only；仅按用户提供的既有分析摘要记录，本轮未重新分析；候选处理路径与脚本加载之间的关系未证实。
- residual_unknowns: entry 516 实际加载/转换路径及非标准 opcode 的预执行转换机制均未知；下一步由新的独立复现工作项继续处理。
