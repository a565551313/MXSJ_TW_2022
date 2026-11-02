# client_mcp — 客户端原生 MCP 接入工具

> 状态：**M3 只读接入**。stdio 报告桥已在 Windows 实机验证；本机 Streamable HTTP 已实现并在 Linux 宿主测试通过；**实时 IPC 与客户端控制仍未完成**。
> 日期：2026-11-03。

## 0. 一键启动（用户只看这一节）

**双击** `tools/client_mcp/启动客户端MCP.bat`，然后等窗口显示：

```text
==============================================================
 MXSJ 客户端 MCP 已启动
--------------------------------------------------------------
 编程工具接入地址：http://127.0.0.1:8765/mcp
 配置文件：        ...\tools\client_mcp\runtime\mcp_client_config.json
 客户端报告：      ...（找到就显示路径，没找到会写“启动游戏后会自动发现”）
--------------------------------------------------------------
 关闭这个窗口即停止服务。不需要在这里输入任何命令。
==============================================================
```

它自己会做完这些事，**不需要你输入任何命令**：

| 它会做 | 说明 |
|---|---|
| 检查 Python | 版本不够会在窗口里给出下载地址 |
| 检查依赖 | 缺 `mcp` / `uvicorn` / `starlette` 时自动安装；官方源失败自动换清华、阿里云镜像 |
| 生成访问令牌 | 随机生成一次，保存在 `runtime/http_token.txt`，以后复用 |
| 选择端口 | 8765 被占用就自动往后找空闲端口 |
| 查找客户端报告 | 在仓库根、`data/`、`log/`、`tools/client_mcp/runtime/` 里找最新的 `mxsj_probe_report.txt` |
| 生成编程工具配置 | 写 `runtime/mcp_client_config.json`，可直接导入 |
| 启动服务并显示状态 | 找到报告时窗口会打印一行“已找到客户端探针报告” |

游戏由你自己启动；本工具不代启动游戏，也不会在你没有双击时后台运行。

### 编程工具怎么接

1. 打开编程工具的 MCP 设置，选择“导入配置文件”或“从 JSON 添加”；
2. 选 `tools/client_mcp/runtime/mcp_client_config.json`（内容形如）：

```json
{
  "mcpServers": {
    "mxsj-client": {
      "url": "http://127.0.0.1:8765/mcp",
      "headers": {"Authorization": "Bearer <自动生成的令牌>"}
    }
  }
}
```

3. 调用 `client_ping` 与 `client_get_probe_report`。

不同工具字段名可能不同；如果它只支持“手动填写”，照抄上面的 `url` 和 `Authorization` 即可，令牌就在 `runtime/http_token.txt` 里。**令牌不要发到聊天、不要提交 Git。**

### 出问题时

窗口不会一闪而过，失败会停住。只需要把**窗口里的文字**和 `tools/client_mcp/启动日志.txt` 发回来，不需要你敲任何命令排查。

### 硬性规则

本工具链的开发和测试环节**一律不要求用户使用命令行**：不要求用户 `pip install`、`cd`、运行 `python xxx.py`、设置环境变量、手写 JSON、生成令牌或查端口。全部由一键启动器完成。这条规则写在 [`docs/ONE_CLICK.md`](docs/ONE_CLICK.md) 与仓库根 `AGENTS.md`。

## 1. 目标

为《夢想世界》台服客户端测试副本提供一套**标准 MCP Server**，让支持 MCP 的编程工具接入同一套客户端原生测试能力：

```text
Cursor / Claude Code / Cline / Continue / 其他 MCP Client
        │ 标准 MCP：stdio 或 Streamable HTTP
        ▼
MXSJ Client MCP Server
        │ 本机 IPC（目标）/ 报告文件快照（现状）
        ▼
客户端内探针
        │
        ▼
真实 Windows 游戏客户端测试副本
```

第一阶段不是外部键鼠自动化，而是在客户端自己的脚本 VM 内加载自写探针，读取真实客户端内部状态。控制类操作必须逐项白名单验证后再开放。

## 2. 当前边界（如实）

- **已经做到**：探针在 Windows 客户端 Python 2.5 VM 内执行并写出报告；MCP 编程工具经 stdio 读取该报告。
- **还没做到**：MCP Server 与运行中的客户端实时通信。`--report-file` 是**报告快照桥**，`client_ping` 只表示报告文件当前可读，**不代表游戏进程存活**。
- **还没做到**：控制类工具、独占锁、登录 / 选角 / 进图 / NPC / 传送场景测试。
- 不默认启动根目录 Mock；Mock 有写 `nocheck`、监听地址等副作用。

## 3. 文件与目录

```text
tools/client_mcp/
├─ 启动客户端MCP.bat    # 用户唯一需要双击的文件
├─ bootstrap.py         # 自检 + 自动装依赖 + 自动生成配置 + 启动服务
├─ runtime/             # 自动生成：令牌、端口、MCP 配置（不入库）
├─ src/mxsj_client_mcp/ # core / mcp / transports
├─ client_probe/        # 客户端 Python 2.5 探针与构建入口
├─ configs/             # 各编程工具接入示例
├─ docs/                # 架构、协议、客户端接入、验收
└─ tests/               # 协议、传输、并发锁、启动器测试
```

`data/script.fls` 直接在仓库内就地修改（用户明确授权并自行备份），不再生成仓外修复包，也不再要求用户解压 / 覆盖任何外部文件。

## 4. 文档入口

| 文档 | 内容 |
|---|---|
| [ONE_CLICK.md](docs/ONE_CLICK.md) | 一键启动的用户流程与“禁止要求用户使用命令行”规则 |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | 总体架构、部署模式、数据流 |
| [PROTOCOL.md](docs/PROTOCOL.md) | 探针与 MCP 宿主之间的 IPC 协议草案 |
| [MCP_CLIENTS.md](docs/MCP_CLIENTS.md) | 标准 MCP 工具面、stdio / HTTP、多编程工具接入 |
| [SECURITY.md](docs/SECURITY.md) | 白名单、鉴权、脱敏、审计、测试副本边界 |
| [SCRIPT_FLS_HANDOFF.md](docs/SCRIPT_FLS_HANDOFF.md) | `script.fls` 就地修改、备份与核对口径 |
| [WINDOWS_ACCEPTANCE.md](docs/WINDOWS_ACCEPTANCE.md) | Windows 实机验收（双击流程） |
| [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | 分阶段实施计划和验收门槛 |

## 5. 第一版最小闭环

```text
仓库内 data/script.fls（就地修目录 + 换掉畸形钩子）
  -> 测试副本加载探针并在主循环里常驻
  -> 探针经本机 IPC 实时响应
  -> 标准 MCP Server 暴露只读工具
  -> 两个 MCP 编程工具（一个 stdio、一个 HTTP）都读到运行中的客户端
  -> 关闭客户端后 client_ping 失败
```

在真实 Windows 客户端验证前，不得宣称“原生接入完成”。当前已完成的是“探针产出报告 + 报告被读取”，不是实时直连。
