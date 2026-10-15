# 项目当前状态（STATUS）

> **快照日期：2026-10-15**（Asia/Shanghai）。本文是唯一的“当前状态”文件：每轮工作结束时更新本文，不要再新建交接文档。
> 长期规则见 [`AGENTS.md`](../AGENTS.md)；项目总览见 [`README.md`](../README.md)；历史快照在 [`archive/`](archive/README.md)。
> 旧会话组件实测不代表本轮全部复跑。当前编辑器增强会话固定分支 `arena/51e31d38-mxsj-tw-2022`：会话起始基线 `fa1387162e60625c0a064403647abe8f65155acb`（PR #31），本期在安全修复 `9ee68e3` 上继续。功能代码 `f224f16`、类型缓存代际修复 `bf2bfc3` 已推送；未开 PR/合并/发布。此前阶段复跑两编辑器及其自检/静态检查；当前轮只复跑脚本编辑器，其它组件表格保留历史证据。本轮续增资源 0.4.1 路径下拉与 UI 0.8.1 包树右键导入，提交记录见本分支顶端；最新续修为资源0.4.3/UI0.8.3通用原生布局写入，当前范围见 §3.13 / §6；旧一次性助手被用户否决为最终方案。

> **本轮最新（2026-10-15）**：0.5.0.dev1补包内读取/恢复编辑、检查并人工采用、双VM原生新包/项目续编。用户已明确授权随工具交付固定原包解码参数；仅完整SHA匹配自动启用，其他版本不套用。171/171（31 GUI）实际通过，真实4007/data75编辑回包且5001/132未改，ruff/严格兼容0。正在制作独立源码＋双compiler＋授权参数测试包，未上传前不提供旧包；script固定长度/未知条目/Windows与客户端仍有限制，不宣称全面完成。详§3.27。

## 1. 分支与集成

| 项 | 值 |
|---|---|
| 工作分支 | `arena/51e31d38-mxsj-tw-2022`（当前会话，固定名称） |
| 基线 | 当前会话起始 `fa1387162e60625c0a064403647abe8f65155acb`（PR #31 合并提交）；安全修复后增加编辑器首期三项功能，代码至 `bf2bfc3` 已推送固定分支，未合并/发布 |
| `master` | 本地起始基线已含 PR #31 合并；未查询远程最新顶端。旧会话 `b04f999` / “编辑器尚未合入”声明已过期 |
| 最近 PR | 起始 HEAD 为 PR #31 合并提交；本轮未开 PR |
| 合并授权 | 无。合入 master / 发布生产需要用户当轮明确授权 |

## 2. 组件状态与实测

| 组件 | 版本/阶段 | 状态 | 本次实测 |
|---|---|---|---|
| 独立脚本编辑器（`script_editor/`） | 0.5.0.dev1源码候选 | 包内恢复编辑和双VM回编/项目续编，已授权附匹配参数 | 171/171（31 GUI）Linux/实际材料通过；正打包上传，未上传前旧0.4.1非新版。script固定长度/未知映射/Windows与客户端待验，详§3.27 |
| 逆向研究（`notes/`, `work/`） | 结案：双 VM opcode 表、0SLF 目录/路径哈希、`.dlg` 2,706/2,901、协议号表 412 条、帧续读 2 字节 | 稳定；未决项见 AGENTS §7 | 锁定输入 SHA 匹配 |
| 注册 UI 补丁（`tools/client_patches/`，历史） | v3.3 已作废 | 用户判定旧 overlay/整图烤字按钮/包外散图不符合原生规范，**勿再分发 v3/v3.2/v3.3**；新实现见下行 | 90/90 仅历史证据，不作为新实现验收依据 |
| 注册原生重做（`tools/registration/`） | phase2-diag1保持，布局写入转向通用编辑器修复 | 用户实测不再冻窗，但协议构造Exception后回首页，**协议→表单未通过原生验收**；不绕过协议、不改script/注册接口 | 本轮注册 **23/23**（真CPython2.5.6/静态PE/存储安全）；通用编辑器另见 §3.13，不能当作实机跳转已通过 |
| 只读复核链（catalog / API / web） | H/I/J 已收尾 | 可运行，只读 | catalog 34/34；review_api 27/27；验收套件 68 通过 + 2 跳过（需 uvicorn 在 PATH 上）；网页未装 node_modules 未跑 |
| 地图编辑器 | 一期 + PR #27 修复 + 10-14 补齐约定（`bootstrap.py`、`启动地图编辑器.bat`、`build_exe.bat`、ruff 0） | GIRB 300/429 扇区仍解不出（明确失败）；Windows EXE 未实机构建/冒烟 | **88/88** 通过（含 6 条 bootstrap 测试；GUI 冒烟在沙箱用 Qt offscreen + 桩 libGL 跑过）；ruff 0；wincompat 0/0 |
| 资源编辑器 | **0.4.3**：任意布局原生导入/替换，保留0.4.2后台清单与打开提速 | 用户已确认600MB打开速度修复有效；按路径明文/旧密文布局自动编码，不执行源码，未改条目不迁移 | 本轮 **118/118**；含新路径保存/重开/修改/再保存、旧错误密钥迁移、中文GBK路径、撤销/高级raw拒绝发布；ruff 0、wincompat 0/0/0、bootstrap自检通过 |
| UI 编辑器 | **0.8.3**：任意布局新增/再次保存统一原生路径密钥，保留0.8.2路径记忆 | 旧明文/错误key只读打开；明确保存当前布局才迁移，新包继续编辑；未改其它负载原样 | 本轮 **203通过 + 1语料库缺失跳过**（204）；独立原生回读、连续编辑与错误输出拒绝；ruff 0、wincompat 0/0/0、bootstrap自检通过 |
| 游戏服务端（`mxsj_server`） | 契约 v0.1 + 设计文档 | **无运行代码**；账号/网关/数据库/地图/战斗均未开始 | 架构测试 150 跑，**1 FAIL + 1 ERROR**（见 §3.1） |
| `mock_server.py` | 历史 Mock，协议号已按客户端修正 | 从未与真机联调；PR #25 顺带改的帧长度 3→2 未单独评审 | 未运行 |
| 文档 | 10-14 整理：AGENTS.md / STATUS.md / 归档目录；README 已刷新；新增 `docs/PYTHON_TOOL_CONVENTIONS.md`（工具开发约定） | — | 仓库内相对链接全部可解析（脚本校验） |
| 开发工具箱（`tools/devkit/`） | 0.1.0：`check_windows_compat.py` | 新增；全仓库扫描 1.3 s | **29/29** 通过；`ruff check tools/devkit` 0 报告；工具箱通过自己的规则 |

## 3. 红灯与已知问题

### 3.1 架构测试红：Agent E 证据的输入指纹过期（当前分支，真实回归）
- 现象：`server/tests/architecture` 中 `test_agent_e_map_npc.InputPinningTests.test_evidence_file_matches_regeneration` FAIL、`test_review_csv_export.RealBatchTests` setUpClass ERROR；`python3 server/tools/export_review_csv.py --check` 报 `E evidence changed; review required`。
- 根因：提交 `45d5590`（10-13，“修复 script.fls 残余条目的分段参数”）修改了 `tools/decompiler/batch_decompile.py`（+492/−10），而 `server/docs/csv_checks/agent_e_reproduction.json` 的 `inputs.shared_decoder.sha256` 钉的是旧值 `7490dbab…`，现值 `242543f8…`。
- 已核实：重新生成后与已提交证据**逐字段比对只有这一个哈希不同**，地图/NPC 分析结果零差异。
- 处置：**本轮未修**（用户选择单独处理）。修法：`python3 server/tools/map_npc_reproduction.py --out server/docs/csv_checks/agent_e_reproduction.json`，提交信息写明“仅 decoder 指纹变化，分析零 diff”，并附 diff 证据。

### 3.2 逆向结论内部矛盾：目录查找是线性还是有序
- `notes/fls_path_hash_and_dlg.md` §2 写明引擎对 0SLF 目录**线性扫描**（`0x48ECF0`）；资源/UI 编辑器 0.3.3/0.5.2 的 P0 修复依据是“引擎按有序目录寻址（含二分模拟），新条目追加到尾且 `r1=0` 会查不到”。
- 两者不能同时成立。修复同时改了排序与 `r1≠0`，真正起作用的可能只是 `r1≠0`（0 疑为哨兵）。需用反汇编回头判定，再统一文档与 docstring。

### 3.3 环境限制（不是缺陷）
- 沙箱无 `libGL.so.1` / `libEGL` / `libxkbcommon` / `libdbus-1`，也不能 `apt`。10-14 起的变通：用 gcc 生成只导出空符号的桩库放到 `LD_LIBRARY_PATH`（`libdbus-1.so.3` 需版本节点 `LIBDBUS_1_3`，`libxkbcommon.so.0` 需 `V_0.5.0`），再加 `QT_QPA_PLATFORM=offscreen`，PySide6 6.12 即可离屏开窗，三个编辑器的 GUI 测试组都能跑。桩库只在沙箱，**不入库**；它能证明「代码不会在导入/建窗时崩」，不能替代 Windows 实机。
- 沙箱 Python 没有 `libpython3.11.so`（Debian 未装 `libpython3.11`），PyInstaller 分析会直接退出；同样用一个空桩 `libpython3.11.so.1.0` 绕过即可完成 spec 干跑（产物不可运行，只验证 hiddenimports/datas）。GitHub release 资产域不可达，装不了 python-build-standalone。
- 复核验收套件原样执行文档中的 `python3 …` 启动命令，依赖必须装在该 `python3` 可见的位置。

### 3.4 仓库体积与许可
- 526 MB 跟踪文件中约 400 MB 是客户端二进制、CEF 运行时（根目录与 `exe/` 各一份）、OGG 音频、商业字体、游戏日志；`.git` 332 MB。
- 根目录没有 LICENSE；客户端材料的再分发权利不明。
- **用户决定本轮不动二进制**（本地 checkout 可能就是游戏目录，`git rm` 后 pull 会删文件）。后续若清理：先确认本地已备份，再只移除工具不依赖的部分（`music*/`、CEF、安装/更新器、未被证据引用的日志），保留 `mx.exe`/`mxmain.dll`/`exe/python27*.dll`/`data/*.fls`/`map/*.map`/`Fonts/`。

### 3.5 Python 工具约定（2026-10-14）与现状的差距
约定全文：[`PYTHON_TOOL_CONVENTIONS.md`](PYTHON_TOOL_CONVENTIONS.md)。下表为本次实测：ruff 0.17（各目录自己的 `pyproject.toml`，没有的用根 `ruff.toml`）；wincompat = `python3 tools/devkit/check_windows_compat.py <目录>`（E = ERROR，W = WARNING）。

| 工具 | ruff 报告 | GUI | 自检启动脚本 | 一键 EXE | wincompat | Windows 实机 |
|---|---|---|---|---|---|---|
| `resource_editor/` 0.3.3 | 0 | PySide6 | ✅ `bootstrap.py` + bat | ✅ `build_exe.bat` + `resource_editor.spec` + `run.py`（10-14；Linux 干跑通过） | 0 | 未验（bat / EXE 都没在 Windows 跑过） |
| `ui_editor/` 0.5.2 | 0 | PySide6 | ✅ `bootstrap.py` + bat | ✅ `build_exe.bat` + `ui_editor.spec` + `run.py`（10-14；Linux 干跑通过） | 0（沙箱语料库兜底路径加 `# win-ok`，缺目录只会 skipTest） | 未验（bat / EXE 都没在 Windows 跑过） |
| `map_editor/` 0.1.0 | **0**（10-14 清掉 74 条；只做定点修改，未整体 `ruff format`） | PySide6（可选） | ✅ `bootstrap.py` + `启动地图编辑器.bat`（10-14；强制 `--gui`，其余参数转发） | ✅ `build_exe.bat`（原 `build.bat`，改名并重写为纯 ASCII）+ spec（10-14 修 onedir 缺 `exclude_binaries` 的硬错误；Linux 干跑通过） | 0 | 未验（PR #25 遗留；bat / EXE 都没在 Windows 跑过） |
| `tools/client_patches/` | 328（E501 268） | CLI | — | — | 7 W + 2 INFO（Py 2.5 片段按设计不可解析） | v3.3 已作废（2026-10-14），待还原+原生重做 |
| `tools/data_browser/desktop_app.py` | 37 | **tkinter** | ❌ | ❌ | 3 E（CONV001） | — |
| `work/.../tools/map_gui.py` | （目录合计 585） | **tkinter** | ❌ | ❌ | 2 E（CONV001）+ 3 W | 历史工具 |
| `tools/data-parser/`、`tools/dis_v43/`、`tools/decompiler/*.py` | 82 / 28 / 239 | CLI | — | — | 0 / 0 / 3 W | — |
| `server/`（src / tools / tests / apps） | 124 / 1423 / 291 / 54 | — | — | — | 10 E（验收脚本 `os.killpg`/`SIGKILL`，Linux 侧按设计）+ 93 W | 不交付 Windows |
| `mock_server.py` | 228 | — | — | — | 1 W | — |

本轮已修的「Windows 必坏」项：`work/.../co_code_analysis/bytecode_58_<module>.bin` 改名为 `bytecode_58_module.bin`（`<` `>` 是 Windows 非法文件名字符，Windows 上 checkout 该文件会报 `invalid path`；`crack_table_b.py` 的引用同步改）；新增 `.gitattributes` 强制 `*.bat`/`*.cmd` CRLF 并重归一化 5 个 bat；`map_editor/build.bat` 补 `chcp 65001`。
补齐顺序：① `map_editor` 加 `bootstrap.py` + 启动 bat，修 ruff 74 条 —— **10-14 已做**；② `resource_editor` / `ui_editor` 各加 `build_exe.bat` + spec —— **10-14 已做**（三个 `build_exe.bat` 同一模板：`py -3`/`python` 探测 → `.venv` → `requirements-dev.txt` → `unittest`（`PYTHONPATH=src`、`QT_QPA_PLATFORM=offscreen`）→ `python -m PyInstaller --noconfirm --clean <tool>.spec`）；③ 三个编辑器在 Windows 实机按 CONVENTIONS §5.3 冒烟并回填 §2 —— **待用户**：双击 3 个启动 bat、3 个 `build_exe.bat`、3 个 EXE，任一失败把 `启动日志.txt` / 控制台输出贴回来；④ 两个 tkinter 工具只保留不改，有需求时用 PySide6 重写。

### 3.6 两个编辑器定向审查（2026-10-14，当前检出 fa13871）

首次审查仅复现，以下缺陷现已在 0.7.1 / 0.3.8 修复。所有破坏性复现使用仓库外临时合成包，未改真实资源。

**修复复核**：UI 写包拒绝源包/别名及挂载资源目录其他包，独占临时副本经布局、新图及未改条目逐字节校验后原子发布；任一步失败清理临时文件、源包与旧输出不动。资源保存同样仅输出新包；导出保护当前/历史源包、工作区其他包、硬/软链接，并约束目录边界、多帧目标预检。资源真名缓存保存后重建，导入路径按 entry_id 保留于会话，网格类型/缩略图/选择也在排序后按条目身份重建；发布前失败恢复写前顺序，旧下标与用户编辑不受排序影响。Qt 缺失时批量测试正常收集。额外定位原有 UI 剪贴板测试在解释器退出时 SIGSEGV（基线也复现）：仅在测试 tearDown 清理该组创建的 QMimeData 后，完整测试正常退出；产品不清空用户剪贴板。

