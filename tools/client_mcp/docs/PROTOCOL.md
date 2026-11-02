# IPC 协议草案：MCP 宿主 <-> 客户端探针

> 状态：localhost TCP 只读 IPC 已实现；真实客户端挂载尚未验收。日期：2026-11-02。  
> 本协议不是游戏 TCP 协议，也不是 MCP 协议本身；它是 MCP Server 与客户端内探针之间的本机测试通道。

## 1. 设计目标

- 简单、可审计、可脱敏。
- 第一阶段只读。
- 支持 hello、心跳、报告读取、错误上报。
- 后续扩展受控命令，但必须白名单。
- 不传输真实账号密码、票据、密钥。

## 2. 传输候选

第一阶段候选：

1. Windows 命名管道；
2. 本机回环 TCP；
3. 本地文件报告 + 轮询，作为最保守兜底。

当前实现选用 localhost TCP 作为第一版测试通道；命名管道仍未实现。无论哪种传输，都必须：

- 默认仅本机；
- 有会话 token 或等价握手；
- 有消息大小限制；
- 有超时；
- 有审计日志。

## 3. 消息封装

所有消息为 UTF-8 JSON。草案字段：

```json
{
  "v": 1,
  "id": "req-000001",
  "kind": "request",
  "session": "session-uuid",
  "method": "probe.get_runtime",
  "params": {},
  "ts": "2026-11-02T00:00:00+08:00"
}
```

响应：

```json
{
  "v": 1,
  "id": "req-000001",
  "kind": "response",
  "session": "session-uuid",
  "ok": true,
  "result": {},
  "error": null,
  "ts": "2026-11-02T00:00:00+08:00"
}
```

事件：

```json
{
  "v": 1,
  "id": "evt-000001",
  "kind": "event",
  "session": "session-uuid",
  "event": "probe.log",
  "data": {},
  "ts": "2026-11-02T00:00:00+08:00"
}
```

## 4. 第一阶段方法

| 方法 | 方向 | 用途 | 阶段 |
|---|---|---|---|
| `probe.hello` | 探针 -> 宿主 | 注册探针、协议版本、客户端构建摘要 | M2 |
| `probe.heartbeat` | 探针 -> 宿主 | 存活与主循环状态 | M2 |
| `probe.get_runtime` | 宿主 -> 探针 | VM / 进程 / 线程 / 时间信息 | M2 |
| `probe.get_modules` | 宿主 -> 探针 | 已加载脚本模块状态 | M2 |
| `probe.get_native_api` | 宿主 -> 探针 | 原生模块可用性，不执行危险调用 | M2 |
| `probe.get_report` | 宿主 -> 探针 | 汇总只读报告 | M2 |
| `probe.read_log` | 宿主 -> 探针 | 读取探针自身脱敏日志 | M2 |

后续候选，未授权前不得实现为可调用：

| 方法 | 用途 | 阶段 |
|---|---|---|
| `probe.get_ui_state` | 当前界面 / 控件状态 | M4 |
| `probe.get_game_state` | 角色 / 地图 / 连接状态 | M4 |
| `probe.invoke` | 白名单原生操作 | M4 |
| `probe.run_scenario` | 组合测试场景 | M5 |

## 5. hello 草案

```json
{
  "v": 1,
  "id": "hello-000001",
  "kind": "event",
  "session": "session-uuid",
  "event": "probe.hello",
  "data": {
    "probe_version": "0.1.0",
    "protocol_version": 1,
    "client_build": {
      "script_fls_sha256": "<用户修改版派生测试包 SHA-256>",
      "baseline_sha256": "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72",
      "probe_entry": "<待定>",
      "vm": "py25"
    },
    "capabilities": [
      "runtime",
      "modules",
      "native_api_status",
      "probe_log"
    ]
  }
}
```

## 6. 错误码草案

| 错误码 | 含义 |
|---|---|
| `E_PROTOCOL_VERSION` | 协议版本不兼容 |
| `E_SESSION` | 会话无效或未握手 |
| `E_TIMEOUT` | 客户端主循环未在规定时间内响应 |
| `E_NOT_ALLOWED` | 方法不在白名单 |
| `E_BUSY` | 已有独占测试会话 |
| `E_CLIENT_STATE` | 当前客户端状态不满足前置条件 |
| `E_NATIVE_API` | 原生 API 不可用或调用失败 |
| `E_REDACTED` | 结果包含敏感字段，已拒绝返回 |
| `E_INTERNAL` | 探针内部错误， details 需脱敏 |

## 7. 限制草案

- 单条消息默认不超过 256 KiB。
- 日志读取默认分页，不一次返回全部历史。
- 请求默认超时 5 秒，场景级超时另行配置。
- 第一阶段不接受二进制 payload。
- 所有返回字段必须经过脱敏检查。

## 8. 与 MCP 工具的关系

MCP Server 将本协议封装为标准 MCP 工具，例如：

```text
client_ping                 -> probe.heartbeat / probe.hello 状态
client_get_runtime_info     -> probe.get_runtime
client_get_module_status    -> probe.get_modules
client_get_native_api_status-> probe.get_native_api
client_get_probe_report     -> probe.get_report
client_read_probe_log       -> probe.read_log
```

MCP Client 不直接访问探针 IPC。
