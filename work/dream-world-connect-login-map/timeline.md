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
