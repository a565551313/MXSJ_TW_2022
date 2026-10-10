# 梦想世界 逆向工程工具集

本目录包含三个核心工具，用于梦想世界（MXSJ）台湾版2022客户端的协议分析和模拟。

---

## 📦 工具清单

| 工具 | 文件名 | 功能 |
|------|--------|------|
| 🔍 **增强版回环捕获工具** | `enhanced_capture_server.py` | 捕获客户端数据包并自动解密 |
| 🎮 **模拟服务器框架** | `mock_server.py` | 模拟游戏服务器，响应客户端请求 |
| 📊 **数据包分析工具** | `packet_analyzer.py` | 分析数据包结构，解析字段 |

---

## 1. 🔍 增强版回环捕获工具

### 功能
- 捕获客户端发送的原始 TCP 数据
- 自动解析协议帧（uint16大端序长度前缀）
- 使用破解的加密算法自动解密数据包
- 显示明文内容和字段分析
- 支持自动破解常见密钥

### 使用方法

```bash
# 基本捕获（不解密）
python enhanced_capture_server.py

# 使用固定密钥自动解密
python enhanced_capture_server.py --key 0102030405060708

# 从文件加载密钥
python enhanced_capture_server.py --key-file key.bin

# 自动尝试破解密钥（尝试常见密钥）
python enhanced_capture_server.py --auto-crack

# 指定端口和输出目录
python enhanced_capture_server.py --port 3134 --output ./my-captures
```

### 工作流程
1. 修改游戏目录中的 `server.ini`，将服务器 IP 改为 `127.0.0.1`
2. 运行捕获工具
3. 启动游戏客户端并选择服务器
4. 工具自动捕获并解密数据包

---

## 2. 🎮 模拟服务器框架

### 功能
- 接收客户端 TCP 连接（端口 3134）
- 使用破解的加密算法解密客户端数据包
- 解析 `loginhello` 握手命令
- 构造服务器响应（角色信息、登录成功等）
- 加密并发送响应

### 使用方法

```bash
# 基本模式（不响应，仅捕获）
python mock_server.py --response-type none

# 自动模式（自动识别命令并响应）
python mock_server.py --response-type auto --auto-crack

# 使用固定密钥
python mock_server.py --key 0102030405060708 --response-type auto

# 登录成功响应模式
python mock_server.py --response-type login_success

# 服务器角色信息响应
python mock_server.py --response-type server_role_info

# 详细调试模式
python mock_server.py --verbose --response-type auto
```

### 响应类型

| 类型 | 说明 |
|------|------|
| `none` | 不响应（仅捕获分析） |
| `auto` | 自动识别命令并响应 |
| `login_success` | 总是返回登录成功 |
| `server_role_info` | 总是返回角色信息 |
| `login_fail` | 总是返回登录失败 |
| `heartbeat` | 总是返回心跳响应 |

---

## 3. 📊 数据包分析工具

### 功能
- 解析协议帧（uint16大端序长度前缀）
- 自动识别和解密数据包
- 详细分解 `loginhello` 握手包的字段结构
- 分析其他已知命令的字段
- 支持已知明文攻击破解密钥
- 生成详细的分析报告

### 使用方法

```bash
# 分析单个捕获文件
python packet_analyzer.py capture-20261010-120000-1.bin

# 使用密钥解密分析
python packet_analyzer.py capture.bin --key 0102030405060708

# 分析目录下所有文件
python packet_analyzer.py ./captures/

# 生成报告
python packet_analyzer.py ./captures/ --report report.md

# 暴力破解密钥（已知明文攻击）
python packet_analyzer.py capture.bin --crack --known-plaintext "loginhello"

# 详细调试模式
python packet_analyzer.py capture.bin --verbose
```

### 分析输出示例

```
======================================================================
📦 帧分析报告
======================================================================
帧长度: 34 字节
长度前缀: 34
Payload长度: 32
解密状态: ✅ 已解密
命令字: 0x0001 (1)
命令名: LOGIN_HELLO (loginhello)

字段分解:
  [   0] command              = 1  (uint16 = 1 (0x0001) [LOGIN_HELLO])
  [   2] version              = 36110848 (0x02270200) [版本 2.27.2.0]
  [   6] player_id            = 12345 (0x00003039)
  [  10] client_version       = '2.27.2'
  [  18] hello_string         = 'loginhello'
  [  28] timestamp            = 1791560339 (0x6AC90A93)
```

---

## 🔧 依赖项

所有工具依赖以下模块（位于 `../notes/protocol-artifacts/`）:

| 文件 | 说明 |
|------|------|
| `im_crypto.py` | 加密/解密模块 |
| `enc_sbox.bin` | 加密S盒（2048字节） |
| `dec_sbox.bin` | 解密S盒（2048字节） |
| `key_sbox_*.bin` | 密钥派生S盒（8×256字节） |

### Python 版本
- Python 3.7+

---

## 📋 典型工作流程

### 场景 1: 捕获并分析真实数据包

```bash
# 1. 启动增强版捕获工具（自动破解模式）
python enhanced_capture_server.py --auto-crack --output ./real-captures

# 2. 在另一个终端，修改 server.ini 指向 127.0.0.1
# 3. 启动游戏客户端，选择服务器

# 4. 捕获完成后，用分析工具详细分析
python packet_analyzer.py ./real-captures/ --report analysis-report.md
```

### 场景 2: 实现离线登录

```bash
# 1. 先用捕获工具获取密钥和 loginhello 格式
python enhanced_capture_server.py --auto-crack

# 2. 用分析工具分析 loginhello 结构
python packet_analyzer.py ./captures/capture-*.bin

# 3. 启动模拟服务器（使用破解的密钥）
python mock_server.py --key <破解的密钥> --response-type auto --verbose

# 4. 修改 server.ini 指向 127.0.0.1，启动游戏
# 5. 游戏应该能进入登录界面！
```

### 场景 3: 破解未知密钥

```bash
# 使用已知明文攻击
python packet_analyzer.py capture.bin --crack --known-plaintext "loginhello"
```

---

## 🧪 测试数据

`test-data/` 目录包含测试用的数据包：

| 文件 | 说明 |
|------|------|
| `test_loginhello_plain.bin` | 明文 loginhello 帧 |
| `test_loginhello_v1.bin` | 长度前缀明文 + payload加密 |
| `test_loginhello_v2.bin` | 整个帧加密 |
| `analysis-report.md` | 分析报告示例 |

---

## ⚠️ 注意事项

1. **备份原始文件**: 修改 `server.ini` 前请备份
2. **防火墙**: 确保 3134 端口未被占用
3. **管理员权限**: 某些操作可能需要管理员权限
4. **法律合规**: 仅用于学习研究，不得用于商业用途

---

## 📚 相关文档

- [加密算法分析](../notes/crypto-analysis-complete.md)
- [脚本分析](../notes/script-analysis-complete.md)
- [最终总结报告](../report/final-summary-20261010.md)

---

## 🔄 更新日志

- **2026-10-10**: 创建三个核心工具
  - `enhanced_capture_server.py` - 增强版捕获工具
  - `mock_server.py` - 模拟服务器框架
  - `packet_analyzer.py` - 数据包分析工具
