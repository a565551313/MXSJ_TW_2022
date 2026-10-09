# Case Scope

## meta
- case_id: dream-world-connect-login-map
- created: 2026-10-09T09:41:23.3102474+08:00
- operator: local
- project_root: D:\Lager\夢想世界
- primary_skill: protocol-reverse/SKILL.md
- primary_id: R21
- lead_role: lead
- specialist_roles: []
- hint: Windows game client protocol reverse engineering for connection login and empty map entry
- preset: offline-sample

## auth
- status: granted
- basis: own_system
- evidence_of_auth: preset:offline-sample (owner-operated local file)
- MUST NOT proceed if status != granted

## in_scope
- assets:
  - D:\Lager\夢想世界\mx.exe
  - 'D:\Lager\夢想世界\mxmain.dll','D:\Lager\夢想世界\IMProtocol.dll','D:\Lager\夢想世界\gameplayer.exe','D:\Lager\夢想世界\server.ini','D:\Lager\夢想世界\service.txt'
- surfaces: []
- activities: []

## out_of_scope
- assets: []
- activities: [dos, phishing_real_users, unrestricted_exfil]

## network_profile
- mode: offline
- notes: |
    offline | lab_only | authorized_target_only | unrestricted_lab
    Change mode only after auth.status = granted.

## deliverables
- report: true
- field_journal: true
- diagrams: true
- timeline: true

## constraints
- timebox: {}
- stealth: low
- data_handling: anonymize

## signoff
- ready_for_act: true
- checklist:
  - [x] auth.status = granted
  - [x] in_scope.assets non-empty OR offline sample path set
  - [x] network_profile.mode chosen
  - [ ] out_of_scope reviewed
  - [ ] roles assigned (see skills/ops/role-map.md)

## ops_refs
- skills/ops/scope-contract.md
- skills/ops/evidence-finding-path.md
- skills/ops/role-map.md
- skills/ops/timeline-workitem.md
- skills/ops/IDENTITY.md