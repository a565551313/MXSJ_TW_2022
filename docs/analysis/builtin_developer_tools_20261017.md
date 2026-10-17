# 客户端内置开发工具与 UI 编辑器：只读调查

日期：2026-10-17。对象：本仓库客户端 `data/script.fls`。本轮不修改客户端、权限、密钥或编辑器，不启动游戏、不执行恢复出来的脚本。

## 结论摘要

1. **确实带有一套完整度较高的内置 UI 编辑器**，不是只有入口占位。主体在 `script/uieditor/`，覆盖预览、控件列表、节点列表、属性编辑、撤销重做、复制粘贴、对齐分布、层级调整和本地布局保存。
2. **预览调用游戏自己的控件类**，不是像外置编辑器一样用 Qt 近似绘制。但它也对定位/提示/热区使用编辑占位，对构造失败使用错误占位；不能把预览完全等同于实际业务界面。
3. **保存写到工作目录的 `interface/<资源路径>.dlg` 明文文件**，不是直接更新 `interface.fls`；查到的保存函数里没有资源包加密/重打包步骤。
4. “开发者模式”不是一个统一开关：`innerversion.IsInnerVer()`、`permission.GetSpecialVersion()`、GM 开关、启动参数中的 MAC 条件分别存在。本客户端脚本里的 `IsInnerVer()` 返回 False。
5. 最值得借鉴的是 `widgetconfig.py` 的控件默认值/属性定义、原生控件构造路径、`ui.lst` 字体字段，以及原生保存格式。它可以作为外置编辑器的参考和原生渲染对照，不应未经验证直接替代现有写包链。

## 证据等级与方法

- **实测（离线）**：从固定原包定向读取条目，按既有密钥目录解密、基线转译到标准 Py2.5 字节码，再解析 marshal/指令/常量；不执行 code object。下面的调用链、字符串和偏移来自本次重新读取原包，不只依赖旧反编译文本。
- **静态分析**：根据字节码控制流推导入口条件、读写路径和界面能力。
- **未验收**：本次没有 Windows 游戏内打开这些工具，没有验证本机权限状态、完整依赖、文件覆盖优先级或保存后重启加载。
- 旧 pycdc 产物只作交叉参照，不视为可直接执行/回编的源码。部分条目可见接缝乱码，例如 entry 2751 的某个对齐信号名、entry 4538 的文件名；不擅自修复并声称恢复完整。

锁定输入（调查前后未改）：

| 输入 | SHA256 |
|---|---|
| `data/script.fls` | `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72` |
| `tools/decompiler/script_fls_keys.json` | `43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb` |

定位入口：`script_manual/inventory/modules.jsonl`（函数/类清单）；解码复用 `tools/script_link/build_script_index.py` 的 `read_entries`、既有 `batch_decompile._decode_segments/_transpile_once`、`parse_pyc/iter_ops`。本轮临时反汇编在仓库外，不批量生成或提交恢复源码。

## 1. UI 编辑器主体

下列编号均为 script.fls 的 **0 起始条目索引**，不是路径哈希。

| 条目 | 脚本 | 职责 |
|---:|---|---|
| 2751 | `script/uieditor/dlguieditor.py` | 编辑器窗口、原生预览、节点/控件/属性面板 |
| 918 | `script/uieditor/dgtuieditor.py` | 界面事件代理、快捷键、打开/新建/保存/对齐 |
| 3495 | `script/uieditor/mduieditor.py` | 编辑状态、控件增删改、命名检查、读写布局 |
| 3399 | `script/uieditor/editorcommand.py` | 命令历史：AddCommand / Undo / Redo |
| 3853 | `script/uieditor/widgetconfig.py` | 控件类型名称、默认值、属性面板定义、类型转换 |
| 993 | `script/uieditor/explorer.py` | 内置资源选择器 |
| 3931 | `script/uieditor/getinterfacefilelist.py` | 开发目录文件列表生成工具 |

另外还带有 `uitrans_*` 系列转换脚本；它们的目标格式和安全性本轮未展开验证，不能只凭命名就拿来批量迁移布局。

### 编辑器界面本身也是一个布局

entry 2751 `CUIEditorDlg.__init__` 在字节码偏移 18 加载 `dialog4/uieditor.dlg`，交给 `combdialog.CCombDialog` 构造。

`InitDlg` 组装：

- `CPreviewDlg`：预览区；
- `CWidgetListDlg`：可添加的控件列表；
- `CNodeListDlg`：节点列表；
- `CAttrListDlg`：属性面板。

所以仅脚本存在不保证窗口能打开，仍需要编辑器自身布局、图片和字体等资源。本仓库没有 `interface.fls`，本轮不能完整验证这些资源依赖。

### 静态确认的操作

