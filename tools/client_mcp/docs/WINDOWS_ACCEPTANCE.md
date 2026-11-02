# Windows 实机验收草案

> 状态：部分执行。日期：2026-11-02。
> 已完成 Windows 探针报告与 stdio MCP 客户端读取；HTTP、实时 IPC、控制操作仍未验收。

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

## 9. 已记录的部分验收（2026-11-02）

用户回传 Windows 探针报告：

```text
python_version: 2.5.0
modules: sys / time / os loaded
native_api: unknown
probe_version: 0.1.0
```

用户 MCP 客户端 `mxsj-client-report` 调用结果：

```text
client_ping: ok=true, alive=true
client_get_probe_report: ok=true，返回上述报告
```

结论：

- M2 探针在客户端 VM 内执行并写报告：已由用户报告证明；
- M3 stdio 报告文件桥：已由用户 MCP 客户端调用证明；
- 报告未绑定包 SHA，不能强绑定到某个 `script.fls`；
- `--report-file` 是快照桥，`client_ping` 不代表实时进程存活；
- HTTP 第二客户端、实时 IPC、控制锁、场景测试仍未验收。

## 10. HTTP 第二客户端验收步骤（报告快照桥）

前提：stdio 报告桥已成功，且 `mxsj_probe_report.txt` 路径已知。HTTP 版复用同一报告文件，不需要替换游戏包。

1. 解压新的宿主包到独立目录，不要覆盖正在运行的 stdio 宿主目录。
2. 安装/检查依赖：

   ```powershell
   cd C:/path/to/client_mcp
   python -m pip install -e .
   python run.py --help
   ```

3. 生成随机 token：

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. 在 PowerShell 中启动 HTTP Server，保持窗口运行：

   ```powershell
   $env:MXSJ_MCP_HTTP_TOKEN="<上一步生成的token>"
   python run.py --transport http --host 127.0.0.1 --port 8765 --report-file "C:/path/to/test-client/mxsj_probe_report.txt"
   ```

5. 在第二个 MCP 编程工具中配置 Streamable HTTP：

   ```json
   {
     "mcpServers": {
       "mxsj-client-http": {
         "url": "http://127.0.0.1:8765/mcp",
         "headers": {
           "Authorization": "Bearer <同一个token>"
         }
       }
     }
   }
   ```

   不同工具的字段名可能不同；选择 HTTP / Streamable HTTP 类型，不要选 SSE。

6. 调用 `client_ping` 和 `client_get_probe_report`。预期 `ok=true`，报告内容与 stdio 客户端一致。
7. 记录第二个工具名称、两个调用结果、错误信息（如有）。不要回传 token。

排错：

- `401 unauthorized`：客户端与服务端 token 不一致，或 Authorization 头未发送。
- `421` / `403`：Host/Origin 不在白名单；使用 `http://127.0.0.1:8765/mcp`，不要用局域网 IP 或自定义域名。
- 连接被拒绝：HTTP Server 未运行、端口不一致或被本机防火墙拦截。
- `client_ping ok=true` 仍只表示报告文件可读，不表示游戏进程实时在线。
