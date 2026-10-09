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


## 2026-10-09T15:31:00+08:00 | lead | dispatch-and-resource-reference-recheck
- action: independently recheck the native command bridge and narrow the `PY_CODERESOURCE` claim
- command_or_ref: Ghidra 12.1.4 on hash-matched `mx.exe`; `FUN_004ac590`, `FUN_004ac030`, `FUN_004576b0`; string VA `0x6c33f4`, reference address `0x4f0444`
- result_summary: confirmed statically that event `0x2714` reaches `FUN_004ac030`, which reads a 16-bit value and invokes the generic Python method bridge as `OnServerCmd(int)`. This does not bind script entry 516's `ProcessServerCmd` constant to the method. `PY_CODERESOURCE` has a string reference at `0x4f0444`, but the site is not inside an identified procedure; no registration, loader, or decoder was established. Script payload decoding still fails for tested records at this historical point.
- artifacts: [evidence/E-REA-006.md, notes/state-machine-draft.md]
- evidence_ids: [E-REA-006, ev_b0fc5f803020a60da58e6ccccc96758b21358c6ca04d03a6611cfde382974b51, ev_30fb71fdb6a011e18bda8ec98fc84d162931071afe60f7b35e52886d613a42ad, ev_4c27741eca6162848ce8934e21c095396e3ee7365c7830be6ed9e3f1649021ce]
- decision_delta: [native_0x2714_OnServerCmd_int_confirmed, script_ProcessServerCmd_binding_unproven, PY_CODERESOURCE_loader_not_located, S2_to_S3_unresolved, no_reply_guessed]
- carry_forward_refs: [WI-008, WI-009, E-REA-004, E-REA-006]
- next: validate the script code-object format or obtain the actual loader path; do not infer the page transition or send a guessed response.


## 2026-10-09T16:12:42+08:00 | lead | server-selection-dialog-trigger-clarification
- action: revise the UI/protocol state transition based on the user's direct observation
- command_or_ref: user's message: “直接选服或者点了下一步都会弹出连接服务器的对话框的”
- result_summary: The trigger is now known: either direct server selection or “Next” opens the “Connecting to server” dialog. This is a UI transition only; it does not prove account-login UI, application-layer exchange, or a causal match to the earlier four loopback accepts. The historical listener accepted TCP and sent no protocol response.
- artifacts: [evidence/E-USER-001.md, notes/state-machine-draft.md, report/analysis.md, workitems.md]
- evidence_ids: [E-USER-001, E-LOOPBACK-001, E-REA-004, E-REA-006]
- decision_delta: [selection_action_known, S2_to_connecting_dialog_observed, dialog_to_account_login_unresolved, capture_correlation_unproven, no_reply_guessed]
- carry_forward_refs: [WI-008, WI-009, E-USER-001]
- next: continue from the connection-dialog state; establish the client-side progress/error condition and required server-command response before implementing any local responder.


## 2026-10-09T16:33:30+08:00 | lead | imp-filetype-and-fls-record-validation
- action: trace the `PY_CODERESOURCE` registration site and independently validate FLS index/decompression
- command_or_ref: Ghidra 12.1.4 on hash-matched `mx.exe`; `0x4f0442-0x4f044a`, `FUN_004f0e50`, `FUN_004f5320`, `FUN_004dfeb0`, `FUN_004e4750`, `FUN_0048f170`, `FUN_0048ecf0`; local `data/script.fls`
- result_summary: confirmed that the embedded `imp` module exports `PY_CODERESOURCE` with numeric value 8; this is an import/file-type constant, not a server opcode. Reproduced the FLS record transforms and independently zlib-decoded all 5,002 records (61,940,973 expanded bytes). Entry 516 was 17,234 bytes after zlib; the then-tested XOR produced only a plausible Python 2.7 code-object header and failed in nested constants. This was the state recorded at that time; the later correction is in E-REA-008.
- artifacts: [evidence/E-REA-007.md, report/analysis.md, workitems.md]
- evidence_ids: [E-REA-007, ev_762e6b954556a435ee0ad035ce1c4c8b3f72595d5ed2cee13d0670cadd4d3099, ev_5fe48796a23cabf8015ec9d0530d000115ad133c2f8645b2014f3c209d3156eb, ev_12564b18ae2dee44a85cf03a804c5c886880047f6bd9f100fdda2e7ca24e6422, ev_339eb05b7a6edd74870699bbcfda2ce1d6802b3620efa2b58593068f0f08b967]
- decision_delta: [imp_PY_CODERESOURCE_8_is_filetype_not_wire_command, all_FLS_zlib_records_validated, entry516_codeobject_transform_unresolved_at_this_time, script_binding_and_S2_to_S3_unresolved, no_reply_guessed]
- carry_forward_refs: [WI-006, WI-008, WI-009, E-REA-006]
- next: identify the actual code-resource loader/transform and verify whether entry 516 binds `ProcessServerCmd` to `OnServerCmd(int)`; do not infer a TCP response from value 8.


