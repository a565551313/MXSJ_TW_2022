### E-CRYPTO-001
- title: IMProtocol.dll 加密算法完整破解
- severity: info
- category: reverse_algo
- status: validated
- observed_at: 2026-10-10T00:00:00+08:00
- source_type: binary
- source_ref: IMProtocol.dll (SHA-256: bc356c88a6470d761b8976f8c027056b8c0e0f483ca2f59cf5c42542e112c82c)
- content_hash: bc356c88a6470d761b8976f8c027056b8c0e0f483ca2f59cf5c42542e112c82c
- artifact_path: notes/crypto-analysis-complete.md, notes/protocol-artifacts/
- repro_command: |
    objdump -d IMProtocol.dll --start-address=0x10005c20 --stop-address=0x10005c20
    python3 notes/protocol-artifacts/im_crypto.py
- raw_excerpt: |
    加密算法核心（0x10005c20）:
      for each byte:
        state = ctx->state & 7
        key_byte = ctx->key[state]
        xored = key_byte ^ input
        output = ENC_SBOX[(state << 8) | xored]
        ctx->state = (state + 1) & 7
    
    关键日志字符串:
      "ConnectNsServer ip:%s, port:%d"
      "OnNsServerConnected  code:%d"
      "C2NSBuffer>>> len:%d"
      "NS2CRawBuffer AskForDecrypt  len:%d"
      "RefreshCryptKey key:%s"
      "OnRecvBufferFromNS<<<"
    
    公司信息: Duoyi Network Inc.
    源文件: .\IMMain.cpp, .\NsProtocol\NsSession.cpp, .\NsProtocol\NsSocket.cpp
- notes: 
    已提取全部S盒：
    - 8个密钥派生S盒（各256字节）@ 0x10026448-0x10026B48
    - 加密S盒（2048字节）@ 0x10026C48
    - 解密S盒（2048字节）@ 0x10027448
    - 验证ENC/DEC互为逆表（全部通过）
    - 密钥8字节，经链式派生扩展
    - 密钥以字符串形式传递（RefreshCryptKey key:%s）
- linked_workitem: WI-006, WI-008
- supersedes: none
