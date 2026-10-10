# 任务 C：地图格式分析（2026-10-10）

## 结论与范围

在**仓库根目录的 `map/`** 而非 `data/` 找到五个原始 `.map`：`2101`, `2111`, `2112`, `2122`, `2303`。五份均可按同一套偏移/长度约束读取，包含 49 个分块，每块有 `GEPJ` 图像样数据、`LLEC` 192 字节阵列和 `GIRB` 尾部。`2303` 额外有 32 条带坐标/矩形大小/载荷长度的前置记录和指向这些记录的分块引用；32 条记录的矩形与 320×240 分块索引全部吻合，故它们是**空间对象记录**（具体是遮挡贴片、场景装饰还是其他对象仍未知）。已成功从 GEPJ 还原**五张 2000×1500 彩色底图 PNG**，并导出原始网格字节与叠层查看器；尚未确定值 0/1 的可行走语义、真实地形高度、传送点/NPC/怪物刷怪点或 `2303` 的空间对象载荷。**不要把网格图当成已证实的碰撞图。**

## 可重复步骤与操作日志（包含失败）

| 步骤 | 具体操作 / 结果 | 状态 |
|---|---|---|
| 1 | 按顺序阅读 `QUICK_START.md`、`TASK_DISPATCH.md`、`TASK-C-map-format.md`，建立 `notes/task-c-地图分析/artifacts/` | 完成 |
| 2 | `ls data/` 和按 map/scene/terrain、图片扩展名搜 `data/`：仅六个 `.fls`，无独立地图/贴图 | 阴性结果；**不能推断 FLS 内不存在地图** |
| 3 | 扩大到仓库根目录：`map/*.map` 五份，总计约 1.1 MB；独立 DDS/TGA/JPEG/PNG 游戏贴图零份 | 找到载体 |
| 4 | `xxd`、`file` 命令不存在；使用标准库 `struct` / `bytes.hex` 完成头部检查；`strings` 对二进制给出大量无意义字符串 | 工具失败并替代 |
| 5 | `artifacts/recon.py` 记录大小、SHA256、头 32 字节、魔数出现次数、头部和首块偏移；`artifacts/recon.json` 是机器可读现场快照 | 可复现 |
| 6 | 在 0/4/8/12/首分块偏移直接调用 `zlib.decompress` 均失败；`script.fls` 的已知 zlib 流格式不能直接套用 `.map` | 排除**这些入口**，不是排除任何内部压缩 |
| 7 | `artifacts/probe_image.py` 将**整段** `GEPJ` 当单个 JPEG：原始载荷有 `FF D8 FF A0 FF C0`，SOF 80×80，SOS 长度 9；只删 `FF A0` 补 `FF D9` 报 Bogus marker length；扩展 SOS 后仍报 Corrupt JPEG / Unsupported marker 且产生伪影。临时试验图自动删除 | **失败原因已确定：12 条独立扫描流被误接在同一张 JPEG 中** |
| 8 | `map_parser.py` 严格验证五份样本，导出 JSON；`map_viewer.py` 对原始值绘制 SVG/ASCII；后来扩充至 11 项测试 | 完成 |
| 9 | `artifacts/analyze_records.py` 检查 `2303` 32 条记录的五字段和 61 次分块引用：`长度=20+字段5`、`索引=7×行+列`，矩形跨度按 320×240 计算，**32/32 与 61/61 均吻合**；增加矩形叠加层 | 新增可靠发现 |
| 10 | `artifacts/native_gepj_trace.py` 静态检查 `mx.exe`：`0x4b8ea2` 加载 26 字节、`0x4b8ee0..0x4b8f26` 把 13 个 LE uint16 累加成分段偏移；数据验证所有 245 个分块的长度之和等于图像载荷 | 验证分段表 |
| 11 | `tools/gepj_decoder.py` 把 JPEG 共用头和后续 12 个独立 80×80 扫描段重组；逐块解码并无缝拼成 320×240 分块、2000×1500 底图；五份共 2940 个 JPEG 图块，`convert` 均无解码警告 | 成功恢复五张 PNG |
| 12 | `artifacts/analyze_llec_pixels.py` 将五张 PNG 的画面亮度与 LLEC 原值按 20×20 格统计，并记录边界内的非二进制值坐标 | `0` 几乎都落在非黑色场景区域，`1` 大多与黑背景相关；边界内其他值只有 `2`，但通行语义待证 |
| 13 | `artifacts/native_walkable_trace.py` 查找 `IsWalkable` 的注册表及比较函数；包装 `0x488a00` 调用 16 位网格阈值判断 `0x4bbb00`，未发现与 LLEC 的直接转换 | 无法凭这段代码证明 `0/1/2` 行走含义 |
| 14 | 实现 `tools/map_gui.py`：Tk 桌面 GUI 按需读取 `.map` 和 PNG，五图切换、缩放/拖拽、原值和记录叠层、坐标定位；`tkinter` 延迟导入以便无头测试 | 完成代码；本沙箱无 `tkinter`、无 DISPLAY，尝试启动只得到明确的缺失提示，无法实机验收 Tk 窗口 |
| 15 | 实现 `tools/map_gui_html.py`：用 Python 标准库将五张底图和原始数据内嵌到 `tools/map-viewer.html`，实现无需服务器的交互式浏览器 GUI | 生成约 8.7 MiB 单文件；本沙箱无浏览器/Xvfb，未人工验收真实浏览器的拖拽操作 |
| 16 | 运行 `artifacts/test_map_gui.py` 的 7 项无头测试（含将已知格式地图复制到仓库外临时目录、更名后读取）、原有 `test_maps.py` 的 11 项测试；对生成 HTML 的脚本运行 Node 语法检查（Node 可用时）；运行 `git diff --check` | 7/7、11/11 均通过，JavaScript 语法与 diff 检查通过；只证明可从任意指定目录读取**同格式**地图，不等于新格式或窗口交互实测 |

