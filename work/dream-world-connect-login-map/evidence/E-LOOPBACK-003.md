### E-LOOPBACK-003
- title: 2026-10-10 用户本地回环测试结果：捕获文件均为 0 字节（与 10-09 一致）
- severity: info
- status: observed (user-reported)
- observed_at: 2026-10-10（具体时间未提供）
- source_type: operator_report
- content_hash: n/a
- repro_command: n/a（测试在用户 Windows 测试副本中执行；本仓库未收到该次测试的文件）
- notes: |
    用户口头报告“测试了，都是0”。未随附新的 capture 文件、harness 日志、游戏日志或截图，
    因此本条只记录用户报告的结论，不包含字节级细节。仓库内 `tools/captures/` 与
    `notes/protocol-artifacts/stream-*.bin` 仍是 2026-10-09 的 0 字节文件，未被覆盖。
- observations:
  - 本次测试结果与 E-LOOPBACK-001（10-09 前段，3 次完成 + 1 次未完成的捕获）和 E-LOOPBACK-002（10-09 后段，7 次完成 + 1 次保持连接）一致：客户端能与 127.0.0.1:3134 建立 TCP 连接，但在捕获窗口内未发送任何应用层字节。
  - 已有的 10-09 捕获记录中，每次连接由客户端主动关闭，持续时间约 9 s 至 117 s（如 13:43:59→13:44:17、21:11:49→21:13:46）。时间长短不一，与客户端超时后切换候选的行为相容，但尚无证据证明。
- interpretation: |
    结论仍然是：TCP 连接可以建立，但“客户端何时发包、是否需要服务端先发数据”未知。本次结果不能区分下列假设（见 notes/loopback-test-plan-20261010.md）。
- effects: 无新增证据字节；无协议结论变化。
- limitations: 未提供测试文件与日志，无法确认连接建立时间、关闭原因、是否存在 Winsock 错误。
- linked_workitems: WI-010, WI-009
