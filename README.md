# MXSJ_TW_2022 ·《夢想世界》客户端研究与 Python 服务端重建

> **状态更新：2026-10-12**

> 本仓库围绕 TW v2.27.2 客户端材料，开展资源/协议研究、静态数据复核、可逆客户端界面改造，以及长期 Python 回合制服务端设计。

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
8. [客户端注册界面预览](#8-客户端注册界面预览)
9. [Python 游戏服务端架构](#9-python-游戏服务端架构)
10. [测试与证据](#10-测试与证据)
11. [已知风险与后续计划](#11-已知风险与后续计划)
12. [协作和变更约定](#12-协作和变更约定)
13. [文档导航与常见问题](#13-文档导航与常见问题)
14. [资源使用与安全提醒](#14-资源使用与安全提醒)

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

截至本次更新：

- 协调分支：`arena/b53b33e6-mxsj-tw-2022`。
- 地图编辑器 [PR #25](https://github.com/a565551313/MXSJ_TW_2022/pull/25) 已按用户授权合入协调分支，合并提交 `6538f92`。
- 累计工作已开为面向 `master` 的 **[Draft PR #26](https://github.com/a565551313/MXSJ_TW_2022/pull/26)**，尚未合入 `master`。
- #26 包含分支累计的研究、复核工具、客户端预览、设计与编辑器工作，**不是只有编辑器的小改动**。
- 合并 #25 是带已知问题的集成决定，不表示缺陷已经修复；问题清单见 [PR25_REVIEW.md](map_editor/PR25_REVIEW.md)。

以上为日期快照。后续请结合最新 Git 历史和 PR 状态判断，不把历史状态当作永久结论。

## 2. 当前能力与完成度

| 方向 | 已有内容 | 当前边界 |
|---|---|---|
| 客户端材料索引 | `script.fls` 的 5002 条索引，模块映射与研究记录 | 条目有索引不等于逻辑全部恢复 |
| 静态数据提取 | 受限解析、异常复核、可复现导出、来源与覆盖证据 | 不是运行原客户端脚本，也不是正式生产配置 |
| 首批复核数据 | `batch_001`，递归共 17 个 CSV、总计 22 个文件 | 保留隔离、缺失、歧义；不发布到 `game_data` |
| 复核 API/网页 | 只读目录加载、查询、搜索、分页、证据展示 | 已有集成验收；不是游戏网关或 GM 后台 |
| 地图编辑器 | Python/Pillow 格式引擎、PySide6 界面、扫描/渲染/导出 | 部分 GIRB 结果错误；源文件保护与启动分派待修 |
| 注册 UI | v3.3 离线候选，三个字段、本地校验、按钮与光标修正 | 无真实注册/保存；Windows 原生验收待完成 |
| 游戏服务端 | 21 个一级责任区、类型契约、81 个细分工作包 | 业务运行、账号数据库、地图与战斗闭环未实现 |
| 网关/安全/GM | 可拆分设计、职责、权限、审计和故障边界 | 设计文档，不是已经启动的安全服务 |
| 根目录 Mock | 历史协议/客户端联调实验脚本 | 不作为正式服务端；默认不启动，先检查副作用 |

## 3. 仓库结构

```text
MXSJ_TW_2022/
├── README.md                     项目总览（本文）
├── AGENT_HANDOFF.md               详细交接与客户端 v3.3 状态快照
├── mx.exe / *.dll / config/       客户端程序及相关材料
├── data/                         FLS 样本（包括 script.fls）
├── map/                          已纳入仓库的地图样本
├── resource/                     客户端资源材料
├── mock_server.py                历史联调 Mock，非正式服务端
├── map_editor/
│   ├── README.md                 编辑器使用与格式说明（部分历史结论已过时）
│   ├── PR25_REVIEW.md             最新独立审查及待修复事项
│   ├── run.py                    CLI / GUI 入口
│   ├── src/map_editor/           core、client、ui 分层实现
│   ├── tests/                    编辑器回归测试
│   └── build.bat / *.spec        Windows 打包脚本与配置
├── tools/
│   ├── client_patches/           可逆注册 UI 预览、冻结资产、测试与审计
│   ├── decompiler/               字节码/归档研究工具和相关材料
│   ├── data-parser/              历史数据解析工具
│   ├── data-export/              历史数据导出工具
│   └── data_browser/             历史浏览工具，非新复核网页入口
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
├── notes/handoff/               交接时重新核验的结构化证据
└── work/dream-world-connect-login-map/
    ├── report/                  客户端/地图/协议的阶段研究报告
    ├── tools/                   专项研究工具
    └── artifacts/               已提交的研究制品与证据
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
- `ui/widgets.py`：PySide6 图形绑定。
- `run.py`：入口，必须显式区分扫描和 GUI。

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
```

将示例路径替换为真实测试副本。不要把 `--export-json` 的目标写成任何源 `.map` 或其它客户端资源路径。导出同名文件也可能覆盖既有输出，应选择新文件名。

Windows 打包入口是 `map_editor/build.bat`。它会安装依赖、执行测试并调用 PyInstaller；当前无参数启动分派仍有缺陷，且没有完成 Windows EXE 实机验收，因此不能将“存在打包脚本”等同于“已有可用安装包”。

### 7.3 合并后仍未修复的问题

| 优先级 | 问题 | 已有证据 / 影响 |
|---|---|---|
| P1 | GIRB 短匹配基址经验修改产生假成功 | 1034/1035 共 429 扇区，PR 接受 144 个，其中只有 129 个与原子程序逐字节一致，新增 15 个全部错误 |
| P1 | JSON 导出可覆盖源地图 | 临时副本已复现 `.map` 被 JSON 截断覆盖 |
| P2 | 超长解码被裁剪后计为成功；截断操作数被补零接受 | 真实扇区 2405 字节错误输出可截成 2400 后通过 |
| P2 | 无参数 EXE 入口不打开 GUI | 只有 `--gui` 进入图形分支，而打包配置关闭控制台 |
| 审查项 | 同 PR 修改了 Mock 协议行为 | 包括 opcode 和扩展长度 3→2 字节，不能称为“纯注释” |

这不是要求现在必须全部解出：**尚未支持的扇区可以明确失败；错误数据不应伪装成成功。** 此前“101 张图中若干张完全解出”的统计不能在修正后直接沿用，需要用可靠标准重新核验。

先读 [独立审查与验收要求](map_editor/PR25_REVIEW.md)，再读 [编辑器 README](map_editor/README.md) 和 [原交接报告](work/dream-world-connect-login-map/report/map-editor-handover-20261012.md)。后两者保留了历史结论，冲突时应以可复现的新证据判断，不能用旧成功率反驳字节级差异。

## 8. 客户端注册界面预览

### 8.1 当前版本和交互范围

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

### 8.2 必须区分的版本事实

| 版本 | 真实状态 |
|---|---|
| v1 / v2.1 | 曾收到局部导航/表单反馈，不能推广为后续版本验收 |
| v3 | 用户实际报告游戏窗口黑屏，已停用，不应继续分发 |
| v3.2 | 用户截图显示新协议/表单，但按钮、说明入口和光标等存在缺陷 |
| v3.3 | 已修正相关控件接口、按钮图片与层级；90 项测试、22 项 CPython 审计通过；**尚未收到原生验收反馈** |

v3.3 只修改 FLS 的 entry `337` / `4007`，其余 5000 条保持不变，原选区后条款/登录 entry `4806` 未改。原始 FLS 与密钥数据库不应被覆盖。

### 8.3 重建、安装和恢复

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

安装细节、已交付候选的哈希/链接、原生复测清单见 [详细交接](AGENT_HANDOFF.md)；开发说明见 [客户端补丁 README](tools/client_patches/README.md)、[v3.3 修正记录](tools/client_patches/REGISTRATION_CONTROL_FIX_V3_3.md)、[v3 黑屏自查](tools/client_patches/V3_STARTUP_SELF_AUDIT.md)。

## 9. Python 游戏服务端架构

### 9.1 当前是架构与契约，不是游戏运行时

`server/src/mxsj_server/` 已划分启动、接入、协议、契约、状态运行时、持久化、观测与业务模块边界。公开类型可导入、目录可检查，但业务 `Protocol` 声明不是实现，字段顺序也不能直接作为客户端封包格式。

当前没有可游玩服务端启动命令，没有正式数据库 schema/迁移链，也没有账号、建角、进入地图和回合战斗的端到端闭环。能启动的 `review_api` 是另一条独立工具链，不应被当作游戏服务器。

### 9.2 21 个一级责任区

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

### 9.3 已确定的设计方向

- 按权威数据所有权划分模块；跨模块不绕过公开接口直接改他人状态。
- 金钱、物品、奖励和附件领取等需要明确事务、幂等和审计，不以“最终大概一致”代替资产一致性。
- 回合制战斗明确行动收集、超时、回合推进、断线/重连视图和结算归属。
- 网关先允许同进程实现，但连接、会话、路由与业务分离，保留独立部署能力。
- 网关拆分不等于会话自动无损迁移或热重启；故障、重连、回送、幂等和版本边界需要落实。
- GM 使用私有管理入口、权限/审批和审计，不能复用玩家连接获得管理权限。
- PostgreSQL 是长期方向；依赖、迁移与部署基线仍需实现阶段锁定。

阅读：[模块清单](server/docs/MODULES.md)、[接口约定](server/docs/INTERFACES.md)、[战斗契约](server/docs/BATTLE.md)、[网关](server/docs/GATEWAY.md)、[网关安全与 GM](server/docs/GATEWAY_SECURITY_GM.md)、[基础能力缺口](server/docs/FOUNDATION_BACKLOG.md)。

## 10. 测试与证据

### 10.1 最近已记录结果

下表汇总已有执行记录，**不是声称每次编辑本 README 都重新运行了全部测试**。测试计数按范围列出，不应简单相加作为项目完成率。

| 范围 | 已记录结果 | 证据 / 局限 |
|---|---|---|
| 客户端补丁单元测试 | 90 通过 | [交接复核 JSON](notes/handoff/2026-10-12-checks.json) |
| CPython 2.5 执行审计 | 22 通过 | [v3.3 审计](tools/client_patches/V3_3_RUNTIME_AUDIT.json)，图形/输入/调度仍有替身边界 |
| 服务端架构 | 161 通过 | 证明目录/契约/静态边界，不证明玩法正确 |
| 文件名映射 | 96/96 | 不是 5002 个模块已全部恢复 |
| 批次核验 | 22 文件通过 | 递归含 17 CSV，仍为复核候选 |
| 复核目录 / API | 34 / 27 通过 | 已有阶段集成记录 |
| 复核网页 | 112 通过、9 在线项默认跳过 | 单独在线联调 12 通过包含相关在线项，不可直接累加 |
| 独立复核验收套件 | 68 通过 | 与地图编辑器的 68 项是不同套件 |
| 真实 Chromium | 16 场景完成 | 复核网页验收，不是游戏原生客户端验收 |
| 地图编辑器 | 合并 #25 后 68 通过 | 未覆盖全部已发现缺陷，不能据此信任 GIRB 输出 |

只读复核工具的完整结果见 [ACCEPTANCE.md](server/docs/review_browser/ACCEPTANCE.md)。历史报告中的临时绝对路径是当时运行坐标，不是稳定的安装依赖。

### 10.2 常用复跑命令

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

### 10.3 完整验收与旧 VM 审计

- 完整复核工具验收见 [验收复跑说明](server/docs/review_browser/ACCEPTANCE.md) 与 [独立检查工具](server/tools/review_browser_checks/README.md)。
- `acceptance_runner.py` 会生成报告并运行更多集成阶段，可能更新仓库中的证据文件；运行前查看工作区，运行后检查差异，不能把新报告无条件覆盖为“已通过”。
- 真实 Chromium 工具需独立准备；缺少时必须保留 `not_executed`，不能把 jsdom 当作真实浏览器。
- CPython 审计使用 `audit_visual_runtime.py --python25 /path/to/cpython-2.5.6/python --report /path/to/report.json`，仅审计指定片段，不执行整个恢复模块。
- 本次 README 编写不启动原生客户端、不重建交付包，也不自动执行根目录 Mock。

## 11. 已知风险与后续计划

### 11.1 优先处理的工作

1. **修复地图工具的错误成功和源资源保护。** 使用原解压子程序的独立字节级结果增加回归用例；失败保持未知，不靠修改测试期望掩盖错误。
2. **修复 GUI 启动并验证 Windows 打包。** 包含首次双击、无配置、选择目录、打开地图、导出和异常提示。
3. **完成 v3.3 原生验收闭环。** 按按钮、焦点、光标、遮罩、验证、返回、再次进入逐项记录，不把部分截图当成整体通过。
4. **独立审查协议行为修正。** 核对 `mock_server.py` 中 opcode、包长度与真实客户端处理，避免“注释修正”掩盖运行变化。
5. **继续数据证据复核。** 保留隔离与歧义，明确何时能进入正式配置；不要为了填满表而编造规则。
6. **落实第一条真实服务端链路。** 从网关、账号、区服角色范围和持久化边界入手，逐步打通注册至地图；不并行宣称全玩法已实现。

### 11.2 开发时的停止条件

- 原 FLS 或密钥数据库与目标版本不匹配：停止构建/覆盖。
- 客户端黑屏、启动失败、资源缺失：恢复已知状态，先定位，不连续盲发新候选。
- 数据解码返回长度正确但内容无法独立验证：不能宣布成功。
- 导出目标可能指向源资源或其路径别名：停止写入。
- 缺浏览器、样本、运行库或 Windows 环境：明确记录未执行，不把跳过当成通过。
- 数据异常尚未批准处理方式：保持隔离，不进入生产目录。

## 12. 协作和变更约定

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

## 13. 文档导航与常见问题

### 13.1 建议阅读顺序

| 目的 | 入口 |
|---|---|
| 接手整个项目 | [AGENT_HANDOFF.md](AGENT_HANDOFF.md)，再补读 [编辑器新审查](map_editor/PR25_REVIEW.md) |
| 了解服务端范围 | [server/README.md](server/README.md) |
| 找模块/玩法材料 | [MODULES.md](server/docs/MODULES.md)、[SUBSYSTEMS.md](server/docs/SUBSYSTEMS.md)、[材料目录](server/docs/catalog/DIRECTORIES.md) |
| 审核数据来源 | [CSV_READINESS.md](server/docs/CSV_READINESS.md)、[SOURCE_EVIDENCE.md](server/docs/SOURCE_EVIDENCE.md) |
| 启动复核网页 | [网页 README](server/apps/review_web/README.md)、[后端文档](server/docs/review_browser/BACKEND.md) |
| 核对复核工具验收 | [ACCEPTANCE.md](server/docs/review_browser/ACCEPTANCE.md) |
| 处理地图问题 | [PR25_REVIEW.md](map_editor/PR25_REVIEW.md)、[编辑器说明](map_editor/README.md) |
| 修改注册预览 | [客户端补丁说明](tools/client_patches/README.md)、[v3.3 修正](tools/client_patches/REGISTRATION_CONTROL_FIX_V3_3.md) |
| 设计接入与运维 | [GATEWAY.md](server/docs/GATEWAY.md)、[GATEWAY_SECURITY_GM.md](server/docs/GATEWAY_SECURITY_GM.md) |
| 了解历史研究 | [work 索引](work/dream-world-connect-login-map/INDEX.md) |

`AGENT_HANDOFF.md` 的主要基线早于地图 PR 集成；其中“下一步”和“当时未合并”等描述是历史快照。当前状态须结合本文及更新后的审查记录，不应静默把旧文档理解为最新承诺。

### 13.2 常见问题

**Q：现在能一条命令启动游戏服务端吗？**

不能。可以启动复核工具，不等于已有游戏账号、地图、战斗或持久化服务。

**Q：是否需要现在就安装 PostgreSQL？**

运行数据复核 API/网页不需要。PostgreSQL 是游戏服务端长期设计方向，不是复核工具当前必需依赖。

**Q：地图编辑器测试全绿，为什么还标为有问题？**

现有用例没有覆盖所有复杂压缩路径。独立对照已经发现长度正确但内容错误、超长被截断和导出覆盖源文件的问题；测试通过只能说明所覆盖断言通过。

**Q：为什么有两个“68 项测试”？**

一个属于只读复核工具的独立验收套件，一个属于地图编辑器。目录、对象和证据不同，不能互相替代。

**Q：网页正常打开，是否代表数据可以作为正式规则？**

不是。网页专门展示“复核候选，非正式规则”，包括隔离、缺失、覆盖与歧义。浏览成功不等于内容获得生产准入。

**Q：v3.3 是否已经证明解决黑屏和所有界面问题？**

已定位旧 v3 的具体错误，并对后续候选执行离线/兼容性检查；但 v3.3 的 Windows 原生验收仍待反馈，不能提前作此保证。

**Q：能否直接运行旧 Mock 来补全链路？**

不建议。它是历史实验入口，有协议行为和客户端修改相关风险。先审查代码与参数、副作用和目标副本，不能把它当正式服务端基线。

**Q：为什么保留旧报告而不全部删除？**

旧报告是证据演进记录。应标注被推翻的结论和新依据，防止后续工作再次依赖错误假设；保留历史不意味着认可旧结论。

## 14. 资源使用与安全提醒

- 仓库包含既有客户端程序、资源及其研究材料。能克隆到这些文件，不代表获得原游戏程序、素材、商标或数据的再分发/商业使用授权。
- 当前根目录未见统一的 `LICENSE` 声明；不要自行推断所有文件都属于同一种开源许可。使用和分发前应逐项核对权利与授权范围。
- 未完成验证的 EXE、FLS 补丁和地图解码结果只应用于受控研究与测试，不应作为正式发行或生产规则。
- 不要求关闭杀毒或系统保护，不提供绕过安全软件的操作步骤。
- 对未知二进制、旧 Python 运行时和恢复脚本使用隔离环境；只执行明确审查过的工具与片段。

---

**项目原则：能展示不等于能运行，能运行不等于正确，测试通过不等于原生验收完成。所有完成声明都应有明确范围、版本和可追溯证据。**
