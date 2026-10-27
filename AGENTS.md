# AGENTS.md — MXSJ_TW_2022 接手指南

> 给任何 AI Agent / 新成员的**长期有效**入口：只写规则、地图、命令和红线。
> “现在红什么、下一步做什么、谁在等谁”这类会过期的信息**只**写在 [`docs/STATUS.md`](docs/STATUS.md)，每轮工作结束时更新那里，不要改这里。

## 0. 这是什么 / 不是什么

- 围绕《夢想世界》台服客户端 **v2.27.2**（多益网络）的逆向研究 + 工具链 + Python 私服重建。仓库根目录**就是一份游戏安装目录**，上面叠加了工具与文档。
- **不是**可游玩的服务端，也**不是**已验收的客户端发行版。共享服务端已有账号／会话／角色元数据的 SQLite 本地基础（`local_server/` 入口），其余主要为契约与设计，尚无客户端监听／进图或 PostgreSQL 实现；根目录 Mock 已有本地交互模拟，但不是正式服务。
- 项目原则：**能展示 ≠ 能运行，能运行 ≠ 正确，测试通过 ≠ 原生验收完成。** 所有完成声明都要有范围、版本和可追溯证据。

## 1. 开始前的 60 秒

> **Arena.ai Agent Mode 必看**：本仓库曾多次出现临时环境不可用，以及HEAD/索引回旧版但新工作文件仍在的状态。开工/恢复/交接先读 [`docs/ARENA_SANDBOX_RECOVERY.md`](docs/ARENA_SANDBOX_RECOVERY.md)。预防靠阶段提交推送、核远端完整OID、记录可复现环境；恢复先保文件、核远端、逐路径证明差异，不能直接reset hard/clean、删.git或覆盖仓库根，也不能把dirty误判为前人没提交。检查点模板见 [`docs/templates/AGENT_CHECKPOINT.md`](docs/templates/AGENT_CHECKPOINT.md)。

1. 读本文 → 读 [`docs/STATUS.md`](docs/STATUS.md)（当前状态、红灯、待办）→ 读你要碰的子目录自己的 `README.md` / `DESIGN.md`。
2. `git status --short && git branch --show-current && git log -5 --oneline`。看到 untracked 目录**不要删**，看到旧 HEAD **不要覆盖**：先对比远程再决定（历史上发生过快照回退）。
3. 核对锁定输入未被改动：
   ```bash
   sha256sum data/script.fls tools/decompiler/script_fls_keys.json
   # 8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72  data/script.fls
   # 43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb  tools/decompiler/script_fls_keys.json
   ```
4. 本地克隆可能是 shallow（深度 2）；需要历史时用 `gh api repos/a565551313/MXSJ_TW_2022/commits?sha=<branch>` 或 `gh pr list --state all`。

## 2. 目录地图

