# mcp — 标准 MCP Server 占位

> 状态：占位，未实现。

未来模块候选：

| 模块 | 职责 |
|---|---|
| `server.py` | MCP Server 生命周期 |
| `tools.py` | 工具 schema、调用分发、结果封装 |
| `resources.py` | 报告 / 日志资源暴露 |
| `errors.py` | MCP 错误到探针错误码映射 |

第一阶段只读工具草案：

```text
client_ping
client_get_runtime_info
client_get_probe_report
client_get_module_status
client_get_native_api_status
client_read_probe_log
```

控制类工具默认不注册或返回未授权，直到 M4 白名单和 Windows 验收完成。
