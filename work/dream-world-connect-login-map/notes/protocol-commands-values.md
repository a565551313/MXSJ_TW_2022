# MXSJ 协议命令字数值文档

**日期**: 2026-10-10
**状态**: C→S 命令已确认 ✅ | S→C 命令待验证 ⏳
**破解方法**: 明文包分析 + 静态分析 + 已知明文攻击

---

## 一、帧格式（已确认）

```
[加密( uint16_be(总长度) + uint16_be(命令字) + payload )]
```

- **总长度**: uint16 大端序，包括长度字段本身（2字节）
- **命令字**: uint16 大端序
- **Payload**: 参数数据（格式因命令而异）

**示例** (loginhello 明文包):
```
00 22  → 总长度 = 34 (0x0022)
00 01  → 命令字 = 0x0001 (LOGIN_HELLO)
02 27 02 00 00 00 30 39 00 06 32 2E 32 37 2E 32 6C 6F 67 69 6E 68 65 6C 6C 6F 6A C9 0A 93  → Payload (30字节)
```

---

## 二、客户端 → 服务器 (C→S) 命令字 ✅ 已确认

| 命令字 | 十进制 | 名称 | 用途 | 确认方式 |
|--------|--------|------|------|---------|
| **0x0001** | 1 | **loginhello** (LOGIN_HELLO) | 登录握手 | 明文包分析 ✅ |
| **0x0002** | 2 | **TEST_HELLO** | 测试连接握手 | 前期分析 ✅ |
| **0x0003** | 3 | **RESELECT_HELLO** | 重选服务器握手 | 前期分析 ✅ |
| **0x0010** | 16 | **C2GS_SELECT_SERVER** (C2S_TRANSFER_SERVER) | 选择服务器（选服） | 前期分析 ✅ |
| **0x00FF** | 255 | **HEARTBEAT** | 心跳包 | 前期分析 ✅ |

### 命令详情

#### 0x0001 — loginhello (LOGIN_HELLO)
- **用途**: 客户端登录握手，连接服务器后的第一个包
- **Payload 结构** (30字节，来自明文包):
  ```
  02 27 02 00 00 00 30 39 00 06 32 2E 32 37 2E 32 6C 6F 67 69 6E 68 65 6C 6C 6F 6A C9 0A 93
  ```
- **包含字段**:
  - `02` — 参数数量? = 2
  - `27 02 00 00 00` — 参数1（类型0x27, 值=2）
  - `30 39` — "09" (可能是区服或渠道号)
  - `00 06` — 字符串长度 = 6
  - `32 2E 32 37 2E 32` — "2.27.2" (游戏版本号)
  - `6C 6F 67 69 6E 68 65 6C 6C 6F` — "loginhello" (命令名字符串)
  - `6A C9 0A 93` — 附加数据/校验和（待分析）
- **证据文件**: `tools/test-data/test_loginhello_plain.bin`

#### 0x0002 — TEST_HELLO
- **用途**: 测试模式握手（CRandomConnectMgr 使用）
- **调用位置**: `CRandomConnectMgr.Connect()` → `loginhello['TEST_HELLO']`

#### 0x0003 — RESELECT_HELLO
- **用途**: 重选服务器握手（CReselectConnectMgr 使用）
- **调用位置**: `CReselectConnectMgr.Connect()` → `loginhello['RESELECT_HELLO']`

#### 0x0010 — C2GS_SELECT_SERVER (C2S_TRANSFER_SERVER)
- **用途**: 选择服务器（选服），在收到服务器列表后发送
- **调用位置**: `C2STransferServer(serverid, netobj)`
- **Payload**: `PacketAddI(serverid)` — uint32 服务器ID
- **解码确认**:
  ```python
  def C2STransferServer(serverid, netobj):
      netobj = net.g_Net
      netobj.PacketPrepare(net.C2GS_SELECT_SERVER)  # = 0x0010
      netobj.PacketAddI(serverid)                    # uint32
      netobj.PacketSend()
  ```

