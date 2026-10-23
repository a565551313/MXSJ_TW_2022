# 《夢想世界》地图编辑器 Studio (`map_editor` v1.0.0)

面向《夢想世界》客户端（`TW v2.27.2`，`mx.exe`）与服务端地图工作流的**全功能地图编辑器、编译器与诊断套件**。

从早期只读查看器（`0.1.0`）升级为完整的 `1.0.0` 生产级工具：完整打通 **`0.1M` `.map` 容器解析、编辑、新建编译、无损序列化写回、`.blk` 双向同步、`GEPJ` 扇区重编码、`LLEC` 通行/阴影编辑、`GIRB` 4×4 动态光照编辑、`PrefixRecord` 2-bit 前景遮罩编辑、`CAStar` 8 方向寻路模拟、NPC/传送阵标注与健康度审计**，并在本轮从 Google Drive `MAP` 分卷下载到仓外的客户端地图集（**101 张 `.map`，11,763 个扇区，20,036 个前景遮罩，约 266 MB**）上完成作者运行的字节级验证。该语料不随仓库分发，独立复核需另行取得语料并重跑测试；其中 JPEG `GEPJ` 的 `MAE` 是有损图像像素误差，不是字节级一致性指标。

---

## 核心特性一览

| 模块能力 | 说明 | 全量实测结果 |
|---|---|---|
| **内容探针发现** | 按 `0.1M` / `0SLF` 文件头签名递归定位任意客户端安装结构，不硬编码目录 | 101 / 101 识别 |
| **完整场景元数据** | 合并 `NEW_RPL_MAP` 热替换表、场景表、小地图表、283 个传送阵、1,293 个 NPC 坐标 | **101 / 101（100%）** 场景名解析 |
| **`GEPJ` 底图编解码** | 原生 `FFA0/SOF0/DHT/DQT/SOS` + 12 个无字节填充 `80×80` 扫描块解码与重编码；支持整图导入切片与单扇区替换 | 与 `mx.exe` `0x00637420` 实机帧缓冲对拍 `MAE = 0.498 / 255` |
| **`LLEC` 通行与阴影编辑** | `16×12`（`20×20 px`）格：`0 可行走`、`1 阻挡`、`2 阴影可行走`、`3 阴影阻挡`；支持画笔、矩形、直线、油漆桶填充 | 2,256,779 个有效格 100% 覆盖 |
| **`.blk` 服务端双向同步** | 支持 `<HH` + 底向上行序 `.blk` / `_second.blk` 导出与导入写回，精确实现 `ServerPos ↔ ClientPos` 变换 | 双向 100% 无损互转 |
| **`GIRB` 动态光照编解码与绘制** | 原生 `mx.exe` `0x0060ea90` `LZO1X-1` 压缩/解压，`80×60`（`4×4 px`）LSB-first 4-bit 亮度采样（`0..15`，标准值 `8`）与实时光照合成预览 | **11,763 / 11,763（100.0%）** 扇区零失败解出 |
| **`PrefixRecord` 前景遮罩** | `LZO1X-1` 2-bit Alpha 前景屋檐/树冠/船桅遮罩解码、RGBA 镂空导出、PNG 导入新增、画布拾取拖拽与删除 | **20,036 / 20,036（100.0%）** 遮罩零失败解出 |
| **扇区空间索引自动重建** | 严格复现多益原版地图编译器 `Win32 ::IntersectRect`（`{ox, oy, ox+319, oy+239}`）开区间判定 | **11,763 / 11,763（0 偏差）** 完全一致 |
| **`CAStar` 寻路与健康审计** | 复现 `mx.exe` `0x004bac30` 8 方向 A* 寻路模拟、连通域孤岛检测、NPC 阻挡合法性与尾部残留字节审计 | 实时交互支持 |
| **保存安全与写后自检** | 默认**严苛只读保护**（禁止覆盖任何已发现源地图）；可选**宽松模式**（二次确认后允许写回）；临时文件写入并完整重解析（含逐扇区 GEPJ 图像解码）校验通过后原子替换目标；新建编译同样采用验证后原子发布 | 98 张标准图 `SHA-256` 100% 一致；3 张历史 `rb+` 图有效体 `SHA-256` 100% 一致 |

---

## 快速启动

### 1. 启动前环境自检（无需手工拼凑依赖）

```bash
python map_editor/bootstrap.py --check-only
```

### 2. 启动 Studio 图形工作台

```bash
# Windows 直接双击 map_editor/启动地图编辑器.bat，或命令行启动：
python map_editor/bootstrap.py --client-root "D:/Games/MXSJ"

# 或使用包入口：
python map_editor/runGUI.py --client-root "D:/Games/MXSJ"
```

### 3. 命令行（Headless CLI，零 Qt 依赖）

```bash
# 扫描客户端或地图目录
python map_editor/run.py --scan map

# 全量 GIRB 动态光照解压校验报告
python map_editor/run.py --scan map --girb-report

# 导出整图底图 PNG / 服务端 .blk / 通行可视化图 / GIRB 光照灰度图 / 结构 JSON
python map_editor/run.py --scan map --export-png 2303:out/2303.png
python map_editor/run.py --scan map --export-blk 2303:out/2303.blk
python map_editor/run.py --scan map --export-walkability 2303:out/2303_walk.png
python map_editor/run.py --scan map --export-lightmap 1034:out/1034_light.png
python map_editor/run.py --scan map --export-json 2303:out/2303.json

# 将修改后的 .blk 同步写回新 .map 文件（自动重解析校验）
python map_editor/run.py --scan map --import-blk 2303:out/2303.blk:out/2303_synced.map

# 从任意整张 PNG/JPG 世界美术底图直接切片编译生成 0.1M .map 文件
python map_editor/run.py --build-map art/world_9001.png:out/9001.map

# 执行地图健康度审计与 8 方向 CAStar 寻路测试
python map_editor/run.py --scan map --audit 2303
python map_editor/run.py --scan map --find-path 2303:200,300:1200,900
```

