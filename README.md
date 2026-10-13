# MXSJ_TW_2022 ·《夢想世界》客户端研究与 Python 服务端重建

> **文档体系（2026-10-14 起）**：
> - [`AGENTS.md`](AGENTS.md) — 给 Agent / 新成员的接手指南：目录地图、命令、红线、工作方式（长期有效）。
> - [`docs/STATUS.md`](docs/STATUS.md) — **当前状态**：分支、各组件实测、红灯、等待事项、下一步（每轮更新）。
> - 本文 — 项目总览：目标、能力边界、各子系统说明、原则与常见问题。
> - [`docs/archive/`](docs/archive/README.md) — 已被取代的历史快照（含原 `AGENT_HANDOFF.md`）。

> 本仓库围绕 TW v2.27.2 客户端材料，开展资源/协议逆向、静态数据复核、可逆客户端界面改造、客户端资源/UI/地图编辑器，以及长期 Python 回合制服务端设计。仓库根目录本身就是一份游戏安装目录，工具与文档叠加其上。

> **目前不是可直接部署、可完整游玩的游戏服务端，也不是已经验收的客户端发行版。**

本 README 是项目总入口，说明“已有些什么、哪些可以运行、哪些还只是设计、已知问题是什么”。详细实现证据、历史交付和接口约定通过文内链接继续阅读。

---

## 目录

