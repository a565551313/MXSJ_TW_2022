# 项目与脚本编辑器分析（2026-10-27，只读分析轮）

> 本文是**分析记录**，不是验收报告、不是路线图、也不改变任何代码或原包。
> 事实分三类标注：**实测**（本轮真跑出来的数字）、**读码**（从源码/文档读到的事实）、
> **推断**（我的判断，写明依据）。当前分支 `arena/0186dc92-mxsj-tw-2022`，起点 `212a034`。
>
> 本轮没有修改任何产品代码、原包、参数表；只新增本文（以及 STATUS 的一条登记）。

## 0. 本轮实测环境

| 项 | 值 |
|---|---|
| 主机 | Linux 沙箱，Python **3.11.2**（PEP 668 保护，系统 pip 不可装包） |
| 额外环境 | `/tmp/se-venv`：PySide6 6.10.3（**Qt 导入失败**，见 §6.6）、xdis 6.3.0、uncompyle6 3.9.4.dev0、ruff 0.17.3 |
| 锁定输入摘要（前后未变） | `data/script.fls` `8b6e9266…c0d72`（24,454,082 B）、`data/data.fls` 354,143 B、`decoding/script-original.json` `43bb090d…daceb` |
| 未执行 | Windows 客户端、两套 Windows 编译器的真实执行、EXE 构建、GUI 交互 |

---

## 1. 项目是什么（一句话与三条不变量）

**实测/读码**：仓库根目录就是一份《夢想世界》台服 v2.27.2 客户端安装目录（`mx.exe`、`mxmain.dll`、
`data/*.fls`、`map/*.map` 都在根上），在此之上叠加了逆向研究、工具链、四个编辑器与一个
Python 服务端设计/骨架。它不是可游玩服务端，也不是已验收的客户端发行版（README 首段明说）。

三条贯穿全仓的不变量（读码：`AGENTS.md` §4、各子项目 README）：

1. **原包只读、生成物写仓库外或新文件名**（0SLF 写回一律新包 + 硬链接 no-clobber）。
2. **"能展示 ≠ 能运行，能运行 ≠ 正确，测试通过 ≠ 原生验收"** —— 所有完成声明必须带范围与可追溯证据。
3. **原生优先**：能用原生控件/`.dlg`/`ui.lst` 实现的，不得用贴图或 overlay 糊。

这三条决定了整个仓库的形态：几乎每个模块都自带 `README`/`DESIGN`/证据 JSON，并且大量测试
**故意以 skip 表达"外部材料没到"**（见 §6.5 对这件事的批评）。

## 2. 仓库地图与体量

| 区块 | 内容 | 体量（读码 + `du`/`find`） | 成熟度（我的判断） |
|---|---|---|---|
| 客户端材料 | 根目录 `*.dll`/`*.exe`/`data/*.fls`/`map/`/`Fonts/` | 1.1 GB 工作树，`git ls-files` 3,220 个文件 | 只读输入，摘要被多处钉死 |
| 逆向研究 | `notes/`（结案笔记）+ `tools/decompiler`、`tools/data-parser`、`tools/dyprot_unpack` | `notes/` 280 KB、无 `.py`；`tools/` 145 MB / 780 个 `.py` | 深，且带"未验/边界"段落；`_dyprot` 54% 仍未解 |
| 编辑器 | `script_editor`(29 MB/121 py)、`ui_editor`(3.5 MB/145 py)、`resource_editor`(665 KB/65 py)、`map_editor`(821 KB/29 py) | 四个独立 PySide6 工具，`core` 无 Qt | 最成熟的一块；UI 编辑器 0.21.0 / **932 项测试**，地图编辑器 1.0.0（101/101 图） |
| 共享核心 | `mx_common/`（真源）+ `tools/devkit/vendor_core.py` 分发到各编辑器 | 单一真源、生成副本 | 明确的所有权设计，值得照抄 |
| 服务端 | `server/src/mxsj_server`（账号/角色第一阶段）+ `mxsj_catalog` + `review_api`(FastAPI) + `review_web`(React) | `server/` 15 MB / 202 py；`local_server/` 152 py | 只读复核链完整；TCP/进图/PostgreSQL 未实现 |
| 协议模拟 | 根 `mock_server.py` / `mock_server_v2.py` | 各 ~197 KB | 有明确副作用边界文档；**仓库根有重复副本**（见 §6.7） |
| 文档/证据 | `docs/`（STATUS/ROADMAP/约定/168 份 md）+ `docs/analysis/evidence/` | 3.2 MB | 密度极高，是本项目最稀缺的资产 |

