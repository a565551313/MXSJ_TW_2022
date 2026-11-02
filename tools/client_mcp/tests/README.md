# tests — 宿主与探针测试

> 状态：已有可运行测试。日期：2026-11-02。

当前覆盖：

```text
test_protocol.py
test_fake_probe.py
test_file_probe.py
test_stdio.py
test_http.py
test_probe_core.py
test_probe_ipc.py
test_probe_package.py
test_script_fls_compare.py
test_bootstrap.py
```

## 测试分层

1. **协议单测**：消息封装、错误码、脱敏。
2. **fake bridge 测试**：Linux 沙箱验证 MCP Server，不连接真实客户端。
3. **传输测试**：stdio / HTTP 鉴权 / HTTP 双客户端并发。
4. **探针静态测试**：Python 2.5 语法 / 自写代码边界。
5. **构建测试**：输入包不变、输出包可校验、未涉及条目不变。
6. **Windows 实机验收**：见 [WINDOWS_ACCEPTANCE.md](../docs/WINDOWS_ACCEPTANCE.md)。

## 结果口径

- fake probe 通过 ≠ 真实客户端通过。
- Linux 通过 ≠ Windows 通过。
- 报告文件桥通过 ≠ 实时 IPC 通过。
- 文档完成 ≠ MCP 可用。
- 跳过 / 未执行不算通过。
