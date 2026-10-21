# Mock Server V2 - 原生加密通道版本

## 概述

`mock_server_v2.py` 是基于 `mock_server.py` 的改进版本，使用**原生 TCP 加密通道**替代了原来的明文通信方式。

## 主要改进

### 1. 不再修改客户端文件

**原版 (mock_server.py)**：
- 需要 patch `data/script.fls` 中的 `SetSeed` 字节码
- 将 `net.g_Net.SetSeed(seed)` 替换为 NOP 空操作
- 客户端被迫使用明文通信
- 必须备份/还原 `script.fls`

**V2 版 (mock_server_v2.py)**：
- 完全不修改 `data/script.fls`
- 客户端使用原生 `SetSeed` 加密
- 服务器端使用 native channel 解密
- 保持客户端文件完整性

### 2. 加密通信实现

V2 使用 `tools/native_channel` 模块实现完整的加密通道：

```python
# 握手阶段（明文）
1. 服务器发送 9 字节 HELLO: [8][1][seed:4][server:2][cert:1]
2. 客户端返回 25 字节裸回复: [seed_3B][22 字节零]
3. 双方基于 seed 派生加密密钥

# 通信阶段（加密 + LZW 压缩）
1. 所有 S2C 包: opcode+payload → LZW压缩 → 封帧 → 流密码加密
2. 所有 C2S 包: 流密码解密 → 拆帧 → 解析 opcode+payload
```

### 3. 代码改动

**新增**：
- 引入 `native_channel` 模块（~10 行）
- `_unframe()` 函数：反向解析 `frame_gs2c` 的输出
- `self.channel` 属性：存储加密通道实例
- `send_raw()` 改造：有 channel 时走加密通道

**修改**：
- `ClientSession.__init__()`: 添加 `self.channel = None`
- `ClientSession.run()`: 
  - 握手后创建 `_NativeChannel(seed, "server")`
  - 主循环改用 `channel.feed()` 接收解密包
- `ensure_client_ready()`: 移除 SetSeed 补丁逻辑

**删除**：
- 不再需要 SetSeed 补丁检测代码
- 不再需要 "检测到客户端发送加密包" 的错误提示
- 不再需要 `--patch-client` 和 `--restore-client` 命令的实际执行

## 使用方法

### 启动服务器

```bash
# 直接启动（不需要 patch 客户端）
python mock_server_v2.py

# 指定端口和地图
python mock_server_v2.py --port 3134 --map 1025
```

### 客户端连接

1. 确保 `mock_server_v2.py` 在游戏根目录（与 `mx.exe` 同级）
2. 启动 `mock_server_v2.py`
3. 启动 `mx.exe`
4. 选择"缩小燈(推薦站)"（127.0.0.1:3134）
5. 客户端自动完成握手，进入登录界面

### 与原版对比

| 特性 | mock_server.py | mock_server_v2.py |
|------|----------------|-------------------|
| 修改 script.fls | ✓ 需要 | ✗ 不需要 |
| 客户端加密 | ✗ 被禁用 | ✓ 原生启用 |
| 通信方式 | 明文 | 加密 + LZW |
| 备份还原 | 需要 | 不需要 |
| 原生兼容性 | 低（修改了客户端） | 高（完全原生） |
| 测试真实加密 bug | 不可能 | 可以 |

## 技术细节

### 加密算法

- **密钥派生**: 基于 seed 通过 `derive()` 函数生成 rx/tx 密钥和偏移
- **流密码**: `StreamCipher` 使用 4KB 块生成器，支持任意位置解密
- **LZW 压缩**: 固定 11-bit 编码，字典跨帧持久化
- **帧格式**: 
  - 短包 (<255B): `[len][opcode][payload]`
  - 长包 (≥255B): `[0xFF][len:3B_LE][opcode][payload]`

### 兼容性（候选实现，尚未在真实客户端验收）

- ⚠️ 候选兼容：密钥派生和流密码已通过离线向量和同族 DLL 对照验证
- ⚠️ 候选兼容：LZW 解码器已通过原生函数对照（发送端使用 literal-only 编码）
- ⚠️ 候选兼容：帧格式已通过离线测试验证
- ❌ **尚未在真实 Windows 客户端上测试**（登录/进图/游戏流程未验收）
- ❌ **受保护的 init/process 包装函数未验证**（仅验证了同族 render.dll 的未保护实现）
- ✅ 正确处理有符号 seed（高 bit 为 1 的情况）

## 测试

运行集成测试：

```bash
python test_v2_channel.py
```

测试内容：
1. `_unframe()` 函数正确性（短包和长包）
2. 加密通道握手流程
3. 双向加密通信

运行 native channel 单元测试：

```bash
python -m unittest discover -s tools/native_channel/tests -v
```

## 已知限制

1. **上行 payload 限制**: C2S 方向保守限制 247 字节（原生行为）
2. **LZW 压缩效率**: 当前使用 literal-only 编码（无字典压缩收益），但完全兼容
3. **SetSeed2 不支持**: 仅支持标准 `SetSeed`，不支持 `SetSeed2` 扩展
4. **代理连接不支持**: 不支持代理/中转连接模式

## 故障排查

### 客户端卡在"正在登录中..."

**原因**: 可能是握手失败或加密通道未正确建立

**解决**:
1. 检查控制台日志，确认看到 "Encrypted native channel established"
2. 确认 `tools/native_channel/` 目录存在且完整
3. 检查 Python 版本 ≥ 3.10
4. 查看是否有 "Channel feed failed" 错误

### 客户端断开连接

**原因**: 可能是 LZW 解压失败或帧格式错误

**解决**:
1. 检查日志中的错误信息
2. 确认客户端版本是 v2.27.2
3. 验证 `data/script.fls` 未被修改（应该是原始版本）

## 后续计划

1. **优化 LZW 压缩**: 实现真正的字典压缩，减少网络流量
2. **添加更多测试**: 覆盖所有 opcode 和边界情况
3. **性能优化**: 减少加密/解密的 CPU 开销
4. **支持 SetSeed2**: 如果客户端使用了扩展加密

## 相关文件

- `mock_server.py` - 原版明文服务器
- `mock_server_v2.py` - V2 加密版本（本文件）
- `tools/native_channel/` - 原生加密通道实现
- `test_v2_channel.py` - 集成测试
- `data/script.fls` - 客户端脚本包（不再需要修改）

## 作者与日期

- 基于 `mock_server.py` (coderabbitai[bot])
- V2 改造: 2026-10-21
- 使用 native channel (coderabbitai[bot], 2026-10-20)
