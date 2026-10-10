# 梦想世界地图 GUI 使用说明

现有五份 `.map` 的 2000×1500 彩色底图已恢复。有两种**完全离线**的图形界面，均由 Python 工具生成/驱动，仅读取原始地图文件。

## 能否查看仓库外的地图？

**可以尝试同格式的更多地图，不限于这五个编号**；但这里验证过的只有现有五份。解析器识别的是已观察到的 `0.1M` 格式：固定 49 个分块（7×7）、每块 `GEPJ` 图像段和 192 字节 `LLEC`，并对偏移/长度等严格校验。不同游戏版本、其他地图格式或与此布局不一致的文件会报错，不能保证通用；是否有其他尺寸/对象类别也尚未用新样本验证。查看器不支持直接打开任意图片当作带网格的地图。

每张地图**必须先有同名、已恢复的 PNG 底图**（例如 `1234.map` 配 `1234.png`）。可把地图放在**仓库外**，无需复制到 Git；以下命令在仓库根目录执行，`/path/to/...` 换为你的实际目录（需本机安装 ImageMagick `convert` 用于解码）：

```bash
# 先用单张新地图试验格式和解码；不会修改输入 .map
python3 work/dream-world-connect-login-map/tools/gepj_decoder.py "/path/to/maps/1234.map" --output "/path/to/textures/1234.png"
# 有桌面和 tkinter 时：启动后自动列出外部目录里所有“同名 .map + PNG”
python3 work/dream-world-connect-login-map/tools/map_gui.py --map-dir "/path/to/maps" --texture-dir "/path/to/textures"
# 没有 tkinter 时：生成包含该目录中所有同名地图/PNG 对的离线网页
python3 work/dream-world-connect-login-map/tools/map_gui_html.py --map-dir "/path/to/maps" --texture-dir "/path/to/textures" --output "/path/to/my-maps.html"
```

地图很多时，可在 **Bash** 中按需批量生成**尚不存在**的 PNG（失败会立即停止，以便检查不兼容文件）：

```bash
mkdir -p "/path/to/textures"
for m in /path/to/maps/*.map; do
  id=$(basename "$m" .map)
  if [ ! -f "/path/to/textures/$id.png" ]; then
    python3 work/dream-world-connect-login-map/tools/gepj_decoder.py "$m" --output "/path/to/textures/$id.png" || break
  fi
done
```

Tk 版也能点“打开 .map…”选择仓库外的单个文件，但仍须选择对应 PNG。浏览器版是**生成时的快照**，不是运行时的文件管理器：加入新地图/PNG 后需重新运行 `map_gui_html.py`；地图越多，HTML 也会越大。选择目录不上传文件、不联网。

## 方式一：直接打开离线浏览器 GUI（本环境可用，推荐）

打开 **`work/dream-world-connect-login-map/tools/map-viewer.html`**。这是 `map_gui_html.py` 用 Python 标准库生成的**单文件**图形界面，五张 PNG 和全部原始格值已内嵌；直接在现代浏览器打开即可，**无服务器、无外链、无网络请求**。无需安装 tkinter 或 Pillow。

- 左侧选 `2101`、`2111`、`2112`、`2122`、`2303`。
- 鼠标拖拽平移；滚轮、顶部按钮或键盘 `+`/`−` 缩放；`0`/“适合窗口”回到全图；点击设定位标，右下角可输入像素坐标定位。
- 左侧勾选“原始 LLEC 网格”“空间记录边框”“分块边界”；鼠标悬停或点击可查看像素坐标、原始网格值，以及命中的空间记录编号。
- **警告**：0/1/2 仍是原始值；红色**不是**已经验证的“不可通行”，青框**不是**已经鉴定的 NPC/传送点。

原始地图或 PNG 更新后，重新生成该 HTML（可用 `--output /path/to/viewer.html` 改路径）：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/tools/map_gui_html.py
```

## 方式二：Python Tk 桌面 GUI

有桌面显示并安装 Python `tkinter`/Tk 8.6+ 的机器可运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/tools/map_gui.py --initial 2303
```

这个 Tk 程序同样支持地图切换、滚动条、拖拽、25%/50%/100%/200% 缩放、图层切换、悬停格值和坐标定位；也可用“打开 .map…”选择其他同格式地图及已还原的对应 PNG。不需要 Pillow；不会执行游戏客户端或连接服务器。`--map-dir` 和 `--texture-dir` 可指定自定义资源目录。

**当前沙箱限制**：这里的 Python 未安装 `tkinter` 且没有桌面 DISPLAY，因此无法在本沙箱实际弹出 Tk 窗口；脚本会显示友好的报错。推荐直接使用上面的离线 HTML GUI；桌面 Tk 的数据/坐标逻辑已做无头测试，窗口交互需在有桌面环境人工验收。

## 数据来源与测试

- 源地图：仓库 `map/*.map`（只读）
- 已恢复底图：同目录 `map-textures/*.png`
- 原始格值和空间记录：`map_parser.py`、`map_viewer.py`
- `notes/task-c-地图分析/artifacts/test_map_gui.py` 测试 Python GUI 的格值查询、矩形命中、图层 run、外部目录发现、离线 HTML 生成与 JS 语法（若有 node）。外部目录测试使用已知格式样本的副本，并非对尚未收到的新地图兼容性的证明。

```bash
PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/test_map_gui.py
PYTHONDONTWRITEBYTECODE=1 python3 work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/test_maps.py
```
