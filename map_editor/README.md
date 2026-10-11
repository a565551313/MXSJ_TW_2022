# 夢想世界 地图编辑器（第一期 · 只读）

只需**指定客户端根目录**，编辑器会递归找出全部地图、解析格式、渲染底图并叠加图层。
安装位置无关：EXE 放哪都行，配置写在用户目录，绝不写在程序目录。

```
第一期范围（已确认）：只读
  客户端目录发现 → 自动列出全部地图 → 底图/LLEC网格/记录框/扇区边界分层渲染
  → 图层开关、坐标定位、PNG/JSON 导出
  ✗ 不写回 .map 文件
```

---

## 1. 快速开始

### 开发环境（任意平台）

```bash
pip install -r requirements.txt
python run.py --gui --client-root "D:/Games/MXSJ"     # 图形界面
python run.py --scan "D:/Games/MXSJ"                  # 终端列出全部地图（不需要 Qt）
python run.py --scan . --export-json 2101:out/2101.json
```

### 打包成 EXE（在 Windows 上执行）

```bat
build.bat
:: 产物：dist\MapEditor\MapEditor.exe
:: 单文件版： set MAP_EDITOR_ONEFILE=1  然后再跑 build.bat
```

`build.bat` 会依次：建虚拟环境 → 装依赖 → **跑测试** → PyInstaller 打包。
测试不通过就不会出包。

> 本仓库的开发沙箱是 Linux，PyInstaller 无法跨平台生成 `.exe`，
> 所以打包这一步由你在 Windows 上执行。

---

## 2. 目录结构

```
map_editor/
├── run.py                     入口（薄壳，转发给 map_editor.cli）
├── build.bat                  Windows 打包脚本
├── map_editor.spec            PyInstaller 配置（含数据文件打包）
├── data/
│   └── scenes_tw_v2_27_2.json 104 个场景的名称/尺寸表（可选，缺失不影响功能）
├── src/map_editor/
│   ├── cli.py                 命令行前端（无 Qt 也能跑，是自动化验证入口）
│   ├── core/                  格式引擎（纯标准库 + Pillow，零 Qt 依赖）
│   │   ├── mapfile.py         .map 容器：扇区数自推导、惰性瓦片读取
│   │   └── gepj.py            GEPJ → RGB，用 Pillow，不调用外部程序
│   ├── client/                「不绑目录」相关
│   │   ├── discovery.py       递归扫描客户端根目录，按内容识别 *.map
│   │   ├── config.py          配置存用户目录（~/.map_editor 或 %APPDATA%）
│   │   ├── scene_table.py     场景名 sidecar 表（可选）
│   │   └── scriptfls.py       0SLF 容器读取（混淆目录 + zlib）
│   └── ui/
│       ├── viewmodel.py       **全部编辑器逻辑，零 Qt 依赖** → 可无头测试
│       └── widgets.py         PySide6 薄绑定层（唯一 import Qt 的文件）
└── tests/                     41 个用例，全部可在无 Qt 环境运行
```

---

## 3. 已验证的事实（本机实测，不是抄文档）

| 项目 | 验证方式 | 结果 |
|---|---|---|
| Pillow 解码 == ImageMagick 参考图 | 5 张样例逐像素比对 | **完全一致** |
| 扇区数自推导（不硬编码 49） | 合成 49/100/800/25/30 扇区的头部 | 全部正确解出 |
| 全部扇区通过标签+长度恒等式 | 5 张样例 × 49 扇区 | 0 失败 |
| GIRB 尾块恒定 | 245 个扇区 | 只有 1 种取值 |
| 区域渲染 == 整图渲染的同区域裁剪 | 3 个不同区域 | 字节级相同 |
| 小视口只解 1 个扇区 | 50×50 区域 | `_sectors` 缓存长度 == 1 |
| 0SLF 目录解混淆 + zlib | 对照 `tools/fls_batch_decoder.py` | entry 1301/400/3970 的 offset/clen/解压长度**逐字段一致** |
| 递归发现地图 | 嵌套目录 + 伪造 `.map` + `.git` 剪枝 | 按内容识别，垃圾文件被拒 |
| 端到端 CLI | 真实扫描本仓库 1241 个文件 | 0.01s，5 张地图 + 中文名 + script.fls/mx.exe 定位 |

跑测试：

```bash
python -m unittest discover -s tests -v      # 41 passed
```

---

## 4. 格式要点（编辑器实际依赖的部分）

**头部**：`0.1M` + `u32 width` + `u32 height` + N 个绝对偏移 + 一个**自指 u32**
（值 == 自己的地址 + 4）+ `u32 record_count` + 记录偏移表。
扇区数 N 不显式存储，靠自指哨兵反推——因此 10000×6000 的 800 扇区地图同样能解。

**扇区**：`u32 refs` | refs×`u32` | `GEPJ` | `u32 len` | 13×`u16` 段长 | 载荷 |
`LLEC`+`u32 192`+192 字节 | `GIRB`+`u32 22`+22 字节 | 4 字节尾。
长度恒等式 `246 + 4·refs + len`。

**GEPJ 不是单张 JPEG**：共享头 + 12 段独立的 80×80 熵编码扫描段，且**未做 FF 填充**。
解码 = 去掉私有 `FF A0` → SOS 长度 `0009`→`000C` 并补 `00 3F 00` → `FF`→`FF 00` 回填 →
补 `FF D9` → 4×3 拼成 320×240。

**坐标**：`mx.exe 0x4baebf` 是有符号 ÷20，即 **1 格 = 20×20 像素**；
`0x4b8d3c` 的 `add eax,0xC0` 对应每扇区 192 格（16×12）。

---

## 5. 明确的已知限制（不要当成已解决）

1. **LLEC 语义未破解**。0/1 的含义只是推断。实测 47,040 格里有 480 格（1.020%）
   既不是 0 也不是 1，共 88 种取值，且呈**连续多字节段**、在列方向严重偏斜
   （第 5/6/8/9/10/11 列分别 62/59/84/88/53/42 次，其余列 2–12 次）。
   运行期网格是 u16 而 LLEC 是 u8，中间转换未知。
   → **网格图层仅供参考，不是已证实的碰撞图；因此第一期不提供行走性编辑。**
2. **`.map` 里没有 NPC / 传送点数据**。2303 里的 32 条空间记录只有
   `(x,y,w,h,payload_len)` + 载荷，**对象类型未知**，UI 里只叫「空间记录框」。
   NPC 数据在 `script.fls` 的 npcposdata（1335 行），第一期未接入。
3. **场景名依赖 sidecar 表**。`script.fls` 的名称藏在 5 段 XOR + Python2.7 marshal 之后，
   本编辑器不重造那套启发式求解。表缺失时显示「场景 2101」，几何数据不受影响。
   再生成：`python tools/build_scene_table.py --repo ../..`
4. **超大图导出会慢**。10000×6000 = 6000 万像素 / 约 180 MB RGB。
   界面渲染是瓦片惰性的所以流畅，但「导出整图 PNG」会耗时很久（会先弹确认框）。

---

## 6. 第二期候选（未开始）

- 写入 `.map`：需要先解决 GIRB 语义与 LLEC 编码，且必须先做**整文件字节级往返验证**
  （读入→写出→逐字节相同）才允许落盘。
- 接入 npcposdata / 传送点图层。
- 破解 LLEC 的 88 种取值与 u8→u16 变换。
- 缩略图缓存（首次扫描后落盘，避免每次重解 GEPJ）。
