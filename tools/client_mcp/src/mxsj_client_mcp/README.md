# mxsj_client_mcp — 包占位

> 状态：占位，未创建 Python 包。

未来目录：

```text
mxsj_client_mcp/
├─ __init__.py
├─ __main__.py
├─ core/
├─ mcp/
└─ transports/
```

约束：

- `core/` 不依赖 Qt，不依赖 Windows 专有 API；Windows 专有 IPC 通过适配层隔离。
- `mcp/` 只封装标准 MCP 工具，不直接访问游戏内存。
- `transports/` 负责 stdio / HTTP，不把传输逻辑混入业务状态。
- 所有文本 IO 显式 `encoding="utf-8"`。
- 不在 import 时启动服务、连接客户端或写文件。