**推断**：这个仓库真正的"产品"不是任何一个编辑器，而是**一套证据纪律**——每个断言都能回溯到
`sha256sum`、反汇编地址、测试输出或用户实机回执，并且每一轮都在文档里写清"未验/边界"。
接手成本高（`AGENTS.md` 23 KB + `STATUS.md` 上百条 blockquote），但犯"把推测当事实"这类错的概率被压得很低。

---

## 3. 脚本编辑器：定位与版本

**读码**：`script_editor/` 版本 `0.6.0.dev9`（`src/script_editor/__init__.py`），
`requires-python >=3.10,<3.16`，Qt 按宿主版本钉死（3.10–3.14 → PySide6 6.10.3，3.15 → 6.12.0）。

- 源码规模：`src/` **9,370 行 / 11 个包**，`tests/` **8,183 行 / 33 个测试模块 + 3 个夹具模块**（测试:源码 ≈ 0.87）。
- 独立可复制：不 import 仓库里的 `ui_editor`/`resource_editor`/`tools`（`DESIGN.md` 明确要求）。
- 分层：`src/script_editor/core/`（无 Qt，可在无显示器环境测）、`gui/`（PySide6）、`data/`（恢复工作进程）。

```
core/archives/    0SLF 与 FLS\0 只读索引 + 受限写包（readers/fls0slf/flsdata/writer/verify/document）
core/vm/          自写 marshal 语法树、双 VM opcode 表、py25 五段 XOR、py27 双流分离
core/compiler/    标准 CPython 2.5.6 / 2.7.13 子进程编译与审计、运行时清单与发行
core/inspection/  原嵌入文件名、静态引用/符号线索、编码转义
core/services/    包自检、路径索引、恢复引擎（双引擎）、语料清单、原生写包、工作流
core/project/     .mxscript.json schema3 工作现场
gui/              window/workspace/menus/actions/code_editor/source_tab/jobs
data/             recovery_worker.py（独立进程）、compile_legacy/audit_legacy
runtimes/         py25/win-x86、py27/win-x86（各 9 个文件，共 20 个，24 MB，已入库）
```

## 4. 数据管线：从包字节到可编辑草稿，再回到新包

**读码**：整条链是单向可验证的，每一段都有独立复核：

```
.fls ──索引（只读头部/目录，惰性）──▶ 存储字节
     ──严格解压（zlib / raw-deflate）──▶ 原生 marshal
     ──参数校准（py25：五段 XOR；py27：无）──▶ 原生 pyc
     ──opcode 映射逆变换──▶ 标准 CPython pyc（魔数 b3f20d0a / 03f30d0a）
     ──独立进程反编译（uncompyle6 + 可选 pycdc）──▶ 未核验草稿
用户编辑 ──标准编译器子进程（-E -S，30s 超时）──▶ 新标准 pyc
     ──等宽 opcode 变换──▶ 原生 marshal（py25 固定扩展长度补零）
     ──XOR + zlib / 重压缩 + CRC──▶ 新条目
     ──流式写包（保留物理布局）──▶ 新文件（硬链接发布，拒绝覆盖）
     ──重开新包、独立逆变换、逐条比对、完整 marshal 读取──▶ 通过才叫"出包"
```

### 4.1 容器解析（`core/archives/`）
- 0SLF：12 字节头 + 16 字节目录记录，长度/偏移用闭式变换还原
  （`clen = ((r1*id + 0xDF25E) ^ r2)`，`doff = ((r2*i*0xF718FE + 0xD59D16C) ^ r3)`）。
- `FLS\0`：64 字节头 + 18 字节本地记录 + raw-deflate；尾部给中央目录偏移；文件名 XOR 0xA5 的 GBK。
- 跨平台坑写进了代码注释：Windows 无 `os.pread`（退化为加锁 seek+read）、必须 `O_BINARY`
  （否则 0x1A 被当 EOF 静默毁包）。这是真实事故（0.2.0 Windows 上报错）留下的防线。
