# src — 现代 Python MCP 宿主源码

> 状态：已实现只读 MCP 宿主。日期：2026-11-02。

包名：`mxsj_client_mcp`。运行环境为 Windows / Linux 上的现代 Python ≥ 3.10；它不是客户端内探针。客户端探针位于 `../client_probe/`，适配客户端老 Python VM。

当前职责：

- 标准 MCP Server，六个只读工具；
- stdio 与本机 Streamable HTTP 传输；
- fake probe、报告文件快照桥、本机 IPC 后端；
- 协议封装、会话标识、脱敏基础。

尚未实现：控制类工具、独占控制锁、实时 IPC 实机验收、场景测试。