重做步骤 5—13（工作目录：仓库根目录，均离线，不修改原始文件；PNG 重建需本机 ImageMagick `convert`）：

```bash
python3 work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/recon.py --output work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/recon.json
PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/test_maps.py
PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/probe_image.py map/2111.map --sector 16
PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/analyze_records.py map/2303.map --output work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/2303-records-validation.json
python3 work/dream-world-connect-login-map/tools/map_parser.py map --output-dir work/dream-world-connect-login-map/tools/map-data
python3 work/dream-world-connect-login-map/tools/map_viewer.py map/2111.map --output work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/2111-llec.svg
python3 work/dream-world-connect-login-map/tools/map_viewer.py work/dream-world-connect-login-map/tools/map-data/2303.json --output work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/2303-llec.svg
python3 work/dream-world-connect-login-map/tools/map_viewer.py map/2303.map --overlay-records --output work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/2303-llec-records.svg
python3 work/dream-world-connect-login-map/tools/map_parser.py map/2303.map --extract-gepj 24 --texture-dir work/dream-world-connect-login-map/tools/map-textures
PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/native_gepj_trace.py --output work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/native-gepj-disasm.txt
# 恢复五张地图底图（每张 49×12 个 80×80 JPEG 图块）
for f in map/*.map; do n=${f#map/}; n=${n%.map}; python3 work/dream-world-connect-login-map/tools/gepj_decoder.py "$f" --output "work/dream-world-connect-login-map/tools/map-textures/$n.png"; done
python3 work/dream-world-connect-login-map/tools/map_viewer.py map/2303.map --base-image work/dream-world-connect-login-map/tools/map-textures/2303.png --overlay-records --output work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/2303-image-records.svg
PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/analyze_llec_pixels.py --output work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/llec-pixel-correlation.json
PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/native_walkable_trace.py --output work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/native-walkable-disasm.txt
python3 work/dream-world-connect-login-map/tools/map_viewer.py map/2111.map --probe 705 984
```

不传 `--output` 的 viewer 会在终端显示 84 行文本图，`.` = 0，`#` = 1，`?` = 其他字节；SVG 同理，格线间隔 16×12。采用**分块按行排列、块内字节按行排列**的显示假设，跨相邻分块的轮廓连续，但坐标轴方向仍需客户端验证。

## 文件级结构（五份样本验证）