- `ArchiveDocument` 打开时抓 `fstat` 修订三元组，并在读取/指纹前后 `_assert_unchanged()`
  （同时比对**原句柄**与**重新打开路径**，防路径被替换）——对应 0.4.1 修过的 Windows ctime 误报。

### 4.2 VM2.5（script）：不是"查表 XOR"，而是算法反推
**读码**（`core/vm/py25/cipher.py`）：key 的语义是**模块名 seed**：

- `module_seed(name)` 逐字符累加 `character_seed(position, byte)`（自带一个 0x7E79 乘加迭代），
  `next_seed(s) = s ^ ((s*0x788B + 0x024543DF) % 0x7F63)`，取 5 个 `&255` 作五段 key；
- 段边界 `bounds_from_seed(seed, size)` 由 `size//5 + seed//256` 递推 5 次；
- 从 key 反推 seed 必须**唯一**（`seed_from_keys` 在 `range(k0, 32768, 256)` 里搜，多于/少于一个都报错）。

这样做的直接后果：研究用的 key 表只是"候选证据"，真正身份由
`module_seed(name)` 与 `mx_hash(name + b".s") == entry_id` 双绑定（`resolve_parameters`）。
短模块出现重复/缺失键或五键碰撞时**不选第一个**，无解就拒绝。这条设计在 dev7 修
"研究边界错 3 字节仍能解析"时是决定性的。

### 4.3 dev9 的关键产品决策：登记表降级为缓存
**读码**（`core/services/bundled_catalog.py` + `package_selfcheck.py`）：
以前"整包 SHA 必须登记过"才自动套参数，用户每重打一次包就得重新登记——这是产品缺陷。
现在：指纹命中 → 直接套用；未命中 → 用**唯一一份**已授权参数表对**每条**允许条目做严格解码
（严格解压 → 原生边界校准 → 严格 marshal），成功率 ≥99% 自动套用并点名坏条目，<99% 整包拒绝。
参数来源没有变（仍是 `decoding/script-original.json`，SHA 钉死），变的只是"用到哪个包上"，
而这个结论由数据自己逐条证明。**这是整个工具里我最认可的一处设计**：把"权限"与"缓存"分开。

### 4.4 VM2.7（data）：指令流/参数流双分离
**读码**（`core/vm/py27/{forward,inverse}.py`）：原生把 code 拆成 ops/args 两条流，
跳转目标要在**两个坐标系**上同时换算（`byte_to_op` / `byte_to_arg`）；
`EXTENDED_ARG`、寻址 >uint16、非边界跳转、坐标不一致一律拒绝，不截断不猜。
`tests/evidence/py27_dispatch.json` 钉了 `exe/python27.dll` 的 SHA、两张分发表 RVA 与处理器字节。
注意 `native 66` 被明确判为"走未知指令"，不是历史笔记里的 `STORE_SLICE` 别名，且**永不发射**。

### 4.5 恢复层：两个独立进程，互不背书
**读码**（`core/services/{module_browser,recovery_process,pycdc_engine,recovery_candidates}.py`）：
先严格 marshal/VM 校验，再跑引擎；每流 2 MiB、总输出 16 MiB、30 s 超时、POSIX 杀进程组；
恢复结果协议 `mxsj-recovery/2` 逐字段校验（引擎版本不符直接拒）。
`complete=True` 只表示"引擎自己跑完了"，metadata 明写 `syntax_checked=false / semantics_verified=false`。
pycdc 是 GPLv3 独立程序，只从外部固定目录+清单加载、复制确定字节到临时目录执行，
许可证与完整对应源码必须随发行（`licenses/recovery/`）。
**Git 里只有 pycdc 源码 tar 包与 README，没有 Windows pycdc 二进制**——所以纯 Git 克隆只能跑单引擎。

### 4.6 写包：字节透明 + 独立回读
**读码**（`core/services/native_build.py`、`core/archives/writer.py`）：
- 0SLF 目录**必须已按 entry_id 严格升序**、`r1 != 0`；写包保留目录的物理位置、条目间空隙与尾部字节
  （真实包里物理顺序与目录顺序并不一致）；只重算 `r2/r3` 与头里的目录偏移。