| 路径 | 是什么 | 入口文档 |
|---|---|---|
| `AGENTS.md` / `README.md` / `docs/STATUS.md` | 规则 / 项目总览 / 当前状态 | 本文 |
| `docs/archive/STATUS_HISTORY.md` | 原 `docs/STATUS.md` 的历史部分（§3 红灯 3.1–3.82、§4–§7 与历史轮次条目），2026-10-27 拆出；**原 §编号未改**，每个 §3.x 有显式锚点 `s3-3-x` | [归档索引](docs/archive/README.md) |
| `docs/archive/` | 已被取代的历史快照（只读，有横幅） | [`docs/archive/README.md`](docs/archive/README.md) |
| `notes/client_binary_reversibility.md` | 客户端 exe/dll 的可逆性边界（逐节熵、RTTI、导出）与三条路的成本；§6–§7 是启动器 `.rsrc` 抽取结果与「资源包主体在 `data/*.fls` / `update.ini`」的分界；**原生符号"搜不到"不等于"不存在"** | `notes/opcode_mapping_and_decompilation.md` |
| `docs/DECOMPILE_CORPUS.md` | 全量反编译语料（79 MB / 5,517 份 `.py`）**要不要建、怎么建**：30 秒决策表、实测过的重建配方、4 个已复现的坑 | [`notes/opcode_mapping_and_decompilation.md`](notes/opcode_mapping_and_decompilation.md) §4.5–§4.6 |
| `docs/PYTHON_TOOL_CONVENTIONS.md` | Python 工具 / 编辑器开发约定（PEP 8、PySide6、自检启动脚本、一键 EXE、Windows 交付检查） | 本文 §5 |
| `notes/` | 逆向**结案**笔记：双 VM opcode 表、0SLF 路径哈希与 `.dlg`、游戏数据、[mxmain RTTI 类图与虚表清单](notes/mxmain_rtti_class_map.md)（352 个类／305 张主虚表／329 条 locator／继承链，工具 `tools/data-parser/mxmain_rtti.py`） | 各文件自述 |
| `work/dream-world-connect-login-map/` | 早期研究区（297 份笔记、证据、报告、专项工具）；2026-10-12 客户端研究快照 = `report/client-status-20261012.md`，不替代当前 STATUS | [`INDEX.md`](work/dream-world-connect-login-map/INDEX.md) |
| `tools/README.md` / `tools/DEPENDENCIES.md` | 工具生命周期、推荐入口与运行／证据／说明三类依赖；移动或淘汰前必读 | [工具索引](tools/README.md)、[依赖清单](tools/DEPENDENCIES.md) |
| `tools/decompiler/` | 双 VM 字节码反编译、5 段 XOR 重打包；`output/` 是反编译文本（**不准确、不可执行，只作线索**） | `notes/opcode_mapping_and_decompilation.md` |
| `tools/data-parser/` | `universal_fls_tool.py`、`mx_path_hash.py`、`extract_dlg.py`、`i0_sprite.py`、`pe_resource_dump.py`（从 exe/dll 的 `.rsrc` 抽皮肤/光标/版式/字串）、`skin_label_patch.py` + `pe_resource_patch.py`（皮肤改字并原位写回）、精灵格式说明 | `I0_SPRITE_FORMAT.md` |
| `tools/client_patches/` | 混合专题：注册 overlay v3/v3.2/v3.3 已停用；内置 UI 列表旧 v1/v2 暂停，v3 为未原生验收源码参考；不可整体判废 | [`分专题状态`](tools/client_patches/README.md) |
| `tools/devkit/` | 开发自检工具箱：`check_windows_compat.py`（Windows 兼容静态检查，交付前必跑）、`check_doc_versions.py`（顶层文档的版本号 vs 各组件 `pyproject.toml`，防版本漂移）、`vendor_core.py`（`mx_common/` → 编辑器 `core/` 的共享核心分发器） | [`README.md`](tools/devkit/README.md) |
| `tools/data-export/`、`tools/data_browser/`、`tools/dis_v43/`、`tools/*.py` | 历史数据导出/浏览/反汇编工具，仍可用但不是现行复核入口 | — |
| `script_editor/` | 双 VM 脚本恢复候选、编辑／编译／新包验证；Git 不含完整运行时发行材料 | [`README.md`](script_editor/README.md) |
| `script_manual/` | 只读脚本目录、有限说明、专题和摘要绑定审核 | [`README.md`](script_manual/README.md) |
| `mx_common/` | 编辑器共享核心**唯一真源**（`mxhash.py`、`native_layout.py`、`output_paths.py`、`sprite_format.py`）；编辑器里的同名文件是 `tools/devkit/vendor_core.py` 生成的副本，**改真源**再用 `--write` 分发 | [`README.md`](mx_common/README.md) |
| `resource_editor/` | `.fls` 资源包浏览/编辑器（PySide6；core 无 Qt） | [`README.md`](resource_editor/README.md)、`DESIGN.md` |
| `ui_editor/` | `.dlg` 布局可视化编辑器（PySide6；core 无 Qt） | [`README.md`](ui_editor/README.md)、`DESIGN.md`、`notes/ui_editor_phase2_design.md` |
| `map_editor/` | 地图解析/渲染/导出 + GIRB 碰撞解码（PySide6 GUI 可选） | [`README.md`](map_editor/README.md)、[`PR25_REVIEW.md`](map_editor/PR25_REVIEW.md) |
| `local_server/` | 共享服务端 SQLite 本地启动配置／操作员控制台；无客户端改包或网络监听 | [`README.md`](local_server/README.md) |
| `server/src/mxsj_server/` | 共享服务端：账号／角色第一阶段实现，其余主要为契约；不得把本地控制台称作可进图服务 | [`server/README.md`](server/README.md)、`server/docs/*.md` |
| `server/src/mxsj_catalog/` + `server/apps/review_api/` + `server/apps/review_web/` | 只读静态数据复核链（加载器 → FastAPI → React） | `server/docs/review_browser/` |
| `server/docs/csv_checks/batch_001/` | 首批待审 CSV + manifest + 证据（**不是**正式配置） | `server/docs/csv_checks/BATCH_001.md` |
| `mock_server.py` | 本地协议模拟器，有登录／进图／交互与客户端写入副作用，不作正式服务端 | [`边界与副作用`](docs/MOCK_SERVER.md) |
| `data/*.fls`、`map/*.map`、`Fonts/`、`mx.exe`、`mxmain.dll`、`exe/python27*.dll` | 工具与逆向依赖的客户端材料；`.gitignore` 只白名单了部分 | — |
| Google Drive 外部包（`interface1019` = 真 `interface.fls` 分卷；`MXSJ_CORPUS` = 全量反编译语料） | 仓库里**没有** `interface.fls`，只能从这两个目录取；**目录内容会随开发更新，每次先列目录、以目录为准**；产物一律留仓库外、不入库 | [`docs/EXTERNAL_CORPUS.md`](docs/EXTERNAL_CORPUS.md) |
| 其余根目录 `*.dll/*.exe/*.pak/music*/log/` | 客户端运行时与用户日志，工具不依赖；部分日志被 `work/.../evidence` 引用 | — |

