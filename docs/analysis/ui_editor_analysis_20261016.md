# UI 编辑器（`ui_editor/`）专项分析报告

> 分析日期：2026-10-16｜分支 `arena/6256d39f-mxsj-tw-2022`（基线 `5ef8aa2`）｜版本对象：**0.8.3**
> 方法：**只读**。读源码 → 在沙箱真实跑测试（含 GUI）→ 反汇编 `mxmain.dll` 独立判定关键假设 → 用真实资源包做端到端写包验证。未修改任何编辑器代码、原包或证据。
> 结论全部可复现；命令见文末附录。

---

## 0. 结论速览

| 维度 | 判断 |
|---|---|
| **它是什么** | 对客户端 `.dlg`（UI 布局，本质是被 XOR 加密的 Python 源码文本）的可视化编辑器：读散装/包内布局 → 画布编辑 → 写回**新** 0SLF 包 |
| **成熟度** | 项目内**最成熟的组件之一**。204 项测试我**全量真跑通过**（含 GUI），核心数据链路覆盖率 90–98%，ruff/wincompat 全 0 |
| **最硬的证据** | 它的核心假设"引擎按 **有序目录 + 二分查找** 寻址"——**我反汇编确认成立**（`0x60DD00` → `0x60E690` 就是 `std::lower_bound`）。这解了项目长期挂着的"线性扫描 vs 有序寻址"悬案 |
| **最实的保护** | 写包：原包不动 → 临时副本 → 逐条逐字节回读比对 → 原生密钥解密校验 → 原子发布；输出与源包/硬链接/符号链接别名一律拒绝 |
| **最弱的地方** | ① 文档与代码漂移（九宫格已实现却在 3 处写着"未做"；`pyproject` 版本停在 0.8.2）② `main_window.py` **1714 行单个类** ③ 格式代码多份分叉（`mxhash`/`native_layout` 与资源编辑器**逐字节相同**，`sprite` 却是两份不同实现，靠人工声明"保持一致"）④ 语料硬门槛 `>2000` 使**仓库内无法验证**它最自豪的那条验收线 |
| **能不能用** | Linux/GUI 侧可用并已验；**Windows 桌面、EXE、进游戏加载、完整 `interface.fls` 语料仍未验**（项目自己也这么说） |

---

## 1. 它做什么，规模多大

- 输入：`.dlg` 布局文件（明文散装，或 `interface.fls` 内 XOR 密文条目）。
- 输出：编辑后的散装 `.dlg`，或一个**全新的 `.fls` 包**（新增/替换布局，可选把新图一并写进包）。
- 代码量：`src` 8,273 行 / 测试 4,483 行（约 1:0.54）；`data/` 另带 1.3 MB `script_index.json` + 102 KB `known_layouts.txt`。

```
src/ui_editor/
├── core/                     # 数据与算法层（约定"零 Qt"，实际 2 个模块例外，见 §5）
│   ├── dlg_codec.py    228   # .dlg ⇄ 字典列表，Big5/GBK 混合字段编解码，保型往返
│   ├── pack.py         137   # 0SLF 只读容器：惰性索引 + 闭式变换解目录
│   ├── pack_build.py   672   # 写包：插入/替换、排序重算下标、回读校验、原子发布
│   ├── native_layout.py144   # 原生路径派生 XOR 密钥（与资源编辑器同一份）
│   ├── mxhash.py       100   # 引擎路径哈希（与资源编辑器/tools 同源）
│   ├── model.py        308   # 控件树 + 撤销/重做快照
│   ├── assets.py       302   # 多包挂载、按路径哈希取图/音（QtGui）
│   ├── painters.py     618   # 38 类控件的近似绘制（QtGui）
│   ├── diagnostics/review/script_index/snap/styles/sprite(_encode)/catalog/layout_import/output_paths
└── ui/                       # PySide6 层（main_window 1714 行 / canvas 539 / panels 496 / property_panel 405 …）
```

数据流：