| 绝对偏移 | 长度 | 解释 / 证据 |
|---:|---:|---|
| 0 | 4 | ASCII `0.1M` (`30 2e 31 4d`)；**不是**任务书猜测的 `MAP\0`；不能仅凭字符串判断版本 |
| 4 | 4 | `uint32_le` 2000，疑似逻辑宽度 |
| 8 | 4 | `uint32_le` 1500，疑似逻辑高度 |
| 12 | 49×4 | 49 个单调递增、绝对文件偏移；样本中 7×7 布局可视化 |
| 208 | 4 | 值 212；作用未知，不是第 50 个分块偏移 |
| 212 | 4 | 前置记录数量：四份为 0，`2303.map` 为 32 |
| 216 | 数量×4 | 若记录数非零，为前置记录的 32 位绝对偏移表；`2303` 第一条偏移 344，最后一条 15802，第一分块偏移 16097 |
| 偏移表末端 | 可变 | 记录本体，仅 `2303` 出现；每条含 20 字节头 + 可变载荷（详见下节）；所有 32 条均被至少一个块引用 |
| 各分块偏移 | 可变 | 下文的块结构 |

每块布局，以分块自身为基准（`r` 为引用个数，`L` 为 `GEPJ` 的长度字段）：

| 相对偏移 | 字节数 | 观察 |
|---:|---:|---|
| 0 | 4 | `uint32_le r`，`2303` 若干块非零，其他样本全部为零 |
| 4 | 4×r | `uint32_le` 前置记录索引；`2303` 索引覆盖 0..31，共 61 次引用；已验证它们对应 320×240 的空间矩形，**不能直接命名为 NPC/传送点** |
| `4+4r` | 4 | ASCII `GEPJ`（字面上是 JPEG 的逆序，不能等同标准 JPEG） |
| `8+4r` | 4 | `uint32_le L`，从本字段之后共 L 字节直到 `LLEC` 标志 |
| `12+4r` | 26 | 13×`uint16_le` **分段长度表**：首个为共享 JPEG 头长度，随后 12 个是 80×80 扫描段长度；长度之和为 `L-26`，加载器 `mx.exe` 还把它们累加成偏移 |
| `38+4r` | `L-26` | GEPJ 原始图像载荷：共享 JPEG 头 + 12 段各自独立的压缩扫描数据；头起始 `FF D8 FF A0 FF C0 00 11 08 00 50 00 50`，SOF 指定 80×80；详见重建算法 |
| `12+4r+L` | 8 | ASCII `LLEC` + `uint32_le 192` |
| `20+4r+L` | 192 | 原始逐字节阵列，以 16 列×12 行展示；大多数为 0/1，边缘和局部也有 2/255/其他值，**不裁剪、不布尔化** |
| `212+4r+L` | 8 | ASCII `GIRB` + `uint32_le 22` |
| `220+4r+L` | 22+4 | 未解的 `GIRB` 体与额外 4 字节尾部；五份样本中标志体相同 |

恒等式 `分块长度 = 4+4r + 8+L + 8+192 + 8+22+4 = 246+4r+L`（最常见 `r=0, L=1219` 时为 1465 字节）。解析器按偏移表和长度共同校验，故不依赖在压缩数据内直接搜索标志。**未发现可命名为高度图的字段**。

### 新发现：完整的 GEPJ 底图重建（已在全部五份样本验证）

**为什么早期尝试失败：**JPEG 看起来有完整的 SOF/DHT/DQT/SOS 头，但不是单个普通 JPEG：`GEPJ` 的 26 字节是 13×LE uint16 长度。第一段恰好在 SOS 分量选择后终止；后续 **12 段是各自独立的 80×80 JPEG 熵编码数据**，不能整体连缀后只加一个 EOI。例如 `2111.map` 的分块 0 长度表 `[281, 76×12]`，和 `281+12×76=1193` 等于 `GEPJ` 的 `1219-26`。所有 245 个块都满足长度恒等式。客户端 `mx.exe` 的加载代码在 VMA `0x4b8ea2` 读取 26 字节，再于 `0x4b8ee0..0x4b8f26` 将 13 个小端 u16 累加为分段偏移（证据：`artifacts/native-gepj-disasm.txt`）。

重建每个 80×80 图块（`tools/gepj_decoder.py`）：