## 3. 环境与命令（从仓库根目录执行）

| 组件 | 依赖 | 测试 / 运行 |
|---|---|---|
| 客户端补丁 | Python 3.11+ 标准库 | `python3 -m unittest discover -s tools/client_patches` |
| SQLite 本地基础 | Python 3.11+ 标准库，SQLite >=3.24 | `python3 local_server/bootstrap.py --check-only`；`(cd local_server && python3 -m unittest discover -s tests -t .)`；显式初始化／建号见 local_server README |
| 服务端骨架 / 来源映射 / 批次核验 | 标准库 | `python3 -m unittest discover -s server/tests/architecture`；`python3 server/tools/verify_source_map.py`；`python3 server/tools/export_review_csv.py --check` |
| 复核目录 / API | `pip install -r server/apps/review_api/requirements.txt` | `python3 -m unittest discover -s server/tests/catalog`；`… -s server/tests/review_api`；运行 `python3 server/apps/review_api/main.py --host 0.0.0.0 --port 8000` |
| 复核验收套件 | 同上，且 `uvicorn` 必须在 `python3` 的 PATH 环境里（测试会**原样执行文档里的启动命令**） | `python3 -m unittest discover -s server/tests/review_browser_acceptance` |
| 复核网页 | Node ≥ 20.19，`npm ci --prefix server/apps/review_web` | `npm --prefix server/apps/review_web run typecheck && npm --prefix server/apps/review_web test`；开发 `npm run dev`（Vite 监听 0.0.0.0:5173，代理 `/api` 到 127.0.0.1:8000） |
| 地图编辑器 | `Pillow>=10`；GUI 另需 PySide6 + 桌面 | `(cd map_editor && python3 -m unittest discover -s tests)`；`python3 map_editor/run.py --scan .` |
| 资源编辑器 | PySide6 + Pillow | `(cd resource_editor && PYTHONPATH=src python3 -m unittest discover -s tests)`；运行 `PYTHONPATH=resource_editor/src python3 -m resource_editor data`（或 `python3 resource_editor/bootstrap.py`） |
| UI 编辑器 | PySide6（+Pillow 转精灵）；`.dlg` 语料库在 `MXSJ_DLG_CORPUS`（Drive 取用见 [`docs/EXTERNAL_CORPUS.md`](docs/EXTERNAL_CORPUS.md)） | `(cd ui_editor && PYTHONPATH=src python3 -m unittest discover -s tests)`；运行 `python3 ui_editor/bootstrap.py` |
| 脚本编辑器 | 本目录 requirements；旧 VM 编译器／恢复引擎材料另见运行时文档 | `(cd script_editor && PYTHONPATH=src python3 -m unittest discover -s tests)`（须在组件目录跑：`repair_runtimes.py` 在组件根，仓库根口径会少收集 9 项）；`python3 script_editor/bootstrap.py --check-only` |
| 脚本手册 | 本目录 requirements；核心校验需 jsonschema，GUI 需 PySide6 | `PYTHONPATH=script_manual/src python3 -m mxsj_manual validate --verify-evidence --repository . --require-full-inventory`；`python3 script_manual/check_manual.py`（统一闸门还需开发依赖） |
| 开发工具箱 / 风格检查 | 检查脚本为标准库；完整测试还需 Pillow；ruff 另装（`pip install ruff`，根 `ruff.toml` 为默认配置） | `python3 -m unittest discover -s tools/devkit/tests`；`python3 tools/devkit/check_windows_compat.py <dir>`；`python3 tools/devkit/check_doc_versions.py`；`ruff check <dir>` |

