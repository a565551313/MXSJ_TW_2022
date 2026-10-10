### E-OBS-001
- title: Windows 观察器首次运行：挂载成功，IMP 函数未命中，客户端连接外部 HTTP 地址（范围偏离）
- severity: high
- status: observed (agent-reported; 原始文件尚未进入工作区)
- observed_at: 2026-10-10 20:28:33 至 20:43:30（+08:00）
- source_type: operator_agent_report
- repro_command: 见 notes/observer-20261010/AGENT-brief-windows.md（第 4–5 节）；observe.js 已同步 Frida 17 修复（ws2_32 改用 Process.findModuleByName）。
- observations:
  - 文件校验：mx.exe SHA-256 `637331b5…` 与 IMProtocol.dll SHA-256 `bc356c88…` 与仓库一致。
  - Python 32 位，Frida 17.23.3。挂载成功，8 个 hook 全部安装（ws2_32.connect、ws2_32.send、IMP_ConnectNsServer、IMP_SendBuffer2NS、IMP_RefreshCryptKey、IMP_EncryptBuffer、IMP_DecryptBuffer、IMP_UnConnectNsServer），无 missing。
  - 观察期间 IMP_* 函数 enter 次数全部为 0。
  - ws2_32.send 次数为 0。
  - ws2_32.connect 共 2 次，目标均为 HTTP 80 端口：150.230.97.144:80（20:42:41）与 158.101.159.192:80（20:43:02）。两次都发生在点击“刷新列表”之后。未出现 127.0.0.1:3134。
  - 界面停在“伺服器選擇”（免費區），弹窗“獲取服務器列表中...”，未选择任何服务器条目。
- interpretation: |
    1. 本次运行没有回答回环问题：列表未加载完成，没有选择 127.0.0.1 条目，因此 3134 上没有任何连接。
    2. 客户端在刷新服务器列表时，会主动通过 HTTP 访问外部地址。这与 notes/agent-config-protocol.md 中“远端服务器列表”的概念相符，但具体 URL、协议内容和用途未证实。
    3. ws2_32.send 为 0 不能证明 HTTP 请求没有发送数据：HTTP 栈可能使用未 hook 的 WSASend 或其他路径；本次只 hook 了 send。
    4. IMP 函数全部未命中，与“尚未进入连接/握手阶段”一致，但不能据此推断密钥流程的时序。
- scope_deviation: |
    任务书第 0 节禁止连接外部地址，第 5 节要求只在回环条目上操作。执行 agent 点击了“刷新列表”，导致客户端连接外部地址。这是执行偏离，已在第 6 节停止条件下停止观察器，但发起连接本身发生在停止之前。
    影响：外部地址已被实际访问；请求内容未被记录；需要决定是否在本机防火墙阻止以下地址的出站连接：150.230.97.144、158.101.159.192，以及 203.70.8.0/24（服务器配置中的外部地址）。
- limitations: 未收到 observe-log.jsonl、gamelog、截图和 netstat 的原文，以上为 agent 的摘要；需要原文核对。
- linked_workitems: WI-002, WI-009, WI-010