- 打开 `.dlg`、新建布局、保存；
- 添加、删除、复制、粘贴，控件名字有效性与重复名修正；
- 改位置和属性、控件 Z 次序调整；
- 撤销、重做；
- 水平/垂直居中、四边对齐、水平/垂直间距；
- 4To3 状态切换（具体转换效果本轮不作结论）；
- 图片路径选择器过滤 `.igs` / `.png` / `.spr`。

entry 918 `CUIEditorDgt.Init` 明确注册方向键、Delete、Ctrl+S/Z/Y/C/V。这里只确认注册，不外推输入焦点冲突、拖动体验或每个操作的运行正确性。

## 2. 怎么进入：至少两条 UI 编辑器入口

### A. GM 命令 `$uieditor`

entry 1572 `script/data/gmcommanddata.py` 的命令数据登记：

```text
$uieditor → OpenUIEditor → dlguieditor.CreateUIEditor()
```

- `OpenUIEditor` 的 IMPORT_NAME 位于偏移 6，CreateUIEditor 调用位于偏移 18。
- 命令元数据标有“指令权限”字符串 `99,`；**不等于每条实际调用路径都会自动执行同一权限判断**。
- 已追到 entry 4947 `script/mxgame/inner/clientcommand.py:DoCommand`：偏移 48–64 先调用 `permission.IsOpenGm()`，不通过则返回；之后偏移 160–172 调用 `gmcommanddata.Function`，由命令表匹配并执行本地处理函数。
- `permission.IsOpenGm()`（entry 1125）调用 `GetPermission('gm')`。权限数据由 `InitPermission` 从 `cfg.GetSysDict('nocheck')` 的 `game` 节读取，`GetPermission` 把对应值与字符串 `'1'` 比较。

**结论**：已确认命令和一条调度链，但本次未验证用户当前运行环境是否允许执行。不能直接承诺输入命令一定打开，也没有改权限去绕过条件。

### B. 启动参数调度 `uieditor`

entry 1904 `script/param.py` 的 `CMD2CALLNOW` 登记 `uieditor → StartUIEditor`。`RunAferStartParam` 拆分传入参数后按表调用。

`StartUIEditor` 字节码：

- 偏移 36–58：`misc.GetMAC()` 与硬编码值 `90004e73cec6` 比较，不相等就返回；
- 偏移 75–90：延迟 0.5 秒调用 `dlguieditor.CreateUIEditor`；
- 另延迟调用 `interface.SetDefaultButton(None)`。

**结论**：这是带特定机器条件的开发入口，不应把 `uieditor` 当作当前客户端任何电脑都通用的启动参数。本轮也未追到原生进程命令行到 `RunAferStartParam` 的完整传参链。

## 3. 几种“开发模式”判断不是一回事

| 判断 | 本轮看到的实现 | 边界 |
|---|---|---|
| `innerversion.IsInnerVer()` | entry 2001：LOAD_GLOBAL False → RETURN_VALUE | 当前原包脚本直接返回 False；不代表别的版本或运行时替换后的值 |
| `permission.GetSpecialVersion()` | entry 1125：惰性调用 `InitSpecialVersion`，缓存 `os.path.exists('nocheck')` | 相对工作目录；不是靠命令表里的 `99` 判断 |
| `permission.IsOpenGm()` | entry 1125：`GetPermission('gm')` | 是另一项配置权限；不是仅看路径存在 |
| `param.StartUIEditor()` | entry 1904：MAC 精确比较 | 仅这条启动入口的检查，不应套在所有入口上 |

`GetSpecialVersion()` 对 UI 编辑器的实际影响：entry 3495 `ReadFromFile` 偏移 42–54 检查它，不通过走“非内部人员，不可以使用内部UI编辑功能”错误分支；通过才读取布局。

因此，“能叫出编辑器窗口”和“能加载布局开始编辑”是两件不同的事。本报告描述原有条件，不提供修改原包或解除条件的补丁。

## 4. 为什么原生预览特别有价值

entry 2751 `CWidget.CreateRealWidget`：

- 一般控件在偏移 116–154 调用 `combdialog.GetClsObj(sWidgetType)`，再以 `dUIInfo` 为参数构造游戏控件；
- `CBox` / `CBoxWithTips` / `CHotBox` 特意用 `interface.CBoxObject` 彩色框标注；
- 构造异常时退回错误占位并提示“控件参数异常”；
- `RefreshSize` 读取 `m_oRealWidget.GetSize()`，把真实尺寸用于编辑包装框。

`CPreviewDlg.LoadUIWidget` 根据 `bLoad` 决定构造、根据 `bShow` 设置可见性，读取 `iX/iY`、`sName`、`sWidgetType`，递归加载 `lChildren`。

**对现有外置编辑器的价值**：可用于校对真实尺寸、九宫格/三宫格、按钮样式、字体等。外置 `ui_editor/core/painters.py` 的 Qt 近似不应反过来当原生显示标准。