- 用仓库**外**的 venv（`python3 -m venv ../mxsj-venv`）；系统 pip 受 PEP 668 保护。
- 每轮重新探测 Python、Qt 与系统库；缺依赖可能导致导入失败或跳过。**跳过／未执行不算通过**，历史沙箱库与离屏结果不证明当前环境或 Windows 可用。
- 冻结客户端片段需要 CPython **2.5.6**（仅编译/审计用，见 `tools/client_patches/V3_3_DELIVERY_AND_ACCEPTANCE.md` §5），不是服务端运行版本。

## 4. 红线（违反任何一条都要先停下来问）

**数据与原包**
1. 不覆盖 `data/script.fls`、`tools/decompiler/script_fls_keys.json` 或任何原始客户端包；所有生成物写到仓库外新目录。构建器拒绝非锁定基线时**不要放宽**。
2. 不执行反编译/恢复出来的游戏模块，不 `eval` 任何数据；只做只读解析与受限字面量重建。不重建已删除的敏感 entry 1288 dump。
3. 不把待审 CSV（`batch_001`）复制进 `server/game_data/`；缺失不补零、异常不静默修复、同名多候选不按名字合并、不用简繁替换掩盖解码损坏。
4. 编辑器写回 `.fls` 时：原包不动、生成新包、写后逐条校验；目录按 entry_id 升序、新条目 `r1≠0`（见 `resource_editor/.../fls0slf.py` 模块注释）。导出目标不得是任何源资源路径或其别名。

**客户端补丁**
5. 注册预览只改 entry 337/4007；其余 5000 条与 entry 4806 逐字节不变。片段保持 Python 2.5 语法，用 CPython 2.5.6 编译后映射 opcode，不用 Python 3 编译。
6. 首页标题独立、点击时才 `import register`、目标页构造成功后才隐藏当前页；不实例化原登录控制器；不恢复 reg2/2980 旧 UI。
7. 不先上传未改完的候选让用户盲试；要求用户提供日志/截图时索取最小且脱敏的证据；只用假数据（`preview@example.invalid`）。

**仓库与协作**
8. 不 `git add` 生成的 FLS/ZIP、`node_modules`、浏览器缓存。新增大二进制前先问。**例外（用户 2026-10-23 明确要求）**：`script_editor/runtimes/` 的两套 Windows 编译器（20 个文件、24.5 MB）已入库；重建后二进制与 `manifest.json` 必须**成对**提交，不得只提交其一，其余生成物仍不入库。
9. 不切分支、不 force-push、不合入 `master`、不发布生产，除非用户当轮明确授权。PR 描述里**行为变更**（协议号、封包长度、导出写入、配置路径）必须写明，不能写成“只改注释”。
10. 不自动启动根目录 `mock_server.py` 对真实客户端；先读 `docs/MOCK_SERVER.md`。默认启动可能改 FLS、写开发模式并监听所有地址；`--no-patch` 不等于完全只读。自测也有固定临时文件副作用。
11. 不索取、不记录真实账号、密码、票据、密钥；不改 Drive 权限、不发邮件。

