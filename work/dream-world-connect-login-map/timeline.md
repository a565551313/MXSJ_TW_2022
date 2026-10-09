# Timeline (append-only)

## 2026-10-09T09:41:23.3102474+08:00 | lead | init
- action: case-init
- command_or_ref: skills/scripts/case-init.ps1
- result_summary: case directory created; scope ready_for_act=true
- artifacts: [scope.md, workitems.md]
- evidence_ids: []
- decision_delta: [case_initialized]
- carry_forward_refs: [scope.md]
- next: open PRIMARY SKILL.md and ACT within scope

## 2026-10-09T10:37:18+08:00 | lead | static-analysis-complete
- action: offline static protocol/config/map analysis
- command_or_ref: notes/agent-config-protocol.md
- result_summary: server.ini and mx.ini establish six endpoint candidates on port 3134 and current lastserver mapping to 203.70.8.205; logs stop at login/server-selection dialogs; static strings expose connection callbacks, packet builders, server command processing, and %04d.map loading; local map headers and dimensions catalogued
- artifacts: [notes/agent-config-protocol.md, evidence/E-001-server-list.md, evidence/E-002-last-server.md, evidence/E-003-login-state.md, evidence/E-004-protocol-map-strings.md, evidence/E-005-map-format.md]
- evidence_ids: [E-001, E-002, E-003, E-004, E-005]
- decision_delta: [phase=static->complete, network_activity=none, login_success=unproven, map_entry=unproven]
- carry_forward_refs: [scope.md, workitems.md]
- next: case handoff with residual uncertainty recorded

## 2026-10-09T10:49:00+08:00 | lead | delegated-static-and-ida
- action: parallel agent analysis plus IDA protocol interface extraction
- command_or_ref: notes/agent-config-protocol.md; notes/state-machine-draft.md; notes/ida-protocol-interface.md
- result_summary: parallel notes added; IDA survey completed for IMProtocol.dll and mxmain.dll; IMProtocol exports expose Winsock connection, crypto wrappers, explicit integer/string serialization, and a two-byte network-order length write before send
- artifacts: [notes/agent-config-protocol.md, notes/state-machine-draft.md, notes/ida-protocol-interface.md]
- evidence_ids: [E-IDA-001, E-IDA-002, E-IDA-003, E-IDA-004, E-IDA-005, E-IDA-006]
- decision_delta: [protocol_layer_confirmed, frame_length_candidate=uint16_network_order, login_opcode=unknown, map_entry=unproven]
- carry_forward_refs: [scope.md, workitems.md, evidence/E-001-server-list.md, evidence/E-002-last-server.md, evidence/E-003-login-state.md, evidence/E-004-protocol-map-strings.md, evidence/E-005-map-format.md]
- next: trace IMProtocol callers and main-module command/map xrefs


## 2026-10-09T12:13:00+08:00 | lead | native-provider-blocked-import-check
- action: resumed offline protocol-interface analysis using REA discovery plus local import-table corroboration
- command_or_ref: `rea.open_binary(mx.exe, provider_id=ida)`; `sha256sum mx.exe mxmain.dll IMProtocol.dll`; `objdump -p mx.exe`
- result_summary: REA MCP tools are registered, but Ghidra/Hopper/IDA native providers are unavailable in this session. Local PE import metadata confirms `mx.exe` imports `IMProtocol.dll` connection, serialization, crypto, and send APIs; no verified function-level caller or channel assignment was obtained.
- artifacts: [notes/ida-protocol-interface.md, evidence/E-IDA-007.md, evidence/E-REA-001.md]
- evidence_ids: [E-IDA-007, E-REA-001]
- decision_delta: [main_image_import_dependency=confirmed, callsite=unknown, NsServer_role=unknown, external_network=none, target_files_unchanged]
- carry_forward_refs: [WI-006, WI-008, evidence/E-IDA-001..E-IDA-007]
- next: when an REA native provider is available, trace callers/xrefs for `IMP_ConnectNsServer`, `IMP_SendBuffer2NS`, and the main-image `Connect`/`PacketSend` path; keep game-login versus auxiliary-channel attribution unresolved until direct evidence exists.


## 2026-10-09T12:44:00+08:00 | lead | ghidra-nsserver-connect-chain
- action: resumed read-only native analysis using REA-Ghidra / Ghidra 12.1.4
- command_or_ref: `rea-ghidra.open_binary(IMProtocol.dll)`; `analyze_function(0x10003000, 0x10001660, 0x10005cb0, 0x10004920, 0x10004a30, 0x10004a60)`
- result_summary: traced `IMP_ConnectNsServer` through the session/socket setup to a Winsock `connect` path. The numeric-address branch converts the port through the existing `htons` import mapping and calls `connect`; the hostname branch passes message `0x502` to a WS2_32 ordinal, while async socket notifications use `context+0x503` and mask `0x3f`. Main-image direct IAT xref queries still returned no code refs, so caller and channel role remain unresolved.
- artifacts: [evidence/E-REA-002.md, evidence/rea-ghidra-improtocol-20261009-1244.json, notes/ida-protocol-interface.md, notes/state-machine-draft.md, report/analysis.md]
- evidence_ids: [E-REA-002, ev_22d0ec4c2c38a4d1a04899546e9398dc534c72fdc5a73a38508899dd3254d8b3, ev_5f12a32d2aae3e653c52a090b8b677af0d00b45b31076acbc1d6ee30ef4667bc, ev_656a2d2aa23811aca5bda8c68effced9d0522c33114c7847a6bb74bc860a2f12, ev_c9e6508cdf6efcde6a47343ee0416c77e2b0349e78e698298071674d40e1a6ec]
- decision_delta: [ghidra_provider=available, dll_tcp_connect_path=confirmed_static, numeric_branch_port_htons=confirmed_static, hostname_async_completion=unresolved, main_image_callsite=unresolved, NsServer_login_role=unknown, external_network=none]
- carry_forward_refs: [WI-006, WI-008, evidence/E-REA-002.md]
- next: resolve `0x502`/`0x503` message dispatcher and inspect indirect main-image calls into IMProtocol; keep login and map-entry states unconfirmed.