- py25 改动若超过原扩展长度 → 直接拒绝（"authored marshal exceeds fixed XOR length; no shrink/rescale"）。
- 发布用 `os.link(tmp, dest)`：目标已存在即失败，文件系统不支持硬链接也失败，**不退化为可覆盖写**。
- 回读不是"再解一遍自己刚写的东西"：`verify_output` 逐条比元数据、比未改区域字节，
  对改项从**实际新包**解压/解密/逆变换，要求与新编译的 pyc 逐字节相等，再交给精确版本 CPython 完整 marshal 读取。
- 1288 由 `core/policy.py` 一处集中排除（读负载之前就返回），不是各处散落的 if。

### 4.7 GUI
**读码**（`gui/*.py`，2,900 行左右）：菜单 5 个（文件/恢复语料/编辑/编码/编译/视图）+ 工具栏；
左侧包树（统一按 `script/login/register.py` 这类**包内路径**显示，ID 留在悬停）、
中央多标签编辑区、右侧"来源与状态"+大纲、底部诊断/布局引用/差异三个页签。
值得注意的工程细节：
- 长任务统一走 `Window.task()`：禁用中央部件 + 全部 `QAction` + 菜单栏 + 所有 dock，
  关闭主窗口被拦，回调显式排队回 GUI 线程（Qt 跨线程直接改控件是这类工具最常见的崩法）。
- 菜单/QAction 保持强引用（注释写明：枚举菜单动作后 C++ 对象被回收会崩）。
- 保存前核对磁盘 SHA（外部改动/删除/新建冲突 → 拒绝覆盖并保留编辑与撤销）。
- 恢复草稿首次 `Ctrl+S` 必须另存新 `.py`，不顺手套写回包。

---

## 5. 本轮实测结果（都是我在这台机器上真跑出来的）

| # | 检查 | 结果 |
|---|---|---|
| 1 | 内置参数对 `data/script.fls` 逐条严格解码（`verify_with_catalog`） | **通过，0 失败，5,001 条路径**，耗时 **6.27 s**；`4007 → script/login/register.py` 正确 |
| 2 | py25 全量 `native → standard → native` 往返（5,001 条，1288 排除） | **5,001/5,001 字节完全一致**，耗时 **52.4 s**（含 zlib+XOR+marshal+opcode 双向） |
| 3 | py27 全量往返（`data.fls` 121 条脚本 / 133 条目） | **121/121 字节一致**，耗时 **0.42 s** |
| 4 | 无改动重写 `script.fls` / `data.fls`（`write_script`/`write_data` 空 changed） | **两包 SHA-256 与原文完全一致**（24,454,082 B / 354,143 B） |
| 5 | 单元测试（系统 Python，缺 PySide6/xdis） | 376 项：**5 失败 / 2 错误 / 120 跳过**（失败几乎全是环境缺依赖） |
| 6 | 单元测试（`/tmp/se-venv`，装齐 PySide6+xdis+uncompyle6） | 376 项：**1 失败 / 120 跳过 / 0 错误**，8.6 s |
| 7 | 跳过原因分类（`-v` 逐条统计） | GUI 缺 `libGL.so.1` **72 项**；未配置真实标准 2.5.6/2.7.13 编译器 **21 项**；外部语料/真包/pycdc 需 opt-in **27 项** |
| 8 | `ruff check script_editor`（0.17.3） | **All checks passed** |
| 9 | `python -m script_editor.runtime_cli audit --root . --static` | 通过：两套运行时各 9 个文件摘要与 `manifest.json` 一致，`execution: not-executed`（如实标注） |

**唯一真红灯**（与 STATUS 2026-10-24 记录的 P1 一致）：
`tests/test_package_selfcheck.py:225` 断言仓库内 `data/script.fls` 的指纹是
`a45e0e49ed33…`，实际是原包 `8b6e9266bbe9…`。`verify_with_catalog` 本身**通过了**
（前三个断言全过），失败只在最后一行哈希钉。`decoding/README.md` 第 35 行也写了
"本仓库 `data/script.fls`（`a45e0e49…`）5001/5001 通过"，与事实不符。

---

## 6. 问题清单（按优先级；均给出位置与证据）

### P1 · 包指纹钉与文档陈述互相矛盾（真红灯，会挡住"全绿"）
- `tests/test_package_selfcheck.py:225` 期望 `a45e0e49ed33`（2026-10-23 的注册派生包），
  仓库里的是原包 `8b6e9266…`。
