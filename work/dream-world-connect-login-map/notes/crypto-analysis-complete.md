# IMProtocol.dll 加密算法完整分析报告

**分析日期**: 2026-10-10
**分析工具**: objdump, Python3, 静态逆向分析
**目标文件**: IMProtocol.dll (SHA-256: bc356c88a6470d761b8976f8c027056b8c0e0f483ca2f59cf5c42542e112c82c)

---

## 1. 概述

IMProtocol.dll 是梦想世界（Duoyi Network Inc.）游戏客户端的网络协议库，负责：
- TCP 连接管理（Winsock2）
- 数据加密/解密
- 协议帧序列化/反序列化
- 事件回调系统

---

## 2. 加密算法详解

### 2.1 算法类型

**自定义流密码（Stream Cipher）**，基于 S盒（Substitution Box）替换。

### 2.2 核心结构

```
CryptContext (12字节):
  +0x00: uint32 state      # 状态计数器（0-7循环）
  +0x04: uint8  key[8]     # 8字节密钥
  +0x0C: (padding)
```

### 2.3 S盒表

| 表名 | 地址 (VA) | 大小 | 用途 |
|------|-----------|------|------|
| KeySbox[0] | 0x10026448 | 256B | 密钥派生第1轮 |
| KeySbox[1] | 0x10026548 | 256B | 密钥派生第2轮 |
| KeySbox[2] | 0x10026648 | 256B | 密钥派生第3轮 |
| KeySbox[3] | 0x10026748 | 256B | 密钥派生第4轮 |
| KeySbox[4] | 0x10026848 | 256B | 密钥派生第5轮 |
| KeySbox[5] | 0x10026948 | 256B | 密钥派生第6轮 |
| KeySbox[6] | 0x10026A48 | 256B | 密钥派生第7轮 |
| KeySbox[7] | 0x10026B48 | 256B | 密钥派生第8轮 |
| ENC_SBOX | 0x10026C48 | 2048B | 数据加密（8状态×256） |
| DEC_SBOX | 0x10027448 | 2048B | 数据解密（8状态×256） |

所有 S盒 都是完整的排列（permutation），即 0-255 的每个值恰好出现一次。

### 2.4 密钥派生算法（0x10005b80）

```python
def derive_key(seed: bytes[8]) -> bytes[8]:
    """
    从8字节种子派生最终密钥
    对应汇编函数: 0x10005b80
    """
    buf = bytearray(12)
    buf[0] = 0
    buf[4:12] = seed  # 复制种子到偏移4
    
    # 第1轮: buf[4] = KeySbox0[buf[4]]
    buf[4] = KeySbox[0][buf[4]]
    
    # 第2-8轮: 链式派生
    for i in range(1, 8):
        xored = buf[4 + i - 1] ^ buf[4 + i]
        buf[4 + i] = KeySbox[i][xored]
    
    return bytes(buf[4:12])
```

**特点**: 链式结构，每个字节的派生依赖于前一个字节的结果。

### 2.5 数据加密算法（0x10005c20）

```python
def encrypt(data: bytes, ctx: CryptContext) -> bytes:
    """
    加密数据
    对应汇编函数: 0x10005c20
    """
    result = bytearray(data)
    for i in range(len(result)):
        state = ctx.state & 7
        key_byte = ctx.key[state]
        xored = key_byte ^ result[i]
        index = (state << 8) | xored
        result[i] = ENC_SBOX[index]
        ctx.state = (ctx.state + 1) & 7
    return bytes(result)
```

### 2.6 数据解密算法（0x10005c60）

```python
def decrypt(data: bytes, ctx: CryptContext) -> bytes:
    """
    解密数据
    对应汇编函数: 0x10005c60
    """
    result = bytearray(data)
    for i in range(len(result)):
        state = ctx.state & 7
        key_byte = ctx.key[state]
        index = (state << 8) | result[i]
        result[i] = DEC_SBOX[index] ^ key_byte
        ctx.state = (ctx.state + 1) & 7
    return bytes(result)
```

### 2.7 算法特点

1. **状态机**: 8个状态循环（0→1→2→...→7→0）
2. **密钥调度**: 每个状态使用密钥的不同字节
3. **S盒替换**: 每个状态有独立的加密/解密S盒
4. **可逆性**: ENC_SBOX 和 DEC_SBOX 互为逆表（已验证）
5. **流密码**: 逐字节处理，无分组概念

---

## 3. 协议帧格式

### 3.1 帧结构

```
+----------------+------------------+
| uint16_be len  |    payload       |
|  (2 bytes)     |  (len-2 bytes)   |
+----------------+------------------+
```

