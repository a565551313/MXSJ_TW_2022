# mxsj_client_mcp — 只读 MCP 宿主包

> 状态：已创建并实现只读工具。日期：2026-11-02。

```text
mxsj_client_mcp/
├─ __init__.py
├─ run.py          # CLI：stdio / loopback HTTP
├─ core/           # 协议、会话、脱敏
├─ mcp/            # 标准 MCP Server 与工具
└─ transports/     # fake probe、报告文件/IPC 后端、HTTP app
```

约束：

- `core/` 不依赖 Qt，不依赖 Windows 专有 API。
- `mcp/` 只封装标准 MCP 工具，不直接访问游戏内存。
- `transports/` 负责传输与后端选择，不把传输逻辑混入业务状态。
- 所有文本 IO 显式 `encoding="utf-8"`。
- 不在 import 时启动服务、连接客户端或写文件。