## 2026-10-09T16:34:00+08:00 | lead | coderesource-id-map-validation
- action: 核验 `PY_CODERESOURCE` 与数值 8 同组传参线索，并评估其能否支持强制进入补丁。
- command_or_ref: hash-matched `mx.exe`; x86 disassembly `0x4f0442..0x4f044a`; `FUN_004f0e50`, `FUN_004dfeb0`, `FUN_004dfdd0`, `FUN_004f5320`; string VA `0x6c33f4`。
- result_summary: 原始指令按顺序压入数值 8、`PY_CODERESOURCE` 字符串地址和模块字典对象；结合 `PyModule_AddObject()` 路径及 `imp` 模块字符串表，证据将其限定为嵌入式 Python `imp.PY_CODERESOURCE == 8` 文件/导入类型常量导出，不是游戏资源处理器注册或网络命令。entry 516 的候选 marshal 载荷当时仍未完整解析，也未恢复其与 `OnServerCmd(int)` 的绑定或 S2 -> S3 跳转条件。
- artifacts: [evidence/E-REA-007.md, evidence/E-REA-006.md, notes/state-machine-draft.md, report/analysis.md, workitems.md]
- evidence_ids: [E-REA-007, ev_5774e116b19d03416f7446c58cc04d232433eabacd9ab5112a4f73f6dceec749, ev_30fb71fdb6a011e18bda8ec98fc84d162931071afe60f7b35e52886d613a42ad, ev_f5308d46fb7bbc62292af327934f4931102b1acf628b4f5408adb8f94e25d357, ev_5fe48796a23cabf8015ec9d0530d000115ad133c2f8645b2014f3c209d3156eb, ev_9c8a07719227d5833b5fdc2815ae10d110a7d3bd4f8896ab8e20ad348d7ba20c, ev_828f0c401010fc24d993acc0581ce8c2f727ded3577eca3b06ae7501a8984a18, ev_23fffaf756a6fa36343f88c39675a893ad52adee0ef096ceb9405a51586cbd57, ev_bf1c1a9d3d93def39d16dca75f5377638d86e6d7eb89a44019080dc4366e3b4f]
- decision_delta: [imp_PY_CODERESOURCE_file_type_constant_confirmed, not_a_network_opcode, code_resource_decoder_unknown_at_this_time, account_page_transition_unresolved, no_binary_copy_patch_created]
- carry_forward_refs: [WI-008, WI-009, E-REA-004, E-REA-006, E-REA-007]
- next: trace the name-to-ID dictionary consumers and recover the custom code-resource payload; select a patch point only after the account-page transition condition is established.


## 2026-10-09T18:52:30+08:00 | lead | entry516-code-object-decode-and-user-stop
- action: record the user's correction to the prior decode status and pause further analysis
- command_or_ref: user-provided investigation handoff; no binary analysis or runtime action was run in this documentation-only task
- result_summary: the handoff reports that five XOR layers yield a complete Python 2.7 marshal tree with 59 code objects, including `CMXNet.OnServerCmd`, `ProcessServerCmd`, and `C2STransferServer`; the earlier parse failure was caused by incorrect decompiler argument ordering. The second-layer non-standard `co_code` opcode encoding and pre-execution conversion remain unresolved. The candidate `render.dll` `Py_Uncompress` route through `ResLib.dll` ordinals 13/12 does not match entry 516's data header and is unconfirmed as its loader. The handoff also reports local PE byte-scan entry names `ReadFls`, `Uncompress`, and `LoadFileExtend`, timeouts for wide and single-function `render.dll` Ghidra decompilation, and that the original `mx.exe` was not modified and no force-entry copy was made.
- artifacts: [evidence/E-REA-008.md, report/analysis.md, notes/state-machine-draft.md, workitems.md]
- evidence_ids: [E-REA-008]
- decision_delta: [marshal_tree_reported_recovered, custom_co_code_opcode_layer_unresolved, candidate_render_loader_unconfirmed, original_mx_exe_unchanged, no_force_entry_copy, further_analysis_paused]
- carry_forward_refs: [WI-006, WI-008, WI-009, E-REA-008]
- next: paused at the user's explicit instruction; do not continue binary/game analysis, patching, or runtime tests without a new user request.