- **长度字段**: 大端序（网络字节序）uint16，表示**整个帧的总长度**（包含长度字段本身）
- **自动填充**: 如果发送时长度字段为0，`IMP_SendBuffer2NS` 会自动填充 `htons(buffer->length)`

### 3.2 发送流程（0x10001aa0）

```python
def send_buffer(buffer):
    # 1. 检查缓冲区有效性
    if not buffer.data or buffer.length <= 2:
        return False
    
    # 2. 如果长度字段为0，自动填充
    if buffer.data[0:2] == b'\x00\x00':
        length = struct.pack('>H', buffer.length)
        buffer.data[0:2] = length
    
    # 3. 获取全局Socket对象并发送
    sock = get_global_socket()
    return sock.send(buffer.data, buffer.length)
```

---

## 4. 连接流程

### 4.1 连接函数链

```
IMP_ConnectNsServer (0x10003000)
  └── WSAStartup(0x202)
  └── 处理服务器地址字符串 (0x10002eb0)
  └── FUN_10001660 (0x10001660)
        └── FUN_10005cb0 (0x10005cb0) - 创建Socket对象
              └── FUN_10004920 (0x10004920) - 实际连接
                    ├── inet_addr / 域名解析（异步，消息0x502）
                    ├── htons(port)
                    └── connect(sock, sockaddr, 16)
```

### 4.2 关键日志字符串

| 字符串 | 含义 |
|--------|------|
| `ConnectNsServer ip:%s, port:%d` | 连接目标 |
| `OnNsServerConnected  code:%d` | 连接成功回调 |
| `OnNsServerUnConnected  code:%d` | 断开连接回调 |
| `C2NSBuffer>>> len:%d` | 客户端→服务器 发送日志 |
| `NS2CRawBuffer AskForDecrypt  len:%d` | 服务器→客户端 接收解密 |
| `OnRecvBufferFromNS<<<` | 接收缓冲区回调 |
| `RefreshCryptKey key:%s` | 密钥刷新（密钥以字符串形式传递！） |
| `NsSocket::Send ` | Socket发送 |
| `WSAGetLastError %d` | 错误码 |

---

## 5. 事件系统

### 5.1 事件ID（从 mx.exe 分析）

| 事件ID | 回调方法 | 含义 |
|--------|----------|------|
| 0x2711 | `OnConnected` | TCP连接成功 |
| 0x2712 | `OnError` | 错误 |
| 0x2713 | 条件回调 | 未知（条件触发） |
| 0x2714 | `OnServerCmd(int)` | 服务器命令 |

### 5.2 事件分发（mx.exe 0x004AC590）

```c
switch (event_id) {
    case 0x2711:  // OnConnected
        call_python_method("OnConnected");
        break;
    case 0x2712:  // OnError
        call_python_method("OnError");
        break;
    case 0x2713:  // 条件回调
        if (condition) call_indirect_callback();
        break;
    case 0x2714:  // OnServerCmd
        cmd = IMP_ReadUInt16(reader);
        call_python_method("OnServerCmd", cmd);
        break;
}
```

---

## 6. 导出函数完整列表

| 序号 | 函数名 | 地址 (VA) | 功能 |
|------|--------|-----------|------|
| 1 | IMP_ConnectNsServer | 0x10003000 | 连接到NS服务器 |
| 2 | IMP_DecryptBuffer | 0x100031a0 | 解密缓冲区 |
| 3 | IMP_EncryptBuffer | 0x100031f0 | 加密缓冲区 |
| 4 | IMP_FreeIMBuffWriter | 0x100035b0 | 释放缓冲区写入器 |
| 5 | IMP_NewIMBuffWriter | 0x10003570 | 创建缓冲区写入器 |
| 6 | IMP_OpenLog | 0x10002fc0 | 打开日志 |
| 7 | IMP_ReadBin | 0x10003400 | 读取二进制数据 |
| 8 | IMP_ReadInt16 | 0x10003330 | 读取int16 |
| 9 | IMP_ReadInt32 | 0x100032c0 | 读取int32 |
| 10 | IMP_ReadInt64 | 0x10003280 | 读取int64 |
| 11 | IMP_ReadInt8 | 0x100033a0 | 读取int8 |
| 12 | IMP_ReadStr | 0x10003400 | 读取字符串 |
| 13 | IMP_ReadUInt16 | 0x10003330 | 读取uint16 |
| 14 | IMP_ReadUInt32 | 0x100032c0 | 读取uint32 |
| 15 | IMP_ReadUInt64 | 0x10003280 | 读取uint64 |
| 16 | IMP_ReadUInt8 | 0x100033a0 | 读取uint8 |
| 17 | IMP_RefreshCryptKey | 0x100030d0 | 刷新加密密钥 |
| 18 | IMP_SendBuffer2NS | 0x100036c0 | 发送缓冲区到NS |
| 19 | IMP_UnConnectNsServer | 0x10003240 | 断开NS服务器 |
| 20 | IMP_WriteBin | 0x10003790 | 写入二进制数据 |
| 21 | IMP_WriteInt16 | 0x10003650 | 写入int16 |
| 22 | IMP_WriteInt32 | 0x10003600 | 写入int32 |
| 23 | IMP_WriteInt64 | 0x10003730 | 写入int64 |
| 24 | IMP_WriteInt8 | 0x100036c0 | 写入int8 |
| 25 | IMP_WriteStr | 0x10003790 | 写入字符串 |
| 26 | IMP_WriteUInt16 | 0x10003650 | 写入uint16 |
| 27 | IMP_WriteUInt32 | 0x10003600 | 写入uint32 |
| 28 | IMP_WriteUInt64 | 0x10003730 | 写入uint64 |
| 29 | IMP_WriteUInt8 | 0x100036c0 | 写入uint8 |

