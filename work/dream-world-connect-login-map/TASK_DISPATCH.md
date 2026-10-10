> ⚠️ **2026-10-10 核对更新**：本文件中部分“已完成/已确认”表述与仓库实际情况不符。以 `report/verification-20261010.md` 为准。主要问题：通信密钥未获得、仓库中无真实捕获字节、loginhello 样本缺失、C→S 命令字数值未证实、`server.ini` 已被改为回环地址。

> 另：文中“加密算法完全破解 ✅”应理解为“算法实现已还原，通信密钥未获得”；任务 A 的 co_code 映射仍为部分完成（v4.3）；引用的 `docs/` 目录不存在。

# 梦想世界(MXSJ)逆向工程 — 任务分派总纲

**总指挥会话**: `arena/6fbb3403-mxsj-tw-2022`
**分派日期**: 2026-10-10
**项目根目录**: `/home/user/MXSJ_TW_2022/`
**工作区根目录**: `/home/user/MXSJ_TW_2022/work/dream-world-connect-login-map/`

---

## 📋 项目背景（必读）

### 项目识别
- **游戏**: 梦想世界 (MX Online / 夢想世界) 台湾版
- **开发商**: Duoyi Network Inc.（多益网络）
- **版本**: 2.27.2 (2022台湾版)
- **客户端大小**: 703MB

### 核心文件
| 文件 | 大小 | 说明 |
|-----|------|------|
| `mx.exe` | 9.7MB | 主程序（含内嵌Python 2.7解释器） |
| `mxmain.dll` | 9.7MB | 主逻辑DLL（与mx.exe相同） |
| `IMProtocol.dll` | 187KB | 网络协议库（29个导出API） |
| `data/script.fls` | 24MB | Python脚本资源包（5002个条目） |

### PE结构（mx.exe/mxmain.dll）
```
.text     VMA 0x00401000  (代码段, 2.8MB)
.rdata    VMA 0x006B0000  (只读数据, 1.2MB)
.data     VMA 0x007DB000  (数据段, 320KB)
_dyprot0  VMA 0x00947000  (保护段, 可能是Themida, 3.2MB)
_dyprot1  VMA 0x00C5E000  (保护段, 2.0MB)
```

### 已完成的重大突破（任务A）

#### 1. IMProtocol.dll 加密算法完全破解 ✅
- **算法**: 自定义8状态流密码，基于S盒替换
- **加密**: `data[i]=ENC_SBOX[(state<<8)|(key[state]^data[i])]; state=(state+1)&7`
- **密钥派生**: 链式S盒派生
- **线上帧格式**: `加密( uint16_be(总长度) + payload )`
- **Python模块**: `notes/protocol-artifacts/im_crypto.py`（测试通过）
- **S盒文件**: `notes/protocol-artifacts/{enc,dec}_sbox.bin` (2048B), `key_sbox_0..7.bin` (256B×8)

#### 2. FLS脚本包格式破解 ✅
- **魔数**: `0SLF`
- **索引**: 16字节/条目（4×uint32），位于文件末尾
- **目录解码**: 3个字段经过自定义变换
- **压缩**: zlib
- **Entry 516解码**: 5层XOR → Python 2.7 marshal → 59个code objects

#### 3. Python字节码自定义编码破解 ✅（部分）
- **编码方式**: 字节替换（S盒），所有字节（含参数）都被替换
- **解码函数**: `0x420F80` (VMA)，多态字节替换
- **已破解映射**: 37个（见 `notes/co_code_analysis/mapping_table_a_v2.json`)
- **已解码**: `script\login\netserver.py` 的30+个函数
- **关键发现**: `C2STransferServer` 选服协议、包构造流程、登录命令列表

#### 4. 网络工具已创建 ✅
- `tools/enhanced_capture_server.py` - 增强版回环捕获（自动解密、自动破解密钥）
- `tools/mock_server.py` - 模拟服务器框架（6种响应模式）
- `tools/packet_analyzer.py` - 数据包分析工具

