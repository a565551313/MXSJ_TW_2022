# Work Items

| ID | title | role | targets | surface | status | evidence | notes |
|----|-------|------|---------|---------|--------|----------|-------|
| WI-001 | Establish scope and auth | lead | case | process | done | | Scope ready; offline read-only analysis |
| WI-002 | Extract server selection and endpoint candidates | lead | server.ini, mx.ini | static config | done | E-001, E-002 | Six entries; all listed ports are 3134; lastserver maps to 203.70.8.205 |
| WI-003 | Determine login pre/post state from logs | lead | local logs, local capture | login state | done | E-003, E-LOOPBACK-001 | Latest run reached server selection only; user confirms account-login UI is not reached; no success/map-entry evidence |
| WI-004 | Recover protocol state symbols | lead | mxmain.dll, IMProtocol.dll | static strings | done | E-004 | Connect/send/receive/error callback symbols identified |
| WI-005 | Identify map resources and map-loading linkage | lead | map/*.map, data/*.fls | map assets | done | E-004, E-005 | Common 0.1M map header and dimensions observed |
| WI-006 | Recover IMProtocol framing and serialization boundaries | lead | IMProtocol.dll, mx.exe | protocol static | in_progress | E-IDA-007, E-REA-002, E-LOOPBACK-002 | Export surface and candidate uint16 network-order length are documented; live loopback use is confirmed, but the client has not emitted a frame and the required server-first response remains unresolved. |
| WI-007 | Maintain handoff state-machine documentation | lead | notes/state-machine-draft.md | documentation | done | E-001..E-005, E-REA-002..E-REA-008, E-USER-001 | Candidate Connect -> Login -> World -> Map state model documented; latest UI and agent findings appended |
| WI-008 | Trace main-image callers of IMProtocol APIs and identify channel role | lead | mx.exe, IMProtocol.dll | native callsites/xrefs | in_progress | E-IDA-007, E-REA-002..E-REA-004, E-REA-008, E-IDA-DYN-001, E-IDA-DYN-002, E-IDA-DYN-003 | Normal launch plus IDA attach is working; first runtime hit is the native/Python bridge at 0x004576B0. Protocol-library/Winsock hit remains open. |
| WI-009 | Trace server-selection to account-login UI transition | lead | mx.exe, mxmain.dll, data/script.fls, local captures | UI/protocol state | in_progress | E-LOOPBACK-001, E-LOOPBACK-002, E-REA-003..E-REA-008, E-USER-001, E-IDA-DYN-001, E-IDA-DYN-002, E-IDA-DYN-003 | Normal client reaches server selection and opens the local TCP connection; no login UI or application frame has been confirmed. |

## Coverage
- [ ] Recon/analysis complete for in-scope assets; native bridge is advanced, login/map state remains unresolved
- [ ] Critical/High candidates triaged (or N/A for pure RE)
- [x] Validated findings have Evidence (E-*)
- [x] Candidate path documented; protocol/UI verification path remains open
- [x] Timeline continuous across major phases
- [x] Report and handoff maintained; evidence graph cleanup remains
- [ ] field-journal anonymized

## Refs
- skills/ops/timeline-workitem.md
- skills/ops/evidence-finding-path.md
