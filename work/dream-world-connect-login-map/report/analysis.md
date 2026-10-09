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
