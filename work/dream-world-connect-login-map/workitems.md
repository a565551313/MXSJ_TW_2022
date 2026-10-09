# Work Items

| ID | title | role | targets | surface | status | evidence | notes |
|----|-------|------|---------|---------|--------|----------|-------|
| WI-001 | Establish scope and auth | lead | case | process | done | | Scope ready; offline read-only analysis |
| WI-002 | Extract server selection and endpoint candidates | lead | server.ini, mx.ini | static config | done | E-001, E-002 | Six entries; all listed ports are 3134; lastserver maps to 203.70.8.205 |
| WI-003 | Determine login pre/post state from logs | lead | local logs | login state | done | E-003 | Reached login and server-selection dialogs; no success/map-entry evidence |
| WI-004 | Recover protocol state symbols | lead | mxmain.dll, IMProtocol.dll | static strings | done | E-004 | Connect/send/receive/error callback symbols identified |
| WI-005 | Identify map resources and map-loading linkage | lead | map/*.map, data/*.fls | map assets | done | E-004, E-005 | Common 0.1M map header and dimensions observed |
| WI-006 | Recover IMProtocol framing and serialization boundaries | lead | IMProtocol.dll, mx.exe | protocol static | in_progress | E-IDA-001..E-IDA-007, E-REA-002 | Export surface, candidate uint16 network-order length, and DLL TCP connect path identified; main-image callsites and channel role unresolved |
| WI-007 | Maintain handoff state-machine documentation | lead | notes/state-machine-draft.md | documentation | done | E-001..E-008 | Candidate Connect -> Login -> World -> Map state model documented |
| WI-008 | Trace main-image callers of IMProtocol APIs and identify channel role | lead | mx.exe, IMProtocol.dll | native callsites/xrefs | in_progress | E-IDA-007, E-REA-001, E-REA-002 | Ghidra 12.1.4 now available; DLL connection chain recovered, but direct main-image IAT xrefs are absent in current analysis and channel role remains unknown |

## Coverage
- [x] Recon/analysis complete for in_scope assets
- [ ] Critical/High candidates triaged (or N/A for pure RE)
- [x] Validated findings have Evidence (E-*)
- [x] Path documented (attack/call/solve)
- [x] Timeline continuous across major phases
- [ ] Report via docs-generator
- [ ] field-journal anonymized

## Refs
- skills/ops/timeline-workitem.md
- skills/ops/evidence-finding-path.md