- **高优先级：UI 写包输出硬链接可截空源包。** `ui_editor/src/ui_editor/core/pack_build.py:470–497` 只用 `resolve()` 判断同文件，不能识别硬链接；不同路径硬链接进入 `open(out, "wb")`，先截断同一个 inode。复现：185 B 合成源包经硬链接输出后变 0 B，随后报魔数错误。GUI 覆盖提示也只比 `Path`，不能兜住别名。另有显式原位覆盖分支，先改包后校验且无自动备份/回滚，与原包保护规则冲突。应拒绝源资源及其别名，先临时文件校验，再发布新包。
- **高优先级：资源批量导出未保护源包/别名。** `resource_editor/src/resource_editor/core/services/exporter.py:137–172` 仅做路径分段清洗与本批次重名去重，没有目标与源资源的 samefile 检查。复现：条目真名与源包名重合，选源包所在目录导出，42 B 合成源包被覆盖为 10 B 条目负载，仍返回 `entries=1, files=1, failed=[]`。同类缺口还需覆盖已有符号链接/硬链接与导出目录逃逸保护。
- **数据关联缺陷：资源保存后真名缓存错位。** `resource_editor/src/resource_editor/core/model/document.py:363–371` 重建槽位时没有清掉/重建 `_names`，并丢弃新增槽位的 `path_name`；新增一个排序靠前的条目后保存，旧真名缓存仍按旧下标使用。合成三条目复现：新条目 NEW 标成旧 B 的名，B 标成 A 的名，A 丢名；负载仍正确，但真名搜索/导出可能误标。应按 entry_id 保留导入路径并重建名称映射，补「命名→新增低哈希→保存→再次导出」回归。
- 实测：两目录 ruff 均 0；Windows 静态检查均 0 ERROR/0 WARNING。UI 不依赖 Qt 的选定 8 个测试文件共 46 项，45 通过、1 因缺少完整 dlg 语料库跳过；完整发现运行 50 项但有 23 ERROR（包含 setUpClass 错误），均受缺 `libGL.so.1` 阻塞，不能算完整通过。资源完整发现运行 41 项：36 通过、4 跳过、1 ERROR；错误为 `test_batch_ops.py` Qt 导入失败后返回类型注解引用未定义的 `EntryGridPanel`，导致整文件不能收集，包含其中非 GUI 测试。未造系统库桩件，未运行 Windows/真实 interface.fls/游戏原生验收。

### 3.7 编辑器首期增强（2026-10-14，用户「好，开工」授权）

**已实现并离线回归**：资源 0.4.0、UI 0.8.0；代码 `f224f16` + 类型缓存修复 `bf2bfc3` 已推送当前固定分支。此前 0.3.8 / 0.7.1 的源保护、独占临时构建、发布前校验、原子新包发布契约不变。

- 资源：每包独立全局增量时间线，替换/还原/增删/帧图导入可撤销重做，多选/按路径批量导入的成功项算一步；空操作不记步，新编辑截断重做。稳定槽位与相邻对象定位不依赖旧下标，构建排序/保存失败之后仍可撤销。50 步/64 MiB 增量预算、超大单步保留一条（不是总进程内存上限）。成功保存清历史并建立新基线，取消/失败不提前清历史；旧 `undo(index)` 参数只兼容签名，现在按文档最近一步撤销。
- 资源 GUI：Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z、只读时间线、当前选择按条目身份恢复、增删计数与缓存重建；编辑框保留文字撤销，只读预览不拦文档撤销。阻塞保存禁编辑/切包；后台预览完成不能误解锁保存。GUI 预览与 core 类型缓存均带代际，编辑/撤销后旧结果不回灌；类型嗅探旧结果回灌先由新回归复现失败，再修复为带代际缓存。
- UI：改名在属性写入之前查静态引用、列模块/entry/类/方法/位置锚点/代码皮肤并默认取消；添加属性覆盖也走同一入口，核心名字字段不能移除。重复/非字符串的新名字拒绝；删除枚举全部后代并继续尊重子树锁定。确认只改布局，不改脚本/索引、不自动接线。
- UI 诊断：零 Qt 只读核心，资源存在性注入；重复名、尺寸/坐标类型、负/零尺寸、父矩形越界、挂载来源缺资源、待入包资源、目标字段编码、静态索引缺控件。按树路径定位，过期结果暂停定位；警告可本次标有意设计，但不写 `.dlg`、不隐藏保存检查、不能隐藏编码错误。零尺寸可能是自动尺寸，越界可能是滚动/重叠，缺资源可能是未挂载/热更新，静态未命中不代表无动态引用。
- 保存清单：资源列真实新增/修改/删除、身份/缓存真名/存储大小，不为认名读取未改负载；UI 列相对最近成功保存基线的树位置字段差异、旧/新值、控件增删、图片新增/替换/未引用跳过与全部诊断。散装不嵌入图；失败/取消保关联/基线/挂账，成功才重设基线。UI 保留撤销历史，撤销/重做至保存基线可恢复干净；`1`/`True` 这类 Python 等值但序列化不同的未知字段也正确列差异和标脏。Big5/GBK 编码错误在 GUI 清单与程序化窗口写回前拒绝，不自动简繁转换，不把兼容回退当引擎支持。

**实测证据**：新增 67 条回归（UI 33、资源 34）。使用 `git archive 9ee68e3` 的仓库外只读基线，资源新增撤销、引用改名取消两条同一探针旧版均 FAIL，本版均 PASS；另补类型缓存旧嗅探回灌与等值类型脏标记的先失败后修复回归。完整进程结果：UI 170 项（169 通过、1 缺全量 dlg 语料库跳过）、资源 97/97，均退出 0；Python 3.11.2 / PySide6 6.8.3 / Pillow 12.3，GUI 仅沙箱 offscreen + 系统库桩件，桩件不入库不交付。无桩件资源 97 项（74 通过、23 GUI 跳过）；UI 无 Qt 12 模块 92 项（91 通过、1 语料库跳过），额外确认测试过程没有 import PySide6。两目录 ruff、Windows 静态检查均 0；bootstrap `--check-only` 均通过；`git diff --check` 通过，锁定 script.fls/key DB SHA 与 AGENTS 完全一致。

**未验/不扩范围**：Windows EXE/桌面快捷键手感、真实完整 `interface.fls`、游戏加载/点击与动态脚本均未验；没有实现自动接线、消息号规划、脚本源码编辑/编译写回、九宫格或包外项目文件。0.8.1 已补成功保存新包后的解析器优先重挂/缓存失效与树挂载，合成布局重开验证通过；真实新图显示仍待实机。诊断只说当前挂载来源未找到，不将其当新包缺失。合成 data.fls（含目录条目）保存后槽位数量、元数据与历史重基线已补专项回归，不外推真实大包/Windows 线程交互验收。未动真实客户端资源、架构证据红灯或注册/服务端代码；未构建 EXE/上传测试包/合并/发布。

### 3.8 两项导入交互（本轮：资源 0.4.1 / UI 0.8.1）

- **授权范围**：资源按路径导入改可搜索/可手填下拉；UI 资源树包根右键
  导入本地 `.dlg` 到完整包内路径。只生成新包，不自动带图片或接脚本。
- **资源**：普通/多选 0SLF 路径导入与帧图转精灵共用 editable QComboBox /
  contains、忽略大小写 QCompleter。候选只取当前槽位真名，剔除目录/无名/
  已删条目；新增/撤销后重新选择即更新。已有地址默认 No；严格相对 GBK
  路径校验，不把本地硬盘地址当游戏地址。FLSDATA 文件名导入行为不变。
- **UI**：无已识别布局的 0SLF 包也入树；导入经过受限解析、Big5 显示文本/
  GBK 资源字段检查，目标是非布局资源则拒绝。取消/错误不切文档；替换和
  丢弃未保存文档都确认。导入后是单文档「待入新包」叶子，可预览/编辑，
  切换/放弃清叶子，保存失败保留内容/历史/待入标记，非多文档队列。
- **核心写包**：`allow_create=True` 显式启用缺失布局新增；默认仍拒绝缺条目。
  新增明文（零 XOR 密钥，与资源编辑器一致），已有布局沿原密钥替换。
  有序目录/非零种子、病态回退重组、独立负载比对与布局读回后才原子发布。
  GUI 校验总数和编号集合计入新增布局；不覆盖原包/别名或其它挂载源包。
- **状态迁移**：成功才清待入标记、优先挂载新包及登记本会话自定义路径；
  树读取严格锁定用户点中的包，不按同名跨包顺序冒取。0SLF 不存全名，
  重启无法自动恢复所有未知路径。连续导入先保存，再在生成的新包节点导入下一份。
- **本轮实测**：新增 30 条回归（资源 7 / UI 23）。完整离屏资源 104/104、
  UI 193 项（192 通过/1 缺完整语料库跳过），退出 0；Python 3.11.2 /
  PySide6 6.8.3 / Pillow 12.3，GL/EGL/xkb/dbus 桩仅在仓库外用于 offscreen。
  无桩件资源 77 通过/27 GUI 跳过；选列 12 个 UI 核心模块 100 通过/1 跳过，
  断言未 import PySide6。两工具 ruff、Windows 静态检查 0/0/0、bootstrap
  `--check-only` 绿；锁定 script.fls/key DB SHA-256 均不变。
- **仍未验**：新增明文布局的客户端原生加载、完整布局语料、Windows 桌面
  快捷键/EXE 与真实大包。工具读回通过不等于游戏验收。已按用户本轮授权上传两个工具源码启动包（见下方交付记录）；未构建 EXE、
  上传客户端测试包、开 PR、合并或发布；未改架构证据、注册/服务端代码及原始客户端包。

### 3.9 工具源码包交付（本轮用户授权 Google Drive 上传）

- 源码提交 **`fe2e057a3783bf595db5bce0320660b279d6d472`**；两个 ZIP 均只含
  对应工具的已跟踪文件、启动/EXE 构建脚本、数据字典/静态索引、测试、文档、
  `交付说明.txt` 和逐文件 SHA-256 清单。不是 Windows EXE，不附客户端包、
  Python/依赖安装包、缓存或沙箱系统库桩；需 Python 3.10+ 和联网安装依赖。
- 打包前工具副本逐文件字节比对通过；ZIP CRC 与全文件读回比对通过。
  在无客户端数据的交付副本复跑：资源 **97 通过 + 7 数据缺失跳过**（104 项），
  UI **191 通过 + 2 数据/语料缺失跳过**（193 项）；均退出 0，Qt offscreen +
  仓库外系统库桩。交付副本 ruff 与 bootstrap 自检通过；不外推 Windows/游戏验收。
- 已上传用户 My Drive 根目录；上传返回和再次读取的**文件大小/MD5 均与本地一致**，
  两个最终文件未在垃圾桶，未更改分享权限。UI 交付说明补准“启动仅自动安装 PySide6，
  转精灵另需 Pillow”，更正前本轮刚上传的 UI 副本已移垃圾桶（非永久删除）；工具代码未改。

