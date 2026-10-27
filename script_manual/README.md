# 客户端脚本开发手册 — 0.1.0.dev4（内容建设中）

> **现行状态入口（2026-10-18）**：版本为 `0.1.0.dev4`；覆盖与审核数量只在 [STATUS §2](../docs/STATUS.md) 维护，由严格校验输出核对。当前 checkout 已包含 PR #51，下方旧会话“未合 master”等叙述只适用于原日期。
> 全量登记含目录和排除项，不等于全量可执行源码／解释完成；专题草稿不继承引用模块的审核。本文不把历史交付 ZIP 当作当前源码打包结果。

**当前开发目标不是目录列表。** 默认进入“开发任务/专题”，首批串起公告、登录、注册、主循环、快捷键、战斗队列6篇/26步骤；包含流程与分支、具体修改入口、检查方案、函数/证据精确跳转，严格加载时可读来源原文预览。专题是A编排的未独审草稿，引用模块accepted不转移给专题。这里只完成第一批，不是全量承诺已经兑现；后续内容与验收见[内容建设计划](docs/CONTENT_PLAN.md)。

**Drive test1是此前dev3样板包，不包含本次专题入口，不作为完整交付。** 本轮尚未重打包/上传，先把内容继续做实；原交付回执保留历史。

独立、只读的脚本字典工具。**JSON 是唯一底稿**，PySide6 查看器和离线单 HTML 共用校验/索引层，不导入或执行游戏脚本，不修改游戏包、脚本编辑器或启动器。

