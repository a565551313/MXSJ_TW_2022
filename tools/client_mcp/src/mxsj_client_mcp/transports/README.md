# transports — MCP 传输与探针后端

> 状态：stdio 与本机 Streamable HTTP 已实现。日期：2026-11-02。

## stdio

- 由本机 MCP 编程工具启动；
- 不默认开放网络端口；
- 适合 Windows 本机 IDE / Agent；
- 入口在 `../run.py`，使用 MCP SDK 的 `stdio_server`。

## Streamable HTTP

- `http.py` 提供本机 ASGI app，端点 `/mcp`；
- 只允许 `127.0.0.1` / `localhost` / `::1`；
- 强制 Bearer token，Host/Origin 白名单，256 KiB body 限制，最多 16 会话；
- 支持多 MCP 客户端只读并发；
- 不默认暴露公网，当前拒绝非本机监听。

## 探针后端

- `fake_probe.py`：Linux 开发/测试用合成数据；
- `ipc_probe.py`：`FileProbeBackend` 读取报告快照，`IpcProbeBackend` 连接本机探针 TCP；
- 报告文件桥不是实时进程会话，`client_ping` 仅表示文件当前可读。

传输层不得包含游戏逻辑；游戏状态和探针命令由 `core/` 与 `mcp/` 处理。
