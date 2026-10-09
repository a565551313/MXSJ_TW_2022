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
- status: observed_static
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