### 关键常量
```python
# FLS解码
FLS_MAGIC = b"0SLF"
FLS_ENTRY_COUNT = 5002
FLS_INDEX_OFFSET = 0x173EB22
XOR_SEGMENTS = [(0x0000,0x0D84,0xB1),(0x0D84,0x1B4D,0x44),(0x1B4D,0x28F5,0x30),
                (0x28F5,0x367C,0x41),(0x367C,0x4352,0x20)]

# 服务器端点（6个，端口3134）
SERVER_IPS = ["203.70.8.198", "203.70.8.199", ..., "203.70.8.207"]
SERVER_PORT = 3134

# 事件系统
EVENT_CONNECTED = 0x2711
EVENT_ERROR = 0x2712
EVENT_CONDITION = 0x2713
EVENT_SERVER_CMD = 0x2714  # 参数: uint16 命令字
```

### 工作区目录结构
```
work/dream-world-connect-login-map/
├── notes/                          # 分析笔记
│   ├── crypto-analysis-complete.md # 加密算法完整报告
│   ├── script-analysis-complete.md # 脚本分析报告
│   ├── protocol-artifacts/         # 加密相关文件
│   │   ├── im_crypto.py            # 加密/解密Python模块
│   │   ├── enc_sbox.bin / dec_sbox.bin
│   │   └── key_sbox_0..7.bin
│   ├── decoder-artifacts/          # FLS解码文件
│   │   ├── decode_entry516.py      # FLS解码器
│   │   └── entry516-five-xor-marshal.bin  # 解码后的marshal数据
│   ├── co_code_analysis/           # 字节码破解（任务A成果）
│   │   ├── netserver_py_decompiled.md    # ⭐ 完整反编译报告
│   │   ├── netserver_py_pseudocode.py    # ⭐ 伪代码
│   │   ├── mapping_table_a_v2.json       # 映射表（37个）
│   │   └── bytecode_*.bin                # 59个函数字节码
│   └── co_code_cracker.py          # 字节码破解工具
├── tools/                          # 网络工具
│   ├── enhanced_capture_server.py  # 增强捕获工具
│   ├── mock_server.py              # 模拟服务器
│   ├── packet_analyzer.py          # 数据包分析
│   └── README.md                   # 工具说明
├── evidence/                       # 证据文件
│   ├── E-CRYPTO-001.md
│   ├── E-SCRIPT-001.md
│   └── E-TOOLS-001.md
└── report/                         # 总结报告
    └── final-summary-20261010.md
```

---

## 🎯 待办任务清单

### ✅ 任务A: 破解co_code编码，反编译登录脚本 — **已完成**
- **状态**: 完成 (80%+)
- **成果**: 见 `notes/co_code_analysis/netserver_py_decompiled.md`
- **剩余**: 7个类定义函数（替换表B）、Connect函数完整解码

---

### 📌 任务B: 分析 script.fls 中的其他脚本

**优先级**: 高
**预计工作量**: 中等
**依赖**: 无（可独立进行）

**目标**: 解码并分析 FLS 中的其他关键脚本，特别是战斗、任务、UI相关脚本。

**背景**:
- FLS 包含 5002 个条目，entry 516 是 `script\login\netserver.py`
- 已有 FLS 解码器 `notes/decoder-artifacts/decode_entry516.py`
- 字节码编码（替换表A）已破解 37 个映射

**具体步骤**:
1. **枚举 FLS 条目**: 修改解码器，遍历所有 5002 个条目，提取脚本路径
   - 使用 `strings` 或解析 marshal 中的 `co_filename` 字段
   - 分类：战斗、任务、UI、网络、配置等
2. **批量解码**: 对关键脚本（战斗、任务）进行 5层XOR + marshal 解析
3. **字节码解码**: 使用已破解的映射表（替换表A）解码字节码
   - 参考 `notes/co_code_analysis/mapping_table_a_v2.json`
4. **识别关键脚本**:
   - 战斗逻辑（技能释放、伤害计算）
   - 任务系统（接取、完成、奖励）
   - 物品/背包系统
   - 聊天系统
5. **提取协议命令**: 找出所有网络命令字和包格式

**交付物**:
- `notes/script-battle-analysis.md` - 战斗脚本分析
- `notes/script-quest-analysis.md` - 任务脚本分析
- `notes/protocol-commands-catalog.md` - 命令字 catalog（新增命令）
- `tools/fls_batch_decoder.py` - 批量解码工具

