# 项目当前状态（STATUS）

> **快照日期：2026-10-14**（Asia/Shanghai）。本文是唯一的“当前状态”文件：每轮工作结束时更新本文，不要再新建交接文档。
> 长期规则见 [`AGENTS.md`](../AGENTS.md)；项目总览见 [`README.md`](../README.md)；历史快照在 [`archive/`](archive/README.md)。
> 旧会话组件实测不代表本轮全部复跑。当前编辑器增强会话固定分支 `arena/51e31d38-mxsj-tw-2022`：会话起始基线 `fa1387162e60625c0a064403647abe8f65155acb`（PR #31），本期在安全修复 `9ee68e3` 上继续。功能代码 `f224f16`、类型缓存代际修复 `bf2bfc3` 已推送；未开 PR/合并/发布。本轮只复跑两编辑器、启动自检、Windows 静态检查与锁定输入核验；其他组件表格仍为历史证据。本轮续增资源 0.4.1 路径下拉与 UI 0.8.1 包树右键导入，提交记录见本分支顶端；当前功能与测试范围见 §3.7 / §3.8 / §6。

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
| 逆向研究（`notes/`, `work/`） | 结案：双 VM opcode 表、0SLF 目录/路径哈希、`.dlg` 2,706/2,901、协议号表 412 条、帧续读 2 字节 | 稳定；未决项见 AGENTS §7 | 锁定输入 SHA 匹配 |
| 注册 UI 补丁（`tools/client_patches/`，历史） | v3.3 已作废 | 用户判定旧 overlay/整图烤字按钮/包外散图不符合原生规范，**勿再分发 v3/v3.2/v3.3**；新实现见下行 | 90/90 仅历史证据，不作为新实现验收依据 |
| 注册原生重做（`tools/registration/`） | 第二期候选：现行风格 + 五账号勾选 | 第一期 1.1 已实机全通。第二期服务条款布局已收齐并逐字拷贝为 `regterms.dlg`；`regform.dlg` 照现行 chgpwd 风格生成（四框/三按钮/原生「註冊五個帳號」）。默认单账号 6~16 位；用户选定五账号模式基础账号 6~14 位，生成原账号及 `_1`~`_4`，密码/邮箱相同。**无真实注册接口**：仅生成候选、明示尚未注册；全成功提示回调已预留但桩不调用。后续已定单条批量＋服务器重名顺延，真实接口/顺延结果回调调整未实现。新 script.fls SHA-256 `17a94c77…`；第二期源码提交 `22a3fab` 已推送、测试包已上传（Drive `1FQjI8tiFSYAihlHUzwJN2GNNZWy5CBy7`，ZIP MD5 `56c583af…`）；Windows 未验（见 §4） | **13/13** 回归通过（含真 2.5.6 编译/运行桩件）；新包读回完整 marshal 逐字节相等、再冒烟全绿；只改 337/4007、其余 5000 条压缩负载全等；ruff 0（嵌入式 2.5 文件仅豁免 UP）；wincompat 0/0 |
| 只读复核链（catalog / API / web） | H/I/J 已收尾 | 可运行，只读 | catalog 34/34；review_api 27/27；验收套件 68 通过 + 2 跳过（需 uvicorn 在 PATH 上）；网页未装 node_modules 未跑 |
| 地图编辑器 | 一期 + PR #27 修复 + 10-14 补齐约定（`bootstrap.py`、`启动地图编辑器.bat`、`build_exe.bat`、ruff 0） | GIRB 300/429 扇区仍解不出（明确失败）；Windows EXE 未实机构建/冒烟 | **88/88** 通过（含 6 条 bootstrap 测试；GUI 冒烟在沙箱用 Qt offscreen + 桩 libGL 跑过）；ruff 0；wincompat 0/0 |
| 资源编辑器 | **0.4.1**：可搜索/手填资源路径，保留 0.4.0 撤销/清单 | 仅当前包已识别且存在的非目录路径；已有默认取消替换确认；0SLF 不编造未知名字；原包不动。Windows/游戏未验 | **104/104**（Qt offscreen + 沙箱系统库桩件）；无桩件 77 通过 + 27 GUI 跳过；ruff 0；wincompat 0/0/0；bootstrap 自检通过 |
| UI 编辑器 | **0.8.1**：包根右键导入 .dlg，保留 0.8.0 引用护栏/诊断/清单 | 单文档新增/替换、待入包预览编辑；显式新增布局安全通道；成功后新包重挂/会话路径登记，树读取锁定指定包。新增明文布局/Windows/游戏未验 | **192 通过 + 1 语料库跳过**（共 193，Qt offscreen + 沙箱系统库桩件，退出 0）；零 Qt 的 12 个核心测试模块 100 通过 + 1 跳过且未 import PySide6；ruff 0；wincompat 0/0/0；bootstrap 自检通过 |
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

## 4. 等待外部输入