- `decoding/README.md:35` 同样把本仓库包写成 `a45e0e49…`。
- 两条互斥的可能：① 仓库应放派生包（不该，原包是锁定输入）；② 测试与文档应改成原包摘要 +
  保留 `a45e0e49` 作为"已登记派生包"的独立用例。**我倾向 ②**，并且应该同时断言两个包都能解码，
  否则这个测试的价值（"仓库自带包必须过自检"）被一个不该存在的哈希钉削弱了。

### P2 · `test_bootstrap` 的 4 项失败是"假红"，但它暴露了测试写法问题
- 系统解释器没有 PySide6 时：`test_supported_python_normal_start_reaches_app`（3 个 subTest）与
  `test_python314_normal_start_reaches_app_without_recovery_dependency` 失败。
- 原因（读码 + 复现）：测试用 `patch.dict("sys.modules", {"PySide6.QtWidgets": SimpleNamespace()})`
  伪造模块，但 `bootstrap.main()` 里是 `__import__("PySide6.QtWidgets")`，
  它会先找顶层 `PySide6`；顶层不在 `sys.modules` 里就抛 `ModuleNotFoundError`（`ImportError` 子类）
  → 返回 2。装了真 PySide6 后这 4 项立刻变绿（实测 #6）。
- 影响：**在没有 GUI 依赖的机器/CI 上，这套测试必然红 4 项**，容易被误读成产品坏了。
  建议把 `sys.modules` 补成 `{"PySide6": SimpleNamespace(QtWidgets=...), "PySide6.QtWidgets": ...}`，
  或用 `patch.object(bootstrap, "__import__")`/把导入抽成小函数再 mock。

### P2 · 两处 docstring 已过期，且同一文件里自相矛盾
- `src/script_editor/core/services/native_build.py:1`："Fail-closed native build API **(not yet wired to the GUI)**"
  —— 实际 `gui/build_actions.py` 已通过 `core/services/workflow.py` 全量接线（F6 → 清单 → 新包 → 承接）。
- `M2_NATIVE_BUILD.md` 首段"GUI仍禁用写包，M3再接入"，而该文件第 5 行又写"GUI现已由M3接入；
  下面第一段的禁用说明仅描述M2最初阶段"。同一文件两句话打架。
- 这类"文档说没做、代码已做"的漂移，正是 `AGENTS.md` §6 反复警告的东西。

### P2 · 跨模块导入私有函数
`core/services/workflow.py:20` `from .native_build import Replacement, _native, build_package`
—— `_native` 是下划线私有 API。要么在 `native_build` 里提供公开入口（例如
`encode_replacement(...)`），要么明确它是包内 API 并去掉下划线。否则重构时最容易断在这里。

### P3 · 88 列约定事实上没有被闸门覆盖
实测：`src/` 里有 **73 行 > 88 字符**，但 `ruff check` 全绿（0.17.3）。
原因：超长部分几乎全是中文行/长点分字符串这类**单个 token**，`E501` 不报；
唯一在第 89 列之后还有空格的那一行（`src/script_editor/data/compile_legacy.py:27`）末尾带 `# noqa: UP031 - …`，
noqa 覆盖整行，所以也没被报。
结论：`docs/PYTHON_TOOL_CONVENTIONS.md` §1 的"88 列"目前是**风格期望**，不是强制。
要么接受并在约定里注明，要么加 `--preview --select E501` 或专门的格式检查（`ruff format`/`black`）
并一次性修掉。不要留着"我们遵守 88 列"的说法，因为现状不成立。

### P3 · 120 项 skip 的表达风险
测试用 skip 表达"'外部材料/真编译器/桌面'不具备"，这在哲学上是对的（不能把跳过算通过），
但输出只有一行 `skipped=120`，**数字本身读起来像"基本全过"**。
建议：在 `tests/` 里加一个 `failUnlessEnoughSkippedIsExpected()` 风格的守卫，
或让 `bootstrap.py --check-only` 打印"跳过明细分类"（它现在只做依赖与编译器检查）。
至少 `先读测试说明.txt` 里已经写了这个边界，但自动化层面没有护栏。

### P3 · GUI 在本类沙箱永远跑不了，文档应写死"需要什么"
PySide6 6.10.3 在 `/tmp/se-venv` 装得上，但 `import PySide6.QtWidgets` → `libGL.so.1: cannot open shared object file`。
72 项 GUI 测试因此跳过（这是环境，不是产品问题）。`AGENTS.md` §3 已提醒"缺依赖可能导致跳过"，
但没说清 Linux 需要 `libgl1`/`libegl1`/`libxkbcommon` 等一组系统库；
建议在 `script_editor/先读测试说明.txt` 补一行"Linux 上跑 GUI 测试需要 apt install ... 或安装 Qt 运行库"。