#### 0x00FF — HEARTBEAT
- **用途**: 心跳包，保持连接
- **推测**: 定时发送，服务器响应 0x10FF

---

## 三、服务器 → 客户端 (S→C) 命令字 ⏳ 待验证

| 命令字 | 十进制 | 名称 | 用途 | 状态 |
|--------|--------|------|------|------|
| **0x1001** | 4097 | **S2C_LOGIN_SUCCESS** | 登录成功响应 | ⏳ 推测 |
| **0x1002** | 4098 | **S2C_SERVER_ROLE_INFO** | 服务器角色信息 | ⏳ 推测 |
| **0x1003** | 4099 | **S2C_LOGIN_FAIL** | 登录失败 | ⏳ 推测 |
| **0x1004** | 4100 | **S2C_SERVER_LIST** | 服务器列表 | ⏳ 推测 |
| **0x10FF** | 4351 | **S2C_HEARTBEAT_ACK** | 心跳响应 | ⏳ 推测 |

> **注意**: S→C 命令字为前期推测值，需要抓包验证

---

## 四、命令字编号规律

```
C→S 命令: 0x0001 - 0x00FF  (小数值，客户端主动发送)
S→C 命令: 0x1001 - 0x10FF  (大数值，服务器响应)
```

- C→S 命令使用 0x00xx 范围
- S→C 命令使用 0x10xx 范围
- 心跳命令使用 0xFF / 0x10FF（特殊值）

---

## 五、包构造协议（Python 脚本侧）

```python
# 包构造流程
netobj.PacketPrepare(command)   # 设置命令字 (uint16)
netobj.PacketAddI(value)        # 添加 int32 参数 (小端序?)
netobj.PacketAddUI(value)       # 添加 uint32 参数
netobj.PacketAddL(value)        # 添加 int64 参数
netobj.PacketAddS(string)       # 添加字符串参数 (长度前缀)
netobj.PacketAddBinaryS(data)   # 添加二进制参数 (长度前缀)
netobj.PacketSend()             # 发送（自动添加长度前缀+加密）
```

---

## 六、验证方法

### 6.1 静态分析
```bash
# 在 mxmain.dll 中搜索命令字常量
objdump -d -M intel mxmain.dll | grep -E "0x0001|0x0002|0x0010"

# 搜索命令分发表
objdump -d -M intel mxmain.dll | grep "jmp.*\[.*\*4"  # 跳转表
```

### 6.2 抓包验证
```bash
# 使用增强捕获工具
python3 tools/enhanced_capture_server.py --port 3134 --auto-crack

# 使用包分析工具
python3 tools/packet_analyzer.py capture.bin
```

### 6.3 已知明文攻击
```bash
# 破解密钥（已知命令名）
python3 tools/packet_analyzer.py capture.bin --crack --known-plaintext "loginhello"
```

---

## 七、相关文件

| 文件 | 说明 |
|-----|------|
| `tools/test-data/test_loginhello_plain.bin` | loginhello 明文包（确认 0x0001） |
| `tools/packet_analyzer.py` | 包分析工具（含命令字表） |
| `tools/mock_server.py` | 模拟服务器（含命令字常量） |
| `notes/protocol-artifacts/im_crypto.py` | 加密模块（帧格式） |
| `notes/co_code_analysis/netserver_py_decompiled.md` | 登录脚本反编译 |

---

## 八、下一步

1. ⏳ **抓包验证 S→C 命令字** — 捕获服务器响应，确认 0x1001-0x10FF
2. ⏳ **破解 loginhello payload 完整结构** — 分析 `6A C9 0A 93` 等未知字段
3. ⏳ **破解 S2C_SERVER_ROLE_INFO 响应格式** — 服务器列表数据结构
4. ⏳ **破解参数类型编码** — 0x27 等类型标记的含义
5. ⏳ **更新协议文档** — 整合命令字到完整协议规范

---

**破解者**: 任务A会话（总指挥）
**日期**: 2026-10-10
**置信度**: C→S 命令 ✅ 高 | S→C 命令 ⏳ 中（待验证）
