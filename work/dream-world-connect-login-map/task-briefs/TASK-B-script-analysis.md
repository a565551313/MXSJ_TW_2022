# 任务书 B: 分析 script.fls 中的其他脚本

**任务编号**: B
**优先级**: 高
**预计工作量**: 中等（2-3天）
**依赖**: 无（可独立开始）
**建议会话数**: 1-2个

---

## 📋 任务背景

梦想世界客户端的游戏逻辑主要由 Python 2.7 脚本驱动，打包在 `data/script.fls`（24MB，5002个条目）。我们已经成功解码了 entry 516（`script\login\netserver.py` 登录脚本），现在需要分析其他关键脚本，特别是**战斗、任务、物品**相关的脚本。

## 🎯 具体目标

1. 枚举 FLS 中所有脚本的路径和分类
2. 批量解码关键脚本（战斗、任务、物品、聊天）
3. 破解这些脚本的字节码（可能使用不同的替换表）
4. 提取所有网络命令字和包格式
5. 分析核心游戏逻辑（战斗公式、任务流程等）

## 📝 详细步骤

### 步骤1: 枚举 FLS 条目（1天）

**目标**: 列出所有 5002 个条目的脚本路径

```python
# 参考 decode_entry516.py，修改为批量解码
# 关键：从 marshal 数据中提取 co_filename 字段

# 伪代码
for index in range(5002):
    entry = extract_entry(archive, index)
    expanded = entry['expanded']
    decoded = xor_decode(expanded)
    reader = MarshalReader(decoded)
    root = reader.read()
    # root 是 code object，有 filename 字段
    filename = root.get('filename', '')
    print(f"Entry {index}: {filename}")
```

**交付物**: `script-catalog.csv`（entry编号、路径、大小、分类）

### 步骤2: 分类关键脚本（半天）

按目录分类，优先级排序：

| 优先级 | 目录 | 原因 |
|-------|------|------|
| P0 | `script\battle\` | 战斗核心逻辑 |
| P0 | `script\net\` | 网络协议（除login外的其他模块） |
| P1 | `script\quest\` | 任务系统 |
| P1 | `script\item\` | 物品/背包 |
| P1 | `script\ui\` | UI逻辑 |
| P2 | `script\npc\` | NPC交互 |
| P2 | `script\chat\` | 聊天系统 |

### 步骤3: 批量解码关键脚本（1天）

使用已有工具批量解码：

```bash
# 创建批量解码脚本
python3 tools/fls_batch_decoder.py --category battle --output notes/script-battle/
python3 tools/fls_batch_decoder.py --category quest --output notes/script-quest/
```

### 步骤4: 破解字节码（持续）

**关键挑战**: 不同脚本可能使用**不同的替换表**

参考任务A的发现：
- 替换表A（已破解37个映射）: 用于大部分业务函数
- 替换表B（未破解）: 用于类定义函数

**策略**:
1. 先用替换表A尝试解码
2. 如果未知opcode比例 > 30%，可能是不同替换表
3. 使用已知明文攻击破解新映射（参考任务A的方法）
4. 记录所有新映射，更新映射表

**映射表位置**: `notes/co_code_analysis/mapping_table_a_v2.json`

### 步骤5: 提取协议命令（持续）

从解码的脚本中提取：
- `PacketPrepare(net.XXX_COMMAND)` 中的命令名
- `OnServerCmd` 中的命令处理
- 所有 `PacketAddI/UI/L/S/BinaryS` 的参数格式

**输出格式**: 更新 `notes/protocol-commands-catalog.md`

### 步骤6: 分析核心逻辑（1天）

重点分析：
- **战斗**: 技能释放流程、伤害计算、战斗状态机
- **任务**: 任务接取/完成条件、奖励发放
- **物品**: 背包操作、装备穿戴、物品使用

## 📦 交付物清单

| 文件 | 说明 |
|-----|------|
| `notes/script-catalog.csv` | 所有5002个脚本的catalog |
| `notes/script-battle-analysis.md` | 战斗脚本分析报告 |
| `notes/script-quest-analysis.md` | 任务脚本分析报告 |
| `notes/script-item-analysis.md` | 物品脚本分析报告 |
| `notes/protocol-commands-catalog.md` | 新增命令字catalog（持续更新） |
| `tools/fls_batch_decoder.py` | 批量解码工具 |
| `notes/co_code_analysis/mapping_table_v3.json` | 更新的映射表（含新发现） |
| `evidence/E-SCRIPT-002.md` | 证据文件 |

## 📚 参考资料

- FLS解码器: `notes/decoder-artifacts/decode_entry516.py`
- 字节码映射: `notes/co_code_analysis/mapping_table_a_v2.json`
- 任务A报告: `notes/co_code_analysis/任务A详细报告.md`
- 登录脚本反编译: `notes/co_code_analysis/netserver_py_decompiled.md`

## ⚠️ 注意事项

1. **不要修改原始文件**: 只读分析 `data/script.fls`
2. **记录新映射**: 发现新的opcode映射要及时记录
3. **区分替换表**: 注意不同脚本可能使用不同替换表
4. **优先P0脚本**: 先完成战斗和网络脚本
5. **命令字是关键**: 每个 `PacketPrepare` 的命令都是协议的重要发现

---

**祝顺利！有问题参考 `TASK_DISPATCH.md`**