**历史集成状态（2026-10-16，[STATUS_HISTORY §3.51](../docs/archive/STATUS_HISTORY.md#s3-3-51)；当前见上方入口）**：七个新PR39–45已全部合入A分支，未合master。5135条目录登记 / 20份说明 / **16份有限审核通过（12 H、4 A_delegate）** / 4份战斗说明待独立复核 / 1排除；无过期审核。合并不是全模块或实机验收，42条战斗函数仍是名称底稿，其余5000模块没有假讲解。

- 已精确核SHA激活九份N7模板；登录四篇由A按用户授权作有限代审，不冒称N7新结论。
- A接手补完战斗四篇的指南/事实定位，因此四篇author均记A共同作者，**A不自批**；剩余工作仅为非A对新字节独立末审，不再让用户转述返修或重开七人。
- 恢复工具布尔参数双repr缺陷已修；新增独立回归，并实际重核四条raw/正文编码链。N1在两棵隔离树重放，三产物一致；详情、范围与未知见[收尾报告](../docs/evidence/script_manual_A_finalize_20261016.md)。
- 历史§3.49/3.50“未合入/3通过”等为当时快照，不是现状。当前源码已集成，但Qt、真实浏览器、Windows/EXE、游戏/原生/服务端仍未验收；Windows源码测试包现按用户授权交付Google Drive，不打游戏包、不合master。

## 开始使用

[已上传源码测试包test1（Google Drive）](https://drive.google.com/file/d/14s0nmb61CfMDFMerb23JpJkQioZHc6J6/view)，[交付回执](../docs/evidence/script_manual_windows_source_test1_delivery_20261016.md)。包内固定源码84e0b9c；后续上传回执不改变已上传ZIP。

**Windows测试交付**：先读 [`WINDOWS_TEST.md`](WINDOWS_TEST.md)，源码ZIP完整解压后双击 `测试手册.bat`（创建venv、强制Qt测试、保留日志），再按说明打开窗口/检查交互或自己运行 `build_exe.bat`。不需要Git或原游戏包；Linux结果不冒充Windows实测。维护者打包用 `python script_manual/make_source_package.py --output <仓库外新ZIP>`，自动收集实际来源依赖、拒绝摘要不符/越界/覆盖、写逐文件SHA清单，不扫入整个游戏或语料。

Arena agent接手/环境变化先读根 [`docs/ARENA_SANDBOX_RECOVERY.md`](../docs/ARENA_SANDBOX_RECOVERY.md)；不要把旧HEAD下的新版文件误删或重复补交。

Windows 安装 Python ≥3.10 后双击 **`启动脚本手册.bat`**。缺依赖自动安装，官方源失败才尝试镜像；失败保留日志。不需要编辑器/游戏运行时，也不内置或调用游戏编译器（本工具不编译、不写包）。

查看器支持：路径/中文功能/函数名搜索、领域/审核状态筛选、职责/函数和消息分支/关联及修改入口/证据四页、内部模块跳转、后台载入与校验、证据摘要/行范围复验、导出离线 HTML。没有说明的模块明确显示“尚未编写”，不填充假解释。

Linux / 命令行（从仓库根）：

```bash
python -m pip install -r script_manual/requirements.txt
PYTHONPATH=script_manual/src python -m mxsj_manual  # GUI
PYTHONPATH=script_manual/src python -m mxsj_manual validate
PYTHONPATH=script_manual/src python -m mxsj_manual validate --verify-evidence --repository .
PYTHONPATH=script_manual/src python -m mxsj_manual build --verify-evidence --repository . --output ../manual-site-v1
```

- 输出目录**必须不存在且在仓库/手册输入目录之外**；重复导出用新目录，绝不覆盖旧站点。
- `index.html` 双击可用，无服务端、网络请求或外部字体；可以整目录拷到别的电脑。`BUILD.json` 记录工具版本、输入文件摘要、覆盖数及 HTML 摘要。生成失败保留 `INCOMPLETE.txt`，不得分发未完成目录。
- `--verify-evidence` **仅**复核注释引用的文本字节 SHA256 和行号；不检查原始包、不做语义验证。冻结原包指纹另见 `coordination/baseline.json`。未加此选项时，页面明确标记证据“本次未校验”。不要求分发原包或79 MB语料。
- `--require-full-inventory` 可与 validate/build 配合，要求冻结包**全部登记条目**齐全（含目录、不可读及政策排除元记录）。本轮5135条登记可通过此结构闸门，；N1已修已知签名/回执问题并独立重放，但不能据此宣称元数据语义全部正确。总量5135是5002+133条登记，并非5135份可执行源码。
- `--content PATH` 在子命令**之前**指定另一份完整数据目录；目录必须包含同版schema、coordination、inventory、annotations、reviews。
- 搜索多个词取交集，路径反斜杠会归一化；功能关键词只能搜到已经编写的说明。搜不到不代表功能不存在。

## 给并行 Agent 的入口

**N1–N7卡已执行并交PR，勿重复启动七人**；[任务卡入口](coordination/NEW_AGENTS_START_20261016.md)保留范围约束，当时已合入A，历史进展见[STATUS_HISTORY §3.51](../docs/archive/STATUS_HISTORY.md#s3-3-51)/收尾报告，当前以STATUS§1–§2为准。下列契约/逻辑owner映射继续生效，但旧B–H分支与“更新原PR”不再是新人操作指令。

1. 先读 [`docs/CONTRACT.md`](docs/CONTRACT.md) — 字段、证据与版本规则。
2. 读 [`docs/AGENT_TASKS.md`](docs/AGENT_TASKS.md) — 权限边界和各任务卡。
3. 使用 `schema/contract.schema.json` 的 `$defs.annotation`，从 `examples/annotation.json` 复制结构，**替换身份/事实/证据**，不能直接复制样板结论。
4. `coordination/tasks.json` 是唯一主负责登记；不是通过文件名抢任务。目录可能重复、路径可能同名，主键始终是 `(archive_sha256, entry_index)`。
5. C–G **只改自己的 `annotations/<domain>/`**。B只改 inventory。H只改 reviews。都不要改总导航、schema、任务归属或根 STATUS，由 A 集成。

## 开发 / 测试 / EXE

```bash
python -m pip install -r script_manual/requirements-dev.txt
python script_manual/check_manual.py  # 六道统一闸门，包含N1/恢复工具独立测试
# python script_manual/check_manual.py --require-gui  # Qt缺失时禁止跳过
PYTHONPATH=script_manual/src QT_QPA_PLATFORM=offscreen python -m unittest discover -s script_manual/tests -v
python script_manual/bootstrap.py --check-only
ruff check script_manual
python tools/devkit/check_windows_compat.py script_manual --strict
```

单元测试使用 `tests/fixtures/` 固定样本，不从生产annotations/inventory构造期望值；真实数据另有不假定说明数量的结构冒烟；统一闸门已包含下面的严格来源/full检查，单独跑测试时仍须另跑 `validate --verify-evidence`。冻结夹具不是新的权威底稿，勿随Agent交付自动改数量。

统一入口只读验证与合成测试，不做恢复/HTML构建；缺任一道工具或任一步非零都会返回失败，不把N1的32项藏在标准手册测试数量里，也不把GUI跳过当通过。

core测试不依赖Qt/游戏包；GUI测试在可用PySide6环境执行。`MXSJ_MANUAL_REQUIRE_GUI=1` 可禁止因Qt缺失而跳过GUI测试，Windows构建脚本已设置。离线浏览器验收是单独的开发检查，不要求用户安装浏览器自动化依赖。

Windows 双击 `build_exe.bat`：建 `.venv`、装依赖、自检和测试，全部成功后打 `dist/MXSJScriptManual/MXSJScriptManual.exe`。`set MXSJ_MANUAL_ONEFILE=1` 改单文件。PyInstaller入口为不安装依赖的 `run.py`，打包包含数据和schema；无参数直接开窗。EXE异常日志写 `%APPDATA%/MXSJScriptManual/`。

Linux spec干跑已尝试，但宿主缺 `libpython3.11.so.1.0`，在Analysis阶段停止；不算打包通过。Windows onedir/onefile均尚未实机构建。

**Linux检查不等于Windows/EXE/游戏验收。** Windows源码测试包按用户授权交付Google Drive；不合master、不打游戏包。