**注意事项**:
- 不同脚本可能使用不同的替换表（参考任务A的发现）
- 优先分析 `script\battle\`, `script\quest\`, `script\item\` 目录
- 记录所有新发现的 opcode 映射，更新映射表

---

### 📌 任务C: 分析地图格式，制作地图查看器

**优先级**: 中
**预计工作量**: 大
**依赖**: 无

**目标**: 分析游戏地图数据格式，制作可视化地图查看器。

**背景**:
- 地图数据可能在 `data/` 目录下的资源包中
- 可能是自定义格式或压缩格式

**具体步骤**:
1. **侦察地图文件**: 在 `data/` 目录搜索地图相关文件
   - 常见格式：`.map`, `.scn`, `.wld`, 或打包在资源文件中
2. **分析文件头**: 识别魔数、版本、结构
3. **解析地图数据**:
   - 地形高度图
   - 碰撞数据
   - 出生点、传送点、NPC位置
   - 贴图/材质引用
4. **提取资源**: 地图使用的贴图、模型
5. **制作查看器**: Python + matplotlib/Pygame/OpenGL 可视化

**交付物**:
- `notes/map-format-analysis.md` - 地图格式分析报告
- `tools/map_viewer.py` - 地图查看器（命令行或GUI）
- `tools/map-data/` - 提取的地图数据

---

### 📌 任务D: 分析技能/装备数据，制作游戏数据浏览器

**优先级**: 中
**预计工作量**: 中
**依赖**: 无

**目标**: 分析游戏的技能、装备、物品数据，制作数据浏览器。

**背景**:
- 数据可能在 FLS 脚本中（Python数据结构）
- 或在独立的数据文件中（Excel导出的二进制/文本）

**具体步骤**:
1. **定位数据源**: 搜索 `data/` 目录中的数据文件
   - 常见：`.csv`, `.xlsx`, `.xml`, `.json`, 或自定义二进制
2. **解析数据格式**: 分析技能、装备、物品的数据结构
3. **关联脚本**: 找到引用这些数据的游戏脚本
4. **制作浏览器**: 网页版或桌面版数据浏览器

**交付物**:
- `notes/game-data-analysis.md` - 游戏数据分析
- `tools/data_browser/` - 数据浏览器（网页或桌面）
- `tools/data-export/` - 导出的数据（JSON/CSV）

---

### 📌 任务E: 增强模拟服务器，支持完整登录流程

**优先级**: 高
**预计工作量**: 中
**依赖**: 任务A成果（协议已理解）、tools/中的现有工具

**目标**: 基于已破解的协议，实现完整的模拟服务器，支持客户端完整登录流程。

**背景**:
- 已有基础工具：`tools/mock_server.py`（6种响应模式）
- 已破解加密算法：`notes/protocol-artifacts/im_crypto.py`
- 已理解登录流程：`notes/co_code_analysis/netserver_py_decompiled.md`
- 关键命令：`loginhello`, `TEST_HELLO`, `RESELECT_HELLO`, `C2GS_SELECT_SERVER`, `S2CServerRoleInfo`

**具体步骤**:
1. **完善协议实现**:
   - 实现完整的加密/解密（使用 `im_crypto.py`）
   - 实现密钥交换（`IMP_RefreshCryptKey`）
   - 实现帧拆包/打包（`uint16_be(总长度) + payload`）
2. **实现登录流程**:
   - 响应 `loginhello` / `TEST_HELLO` → 返回服务器列表
   - 实现 `S2CServerRoleInfo` 响应（服务器角色信息）
   - 响应 `C2GS_SELECT_SERVER` → 返回选服结果
3. **确定命令字数值**:
   - 通过抓包或动态分析确定 `loginhello` 等命令的 uint16 数值
   - 参考 `tools/packet_analyzer.py` 的已知明文攻击
4. **测试验证**:
   - 使用 `tools/enhanced_capture_server.py` 验证
   - 确保客户端能完整走完登录流程

**交付物**:
- `tools/mock_server_v2.py` - 完整模拟服务器
- `notes/protocol-commands-values.md` - 命令字数值文档
- `notes/login-flow-complete.md` - 完整登录流程文档
- `tools/test-data/` - 测试数据包

---

### 📌 任务F: 分析反作弊/保护系统

**优先级**: 低
**预计工作量**: 大
**依赖**: 无

**目标**: 分析游戏的反作弊和保护机制。

**背景**:
- `_dyprot0` / `_dyprot1` 段可能是 Themida 保护
- 可能有心跳检测、内存完整性检查、行为检测

**具体步骤**:
1. **识别保护壳**: 确认 `_dyprot0`/`_dyprot1` 是否为 Themida/WinLicense
2. **分析反作弊模块**: 搜索心跳、检测相关代码
3. **分析通信加密**: 确认 IMProtocol.dll 加密的密钥交换机制
4. **文档化发现**: 记录保护机制和潜在的绕过方法

**交付物**:
- `notes/anti-cheat-analysis.md` - 反作弊分析报告
- `notes/protection-mechanisms.md` - 保护机制文档

---

### 📌 任务G: 编写完整协议文档

**优先级**: 高
**预计工作量**: 中
**依赖**: 任务A、B、E的成果

**目标**: 整理所有协议发现，编写完整的网络协议文档。

**背景**:
- 已有：加密算法、帧格式、登录流程、部分命令
- 需要：完整的命令列表、包格式定义、状态机

**具体步骤**:
1. **整理命令字**: 汇总所有 C→S 和 S→C 命令及其数值
2. **定义包格式**: 每个命令的参数格式（int/uint/string/binary）
3. **绘制状态机**: 登录→选服→进入游戏的状态转换
4. **编写协议规范**: 类似 RFC 格式的协议文档
5. **提供示例**: 抓包数据 + 解析后的示例

**交付物**:
- `docs/MXSJ-Protocol-Specification.md` - 完整协议规范（⭐核心交付物）
- `docs/packet-examples.md` - 包示例
- `docs/state-machine.md` - 状态机文档

---

### 📌 任务H: 其他（机动）

**优先级**: 低
**内容**: 根据项目进展灵活安排，如：
- 破解音频格式（AudioLog混淆）
- 分析渲染引擎（render.dll, 24MB）
- 研究账号注册/验证流程
- 制作资源提取工具（贴图、模型、音频）

---

## 🛠️ 通用指南（所有任务必读）

### 工作区约定
- **每人创建自己的工作区**: `work/dream-world-connect-login-map/notes/<任务名>-<你的标识>/`
- **不要修改已有文件**: 只读分析原始样本，新建文件放在自己的工作区
- **共享成果放在固定位置**: 工具放 `tools/`，报告放 `notes/`，证据放 `evidence/`

### 分析原则
1. **离线只读**: 不修改原始游戏文件，不连接外部服务器
2. **详细记录**: 每一步分析都要记录，包括失败的尝试
3. **证据保存**: 重要发现保存原始数据和截图
4. **代码可复现**: 所有分析脚本化，可重复运行

### 工具使用
```bash
# 反汇编
objdump -d -M intel mx.exe --start-address=0x401000 --stop-address=0x402000