```
散装 .dlg ──┐
            ├─→ dlg_codec(解析, 字段级 Big5/GBK 解码) → Widget 树(LayoutDocument, 50 步撤销)
包内条目 ────┘                                                │
   ↑ pack.py 惰性索引 / 原生 XOR 解密                          ↓ 编辑
   └──────────── pack_build：排序插入 + r3 按新下标重算 + 回读校验 + 原子发布 ←─ 序列化
```

---

## 2. 核心机制拆解

### 2.1 `.dlg` 编解码：格式是"半个 Python 源码"
文件 = `# -*- coding: gbk -*-` + `# MD5: …` + `UI_INFO = [ {…}, … ]`。
真正的难点不是语法，而是**同一文件里混着两种历史编码**：显示文本字段（`sText/sTitle/sTitles/sTips`）是 **Big5 字节**，资源路径字段（`sFileName/sBarFileName/sBgFileName/sSoundPath`）是 **GBK 字节**。编辑器的做法是：整文件先按 **GB18030 + surrogateescape** 还原成源码形态（不丢任何字节），再**按字段**分别用 big5/gbk 解码给界面；写回时反向。这是它做对了的关键设计——任何"整文件按一种编码处理"的方案都会毁掉数据。

### 2.2 0SLF 容器与"闭式变换"
目录每条 16 字节 `<IIII (entry_id, r1, r2, r3)>`，真实长度/偏移被混淆：

```
len = ((r1*entry_id + 0x0DF25E) ^ r2)
off = ((r2*index*0x00F718FE + 0x0D59D16C) ^ r3)
```

**`index`（该记录在目录里的下标）参与了偏移解码**——这是整个编辑器写包逻辑的支点，也是 §3 的判定对象。

### 2.3 原生存储密钥
`.dlg` 条目不是随机密钥，而是**由包内完整路径派生**：`entry_id = mx_hash(路径)`，`key = ((entry_id + 0x9234AB) & 0xffffffff) ^ 0x937F4912`（我核到这两个常量在 `mxmain.dll` 各出现 1 次）。0.8.3 起新增/替换/迁移一律用它写；旧明文或错密钥只作**读取兼容**，明确保存时才迁移。

### 2.4 写包安全链（这是它最强的一段代码）
`patch_pack_copy()` 的顺序严格执行：拒绝源包/硬链接/符号链接别名 → 布局字面量结构化预检（`ast` 白名单，**不执行任何代码**）→ 独占临时副本上打补丁 → `_verify_copy()`：

1. 目录必须**严格升序且无重复**；
2. **任何 `r1 == 0` 直接拒绝**（"零校验种子"）；
3. 条目集合必须等于 `原集合 ∪ 新增图片 ∪ 目标布局`；
4. **未改条目分块逐字节比对**（明确写着"不以 span 相同代替"）；
5. 目标布局用**原生密钥解密回读**并逐字节等于待写明文（不是从输出头反推密钥的自洽校验）；
6. 附加图片逐条回读一致 → 最后 `os.replace` 原子发布。

我做了一个真实端到端验证（源包 `data/passive.fls`：新增 1 个布局 + 3 个"乱序"资源）：

| 检查项 | 结果 |
|---|---|
| 条目 41 → 45；目录严格递增 | ✅ |
| 原 41 条：引擎查得到 / 负载被改 | 0 条查不到 / 0 条被改 ✅ |
| 新增 4 条：引擎查得到 / 内容回读一致 | 4/4 ✅（新布局还能用原生密钥解出明文并解析出控件） |
| 新包内 `r1 == 0` 条数 | 0 ✅ |

### 2.5 界面层能做什么（摘要）
38 类控件模板（默认属性取自 **47,139 个真实控件**普查）、拖动/把手缩放/等比、吸附+参考线、网格标尺、对齐与等距分布、多选复制粘贴删除、控件锁定（编辑器状态，不写进文件）、50 步撤销重做（同字段合并为一步）、按钮多状态预览、资源树（代际着色/缺失灰显）、包内选图窗（含"添加新图到包/转精灵"）、静态诊断面板（重复名/负尺寸/越界/缺图/编码错误）、保存前变更清单、`.dlg ⇄ script.fls` 静态联动（2,920 布局 / 1,417 模块索引）。

---

## 3. 关键判定：引擎到底是"线性扫描"还是"有序 + 二分"？

