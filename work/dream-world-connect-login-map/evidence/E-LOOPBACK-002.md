### E-LOOPBACK-002
- title: 客户端已实际连接本地 127.0.0.1:3134，但在无应用层响应时停留于连接服务器界面
- severity: info
- status: observed
- observed_at: 2026-10-09T21:14:47+08:00
- source_type: local_runtime_capture_and_user_screenshot
- content_hash: n/a
- repro_command: |
    Get-NetTCPConnection -LocalPort 3134
    Get-Content notes/protocol-artifacts/responsive-harness.log -Tail 80
- notes: offline local runtime evidence; screenshot was supplied by the user and is retained as conversation evidence.
- artifacts:
  - `notes/protocol-artifacts/responsive-harness.log`
  - `notes/protocol-artifacts/stream-0001.bin` through `stream-0007.bin`
  - user screenshot: `D:/reasetup/temp/codex-clipboard-780c7e68-8711-4226-9aaa-c8d5c0a77c62.png`
- observations:
  - The screenshot shows the client on the server-selection page with the modal text `正在连接服务器...`.
  - The same screenshot shows the local harness in capture-only mode listening on `127.0.0.1:3134`.
  - The harness log records seven completed connections between 21:10:33 and 21:14:27. Each completed stream saved 0 bytes.
  - A further connection was accepted at 21:14:47 and remained open at inspection time.
  - `Get-NetTCPConnection -LocalPort 3134` showed `127.0.0.1:3134 -> 127.0.0.1:62266` in `Established` state, owned by the Python harness process.
- interpretation:
  - The client is definitely reaching the local TCP listener; this closes the earlier uncertainty about whether the configured loopback endpoint was being used.
  - The client has not sent application bytes before the completed retries, and remains waiting on the current connection while the harness sends no protocol response.
  - This is consistent with a server-first handshake or an earlier auxiliary-channel wait, but does not yet identify the required response or prove that 3134 is the main game-login channel.
- effects: Local loopback only; no external server connection and no client binary modification.
- limitations: No application payload or server response has been captured. The screenshot does not by itself identify the expected protocol message.
- linked_workitems: WI-006, WI-009