| 工具 / 文件 | Google Drive | 大小 / MD5 / SHA-256 |
|---|---|---|
| 资源 0.4.1 · `resource_editor_0.4.1_source_20261014_fe2e057.zip` | [下载](https://drive.google.com/file/d/1D-zDVh5rfpfxcTw5J1AGqDaJdlA-S2zi/view) | 159,089 B；MD5 `622b700479431736d62202ae2bbe555c`；SHA-256 `fcf7f84a68d5ff2a21c20df2c75e778cd301aa1c2b9aea47b9414bc02b8e90b1` |
| UI 0.8.1 · `ui_editor_0.8.1_source_20261014_fe2e057.zip` | [下载](https://drive.google.com/file/d/13Os-8wj-R86AHnvXWNubkrDFhG47NBV7/view) | 383,390 B；MD5 `69a9539af9cefeb090afe0d4a3d7c23a`；SHA-256 `d708608f204b25383579119aa473f1fe0410543a45c75d8eff6a05917352fa27` |

### 3.10 用户反馈修复：重开找不到布局 / 大包打开变慢

- **用户实测更新**：用户确认当时填写 `login/regform.dlg`；约 600 MB 包在双击
  文件名的打开读条阶段很慢。更新后用户本轮明确反馈“速度很快，新布局也找到了”。
  两项交互问题按该测试环境通过；未拿到实际包字节，不外推所有写回/游戏加载或 EXE 验收。
- **已确认的代码缺口**：0.8.1 只存本会话路径，重启未知地址不参与扫描；
  资源打开阻塞任务会先嗅探全条目、读布局引用，然后才显示网格。
- **UI 0.8.2**：保存/精确回读成功才把合法 .dlg 地址存入 QSettings；新实例
  按每个包实际编号相交显示，不改包格式、不增加包外项目文件。包根“按包内
  路径打开布局…”只读检查旧新包，成功才入树/记忆；失败/取消不挂幽灵节点。
  已知 `login/regform.dlg` / `login/regterms.dlg` 同步两工具字典。basename
  与完整地址不等同，不会猜路径/自动重命名。新回归有另一个进程读设置证明。
- **资源 0.4.2**：阻塞阶段只建索引/快速匹配字典；完整类型和布局引用后台补。
  “待识别”不假报二进制；每包最多一任务，发布检查文档/代际/归档，过期拒绝
  并重排；保留页码/多选。label/搜索只匹配目录，不隐式读全部布局；显式目录
  导出仍补全引用真名。读/关闭互斥，防旧后台工作读取被复用的文件描述符。
- **本轮回归**：资源 110/110、UI 197 项（196 通过/1 缺完整语料跳过），
  Linux / Python 3.11.2 / PySide6 6.8.3 / Qt offscreen + 仓库外系统库桩，
  进程退出 0；ruff/wincompat 0/0/0，bootstrap 自检通过，锁定原包/key SHA
  均不变。未在 Windows/用户的 interface.fls 量耗时，不能宣称实际卡顿已消失。
- **交付完成**：修复代码 `f6e6e2a` 已推送，两个源码启动 ZIP（非 EXE）已上传
  My Drive 根目录。交付副本资源 103 通过/7 数据跳过、UI 195 通过/2 数据或
  语料跳过，退出 0；ruff/ZIP CRC/逐文件字节与清单校验通过。上传返回大小/
  MD5 与本地一致，不附资源/缓存/系统库桩，不改分享权限、不删除旧版。
  旧 0.4.1/0.8.1 包不是此次修复版。
  - [资源 0.4.2 下载](https://drive.google.com/file/d/16OCdL0m6ajPxPTbk6eWy3qUqyX2RU7Ny/view)：
    `resource_editor_0.4.2_source_20261014_f6e6e2a.zip`，162,019 B，
    MD5 `0248ce26fc493fce58f10b9c6e5f57a1`，
    SHA-256 `9f26b885fbae1f665925c89763de7172adcb4318c259d7edb078b9f5690c6cef`。
  - [UI 0.8.2 下载](https://drive.google.com/file/d/12iJrtHBbr9MqZYRwmn2XP4cKVP7j1VNg/view)：
    `ui_editor_0.8.2_source_20261014_f6e6e2a.zip`，386,673 B，
    MD5 `c77378c806978420f3f4bb09d5a3f9c6`，
    SHA-256 `3ce6d781d3bd9e965905440892022c6783d12abe537b2fcd46fa0505fbc8893d`。

### 3.11 注册第二期点击“申请会员”卡屏（用户新反馈，待定位）

- 用户已确认编辑器打开速度/新布局查找修复有效；进一步确认：游戏使用网盘
  registration_phase2.zip 的 script，两张新布局在同一个 fls 都能找到；卡屏是
  **整个窗口冻住、无响应**，不是仅“首页隐藏/空屏”。这些前提不再重复询问。
  未取得该用户包字节/原生阶段日志，能找到路径仍不等于加载成功。
- 已找到自写源码 `tools/registration/register.py`（entry 4007），入口打包器
  `build_native_registration.py`（entry 337 的 9 字节条件补丁），已发第二期
  script SHA-256 `17a94c77e4cda673023f0e17221edb73f789183a0af0d4fcd5c6a1d3b651e0b2`。
- 实际流程：`Show(True)` → `Step(0)` → `CRegTermsPanel` 先加载
  **login/regterms.dlg** / 取 loc_msg / 创建原生 COutput；同意后才加载
  login/regform.dlg / 四编辑框和五账号勾选。只确认 regform 可查不够，必须
  同一个实际安装的 interface.fls 同时含两张；在原包上分别保存的两个副本不算。
- 只读解密/解析原始 entry 337 的 code object 并正规化反汇编确认：
  CMainPage.OnMessage 的 pc 215/218/221 为 Show(False)，225/228/231/234
  才调用 register.Show(True)。已有补丁仅改 pc 102..110，不改变这个先后。
  原第二期自写 Show/Step 未捕获构造异常；因此“先隐藏首页、布局构造失败后看似卡屏”
  是有代码依据的**候选解释**，不是已证实的本次根因，更不能排除原生加载阻塞。
- 现有 register_diag.txt 主要覆盖表单消息/提交，没有覆盖入口和条款构造。
  若日志不存在或未新增，不能拿它证明注册模块没执行。
- **本轮新增 phase2-diag1**：自写 register.py 在首次模块/依赖导入、InputSecrecy、
  Step、条款布局、loc_msg/尺寸、COutput 构造/定位/游标/排版/滚动及表单阶段
  各写 begin/ready，每条关文件；photo 不可写时尝试工作目录 register_diag.txt。
  仅阶段/尺寸/异常类型，无账号/密码/邮箱/异常文本。初次构造抛 Python 异常
  时尝试解除输入保密并恢复首页；切页失败保留旧全局引用。没有中断原生同步
  调用的能力，**没有复现/证实修复用户的整窗卡死**；原生函数不返回时 except 无效。
- 只读反汇编原 code object：579/CCombPanel.__init__ 和 4832/COutput.__init__
  均含 MessageProcess，所以“layout begin”或“output create begin”不只定位到
  文件读取/文本构造，也含消息处理。COutput 将行宽设为 w-20；防御性拒绝非正
  行宽/高度，但没有证据表明用户实际控件尺寸异常。不改引擎/布局/目录 f1/XOR。
- 重建真 CPython **2.5.6**，14/14 离线回归通过（无 skip），ruff、Windows 静态
  检查均 0。新增同一故障探针：旧自写源码在模拟 regterms 构造异常时抛出、
  新版回退；另测阶段顺序/文本初始化异常/旧引用保留/日志写失败与备用路径。
  这只证实自写错误处理，不是假装复现真实引擎无响应；未执行任何原游戏代码。
- 已构建仓库外新包 `/home/user/registration-phase2-diag1-build/script.fls`，
  24,263,562 B，SHA-256 `7cf8d5c4b2cfbf6b8e241f0088df5542c5c000ef438244d590a487db0d52d274`。
  原包仅337/4007变；337仍原9字节补丁。用旧自写源码重建出的全包 SHA 与已发
  第二期 `17a94c...` 完全相同，再逐条比较：**相对用户第二期仅4007变，其余
  5001条压缩负载相等**。新包 marshal 精确读回及真2.5.6桩冒烟通过。
- 测试/说明 `tools/registration/DIAGNOSTIC_TESTING.md`。用户只须在测试副本
  备份并替换 script，不重导或覆盖 interface；若再冻住只取新日志最后30行。
  下一步必须取实际最后阶段，再决定检查资源字节/原生排版/消息处理；不能直接
  宣称卡屏已解决。诊断包随后按用户本轮“你传网盘”授权上传；未改权限，原包/key DB SHA 均未改变。
- 诊断包源码提交 `e3c288e631211f59631e89d68b6e09440d077dfe`，本地交付
  `/home/user/registration-phase2-diag1-delivery/registration_phase2_diag1.zip`，
  **24,190,013 B**，ZIP SHA-256
  `ac8b9db8c17f7e39025fd81994c6e76c9e1111427442642829caed1b7356cd6d`，
  MD5 `c82f585455b720a991c237a3e7877a97`。仅 data/script.fls、诊断测试说明、
  源码/构建证据 manifest、SHA256SUMS 四文件，无 interface/编译器/key DB/桩件。
  CRC、逐文件解包相等、包内 script SHA 核验通过；先以会话附件呈现，随后按用户明确授权上传 Drive。
  不重新分发旧二期包，不把此次诊断交付记成原生卡屏已解决。
- **网盘交付已完成**：[registration_phase2_diag1.zip](https://drive.google.com/file/d/1YxoYNmpTejl7qk86K9ELg_b1bvYJcGk8/view)，My Drive 根目录。上传返回大小 24,190,013 B、MD5 `c82f585455b720a991c237a3e7877a97` 与本地一致；未再次下载核验，未改分享权限/删除旧包。

### 3.12 diag1 实机返回条款构造异常；原生路径 XOR 与存储修复助手

> 本节为此前助手阶段记录，用户随后拒绝其作为最终解决方案；已由 §3.13 通用编辑器修复接续，勿再催助手交付。

- 用户本轮提供完整入口日志：模块导入、InputSecrecy 都 ready；
  `step=0 begin` → `terms layout begin` → `step=0 EXC type=Exception` →
  recovery secrecy/home ready。用户明确“不再卡屏，现在点了没反应、不跳协议页”。
  **diag1 回退按此测试环境奏效，注册协议/表单未通过**。已确认这次异常在
  CCombPanel 构造期间、条款文本/loc_msg 初始化之前，不能凭类型确认具体内部行。
- 深追真实 C_sys.LoadFile PyMethodDef：字符串0x6B4038、方法表0x7DB2F0、函数
  **0x45D580**；旧笔记0x461340实际为 **ReadFls**，不能当同一加载器。
  静态追到0x60E080/0x454860路径哈希、0x60E153的
  `key=((hash+0x9234AB)&0xffffffff)^0x937F4912`，0x609C80读包后逐DWORD XOR。
  regterms key字节 `a9bd00b5`、regform `f94b3e60`。不是明文头自解密、也不是
  目录f1密钥。证据 notes/native_dlg_path_cipher.md；原PE哈希/调用位移/指令签名
  新回归钉住，只读字节/反汇编，不执行/模拟执行原游戏代码。
- **确定的旧写入缺陷**：注册说明让资源工具原样导入明文，UI 缺地址新增也为
  明文/零密钥；编辑器回读能解析但原生路径XOR后不再是布局。这与日志吻合；
  尚未取到用户实际存储字节，故实际两条状态/这是否唯一故障仍待助手报告。
  不再把“明文新增实机待验”说成已知可兼容原生；旧笔记明确加更正横幅。
- 新 `tools/registration/repair_interface_layouts.py` 是**标准库一次性CLI助手**，
  非新GUI/EXE、不改游戏脚本、不启动游戏。拖测试副本当前interface到同目录
  `修复注册布局存储.bat`，需要已有Python3.10+，无需PySide等第三方依赖。
  检查两条当前存储：原生密文则不动；明文/已知头反推可解则保留用户全部明文字节
  按路径密钥重加密。只出新包、不取仓库模板、不改目录/其余负载、逐字全文件比对
  后原子独占发布，输入/别名/已存在输出拒绝；缺地址/非法字面量/重叠/无序则拒绝。
  两条均正确则NO OUTPUT，应另查失败点；不盲目补布局/不要求上传600MB。
- 新包通常为 `interface_native_fixed.fls`；diag1 script保持不变。操作说明
  `tools/registration/NATIVE_STORAGE_REPAIR.md`。Windows BAT/NTFS发布/用户实际
  新包和原生跳转尚未验；FAT等不支持硬链接会安全拒绝，不降级覆盖。
- 新回归9项，本轮总 **23/23**（含真2.5.6自写脚本回归，无skip），ruff 0。
  原策略合成探针：明文按真实路径key解密无法还原头，本版密文精确回读原字节。
  覆盖用户编辑保留、跨1MiB块整包等值、旧错误密钥/混合状态、已正确无输出、
  输入/硬软链接/既有输出保护、非法数据、验证失败与发布竞争安全清理。
  这是确定存储缺陷的离线复现/修正，**不是用户条款已实机出现**。
- 没有直接改两编辑器执行管线/发新编辑器版；只在UI pack_build文档标记旧
  明文/零密钥新增不兼容。通用新路径加密与按原生key验证是后续必要修正；
  已正确加密的现有路径再由UI沿原密钥写仍可保留该形式，但游戏仍需回读验证。
  原包/key DB/两张模板均不改，不改337/4007，不写真实注册接口。
- 修复助手源码提交 `ec6511d912d3ddb9c2d588588ab5371f61ca301e` 已推送。
  仓库外 ZIP `/home/user/registration-layout-storage-fix-delivery/registration_layout_storage_fix.zip`
  12,855 B，MD5 `a93a452ffd09504d5c965935bb253875`，SHA-256
  `37b1efee63edd9337f799fc7cc0c4db2ac2b84d08c88a21af7f918faeb7591fa`。
  六文件仅助手/BAT/说明/静态依据/manifest/校验和，无FLS/模板/key DB/编译器。
  CRC/源码字节/解包读回/交付副本ruff、合成包独立CLI执行及既有输出拒绝通过；
  Windows静态检查0/0。此时本地打包完成、未上传，须按现有发布约束获本轮上传授权。


### 3.13 用户拒绝一次性助手：两个编辑器通用原生写入/持续编辑

**需求纠正**：用户布局还在调整，不接受只修regterms/regform存储的助手作为最终方案。
本轮修两个编辑器正常新增/导入→保存新包→重开→再编辑→再次保存流程，不导模板覆盖用户改动。

- 原生密钥为 `((entry_id + 0x009234AB) & 0xffffffff) ^ 0x937F4912` 的小端重复XOR。
  新增/替换目标都用路径编号派生；历史头反推只作输入兼容，不再用于发布正确性判断。
- 两包各自包含相同零Qt `core/native_layout.py`；严格GBK相对路径、字面量AST、不执行源码、
  保留明文混合字节。opaque只看前缀，正常非布局文本/图片不自动编码。
- UI0.8.3：普通/新条目/重组回退都原生编码；发布前严格原生回读、未改负载逐字比对。
  已原生输入不双重加密；附加图片接口拒绝.dlg绕过。没改字段也可保存当前布局迁移。
- 资源0.4.3：按路径新增/替换统一编码；内容替换识别新/旧布局。高级raw保持原字节契约，
  但改动已识别布局保存必须原生回读；原路径记录或源布局提示不会被损坏新头降级绕过。
  原包保护、原子输出、撤销/重做、原未改负载保持；旧头提示仅读4KB，不拖回打开全扫描。
- 先复现旧工具新增：独立公式探针 RESOURCE OLD FAIL/UI OLD FAIL；修后同探针两PASS。
  不是只把3个旧明文/沿任意key期望改掉：另加两个工具连续流程、任意future路径、
  中文GBK/大小写/斜杠、旧明文/错误key、native输入、opaque、失败源/既有输出不动等回归。
- 实跑资源118/118，UI204（203通过+1缺语料库跳过），注册23/23含真2.5.6；
  ruff 0、wincompat0E/0W/0I、自检通过。Qt用仓库外桩+Linux offscreen，非Windows实机。
- 当前操作见 [正常编辑流程](../tools/registration/EDITORS_NATIVE_LAYOUT_WORKFLOW.md)。
  原生注册协议→同意→表单仍待用户测最新输出，不能宣称唯一根因或游戏已全修好。
- 源码ZIP已在仓库外完成CRC/源码manifest核验和解包复跑：资源118项（缺原包7跳过）、UI204项（缺原包/语料库2跳过），无失败。包不含原FLS、Qt桩、编译器或模板；代码提交 `e46e94b` 已推送固定分支，不开PR/合并。
- 本轮询问后用户明确选择“上传两个新版包”，已上传My Drive根目录，未改权限：
  [资源0.4.3源码ZIP](https://drive.google.com/file/d/1GdGFrRPA_e-QvnKsq5w55zahPdSbahxW/view)，
  169,742B，MD5 `76003d580acc6c2b67da04c5c35d9d45`，SHA256 `350f5175fa32bd1d95ce90cf76f7889be734f42d5200680d4debb9e8e2cdf99c`；
  [UI0.8.3源码ZIP](https://drive.google.com/file/d/1S9_89VFYdUWosXrZhAQK419yu9IfGDRu/view)，
  396,808B，MD5 `ff9d71b2d0acd2087bfe7960fa7291e8`，SHA256 `21a6784eda15170bd638caac255aae472da50c094a4e246119400f73dfd777b7`。
  上传返回大小/MD5均与本地一致；未再次下载、未删除旧包，不冒充已构建EXE或实机验收。

### 3.14 2026-10-15 协议已显示，同意进入账号框构造后AttributeError

- 新实机事实：协议可进入；`terms msgid=1`→`step=1 begin`→`form layout ready`
  →`form import C_object ready`→`form account begin`→`AttributeError`。
  用户确认目标控件是account/CBox，不能继续让用户重命名正确控件/重导布局。
- 不能只凭异常类型认定缺哪项；原日志把CEDIT属性、FONT_EDIT属性、原生工厂内部与
  SetLimit并在一段。新增phase2-diag2只分割这条调用链，保留原生接口/参数/协议回退。
  严格代码元数据日志最多12帧；缺失属性名仅在静态co_names中且是ASCII标识符才输出，
  不打印异常值/repr/局部变量/账号资料。字段布局不改，不加字体/控件替代fallback。
- 原始code object只读核对entry3564 CreateEdit别名/7形参/9参数子类构造、entry3854
  CEdit.SetLimit确实存在。测试桩由假cls(name)改为9参数边界；没有执行恢复游戏代码。
- 真2.5.6回归26/26（含6种定位/隐私/旧协议引用保留探针）、ruff0、wincompat0/0/0。
  原diag1源对新的精确定位探针先失败。新包marshal逐字回读及读回模块桩冒烟通过，
  相比按旧源码重建的diag1仅4007压缩负载改变，另外5001条全等。
- 仓库外 `/home/user/registration-phase2-diag2-delivery/data/script.fls`，
  SHA256 `4022b90e3568248317a8c6799c4fc8e61f641a538668616d7b7d51f345f39f09`。
  是诊断版，实际缺失属性及表单显示尚未解决/验收；代码 `839c0c4` 已推送。
  用户本轮明确选择上传，已上传 [registration_phase2_diag2.zip](https://drive.google.com/file/d/1ELUEuF4mGD_4AE4EiYMF5K6wgYDDIYDc/view) 到My Drive根目录；
  返回大小/MD5与本地一致，未改权限/删除旧包，未再次下载核验。
  ZIP `registration_phase2_diag2.zip`，24,201,007B，MD5 `611eab945260ee28628703aa6caf0c29`，
  SHA256 `4ee6b9c8aa2e840527bc3075ae94e3cef56aa19de2df0fd0dd592cd02ae88b78`；
  ZIP CRC/逐文件回读通过，未含模板或interface.fls。

### 3.15 2026-10-15 FONT_EDIT实机确认缺失，按原生注册字体修复

- 用户diag2输出：account anchor/factory ready，font resolve begin后AttributeError，
  `missing_attribute=FONT_EDIT`。实际缺陷为脚本依赖本客户端不存在的旧别名，不是布局。
- 原entry4007 `CRegPanel2/CreateEdits` pc18/21的LOAD_GLOBAL interface/LOAD_ATTR FontLT14_3
  已只读核对；协议正文也实机使用该字体成功。四框/提示区统一明确选该原生字体，
  提示区使用黑色0与当前四框一致，不依赖COLOR_EDIT，不注入别名或fallback。
- 默认离线桩移除以前假设存在的FONT_EDIT/COLOR_EDIT。旧diag2对“缺旧别名仍进表单”
  同探针先失败，新代码通过，测试同时检查四框与提示字体/颜色、旧别名即使存在也不用。
- 真2.5.6 32/32；ruff/wincompat通过。保留diag2元数据保护、分段标记，新增font1版本标记。
  新包与实际已发diag2的精确重建（SHA匹配）只4007变，其余5001条压缩负载全等。
- 本轮构建曾被完整marshal比对拦下：旧修复转译器在边界附近把新代码有效LOAD_FAST猜成
  STORE_NAME（新源解密原生字节实际精确匹配输入）。没有放宽断言/改key DB；新增零执行
  authored_marshal用于已知自写载荷：严格源混淆字节+zero padding比对，拒绝修tag/长度/边界，
  逐co_code确定逆映射后完整标准marshal逐字匹配，再运行新包读回模块桩冒烟。原条目转译仍原逻辑，
  未改batch_decompile证据指纹。新增4项严格校验拒绝损坏回归。
- 输出 `/home/user/registration-phase2-font1-delivery/data/script.fls`，SHA256
  `77b3eac611f52cf8ac750fe1adf57d672e3f3e85f51fa5f9c81980e1d6564466`。
  不动用户interface.fls/布局/协议，不绕过流程，不接注册接口。Windows/表单交互待实机。
  源码包已完成CRC/逐文件回读，ZIP `registration_phase2_font1.zip`，24,199,085B，
  MD5 `766b458916c391b872972a371038badf`，SHA256 `438994935eb3fa6af77c2ac4ee06d5d5f0b1602d2f050ee73f9e189b03ce9a7a`。
  源码 `254e934` 已推送。用户本轮明确选择上传，已上传
  [registration_phase2_font1.zip](https://drive.google.com/file/d/1YtpqnvZFYxDJeK9biN3rLyFcr8WYurf9/view)
  到My Drive根目录；返回大小/MD5与本地一致，未改权限/删除旧包，未再次下载核验。
  不能拿此字体修正冒充全部原生验收。

### 3.16 独立脚本编辑器开工授权（2026-10-15）

用户确认font1后“确实好了”，协议→表单这一步已实机通过，不外推全部控件/服务器验收。
用户要求独立工具、可内置编译器、script.fls与data.fls均支持，先看结构后明确“先提交推送然后开工”。
当前工作区干净，既有字体修复已提交至41f1e49；先提交本设计检查点并推送当前会话分支，随后开始M1。
设计见script_editor/DESIGN.md；M1基础不冒充原生写包/Windows双编译器已交付。

### 3.17 独立脚本编辑器M1基础实现（2026-10-15）

**顺序与范围**：先完成设计提交`2f5f7e4`并push固定分支，再写代码。新增独立`script_editor/`，
不跨目录import旧工具，容器只读模块从资源编辑器有来源地整理并去除写包函数。
版本`0.1.0.dev1`；这是基础代码，不是完整工具交付，也不称Windows可用。

- 核心：0SLF/FLS\0惰性只读索引/稳定条目身份/候选VM；FLS目录名、范围、本地头与尾标记严格校验，
  不用GBK替换丢字；不解压/执行恢复模块。打开后的原包修改/路径替换拒绝旧索引；指纹按需计算缓存。
  源码严格UTF8/可读BOM、原子保存、已知输入/硬软链接保护、明确Big5/GBK选中文字面量。
- 项目：相对路径/包SHA/VM/下标与身份、用户关联而非原生语义证明；原包变化拒绝恢复关联，不复制大包。
- 编译：精确2.5.6/2.7.13及magic检查、exe哈希变化拒绝、Windows x86要求、-E -S独立子进程/30秒超时，
  只compile+marshal、不import/exec目标。仅发布标准pyc；原生输出后端不存在、GUI按钮禁用。
  真2.5最小开发编译器缺binascii/_struct，探针/助手不额外依赖它们；中文co_filename显式用UTF8字节，
  不让2.5将unicode路径隐式转ASCII。助手保留2.5语法，仅一处UP031局部豁免有理由。
- GUI代码：双包树/筛选、来源确认、参考稿只读禁编译、源码多标签/行号/基础单行高亮/查找替换/撤销，
  源码与项目脏状态提醒，索引/指纹/编译后台任务。**这些交互测试未能在本环境执行**。
  自检/中文名ASCII CRLF启动BAT、onedir构建BAT/spec和版本入口已写，未构建/冻结/实机。

**实际验证**：`PYTHONPATH=script_editor/src MXSJ_PY25=<外部2.5.6> MXSJ_PY27=<外部2.7.13>
QT_QPA_PLATFORM=offscreen .../python -m unittest discover -s script_editor/tests`：41项，35通过、6 GUI跳过。
两真实编译测试分别核对版本/头魔数、中文文件名、独立完整marshal读取EOF、编译重现全等、故意含文件写入/
raise的源码**未执行**、语法失败旧输出不变、跨VM拒绝。另覆盖包损坏/失效索引、项目迁移/指纹不符、
输出别名/原子发布失败；仓库外独立副本以`-I`导入全部core，无Qt/兄弟目录依赖。
原始`script.fls`与`data.fls`只读实测各5002/133条，未改内容；锁定script/key DB SHA与AGENTS一致。
ruff 0；wincompat --strict 0 ERROR/0 WARNING；bootstrap --check-only因libGL.so.1缺失准确返回2并日志，
不当作环境通过。PySide6 6.12.0装于仓库外venv，未造Qt系统库桩件，GUI没有算通过。

**尚未完成**：M1 GUI实际运行验收；M2双VM变换/原生独立回读/新包输出；M3真实源码链与差异/关联布局；
M4 Windows两套完整运行时、全文件清单/许可证/哈希、EXE/路径/DPI实机。
`runtimes/manifest.json`明确为空，目前仅exe摘要校验框架，不称完整依赖供应链审计。
Linux2.7.13从CPython官方GitHub tag v2.7.13构建，编译器和产物都留仓库外，不混入Git/发行包。
没有上传脚本编辑器测试包、没有开PR/合并/发布；现有两编辑器/注册运行源码未改。

### 3.18 M2双VM原生新包核心（2026-10-15，用户“继续下一阶段”）

**已实现（支持子集）**：`script_editor/`升0.2.0.dev1，核心/API与实验`native_cli`自包含，
不导入旧打包器/猜测修复器。VM2.5递归等宽opcode映射、来源绑定五段XOR、固定原扩展长度/仅根后零padding；
超长拒绝，绝不缩lnotab/伸缩边界。外部catalog需显式包SHA和catalog SHA，profile还绑下标/身份/存储SHA。
VM2.7递归co_extra、split-stream、跳转双坐标与行号转换；完整有界marshal树读取/引用检查、
单条解压64MiB上限、未知/截断/拼接流拒绝；EXTENDED_ARG与uint16寻址溢出等暂不支持。

写包核心只改明确条目，不添加模块/不猜导入hash。0SLF实际物理顺序不同于ID目录，按原物理顺序写，
目录/r1不变，头未知字段/空隙/尾部保留；data未改本地记录连填充全等，改项重算CRC/长度，保留目录原名原字节。
临时包重开后，全量逐条/容器封套比较；改项从实际新包独立逆变换，标准marshal全字节等于本次自写pyc，
再用精确标准CPython完整marshal读取CodeType至EOF；不执行目标模块。原包变化则拒绝。
发布以同目录临时文件硬链接到**不存在的新目标**，含发布竞态也不覆盖任何已有文件；不支持硬链接则安全失败。
此阶段比允许覆盖旧输出更严格，反复编辑须新名字；已补“重开上轮新包/重绑profile/再改再出新包”回归。

**真正复现后修复**：真实2.7编译的分号语句产生连续`6,0`行号事件，初版将零行差当填充全合并，
完整字节回读断言失败；新增失败样例后改为只聚合`255,0`溢出段，保留合法零行差事件，真编译复跑通过。
没有通过裁行号或放宽相等断言来凑绿。跳转参数流第二坐标被篡改也明确拒绝，不再像旧转译器忽略它。

**独立证据/旧研究差异**：当前`exe/python27.dll` SHA256 `66f90925…`，实际EvalFrameEx位于
`0x1E12A3A0`，分发表RVA `0x12D8EC/0x12DA94`，不是旧笔记中的地址。
只读PE/反汇编抽样钉`tests/evidence/py27_dispatch.json`，标准2.7语义与当前DLL核对：
BUILD_SET104→183、BUILD_MAP105→137、LOAD_ATTR106→230、COMPARE_OP107→124、IMPORT_NAME108→135、
IMPORT_FROM109→155；旧注释名称误标，不能当golden。旧表把原生66映为STORE_SLICE+2，当前DLL实际走unknown，
本工具排除该条并拒绝，不改旧研究工具/架构钉指纹。

**本轮实际跑过**：79项，73通过、6 GUI因libGL.so.1缺失未执行；含两真实标准编译器M1/M2完整管线、
嵌套/闭包/long/complex/集合/字典/导入/属性/比较、行号溢出与分号、目标源码含写文件/raise但未执行，
新包重开再编、多项显式替换、损坏/错身份/错键/超长/回读不符/运行时marshal后置失败/发布失败/输出竞态等。
真实材料测试显式`MXSJ_M2_REPO`，不在独立发行工具内暗找仓库路径；独立core副本无Qt/兄弟依赖检查通过。
- 原始script包4007替换当前自写register源码：其余5001条存储负载全等，完整marshal回读通过。
- 原始data包75替换离线探针：其余132条本地记录全等；另实际命令行端到端通过。
  **data探针有意替换核心库，不能用于客户端**；全部验证产物在仓库外/临时目录，没有上传或交付。
- 原始337严格读取遇未知opcode150而拒绝，已有真实材料负向测试，不能称所有脚本都可编辑。
- 锁定script/key DB和原始data/DLL哈希未变；ruff 0、wincompat --strict 0/0；bootstrap --check-only
  仍因缺libGL正确退出2，不算GUI/环境通过。spec补带独立audit助手，未做冻结干跑/Windows构建。

**下一步/未做（M2时点；M3后续见§3.19）**：M3接GUI写包清单、项目承接新包与关联布局/诊断；未知条目继续只读。
M4 Windows标准x86双编译器随包/全文件哈希与许可证、EXE/DPI/原生实机仍未交付；当前manifest为空。
没有修改两旧编辑器/注册源码/原包，没有新增DLL、pyc、FLS、ZIP到Git，也没有合并/发布。

### 3.19 M3可信源码清单与新包续编接线（2026-10-15，功能代码已实施，GUI未验收）

**Linux已做**：`script_editor/`升`0.3.0.dev1`，新增无Qt的`services/workflow.py`，
快照当前编辑区→保留原co_filename原始bytes→真实标准编译与完整marshal审计→
native全pyc往返→不可变预编译清单→沿用M2严格新包发布→纯元数据重基。
明确仅改当前绑定一条，不自动接线/新增模块；无负载变化不出包。
标准pyc单独导出仍用源码路径UTF8，native才用原文件名bytes，不猜字符集。
marshal树现在保留`s/t/R`标量值供文件名读取，发射原raw不变，M2全部回归通过。

GUI拆为window/project_actions/build_actions/preview；匹配选中条目、源码、VM与已验证编译器才启用原生动作。
预编译后清单显示双包来源/身份/摘要/负载变化/源码diff/带行号的静态布局与API线索，默认取消；
陈旧清单不能发布。成功承接确切新包，迁移同包其它绑定/会话基线，其它包不动；
源码文字/dirty/撤销不自动保存或清除。已发布但UI采用失败单独报告新包路径/SHA，保留旧关联。
后台期间全部动作/快捷键禁用，回调显式queued；大包解析/指纹/编译在worker。
项目后台预读全部UTF8/包，采用前拒绝同源跨VM/已开reference冲突；失败回滚新增树/标签。
这些GUI行为已写测试，但当前真实Qt不可运行，**不宣称事务/线程/交互已实测通过**。

schema2兼容schema1读，保存原文件名HEX/上次成功入包源码SHA/显式XOR目录路径、摘要和包来源；
不保存compiler路径、不复制源码/大包/keys。相对路径同盘可迁移，跨Windows盘保存绝对路径。
项目保存不代替源码保存；dirty时明确确认。diff只有会话可信文本基线；重开仅有SHA时明示不能逐行比，
不拿磁盘现文本/反编译稿伪造基线。目录读取限制16MiB，防增长竞态；生成器元数据同样保留输入别名保护。
布局/GetObject/GetChild/FONT_EDIT只是静态提示，不eval/执行、不猜非ASCII字节编码；
**未挂载interface验证控件，不做自动布局接线或资源/脚本联合保存**。

**本轮实测**：105项，91通过、14 GUI明确skip（旧6＋新8）；
含真实2.5.6/2.7.13双VM快照→预编译→发布→项目保存/重开→再编、原文件名非UTF8 bytes真实编译/回读，
schema1/2/相对路径迁移、原包/catalog变化、重复关联、错误SHA/参考稿/VM/语法/基线拒绝、
已有目标/发布失败/其它已知输入保护、未改条目与未选绑定SHA保持；core独立副本无Qt/兄弟目录依赖回归通过。
- 注册当前自写源码经4007两轮离线构建，每轮其它5001条负载不变；不修改注册源码/用户布局/account/CBox。
- 原data条目75经两轮M3工作流，每轮其它132条记录保持；**故意替换核心库的离线探针，禁止客户端/上传/交付**。
- 所有FLS只在仓库外TemporaryDirectory，测试结束删除；没有新增客户端包或编译器二进制到Git。
- ruff check/format通过；wincompat `--strict --no-git` ERROR0/WARNING0/INFO0；compileall/版本CLI通过。
  bootstrap `--check-only`因QtWidgets缺libGL正确退出2；还缺libEGL/libxkbcommon/libdbus，未造桩假验收。
- 原script/data/keys复算SHA分别仍为8b6e9266…/5f96bdb2…/43bb090d…；仅改新工具和文档。
  完整本轮日志位于沙箱仓库外`/home/user/script-editor-m3-verification/`，不作为发行物。

**Windows待验/下一步**：先补真实Qt GUI交互验收（新8项＋原6项），M3仍未完整验收；
然后M4 Windows双x86标准编译器来源/许可/全部文件哈希、随包运行、EXE与中文/空格/跨盘路径、DPI、
文件锁/硬链接、客户端加载和注册业务实机。manifest仍空；没有以Linux编译代替Windows交付。
详细使用与范围见[`script_editor/M3_WORKFLOW.md`](../script_editor/M3_WORKFLOW.md)。

### 3.20 M4准备：整套运行时审计与发行检查（2026-10-15，未交付Windows产物）

**实际实施**：`script_editor/`升`0.3.1.dev1`。确认原`bundled_compiler`仅查EXE SHA，
不能检测DLL/标准库变化；新增core/compiler/bundles.py、distribution.py及runtime_cli/release_checks。
运行时schema2记录精确版本/魔数/32bit、官方源码来源URL/commit/源码包SHA、许可路径和**所有文件SHA**。
有界JSON/重复字段/VM、非法Windows路径/越界/大小写冲突、链接/重解析点、漏件/额外文件、
PE32/x86与EXE/DLL类型、许可缺失均拒绝；CRT须有许可记录。
注册Compiler携带不可变BundlePin，每次编译/完整marshal审计前后复验整套文件及清单；
源码/标准pyc的输出保护包括全部运行时输入，显式开发编译器在GUI说明不是随包审计。
保留schema1空清单不可用兼容，但拒绝schema1非空EXE-only清单，不降级。

runtime_cli支持明确`--static`（不执行，报告static-only），默认真实Windows双VM版本/编译/完整marshal验收；
合成目标含写文件/raise但只编译不执行。stage只往不存在的runtimes子目录复制清单列出的文件，
复验源清单竞态/目标字节，失败只删除本次新建目录，不删除旧EXE/输入。
build_exe.bat在装依赖前即要求双运行时Windows实测，空manifest立即失败；
release_checks要求发现指定GUI/双编译器/native端到端测试，防止空套件假绿；
绑定随包编译器跑全测试，GUI/真实编译器skip致失败，仅6个确切外部游戏/DLL材料测试可缺失；
测试后再核验运行时，PyInstaller后精确复制/复验并记录runtime-audit.json。
没有执行Windows bat/spec，也没有把该流程写成已构建成功。

**本轮Linux实测**：129项收集，115通过、14 GUI仍因libGL/libEGL/libxkbcommon/libdbus缺失未执行。
其中新增24项明确使用合成PE头/测试文件/mock probe，只验证整套SHA护栏/复制清理/竞态/CLI/skip策略；
**这些不是可执行Windows标准编译器，没有启动这些合成PE，不能计为Windows验收**。
既有真实Linux2.5.6/2.7.13、真实双包M3两轮构建及core隔离继续通过；
ruff/format、Windows静态`--strict --no-git`零报告，compileall/版本CLI通过。
bootstrap仍正确退出2；空manifest的runtime_cli审计与release_checks均明确失败，不产出发行物。
本轮日志在仓库外`/home/user/script-editor-m4-verification/`。

**来源事实**：只读GitHub官方refs确认2.5.6 commit `11a859d70dffc8da51d346dabd1fe6a635825ae5`，
2.7.13 commit `9c1426de7521299f70eb5483e7e25d1c2a73dbbd`；核验已有codeload源码包SHA，
见[`M4_RUNTIME_DISTRIBUTION.md`](../script_editor/M4_RUNTIME_DISTRIBUTION.md)。
这是源码来源，不是Windows二进制哈希；未伪造运行时清单条目。旧vcproj/vcxproj工具链不能假定当前runner直接可编译。

**未解决/下一步**：没有Windows/Wine执行环境，没有真正标准x86双运行时或CRT再发行许可/逐文件实际哈希；
manifest仍为空（schema2）。需真实Windows旧工具链构建/合法来源审查、子进程DLL搜索路径/中文ANSI argv/跨盘、
NTFS硬链接/文件锁、14项GUI/EXE双击/DPI/退出及客户端业务验收。
整套本地哈希不等于数字签名、可重现构建证明或法律许可审核；不称M4完成/免安装交付。
本轮仅改新脚本工具与文档，不修改游戏/keys/DLL/注册源码/用户布局，不上传游戏探针，不合master。

### 3.21 脚本编辑器源码GUI测试包已授权上传（2026-10-15，历史缺件包）

> 已被§3.22的含双编译器源码ZIP取代；以下保留历史记录，不是当前交付状态。

用户明确授权“打包传到网盘我去测试”。上传前已说明这是源码测试包，不是EXE/内置双编译器发行。
新增`script_editor/先读测试说明.txt`（启动与测试边界/最小脱敏反馈），修README中遗留的“只复制空清单”旧构建说明。
独立工具全部从提交`7f3414e8242d1ed2e6f418d0d9cc89a89eb4e692`取材，打包bat恢复ASCII/CRLF。
新增包内PACKAGE_MANIFEST.json记录来源提交与逐文件SHA；无游戏/FLS/DLL/EXE/keys/探针/本地日志或缓存。

- 文件：`MXSJ_ScriptEditor_0.3.1.dev1_source_test.zip`，86文件，135692字节。
- SHA256：`45638bb94756f2e43a39883e536b2c0df58a1018ffe5d711f86686e9756b3b05`。
- MD5：`e6cda49d6a1f186ebdeb16a54af4fac5`；Drive返回MD5/size与本地一致。
- 网盘：https://drive.google.com/file/d/135Wg6izLhOVzQ4H9e5-L3273_6DiUrhi/view 。未修改分享权限。
- 解压到仓库外独立目录复测：129项，115通过，14 GUI因真实Qt系统库缺失未执行；
  ruff 0、版本CLI0.3.1.dev1、包内逐文件SHA全匹配，ZIP CRC全过。
  真实双编译器与游戏材料测试仅通过显式环境变量启用，不是运行时自动寻找仓库。
- 产物和日志仅在仓库外`/home/user/script-editor-0.3.1-delivery/`，没有把ZIP/编译器加Git。

用户解压先读说明，双击启动bat；需已有Python3.10+，自检尝试安装PySide6。
这轮可测双包索引、源码编辑/撤销/查找替换/关闭与只读保护；缺已验证开发编译器时原生写包不可用。
script关联还需用户显式提供匹配包的研究目录，不猜key，不拿游戏DLL或反编译稿替代。
当前空runtime清单使build_exe.bat明确拒绝发行构建；不要把源码GUI测试当Windows免安装交付。
M4真实Windows运行时/许可/EXE与M3 GUI实测仍待完成，不重传旧font1/diag2或游戏验证探针。

### 3.22 补齐双Windows编译器并重新打包上传（2026-10-15）

用户明确要与UI/资源编辑器一样的**独立源码包**，由包内脚本自行构建编辑器EXE；
这次修补的是缺失的两套编译器，不再给空manifest的替代GUI包。
先推送维护者构建脚本检查点`188b16d`，再推送产品代码`efeddeafcadf5ddf999567dfbfe59f15e2241a02`。

**补齐的真实构建物与产品变化**：
- 从固定官方源码交叉构建标准CPython2.5.6/2.7.13，Zig0.13.0、x86-windows-gnu；
  分别156/178个官方core编译单元，0失败。4个EXE/DLL均为真实PE32/i386，非合成测试PE或游戏DLL。
- 两套各9个文件：EXE、DLL、ZIP_STORED纯Python标准库、BUILD.json及5份原许可；
  schema2清单现非空，全部18个文件实际SHA/官方归档URL/commit/归档SHA齐。
  2.7.13归档SHA已按本次实下纠正为`ae1dc735e2990bf8de8e73c3f77b35d4f69502570957c743a7e8618a652fe08a`。
- 只改MinGW平台适配（posix分支、私有strcasecmp名、Windows.h大小写），每文件前后SHA写BUILD；
  compiler/opcode/marshal未改。原许可含CPython、Zig、MinGW、LLVM、zlib。
- 目标Windows10/11系统UCRT，不再分发微软CRT，不支持XP/Win7；这是compiler-only运行时，
  非含全部外部扩展的通用Python2发行。维护者可用`build_runtimes.py`重建，普通用户不需要Zig。
- GUI开窗后后台自动探测两套精确版本/魔数/x86/整套SHA，无需先打开源码选EXE；
  失败显示诊断、禁用对应编译，不阻止源码阅读编辑。新增无Qt依赖的`检查内置编译器.bat`；
  bootstrap的check-only也做真正双编译/marshal验证。build_exe仍严格拒绝GUI/编译器skip和缺件。
- 二进制保持gitignored，只随交付ZIP；不改原游戏/keys/注册源码、布局/account/CBox或旧编辑器。

**实测与未验范围**：
- 重新构建真实Linux2.5.6/2.7.13作为回归编译器；134项118通过、16 GUI因libGL缺失未执行（3.353s）。
  显式启用只读游戏/DLL材料；全套包括两VM原生包/注册项目续编回读，原包/keys SHA保持锁定值。
- ZIP解压到仓库外含中文/空格的独立目录：134项112通过、22 skip（16 GUI＋6 opt-in材料，1.687s）；
  不携带游戏材料，只通过显式环境变量使用回归编译器，不依赖仓库兄弟目录。
- 18文件整套静态审计通过；ZIP CRC及全部109个交付文件SHA清单一致；
  解压副本wincompat walk 109文件/72源码脚本，ERROR/WARNING/INFO均0；ruff0且77文件format通过。
  bootstrap正确退出2/写日志（Qt系统libGL缺失），不把未执行当通过。
- Windows CI尝试run38662087057在分配job前startup_failure；试验工作流已移除。
  Wine源码构建实验也未得到可执行环境；均没有Windows运行证据。
  **真实Windows启动/编译/marshal、GUI、EXE自构建/双击、中文跨盘/文件锁及客户端仍待验证**。

**已上传的新交付**（只上传这一份工具ZIP，不重传旧包/探针、不改分享权限）：
- `MXSJ_ScriptEditor_0.3.2.dev1_source_with_compilers.zip`，109文件，**7114401字节**。
- 源码提交：`efeddeafcadf5ddf999567dfbfe59f15e2241a02`。
- SHA256：`17194fd1f1df20e656f0919fff07ef47b8663e05175837eba1c3557efcaaf8cf`。
- MD5：`19ee695bfc4b94f3fbeac21b3fea0876`；上传后重新读取Drive元数据，MD5与size均和本地一致。
- 网盘：https://drive.google.com/file/d/1yb1JsQbnWgremYR5u1-aQlwFjOWPSFO_/view 。
- 包内附`先读测试说明.txt`、`SOURCE_DELIVERY.json`、`PACKAGE_SHA256.json`与明确static-only的审计记录。
  源ZIP/构建工作区在仓库外缓存；源码与构建方法已Git保存，ZIP/编译器没有加入Git。

用户完整解压到新目录，先双击检查内置编译器bat，再启动GUI；需EXE时自行运行build_exe.bat。
不需要另装Python2；源码启动/自构建仍需Python3.10+及PySide6。源码交付形式本身符合要求，
剩余问题是Windows实测，不再把“必须由助手给成品EXE”当作验收条件。

### 3.23 脚本编辑器工作区重整（2026-10-15，代码初版/仅预览）

用户明确指出0.3.2“这么简陋”，原菜单＋三栏文本框不能当成完整编辑器交付。
先提交/推送检查点`0d18214`，再实现0.4.0.dev1；未重新打包上传，不把旧网盘链接当新版。

本轮实际改动：
- 工具栏与菜单复用同一QAction，打开包/源码/项目、保存、撤销重做、查找、关联、生成新包、
  编译器检查可直达；按来源/关联/VM/任务状态启用，不新增空按钮。
- 可停靠包导航、来源属性、大纲、底部检查台；视图菜单隐藏/恢复默认；正式入口QSettings只保存
  窗口/面板布局，测试注入独立设置，不污染用户偏好或自动重开游戏文件。
- 包选择器明确切换script/data，原包只读；显示0基下标与真实记录身份，不猜模块名；
  已关联者标注来源文件，双击打开对应源码，切包不自动改源码VM或关联。
- 源码标签带路径/来源/VM，等宽字体、当前行、四空格Tab/选区缩进、自动缩进、三引号状态高亮。
  UTF-16位置处理兼容非BMP字符；选区缩进、全部替换仍一次撤销，参考稿各入口只读。
- Ctrl+F区分大小写/整词/双向循环查找、当前/全部替换；类/函数分层大纲和布局/控件引用可定位行。
  只做词法线索，兼容Py2 print语句，不AST执行/恢复代码，不声称挂载/语法已通过。
- 差异明确比较打开时文本与编辑缓冲区，保存不伪造原包文本基线；分析延迟合并，
  大型源码停止自动扫描；超长差异明确标注截断，不改变实际编译文本。
- 工作区拆分成独立装配/菜单/行为/源码标签模块；后台任务同时禁用停靠区交互并恢复原状态。
  原包只读、可信源码、双VM隔离、严格预编译/新名发布/回读护栏和编译器文件完全未放宽。

**真实GUI环境与现场发现**：
- 原沙箱缺GL/EGL/xkbcommon/dbus，现用真实GLVND1.7.0、D-Bus1.12.24及OpenCV wheel里的真实
  libxkbcommon补齐进程本地依赖；不是桩库、不修改系统PATH，不随产品分发Linux库。
  私有测试依赖与日志保留`/home/user/script-editor-test-environment/`，PySide6安装仍在外部venv。
- PySide6 6.12.0/Python3.11.2的最小QTreeWidgetItem循环复现None计数每条减2并崩溃；
  不是原包损坏。已固定6.10.3并实测6000节点，bootstrap识别/修复不匹配版本，
  直接GUI入口也拒绝其它版本；源码Python支持范围明确为3.10—3.14。
- 6.10.3下枚举临时menuAction会释放C++菜单/分隔符；已显式持有菜单、menuAction和dock action引用。
  原有菜单/禁构建测试真实复现失败后修复，不是改测试绕过。

**本轮实测**：149/149全执行通过，含26项GUI及真实Linux2.5.6/2.7.13编译、只读原材料与
两轮原生新包/项目回归（最终3.754s）；无GUI skip。新增15项：工作区/来源/导航、缩进/高亮、
引用/差异、搜索撤销、6000节点、Qt版本拒绝以及纯核心词法大纲。
ruff0、84文件format通过；wincompat95文件/79源码脚本，ERROR/WARNING/INFO均0。
18文件双Windows运行时静态审计仍过，原script/data/keys SHA保持锁定值。
bootstrap现在真实加载Qt后正确退出2：非Windows禁止执行Windows运行时，不再是缺Qt库。

真实预览：`/home/user/MXSJ_ScriptEditor_0.4.0_workspace.png`，由实际Qt程序抓图，
打开只读script/data与已有作者源码；编译器为显式选入并验证的Linux开发版，不冒充Windows执行。
**0.4未重新打包/上传；Windows双编译器、GUI、EXE/客户端验收仍待。**
当前先提供界面方向预览，不再把测试数量当作界面完整性或成品交付的替代。

### 3.24 工作区重整源码＋双编译器正式上传回执（2026-10-15）

用户明确授权“提交推送上传”。功能提交`4655c77`，交付说明提交并推送
`0216b58f80c327f0373455e39633143f602f7cd4`，按此提交的script_editor完整tracked文件
打包，额外仅加入manifest指定的18个真实Windows运行时文件、静态审计和来源/SHA清单。
所有bat规范化CRLF。§3.23的“仅预览/未上传”为历史检查点，现由本回执取代。

- 新文件：`MXSJ_ScriptEditor_0.4.0.dev1_source_with_compilers.zip`。
- Drive：[下载0.4.0源码＋双编译器](https://drive.google.com/file/d/1QNXpgwiGECqh377UN2npCNNTh32AGAvn/view)
  （ID `1QNXpgwiGECqh377UN2npCNNTh32AGAvn`，与旧包同一My Drive根目录，旧包保留，不改权限）。
- 116文件，**7,130,558字节**；上传后另调get_file，大小和MD5与本地相同；未再次下载。
- SHA256：`d4f417c142657aafa29ede993d5fcb807161b002e30e782a0d31a71dd4f3f9ed`。
- MD5：`1c5338c7427e709aa3793cfb550afea7`。
- 本地交付：`/home/user/deliveries/script-editor-0.4.0/`，含ZIP及receipt.json；不进Git。

交付前复跑仓库**149/149全通过**（4.879s，26 GUI，无skip）。ZIP完整解压到仓库外
含中文/空格的新目录，清除MXSJ_M2_REPO、只用自身src再测：149项中**143通过、6项外部游戏
材料测试按设计跳过**（2.083s），26 GUI全部执行，真实Linux双编译器及核心原生新包回读通过。
独立源码ruff通过；Windows兼容严格扫描121条目/79源码脚本，0 ERROR/WARNING/INFO。
本地ZIP CRC、精确文件集合、每个文件SHA、18运行时文件已在上传前/后核对；
解压后静态SHA/PE/来源审计也通过，未混入缓存、启动日志、游戏材料或Linux测试依赖。

交付是**独立源码测试包＋内置CPython2.5.6/2.7.13 Windows x86编译器**，不是编辑器EXE。
Windows端先完整解压到新目录，运行“检查内置编译器.bat”，再运行“启动脚本编辑器.bat”；
需要EXE时用户运行build_exe.bat，实际双VM/严格GUI检查不通过仍禁止构建。
Windows双编译器执行、桌面、EXE/客户端验收仍待；不把Linux结果或静态审计冒充通过。

### 3.25 Windows刚打开即误报源包变化修复（2026-10-15，0.4.1.dev1）

用户在0.4.0实机看到“源包打开后发生变化或被替换”，进一步确认**刚打开就报**。
不能据此认定用户改包。排查并对照官方CPython3.13/3.14源码：
`Modules/posixmodule.c`的win32_xstat把ctime重映射成birthtime；
`Python/fileutils.c`的_Py_fstat_noraise经FileBasicInfo保留实际ChangeTime。
因此ArchiveDocument将path.stat()与reader的fstat五元组直接比较会误报；
用户Python精确版本尚未知，但代码问题与触发症状一致，不需要先让用户反复重新打开。
源码依据：[CPython3.13 posixmodule](https://github.com/python/cpython/blob/v3.13.0/Modules/posixmodule.c)、
[fileutils](https://github.com/python/cpython/blob/v3.13.0/Python/fileutils.c)。

修复：
- FileReader的大小/初始修订同次fstat捕获，ArchiveDocument不在初始化中重新把变化当新基线。
- 新增path_revision：重新只读/二进制打开当前路径，同一fstat接口核对身份、大小、mtime/ctime，
  临时描述符在finally关闭；原句柄前后复核仍在，不能只看旧句柄或去掉inode/时间检查。
- revision与close共用锁，初始化快照失败也释放原描述符；不改源包、不改编译器或GUI工作流。
- 版本0.4.1.dev1；新的Windows差异回归列入build_exe严格必跑集合。

新增5项：模拟路径/句柄ctime/身份命名差异的不变文件、相同元数据下路径身份改变、
句柄变而路径快照伪装未变、FileReader打开后初始化前变动、临时快照失败释放句柄。
先跑旧码，ctime/身份差异两子用例复现同一ContainerError，且打开后重设基线用例未拒绝；
修后5/5通过。其它新API相关旧码失败不冒充已有行为缺陷证据。
完整Linux154/154（26 GUI、真实双Linux compiler/只读材料）全执行通过，4.238s。
模拟Windows差异不是Windows实机执行；不重新给0.4.0链接当修复版。

**0.4.1交付回执**：
- 修复与随包源码：`661efe3e858565bf29aaba428a78e2594c2ce523`，已推送固定分支。
- [下载0.4.1修复源码＋双编译器](https://drive.google.com/file/d/1xnMZls3kZmylUHZi8sRrcvlvnt4bU9fQ/view)。
- 文件`MXSJ_ScriptEditor_0.4.1.dev1_source_with_compilers.zip`，117文件，7,132,907字节。
- SHA256：`ef5f7a4a308b52d9bfeb5af7dfecec1720ae3859a7fe07fcd77d23551d26c5b3`。
- MD5：`61eac4d24c136a2eb0522961acb67df2`；上传后另调用get_file核对大小/MD5一致，未再次下载。
- 与旧包同一My Drive根目录；旧包保留、分享权限未改。仍为源码＋两套18文件Windows x86
  compiler/标准库/许可/清单＋自构建EXE脚本；不含游戏、keys、离线探针或Linux测试依赖。
- ZIP CRC、精确文件集合、逐文件SHA通过；双运行时静态审计复过，编译器本身未改。
  独立解压到仓库外中文/空格目录，仅自身src、取消真实材料环境：154项148通过，
  6项材料测试按设计跳过，26 GUI全执行，2.222s；ruff/严格兼容122条目80源码，均0。
- 本地`/home/user/deliveries/script-editor-0.4.1/receipt.json`保存交付核对；不进Git。
- 提醒用户完整解压到新目录，确认版本0.4.1.dev1再打开自己的原包；不要改原包元数据、
  删除保护、换游戏DLL或覆盖旧工具目录。Windows修复效果仍待实机确认。


### 3.26 补真正包内脚本读取与恢复编辑（2026-10-15，0.5.0.dev1开发中）

用户发现所有未关联条目都提示先提供自己的源码，并进一步质疑“残次品，不能编辑源码有什么用”。
已承认0.4只是有源回编器，不满足用户从包内打开现有脚本编辑的目标，不再拿信任限制或UI重整代替功能。
本轮先push既有检查点，再补包内工作流；**未上传0.5候选、未提供旧链接冒充新版或宣称功能全面**。

已实现：
- 未绑定条目双击后台严格解码成标准pyc，调用独立30秒限时进程恢复；三页中央工作区为
  可编辑恢复草稿/反汇编/来源诊断。失败显示具体缺参数/未知映射/坏格式与存储预览，不造pass源码。
- 草稿可撤销/查找/显式字节转换/另存新UTF-8.py；新文件原子拒覆盖及竞态，原参考页仍只读。
  草稿可编辑但不自动绑定，不准直接原生发布。重新打开带草稿/VM标记的文件也仍未核验。
- 检查并采用：VM/条目/来源指纹核对→真实标准编译→原生往返全字节回读→人工确认业务逻辑，
  才标记recovered-reviewed并建立关联；未修改的部分恢复输出直接拒绝采用。
- 关联新增source_kind/recovery_sha256，schema2兼容缺省authored，拒绝未核验草稿/未知来源入关联；
  项目重开保留恢复来源，清单显示原标准字节码SHA，不把恢复稿称作原始源码。
- 已读嵌入文件名可在树标签显示/筛选，原始文件名字节仍无损保留，不用于猜模块身份或写磁盘路径。
- 继续原有F6不可变清单、每轮新名/只读原包、未改条目保留、完整回读及项目承接，原生codec未改。

恢复引擎：uncompyle6 3.9.3 / xdis 6.1.8 / spark-parser1.9.0 / six1.17.0 / click8.5.0固定依赖，
bootstrap只查分发元数据不在GUI导入引擎；主进程只以标准pyc/JSON文件调用独立GPL worker。
GPL worker单独spec/EXE，主GUI明确排除其引擎；build_exe新增独立程序、完整上游对应源码/许可归档，
最后实际双VM恢复EXE smoke，任何失败阻断；**本轮没有Windows构建或执行，不能称这些已实机验收**。
新增源文件许可及上游全文在licenses/recovery，原主编辑器权利不自动改成GPL。
输入先核心限量marshal验证；超64MiB存储不加载全条目，仅预览；worker输出限长/协议验证/无stdout污染。

现场修复真实输出问题（不改VM指令/编译器/原加密边界）：
- uncompyle6在Python3宿主给2.5字符串输出b前缀，合法2.5不能编译：仅按token移除b，保留字节内容。
- 部分模块尾隐式LOAD_NAME None被输出为非法顶层return：只处理最后的顶层bare return/return None，
  不碰函数return/表达式返回值。
- xdis6.1.8的UnicodeForPython3.__repr__丢前两字并错误输出u'\u'；在独立worker中修正常量显示，
  Unicode以正确u+ascii转义，不改常量值，兼容future_unicode_literals，不修改安装的库文件。
  新增中文/引号/反斜杠/非BMP/字节常量的真实双VM编译并解析marshal核对值，不只是断言能编译。

真实回归：新增13项，合计**167/167全执行通过，30 GUI，无skip**，8.438s。
- 合成合法模块由真实双compiler编译，包内恢复/编辑/两轮读取和来源项目重开；带副作用sentinel但绝不执行。
- Qt真实worker从未关联条目进入可编辑草稿，取消另存/拒绝采用/明确采用/F6发布及项目重开，双VM均过。
- 真实原包script下标4007和data75直接恢复（不取作者.py），编辑后回编/新包回读通过；未改5001/132逐条全等。
- script4007原样恢复稿回编**超过原固定展开长度10字节**，没有放宽护栏；隔离回归明确缩短常量后
  验证在原边界内可写。**这不是任意模块任意改动都能写回的证据，更不能隐藏固定长度限制**。
- 失败/缺catalog/资源条目、VM/marshal拒绝、timeout、发布竞态及未核验关联拒绝均有回归。
ruff0、92文件格式通过；严格兼容109条目/86源码脚本，ERROR/WARNING/INFO均0。
实际调用发行入口`python -m script_editor.release_checks --root script_editor`，返回2并明确
`Release blocked: Windows运行时执行验收只能在真实Windows进行`；未伪装平台/替换发行编译器绕过，
因此167项是Linux开发环境测试通过，不是Windows发行检查通过。
真实Qt恢复视图已抓图并查看：`/home/user/script-editor-recovery-workspace.png`，实际双包、原4007恢复草稿可编辑、
无源码关联、无目标执行/写包；编译器为显式Linux开发版，不是Windows实测证据。

**未解决/待授权**：
- 工具目前仍不附匹配script.fls的XOR参数表。为了用户开包即可读取，需要明确授权将既有固定原包
  对应的逐模块解码参数与工具交付；不擅自把“只传工具不传keys”的旧边界改掉。
  未授权前不复制/上传参数、不猜key；data恢复本身不需要该目录。下一步只询问这个交付决定，不让用户重新决定核心功能。
- 未知映射/分段失败/反编失败只诊断，不保证全部恢复；script超过固定长度仍拒绝，未做lnotab裁剪或猜边界。
- 尚无全包模块名扫描/恢复覆盖率批处理；Windows恢复EXE/GUI新流程/客户端语义仍待验。
- 当前0.5为已提交开发进展，不是已完成“功能全面”的新发行包；旧0.4.1只有开包误报修复。

### 3.27 已授权附带固定原包参数，制作0.5独立源码测试包（2026-10-15）

§3.26核心及回归已在8d6ee2d/09414c6提交推送。之后询问唯一阻断交付的参数授权，
用户明确选择**“允许附带匹配的解码参数”**，不是要求其提供源码，也没有授权上传游戏包。
据此把原有已知SHA的参数原样复制到工具自身decoding/script-original.json，独立运行不读仓库tools。
自动使用条件为整个原包SHA和参数文件SHA同时精确匹配；data不需要；其他包不按名字/目录猜测。
派生包使用已验证项目关系，或显式确认来源选取JSON后逐模块严格校验；保留固定边界/未知拒绝。
打开包的SHA计算在后台，不冻结UI；缺/坏参数不隐藏包索引，诊断明确且不套错误参数。

新增参数audit/stage CLI及Windows构建复制复查，缺件/摘要错/目标已存在阻断；参数不进入运行时清单，
两套compiler仍按原18文件独立清单。新增3项参数匹配/篡改/拒覆盖回归，1项实际Qt开包自动匹配后
无外部源码恢复编辑回归；发行检查强制此GUI用例和内置参数摘要。真实4007/data75回归已改用工具
自身参数自动匹配，不再读取tools目录。

当前全套**171/171，无skip，8.781s，31 GUI**；ruff0/96文件格式全过，严格兼容114条目/89源码脚本
ERROR/WARNING/INFO均0；原包script/data和原参数SHA未变。真实Windows发行检查仍因非Windows返回2，
没有降低门槛。接下来从提交快照打独立源码＋完整双Windows编译器＋参数ZIP，中文路径隔离解压回归，
静态审计与逐文件清单复核后上传原网盘父目录，不改分享权限；完成后记录新的链接/摘要。

## 4. 等待外部输入

| 事项 | 等谁 | 阻塞什么 |
|---|---|---|
| 脚本编辑器0.5源码测试候选（§3.27），参数授权已获 | 新源码ZIP上传后用户Windows/客户端测试 | 不重复询问参数授权；script固定容量/未知映射继续严格拒绝，不把Linux或静态检查冒充Windows |
| 资源大包打开/新布局查找用户已确认通过；其余 Windows 快捷键/EXE、新图游戏加载仍待验 | 用户 | 不把两项交互通过外推完整编辑器/原生加载验收 |
| font1用户确认“确实好了”；account/CBox保留 | 后续功能按需验收，不再等font1重传/复测 | 不外推全部表单/真实服务器成功，不重导/改用户布局，不索取真实资料 |
| 真实注册接口与五账号整批成功回覆 | 后续服务端工作线（未开工） | 已定单条批量＋重名顺延（最多 `_99` 且最终 16 位，整批五个/同批重试不重复创建）；真实接口/固定成功回调调整/服务器验收未做，本阶段继续留桩，不能假报成功 |
| 是否合入 master、是否清理二进制 | 用户授权 | — |

## 5. 下一步（优先级）

当前用户请求优先：补真正可从包内恢复/编辑脚本的功能，不再只修UI或要求自有.py（§3.26）。
0.5开发工作流已实测，匹配参数的交付授权已获得；正打独立源码新包，不宣称全面完成，继续补覆盖率/固定长度/Windows验证，
不把阶段版或旧0.4.1网盘包当满足用户目标的成品。
M3功能已接线且核心离线回归通过（§3.19），
M4双Windows编译器/标准库/许可及完整SHA已补齐并随源码ZIP上传（§3.22），
Linux原先缺库的GUI现已全量实际通过；Windows仍须双编译器自检、真实桌面及EXE/客户端验收；
布局当前仅静态线索，不将挂载验证/自动接线算作已完成。
font1用户已确认好了，不再沿用旧账号框排查为当前任务；保留用户布局与account/CBox。
下面其余历史工作不混入本轮脚本编辑器实现。

1. 修 §3.1（单独一个小提交），让架构套件与 `--check` 回绿。
2. **UI 编辑器 × script.fls 联动 + 注册界面原生重做**（用户 2026-10-14 定的方向，合并为一条线）：① ✅（0.7.0）离线索引生成器 `tools/script_link/build_script_index.py`：不跑反编译、直接转译+解析 Py2.5 marshal/字节码挖掘，4,987/5,002 个模块挖成（15 条基线转译失败未做边界修复），关联 2,920 个布局、13,162 个被取用名、19 个高置信代码皮肤锚点；随包 `script_index.json`（1.3 MB，查询层 `core/script_index.py`）。② ✅（0.7.0）代码现造的按钮（如 login 的占位锚点）按真皮肤渲染，不再显示默认占位（`painters._paint_code_skin`；皮肤覆盖仅限高置信工厂模式，其余代码控件仍占位）；左栏「脚本」页显示引用模块/被取用控件/锚点与皮肤详情，点名字回画布选中；打开布局状态栏报关联计数；③ ✅（0.8.0）改名/删除子树引用护栏、静态布局诊断与保存前清单（详 §3.7）；加控件自动接线（GetObject 认领 + OnMessage 骨架 + 空闲消息号）仍未实现；④ 脚本可在编辑器内查看/编辑，保存时布局与脚本一起出新包（写回管线 `tools/decompiler/pack_and_encrypt.py` 已验证往返逐字节一致；编辑后源码编译依赖 CPython 2.5.6——**2026-10-14 已在沙箱从 GitHub 源码自建成功**，自写源码经编译→混淆→5 段 XOR 加密→重打包→解密→转译往返全通（代码对象/繁体 unicode 常量/控制流一字不差），「仓库侧打包」路线打通，不必依赖 Windows）；⑤ 第一个实战：注册界面按原生重做（原生 `.dlg` + 原生脚本套路，参照 `chgpwd` 类原生表单；提交先留桩并明示未接通；用户已定字段/条款页/桩文案，见 §6）。硬边界：546 个 stub + 12 个转译失败的脚本无源码、不可联动编辑，须明确标记；写脚本前先拿无害小改动做真机验证。
3. 判定 §3.2，统一 `notes/` 与编辑器文档。
4. 两编辑器新功能先在客户端副本上复核（新增路径下拉、包树右键导入/替换、连续新包导入和新增原生编码布局加载）：撤销/重做混合批量、引用取消/确认、诊断定位/刷新、保存清单取消与新包读回，特别检查保存后新图解析器来源迁移；严禁覆盖原包。三个编辑器在 Windows 实机跑 CONVENTIONS §5.3 冒烟（启动 bat → `build_exe.bat` → 双击 EXE），把结果回填 §2 / §3.5；沙箱侧 10-14 已把完整测试（含 GUI 组）跑绿，不再需要「有桌面的机器跑测试」这一步。
5. 二进制清理（需授权）与 LICENSE/权利说明。
6. 服务端第一条真实链路（网关 + 账号 + 区服 + PostgreSQL），按 `server/docs/GATEWAY.md`、`INTERFACES.md` 开工；在此之前不要再堆设计文档。

## 6. 最近变更

| 日期 | 变更 |
|---|---|
| 2026-10-15 | 用户明确允许随工具源码网盘包附带固定原包匹配解码参数；已实现后台完整SHA自动匹配、参数摘要核对、独立audit/stage及新GUI无手动参数恢复回归。171/171（31 GUI）通过，正打独立源码＋双compiler＋授权参数包；仍不含游戏包，不宣称全面完成，详§3.27。 |
| 2026-10-15 | 用户拒绝只能关联自有源码的残缺功能：0.5开发接入包内严格解码/独立恢复进程、可编辑草稿/反汇编、检查人工采用、来源持久化及双VM回包续编。167/167（30 GUI）通过，真实4007/data75恢复编辑回包且5001/132未改；修恢复引擎Unicode/Py2.5字面量渲染。未上传候选，不宣称全面完成；XOR参数随包授权待定，script固定长度/未知模块/Windows仍待，详§3.26。 |
| 2026-10-15 | 用户0.4.0刚开包报源包变化：定位Windows stat/fstat ctime语义差异，统一原/新句柄fstat并固定初始快照，保留修改/替换保护。修复661efe3已push，0.4.1含双编译器源码ZIP上传Drive `1xnMZls3kZmylUHZi8sRrcvlvnt4bU9fQ`，7132907B/117文件，重读大小MD5一致。154/154（26 GUI），解压148过＋6材料跳过，Win差异模拟先失败后通过，实机待确认；不改游戏材料/权限，详§3.25。 |
| 2026-10-15 | 按用户“提交推送上传”：0.4.0.dev1工作区源码＋双Windows编译器新ZIP已传Drive `1QNXpgwiGECqh377UN2npCNNTh32AGAvn`，7130558字节/116文件，重读大小MD5一致；源码0216b58，仓库149/149（26 GUI），独立解压143过＋6材料跳过，ZIP逐文件SHA与双运行时静态审计过。不含游戏/keys/探针，不改权限；Windows/EXE/客户端未验，详§3.24。 |
| 2026-10-15 | 用户批评脚本编辑器简陋：先push检查点0d18214，重整0.4.0.dev1工具栏/可停靠工作区、包切换、大纲/引用定位、编辑差异、查找和缩进。补真实Qt依赖，149/149（26 GUI）全执行通过；隔离Qt6.12/Python3.11大树崩溃，固定6.10.3并修菜单生命周期。提供真实Linux Qt截图，仅预览未重打包上传；Windows未验，详§3.23。 |
| 2026-10-15 | 按用户“补齐重新打包上传”：0.3.2.dev1独立源码＋真实Windows x86双编译器ZIP已传Drive `1yb1JsQbnWgremYR5u1-aQlwFjOWPSFO_`，7114401字节，重读MD5一致；18运行时文件SHA/标准库/5许可与自动双VM检查齐。134项118过16 GUI未执行，独立解压112过22跳过；源码提交efeddea，不含游戏/keys/探针，不改分享权限。真实Windows/GUI/EXE/客户端未验，详§3.22。 |
| 2026-10-15 | 用户授权打包上传测试：脚本编辑器0.3.1.dev1源码GUI ZIP已传Drive `135Wg6izLhOVzQ4H9e5-L3273_6DiUrhi`，135692字节、MD5与本地一致；解压副本129项115通过14 GUI未执行，先读说明/启动bat随包。明确无EXE/Windows双编译器、不含游戏包/keys/探针，不改权限；等用户真实GUI测试，详§3.21。 |
| 2026-10-15 | 用户继续：脚本编辑器0.3.1.dev1补M4整套运行时文件SHA/PE32/来源许可/注册后复验及严格发行检查；129项115通过14 GUI缺系统库未执行，新增24项为合成PE/mock护栏测试。manifest仍空，Windows真实双运行时/EXE与M3 GUI均未验收，缺件不再构建假完整发行；原包/注册源码/旧工具未改、无上传，详§3.20。 |
| 2026-10-15 | 用户继续M3：脚本编辑器0.3.0.dev1接可信源码预编译/清单/GUI单条新包与项目续编、原始co_filename字节/schema2/静态引用提示；105项91通过14 GUI缺真实系统库未执行。注册4007及data75均两轮离线回归、其余5001/132保持；M3 GUI未完整验收，M4随包编译器/EXE仍未交付。原包/keys/注册源码/两旧编辑器未改，无上传/合并/发布；详§3.19。 |
| 2026-10-15 | 用户继续下一阶段：独立脚本编辑器0.2.0.dev1实现M2支持子集原生后端/实验CLI，79项73通过6 GUI未执行；真编译/真实双包回读全等及5001/132未改条目校验通过。修真实分号lnotab零差事件丢失，静态核对当前DLL分发表和2.7语义、排除错误opcode66。只生成仓库外验证新包，旧原包/研究工具未改；GUI写包/M4随包编译器未完成，详§3.18。 |
| 2026-10-15 | 按用户“先提交推送然后开工”，先push设计检查点`2f5f7e4`，再实现独立脚本编辑器0.1.0.dev1基础，双包只读/手工源码与参考模式/项目/双标准编译核心。41项35通过6 GUI缺libGL未执行；ruff、wincompat 0；bootstrap正确返回2。原生写包/Windows随包编译器禁用或未实现，详情§3.17；未改原包/旧工具，不当作完整交付。 |
| 2026-10-15 | diag2实机报missing_attribute=FONT_EDIT。按原entry4007的FontLT14_3原生调用修四框/提示区，去除旧FONT_EDIT/COLOR_EDIT依赖与假测试桩；旧源无别名探针失败→新源通过，真2.5.6 32/32。新源构建校验发现旧边界猜测误改LOAD_FAST，新增严格自写marshal确定逆变换而非放宽断言，原转译器/key DB不改。新包与精确diag2重建仅4007变化，保留全部用户布局；实机待验，交付状态见§3.15。 |
| 2026-10-15 | 用户已进入协议，同意消息1到达、表单layout ready，但账号框初始化AttributeError；用户确认account/CBox。新增diag2拆解原生输入框调用、受限缺失属性/代码位置日志；只读原生工厂签名核对并纠正桩的cls(name)错误边界。真2.5.6 26/26、旧源定位探针先失败、新包marshal回读/桩冒烟/5001条与diag1等值、ruff与wincompat通过。不动用户布局，不声称已修好；本轮用户明确授权后上传Drive，大小/MD5与本地一致，详§3.14。 |
| 2026-10-14 | 用户否决一次性两路径助手作为终局，资源0.4.3/UI0.8.3修正常新增/修改/连续保存：统一原生路径XOR，旧明文/错key目标显式保存迁移，严格原生发布验证，不覆模板，不碰script；独立旧行为两FAIL→两PASS，资源118/118、UI203通过+1跳过、注册23/23，ruff/wincompat/启动自检通过。Windows与协议→表单仍待验，源码包已获当轮授权上传Drive，大小/MD5一致，交付链接见 §3.13。 |
| 2026-10-14 | 用户日志确认diag1已不再冻窗，但条款CCombPanel构造抛Exception、回首页，未跳转。静态追真实LoadFile方法表/机器码发现路径XOR公式；旧0x461340实际ReadFls，明文头自解是编辑器技巧而非原生。新增标准库两布局存储修复助手（保留用户明文字节，原包只读、整包逐字校验、新包独占发布、不改script），23/23回归含真2.5.6/静态PE/存储安全探针、ruff通过。只修确定存储缺陷，实际用户两条状态/Windows/条款跳转仍待验；编辑器通用新增未修，详 §3.12。 |
| 2026-10-14 | 用户明确“你传网盘”，上传现有已校验 registration_phase2_diag1.zip 到 My Drive 根目录（ID `1YxoYNmpTejl7qk86K9ELg_b1bvYJcGk8`）。上传返回大小/MD5 与本地相等；未改权限/删除旧包，未再次下载核验。只换 script，不重导 interface，仍是卡屏诊断版、原生根因待最后阶段日志。详 §3.11。 |
| 2026-10-14 | 用户确认原第二期网盘脚本、同包两布局、卡屏为整窗无响应。新增 phase2-diag1：模块导入至原生布局/条款文本/表单逐段日志、会返回的 Python 异常回退及原子切页引用发布；原生阻塞仍未定位/不能靠 except 恢复。真2.5.6重建，14/14回归+ruff+Windows静态检查通过；旧版同一布局异常探针先失败，新版通过。新 script 对已发第二期仅4007负载改变，337/其余5000条全等，未改接口/布局/原包。详 §3.11 和注册目录诊断说明。未上传 Drive/改权限。 |
| 2026-10-14 | 用户确认编辑器“速度很快，新布局也找到了”，大包打开/新布局查找两项按该环境通过。新增反馈：第二期脚本点击申请会员卡屏。已定位 tools/registration 源码/337入口/4007注册模块，确认先条款 regterms 再表单 regform；原始 337 正规化字节码证实先隐藏主页再构造注册页，构造异常是候选原因而非本次已证实根因。需确认同一实际新包包含两张布局、脚本版本/卡屏形态及最小诊断。只读复核，注册回归12通过+1真2.5.6缺失跳过，原包/key SHA不变；本轮未改脚本/出包/上传。详 §3.11。 |
| 2026-10-14 | 用户反馈布局导入保存后重开找不到、资源编辑器打开大包变慢。确认 0.8.1 自定义路径仅本会话及打开前全量扫描两处缺口，修为 UI 0.8.2 QSettings 地址记忆/包根精确路径只读恢复、资源 0.4.2 索引先显示/全量识别后台化、过期回调/多选/读关闭互斥护栏；注册两完整地址同步字典。新增 10 条回归：资源 110/110、UI 196 通过+1 语料跳过，ruff/wincompat/bootstrap 绿、原包/key SHA 不变。未取得用户确切地址/文件，不按大小断言数据正确；真实 Windows 打开速度/游戏仍待验。修复 `f6e6e2a` 已推送；源码修复 ZIP 已上传 My Drive 根目录且大小/MD5 与本地一致（资源 162,019 B、UI 386,673 B）；详情/链接见 §3.10，旧包保留，分享权限未改。 |
| 2026-10-14 | 按用户要求打包上传两工具到 My Drive 根目录：资源 0.4.1 / UI 0.8.1 源码启动 ZIP（非 EXE），代码钉 `fe2e057`。ZIP CRC/逐文件字节/清单 SHA 验证通过；交付副本资源 97 通过+7 数据跳过、UI 191 通过+2 数据/语料跳过，ruff/bootstrap 绿；Google Drive 文件大小/MD5 二次核验与本地一致。包内说明含 Python/启动步骤和新增明文布局/Windows/游戏待验边界；未改分享权限、未附客户端资源或桩件、未构建 EXE/开 PR/合并。最终下载链接/完整哈希见 §3.9。 |
| 2026-10-14 | 两项新交互按授权实现：资源 0.4.1 可搜索/手填包内地址（实际存在/已识别路径，不造未知名）；UI 0.8.1 包根右键导入明文 .dlg、单文档待入包预览编辑、明确新增/替换清单和显式新增写包通道。保存成功优先重挂新包/登记会话地址，树重开按指定包取布局。新增明文存储/替换沿原 XOR 密钥，原包不动、不自动导图/接脚本。新增 30 条回归；资源 104/104、UI 192 通过 + 1 语料库跳过；ruff/wincompat/bootstrap 绿，锁定输入 SHA 不变。系统库桩仅用于沙箱离屏；Windows/游戏/新增原生编码布局加载未验。固定分支提交记录见顶端，未开 PR/合并/发布/上传测试包；详 §3.8。 |
| 2026-10-14 | 用户授权首期三项已实现：资源 0.4.0 全局增量撤销/重做（增删替换/还原与批量一步）、UI 0.8.0 修改前静态引用护栏/删除子树检查/零 Qt 布局诊断、双工具保存前改动清单。功能 `f224f16`、类型缓存代际修复 `bf2bfc3` 已推送固定分支；新增 67 条回归，UI 170 项（169 通过、1 缺语料库跳过）、资源 97/97，沙箱 offscreen 进程均退出 0；无桩件 UI 92 项（91 通过、1 跳过）、资源 97 项（74 通过、23 GUI 跳过）；ruff/wincompat 0、bootstrap 自检绿、原包/key DB 哈希不变。版本基线探针旧版两 FAIL、本版两 PASS；详情/已知边界见 §3.7。只生成新包，不改编译脚本、不自动接线；未验 Windows/游戏，未构建 EXE/开 PR/合并/上传测试包。 |
| 2026-10-14 | 用户授权修复两个编辑器：UI 0.7.1、资源 0.3.8，代码提交 `eeff8c4` 已推送固定分支 `arena/51e31d38-mxsj-tw-2022`，未开 PR/合并/发布。新增 30 条输出安全/原子失败/真名连续性/GUI 状态回归（UI 16、资源 14）；最初 12 条核心回归在旧实现上复现失败后再修复。行为变化：Ctrl+S/另存包都生成新包，拒绝源资源及别名，不再原位覆盖源包；UI 的未改条目发布前分块逐字节检查，不能以 span 相同替代。资源导出追加目录边界与全帧预检；保存后真名和网格按 entry_id 重建。完整离屏实测 UI 137 项（136 通过、1 缺完整语料库跳过）、资源 63/63，进程均退出 0；环境 Python 3.11.2 / PySide6 6.8.3 / Pillow 12.3，系统库桩件只用于沙箱 offscreen，不入库、不代替 Windows/游戏验收。无桩件 UI 核心 74 项（73 通过、1 跳过）、资源 63 项（53 通过、10 GUI 跳过）；两目录 ruff 0、wincompat 0/0/0、bootstrap 自检通过。锁定原包/key DB 哈希未变。更新 README/DESIGN，未修架构证据红灯、未构建 Windows EXE、未合并/发布或上传测试包。 |
| 2026-10-14 | 项目分析复核（`arena/51e31d38-mxsj-tw-2022`，基线 `fa13871`）：只读检查主要目录、实现与文档，未改业务代码、原包或证据。锁定 script.fls/key DB 的 SHA-256 均匹配；catalog 34/34、devkit 29/29；注册测试 13 项中 12 通过、1 因未设置 CPython 2.5.6 而跳过。架构 150 项仍为 1 FAIL + 1 ERROR；来源文件名核验 96/96（非玩法验证）；CSV `--check` 仍报 `E evidence changed; review required`。将地图/NPC 证据重生成至仓库外后递归逐字段比对，仅 `/inputs/shared_decoder/sha256` 变化（`7490dbab…` → `242543f8…`），未修复已提交证据。API/网页/编辑器 GUI/Windows/客户端联调本轮未执行；未启动 Mock、未提交/推送/发布。本轮仅更新本文，标明旧会话状态与当前检出事实的区别。 |
| 2026-10-14 | 注册第二期授权执行**已完成**：源码/原生布局/真实母版/回归测试/批量顺延方案/记账以提交 `22a3fab` 推送到固定分支 `arena/23e52686-mxsj-tw-2022`（未合入 master）；`registration_phase2.zip` 已上传 Google Drive，文件 ID `1FQjI8tiFSYAihlHUzwJN2GNNZWy5CBy7`，[下载](https://drive.google.com/file/d/1FQjI8tiFSYAihlHUzwJN2GNNZWy5CBy7/view)，24,189,000 B，ZIP MD5 `56c583afa4fa58b7fa8f47efb5a802c3`、SHA-256 `0541062f45a74bfbda99b62022d30c3929feb0e0979069d36b06d513d3cec97b`。上传返回的文件大小/MD5 与本地逐字节校验包一致，未改分享权限。只发第二期界面测试包，真实注册/查重/顺延/事务仍未实现；Windows 仍待用户按包内说明导入 `login/regterms.dlg` / `login/regform.dlg` 至 interface.fls 新包并实机验证。 |
| 2026-10-14 | 用户明确授权「提交推送上传」，注册第二期出货执行中。交付前重新跑 13/13 回归、ruff 0、wincompat 0 ERROR/0 WARNING；重建两张布局与 script.fls（SHA-256 `17a94c77…`），新包读回完整 marshal 比对及真 2.5.6 冒烟全绿，原 5000 条压缩负载全等。按工作区重新打包 `registration_phase2.zip`（24,189,000 B，MD5 `56c583afa4fa58b7fa8f47efb5a802c3`），逐文件解包字节比对和 ZIP CRC 通过；测试说明补充已定的「单条批量＋重名顺延」仍属待服务端实现规则。只交付原生注册 UI/校验/候选名单，不创建真实账号、不假报成功；Windows 新布局/勾选皮肤仍待用户实机。准备提交推送当前固定分支并上传网盘，完成后补编号。 |
| 2026-10-14 | 用户通过选项选定后续注册规则：**一条批量请求＋服务器跳过重名顺延**。请求带基础账号、数量 1/5、共用密码/邮箱及批次编号；五账号模式按原名、`_1`、`_2`…查找，最多 `_99` 且最终最长 16 位（14 位基础仅到 `_9`）。凑满五个才整批创建，凑不满就整批不创建；服务端唯一性/事务及同批重试返回原结果防止重复建五个；成功弹窗/登录预填使用服务器实际名单。单账号重名不擅自改名。**这是已定业务规则，不是已实现接口**：现运行源码仍不发送/查重/顺延，当前固定 pending 名单回调须在接口接通前调整，需补重名/耗尽/并发/重试验收。仅更新 README/STATUS，未改运行源码、未提交/推送/上传；选择方案不等于发布授权。本轮既有客户端离线回归复跑 13/13、ruff 0、wincompat 0/0（不作为顺延/事务/幂等服务端验收证据）。 |
| 2026-10-14 | 用户询问五账号的发送方式（连续五次/一次带标记）与重名顺延。核对现状：注册模块只在内存生成固定五份，不发数据、不查数据库、不顺延。已解释推荐的后续方案：单条批量业务请求（基础账号、数量 1/5、共用密码/邮箱、批次编号）由服务器统一查重和整批创建，回传实际名单，避免重试多建一组。发送方式/重名策略待用户选定；顺延必须守最终 16 位，14 位基础只到 `_9`、`_10` 超长，建议最多 `_99` 同时守长度上限，凑不齐则整批不创建。若定顺延，当前固定名单成功回调及登录预填须在接口接通前调整为服务器实际结果。**本轮未改运行源码、未实现接口、未提交/推送/上传**；上轮发布授权询问被跳过，不能视为授权。 |
| 2026-10-14 | 注册第二期增加用户点单的原生「註冊五個帳號」勾选（默认关闭）。用户通过选项确定基础账号上限 14 位，单账号仍 16 位；候选依次为原账号、`_1`~`_4`，共用密码/邮箱；下划线只作为自动后缀，切换不截断已有输入。已取回服务条款 `service.dlg`（Drive `1KaFXbFxU-VOJ5OJ0UIS7rINmn9uhJagS`，2984 B，SHA-256 `820f09a8…`）逐字拷为 regterms；五份真实模板重新取回并钉 SHA 防乱码、布局写入保留 Big5 文案/GBK 皮肤原字节。checkbox 采用原生 `CIMGCHECKBOX(interface.CImageCheckBox, 锚点, parent, 皮肤, True, 4)`，反汇编实证 LeftUp 先发消息再自动翻转，所以 manual=True 只翻一次；皮肤源于原 ui_res_style1 的登入注册勾选框。完成回调仅在已发送真请求且完整名单确认后列出五个账号（部分/重复/过期/旧表单回覆不能报全成功）；**本包无服务端接口，仅列待注册候选并明示尚未注册**。13/13 回归、ruff 0、wincompat 0/0；打包器增加禁止覆盖输入/硬链接别名、完整 marshal 往返相等断言与新包读回模块冒烟，原 5000 条压缩负载全等；script.fls SHA-256 `17a94c77e4cda673023f0e17221edb73f789183a0af0d4fcd5c6a1d3b651e0b2`、regform SHA-256 `8eeb7568…`。候选 zip 已本地打好并逐文件解包比对（MD5 `9220555bb808346eac38170c17c2c3dd`），未提交/推送/上传，等待授权与 Windows 实机。 |
| 2026-10-14 | 注册第一期 1.1 实机复测**全通**（用户确认）。第二期推进：用户回传 `reg.zip`（chgpwd/reg1/reg2/confirm 四张布局，已存 `tools/registration/templates/`）并拍板：注册协议直接拷贝服务条款 dlg、旧注册页风格与现行严重不符必须改；帐号规则与密码同口径（6~16 字母数字）、表单三按钮（上一步/确认注册/返回首页）。已完成：`build_regform_dlg.py` 从 chgpwd.dlg 派生 `regform.dlg`（登陆套件、四输入行、三按钮，经 UI 编辑器 codec 解析校验）；脚本 v2 改协议页照 `loginin.CServiceMessageDialog` 范式（regterms/loc_msg）、表单四框 + CPwdEdit 式输入限制 + 提示区，新 script.fls SHA-256 `5bfe2d797c4e5ce722f55152125fb91935c09afa957ffffb96e06e3056378829`、2.5.6 冒烟全绿。只差用户导出 `login/service.dlg`（见 §4）生成 regterms.dlg 后打包上传。 |
| 2026-10-14 | 注册第一期实机首测回報：条款页可打开、能进表单页、拒绝/上一步可返回；点「下一步」无反应。定位：原版脚本所有 UI 文案是 Big5 字节串，1.0 传 unicode 给 `ShowNewMessageBox`，其内部字节拼接解码失败、异常被客户端吞掉。1.1 修复：源码全部 UI 文案改 Big5 字节字面量（`MSG_*` 常量与原版逐字一致）、提交路径加 try/except 兜底弹框、表单消息与提交阶段写诊断 `photo\register_diag.txt`；构建器断言桩文案为 Big5 字节且不以 unicode 残留，2.5.6 冒烟全绿（含诊断文件断言）。新产物 `out/script.fls` SHA-256 `a90f0b62ceede2d6ebf35784eb52bf7992d6f75ff6c608016bbd88811cf9ef65`；1.1 包已上传网盘（Drive `1Hhnp_75jfCHlIZm5_qKYjWoUQ4GmT4DE`，zip MD5 `8abb9230886018f0cbd24199a15b58f4`，含测试说明），待用户实机复测。 |
| 2026-10-14 | 注册原生重做**第一期测试包建成**（`tools/registration/`，产物 `out/script.fls` SHA-256 `f062b8e9c1819d63fd4e4662bb3d974b5d0349a612c80b2c724b205cf0efe5fe`，git 忽略不入库）：新源码 `register.py`（条款页 `CRegTermsPanel`/表单页 `CRegFormPanel`/`CConfirm` 原样保留/对旧运营商网络名零残留断言）经自建 CPython 2.5.6 编译后整模块替换条目 4007，首页条目 337 打与 v1 已实机验证逐字节相同的 9 字节谓词补丁（其余 5000 条负载逐字节不变，构建器自动校验）；另用真 2.5.6 解释器加桩件把「开条款（servicedata 缺失走占位条款）→同意→表单（验证码/2980 占位已隐藏）→四种校验提示→桩提示→回条款/回首页→CConfirm 确认流程」全走通（`harness.py2`）。已知差异（README 记账）：本期表单沿用旧 reg2 版式=邮箱即帐号，独立帐号框待第二期改 layout；条款为占位文本（原 `servicedata` 模块不在本版 script.fls 内）。已上传网盘（Drive `1JS4-sYtKyZv6ANbJkk4m7TPebX3fivtY`，zip MD5 `273de8b9013ccc13d30b2460486c20d2`，含测试说明），待用户在已还原的测试副本实机验证；第二期等模板导出后给表单加帐号框并定版条款。 |
| 2026-10-14 | 注册原生重做开工前置全部就绪：① 用户确认测试副本已还原原包，并拍板表单字段=账号/密码/确认密码/邮箱、先过会员条款页、点确认注册后的桩文案=「伺服器尚未開放註冊，請稍後再試」；② 沙箱自建 CPython 2.5.6 成功（GitHub 源码 `-std=gnu89` 编译），玩具模块实证「自写 Py2.5 源码→编译→`pack_and_encrypt.py pack-script`→解密转译」往返无损，脚本重打包不再依赖 Windows；③ 加载链确认：台服走 `innerversionfun.LoadUIFileData`（原生 `C_sys.LoadFile` 解密后脚本层 `exec` 布局文本），新 `.dlg` 的 XOR 密钥由原生侧按明文头自解（与每条目随机密钥的实测一致），第一期先复用旧 `login/reg1.dlg`/`login/reg2.dlg`（只换脚本、不动 interface.fls），布局定版待用户导出模板（见 §4）。下一步：重写 `login/register.py`（条目 4007）+ 沿用 v1 已实证首页入口补丁，出第一期测试包。 |
| 2026-10-14 | UI 编辑器 0.7.0（脚本联动第一期 + 控件树锁定图标；Drive `18Tzk1T5KbDA4VhosnaRHrbwydwOSTwqJ`）：控件树改为两列、每行第二列小锁（默认开锁图标，点切换、与画布锁定双向同步；顺带修好控件树点击选中的反查失效）。新增索引生成器 `tools/script_link/`（基线转译+marshal/字节码挖掘 4,987/5,002 模块、2,920 布局、生成用时约 10 秒、5 条合成测试）；编辑器侧 `core/script_index.py` 查询层 + 随包 `data/script_index.json`；打开布局自动关联脚本（状态栏报数、左栏新增「脚本」页、点控件名回画布选中），代码现造按钮按真皮肤渲染（`_paint_code_skin`，取不到图回落占位）。119 通过 + 1 跳过、ruff 0、wincompat 0/0、从 zip 复跑绿；真包皮肤效果待用户用真实 `interface.fls` 验证（仓库无此包）。联动后续：脚本源码查看/编辑、加控件自动接线、脚本写回（§5 第 2 项），注册界面原生重做为第一个实战。 |
| 2026-10-14 | 用户决定暂缓：条目 1163/52226 的定点补解码先放一放（工具侧已万事俱备：0.3.7 导出解码失败条目必落原始 `.bin`，只差用户重导回传），优先转攻**注册界面原生重做**（§5 第 2 项 ⑤）。恢复 1163 线时第一步仍是导出 `interface_1163.bin`/`interface_52226.bin` 回传。 |
| 2026-10-14 | 资源编辑器 0.3.7（Drive `1ytgJ6Li81kdC0tA5VCrGJDwSvEfafnLE`）+ 用户回传 `1163b.zip` 复核：1162 导出的 PNG 是正常精灵帧（卷轴图局部）；52226 点击预览报 totalLines 不符、1163 报头解析越界，但两条**仍未随包回传**——点击只是预览报错，导出是独立动作，0.3.6 起导出解码失败条目必落原始 `.bin`（已用同形态样本在导出器实测），已请用户对 1163/52226 用右键「导出该条/导出选中」重导；用户另问 sound.fls 不能在编辑器播放——属实为缺功能（旧版只给 Hex 预览），0.3.7 新增音频识别与预览播放：`core/codecs/wav.py` 解析 RIFF 头（PCM 按字节数、GSM 每 65B 块 320 样本、IMA 每 1024B 块 2041 样本，fact 只兜底，与 libsndfile 实测一致），预览页可播放/停止/拖进度，解码走系统多媒体后端（沙箱无后端时降级为只看信息、已实测不崩；Windows 的 FFmpeg 后端对 PCM/IMA/GSM 一般可解，GSM 仍以实机为准）；49/49 绿、ruff 0、wincompat 0/0、zip 包内复跑通过。 |
| 2026-10-14 | 资源编辑器 0.3.6（Drive `19CbOVerFBV8qvT4ahQG6h7P7wEfRZ4k0`）：用户回传 `1163.zip` 分析定版——① 条目 1163 本体仍未拿到：旧导出遇精灵解码失败整条丢弃（`export_entries` 只记 failed 不落文件），0.3.6 改为回退原始字节 `.bin`，并让无真名的 XOR `.dlg` 按内容识别导出解密明文；② `item.fls` 四条样本（225/236/625/639）是新精灵变体 **T4/T5**：与 I0 同头同 token 文法、无调色板、像素为 3 字节 RGB（T4 用 u8 行长、T5 用 u16），四条均 `data_end==len` 且渲染为武器/翅膀/图鉴图逐张核对，资源与 UI 两边解码器已同步支持；③ `interface.fls` 的 `0x1C` 头条目（0016/0042/0047/52227）是 **Spine 骨骼二进制**（版本 3.4.02/3.6.52、BE 浮点、`./images/`、root 骨骼、附件名 `tx_*`/`Btxx_*`），不是坏精灵；用户导出的 interface_52227 与 0.3.4 校验报告的同号精灵对不上，疑保存新增条目排序插入造成校验下标整体偏移，待 0.3.6 发布后重导 1163 及相邻条目定点补解码；④ 其余样本定性：8 条 interface 无名条目是路径字典未收录的 XOR `.dlg`（已全部解密核对）、sound 大条目是 RIFF WAV（PCM/GSM610/IMA-ADPCM）、小条目是 GBK 重定向文本、`dialog/heroreplace.dlg` 正常。sound 条目导出自动落 `.wav`。44/44 绿、ruff 0、wincompat 0/0、zip 包内复跑通过。 |
| 2026-10-14 | 三个编辑器补齐工具约定 ①②：`map_editor` 新增 `bootstrap.py` + `启动地图编辑器.bat`、`tests/test_bootstrap.py`，ruff 74→0（定点改：E501 换行、`itertools.pairwise`、`zip(strict=True)`、`Iterator` 真实导入、`assertRaises(FlsError)` 等），`build.bat` 改名 `build_exe.bat` 并重写为纯 ASCII，spec 补 `exclude_binaries`，修 `test_cli_and_isolation` 读到开发者真实配置的隔离漏洞；`resource_editor` / `ui_editor` 各加 `build_exe.bat`、`<tool>.spec`、`run.py`、`requirements*.txt`、`.gitignore`（`build/` `dist/` `启动日志.txt`）。沙箱用桩库跑通 Qt offscreen：三套测试 88 / 37 / 92+1 跳过全绿；三份 spec onedir + onefile 干跑通过。**Windows 实机未验**（§3.5 ③）。 |
| 2026-10-14 | 用户实机确认：UI 编辑器 0.5.3 在真实 `interface.fls` 上加图存包成功、使用无报错——P0 写回修复 + 0.5.3 保存明示两轮闭环（§4 该行 UI 侧销项；资源编辑器同路径与 EXE 路径仍待验）。 |
| 2026-10-14 | 用户立「原生优先」规矩并写入 `AGENTS.md` §4（第 12、13 条）：原生能实现的必须按原生规范做；原生做不到、只能用替代方式的，必须反复向用户确认并获明确同意才能做。同时用户判定注册预览 v3.3 不规范（代码 overlay 拼控件、整图烤字按钮、包外散图）并作废——待其在 Windows 测试副本还原原包（`script.fls.before-registration-preview` 改回，SHA-256 `8b6e9266…`）并移除 `photo/registration_preview_v3`，勿再分发 v3/v3.2/v3.3。重做方向已定（§5 第 2 项）：注册界面按原生重做（原生 `.dlg` + 原生脚本套路，提交先留桩），与 UI 编辑器 × script.fls「一步到位」联动合并为一条线，注册界面为第一个实战。本轮发布：UI 编辑器 0.6.0（右键/复制粘贴/等比/锁定，Drive `1PHmkw04IIwRCdFT9Q58qfgxRS9WLrKUN`，MD5 `dd661dc6e60222c33a5ab4e0b6d0fd05`）与资源编辑器 0.3.5（工具栏，Drive `1ylUzM_i82-lzfaEp3WVx37gsNtNie4bo`，MD5 `ef29abe85fd1b7d7f1e0e00620f7eb31`）已提交推送并上传网盘。 |
| 2026-10-14 | 两编辑器补常用功能（用户点单）：资源编辑器 0.3.5 新增顶部图标工具栏（目录/打开/刷新/保存/另存/导出/导入/精灵/删除；图标在上+两字短名、与菜单共用同一动作、置灰同步，规格对齐 UI 编辑器；现画图标 `gui/icons.py`），40/40 绿。UI 编辑器 0.6.0 画布控件右键菜单 + 复制/粘贴/删除（Ctrl+C/Ctrl+V/Delete 走系统剪贴板 MIME，多选整组、粘贴偏移 16px 不重叠、整组一步撤销、删除改进为多选并汇总子控件数确认；焦点在文本框时三键回落文本编辑不误伤；model 新增 `insert_widget`）；追加「等比」工具栏开关（canvas `aspect_resize`：角把手按相对变化大的一轴定比例、边把手以中心为锚、最小 8px 保比例、Shift 临时等比）与「锁定」控件开关（工具栏/右键菜单/Ctrl+L：锁后拖不动/缩不了/删不掉、对齐分布绕开、父锁不挡子；`Widget.locked` 仅内存态不写 .dlg、不标脏不进撤销，撤销重建后按序号路径恢复锁定），112 通过 + 1 跳过绿。两边 ruff 0、wincompat 0/0；Windows 手感待用户确认。 |
| 2026-10-14 | 资源编辑器 0.3.4（用户实机反馈）：真实 interface.fls（53,555 条）仅新增一条无关条目，保存却被写后校验的逐条试解码拦下——条目 1163（头解析越界读）、52227（totalLines 与帧高和不符）是原包自带精灵，本机解码器未覆盖其变体，字节并未经手改动。改判责任：字节逐字比对仍是硬闸门，试解码只对本次改动/新增（`PackDocument.changed_indexes()`）的条目拦截，未改动者记 `sprite_undecodable` 在保存日志提示。补两条回归（未动不拦、改了必拦），39/39 绿。解码器缺口待样本：请用户从原包导出条目 1163/52227 的原始字节后再定点补。 |
| 2026-10-14 | UI 编辑器 0.5.3（用户 0.5.0 原生反馈两缺陷）：① 关闭窗口中画布补发缩放信号时 `_on_zoom_changed` 只判 `hasattr`，标签 C++ 对象已删仍 `setText` 抛 `RuntimeError: libshiboken ... already deleted`——改用 `shiboken6.isValid` 把关；② 「图片保存成功却没存进去」：挂账新图仅当被当前布局引用才随包写（设计如此），旧成功弹窗不报实际写入数，未引用被静默漏过、且保存默认生成 `原名_patched.fls` 新包，用户重开原包自然还是原条数——弹窗改明示新包路径、条目总数、实际写入/替换数，有未引用挂账图时点名警告（报告新增 `staged_unreferenced`/`entries_after`）。补两条回归测试，94+1 跳过全绿。用户侧用 0.5.0 时另请注意：务必升级到含 P0 写回修复的版本再对真实包加图。 |
| 2026-10-14 | 工具开发约定：新增 `docs/PYTHON_TOOL_CONVENTIONS.md`（PEP 8 + 模块化、GUI 一律 PySide6、必须有 `bootstrap.py` 自检启动与 `build_exe.bat`、Linux→Windows 交付检查）与 AGENTS §5 摘要；新增 `tools/devkit/check_windows_compat.py`（Windows 兼容静态检查，29 测试）、根 `ruff.toml`、`.editorconfig`、`.gitattributes`（`*.bat` CRLF）；`map_editor/pyproject.toml` 补 ruff 配置，两个编辑器的 ruff 规则加 `W`；修 Windows 必坏项（`bytecode_58_<module>.bin` 改名、bat CRLF、`build.bat` 加 `chcp 65001`）。差距清单见 §3.5。 |
| 2026-10-14 | 文档整理：新增 `AGENTS.md`、`docs/STATUS.md`、`docs/archive/`（归档 14 个过期快照：根目录 `AGENT_HANDOFF.md`、`work/` 下 10-09/10-10 交接与分派文档、地图编辑器交接报告、`CLIENT_DATA_AGENT_HANDOFF.md`、4 份 route-scope 残留）；v3.3 事实表抽成 `tools/client_patches/V3_3_DELIVERY_AND_ACCEPTANCE.md`；刷新 `README.md`（补两个编辑器、修正测试计数、状态移到本文）、`server/README.md`、`tools/client_patches/README.md`、`work/.../INDEX.md`。未改任何代码、测试、数据与二进制。 |
| 2026-10-13 | 资源编辑器 0.3.3 / UI 编辑器 0.5.2：写回目录不变量 P0 修复；decoder 分段参数修复（引发 §3.1）。 |
| 2026-10-12 | PR #26/#27 合入 master：复核链、注册 UI v3.3、网关设计、地图编辑器及其修复。 |

## 7. 如何更新本文

每轮结束：改快照日期 → 更新 §1 分支/基线 → 用**实际跑过**的结果更新 §2（没跑就写“未执行”）→ 增删 §3/§4 → 调整 §5 → 在 §6 追加一行。不要删历史行；超过一屏时把旧行搬到 `archive/`。
