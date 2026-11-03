# MCP 编程工具接入

> **用户接入请走一键启动**：双击 `tools/client_mcp/启动客户端MCP.bat`，再导入
> `tools/client_mcp/runtime/mcp_client_config.json`。本文下面的命令行只作开发者参考，
> 不要求用户执行（2026-11-03 用户要求）。


> 状态：stdio 与本机 Streamable HTTP 已实现；Windows 真实探针报告已通过 stdio 报告文件桥被 MCP 客户端读取。日期：2026-11-02。
> 目标：让各种支持 MCP 的编程工具接入同一套客户端原生测试能力，而不是绑定某一个 IDE。

## 1. 接入方式

### 1.1 stdio

适合 MCP Server 与编程工具在同一台 Windows 机器上。

当前命令形态：

```bash
python tools/client_mcp/run.py --transport stdio
```

通用配置示例，具体字段以各工具文档为准：

```json
{
  "mcpServers": {
    "mxsj-client": {
      "command": "python",
      "args": [
        "C:/path/to/MXSJ_TW_2022/tools/client_mcp/run.py",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

### 1.2 Streamable HTTP

适合多工具接入、本机多客户端、未来 CI 或受控远程验收。

当前版本已实现本机 HTTP，命令形态：

```bash
python tools/client_mcp/run.py --transport http --host 127.0.0.1 --port 8765 --http-token <token>
```

通用配置示例：

```json
{
  "mcpServers": {
    "mxsj-client": {
      "url": "http://127.0.0.1:8765/mcp",
      "headers": {
        "Authorization": "Bearer <local-test-token>"
      }
    }
  }
}
```

当前版本只允许监听 `127.0.0.1` / `localhost` / `::1`，并强制 Bearer token；非本机监听会被拒绝。token 可用 `--http-token` 或环境变量 `MXSJ_MCP_HTTP_TOKEN` 提供，不得提交 Git。局域网/远程访问不在当前版本范围内。

## 2. 第一阶段 MCP 工具面

只读工具：

| 工具 | 用途 |
|---|---|
| `client_ping` | 检查 MCP Server 与探针会话是否存活 |
| `client_get_runtime_info` | 读取客户端 VM / 进程 / 线程基础信息 |
| `client_get_probe_report` | 读取探针汇总报告 |
| `client_get_module_status` | 读取脚本模块加载状态 |
| `client_get_native_api_status` | 读取原生模块可用性 |
| `client_read_probe_log` | 读取探针脱敏日志 |

后续受控工具，第一阶段不开放：

| 工具 | 用途 |
|---|---|
| `client_get_ui_state` | 当前界面 / 控件状态 |
| `client_get_game_state` | 角色 / 地图 / 连接状态 |
| `client_invoke_allowed_action` | 白名单原生操作 |
| `client_run_scenario` | 登录 / 进图 / NPC / 传送等场景 |
| `client_stop_scenario` | 停止当前场景 |

## 3. 多客户端并发

多个编程工具可以同时连接 MCP Server，但必须区分：

### 3.1 只读操作

可并发：

```text
client_ping
client_get_probe_report
client_read_probe_log
```

### 3.2 控制操作

必须独占：

```text
client_invoke_allowed_action
client_run_scenario
```

MCP Server 需要维护：

- MCP 客户端会话 ID；
- 探针会话 ID；
- 控制锁持有者；
- 锁超时；
- 操作审计。

## 4. 配置示例目录

当前在 `configs/` 提供：

```text
configs/generic_stdio.example.json
configs/generic_http.example.json
configs/generic_stdio_report_file.example.json
# 后续候选：
configs/cursor.example.json
configs/claude_code.example.json
configs/cline.example.json
configs/continue.example.json
```

这些示例必须标注：

- 路径需要替换；
- token 不得提交到 Git；
- 不同工具字段可能不同；
- 示例不代表所有工具字段完全一致。

## 5. Arena / 远程 Agent 连接边界

当前 Arena 沙箱不能默认访问用户 Windows 本机的 `127.0.0.1`。可选模式：

1. Linux 沙箱连接 fake probe，验证 MCP 协议；
2. Windows 本机编程工具连接真实探针；
3. 用户回传 Windows 报告；
4. 未来如需要远程直连，另行实现安全网关。

不得把“沙箱 fake probe 通过”写成“真实 Windows 客户端接入完成”。