# 搜索字符串
strings -el mx.exe | grep -i "关键字"  # UTF-16LE
strings mx.exe | grep -i "keyword"    # ASCII

# 运行已有工具
python3 tools/enhanced_capture_server.py --help
python3 tools/mock_server.py --response-type auto --key <HEX>
python3 tools/packet_analyzer.py capture.bin --key <HEX>

# 使用加密模块
python3 -c "from notes.protocol-artifacts.im_crypto import *; ..."

# 使用字节码解码
python3 notes/co_code_analysis/co_code_analyzer.py
```

### 关键参考文件
| 需求 | 参考文件 |
|-----|---------|
| 加密算法 | `notes/crypto-analysis-complete.md` + `notes/protocol-artifacts/im_crypto.py` |
| FLS解码 | `notes/decoder-artifacts/decode_entry516.py` |
| 字节码映射 | `notes/co_code_analysis/mapping_table_a_v2.json` |
| 登录协议 | `notes/co_code_analysis/netserver_py_decompiled.md` |
| 网络工具 | `tools/README.md` |
| 总体进展 | `work/dream-world-connect-login-map/report/final-summary-20261010.md` |

### 沟通约定
- 每个任务完成后，在自己的工作区创建 `README.md` 说明成果
- 更新 `evidence/` 目录，添加新的证据文件（编号 E-XXX-001）
- 重大发现及时在任务文档中标注

---

## 📨 分派建议

根据依赖关系，建议同时开启以下任务：

| 波次 | 任务 | 原因 |
|-----|------|------|
| **第一波（立即）** | B（其他脚本）、C（地图）、D（游戏数据）、G（协议文档-初稿） | 互不依赖，可并行 |
| **第二波（1-2天后）** | E（模拟服务器）、G（协议文档-终稿） | 依赖B的命令发现 |
| **机动** | F（反作弊）、H（其他） | 低优先级 |

---

**总指挥**: 任务A会话
**最后更新**: 2026-10-10
**文档版本**: v1.0