1. 从共享头移除 `SOI` 后的专有 `FF A0`；在 `SOS` 把长度 `0009` 改成标准 `000C`，并在分量选择符后补 `00 3F 00`。
2. 对每个扫描段单独进行 JPEG 字节填充：数据中每个字面 `FF` 变为 `FF 00`；在尾部加 `FF D9`。把**同一个修复后的 JPEG 头**分别加到 12 段前面。
3. 使用本地 ImageMagick `convert jpeg:- -depth 8 rgb:-` 解码，任何非零退出、警告或不是 80×80×3 字节都拒绝；把 12 块按 4 列×3 行拼为 320×240 的分块；49 分块按 7 列×7 行合成后裁切至头部的 2000×1500。

这套算法对五张地图共 **245×12 = 2940** 个 80×80 图块都无解码警告。输出图像能看到完整、连续的室内场景（如 `2111.png` 木楼室内，`2303.png` 神殿），没有早期测试的马赛克伪影。PNG 散列和再生命令见 `tools/map-textures/README.md`。**这是地图背景图，并不自动识别 NPC、可行走层或独立前景对象。**

### 新发现：`2303` 前置记录的矩形与分块索引

每条记录前 20 字节恰为五个 `uint32_le`。五字段可由全部样本内的长度和交叉引用验证为 **x、y、矩形宽、矩形高、后续载荷长度**：全部 32 条满足 `本记录长度 = 20 + 第五字段`；宽高为正、矩形在 2000×1500 范围内。第 0 条从文件偏移 344 起，头是 `(1159, 1205, 60, 33, 171)`，总长 `20+171=191`。第 1 条 `(1219, 878, 61, 327, 396)`，总长 `416`。尚未解码载荷，也未确认对象是场景图、遮挡层还是别的类型。

对于所有 32 条记录：矩形覆盖的分块列从 `x//320` 到 `(x+w-1)//320`，分块行从 `y//240` 到 `(y+h-1)//240`；预测分块序号 `行×7+列` 与文件中实际 61 次引用 **完全一致（32/32 条，61/61 次）**。例如第 1 条预测 `[24,31,38]`，与实际相同；第 2 条预测 `[19,26,33,40]`，也与实际相同。这确立了 7×7 分块的**行优先顺序和 320×240 像素扇区尺寸**。每块 `LLEC` 若按 16×12 排列，则每字节恰覆盖 20×20 像素；后一对应关系仍需客户端验证。最后一列/行有超出逻辑尺寸的边缘冗余（7×320=2240、7×240=1680）。

复现：`artifacts/analyze_records.py`；逐条预测/实际及检查布尔值见 `artifacts/2303-records-validation.json`。可用 `map_viewer.py map/2303.map --overlay-records --output ...svg` 在原始网格图上显示 32 个**未定性空间对象**的红色矩形框。

### 新分析：LLEC 与地图像素、寻路接口的关系（语义仍未坐实）

`artifacts/analyze_llec_pixels.py` 对五张已恢复 PNG 和原始 LLEC 做**只读统计**：仅取逻辑尺寸 2000×1500 内的格子，以每个 20×20 像素格的 16 个采样点比较 RGB（`max(R,G,B)<16` 算黑）。五张图合计，原始值 `0` 有 3751 格，黑像素占 **0.02%**；原始值 `1` 有 33691 格，黑像素占 **86.68%**；其他值有 58 格，黑像素占 **3.45%**。五张地图各自都符合此方向（详见 `artifacts/llec-pixel-correlation.json`）。**这是画面关联，不是移动判定**：`0` 是可见场景中的开放区域候选，`1` 大多为黑色背景/墙体等候选，不应把它们自动标成“允许/禁止通行”。

进一步检查：逻辑边界**内**所有非 0/1 字节都是 `2`（共 13+22+4+3+16=58 格）；其坐标形成连续的小段，例如 `2111` 的 `(700,980)` 和 `2303` 的 `(720,1080)..(920,1180)`。边界外有其他杂值，因此不能对完整 7×7×192 阵列简单布尔化。`2` 的用途可能是边界或特定区域，**尚无证据确认是楼梯、传送点或入口**。

原生关联（`artifacts/native_walkable_trace.py` → `native-walkable-disasm.txt`）：`mx.exe` 的 `IsWalkable` 注册表绑定到 VMA `0x488a00`，该包装调用 `0x4bbb00`；后者在边界检查后取 **16 位网格**元素并与阈值比较（小于阈值时返回真）。寻路路径处理代码 `0x4baebf..0x4baf27` 还用乘 `0x66666667`、算术移位 3 位的整数除法把像素坐标约化到 **20 像素网格**，与 LLEC 的 16×12/320×240 几何相符。地图加载器 `0x4b8d3c` 则读取 LLEC 的 192 **字节**。二者之间的赋值/转换链尚未找到，故**不能把 `IsWalkable` 的比较直接套在 LLEC 字节上**。查看器新增 `--probe X Y` 查询原始字节，例如 `map_viewer.py map/2111.map --probe 705 984` 得到 2，但不解释通行语义。