| 事项 | 等谁 | 阻塞什么 |
|---|---|---|
| 两个编辑器在真实 Windows + 真实 `interface.fls` 上的实机验证（新图写包后进游戏能否显示） | 用户 | 编辑器“可用”声明 |
| 注册第二期 Windows 实机：两张新布局按完整游戏路径导入 interface.fls 新包，验证协议/四框/三按钮/勾选皮肤与点击；新增明文 dlg 能否由原生加载 | 用户（取得测试包后） | 二期可用声明；离线通过不等于实机验收 |
| 真实注册接口与五账号整批成功回覆 | 后续服务端工作线（未开工） | 已定单条批量＋重名顺延（最多 `_99` 且最终 16 位，整批五个/同批重试不重复创建）；真实接口/固定成功回调调整/服务器验收未做，本阶段继续留桩，不能假报成功 |
| 是否合入 master、是否清理二进制 | 用户授权 | — |

## 5. 下一步（优先级）

1. 修 §3.1（单独一个小提交），让架构套件与 `--check` 回绿。
2. **UI 编辑器 × script.fls 联动 + 注册界面原生重做**（用户 2026-10-14 定的方向，合并为一条线）：① ✅（0.7.0）离线索引生成器 `tools/script_link/build_script_index.py`：不跑反编译、直接转译+解析 Py2.5 marshal/字节码挖掘，4,987/5,002 个模块挖成（15 条基线转译失败未做边界修复），关联 2,920 个布局、13,162 个被取用名、19 个高置信代码皮肤锚点；随包 `script_index.json`（1.3 MB，查询层 `core/script_index.py`）。② ✅（0.7.0）代码现造的按钮（如 login 的占位锚点）按真皮肤渲染，不再显示默认占位（`painters._paint_code_skin`；皮肤覆盖仅限高置信工厂模式，其余代码控件仍占位）；左栏「脚本」页显示引用模块/被取用控件/锚点与皮肤详情，点名字回画布选中；打开布局状态栏报关联计数；③ ✅（0.8.0）改名/删除子树引用护栏、静态布局诊断与保存前清单（详 §3.7）；加控件自动接线（GetObject 认领 + OnMessage 骨架 + 空闲消息号）仍未实现；④ 脚本可在编辑器内查看/编辑，保存时布局与脚本一起出新包（写回管线 `tools/decompiler/pack_and_encrypt.py` 已验证往返逐字节一致；编辑后源码编译依赖 CPython 2.5.6——**2026-10-14 已在沙箱从 GitHub 源码自建成功**，自写源码经编译→混淆→5 段 XOR 加密→重打包→解密→转译往返全通（代码对象/繁体 unicode 常量/控制流一字不差），「仓库侧打包」路线打通，不必依赖 Windows）；⑤ 第一个实战：注册界面按原生重做（原生 `.dlg` + 原生脚本套路，参照 `chgpwd` 类原生表单；提交先留桩并明示未接通；用户已定字段/条款页/桩文案，见 §6）。硬边界：546 个 stub + 12 个转译失败的脚本无源码、不可联动编辑，须明确标记；写脚本前先拿无害小改动做真机验证。
3. 判定 §3.2，统一 `notes/` 与编辑器文档。
4. 两编辑器新功能先在客户端副本上复核（新增路径下拉、包树右键导入/替换、连续新包导入和新增明文布局加载）：撤销/重做混合批量、引用取消/确认、诊断定位/刷新、保存清单取消与新包读回，特别检查保存后新图解析器来源迁移；严禁覆盖原包。三个编辑器在 Windows 实机跑 CONVENTIONS §5.3 冒烟（启动 bat → `build_exe.bat` → 双击 EXE），把结果回填 §2 / §3.5；沙箱侧 10-14 已把完整测试（含 GUI 组）跑绿，不再需要「有桌面的机器跑测试」这一步。
5. 二进制清理（需授权）与 LICENSE/权利说明。
6. 服务端第一条真实链路（网关 + 账号 + 区服 + PostgreSQL），按 `server/docs/GATEWAY.md`、`INTERFACES.md` 开工；在此之前不要再堆设计文档。

## 6. 最近变更

| 日期 | 变更 |
|---|---|
| 2026-10-14 | 按用户要求打包上传两工具到 My Drive 根目录：资源 0.4.1 / UI 0.8.1 源码启动 ZIP（非 EXE），代码钉 `fe2e057`。ZIP CRC/逐文件字节/清单 SHA 验证通过；交付副本资源 97 通过+7 数据跳过、UI 191 通过+2 数据/语料跳过，ruff/bootstrap 绿；Google Drive 文件大小/MD5 二次核验与本地一致。包内说明含 Python/启动步骤和新增明文布局/Windows/游戏待验边界；未改分享权限、未附客户端资源或桩件、未构建 EXE/开 PR/合并。最终下载链接/完整哈希见 §3.9。 |
| 2026-10-14 | 两项新交互按授权实现：资源 0.4.1 可搜索/手填包内地址（实际存在/已识别路径，不造未知名）；UI 0.8.1 包根右键导入明文 .dlg、单文档待入包预览编辑、明确新增/替换清单和显式新增写包通道。保存成功优先重挂新包/登记会话地址，树重开按指定包取布局。新增明文存储/替换沿原 XOR 密钥，原包不动、不自动导图/接脚本。新增 30 条回归；资源 104/104、UI 192 通过 + 1 语料库跳过；ruff/wincompat/bootstrap 绿，锁定输入 SHA 不变。系统库桩仅用于沙箱离屏；Windows/游戏/新增明文布局加载未验。固定分支提交记录见顶端，未开 PR/合并/发布/上传测试包；详 §3.8。 |
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
