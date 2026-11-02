# client_mcp — 客户端原生 MCP 接入工具

> 状态：**M0 文档骨架 / 未实现**。  
> 日期：2026-11-02。分支：`arena/6a13368c-mxsj-tw-2022`。  
> 本目录目前只有目录结构与文档；没有可运行 MCP Server，没有客户端探针产物，没有修改原始 `data/script.fls`。

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

第一阶段不是外部键鼠自动化，也不是浏览器测试；目标是在客户端自己的脚本 VM 内加载自写探针，读取真实客户端内部状态。后续受控操作必须逐项白名单验证。

## 2. 当前边界

- 不修改仓库原始 `data/script.fls`。
- 不修改 `mx.exe`、`mxmain.dll`、`exe/python27.dll`、key DB。
- 不执行反编译 / 恢复出来的游戏模块。
- 不默认启动根目录 Mock；Mock 有写 `nocheck`、监听地址等副作用。
- 不提供任意 `eval/exec`、任意 shell、任意内存读写。
- 不接正式服，不绕过保护机制，不记录真实账号密码。
- 文档中的协议、工具名、配置均为**草案**，不代表已经实现。

## 3. 等待用户输入

用户将提供已经做过多次修改的 `script.fls`。收到后不能直接覆盖仓库原包，必须先做输入登记和只读差异核对。流程见：

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

目前各子目录以 README 占位，说明未来职责；尚未创建可运行 Python 包。

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