### 样本对照

| 文件 | 字节数 | 首块偏移 | 前置记录数 | LLEC 的 0/1/其他总数 |
|---|---:|---:|---:|---:|
| 2101.map | 178738 | 216 | 0 | 2447 / 6934 / 27 |
| 2111.map | 216248 | 216 | 0 | 2442 / 6874 / 92 |
| 2112.map | 210562 | 216 | 0 | 2281 / 6936 / 191 |
| 2122.map | 260059 | 216 | 0 | 3018 / 6377 / 13 |
| 2303.map | 228529 | 16097 | 32 | 2296 / 6955 / 157 |

每份共 49×192=9408 字节；精确 SHA256、逐值频次见 `artifacts/recon.json` 与 `tools/map-data/*.json`。`2303` 前置记录已验证是地图像素坐标的矩形数据，但**对象类别仍未知**；实际刷怪、出生/传送配置可能在其他文件或服务器端。

## GUI 查看器：复现、测试与限制

在仓库根目录执行，离线且不修改 `map/*.map` 或任何游戏原文件：

```bash
# Tk 桌面版：需要本机有 tkinter/Tk 8.6+ 和图形桌面
PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/tools/map_gui.py --initial 2303
# 生成可直接以浏览器打开的单文件 GUI（不需要网络、服务器或 Tk）
PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/tools/map_gui_html.py
# 无头测试；若有 Node，还会检查 HTML 内嵌 JavaScript 语法
PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/test_map_gui.py
PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/test_maps.py
```

打开 `tools/map-viewer.html` 可切换五图、滚轮/按钮缩放、拖拽、显示原始 LLEC 网格和 `2303` 的未定性空间记录、查询/定位像素坐标；桌面 Tk 版有同类操作。它们不是仅允许这五个编号：使用 `--map-dir`、`--texture-dir` 可读外部**同格式** `.map`/同名 PNG 对，HTML 则用 `--output` 重新生成快照。外部目录测试只复制了已知样本；未知版本/布局的地图未验证，不保证解析。详细命令、批量恢复底图的 Bash 示例和按键见 `tools/MAP_GUI_README.md`。两版都**只展示原始格值**，不能称其为已验证的碰撞或寻路规则；矩形也不能当作 NPC/传送点。生成器将已恢复 PNG 内嵌 HTML，因此如原地图或底图更新，须重新运行生成器。本沙箱缺少 `tkinter` 与图形显示，也没有可用的浏览器或 Xvfb；已完成代码/数据测试和 HTML 脚本语法检查，但两种界面的实机鼠标交互均未在这里验收。

## 交付、限制和下一步

- `tools/map_parser.py`：只读、校验边界/魔数/长度/引用及 GEPJ 分段表，支持 `--output-dir` 导出五份 JSON；可用 `--extract-gepj N --texture-dir DIR` 抽出**原样二进制**。
- `tools/gepj_decoder.py`：本机 `convert` + Python 标准库离线解码，严格拒绝解码警告；五张 2000×1500 地图底图 PNG 在 `tools/map-textures/`。
- `tools/map_viewer.py`：`.map`/`.json` → ASCII 或独立 SVG。`--base-image tools/map-textures/2303.png --overlay-records` 生成**离线自包含、PNG 底图 + 空间矩形** SVG；可再加 `--overlay-cells` 叠加未证实语义的原始网格字节；`--probe X Y` 查询指定像素的原始字节值。
- `tools/map-data/`：五个样本的字节网格、偏移、散列、13 个 GEPJ 分段长度及 `2303` 的矩形记录字段。
- 下一步：追踪 `IsWalkable` 使用的 16 位网格怎样由地图字节构建/动态更新；研究 `2303` 的空间对象载荷及其渲染层级；查找 NPC/传送点/刷怪信息的独立来源。PNG 是已恢复的场景**底图**，不是完整动态场景。
