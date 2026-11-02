# mcp — 标准 MCP Server

> 状态：已实现六个只读工具。日期：2026-11-02。

| 模块 | 职责 |
|---|---|
| `server.py` | MCP Server 生命周期、工具注册与分发 |
| `tools.py` | 工具 schema、参数校验、结果封装 |

当前只读工具：

```text
client_ping
client_get_runtime_info
client_get_probe_report
client_get_module_status
client_get_native_api_status
client_read_probe_log
```

控制类工具默认不注册，直到 M4 白名单和 Windows 验收完成。资源暴露、错误码映射等后续再补。