---

## `0.1M` `.map` 二进制容器规范（本轮外部 101 张语料实证；非仓库内可复现数据）

```text
+-------------------------------------------------------------------+
| File Header (12 bytes):                                           |
|   magic = b"0.1M" | uint32 width | uint32 height                  |
+-------------------------------------------------------------------+
| Sector Offset Table:                                              |
|   uint32 sector_offsets[N]  (N = ceil(width/320) * ceil(height/240))
|   uint32 header_end_marker  (= 12 + 4*N + 4)                      |
+-------------------------------------------------------------------+
| Prefix Foreground Mask Table:                                     |
|   uint32 record_count (M)                                         |
|   uint32 record_offsets[M]                                        |
|   PrefixRecord[0 .. M-1]:                                         |
|     int32 x, int32 y, uint32 w, uint32 h, uint32 len              |
|     byte payload[len] -> LZO1X-1 压缩的 LSB-first 2-bit Alpha 位图 |
+-------------------------------------------------------------------+
| Sector Payloads [0 .. N-1] (按行主序 320×240 px 排列):              |
|   uint32 ref_count + uint32 record_refs[ref_count]                |
|   Block b"GEPJ" + uint32 len: <13H 段长表 + Header + 12×80x80 Scan |
|   Block b"LLEC" + uint32 192: 16×12 字节通行/阴影格                 |
|   Block b"GIRB" + uint32 len: LZO1X-1(2400B = 80×60 4-bit 亮度)    |
|   Terminator: uint32 0 (4 zero bytes)                             |
+-------------------------------------------------------------------+
```

### 服务端与客户端坐标换算公式（`mx.exe` `0x00487700..0x0048838e`）

设地图宽高为 `(W, H)`，逻辑格列行数 `W_cells = (W + 19) // 20`，`H_cells = (H + 19) // 20`：

* **服务端格坐标 `(sx, sy)`（左下角原点，Y 轴向上） → 客户端像素中心 `(px, py)`（左上角原点，Y 轴向下）**：
  $$\text{px} = 20 \cdot sx + 10, \qquad \text{py} = (H_{\text{cells}} - sy) \cdot 20 - 10$$
* **客户端像素 `(px, py)` → 服务端格坐标 `(sx, sy)`**：
  $$sx = \lfloor \text{px} / 20 \rfloor, \qquad sy = H_{\text{cells}} - 1 - \lfloor \text{py} / 20 \rfloor$$

---

## 代码分层与无头可测架构

```text
map_editor/
├── bootstrap.py                     # 零依赖启动器与依赖自检（--check-only）
├── run.py / runGUI.py               # 命令行入口 / 图形工作台入口
├── build.py                         # Windows PyInstaller onedir 打包脚本
├── data/scenes_tw_v2_27_2.json      # 完整场景/NEW_RPL_MAP/NPC/传送阵表（101/101 全覆盖）
├── tools/build_scene_table.py       # 从仓库 CSV + script.fls 自动重建场景元数据
├── src/map_editor/
│   ├── core/                        # 纯 Python 二进制编解码与算法层（零 Qt 依赖）
│   │   ├── lzo1x.py                 # mx.exe 0x0060ea90 兼容 LZO1X-1 压缩与解压
│   │   ├── gepj.py                  # GEPJ 320×240 扇区图像编解码、切片与光照渲染
│   │   ├── girb.py                  # 80×60 4-bit 动态亮度表编解码与光照调制
│   │   ├── mask.py                  # PrefixRecord 2-bit Alpha 遮罩与 IntersectRect 索引
│   │   ├── blk.py                   # .blk 读写、LLEC 互转与 ServerPos↔ClientPos 换算
│   │   ├── pathfinding.py           # CAStar 8 方向 A* 寻路与通行孤岛分析
│   │   └── mapfile.py               # MapDocument 读写、画笔/矩形/直线/填充与写后自检
│   ├── client/                      # 客户端目录探针、配置持久化、FLS 与场景元数据
│   └── ui/
│       ├── viewmodel.py             # 完整编辑器状态机、100 步撤销/重做与严苛/宽松保护（零 Qt）
│       └── widgets.py               # 唯一导入 PySide6 的 Studio 图形工作台
└── tests/                           # 自动化单测、外部全量 101 图回归与 Offscreen GUI 测试
```

## 质量校验与打包

```bash
# 运行全部单元测试（含 Qt 隔离守卫、全量 101 图无损往返与 Offscreen GUI 截图验证）
PYTHONPATH=map_editor/src python -m unittest discover -s map_editor/tests -v

# PEP 8 / Ruff 静态检查与 Windows 兼容性静态扫描
ruff check map_editor
python tools/devkit/check_windows_compat.py map_editor

# 在 Windows 10/11 上构建免 Python 安装独立发布目录 dist/map-editor/
python map_editor/build.py
```
