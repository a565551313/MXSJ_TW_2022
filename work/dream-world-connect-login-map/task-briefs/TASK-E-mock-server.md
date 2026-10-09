# 任务书 E: 增强模拟服务器，支持完整登录流程

**任务编号**: E
**优先级**: 高
**预计工作量**: 中（2-3天）
**依赖**: 任务A成果（协议已理解）
**建议会话数**: 1个

---

## 📋 任务背景

我们已经破解了梦想世界的网络加密算法（IMProtocol.dll）和登录脚本协议（netserver.py）。现在需要实现一个**完整的模拟服务器**，让客户端能够完整走完登录流程，为后续协议研究和私服开发打下基础。

## 🎯 具体目标

1. 完善加密/解密实现（基于 `im_crypto.py`）
2. 实现完整的登录握手流程
3. 确定所有关键命令字的数值（uint16）
4. 支持客户端从启动到进入选服界面的完整流程
5. 可扩展：支持进入游戏地图

## 📝 详细步骤

### 步骤1: 完善协议实现（1天）

**已有基础**:
- 加密模块: `notes/protocol-artifacts/im_crypto.py`
- 基础服务器: `tools/mock_server.py`（6种响应模式）
- 捕获工具: `tools/enhanced_capture_server.py`

**需要完善**:

```python
# 1. 完整的帧处理
class FrameHandler:
    def pack(self, payload: bytes) -> bytes:
        """打包: 加密( uint16_be(总长度) + payload )"""
        length = len(payload) + 2  # 包括长度字段本身?
        frame = struct.pack('>H', length) + payload
        return self.encrypt(frame)
    
    def unpack(self, data: bytes) -> list:
        """拆包: 返回完整的payload列表"""
        frames = []
        while len(data) >= 2:
            decrypted = self.decrypt(data)
            length = struct.unpack('>H', decrypted[:2])[0]
            payload = decrypted[2:length]
            frames.append(payload)
            data = data[length:]
        return frames

# 2. 密钥交换
class KeyExchange:
    def __init__(self):
        self.ctx = CryptContext()
    
    def handle_key_exchange(self, client_data: bytes) -> bytes:
        """处理客户端的密钥交换请求"""
        # 分析 IMP_RefreshCryptKey 的密钥格式
        # 可能是: 客户端发送种子，服务器派生密钥
        pass
```

### 步骤2: 确定命令字数值（1天）

**关键任务**: 确定以下命令的 uint16 数值：

| 命令名 | 方向 | 来源 |
|-------|------|------|
| `loginhello` | C→S | netserver.py Connect() |
| `TEST_HELLO` | C→S | netserver.py Connect() (647B) |
| `RESELECT_HELLO` | C→S | netserver.py Connect() (689B) |
| `C2GS_SELECT_SERVER` | C→S | C2STransferServer() |
| `S2CServerRoleInfo` | S→C | S2CServerRoleInfo() |

**方法**:
1. **静态分析**: 在 `mxmain.dll` 中搜索命令注册代码
   ```bash
   # 搜索命令名字符串的交叉引用
   strings -el mxmain.dll | grep -i "loginhello\|C2GS_SELECT\|TEST_HELLO"
   ```
2. **已知明文攻击**: 使用 `tools/packet_analyzer.py`
   ```bash
   python3 tools/packet_analyzer.py capture.bin --known-plaintext "loginhello"
   ```
3. **动态分析**: 在 Windows 上用调试器捕获（如果可用）
4. **暴力枚举**: 编写脚本尝试所有 uint16 值，观察客户端反应

### 步骤3: 实现登录流程（1天）

**流程**（基于 netserver.py 反编译）:

```
客户端                          模拟服务器
   |                                |
   |  1. TCP连接                     |
   |  2. 密钥交换                    |
   | <----------------------------> |
   |                                |
   |  3. loginhello / TEST_HELLO   |
   | -----------------------------> |
   |  4. S2CServerRoleInfo         |
   |     (服务器列表)               |
   | <----------------------------- |
   |                                |
   |  5. C2GS_SELECT_SERVER        |
   |     + serverid                 |
   | -----------------------------> |
   |  6. 选服结果                   |
   | <----------------------------- |
   |                                |
   |  7. (可选) 进入游戏             |
```

**服务器列表格式**（推测，需要验证）:
```python
# S2CServerRoleInfo 响应格式（推测）
# 需要从 S2CServerRoleInfo() 函数的字节码分析
server_list = [
    {
        'serverid': 1,
        'name': '梦想世界1服',
        'ip': '203.70.8.198',
        'port': 3134,
        'district': '电信',
        'iType': 0,  # 服务器类型
        # ...
    },
    # ...
]
```

### 步骤4: 测试验证（半天）

```bash
# 启动模拟服务器
python3 tools/mock_server_v2.py --port 3134 --log-level DEBUG

# 在另一个终端，使用捕获工具验证
python3 tools/enhanced_capture_server.py --target 127.0.0.1:3134 --auto-crack

# 或直接修改客户端 hosts，指向本地
# 127.0.0.1  login.mxyx.com  (需要知道实际域名)
```

### 步骤5: 扩展功能（可选）

- 支持多客户端同时登录
- 模拟游戏内场景（聊天、移动、战斗）
- 数据库支持（玩家数据持久化）

## 📦 交付物清单

| 文件 | 说明 |
|-----|------|
| `tools/mock_server_v2.py` | ⭐ 完整模拟服务器 |
| `notes/protocol-commands-values.md` | ⭐ 命令字数值文档 |
| `notes/login-flow-complete.md` | 完整登录流程文档 |
| `notes/server-list-format.md` | 服务器列表格式定义 |
| `tools/test-data/` | 测试数据包（pcap/bin） |
| `evidence/E-MOCK-001.md` | 证据文件 |

## 📚 参考资料

- **加密模块**: `notes/protocol-artifacts/im_crypto.py`
- **登录协议**: `notes/co_code_analysis/netserver_py_decompiled.md`
- **现有工具**: `tools/mock_server.py`, `tools/enhanced_capture_server.py`
- **加密分析**: `notes/crypto-analysis-complete.md`
- **命令列表**: `notes/co_code_analysis/netserver_py_decompiled.md` 第3节

## ⚠️ 注意事项

1. **密钥交换**: 这是最难的部分，需要仔细分析 `IMP_RefreshCryptKey`
2. **命令字数值**: 必须准确，否则客户端无法识别
3. **服务器列表格式**: 需要从 `S2CServerRoleInfo()` 字节码精确分析
4. **测试环境**: 建议先用捕获工具验证，再跑真实客户端
5. **日志详细**: 服务器要有详细日志，方便调试

---

**祝顺利！这是最有成就感的任务之一！**