### P3 · 仓库根有重复的 Mock 文件
`mock_server.py` 与 `mock_server (1).py` 字节数相同（197,303 B），`mxmain.dll` 与 `mx.exe` 同为 9,698,712 B
（STATUS 里已说明二者同摘要）。这类重复不伤功能，但会让"哪个是真源"变成考古。
`git ls-files` 里两份 mock 都在，建议保留一份并加说明（此事不在本轮范围，未动）。

### 观察（不是缺陷）：设计上刻意付出的代价
- **每次改一条也要整包复制**：`script.fls` 24 MB、`data.fls` 346 KB，新包必然同尺寸。
  对人工迭代没问题，但没法做"增量补丁/热更新"。
- **固定扩展长度不扩容**：正确恢复的 `4007` 回编超 49 字节仍被拒绝（README 反复强调）。
  这是安全换可用性的取舍；代价是"逻辑上更优的源码改法"可能无法入包。
- **pycdc 不在 Git**：纯克隆只能单引擎恢复；发行 ZIP 才有第二引擎。这会让新接手者误判工具能力。
- **硬链接发布在 Windows/非 NTFS 上未实测**（代码与文档都这么说）。
- **1288 一律排除**：这是项目决策（不重建敏感 dump），但会让"为什么少一条"反复被问。

---

## 7. 我对这个脚本编辑器的总评

**做得好的地方（读码 + 实测支撑）**：

1. **边界画得比功能多**：`policy.py` 一个集合、`guard_new_package` 一个入口、
   `verify_output` 一个终点。所有"不能做"都收敛在少数几个函数里，而不是散落成 40 个 if。
2. **不自我背书**：写包后的验证要从**新包**重新解出来再做逆变换，连 marshal 都要用精确版本
   Python 再读一遍——这条闭环是我见过同类工具里最严的。本轮实测 #2/#4 也证明了
   codec 与 writer 在真实包上是**字节透明**的（5,001/5,001 往返一致、空改动重写逐字节一致）。
3. **对"C 编译器/VM 的语义"有实物证据**：`tests/evidence/py27_dispatch.json` 钉 DLL SHA 与分发表字节，
   `native 66` 这种"历史笔记写错了"的点被单独纠正并写进 docstring。
4. **产品意识**：dev9 把"整包指纹登记"降级为缓存，直接消灭了用户每打一次包就要手动登记一次的痛点，
   而且没有放宽任何密码学/结构检查。

**最该改的三件事（如果继续做）**：

1. 修 P1 的哈希钉 + `decoding/README` 的事实错误（半天工作量，换来"测试全绿"这个信号可信）。
2. 修 P2 的两处过期 docstring 与 `_native` 私有导入（避免下一个 Agent 依据文档做错判断）。
3. 修 `test_bootstrap` 的伪模块写法（让无 GUI 依赖的机器也能绿，否则每次 CI 都要人工解释 4 条红）。

**不建议现在做的事**：扩容（放宽固定长度）、开放任意模块写回、把恢复稿自动提升为"可信源码"、
把 Linux 结果写进 Windows 验收。这几件在本仓库的语境里等于自杀式乐观。

## 8. 相关入口

- 工具本体：[`script_editor/README.md`](../../script_editor/README.md)（0.6.0.dev9 变更与边界）
- 设计/工作流：[`DESIGN.md`](../../script_editor/DESIGN.md)、[`M2_NATIVE_BUILD.md`](../../script_editor/M2_NATIVE_BUILD.md)、
  [`M3_WORKFLOW.md`](../../script_editor/M3_WORKFLOW.md)、[`M4_RUNTIME_DISTRIBUTION.md`](../../script_editor/M4_RUNTIME_DISTRIBUTION.md)
- 参数与登记：[`decoding/README.md`](../../script_editor/decoding/README.md)
- 双 VM 逆向结案：`notes/opcode_mapping_and_decompilation.md`、`notes/native_dlg_path_cipher.md`
- 当前状态：[`docs/STATUS.md`](../STATUS.md)
