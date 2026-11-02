# src — 现代 Python MCP 宿主源码占位

> 状态：占位，未实现。

未来包名：

```text
mxsj_client_mcp
```

目标运行环境：Windows / Linux 上的现代 Python ≥ 3.10。  
它不是客户端内探针；客户端内探针位于 `../client_probe/`，需要适配客户端老 Python VM。

未来职责：

- 标准 MCP Server；
- stdio / Streamable HTTP 传输；
- 与客户端探针的本机 IPC；
- 会话、锁、脱敏、审计；
- 报告存储与查询。

当前没有 `pyproject.toml`、`run.py` 或可导入包；M0 只写文档和目录。
