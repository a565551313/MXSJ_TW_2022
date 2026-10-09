### E-IDA-DYN-004
- title: 服务端首帧探针触发客户端异常路径，尚未进入登录界面
- severity: info
- status: observed
- observed_at: 2026-10-09T23:41:00+08:00
- source_type: loopback_response_plus_ida_debug
- repro_command: |
    responsive_loopback_harness.py --port 3134 --initial-response-hex 0002
    IDA session 90170726
- observations:
  - 客户端重新连接 `127.0.0.1:3134` 后，harness 立即发送 `00 02`。
  - IDA 随后暂停在 `0x76FFB972`，解析为 `KernelBase.dll!RaiseException+0x62`。
  - 调用栈上层回到 `mx.exe` 的 JSON/错误处理调用链。
  - 客户端没有进入账号登录页；没有观察到 `OnServerCmd`、业务帧或角色/地图数据。
  - 客户端入站捕获文件仍未形成业务数据，连接保持在调试暂停状态。
- interpretation:
  - 连接建立后服务端首帧探针确实影响了客户端执行路径。
  - `00 02` 不是可接受的空响应；客户端在解析/校验阶段进入异常处理。
  - 下一步应从异常调用链恢复期望的首帧结构、解密/校验前置字段和错误码，不应继续把该响应当作登录成功。
- effects: 仅本地回环响应与调试暂停；未访问外部地址，未修改客户端文件。
- linked_workitems: WI-006, WI-008, WI-009
