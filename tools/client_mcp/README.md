# client_mcp — 客户端原生 MCP 接入工具

> 状态：**M3 只读接入**：stdio 与本机 Streamable HTTP 已实现；支持 fake probe、本机 IPC 参数和报告文件快照桥。
> 日期：2026-11-02。Windows 客户端探针报告已通过 stdio 被 MCP 编程工具读取；HTTP 实机与实时 IPC 尚未验收。

运行：`python tools/client_mcp/run.py --transport stdio`，依赖 `pip install -e tools/client_mcp`。Windows 也可使用 `start_client_mcp.bat` 启动，`--check-only` 仅检查环境；`build_exe.bat` 可构建 EXE。客户端配置见 [configs/README.md](configs/README.md)。当前支持 stdio 与本机 Streamable HTTP；后端可选 fake probe、本机 IPC 参数和 `--report-file` 报告快照桥。控制操作尚未实现。

## 1. 目标

为《夢想世界》台服客户端测试副本提供一套**标准 MCP Server**，让支持 MCP 的编程工具可以接入同一套客户端原生测试能力：

```text
Cursor / Claude Code / Cline / Continue / 其他 MCP Client
        │ 标准 MCP：stdio 或 Streamable HTTP
        ▼
MXSJ Client MCP Server
        │ 本机 IPC
        ▼
客户端内探针 / 后续原生桥
        │
        ▼
真实 Windows 游戏客户端测试副本
```

第一阶段不是外部键鼠自动化；目标是在客户端自己的脚本 VM 内加载自写探针，读取真实客户端内部状态。后续受控操作必须逐项白名单验证。

## 2. 当前边界

- 不默认启动根目录 Mock；Mock 有写 `nocheck`、监听地址等副作用。
- 已实现六个只读 MCP 工具；控制类工具、实时 IPC 实机验收和场景测试仍未完成。
- `--report-file` 是报告快照桥，`client_ping` 仅表示报告文件当前可读，不代表游戏进程实时存活。

## 3. 输入包与基线

用户修改版 `script.fls` 已收到并做只读登记/差异核对；不得覆盖仓库原包或用户包。流程见：

- [SCRIPT_FLS_HANDOFF.md](docs/SCRIPT_FLS_HANDOFF.md)

原始锁定基线仍为：

```text
data/script.fls
SHA-256: 8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72

tools/decompiler/script_fls_keys.json
SHA-256: 43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb
```

## 4. 目录结构

```text
tools/client_mcp/
├─ README.md
├─ docs/
│  ├─ ARCHITECTURE.md
│  ├─ PROTOCOL.md
│  ├─ MCP_CLIENTS.md
│  ├─ SECURITY.md
│  ├─ SCRIPT_FLS_HANDOFF.md
│  ├─ WINDOWS_ACCEPTANCE.md
│  └─ IMPLEMENTATION_PLAN.md
├─ src/
│  └─ mxsj_client_mcp/
│     ├─ core/          # 协议、IPC、会话、状态、锁
│     ├─ mcp/           # 标准 MCP Server、工具、资源
│     └─ transports/    # stdio / Streamable HTTP
├─ client_probe/        # 客户端老 Python VM 内探针与构建入口
├─ configs/             # 各编程工具接入示例
└─ tests/               # 协议、fake bridge、传输、并发锁测试
```

现有 Python 包提供六个只读工具、fake probe、报告文件桥和本机 IPC 后端；客户端探针已能在 Windows 测试副本 VM 内写报告。控制类工具仍未实现。

## 5. 文档入口

| 文档 | 内容 |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | 总体架构、部署模式、数据流 |
| [PROTOCOL.md](docs/PROTOCOL.md) | 探针与 MCP 宿主之间的 IPC 协议草案 |
| [MCP_CLIENTS.md](docs/MCP_CLIENTS.md) | 标准 MCP 工具面、stdio / HTTP、多编程工具接入 |
| [SECURITY.md](docs/SECURITY.md) | 白名单、鉴权、脱敏、审计、测试副本边界 |
| [SCRIPT_FLS_HANDOFF.md](docs/SCRIPT_FLS_HANDOFF.md) | 用户修改版 `script.fls` 的交付、登记、差异核对 |
| [WINDOWS_ACCEPTANCE.md](docs/WINDOWS_ACCEPTANCE.md) | Windows 实机验收步骤与报告格式 |
| [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | 分阶段实施计划和验收门槛 |

## 6. 第一版最小闭环

第一版目标不是全功能控制，而是：

```text
用户修改版 script.fls
  -> 只读登记 / 差异核对
  -> 生成测试副本探针包
  -> Windows 客户端加载探针
  -> 探针通过本机 IPC 上报
  -> 标准 MCP Server 暴露只读工具
  -> 至少两个 MCP 编程工具成功读取报告
```

在真实 Windows 客户端验证前，不得宣称“原生接入完成”。
