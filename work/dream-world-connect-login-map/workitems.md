# Work Items

| ID | title | role | targets | surface | status | evidence | notes |
|----|-------|------|---------|---------|--------|----------|-------|
| WI-001 | Establish scope and auth | lead | case | process | done | | Scope ready; offline read-only analysis |
| WI-002 | Extract server selection and endpoint candidates | lead | server.ini, mx.ini | static config | done | E-001, E-002 | Six entries; all listed ports are 3134; lastserver maps to 203.70.8.205 |
| WI-003 | Determine login pre/post state from logs | lead | local logs, local capture | login state | done | E-003, E-LOOPBACK-001 | Latest run reached server selection only; user confirms account-login UI is not reached; no success/map-entry evidence |
| WI-004 | Recover protocol state symbols | lead | mxmain.dll, IMProtocol.dll | static strings | done | E-004 | Connect/send/receive/error callback symbols identified |
| WI-005 | Identify map resources and map-loading linkage | lead | map/*.map, data/*.fls | map assets | done | E-004, E-005 | Common 0.1M map header and dimensions observed |
| WI-006 | Recover IMProtocol framing and serialization boundaries | lead | IMProtocol.dll, mx.exe | protocol static | paused | E-IDA-001..E-IDA-007, E-REA-002 | Export surface, candidate uint16 network-order length, and DLL TCP connect path identified; main-image callsites and channel role unresolved. Further analysis paused at user's explicit request. |
| WI-007 | Maintain handoff state-machine documentation | lead | notes/state-machine-draft.md | documentation | done | E-001..E-008 | Candidate Connect -> Login -> World -> Map state model documented; latest UI and pause status appended |
| WI-008 | Trace main-image callers of IMProtocol APIs and identify channel role | lead | mx.exe, IMProtocol.dll | native callsites/xrefs | paused | E-IDA-007, E-REA-001..E-REA-004, E-REA-008 | Native `0x2714` dispatches a 16-bit value to `OnServerCmd`; the decoded entry includes script methods `CMXNet.OnServerCmd` and `ProcessServerCmd`, but their binding, runtime callers, command semantics, and channel role remain unresolved. Paused per user instruction. |
| WI-009 | Trace server-selection to account-login UI transition | lead | mx.exe, mxmain.dll, data/script.fls, local captures | UI/protocol state | paused | E-LOOPBACK-001, E-REA-003..E-REA-008, E-USER-001 | User reports direct server selection or “Next” opens the connecting dialog. Entry 516 is reported as a complete 59-code-object Python 2.7 marshal tree, but its second-layer non-standard `co_code` opcode encoding and S2 -> S3 condition remain unresolved; candidate loader path is unconfirmed. No response or patch is guessed; original `mx.exe` is unchanged and no force-entry copy exists. Further binary/game analysis paused at user's explicit request. |

## Coverage
- [ ] Recon/analysis complete for in-scope assets; analysis is paused with unresolved items per user's explicit instruction
- [ ] Critical/High candidates triaged (or N/A for pure RE)
- [x] Validated findings have Evidence (E-*)
- [x] Path documented (attack/call/solve)
- [x] Timeline continuous across major phases
- [ ] Report via docs-generator
- [ ] field-journal anonymized

## Refs
- skills/ops/timeline-workitem.md
- skills/ops/evidence-finding-path.md