1. [项目目标与当前结论](#1-项目目标与当前结论)
2. [当前能力与完成度](#2-当前能力与完成度)
3. [仓库结构](#3-仓库结构)
4. [环境准备](#4-环境准备)
5. [只读静态数据复核工具](#5-只读静态数据复核工具)
6. [客户端资源与数据研究](#6-客户端资源与数据研究)
7. [地图编辑器](#7-地图编辑器)
8. [资源编辑器与 UI 编辑器](#8-资源编辑器与-ui-编辑器)
9. [客户端注册界面预览](#9-客户端注册界面预览)
10. [Python 游戏服务端架构](#10-python-游戏服务端架构)
11. [测试与证据](#11-测试与证据)
12. [已知风险与后续计划](#12-已知风险与后续计划)
13. [协作和变更约定](#13-协作和变更约定)
14. [文档导航与常见问题](#14-文档导航与常见问题)
15. [资源使用与安全提醒](#15-资源使用与安全提醒)

## 1. 项目目标与当前结论

### 1.1 长期目标

- 使用 **Python + asyncio + PostgreSQL** 构建可长期维护的回合制游戏服务端。
- 本地测试与后续公网运行沿用同一套业务架构，不以一次性 Mock 作为正式基础。
- 基于客户端资源、字节码、协议和实际行为建立可追溯证据；不把猜测当作已还原的规则。
- 支持必要的客户端修改，逐步形成真实的 **注册 → 选区 → 登录 → 创建角色 → 进入地图** 链路。
- 首条真实链路就包含网关，预留网关独立部署、安全控制、运维与私有 GM 管理能力。
- 按数据所有权、模块目录和接口契约支持多人、多 Agent 并行协作。
- 长期面向简体中文玩法体验，但**不以简繁替换掩盖原始数据损坏或解码错误**。

### 1.2 目前真正可以做什么

1. 核对部分客户端静态数据的结构、来源、边界和异常记录。
2. 运行独立的只读数据复核 API 与网页，浏览道具、宠物、技能、地图/NPC 和异常证据。
3. 用地图工具扫描、解析和渲染样本；地图工具仍有重要缺陷，必须在副本上使用。
4. 重建离线注册界面的测试候选，并在完整 Windows 客户端副本上进行人工验证。
5. 阅读和检查服务端目录、模块契约、网关与安全设计，为真实运行实现做准备。

**目前不能据此宣称：**账号服务已上线、数据库已落地、角色可持久化、地图/战斗闭环可玩、全部协议兼容、全部地图碰撞正确，或注册界面已完成原生验收。

### 1.3 分支与集成状态

分支、基线、与 `master` 的差距、PR 状态和合并授权**只在 [`docs/STATUS.md`](docs/STATUS.md) §1 维护**，本文不再保存日期化的分支快照。
简要脉络：PR #1–#27 已全部合入或关闭（#26 把复核链、注册 UI、设计与地图编辑器带进 `master`，#27 修地图编辑器缺陷）；
2026-10-13 的资源编辑器、UI 编辑器与 0SLF 路径哈希逆向在工作分支上，截至 STATUS 快照日期尚未合入 `master`。
合并 #25 当时是带已知问题的集成决定，问题清单见 [PR25_REVIEW.md](map_editor/PR25_REVIEW.md)。

## 2. 当前能力与完成度

| 方向 | 已有内容 | 当前边界 |
|---|---|---|
| 客户端材料索引 | `script.fls` 的 5002 条索引，模块映射与研究记录 | 条目有索引不等于逻辑全部恢复 |
| 静态数据提取 | 受限解析、异常复核、可复现导出、来源与覆盖证据 | 不是运行原客户端脚本，也不是正式生产配置 |
| 首批复核数据 | `batch_001`，递归共 17 个 CSV、总计 22 个文件 | 保留隔离、缺失、歧义；不发布到 `game_data` |
| 复核 API/网页 | 只读目录加载、查询、搜索、分页、证据展示 | 已有集成验收；不是游戏网关或 GM 后台 |
| 地图编辑器 | Python/Pillow 格式引擎、PySide6 界面、扫描/渲染/导出、GIRB 碰撞解码 | GIRB 300/429 扇区仍解不出（已消除假成功）；Windows EXE 未实机冒烟 |
| 资源编辑器 | `.fls` 包惰性秒开、精灵 I0/T0/I1 预览、PNG 替换、按路径导入、真名识别、原子保存 | 0.3.3；真实 Windows + 进游戏显示验证待用户反馈；script.fls 条目只浏览不解码 |
| UI 编辑器 | `.dlg` 布局 2,706 条往返保真、画布编辑/吸附/对齐、撤销重做、写回 `.fls`、按钮态预览 | 0.5.2；九宫格（M3.3）未做；`.dlg` 语料库未入库 |
| 0SLF 路径哈希 / `.dlg` 提取 | 引擎自研哈希复刻、2,706/2,901 `.dlg` 定位解码、`ui.lst` 样式表 | script.fls 模块导入不走此哈希；`.dlg` XOR 密钥派生未定位 |
| 注册 UI | v3.3 离线候选，三个字段、本地校验、按钮与光标修正 | 无真实注册/保存；Windows 原生验收待完成 |
| 游戏服务端 | 21 个一级责任区、类型契约、81 个细分工作包 | 业务运行、账号数据库、地图与战斗闭环未实现 |
| 网关/安全/GM | 可拆分设计、职责、权限、审计和故障边界 | 设计文档，不是已经启动的安全服务 |
| 根目录 Mock | 历史协议/客户端联调实验脚本 | 不作为正式服务端；默认不启动，先检查副作用 |

## 3. 仓库结构

```text
MXSJ_TW_2022/
├── AGENTS.md                     Agent / 新成员接手指南（规则、地图、命令、红线）
├── README.md                     项目总览（本文）
├── docs/
│   ├── STATUS.md                 当前状态快照（每轮更新）
│   └── archive/                  已被取代的历史快照（含原 AGENT_HANDOFF.md）
├── notes/                        逆向结案笔记：双 VM opcode 表、0SLF 路径哈希与 .dlg、游戏数据、UI 编辑器二期设计
├── mx.exe / mxmain.dll / *.dll   客户端程序（根目录即游戏安装目录；mx.exe/mxmain.dll/exe/python27*.dll 是逆向对象）
├── data/                         FLS 样本（script.fls 等 6 个包；.gitignore 白名单）
├── map/                          已纳入仓库的地图样本
├── Fonts/                        客户端字体（补丁图片重绘与 UI 编辑器文字渲染使用，不随包分发）
├── mock_server.py                历史联调 Mock，非正式服务端
├── resource_editor/              .fls 资源包浏览/编辑器（PySide6；core/gui 分层）
│   ├── README.md / DESIGN.md     使用说明、版本历史 / 架构决策
│   ├── src/resource_editor/      core（containers、codecs、services）、gui
│   ├── tests/                    合成夹具 + 真实包测试（data/ 存在时启用）
│   └── 启动编辑器.bat / bootstrap.py  Windows 一键启动 / 自检入口
├── ui_editor/                    .dlg 布局可视化编辑器（PySide6；core/ui 分层）
│   ├── README.md / DESIGN.md     使用说明、版本历史 / 架构决策
│   ├── src/ui_editor/            core（dlg_codec、pack、sprite、styles、snap）、ui
│   ├── tests/                    编解码往返、模型、GUI 冒烟（需桌面）
│   └── 启动UI编辑器.bat / bootstrap.py
├── map_editor/
│   ├── README.md                 编辑器使用与格式说明（部分历史结论已过时）
│   ├── PR25_REVIEW.md             最新独立审查及待修复事项
│   ├── run.py / runGUI.py        CLI+GUI 合一入口 / 纯 GUI 入口
│   ├── src/map_editor/           core、client、ui 分层实现
│   ├── tests/                    编辑器回归测试
│   └── build.bat / *.spec        Windows 打包脚本与配置
├── tools/
│   ├── client_patches/           可逆注册 UI 预览、冻结资产、测试与审计、v3.3 交付事实表
│   ├── decompiler/               双 VM 字节码反编译、5 段 XOR 重打包；output/ 为反编译文本（仅线索）
│   ├── data-parser/              universal_fls_tool、mx_path_hash、extract_dlg、i0_sprite 等
│   ├── data-export/              历史数据导出结果
│   ├── data_browser/             历史浏览工具，非新复核网页入口
│   └── dis_v43/ 及根级 *.py       历史反汇编/解码器
├── server/
│   ├── README.md                 服务端工程边界与导航
│   ├── src/mxsj_server/          游戏服务端骨架、模块契约
│   ├── src/mxsj_catalog/         已实现的独立只读数据加载核心
│   ├── apps/review_api/          FastAPI 复核查询 API
│   ├── apps/review_web/          React / TypeScript / Vite 复核网页
│   ├── docs/                    架构、子系统、复核与验收文档
│   │   └── csv_checks/batch_001/ 首批待审 CSV 和证据
│   ├── tests/                   架构、目录/API、独立验收等测试
│   ├── tools/                   复现、核验、导出与验收工具
│   ├── game_data/               正式静态配置预留，未发布首批复核数据
│   ├── migrations/              数据库迁移预留
│   └── deploy/                  部署能力预留
└── work/dream-world-connect-login-map/   早期研究区（2026-10-09 起）
    ├── INDEX.md                 研究区索引
    ├── report/                  阶段研究报告；client-status-20261012.md 为客户端侧权威现状
    ├── notes/ evidence/         297 份笔记与证据链
    ├── tools/                   专项研究工具（部分帧模型已过期，见 client-status）
    └── artifacts/               已提交的研究制品（协议号表等）
```

**仓库材料不等于完整客户端安装包。** 文件是否被跟踪受 `.gitignore` 和既有样本范围影响；运行原生客户端所需的全部图片、资源与运行库，不保证由一次克隆全部提供。尤其不要把仅生成 FLS 的补丁目录当作完整客户端启动。

## 4. 环境准备

### 4.1 按模块安装，不强行统一历史运行环境

| 使用场景 | 环境要求 |
|---|---|
| 服务端骨架、数据核验、复核目录 | Python 3.11+；多数静态检查仅需标准库 |
| 复核 HTTP API | Python 3.11+，依赖见 `server/apps/review_api/requirements.txt` |
| 复核网页 | Node.js 与 npm；建议 Node 22.12+，安装时遵守依赖自身版本要求 |
| 地图 CLI/测试 | 地图包声明 Python 3.10+，需 Pillow；项目统一使用 Python 3.11+ 较方便 |
| 地图 GUI | 另需 PySide6、可用桌面图形环境 |
| 地图 Windows EXE | 在 Windows 上运行 PyInstaller；本项目没有已验收 EXE |
| 资源编辑器 / UI 编辑器 | Python 3.10+，PySide6 + Pillow；Windows 可双击各自目录下的 `.bat` 自动装依赖；核心（非 GUI）测试无需桌面 |
| 注册候选构建 | Python 3.11+；修改/重新冻结自写旧 VM 片段还需 CPython 2.5.6，重绘资产需 Pillow |
| 原生客户端验证 | 匹配版本的完整 Windows 客户端测试副本 |

CPython 2.5.6 仅用于兼容性编译/受限审计，不是未来服务端运行环境。不要在它上面安装现代依赖或执行任意恢复模块。

### 4.2 建议的开发环境

以下命令默认从仓库根目录执行，示例使用 POSIX shell；Windows 可用对应 Python 命令与 PowerShell 激活方式。

```bash
# 虚拟环境放在仓库外，避免误提交依赖目录
python3 -m venv ../mxsj-venv
. ../mxsj-venv/bin/activate

# 只准备复核 API 时
python -m pip install -r server/apps/review_api/requirements.txt

# 只需要地图命令行或无头测试时，无需先安装 Qt
python -m pip install 'Pillow>=10.0'

# 需要复核网页时
npm ci --prefix server/apps/review_web
```

Windows PowerShell 激活示例：`..\mxsj-venv\Scripts\Activate.ps1`。原生 GUI 与完整浏览器验收依赖应按各子项目文档另行准备。

## 5. 只读静态数据复核工具

这是目前较完整、可以独立运行的一条工具链。它只读取已提交的复核材料，不需要先实现游戏服务端，也不依赖 PostgreSQL 运行。

```text
客户端资源研究
    ↓ 受限解析、来源确认、异常隔离
batch_001：CSV + manifest + validation + JSONL 证据
    ↓ 哈希、结构、数量、证据关联校验
mxsj_catalog：只读加载与查询
    ↓ FastAPI，/api/v1/review
React 复核网页：搜索、分页、详情、来源、异常
```

### 5.1 启动 API

完成上一节 Python 依赖安装后，在终端 A 运行：

```bash
python server/apps/review_api/main.py --host 0.0.0.0 --port 8000
```

- API 前缀：`/api/v1/review`。
- 默认数据目录：`server/docs/csv_checks/batch_001`。
- 可通过 `--batch-dir` 或 `REVIEW_BATCH_DIR` 选择批次目录；加载失败应先排查证据和文件一致性，不能随意修改 manifest 来绕过错误。
- 该服务是内部数据复核工具，不是玩家登录端口，不提供数据编辑、注册账号或发布能力。

### 5.2 启动网页

终端 B：

```bash
cd server/apps/review_web
npm run dev
```

默认 Vite 监听 `0.0.0.0:5173`，API 由服务器侧代理转发到 `http://127.0.0.1:8000`。

- 本机开发可打开终端显示的网页地址。
- 沙箱/远程环境应打开平台提供的预览 URL，而不是在自己的浏览器中访问沙箱的 `localhost`。
- 浏览器只发送相对路径 `/api/...`；`VITE_API_PROXY_TARGET` 是开发服务器的代理目标，不是浏览器直连地址。
- 两个进程分开运行；API 失败会显示错误，**不会偷偷降级为夹具数据**。
- 回放模式必须显式启用，页面会标示“非真实数据”；不能拿回放成功当作真实联调成功。

> `0.0.0.0` 会监听可用网卡。以上是受控开发环境用法，不构成公网部署方案；不要把未做访问控制的工具端口直接暴露到公网。

### 5.3 数据和查询语义

- `batch_001` 总计 **22 个文件**：17 CSV + 5 个 JSON/JSONL 文件；17 CSV 是递归统计，顶层只有 9 个，其余在 `maps_npcs/`。
- CSV 内容是静态定义/模板与研究证据，不是玩家拥有的物品、宠物或角色数据库。
- manifest 用于声明文件、长度、哈希与列结构；validation 和 JSONL 用于保留统计、隔离与写入覆盖证据。
- 缺失不补零，错误不静默修复；保留同名多候选、零 ID、重复行和原始顺序。
- 不把不同 NPC 来源直接按 ID 去重合并。
- 不把公式前缀、富文本标记当作可执行内容，不用 `eval` 处理数据。

详情见 [后端说明](server/docs/review_browser/BACKEND.md)、[API 契约](server/docs/review_browser/API_CONTRACT.md)、[网页说明](server/apps/review_web/README.md) 和 [集成验收](server/docs/review_browser/ACCEPTANCE.md)。

## 6. 客户端资源与数据研究

### 6.1 材料覆盖不代表逻辑恢复

- 当前全量索引包含 **5002 个 `script.fls` 条目**。
- 服务端设计整理了 21 个一级责任区和 81 个细分工作包。
- 81 个工作包引用 1654 个不同条目，仍有 **3348 个条目尚未映射到这些工作包**。
- CSV 可提取性盘点覆盖 33 个脚本、48 个表目标，但“可提取”“待复核”和“可作为正式配置”是不同状态。
- 客户端显示层可以提供参数和协议线索，但不能直接当作权威服务端规则。

### 6.2 第一批数据的关键事实

| 数据 | 已记录结果 | 不能做的推断 |
|---|---|---|
| 道具 entry 1945 | 6852 条来源记录，6851 条进入待审 CSV，1 条隔离 | 不能丢掉原字节后补一个看起来正常的中文名 |
| 宠物 entry 2027 | 135 条进入待审 CSV | 不代表宠物培养/战斗业务完成 |
| 资质 entry 2954 | 132 条来源记录，131 条进入待审 CSV，1 条隔离 | 不把上下界异常自动“纠正” |
| 技能 entry 3205 | 590 次写入、581 个唯一键、9 次覆盖；579 条待审，2 条隔离 | 不重新把 590 当成唯一技能数 |
| 缺失资质 | 3 条独立缺失记录 | 不合成 0 值来满足关联 |
| 同名技能 | 保留候选及歧义 | 不默认选择第一个技能 ID |

已知隔离包括道具 `72548`、资质 `2800`、技能 `719/4406`；缺失资质涉及 `3010/4021/4022`。如 `高級命中` 和 `終級命中` 的多候选关系须保留，不能仅凭名称合并。

完整证据见 [CSV 可提取性清单](server/docs/CSV_READINESS.md)、[数据异常复核](server/docs/CLIENT_DATA_REVIEW.md)、[独立复核](server/docs/CLIENT_DATA_INDEPENDENT_CHECK.md) 和 [批次目录](server/docs/csv_checks/batch_001)。

### 6.3 推荐的只读核验命令

```bash
python server/tools/verify_source_map.py
python server/tools/export_review_csv.py --check
python server/tools/review_browser_checks/verify_data_baseline.py
```

以上用于核对映射、已提交批次和独立基线。导出器的 `--check` 与重新生成/发布配置不是同一个动作；正式数据发布需要单独评审，不应直接把待审 CSV 复制到 `server/game_data/`。

## 7. 地图编辑器

### 7.1 定位和实现

`map_editor/` 是第一期地图查看/研究工具，产品范围原定为只读：发现地图、解析结构、底图渲染、分层叠加、坐标查询与 PNG/JSON 导出。**目前只读保护存在缺口，不能据产品定位假设它绝不会改坏源文件。**

- `core/`：地图容器、GEPJ 图像、GIRB 解码；不依赖 Qt。
- `client/`：客户端目录发现、配置、场景名表与 FLS 读取。
- `ui/viewmodel.py`：可无头测试的状态与导出逻辑。
- `ui/widgets.py`：PySide6 图形绑定；画布支持按住鼠标左键拖动平移、
  `Ctrl`+滚轮缩放（与顶部缩放输入框同步状态）、工具栏"适应窗口"一键缩放
  到整图，2026-10-12 新增，细节见 [编辑器 README](map_editor/README.md) 的
  "画布鼠标/滚轮操作"一节——本仓库沙箱没有 `libGL.so.1`，无法起 Qt 窗口做
  可视化回归，只做了代码走查，需要在有桌面环境的机器上验收。
- `run.py`：命令行/GUI 合一入口，默认命令行，`--gui` 才开图形界面；打包成
  无控制台 EXE 后不带参数双击启动时（`sys.frozen` 且 argv 为空）也会自动
  打开图形界面（2026-10-12 修复，见 7.3）。
- `runGUI.py`：纯 GUI 入口，不管传不传参数、传了哪些参数都一律直接打开图形
  界面（内部自动补 `--gui` 再转发给同一套 `cli.main()`），适合只想双击进
  图形界面、不想记命令行参数的场景（2026-10-12 新增）。

图像解码使用 Pillow；场景名存在 sidecar 表依赖。LLEC、GIRB 和 MASK 的角色不能只根据名称猜测，也不能把少量样本观察推广为格式定律。

### 7.2 使用方式

**先备份，使用客户端测试副本；导出目录必须与源资源分离。** 以下 CLI 示例从仓库根目录读取样本，将输出放到仓库外新目录：

```bash
python map_editor/run.py --scan .

mkdir -p ../mxsj-map-exports
python map_editor/run.py --scan . \
  --export-json '2101:../mxsj-map-exports/2101.json'

python map_editor/run.py --scan . \
  --export-png '2101:../mxsj-map-exports/2101.png'
```

GUI 在有桌面环境的电脑上使用，先安装完整运行依赖：

```bash
python -m pip install -r map_editor/requirements.txt
python map_editor/run.py --gui --client-root /path/to/client-test-copy
python map_editor/runGUI.py --client-root /path/to/client-test-copy   # 永远直接开图形界面
```

将示例路径替换为真实测试副本。不要把 `--export-json` 的目标写成任何源 `.map` 或其它客户端资源路径——导出前现在会自动检查并拒绝写到当前打开或已扫描到的任何源地图路径（2026-10-12 修复，见 7.3）。导出同名文件也可能覆盖既有输出，应选择新文件名。

Windows 打包入口是 `map_editor/build.bat`。它会安装依赖、执行测试并调用 PyInstaller；无参数启动分派逻辑已修复（见 7.3），但尚未完成 Windows EXE 实机双击冒烟验证，因此不能将“存在打包脚本 + 分派逻辑已改”等同于“已有经过实机验收的可用安装包”。

### 7.3 合并后的问题与修复状态

| 优先级 | 问题 | 状态 | 已有证据 / 影响 |
|---|---|---|---|
| P1 | GIRB 短匹配基址经验修改产生假成功 | ✅ 已修复（2026-10-12） | 1034/1035 共 429 扇区，原 PR 接受 144 个，其中只有 129 个与原子程序逐字节一致；基址改回 `0x801` 后仍解出 129 个，与原子程序完全一致，0 个假成功 |
| P1 | JSON/PNG 导出可覆盖源地图 | ✅ 已修复（2026-10-12） | 原已在临时副本复现 `.map` 被 JSON 截断覆盖；现在导出前会拒绝写到当前打开或已扫描到的任何源地图路径（含路径别名/大小写/硬链接判断），命中即抛 `ExportBlockedError` 并提示，不再触达写文件 |
| P2 | 超长解码被裁剪后计为成功；截断操作数被补零接受 | ✅ 已修复（2026-10-12） | 真实扇区 2405 字节的错误输出原本会被截成 2400 字节当作成功；现在结束标记触发时长度必须恰好等于 2400，否则直接报错，`--girb-report` 统计不变 |
| P2 | 无参数 EXE 入口不打开 GUI | ✅ 已修复（2026-10-12，**仅限分派逻辑，未做 Windows 实机冒烟**） | 原本只有 `--gui` 才进图形分支，而打包配置关闭控制台，双击无参数启动等于“什么都没发生”；现在冻结（PyInstaller）且无参数时自动打开 GUI，开发环境 `python run.py` 无参数行为不变。另新增 `runGUI.py` 入口，不论传什么参数都直接开图形界面 |
| 审查项 | 同 PR 修改了 Mock 协议行为 | 未处理（超出 map_editor 范围） | 包括 opcode 和扩展长度 3→2 字节，不能称为“纯注释”，需要单独评审 |

**GIRB 解码覆盖率仍有缺口，不是“已解决”**：300/429 个真实扇区依旧解不出，上面第一行的修复只是去掉了“假成功”，没有提升覆盖率；**尚未支持的扇区继续明确失败，错误数据不会被伪装成成功。** 此前“101 张图中若干张完全解出”的统计不能在修正后直接沿用，需要用可靠标准重新核验。

先读 [独立审查与验收要求](map_editor/PR25_REVIEW.md)，再读 [编辑器 README](map_editor/README.md)；一期交接报告已归档至 [docs/archive/2026-10-12-map-editor-handover.md](docs/archive/2026-10-12-map-editor-handover.md)，其中保留了历史结论，冲突时应以可复现的新证据判断，不能用旧成功率反驳字节级差异。

## 8. 资源编辑器与 UI 编辑器

两者都是 2026-10-13 新增的独立 PySide6 桌面工具，建立在 [0SLF 路径哈希与 `.dlg` 逆向结案](notes/fls_path_hash_and_dlg.md) 之上：引擎用自研哈希把资源路径映射为 `entry_id`，`.dlg` 布局是 `interface.fls` 内 4 字节 XOR 的 Python 源码。核心解析与界面分离，核心层不依赖 Qt，可无头测试。

### 8.1 资源编辑器（`resource_editor/`，0.3.3）

- 打开任意 `.fls`：`0SLF` 容器（script/skill/skill2/passive/effect/magicres5）与名目录式 `data.fls`。只读目录建索引实现**大包秒开**（1 GB 包 0.07 秒），条目与缩略图按需加载。
- 预览：精灵 I0/T0/I1 动画播放、帧列表、调色板；`script.fls` 条目只浏览不解码；`effect.fls` 41 个未破译条目仅 Hex 查看。
- 编辑：PNG 替换精灵帧（带往返误差报告）、原始数据替换、按路径导入（路径哈希即条目号）、帧图转精灵导入、条目增删与撤销；保存时 `.bak` 备份 + 原子替换，未改条目逐字节原样。
- 真名识别：内置 2,901 条布局路径字典，再从已命名 `.dlg` 扒出图片引用反查，`interface.fls` 中绝大多数 UI 图片可显示真名。
- 导出：单条目 / 选中 / 整页 / 整包，按真名建目录树。

### 8.2 UI 编辑器（`ui_editor/`，0.5.2）

- 打开散装 `.dlg` 或直接从 `.fls` 包内打开；左侧资源树按代际着色（现役新 UI / 第三代 / 死引用），`ui.lst` 自动作为样式表。
- 画布点选、拖动、改尺寸，边缘/中线吸附与参考线，网格/标尺，多选对齐与等距分布；右侧属性面板按类型编辑任意字段；38 种控件的默认属性来自 47,139 个真实控件普查。
- 撤销/重做 50 步；按钮正常/按下/悬停/禁用四态预览（切法是否与游戏一致以进游戏比对为准）。
- 保存：写回原版式 `.dlg` 文本（`# -*- coding: gbk -*-` 头；显示文本 Big5、资源路径 GBK 分字段编解码）；「保存回资源包」生成新包、原包不动、写后逐条校验；可把新图片添加进包并自动转成游戏精灵格式；导出 PNG 对照。
- 硬门槛：2,706 个已解密 `.dlg` 全部通过「解析 → 序列化 → 再解析」一致性测试（语料库未入库，由 `MXSJ_DLG_CORPUS` 指向）。

### 8.3 共同边界与注意事项

- **写回必须维持目录不变量**（0.3.3 / 0.5.2 的 P0 修复）：目录按 `entry_id` 升序、新增条目 `r1≠0`，否则游戏查不到新条目甚至卡屏。曾用旧版加图保存过的包，用新版打开再保存一次即可修复。该不变量与 `notes/` 中“引擎线性扫描目录”的结论尚未用反汇编统一，见 [STATUS §3.2](docs/STATUS.md)。
- 只在客户端测试副本上使用；生成的新包与原包分离；与原版客户端的最终兼容性需要 Windows 原生进游戏验证，截至 STATUS 快照日期尚无用户反馈。
- 运行与测试：

```bash
python -m pip install PySide6 Pillow
PYTHONPATH=resource_editor/src python resource_editor/bootstrap.py --check-only   # 启动自检
PYTHONPATH=resource_editor/src python -m resource_editor data                     # 以目录打开
python ui_editor/bootstrap.py [布局文件|目录|资源包]
(cd resource_editor && PYTHONPATH=src python -m unittest discover -s tests)
(cd ui_editor && PYTHONPATH=src python -m unittest discover -s tests)
```

Windows 用户可直接双击 `resource_editor/启动编辑器.bat`、`ui_editor/启动UI编辑器.bat`（自动检查并安装依赖，失败原因写入同目录启动日志）。GUI 测试需要桌面环境；无 `libGL` 的无头环境只能跑核心测试。设计决策与路线见各自 `DESIGN.md` 和 [UI 编辑器二期设计](notes/ui_editor_phase2_design.md)。

## 9. 客户端注册界面预览

### 9.1 当前版本和交互范围

当前候选为 **v3.3 控件修正版**，实现与证据位于 `tools/client_patches/`。

- 首页入口改为简体「注册账号」。
- 首页不预先加载注册模块，只有点击入口才加载；先准备目标页面，成功后再隐藏当前页面。
- 协议页参考选区后服务条款布局；表单参考现有新登录布局/底图，不实例化旧登录控制器来借用业务流程。
- 三个字段：邮箱、密码、确认密码。
- 注册动作执行必填、邮箱格式/长度、密码 6–16 位和两次输入一致性检查；邮箱限制为基础 ASCII、最多 32 字符。
- 合法输入也只显示离线提示，不创建账号，不保存凭据，不模拟注册成功。
- Info「离线预览说明」直接显示「離線預覽，未送出。」；它不读取字段、不先做必填校验。
- 上一步/拒绝不保存、不提交；保留原选区和登录流程。

这是局部离线预览，不是整个客户端的断网沙箱。未改动的公告、官网、登录等部分仍可能保留原联网行为。

### 9.2 必须区分的版本事实

| 版本 | 真实状态 |
|---|---|
| v1 / v2.1 | 曾收到局部导航/表单反馈，不能推广为后续版本验收 |
| v3 | 用户实际报告游戏窗口黑屏，已停用，不应继续分发 |
| v3.2 | 用户截图显示新协议/表单，但按钮、说明入口和光标等存在缺陷 |
| v3.3 | 已修正相关控件接口、按钮图片与层级；90 项测试、22 项 CPython 审计通过；**尚未收到原生验收反馈** |

v3.3 只修改 FLS 的 entry `337` / `4007`，其余 5000 条保持不变，原选区后条款/登录 entry `4806` 未改。原始 FLS 与密钥数据库不应被覆盖。

### 9.3 重建、安装和恢复

使用已提交冻结资产重建候选的示例：

```bash
python tools/client_patches/build_visual_preview.py \
  --allow-unverified-candidate \
  --output-dir ../mxsj-registration-v3_3-candidate
```

`--allow-unverified-candidate` 是明确承认尚未完成原生验收的保护开关，不代表绕过验证后就可正式发布。输出应使用仓库外新目录，输入版本/哈希不匹配时必须停止，不能强行套用。

安装原则：

1. 关闭游戏和更新器，准备完整客户端测试副本，备份其 `data/script.fls`。
2. 核对版本和原包哈希。
3. **同时更新生成的 FLS 与全部 8 张 PNG**；图片子目录沿用 `photo/registration_preview_v3`，不能因为名称未变就沿用旧图片。
4. 只合并该图片子目录，不替换或删除整个 `photo`。
5. 用假数据检查协议、返回、字段输入、鼠标焦点、Tab、闪烁光标、密码遮罩和离线分流。
6. 若再次黑屏/崩溃，保留脱敏日志与哈希，停止盲试，关闭客户端后恢复备份。

安装细节、已交付候选的哈希/链接、原生复测清单见 [v3.3 交付事实表](tools/client_patches/V3_3_DELIVERY_AND_ACCEPTANCE.md)；开发说明见 [客户端补丁 README](tools/client_patches/README.md)、[v3.3 修正记录](tools/client_patches/REGISTRATION_CONTROL_FIX_V3_3.md)、[v3 黑屏自查](tools/client_patches/V3_STARTUP_SELF_AUDIT.md)。

## 10. Python 游戏服务端架构

### 10.1 当前是架构与契约，不是游戏运行时

`server/src/mxsj_server/` 已划分启动、接入、协议、契约、状态运行时、持久化、观测与业务模块边界。公开类型可导入、目录可检查，但业务 `Protocol` 声明不是实现，字段顺序也不能直接作为客户端封包格式。

当前没有可游玩服务端启动命令，没有正式数据库 schema/迁移链，也没有账号、建角、进入地图和回合战斗的端到端闭环。能启动的 `review_api` 是另一条独立工具链，不应被当作游戏服务器。

### 10.2 21 个一级责任区

| 分组 | 模块 |
|---|---|
| 账号与角色 | `account`、`character` |
| 资产与制造 | `economy`、`inventory`、`crafting` |
| 世界与交互 | `world`、`npc`、`housing` |
| 战斗与规则 | `battle`、`skill` |
| 宠物与子女 | `pet`、`children` |
| 任务与活动 | `quest`、`activity` |
| 组织与关系 | `party`、`guild`、`social` |
| 邮件与交易 | `mail`、`trade` |
| 外观与运营 | `appearance`、`administration` |

21 个目录是责任划分，不是完整玩法清单。更细的 81 个工作包、未覆盖能力及材料索引见 [子系统盘点](server/docs/SUBSYSTEMS.md)。

### 10.3 已确定的设计方向

- 按权威数据所有权划分模块；跨模块不绕过公开接口直接改他人状态。
- 金钱、物品、奖励和附件领取等需要明确事务、幂等和审计，不以“最终大概一致”代替资产一致性。
- 回合制战斗明确行动收集、超时、回合推进、断线/重连视图和结算归属。
- 网关先允许同进程实现，但连接、会话、路由与业务分离，保留独立部署能力。
- 网关拆分不等于会话自动无损迁移或热重启；故障、重连、回送、幂等和版本边界需要落实。
- GM 使用私有管理入口、权限/审批和审计，不能复用玩家连接获得管理权限。
- PostgreSQL 是长期方向；依赖、迁移与部署基线仍需实现阶段锁定。

阅读：[模块清单](server/docs/MODULES.md)、[接口约定](server/docs/INTERFACES.md)、[战斗契约](server/docs/BATTLE.md)、[网关](server/docs/GATEWAY.md)、[网关安全与 GM](server/docs/GATEWAY_SECURITY_GM.md)、[基础能力缺口](server/docs/FOUNDATION_BACKLOG.md)。

## 11. 测试与证据

### 11.1 最近已记录结果

下表是**长期参考的套件清单与范围说明**；每个套件最近一次**实际运行**的结果（含红灯）记录在 [docs/STATUS.md §2](docs/STATUS.md)，以那里为准。测试计数按范围列出，不应简单相加作为项目完成率。

| 范围 | 已记录结果 | 证据 / 局限 |
|---|---|---|
| 客户端补丁单元测试 | 90 通过 | [交接复核 JSON](notes/handoff/2026-10-12-checks.json) |
| CPython 2.5 执行审计 | 22 通过 | [v3.3 审计](tools/client_patches/V3_3_RUNTIME_AUDIT.json)，图形/输入/调度仍有替身边界 |
| 服务端架构 | ~150 项（2026-10-14 实测 1 FAIL + 1 ERROR，见 STATUS §3.1） | 证明目录/契约/静态边界与证据指纹，不证明玩法正确 |
| 文件名映射 | 96/96 | 不是 5002 个模块已全部恢复 |
| 批次核验 | 22 文件通过 | 递归含 17 CSV，仍为复核候选 |
| 复核目录 / API | 34 / 27 通过 | 已有阶段集成记录 |
| 复核网页 | 112 通过、9 在线项默认跳过 | 单独在线联调 12 通过包含相关在线项，不可直接累加 |
| 独立复核验收套件 | 68 通过（2 项真实浏览器默认跳过） | 与地图编辑器历史上的 68 项是不同套件 |
| 真实 Chromium | 16 场景完成 | 复核网页验收，不是游戏原生客户端验收 |
| 地图编辑器 | 82 通过（PR #27 后；#25 时为 68） | 未覆盖全部已发现缺陷，不能据此信任 GIRB 输出 |
| 资源编辑器 | 核心 29 通过 + 2 跳过；GUI/批量操作需桌面 | 真实包测试在 `data/` 存在时启用 |
| UI 编辑器 | 核心 37 通过 + 1 跳过；GUI/绘制/写包需桌面 | 2,706 条 `.dlg` 往返测试需语料库（`MXSJ_DLG_CORPUS`） |

只读复核工具的完整结果见 [ACCEPTANCE.md](server/docs/review_browser/ACCEPTANCE.md)。历史报告中的临时绝对路径是当时运行坐标，不是稳定的安装依赖。

### 11.2 常用复跑命令

从仓库根目录运行，按需先安装对应依赖：

```bash
# 客户端补丁与服务端骨架
python -m unittest discover -s tools/client_patches -v
python -m unittest discover -s server/tests/architecture -v

# 数据加载/API，以及独立复核验收工具的测试
python -m unittest discover -s server/tests/catalog -v
python -m unittest discover -s server/tests/review_api -v
python -m unittest discover -s server/tests/review_browser_acceptance -v

# 地图工具：使用其目录作为工作目录
(cd map_editor && python -m unittest discover -s tests -v)

# 资源编辑器 / UI 编辑器（核心测试无需桌面；GUI 测试需 PySide6 + libGL）
(cd resource_editor && PYTHONPATH=src python -m unittest discover -s tests -v)
(cd ui_editor && PYTHONPATH=src python -m unittest discover -s tests -v)

# 网页类型、单元测试和构建
npm --prefix server/apps/review_web run typecheck
npm --prefix server/apps/review_web test
npm --prefix server/apps/review_web run build
```

地图测试依赖相应地图和参考资源；缺夹具导致跳过不能算覆盖通过。无头执行不要求 Qt，但 GUI/原生渲染仍需另测。

真实 HTTP 联调必须先启动 API，再在前端目录运行：

```bash
cd server/apps/review_web
REVIEW_API_BASE=http://127.0.0.1:8000 npx vitest run src/api/liveBackend.test.ts
```

这个地址供在同机运行的测试进程使用，不是要求远程用户的浏览器连接沙箱回环地址。

### 11.3 完整验收与旧 VM 审计

- 完整复核工具验收见 [验收复跑说明](server/docs/review_browser/ACCEPTANCE.md) 与 [独立检查工具](server/tools/review_browser_checks/README.md)。
- `acceptance_runner.py` 会生成报告并运行更多集成阶段，可能更新仓库中的证据文件；运行前查看工作区，运行后检查差异，不能把新报告无条件覆盖为“已通过”。
- 真实 Chromium 工具需独立准备；缺少时必须保留 `not_executed`，不能把 jsdom 当作真实浏览器。
- CPython 审计使用 `audit_visual_runtime.py --python25 /path/to/cpython-2.5.6/python --report /path/to/report.json`，仅审计指定片段，不执行整个恢复模块。
- 本次 README 编写不启动原生客户端、不重建交付包，也不自动执行根目录 Mock。

## 12. 已知风险与后续计划

### 12.1 优先处理的工作

排序后的待办与阻塞项以 [docs/STATUS.md §4–§5](docs/STATUS.md) 为准；下面是长期有效的工作方向：

1. **完成 v3.3 原生验收闭环。** 按按钮、焦点、光标、遮罩、验证、返回、再次进入逐项记录，不把部分截图当成整体通过。
2. **保持证据指纹与工具同步。** 改动被证据 JSON 钉死的工具（如 `batch_decompile.py`）后必须重新生成证据并逐字段 diff，否则架构套件变红。
3. **提升而不是伪装 GIRB 覆盖率。** 用原解压子程序的字节级结果加回归用例；失败保持未知。
4. **编辑器实机验证。** 在 Windows + 真实 `interface.fls` 上验证写回的新图/布局进游戏可见；统一“目录线性扫描 vs 有序寻址”的结论。
5. **独立审查协议行为修正。** 核对 `mock_server.py` 中 opcode、包长度与真实客户端处理，避免“注释修正”掩盖运行变化。
6. **继续数据证据复核。** 保留隔离与歧义，明确何时能进入正式配置；不要为了填满表而编造规则。
7. **落实第一条真实服务端链路。** 从网关、账号、区服角色范围和持久化边界入手，逐步打通注册至地图；不并行宣称全玩法已实现。

### 12.2 开发时的停止条件

- 原 FLS 或密钥数据库与目标版本不匹配：停止构建/覆盖。
- 客户端黑屏、启动失败、资源缺失：恢复已知状态，先定位，不连续盲发新候选。
- 数据解码返回长度正确但内容无法独立验证：不能宣布成功。
- 导出目标可能指向源资源或其路径别名：停止写入。
- 缺浏览器、样本、运行库或 Windows 环境：明确记录未执行，不把跳过当成通过。
- 数据异常尚未批准处理方式：保持隔离，不进入生产目录。

## 13. 协作和变更约定

1. **先阅读目录所有权与公共契约。** 见 [OWNERSHIP.md](server/docs/OWNERSHIP.md) 和 [WORK_PACKAGES.md](server/docs/WORK_PACKAGES.md)。
2. **事实、推断、设计分开标注。** 原文件字节、反汇编、调用点、实测结果与经验假设应能区分。
3. **区分研究工具和游戏业务。** `mxsj_catalog` / `review_api` 的完成不代表 `mxsj_server` 已可运行。
4. **保持数据可追溯。** 保留来源条目、偏移、原字节、重复写入、隔离原因与版本哈希。
5. **先复现，再修复，再补测试。** 不只统计异常减少，也验证输出内容与边界；测试替身自身也可能有错误假设。
6. **只在副本和临时目录做破坏性测试。** 不覆盖原客户端、不运行任意反编译模块、不把历史 Mock 自动当作安全入口。
7. **控制提交内容。** 源码、测试、小型冻结资产与证据按既有规则管理；依赖目录、构建缓存、生成的 FLS/ZIP 放仓库外，不顺手提交大包。
8. **明确 PR 行为变更。** 协议编号、封包、导出写入和配置路径变化都属于行为，不写成“只改注释”。
9. **分支集成与生产发布分开。** 当前 Draft PR 只是审阅入口；不得以“已合并到协调分支”推导出 master/生产发布授权。
10. **保留保护边界。** 不在仓库、日志、截图或报告中提交真实账号、密码、票据或凭据；需要客户端反馈时索取最小且脱敏的证据。

## 14. 文档导航与常见问题

### 14.1 建议阅读顺序

| 目的 | 入口 |
|---|---|
| 接手整个项目 | [AGENTS.md](AGENTS.md) → [docs/STATUS.md](docs/STATUS.md) → 要碰的子目录 README |
| 看历史交接快照 | [docs/archive/](docs/archive/README.md)（含原 `AGENT_HANDOFF.md`） |
| 了解服务端范围 | [server/README.md](server/README.md) |
| 找模块/玩法材料 | [MODULES.md](server/docs/MODULES.md)、[SUBSYSTEMS.md](server/docs/SUBSYSTEMS.md)、[材料目录](server/docs/catalog/DIRECTORIES.md) |
| 审核数据来源 | [CSV_READINESS.md](server/docs/CSV_READINESS.md)、[SOURCE_EVIDENCE.md](server/docs/SOURCE_EVIDENCE.md) |
| 启动复核网页 | [网页 README](server/apps/review_web/README.md)、[后端文档](server/docs/review_browser/BACKEND.md) |
| 核对复核工具验收 | [ACCEPTANCE.md](server/docs/review_browser/ACCEPTANCE.md) |
| 处理地图问题 | [PR25_REVIEW.md](map_editor/PR25_REVIEW.md)、[编辑器说明](map_editor/README.md) |
| 编辑资源包 / UI 布局 | [resource_editor/README.md](resource_editor/README.md)、[ui_editor/README.md](ui_editor/README.md)、[0SLF 路径哈希与 .dlg](notes/fls_path_hash_and_dlg.md) |
| 看懂字节码 / 反编译 | [opcode 映射与反编译报告](notes/opcode_mapping_and_decompilation.md) |
| 修改注册预览 | [客户端补丁说明](tools/client_patches/README.md)、[v3.3 修正](tools/client_patches/REGISTRATION_CONTROL_FIX_V3_3.md)、[v3.3 交付事实表](tools/client_patches/V3_3_DELIVERY_AND_ACCEPTANCE.md) |
| 设计接入与运维 | [GATEWAY.md](server/docs/GATEWAY.md)、[GATEWAY_SECURITY_GM.md](server/docs/GATEWAY_SECURITY_GM.md) |
| 了解历史研究 | [work 索引](work/dream-world-connect-login-map/INDEX.md)，客户端侧权威现状 [client-status-20261012.md](work/dream-world-connect-login-map/report/client-status-20261012.md) |

归档目录里的文档保留的是写作当时的“下一步 / 分支 / 计数”，不应静默把它们理解为最新承诺；现行状态只看 `docs/STATUS.md`。

### 14.2 常见问题

**Q：现在能一条命令启动游戏服务端吗？**

不能。可以启动复核工具，不等于已有游戏账号、地图、战斗或持久化服务。

**Q：是否需要现在就安装 PostgreSQL？**

运行数据复核 API/网页不需要。PostgreSQL 是游戏服务端长期设计方向，不是复核工具当前必需依赖。

**Q：地图编辑器测试全绿，为什么还标为有问题？**

现有用例没有覆盖所有复杂压缩路径。独立对照已经发现长度正确但内容错误、超长被截断和导出覆盖源文件的问题；测试通过只能说明所覆盖断言通过。

**Q：为什么历史文档里有两个“68 项测试”？**

一个属于只读复核工具的独立验收套件（仍为 68），一个是地图编辑器 PR #25 时的计数（PR #27 后已是 82）。目录、对象和证据不同，不能互相替代；现行计数以 `docs/STATUS.md` 为准。

**Q：资源编辑器 / UI 编辑器能直接改线上客户端吗？**

不建议。它们生成新包、原包不动，但与原版客户端的最终兼容性要在 Windows 测试副本里进游戏验证；曾用 0.3.3 / 0.5.2 之前版本新增过条目的包，先用新版重新保存一次修复目录。

**Q：网页正常打开，是否代表数据可以作为正式规则？**

不是。网页专门展示“复核候选，非正式规则”，包括隔离、缺失、覆盖与歧义。浏览成功不等于内容获得生产准入。

**Q：v3.3 是否已经证明解决黑屏和所有界面问题？**

已定位旧 v3 的具体错误，并对后续候选执行离线/兼容性检查；但 v3.3 的 Windows 原生验收仍待反馈，不能提前作此保证。

**Q：能否直接运行旧 Mock 来补全链路？**

不建议。它是历史实验入口，有协议行为和客户端修改相关风险。先审查代码与参数、副作用和目标副本，不能把它当正式服务端基线。

**Q：为什么保留旧报告而不全部删除？**

旧报告是证据演进记录。应标注被推翻的结论和新依据，防止后续工作再次依赖错误假设；保留历史不意味着认可旧结论。

## 15. 资源使用与安全提醒

- 仓库包含既有客户端程序、资源及其研究材料。能克隆到这些文件，不代表获得原游戏程序、素材、商标或数据的再分发/商业使用授权。
- 当前根目录未见统一的 `LICENSE` 声明；不要自行推断所有文件都属于同一种开源许可。使用和分发前应逐项核对权利与授权范围。
- 未完成验证的 EXE、FLS 补丁和地图解码结果只应用于受控研究与测试，不应作为正式发行或生产规则。
- 不要求关闭杀毒或系统保护，不提供绕过安全软件的操作步骤。
- 对未知二进制、旧 Python 运行时和恢复脚本使用隔离环境；只执行明确审查过的工具与片段。

---

**项目原则：能展示不等于能运行，能运行不等于正确，测试通过不等于原生验收完成。所有完成声明都应有明确范围、版本和可追溯证据。**
