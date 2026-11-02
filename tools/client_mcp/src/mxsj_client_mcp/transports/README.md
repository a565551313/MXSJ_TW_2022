# transports — MCP 传输层占位

> 状态：占位，未实现。

未来支持：

```text
stdio.py
http.py
```

## stdio

- 由本机 MCP 编程工具启动；
- 不默认开放网络端口；
- 适合 Windows 本机 IDE / Agent。

## Streamable HTTP

- 默认监听 `127.0.0.1`；
- 非本机监听必须显式开启并鉴权；
- 支持多 MCP 客户端；
- 控制类请求需要会话锁；
- 不默认暴露公网。

传输层不得包含游戏逻辑；游戏状态和探针命令由 `core/` 与 `mcp/` 处理。