这是项目长期挂着的红灯（[`STATUS_HISTORY §3.2`](../archive/STATUS_HISTORY.md#s3-3-2)），而 UI 编辑器的**全部写包正确性**都押在"有序 + 二分"上。我自己反汇编 `mxmain.dll` 判定：

**先确认解码器**（`0x48F170`）：逐条读 16 字节，用 `index` 参与三条闭式变换，输出内存结构 `[entry_id, f1, len, off]`。常量 `0x0E7C83D2` / `0x0DF25E` / `0x00F718FE` 在整份 `.text` 里**各只出现 1 次** → 目录解码只有这一处实现。

**再看真实 LoadFile 链**（笔记 `notes/native_dlg_path_cipher.md` 已更正：`0x48ECF0` 其实是 `ReadFls`，不是 LoadFile）：

```
0x45D580 C_sys.LoadFile
  └→ 0x609760 → 0x6097F0 资源打开
       └→ 0x60DD00  包内定位（我在这里找到决定性代码）
            0x60DD11 call 0x60E080   ; 路径规范化 + 哈希（→ entry_id）
            0x60DD35 call 0x60E690   ; ← 关键：传 (begin, end, &entry_id)
            0x60DD3D cmp %esi,%eax   ; 返回 end ？→ 未找到
            0x60DD41 cmp %edi,(%eax) ; *it != entry_id ？→ 未找到
```

**`0x60E690` 就是 `std::lower_bound`**：

```asm
60e69a: sub %esi,%ecx        ; end - begin
60e69c: sar $0x4,%ecx        ; ÷16 → 记录条数
60e6b0: mov %ecx,%eax ; cltd ; sub %edx,%eax ; sar %edx   ; step = count/2
60e6bd: cmp %edi,(%esi,%eax,8)   ; 比较 *(begin + step*16) 与 key
60e6c0: jae → count = step       ; key ≤ mid → 取左半
60e6c2: → begin = mid+1; count -= step+1   ; 否则右半
```

结论（**与编辑器一致，与旧笔记 §2 相反**）：

1. **引擎对 0SLF 目录用的是二分查找（`lower_bound` + 相等判定）**，命中要求 `entry_id` 相等 → **目录必须按 `entry_id` 升序**。编辑器 0.5.2 的"按编号有序插入"修复方向**完全正确**。
2. **旧笔记 `notes/fls_path_hash_and_dlg.md §2` 的"线性扫描"结论不适用**：那段描述的是 `0x48ECF0`（= `ReadFls`）的取目录路径，而 `.dlg` 走的真实链在 `0x60DD00`。**该笔记需要像 `native_dlg_path_cipher.md` 那样加更正横幅**，否则会持续误导后来者。
3. **反例验证**：我把同一份新条目改成"追加到目录尾（不排序）"，用精确复刻的 `lower_bound` 查询 → **查不到**（插值点落在一个无关的 `entry_id` 上）。这与 0.5.2 记录的"新图不显示、重开条目变少、进游戏卡屏"症状一致，说明当时的根因诊断是对的。
4. 次要结论：`index` 只影响 `len/off` 的解码，`entry_id` 比较与 `index` 无关。所以真正的不变量是**"每条记录必须用它当前所在的下标编码"**——插入点之后所有记录的下标都会变，`r3` 必须整体重算。编辑器正是这么做的（`build_archive` 排序重建 + `_write_located` 迁移时把目录顺移到新负载之后）。
5. `r1` 解码出的 `f1` 落在内存记录 `+4`，**查询路径完全不读它**，用途仍未知；编辑器保守地要求非零是合理防守，不是已被证实的引擎要求（真实 6,056 条无一为 0 只是观察，不是证明）。

> **对本会话第一轮报告的更正**：我在上一轮把这条列为"P0 未决矛盾"，并倾向了笔记的"线性扫描"说法。**这个倾向是错的**，正确的一侧是编辑器的"有序 + 二分"。矛盾本身确实存在，但它是**文档问题**（旧笔记未更正），不是编辑器实现问题。

---

## 4. 我实测的东西（可复现）

沙箱原本缺 `libGL/libEGL/libxkbcommon/libdbus-1`，GUI 组会大面积 Skip/Error（上一轮就是这样：22 ERROR + 34 Skip）。我按项目自己记录过的思路用 `gcc` 造**空符号桩库**（版本脚本需声明 `LIBDBUS_1_3` / `V_0.5.0`）放进 `LD_LIBRARY_PATH`，配合 `QT_QPA_PLATFORM=offscreen`，让 GUI 测试**真跑起来**。桩库只在 `/home/user/qtstubs`，**未入库**。

| 项目 | 命令 | 结果 |
|---|---|---|
| 全套单元测试（**含 GUI**） | `PYTHONPATH=src QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests` | **Ran 204 → OK (skipped=1)**，与项目自述"203 通过 + 1 语料库跳过"**完全一致** |
| 覆盖率 | `coverage run --source=src/ui_editor -m unittest discover -s tests` | **总 81%**；`dlg_codec` 94%、`pack_build` 92%、`pack` 92%、`model` 96%、`diagnostics`/`review` 100%；**`painters` 仅 42%**、`image_picker` 60%、`canvas` 66%、`property_panel` 70% |
| 代码风格 | `ruff check ui_editor` | **All checks passed** |
| Windows 静态检查 | `tools/devkit/check_windows_compat.py ui_editor` | **ERROR 0 / WARNING 0 / INFO 0**（73 文件名 + 62 源文件） |
| 启动自检 | `python ui_editor/bootstrap.py --check-only` | 通过，exit 0 |
| 批处理约定 | 检查 `启动UI编辑器.bat` / `build_exe.bat` | 均 **ASCII + CRLF** ✅ |
| 真实 `.dlg` 编解码 | 仓库内 8 个真实布局（`tools/registration/**`） | 解析 8/8 成功、结构往返 8/8 一致、**逐字节**相同仅 1/8（见 §5） |
| 原生密钥往返回 | `encode_layout` → `decode_native`（真实路径派生密钥） | **8/8 逐字节一致** |
| 38 类控件绘制冒烟 | 用真实 `PaintContext`（零挂载资源）逐个 `paint_widget` | **38/38 无异常**；`iWidth=0` 兜底尺寸 (80,24) |
| 写包端到端 | 见 §2.4（真实 `passive.fls` + 4 条新增） | 全部通过 |
| 引擎算法对拍 | 复刻 `0x60DD00`+`0x60E690` 查询编辑器输出 | 新条目与原条目**全部可定位**；不排序的对照写法**查不到** |

**判断：这个组件的自述是可复现的，没有夸大。** 它是项目里少有"我说通过就真能通过"的部分。

---

## 5. 问题清单（按严重度）

### P1-1 文档与代码漂移，且方向是"低报"
- **九宫格已实现却被三处写成"未做"**：`core/painters.py` 有 `_paint_nine`（三分切、边角不变形），并已注册进分发表 `"CPngNineFrame": _paint_nine`；但 `painters.py` 模块 docstring 仍写"九宫格切分细节等**不在一期范围内**"，根 `README.md §2` 表写"**九宫格（M3.3）未做**"，`docs/STATUS.md` 也写"没有实现…九宫格"。实现本身是**固定三分 + `min(sw, w/2)` 夹取**的近似（真实九宫格通常可配 insets），但"未做"这个说法已经不成立。
- **版本号漂移**：`__init__.py` = `0.8.3`，`pyproject.toml` = `0.8.2`（资源编辑器同病：0.4.3 vs 0.4.2）。影响打包元数据/`importlib.metadata`，且没有任何测试钉住一致性。
- `README.md` 是密到不可读的版本历史堆栈（0.1.x–0.8.3 全塞在正文），`DESIGN.md` 同样按版本段落线性追加。

### P1-2 同一份格式代码多处分叉，靠"人工声明一致"维持
- `mxhash.py`（100 行）与 `native_layout.py`（144 行）在 `ui_editor` 与 `resource_editor` 里 **SHA-256 完全相同**（`6c4b2475…` / `e63722d9…`）——即**两份副本**，注释也承认"Same standalone module is shipped inside both editors"。
- 但 `sprite.py`（229 行，无 Pillow 的解码）与资源编辑器 `core/codecs/sprite.py`（533 行）**是两份不同实现**，`sprite_encode.py` 还在 docstring 里写"编码格式与 `resource_editor/core/codecs/sprite.py` **保持一致**（I0 优先，单行过长自动改用 I1）"——一致性靠**手写声明**维护，没有任何交叉测试。
- 后果：任何格式规则的修正（比如本次 §3 的结论、r1 策略、XOR 密钥）都要在 3+ 处同步改，漏一处就产生"编辑器 A 写的包编辑器 B 读不对"的隐性故障。

### P1-3 `main_window.py` 1,714 行单个类 ≈ 100 个方法
同类对比：`resource_editor/gui/main_window.py` 1,369 行，`script_editor/gui/window.py` **522** 行。UI 编辑器的最大文件里混着菜单/工具栏/资源树/选图窗/脚本面板/诊断/保存评审/写包校验/编辑命令——**唯一真正需要大改时最容易出事的地方**（保存链路的关键校验也都塞在这里，如 `write_pack_copy` 里那段自己实现的"二分模拟引擎寻址"）。

### P1-4 最自豪的那条验收线在仓库内**跑不了**
`tests/test_codec.py` 的语料测试是项目反复引用的"硬门槛：2,706 个 `.dlg` 全部保型往返"，但它：
1. 依赖仓库外语料（`MXSJ_DLG_CORPUS` 或 `/home/user/interface_dlg_decoded`）；
2. 开头就是 `self.assertGreater(len(files), 2000)`——我把语料指向仓库里 8 个**真实** `.dlg` 想部分验证时，得到的是 **FAILED**（8 not greater than 2000），**连这 8 个文件的往返都没跑**；
3. 测试文件里硬编码了开发沙箱的绝对路径（带 `win-ok` 注释，Windows 不受影响，但仍属环境泄漏）。
→ 结论：**这条门槛目前只有作者本机能证明**。仓库内能跑的替代品是我们上面的"8 个真实布局 + 原生密钥往返"，覆盖极窄。

### P2-1 保存必然改写目标条目字节（"未改条目保护"不覆盖它自己）
真实 8 个 `.dlg` 里，`dump_bytes(parse_bytes(x)) == x` **只有 1/8 成立**（那 1 个是编辑器自己生成的夹具）。差异是**格式与键序归一化**（`sWidgetType/sName/iX` 提到前面、`fScaleX 1.0` 之类重排），结构完全一致。
→ 所以：① 哪怕用户只是"打开→保存回新包"不改任何东西，目标条目的字节也会变；② 项目宣称的"未改条目逐字节校验"**天然排除目标布局本身**，这没问题，但读 README 时容易误解为"整体逐字节保真"。建议在 UI/README 里把"目标条目会按编辑器版式重写"写明。

### P2-2 同一包里两套相反的风险态度
`native_layout.path_bytes()` 明确写 "**Never replace unencodable filename bytes**"（不可编码的路径直接抛错）；但 `catalog.py` 与 `main_window.py` 多处用 `mx_hash(name.encode("gbk", "replace"))`——不可编码字符会被静默替换成 `?`，于是**哈希的是另一个路径**。风险不高（路径来自内部字典），但它恰好是本项目最反对的那类"静默替换"，且出现在决定"包里有/没有这条"的判定上。

### P2-3 读取兼容里有一段"猜测型回退"
`unpack_packed_text()` 在明文头反推失败后，会用**列频率法**暴力猜 4 字节 XOR 密钥。它前面有"明文/`[`开头直接返回"的短路、后面有 `validate_plain()` 的 AST 严格校验兜底，实际很难误判；但这是整个"拒绝猜测"的代码库里少见的启发式，且会**静默把旧密钥条目迁移成原生密钥**（文档已声明，属设计选择）。建议在诊断/变更清单里显式标注"本条已从旧存储迁移"，避免用户以为只是改了个字段。

### P2-4 覆盖率的分布与"手感"相反
`painters.py` 42% —— 也就是说**最像游戏的那一层（38 类控件的近似绘制）验证最少**。九宫格、按钮多状态、字体/样式着色都属"以进游戏比对为准"的近似，42% 覆盖配合"编辑器里好看 ≠ 游戏里一样"的固有风险，建议给出**截图对照清单**而不是继续加单测。

### P2-5 `core/` 并非零 Qt，与约定冲突
`core/assets.py`（`QImage`）与 `core/painters.py`（`QPainter/QPixmap/QFont`）都 import PySide6，而项目约定是"`core` 不 import Qt、可在无显示器环境测试"（`AGENTS.md §5.1`）。`core/__init__.py` 已注明这个例外，但后果是：**没有 Qt 的环境会连带 22 项测试报错**（上一轮实测），也让"核心层可无头测试"这条卖点打折扣。建议把这两者移到 `render/` 层。

### P2-6 数据双份、可能漂移
`data/known_layouts.txt`（2,903 条路径）与 `data/script_index.json`（2,920 布局 + 1,417 模块）是**两个重叠的布局路径来源**，分别服务"包内识别/代际标记"和"脚本联动"。两者由不同工具生成（后者依赖 `tools/script_link/build_script_index.py`，**不在 ui_editor 包内**），没有任何一致性测试。

### P3 其它
- 无 CI：仓库里没有 `.github/`，204 项测试全靠人手跑（`gh run list` 里的失败运行属于另一分支）。
- 未做（均已声明）：控件自动接线/消息号规划、脚本源码编辑与编译写回、多布局待入包队列、包外项目文件、Windows EXE 实机。
- 硬门槛 2,706 条语料既不在仓库也不随交付包，`known_layouts` 只有路径没有内容 →"包内全名恢复"永远需要用户侧辅助（已有"按包内路径打开布局"的记忆机制兜底）。

---

## 6. 值得肯定的设计（不只列问题）

1. **身份即路径、路径即密钥**：编辑器不发明任何"项目文件格式"，包外只有明文 `.dlg` 和本机 `QSettings` 记忆，不往游戏目录塞元数据。
2. **写包永不覆盖**：源包、已挂载包、同路径、硬链接、符号链接别名全部拒绝，连"确认后覆盖"的分支都不提供。
3. **验证不靠自洽**：目标布局用**游戏的原生密钥**解密回读逐字节比对，而不是"用我自己的密钥解开我自己写的字节"。
4. **失败即失败**：编码不合法 → 禁止确认保存（GUI 与程序化 `write_pack_copy()` 双闸门）；结构不合式 → 拒绝写 `.dlg` 路径；目录零种子 → 拒绝发布。
5. **静态推断明确标注**：脚本联动、诊断面板、代际着色都写了"静态推断、进游戏为准"，不把索引当运行时事实。
6. **对"不确知"的处理**：`iWidth=0` 取图片尺寸、`fScaleX` 等未知字段原样保留、未知控件类型走 `_paint_fallback` 而不是丢弃。

---

## 7. 建议（按性价比排序）

| # | 动作 | 成本 | 收益 |
|---|---|---|---|
| 1 | 给 `notes/fls_path_hash_and_dlg.md §2` 加更正横幅：`.dlg` 走 `0x45D580→0x60DD00→0x60E690`（**二分/lower_bound**），`0x48ECF0` 是 `ReadFls`；把 `0x60DD00`/`0x60E690` 写进 `notes/native_dlg_path_cipher.md` | 0.5 h | 关掉 [STATUS_HISTORY §3.2](../archive/STATUS_HISTORY.md#s3-3-2) 这条长期红灯，避免后来者按"线性扫描"改坏目录 |
| 2 | 修文档漂移：九宫格三处改口径（说明是固定三分近似）；`pyproject.toml` 版本对齐 `__init__` 并加一条一致性测试 | 1 h | 消除"低报/错报"，让 README 可信 |
| 3 | 把 `mxhash.py` / `native_layout.py` / `sprite*.py` 收进一个共享包（`<pkg>_core` 或顶层 `mx_common/`），三编辑器改为依赖它；加"多实现同源"回归 | 0.5–1 天 | 一处修全处对；本次 §3 的结论只需落一处 |
| 4 | 拆 `main_window.py`：把写包校验（`write_pack_copy` 里的 verifier）、资源树、脚本面板、诊断分别成类/模块；先给 `write_pack_copy` 抽 `core/publish.py` | 1–2 天 | 让最危险的路径可独立测试（现在它只被 GUI 测试间接覆盖） |
| 5 | 把语料门槛改成"可用文件数 ≥ N 即跑，结果按数量上报"，并去掉测试里的沙箱绝对路径；同时把仓库内 8 个真实 `.dlg` 固定为最小语料 | 1 h | 让 CI/任何机器都能验证解码器，而不是只有作者本机 |
| 6 | `painters.py` 转向"截图对照清单"（列出每个控件类型在真机的期望外观，人工核对 + 记录差异），而不是继续堆单测 | 半天起 | 直接对接受伤害最大的风险（画不对） |
| 7 | 保存对话框/README 里明示"目标条目将按编辑器版式重写"，并在变更清单里标出"旧存储迁移"与"版式重写"两类 | 1 h | 消除用户对"我没改为什么字节变了"的困惑 |
| 8 | 统一路径编码策略：`encode("gbk","replace")` 全换 `path_bytes()`（抛错）或在诊断里报告 | 1 h | 与自家红线一致 |

**不建议现在做的事**：扩功能（自动接线、脚本写回、多布局队列）。当前 0.8.3 的边界是清晰的、诚实的，扩功能之前先把"共享 core + 文档一致 + 保存路径可测"这三件事做完，否则每加一个功能都会把 P1-2/P1-3 再放大一次。

---

## 附 A：本次复跑的完整命令

```bash
# 0) 沙箱 GUI 依赖（一次性；桩库不入库，见附 B）
export LD_LIBRARY_PATH=/home/user/qtstubs
export QT_QPA_PLATFORM=offscreen

# 1) 全套测试（含 GUI）
cd ui_editor && PYTHONPATH=src python -m unittest discover -s tests        # Ran 204 → OK (skipped=1)

# 2) 覆盖率
python -m coverage run --source=src/ui_editor -m unittest discover -s tests
python -m coverage report --sort=cover                                     # TOTAL 81%

# 3) 质量闸门
ruff check ui_editor
python tools/devkit/check_windows_compat.py ui_editor                      # 0/0/0
python ui_editor/bootstrap.py --check-only                                 # exit 0

# 4) 引擎寻址判定（反汇编）
objdump -D -b pei-i386 -m i386 --start-address=0x60DD00 --stop-address=0x60DE60 mxmain.dll
objdump -D -b pei-i386 -m i386 --start-address=0x60E690 --stop-address=0x60E760 mxmain.dll

# 5) 写包端到端 + 引擎算法对拍（脚本在 /tmp，未入库）
python3 /tmp/engine_probe_test.py
```

## 附 B：沙箱 Qt 桩库配方（复用项目已验证的思路，**不入库**）

```bash
mkdir -p /home/user/qtstubs && cd /home/user/qtstubs
# libGL/libEGL：收集 offscreen 插件与 QtGui 的未定义 gl*/egl*/glX* 符号后逐个空实现
nm -D -u $QT/plugins/platforms/libqoffscreen.so $QT/lib/libQt6Gui.so.6 ... \
  | awk '{print $2}' | sed 's/@.*//' | grep -E '^(gl|egl|glX)' | sort -u > gl_syms.txt
{ echo 'void _stub(void){}'; while read -r s; do echo "void $s(void){}"; done < gl_syms.txt; } > gl.c
gcc -shared -fPIC -o libGL.so.1 gl.c && cp libGL.so.1 libEGL.so.1
# libdbus / libxkbcommon：需要带版本节点，否则 Qt 加载时报 undefined symbol
gcc -shared -fPIC -Wl,--version-script=dbus_v1.map -o libdbus-1.so.3 dbus.c   # LIBDBUS_1_3
gcc -shared -fPIC -Wl,--version-script=xkb.map   -o libxkbcommon.so.0 xkb.c   # V_0.5.0
```

> 桩库只能证明"代码在导入/建窗/离屏绘制时不崩"，**不能替代 Windows 桌面与进游戏验收**；本报告所有 GUI 结论均标注了这一边界。
