# 任务书 D: 分析技能/装备数据，制作游戏数据浏览器

**任务编号**: D
**优先级**: 中
**预计工作量**: 中（2-3天）
**依赖**: 无
**建议会话数**: 1个

---

## 📋 任务背景

梦想世界的技能、装备、物品、怪物等游戏数据存储在客户端中。这些数据可能是：
- FLS 中的 Python 脚本（数据以 Python 字典/列表形式）
- 独立的数据文件（Excel 导出的 CSV/二进制）
- 数据库文件（SQLite 等）

我们需要分析这些数据，制作一个**游戏数据浏览器**，方便查看和导出。

## 🎯 具体目标

1. 定位游戏数据源（技能、装备、物品、怪物、NPC、任务等）
2. 解析数据格式
3. 提取所有游戏数据
4. 制作数据浏览器（网页版或桌面版）
5. 导出为常用格式（JSON/CSV/SQLite）

## 📝 详细步骤

### 步骤1: 定位数据源（1天）

```bash
# 搜索数据文件
find data/ -iname "*.csv" -o -iname "*.xlsx" -o -iname "*.xml" -o -iname "*.json" 2>/dev/null | head -30
find data/ -iname "*skill*" -o -iname "*item*" -o -iname "*equip*" -o -iname "*quest*" 2>/dev/null | head -30
find data/ -iname "*.db" -o -iname "*.sqlite*" -o -iname "*.mdb" 2>/dev/null | head -20

# 在FLS脚本中搜索数据定义
# (参考任务B的方法，解码包含数据的脚本)

# 搜索大文件（数据文件通常较大）
find data/ -size +500k -type f 2>/dev/null | head -20
```

**可能的数据位置**:
- `data/config/` - 配置数据
- `data/table/` - 数值表
- FLS 中的 `script\data\` 或 `script\table\` 目录
- `data/res/` - 资源包

### 步骤2: 分析数据格式（1天）

**常见格式**:
1. **CSV/Excel**: 人类可读，易于解析
2. **二进制表格**: 固定/变长记录
3. **Python脚本**: 字典/列表定义
4. **SQLite**: 标准数据库
5. **自定义二进制**: 需要逆向

```python
# 示例：解析CSV数据
import csv

def load_csv_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

# 示例：解析二进制表格
def parse_binary_table(data):
    # 分析文件头，确定记录格式
    # 可能是固定长度记录或带长度前缀
    pass
```

### 步骤3: 关联脚本逻辑（半天）

找到引用这些数据的游戏脚本：
- 技能释放逻辑（战斗脚本）
- 装备穿戴逻辑（物品脚本）
- 任务奖励（任务脚本）

### 步骤4: 制作数据浏览器（1-2天）

**方案A: 网页版（推荐）**
```python
# 使用 Flask + 前端表格
# 或 Streamlit（快速原型）

import streamlit as st
import pandas as pd

st.title('梦想世界游戏数据浏览器')
category = st.sidebar.selectbox('分类', ['技能', '装备', '物品', '怪物', 'NPC', '任务'])
df = pd.read_csv(f'data/{category}.csv')
st.dataframe(df)
```

**方案B: 桌面版（PyQt）**
```python
# 树形导航 + 表格显示 + 搜索过滤
```

**功能需求**:
- 分类浏览（技能/装备/物品/怪物/NPC/任务）
- 搜索和过滤
- 详情查看
- 导出（JSON/CSV/Excel）
- 关联数据（如点击技能查看关联怪物）

### 步骤5: 导出数据（半天）

```python
# 导出为多种格式
import json
import sqlite3

# JSON
with open('export/skills.json', 'w') as f:
    json.dump(skills_data, f, ensure_ascii=False, indent=2)

# SQLite数据库
db = sqlite3.connect('export/game_data.db')
# 创建表并插入数据
```

## 📦 交付物清单

| 文件 | 说明 |
|-----|------|
| `notes/game-data-analysis.md` | 游戏数据源分析报告 |
| `tools/data_browser/` | ⭐ 数据浏览器（网页或桌面） |
| `tools/data-export/` | 导出的数据（JSON/CSV/SQLite） |
| `tools/data-parser/` | 数据解析工具 |
| `evidence/E-DATA-001.md` | 证据文件 |

## 📚 参考资料

- FLS解码: `notes/decoder-artifacts/decode_entry516.py`
- 项目结构: `TASK_DISPATCH.md`

## ⚠️ 注意事项

1. 数据可能分散在多个文件中
2. 可能有加密/混淆的数据
3. 注意数据之间的关联（外键）
4. 浏览器先做命令行版，稳定后再做GUI
5. 导出的数据要包含完整的元数据

---

**祝顺利！**
