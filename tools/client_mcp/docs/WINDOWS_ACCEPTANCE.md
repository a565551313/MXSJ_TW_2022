# Windows 实机验收草案

> 状态：草案，未执行。日期：2026-11-02。  
> 本文件描述未来验收步骤；当前没有可运行探针、MCP Server 或测试包。

## 1. 验收前提

- 用户已提供修改版 `script.fls`。
- 已完成输入登记和只读差异核对。
- 已生成探针测试包，并确认未覆盖原始包。
- Windows 测试副本与日常客户端隔离。
- 使用假账号 / 测试账号，不使用真实凭据。
- 不接正式服。

## 2. 环境记录

验收报告必须记录：

```json
{
  "windows_version": "",
  "python_version": "",
  "client_build": "",
  "script_fls_sha256": "",
  "probe_build_sha256": "",
  "mcp_server_version": "",
  "transport": "stdio / http",
  "mcp_clients": [],
  "test_server": "none / mock_v2 / other-isolated",
  "run_id": ""
}
```

## 3. M2 只读探针验收

步骤：

1. 将探针测试包放入 Windows 测试副本。
2. 启动客户端。
3. 确认探针模块加载。
4. 确认探针生成本地报告或建立 IPC。
5. 读取报告，确认包含：
   - VM 信息；
   - 探针版本；
   - 客户端测试包 SHA-256；
   - 模块加载状态；
   - 原生模块可用性；
   - 错误 / 异常摘要。
6. 确认没有记录账号密码。
7. 关闭客户端后确认无残留探针进程。

通过标准：

```text
客户端真实进程内探针报告可读；
报告字段与输入包哈希绑定；
无敏感信息；
无原始包修改。
```

## 4. M3 MCP Server 验收

步骤：

1. 启动 MCP Server。
2. 使用 fake probe 在 Linux 验证协议。
3. 在 Windows 连接真实探针。
4. 编程工具 A 通过 stdio 接入。
5. 编程工具 B 通过 HTTP 接入。
6. 两个工具分别调用：
   - `client_ping`
   - `client_get_probe_report`
7. 确认返回一致且脱敏。
8. 确认多客户端只读并发不冲突。

通过标准：

```text
至少两个不同 MCP 编程工具成功读取真实客户端探针报告；
stdio 与 HTTP 均可用；
控制锁未开放或默认拒绝。
```

## 5. M4 受控操作验收

只读通过后，才选择一个最小受控操作，例如：

- 读取当前界面状态；
- 触发一个已验证按钮消息；
- 打开一个已知安全界面。

验收必须记录：

```text
操作前状态
调用参数摘要
操作后状态
耗时
错误码
是否独占锁
审计日志
```

通过标准：

```text
操作在客户端内部真实执行；
状态变化可被探针读取；
未授权命令被拒绝；
敏感信息不泄露。
```

## 6. M5 场景验收

候选最小场景：

```text
登录 -> 选角 -> 进图
```

后续扩展：

```text
NPC 对话
传送
断线重连
异常协议
多客户端交互
```

每个场景必须有：

- 前置条件；
- 步骤；
- 断言；
- 超时；
- 失败截图 / 日志可选；
- 报告 JSON。

## 7. 报告位置

```text
../mxsj-client-mcp-out/windows/acceptance/<run_id>/
├─ environment.json
├─ probe_report.json
├─ mcp_calls.jsonl
├─ steps.json
├─ result.json
└─ evidence/
```

## 8. 不可接受的“通过”

以下不能算通过：

- Linux fake probe 通过；
- 只修改文档；
- 只启动 MCP Server 但没有真实探针；
- 只看到客户端窗口但没有内部报告；
- 只靠截图判断；
- 跳过 Windows 实测；
- 使用真实账号；
- 覆盖原始包。
