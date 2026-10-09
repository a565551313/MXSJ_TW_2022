# 任务书 C: 分析地图格式，制作地图查看器

**任务编号**: C
**优先级**: 中
**预计工作量**: 大（3-5天）
**依赖**: 无
**建议会话数**: 1个

---

## 📋 任务背景

梦想世界是一款2D/2.5D MMORPG，地图数据存储在客户端资源文件中。我们需要分析地图格式，提取地图数据（地形、碰撞、传送点、NPC位置等），并制作可视化查看器。

## 🎯 具体目标

1. 定位并识别地图数据文件
2. 分析地图文件格式（文件头、结构、压缩）
3. 解析地图数据（高度图、碰撞、传送点、NPC/怪物刷新点）
4. 提取地图使用的贴图资源
5. 制作地图查看器（命令行或GUI）

## 📝 详细步骤

### 步骤1: 侦察地图文件（1天）

```bash
# 搜索地图相关文件
find data/ -iname "*map*" -o -iname "*.scn" -o -iname "*.wld" 2>/dev/null | head -50
find data/ -iname "*scene*" -o -iname "*terrain*" 2>/dev/null | head -50

# 查看data目录结构
ls -la data/
find data/ -type d | head -30

# 搜索大文件（地图通常较大）
find data/ -size +1M -type f 2>/dev/null | head -20
```

**可能的文件位置**:
- `data/map/` 或 `data/scene/`
- `data/res/map/` 
- 打包在 `data/*.pak` 或 `data/*.fls` 类似的资源包中

### 步骤2: 分析文件格式（1-2天）

对找到的地图文件：

```bash
# 查看文件头
xxd map_file.dat | head -20

# 搜索魔数
strings map_file.dat | head -30

# 分析压缩（可能是zlib/lzma）
python3 -c "
data = open('map_file.dat','rb').read()
print('Size:', len(data))
print('First 64 bytes:', data[:64].hex())
# 尝试zlib解压
try:
    import zlib
    d = zlib.decompress(data)
    print('Zlib OK, decompressed:', len(d))
except: pass
"
```

**常见格式特征**:
- 魔数（如 `MAP\0`, `SCN\0`, 自定义）
- 版本号
- 宽/高（地图格子数）
- 图层数
- 压缩标志

### 步骤3: 解析地图数据（1-2天）

典型地图数据包含：
- **地形高度图**: 每个格子的高度值
- **碰撞数据**: 哪些格子可行走
- **贴图索引**: 每个格子使用的贴图
- **传送点**: 坐标 + 目标地图ID + 目标坐标
- **出生点**: 玩家出生位置
- **NPC/怪物刷新点**: 位置 + NPC/怪物ID + 刷新时间
- **事件触发区域**: 进入触发事件

```python
# 伪代码：解析地图数据
import struct

def parse_map(data):
    # 解析文件头
    magic = data[:4]
    version = struct.unpack('<I', data[4:8])[0]
    width = struct.unpack('<I', data[8:12])[0]
    height = struct.unpack('<I', data[12:16])[0]
    
    # 解析各层数据
    offset = 16
    # ... 根据实际格式解析
    
    return {
        'magic': magic,
        'version': version,
        'width': width,
        'height': height,
        # ...
    }
```

### 步骤4: 提取贴图资源（半天）

```bash
# 搜索贴图文件
find data/ -iname "*.dds" -o -iname "*.tga" -o -iname "*.png" -o -iname "*.jpg" | head -20
find data/ -iname "*tile*" -o -iname "*texture*" | head -20
```

分析贴图格式，可能需要转换（DDS→PNG）。

### 步骤5: 制作地图查看器（1-2天）

**方案A: 命令行 + matplotlib（简单快速）**
```python
import matplotlib.pyplot as plt
import numpy as np

def show_map(map_data):
    plt.imshow(map_data['heightmap'], cmap='terrain')
    plt.colorbar()
    # 标记传送点、NPC等
    for tp in map_data['teleports']:
        plt.plot(tp['x'], tp['y'], 'r^')
    plt.show()
```

**方案B: Pygame（交互式）**
```python
import pygame

# 加载地图，渲染贴图，支持缩放/拖动
# 显示碰撞层、NPC位置等
```

**方案C: 网页版（Three.js/Babylon.js）**
- 导出为JSON格式
- 网页端渲染

## 📦 交付物清单

| 文件 | 说明 |
|-----|------|
| `notes/map-format-analysis.md` | 地图格式完整分析报告 |
| `tools/map_parser.py` | 地图解析器（Python模块） |
| `tools/map_viewer.py` | 地图查看器 |
| `tools/map-data/` | 提取的地图数据（JSON） |
| `tools/map-textures/` | 提取的贴图（PNG） |
| `evidence/E-MAP-001.md` | 证据文件 |

## 📚 参考资料

- 项目结构: `TASK_DISPATCH.md`
- 快速开始: `QUICK_START.md`

## ⚠️ 注意事项

1. 地图文件可能很大，注意内存使用
2. 可能有多种地图格式（室内/室外）
3. 贴图可能是图集（多个小图打包成一个大图）
4. 查看器先做命令行版，稳定后再做GUI
5. 记录所有发现的文件格式

---

**祝顺利！**
