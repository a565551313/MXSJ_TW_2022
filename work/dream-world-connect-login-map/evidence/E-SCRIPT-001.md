### E-SCRIPT-001
- title: Entry 516 (script\login\netserver.py) 完整解码和分析
- severity: info
- category: reverse_algo
- status: validated
- observed_at: 2026-10-10T01:00:00+08:00
- source_type: script
- source_ref: data/script.fls entry 516 (0x183E0854)
- content_hash: 956b10875b586d47810315a489c7a43afcaee9f29d0864fbde2354306877b736 (5层XOR后)
- artifact_path: notes/script-analysis-complete.md, notes/decoder-artifacts/
- repro_command: |
    python3 work/dream-world-connect-login-map/notes/decoder-artifacts/decode_entry516.py
    strings work/dream-world-connect-login-map/notes/decoder-artifacts/entry516-five-xor-marshal.bin
- raw_excerpt: |
    脚本路径: script\login\netserver.py
    代码对象数: 59
    
    关键命令字符串:
      - loginhello (登录握手)
      - TEST_HELLO (测试握手)
      - RESELECT_HELLO (重选握手)
      - Transfer!!fieldname=%s servername=%s server_ip=%s port=%d, serverid=%d
    
    核心类:
      - CMXNet (OnServerCmd, OnConnectFail, OnError, PacketPrepare)
      - CConnectMgr (Connect, GetServerInfo, GetTestProxyList, GetTestServerList)
      - CRandomConnectMgr (RandomConnect)
      - CReselectConnectMgr (ReselectServerConnect, DgwReselectServerConnect)
    
    关键字段:
      - m_Pwd (密码), m_PassPort (通行端口), m_ServerID, m_Idx
      - g_LoginServerIP, g_LoginServePort, g_iPlayerId
    
    DGW系统:
      - dgwconnecttest, DGW_RESELECTCONNECT, g_DGWRsLoginInfo
- notes: 脚本是登录阶段网络处理模块，负责服务器选择、连接管理、命令处理。loginhello 是推测的登录握手命令。co_code 仍有自定义编码层未破解。
- linked_workitem: WI-009, WI-011
- supersedes: none