---

## 7. 关键内部函数

| 地址 | 功能 | 说明 |
|------|------|------|
| 0x10005c20 | encrypt_data | 数据加密核心 |
| 0x10005c60 | decrypt_data | 数据解密核心 |
| 0x10005b80 | derive_key | 密钥派生 |
| 0x10001aa0 | send_buffer | 发送缓冲区（含长度前缀处理） |
| 0x10001970 | send_with_length | 带长度前缀的发送 |
| 0x10001660 | connect_internal | 内部连接函数 |
| 0x10004920 | socket_connect | Socket连接（IP/域名处理） |
| 0x10001770 | init_crypto | 初始化加密上下文 |
| 0x10005cb0 | recv_handler | 接收数据处理 |
| 0x10005f80 | log_message | 日志输出 |
| 0x10004c90 | string_op | 字符串操作 |
| 0x10002160 | get_global_1 | 获取全局对象1（0x10028b38） |
| 0x100021d0 | get_global_2 | 获取全局对象2（0x10028b64） |

---

## 8. 全局变量

| 地址 | 用途 |
|------|------|
| 0x10028b24 | 加密上下文初始化标志 |
| 0x10028b28 | 全局对象指针1 |
| 0x10028b2c | 全局对象指针2 |
| 0x10028b30 | 全局对象指针3 |
| 0x10028b38 | 全局单例1 |
| 0x10028b60 | 日志初始化标志 |
| 0x10028b64 | 全局单例2（TraceLogger） |
| 0x10028b8c | 另一个初始化标志 |
| 0x10028b90 | 日志级别 |
| 0x10028b94 | 日志计数器 |

---

## 9. 破解要点总结

### 9.1 已破解
- ✅ 加密算法（完整S盒提取）
- ✅ 密钥派生算法
- ✅ 帧格式（uint16大端序长度前缀）
- ✅ 连接流程
- ✅ 事件ID映射
- ✅ 日志字符串

### 9.2 待破解
- ⏳ 初始密钥来源（`RefreshCryptKey key:%s` 表明密钥以字符串形式传入）
- ⏳ 登录协议具体命令字
- ⏳ 服务器首包响应格式
- ⏳ Python脚本（entry 516）的具体逻辑

### 9.3 下一步建议
1. **动态分析**: 在 `IMP_RefreshCryptKey` 下断点，捕获实际密钥
2. **抓包分析**: 捕获真实的登录数据包，用提取的算法解密
3. **脚本解码**: 完整解码 entry 516 的 Python 代码，理解 `OnServerCmd` 处理逻辑
4. **协议模拟**: 用提取的加密算法实现一个模拟服务器

---

## 10. 工具文件

已生成的工具和数据文件（位于 `notes/protocol-artifacts/`）:

| 文件 | 说明 |
|------|------|
| `enc_sbox.bin` | 加密S盒（2048字节） |
| `dec_sbox.bin` | 解密S盒（2048字节） |
| `key_sbox_0.bin` ~ `key_sbox_7.bin` | 密钥派生S盒（8×256字节） |
| `im_crypto.py` | Python加密/解密模块 |

---

## 11. 公司信息

- **公司**: Duoyi Network Inc.（多益网络）
- **产品**: 梦想世界（Fantasy Westward Journey / MXSJ）
- **文件版本**: 1.0.0.1
- **源文件路径**: `.\IMMain.cpp`, `.\NsProtocol\NsSession.cpp`, `.\NsProtocol\NsSocket.cpp`
