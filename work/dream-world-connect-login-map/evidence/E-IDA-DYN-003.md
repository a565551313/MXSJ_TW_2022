### E-IDA-DYN-003
- title: 正常启动客户端后附加 IDA，点击服务器流程命中 native/Python 调用桥
- severity: info
- status: observed
- observed_at: 2026-10-09T23:24:00+08:00
- source_type: ida_gui_debug_runtime
- repro_command: |
    session: 90170726
    attach:
      import ida_dbg
      ida_dbg.attach_process(13920, -1)
    continue:
      dbg_continue(database="90170726")
    breakpoint:
      0x004576B0
- observations:
  - 普通方式启动的 `mx.exe` PID `13920` 正常进入服务器选择界面。
  - 客户端与本地监听器建立了 `127.0.0.1:3134` TCP 连接。
  - 在服务器选择流程中，IDA 停在 `0x004576B0`。
  - 当前线程 ID 为 `14024`；寄存器现场包含 `EAX=0x8`、`ECX=0x0101BCF0`、`ESI=0x142AB720`、`EIP=0x004576B0`、`ESP=0x0019F95C`。
  - 现场栈 128 字节已通过 `dbg_read` 保存，首 32 字节为：
    `b6ba4a00505d021564b16b0032b16b000000000060b16b00505d021520b72a142`
  - 调用栈从 `0x004576B0` 返回到多个 `mx.exe` 调用点，未出现 `IMProtocol.dll` 或 `WS2_32` 帧。
  - 本命中不是 `connect/send/recv` 或 `OnServerCmd` 命中；它确认的是 native/Python 桥在服务器流程中被调用。
- interpretation:
  - 正常启动并附加 IDA 的动态路径已可用。
  - `0x004576B0` 是服务器选择流程中的早期桥调用点，下一步需要在该点返回后继续到 `IMProtocol.dll` 或 Winsock 调用，才能取得首帧方向和业务缓冲区。
- effects: 本地调试附加与回环连接；未访问外部地址，未修改客户端文件。
- limitations: 重启监听器后客户端没有再次建立连接，`--initial-response-hex 0002` 尚未产生可归因的 UI/协议状态变化。
- linked_workitems: WI-008, WI-009