**原生优先（用户 2026-10-14 定，适用于一切面向客户端的功能）**
12. 凡游戏原生机制能实现的功能——原生控件、`.dlg` 布局、`ui.lst` 样式、引擎与脚本的既有套路——**必须**按原生规范实现，不得用外挂图片、代码 overlay 临时拼凑控件、包外散图等非原生方式替代。注册预览 v3.3 的整图按钮 + 透明点击框做法已被用户判定为不规范并作废（见 STATUS），不得再沿用或作为先例。
13. 原生确实实现不了、只能借助其他方式实现的功能，必须先把「原生为什么做不到、替代方案是什么、与原生的差异和风险」向用户**反复确认**，只有得到用户明确同意后才能动手；未经同意不得先实现再汇报。

## 5. Python 工具 / 编辑器开发约定

> 2026-10-14 与用户约定；全文、目录模板与清单见 [`docs/PYTHON_TOOL_CONVENTIONS.md`](docs/PYTHON_TOOL_CONVENTIONS.md)。新写或大改的 Python 工具、编辑器、脚本一律遵守；老工具碰到就补齐，差距清单在 [STATUS_HISTORY §3.5](docs/archive/STATUS_HISTORY.md#s3-3-5)。

1. **PEP 8 + 模块化**：`ruff check <tool>` 0 报告（规则 `E,W,F,I,UP,B`、88 列、py310；根 `ruff.toml` 是默认值，工具自己的 `pyproject.toml` 照抄一份）。`src/<package>/{core,gui}` 分层，`core` 不 import Qt、可在无显示器环境测试；路径用 `pathlib`，文本 IO 必须显式 `encoding="utf-8"`。
2. **GUI 一律 PySide6**（≥ 6.4）。不新增 tkinter / PyQt / wx 代码；现有 tkinter 工具只保留，不修补。
3. **必须有自检并启动脚本**：`bootstrap.py`（检查 Python ≥ 3.10、缺依赖自动 `pip install` 并带国内镜像回退、`--check-only`、失败写 `启动日志.txt` 并停住不闪退）+ `启动<工具名>.bat`（CRLF、纯 ASCII、`chcp 65001`、`py -3` → `python` 探测）。参考实现 `resource_editor/bootstrap.py`。
4. **必须有一键构建 EXE 脚本**：`build_exe.bat` + `<tool>.spec`（venv → 依赖 → 测试 → PyInstaller → `dist\<Name>\<Name>.exe`；GUI 用 `console=False` 且无参数双击必须直接开窗）。EXE 只能在 Windows 上构建：Linux 侧把 spec 写对并干跑，Windows 侧构建并把结果写回 STATUS。参考实现 `map_editor/build_exe.bat`（三个编辑器的 `build_exe.bat` 同一模板）+ `map_editor/map_editor.spec`。
5. **Linux 开发 → Windows 交付前必查**：`ruff check` → 单元测试（`QT_QPA_PLATFORM=offscreen`）→ `bootstrap.py --check-only` → `python3 tools/devkit/check_windows_compat.py <tool>`（0 ERROR，WARNING 逐条修掉或说明）→ 过一遍 CONVENTIONS §5.2 人工清单（路径大小写、编码、`sys.executable`、文件锁、`%APPDATA%`）。PR 描述分三栏写 **Linux 已做 / Windows 待验 / 已知差异**；没在 Windows 实机跑过就不能写「可用」。

## 6. 工作方式

- **事实 / 推断 / 设计三分开**：原字节、反汇编地址、测试输出是事实；“应该是”“推测为”要写明；设计文档不是实现。
- **先复现，再修复，再补能复现旧 bug 的测试。** 不要只改测试期望让它变绿；记住本项目最贵的教训：*测试替身可能与实现共享同一个错误假设*（CClickBox 签名事故）——接口以原 code object / 反汇编核对。
- **证据钉死输入**：许多测试把工具源码的 SHA-256 钉进证据 JSON（例如 `server/docs/csv_checks/agent_e_reproduction.json` 钉了 `tools/decompiler/batch_decompile.py`）。改这些工具后必须重新生成证据、逐字段 diff 并在提交信息里说明，否则架构测试会红。
- **文档去处**：长期规则 → 本文；当前状态 → `docs/STATUS.md`；**历史轮次 → `docs/archive/STATUS_HISTORY.md`**（2026-10-27 起，STATUS 的 §3／§4–§7 历史部分已拆出，§编号未改）；逆向结案 → `notes/`；子项目细节 → 子项目 README/DESIGN；被取代的快照 → `docs/archive/`（`git mv` + 横幅 + 修链接 + 登记索引，见 `docs/archive/README.md`）。不要再在根目录新建 `*_HANDOFF.md`。
- **结束一轮工作时**：更新 `docs/STATUS.md`（日期、分支、测试实测、红灯、下一步），提交并推送到当前会话分支。
- 多 Agent 并行时按 `server/docs/OWNERSHIP.md` 的目录所有权划分；跨模块只走 `contracts`。

## 7. 已知坑（详见 STATUS 与各子项目文档）

- GIRB 动态光照编解码**已全量解决（2026-10-23，map_editor v1.0.0）**：在仓外取得的 101 张客户端
  `.map` 语料（11,763 扇区）上，GIRB **11,763/11,763 零失败解出**；旧「1034/1035 固定样本中
  300/429 扇区解不出」是 0.1.0 时代的**历史缺口**，已不再成立，不要再据此下结论。
  但该 101 图语料**不随仓库分发**，复核需另行取得语料并重跑测试；「全量」只指该次语料，
  不是对任意地图的普遍保证。旧结论见 `docs/archive/` 与 `map_editor/README.md` 的版本历史。
- 0SLF 目录寻址**已判定（2026-10-16，反汇编）**：`.dlg` 走的 LoadFile 链在 `0x60DD00`
  用 **二分**（`0x60DD35` → `0x60E690` = `lower_bound`，16 字节记录、比 entry_id；返回后
  `0x60DD3D`/`0x60DD41` 判未命中）。所以**目录必须按 entry_id 升序**，新增/插入条目后
  其后所有记录的下标都变、`r3` 必须重算。`notes/fls_path_hash_and_dlg.md` §2 的「线性扫描」
  说的是 `0x48ECF0`（= `ReadFls`）那条路，该文已加更正横幅；细节见
  `notes/native_dlg_path_cipher.md` §2.1。改目录写回逻辑前先读这两处。
- 历史协议号／帧结论必须绑定具体链路：旧记录有 `0xFF` 后续读 2 字节，当前 Mock 使用 `MAX_LEN_BYTES=3`。不要套用无版本的“协议真值”；先读 `docs/MOCK_SERVER.md`，修改需独立证据。
- `script.fls` 模块导入不走 `.dlg` 的完整路径寻址；当前脚本编辑器以模块名 seed 与 `hash(basename + ".s")` 绑定身份（见 `script_editor/src/script_editor/core/vm/py25/cipher.py`）；`.dlg` 原生路径 XOR 已由真实 LoadFile 静态链定位（见 `notes/native_dlg_path_cipher.md`）；头反推只作旧存储读取兼容，不能用于写包验证。
- 静态分析、Mock 回环、用户实机反馈和真实抓包是不同证据。不能把回环生成的报文称为真实客户端抓包；也不能沿用旧文档断言全部研究材料的覆盖范围。
- 反编译产物 ≠ 可回编译源码（2026-10-15 用自建 CPython 2.5.6 实测）：这批 `.pyo` 的模块码对象以 RETURN_VALUE 收尾，uncompyle6 如实还原成模块顶层一句 `return`，于是 4,998 个产物里有 3,220 个**只因这一行** `compile()` 不过（剥掉后 75.4% 可编译）。走「编辑后回编译」管线前必须先剥它，并对候选文件做一次 `compile()` 校验；第二引擎 pycdc 的产物没有这个伪影，但自身语法错误率更高（48.4% 可编译），只用于阅读与交叉印证（详见 `notes/opcode_mapping_and_decompilation.md` §4.6）。
- 清点 `script.fls` 的反编译产物**必须扫目录**，别按 `script_entries.jsonl` 的 `current_filename` 匹配：12 个条目的包内自报文件名带位元污染（含 `\x00`/`?`/`*`），`batch_decompile` 写文件时会抛 `OSError` 而**静默零产物**；catalog 无名条目则落在 `script/unknown/`。2026-10-15 复核：所谓「26 条无产物」= 13 条清点误差 + 9 条可救 + 4 条无解。定点恢复用 `tools/decompiler/recover_entries.py`（只读复用 `batch_decompile`，它的 SHA 被 `agent_e_reproduction.json` 锁定，不要改）。
- 「某模块不在 `script.fls` 里」这类结论要先回查条目自报路径再下判断：`servicedata` 曾被判缺失，实际是无名条目 `1931` → `script/data/servicedata.py`，真条款全文一直在包内，而客户端就是裸名 `import servicedata`（`script/data` 在 import 路径上）。
- 真机「窗口标题/聊天乱码」多半**不是资源损坏**：客户端只有 `SetWindowTextA`，脚本层
  `SetSysCaption` 零转换，标题与 IM 层文字由**系统 ANSI 代码页**解释（详见
  `notes/title_and_chat_encoding.md`）。别去改 `data/data.fls` 里 `core/gamecode.pyo` 的
  `SYSCODE='gbk'`——它是编译期常量且与日志路径共用，正路是 cp950（Locale Emulator / 系统区域）。
- 本版本 `interface.GCODE = BIG5`，但 `GetGameRegion()` 被 `script/delegate.py` 覆盖成 `'cn'`，
  即台服构建用的是**简中屏蔽词子集**（表现是命中变 `*`，不是乱码）。做简体化时别用简繁转换
  掩盖解码错误（`裏`/`羣` 等在 cp950 不可编码，会静默丢字）。
- **别默认全量反编译语料存在**：生成物写在仓库外，环境变化后需重新确认。全档符号检索前先读 [`docs/DECOMPILE_CORPUS.md`](docs/DECOMPILE_CORPUS.md)，优先定点恢复；只有确需语义级全档检索才重建全量。
- `tools/decompiler/batch_decompile.py` 整池并行可能被超大常量模块堵住（历史 entry 2371 `preload_mov`、2679 `wingtypeposdata`）；补跑采用逐条子进程与超时，生成物不入库。
- `tools/decompiler/output/` 下的 `.py` 是反编译输出，有缺失和错误，不是源码。
- **顶层文档的版本号不许手工维护**：README / AGENTS / STATUS 里各组件的版本号必须与
  对应 `pyproject.toml` 的 `[project].version` 一致。改动组件版本后**同一轮**同步文档，
  并跑 `python3 tools/devkit/check_doc_versions.py`（退出码 1 = 漂移，要改文档而不是放宽检查）。
  这不是形式主义——`ui_editor` 从 0.8.4 涨到 0.21.0 期间 README 一次没跟上，读者据此
  长期以为 UI 编辑器只支持「字段编码和布局导出」，能力边界完全描述错了。
  该工具**只比对字符串**，不判断某段版本叙述是否过时；过时仍要人工看。

## 8. 术语

| 术语 | 含义 |
|---|---|
| FLS / `0SLF` | 客户端资源包；12 字节头 + 16 字节目录记录（`entry_id, r1, r2, r3`，长度/偏移经闭式变换混淆） |
| entry | `script.fls` 中的条目号（共 5002）；`server/docs/catalog/script_entries.jsonl` 是索引 |
| 五段 XOR | `script.fls` 载荷在 zlib 之外的分段异或加密，keys/bounds 在 key DB |
| 双 VM | `mxmain.dll` 内定制 Python 2.5（`HAVE_ARGUMENT=0x5F`）与 `exe/python27.dll` 内定制 Python 2.7（指令/参数双流） |
| `.dlg` | UI 布局文件（Python 源码，GBK/Big5 混合），存于 `interface.fls`，按路径哈希寻址 |
| GEPJ / GIRB / LLEC / MASK | `.map` 内的块：底图 / 碰撞网格 / 判定表 / 掩码（角色不能只凭名字猜） |
| batch_001 | 首批待审静态数据：17 CSV + manifest + validation + JSONL 证据 |
| H / I / J | 复核链的三个历史工作包：目录+API / 网页 / 独立验收 |