**限制**：编辑预览自身有包装和占位；`CFakeDlg.OnMessage` 目前看到的是日志输出，不是业务脚本的完整事件处理。仅增加 `iMsgId` 不等于自动接上游戏功能。

## 5. 打开与保存的真实行为

### 打开

entry 918 `CUIEditorDgt.GetFileInfo` 合并 `file_interface.FILE_INFO` 与 `GetTmpFileInfo()` 扫描的本地 `.\\interface` 文件树，不只是现场枚举包目录。

entry 3495 `CUIEditorMgr.ReadFromFile`：

1. 规范化路径分隔符；
2. 检查特殊版本状态；
3. `C_sys.LoadFile(sFilePath, 'interface')`；
4. 得到内容则清理 CR，再执行布局文本、取出 `UI_INFO`；
5. 读不到时还存在路径变模块名（`/` → `_`，去扩展名）后 `__import__` 的回退。

**不要在游戏内打开来历不明的布局**：这里是执行文本/导入模块，不是外置编辑器那种仅解析字面量的安全读取。上面的 `exec` 是字节码观察结果，本调查没有执行它。

### 保存

entry 3495 `CUIEditorMgr.SaveCurFile` 的关键证据：

| 偏移 | 行为 |
|---:|---|
| 24–42 | `os.path.join(os.getcwd(), 'interface')` |
| 219–237 | 把目标相对资源路径接在 interface 目录后 |
| 240–270 | `GetUIWidgetList` → `FormatDict` → `'UI_INFO = %s'` |
| 277–289 | `open(目标路径, 'w')` |
| 292–317 | 写编码头与固定 MD5 注释 |
| 318–340 | 写布局文本、关闭文件 |

写入头为：

```text
# -*- coding: gbk -*-
# MD5: 12345678901234567890123456789012

UI_INFO = ...
```

`FormatDict` 自己递归格式化 dict/list/tuple/str，字典走 `iteritems()`，不是原布局字节保真保存。MD5 行在这条保存路径是固定文本，**不是该函数计算出来的内容摘要**。

例如目标资源路径 `dialog4/example.dlg`，输出是工作目录下的 `interface/dialog4/example.dlg`。已有同路径文件会被 `'w'` 覆盖；新建流程另会生成时间戳文件名。

**未见直接更新 `.fls`**，也未见在这里调用路径密钥加密。散装文件在当前客户端的最终加载优先级、是否需要重载/重启，仍需追 `C_sys.LoadFile` 或做客户端副本实测，不能仅凭这条保存路径下结论。

## 6. 同时存在的其它开发工具入口

下表为 entry 1572 命令表及对应函数的静态线索，不是“本机全部已可用”的清单。各工具仍需单独核对权限与资源依赖。

| 命令 | 处理函数 | 用途/本轮核对范围 |
|---|---|---|
| `$uieditor` | `OpenUIEditor` | 本报告主线，原生布局编辑器 |
| `$uimix` | `UIMix` | UI 快捷工具；检查 `IsInnerVer()` 后才调用 `mixinfunc.DoMixIn()`，该依赖未在本轮目录中确认 |
| `$openmapeditor` | `OpenMapEditor` | 有当前地图对象才调用 `dlgplaceobjeditor.Show()`；不是据此就能认定支持全部地图格式编辑 |
| `$warlocation` | `WarLocation` | 战斗站位工具入口 |
| `$coloreditor` | `OpenColorEditor` | `dlginnercoloreditor.Show()` 染色编辑器 |
| `$hsveditor` | `ShowHsvEditor` | HSV 染色工具入口 |
| `$uiprofile` | `OpenUIProfile` | UI 性能工具入口 |
| `$btnlighteditor` | `OpenBtnLightEditor` | 按钮帧数/显示调整入口 |
| `$File` | `StartExplorer` | 内置资源浏览器入口 |

另有调试、录制、特效和脚本相关命令；本轮不把整张 GM 命令表当作安全可随意运行的工具箱，更没有执行任何服务器指令。

## 7. 建议怎么利用，而不是继续盲做外置编辑器

1. **优先提取 widgetconfig 的属性表与默认值，和现有外置编辑器交叉核对。** 这里是客户端作者自己写的编辑配置，比从大量布局取众数更接近设计意图；但它可能只覆盖可编辑子集，不能直接覆盖所有现有模板。
2. **把内置原生预览当渲染参照。** 用户已有“添加控件后游戏能显示”的实测，不要求重复；以后调查九宫格、字体或某类特殊控件时，直接对比原生编辑器相同数据更有针对性。
3. **保持当前外置编辑器的安全写包路径。** 原生编辑器保存散装明文，我们的工具能生成新包并校验，两者职责并不重复，可以配合使用；在确认散装覆盖顺序前不自动部署。
4. 下一步若授权深入，先做“原生 widgetconfig 与外置属性/默认值差异表”，再决定改什么；本轮未改实现、未开启模式、未新增自动接线。
