# tests — 测试占位

> 状态：占位，当前没有可运行测试。

未来测试候选：

```text
test_protocol.py
test_ipc_fake_bridge.py
test_mcp_tools.py
test_stdio_transport.py
test_http_transport.py
test_multi_client_lock.py
test_probe_static.py
test_build_probe_package.py
```

## 测试分层

1. **协议单测**：消息封装、错误码、脱敏。
2. **fake bridge 测试**：Linux 沙箱验证 MCP Server，不连接真实客户端。
3. **传输测试**：stdio / HTTP。
4. **并发锁测试**：多个 MCP 客户端只读并发、控制独占。
5. **探针静态测试**：Python 2.5 语法 / 自写代码边界。
6. **构建测试**：输入包不变、输出包可校验、未涉及条目不变。
7. **Windows 实机验收**：见 [WINDOWS_ACCEPTANCE.md](../docs/WINDOWS_ACCEPTANCE.md)。

## 结果口径

- fake probe 通过 ≠ 真实客户端通过。
- Linux 通过 ≠ Windows 通过。
- 文档完成 ≠ MCP 可用。
- 跳过 / 未执行不算通过。
