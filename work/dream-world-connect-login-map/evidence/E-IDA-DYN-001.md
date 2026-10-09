### E-IDA-DYN-001
- title: IDA 9.4 已建立 GUI 调试会话并挂载关键协议断点；本轮尚未取得命中数据
- severity: info
- status: observed
- observed_at: 2026-10-09T21:58:00+08:00
- source_type: ida_gui_debug_session
- content_hash: n/a
- repro_command: |
    IDA Pro 9.4 GUI session `90170726`
    IDA Python: `ida_dbg.load_debugger("win32", 0)`
    IDA Python: `ida_dbg.attach_process(18840, -1)`
    IDA Python: `ida_dbg.add_bpt(...)`
- notes: offline/local dynamic instrumentation preparation; no binary patch or file modification was performed.
- observations:
  - IDA GUI adopted `D:\Lager\夢想世界\mx.exe.i64` as session `90170726`.
  - The session enumerated the live 32-bit module layout, including `mx.exe` at `0x00400000` and `IMProtocol.dll` at `0x01540000`.
  - Breakpoints were accepted at:
    - `mx.exe+0x0AC590` (`0x004AC590`)
    - `mx.exe+0x0AC030` (`0x004AC030`)
    - `mx.exe+0x0576B0` (`0x004576B0`)
    - `IMProtocol.dll+0x3000` (`0x01543000`)
    - `IMProtocol.dll+0x3240` (`0x01543240`)
    - `IMProtocol.dll+0x3330` (`0x01543330`)
    - `IMProtocol.dll+0x31A0` (`0x015431A0`)
    - `IMProtocol.dll+0x31F0` (`0x015431F0`)
  - An attach attempt was issued against the running client PID `18840`; the debug session entered an attached state, but the target later exited during the connection retry cycle.
  - No breakpoint hit, register snapshot, receive buffer, command value, or Python callback invocation was captured in this run.
- interpretation:
  - IDA-based dynamic instrumentation is available and the important native addresses have been mapped into the live module layout.
  - This evidence demonstrates instrumentation readiness only; it does not establish a runtime protocol event.
- effects: Local debugger attachment only; no external connection and no client file modification.
- limitations: A fresh client launch under IDA is required to catch initialization and connection events before timeout.
- linked_workitems: WI-008, WI-009
