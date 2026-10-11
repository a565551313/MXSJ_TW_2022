# AGENT E — client static configs: map / scene / NPC-name / NPC-position extraction

**Scope.** The five items assigned in `server/docs/CSV_ANOMALY_ASSIGNMENTS.md`
(entries **400**, **1301**, **1799**, **2601**, **2804**), plus two entries the evidence forced into the
picture: **4897** (`script\data\minimapnpcpos_test.py`, witness) and **1870** (`script\taiwan\npcpos_fix.py`,
specimen). Entry numbers are zero-based indices into `data/script.fls`.

**Inputs / provenance.** `data/script.fls` SHA-256
`8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`; key database
`tools/decompiler/script_fls_keys.json` SHA-256
`43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb` (the hashes recorded in
`server/docs/catalog/csv_readiness_survey.json`, re-checked here). The "anomaly as delivered" strings are
quoted verbatim from that JSON.

**Constraints honoured.** Read-only on the client and on `data/script.fls`. No recovery script executed, no
`exec`/`eval`, no game code imported, `mock_server.py` not started, nothing written to
`tools/decompiler/*` or `server/game_data/`. The only repository file created by this round is this report.
No ID or name was guessed; no byte was trimmed; no record dropped; no table merged with another; no
Simplified/Traditional conversion.

**Method (independent of Agent A's tools).** Each entry's payload is XOR-decrypted with the saved key/bound
sets and then parsed with an independently written marshal walker (it resolves `TYPE_STRINGREF` references
through the interned-string table and keeps absolute payload offsets). Because the saved boundary placement
is a *heuristic* result, every slot of the 4-boundary set was re-scanned and judged by four independent
criteria, in this order:

1. **bytecode validity** – every instruction decodes to a mapped opcode and every argument is inside the
   limits taken from the code object itself (`n_consts`, `n_names`, code length);
2. **structural consistency** – the marshal walker must consume the whole payload and the code object's tail
   fields (`co_filename`, `co_name`, `co_lnotab`) must come out sensible;
3. **literal evaluation** – the table assignment (a pure literal segment) is evaluated with duplicate-key
   detection; every text constant must be valid cp950; no constant may be left stranded;
4. **cross-table discrimination** – where two tables describe the same `(scene, npcid)` pair, the framing
   that makes the two tables agree wins (this decides what 1–3 cannot).

Criterion 1 alone is **not** a validity test: with the correct limits, slots that are off by a few bytes can
still produce thousands of plausible instructions, and criterion 3 passes several *wrong* placements when
the shifted characters happen to remain valid cp950 (§5.3 shows eight such placements). All probes ran
outside the repository in `/tmp/mx` (scratch, may not persist; the numbers below are self-contained).

**Framing summary (all entries of this round).**

| entry | file (`co_filename`) | keys | saved bounds | repaired bounds | delivered symptom |
|-------|----------------------|------|--------------|-----------------|-------------------|
| 400 | `script\data\sceneid2name.py` | `[116,171,175,82,162]` | `[961,2001,3063,4125]` | unchanged (already correct) | `DATA[1071]` "not in map catalog" |
| 1301 | `script\data\mapdata.py` | `[103,65,178,5,215]` | `[1612,3237,4884,6553]` (solver: `(1615,3239)`) | **`[1616,3239,4884,6553]`** | `DATA` key is the text `兔坦卡門陵墓` |
| 1799 | `script\data\npcname2realnamedata.py` | `[92,155,4,210,100]` | `[528,1096,1655,2207]` | **`[528,1093,1652,2202]`** | two constants fail cp950 |
| 2601 | `script\data\npcposdata.py` | `[81,41,105,238,184]` | `[18821,37733,56546,75375]` | **`[18827,37735,56546,75376]`** | `unsupported opcode 101 at 124` |
| 2804 | `script\data\minimapnpcpos.py` | `[65,33,179,28,4]` | `[26695,53365,79988,106627]` | **`[26695,53365,79989,106619]`** | `no supported literal assignment for DATA` |
| 4897 (witness) | `script\data\minimapnpcpos_test.py` | `[18,234,200,190,246]` | `[26677,53319,79959,106579]` | slot 2 only: **`79961`** (slot 0 `26677/26678` unresolved) | — |
| 1870 (specimen) | `script\taiwan\npcpos_fix.py` | `[73,68,68,136,96]` | `[276,336,553,766]` | not attempted | `co_names` entry not an identifier |

---

## 1. Entry 1301 / `script\data\mapdata.py` — "one key is the text `兔坦卡門陵墓`"

**Anomaly as delivered**: `entry_index: 1301, table: DATA,
issues: [{key: "兔坦卡門陵墓", kind: "schema", path: "row"}], status: literal_assignment_recovered,
count: 104`.

**Anomaly source (verified).** The recovery pipeline (`review_client_data_boundaries.Review.load`) decodes
this entry with the saved key database but lets the span heuristic transpiler re-place the code span
(`use_solver=True`). For 1301 that heuristic returns **`(1615, 3239)`**, i.e. boundary 1 sits **one byte too
early**. The key database separately stores `[1612, 3237, 4884, 6553]` (what `use_solver=False` would use):
that placement is **four** bytes early and my independent parse of it dies at code offset 1591
(`unmapped custom opcode 0x7c`) — which is also why the pipeline prefers the solver result for this entry.
With the solver's `(1615, 3239)` the literal evaluates, but:

* the text constant `兔坦卡門陵墓` is pushed where the record's key belongs, so `DATA` ends up with
  104 keys of **mixed type** (103 ints + 1 `bytes`),
* the integer constant `1071` is left **stranded** (unused) — that is precisely the record that lost its key,
* the record under the stray text key is `{name: 加洛法師師道殿, w: 1588, h: 1220}`.

So the delivered row count (104) is right while one key is not: the key that belongs to that record is the
integer that the *repaired* placement loads one instruction later.

**Original bytes.**

```
entry 1301  keys = [103, 65, 178, 5, 215]     saved bounds = [1612, 3237, 4884, 6553]
code payload = payload[22 : 3881), code_len = 3859
  (payload layout: 'c', argcount u32, nlocals u32, stacksize u32, flags u32, then 's' + u32 code_len
   at payload[18:22]; verified by the walker for all entries of this round: code_pos = 22)
literal store offsets: DATA @ code offset 3792 (STORE_GLOBAL), MAP_ASCRIPTION @ 3852 (STORE_NAME)

raw payload 1600..1636:
  e8 6f 67 62 57 e8 39 67 3d e8 6d 67 62 3d e8 14 41 44 71 fa 41 41 71 ce 35 41 1b ce 47 41 44 71 ce 1c 41 1b

decoded instruction stream (repaired placement [1616,3239,...]): key0 = 0x67 up to 1616, key1 = 0x41 after
  1583 LOAD_CONST const[94]=1220      1586 ROT_TWO        1587 LOAD_CONST const[10]='h'
  1590 STORE_SUBSCR                   1591 ROT_TWO        1592 LOAD_CONST const[115]=1071
  1595 STORE_SUBSCR                   1596 DUP_TOP        1597 BUILD_MAP 0
with the solver placement (1615,3239) the same window reads: 1586 LOAD_CONST 'h'; 1590 BINARY_SUBTRACT;
1591 UNMAPPED 0x7c      with the DB placement (1612,3237) the parse already dies at 1591.
const[115] = 1071 (int)   const[253] = None   const[0..4] = the five nested code objects
```

**Reproduction.** Boundary sweep, criteria 1–3 (the entry is small; whole grid re-run):

| b1 | b2 | code valid | `DATA` evaluates | keys | stranded consts |
|----|----|-----------|------------------|------|-----------------|
| 1615 | 3239 | yes | yes, 104 rows | **103 int + 1 `bytes` (`兔坦卡門陵墓`)** | `[0,1,2,3,4,115,253]` — `const[115]=1071` stranded |
| **1616** | **3239** | **yes** | **yes, 104 rows** | **104 ints** | `[0,1,2,3,4,253]` |
| 1613…1614, 1617…1619 × 3238, 3240 | | no (opcode/arg) | | | |
| 1612/3237 (= saved DB) | | no: dies at 1591 | | | |

**Conclusion — status `candidate` (boundary repair).** The text key is **not** a legitimate special key and
**not** a source-data error: it is the artifact of a boundary sitting one byte early, with the *string*
constant taking the place of the integer key. The correct placement is **`[1616, 3239, 4884, 6553]`**, under
which `DATA` is a plain `{int -> {name, w, h}}` dictionary with **104 integer keys** (all three fields present
in every row, no duplicate keys), `DATA[1071] = {name: 加洛法師師道殿, w: 1588, h: 1220}`, and
`MAP_ASCRIPTION = {1039:1039, 1040:1039, 1041:1039, 1073:1073, 1074:1073, 1075:1073}` (6 rows; the second
and third floors of the two towers point at their first floor, which points at itself; consumed by
`GetParentMap(iMapID) = MAP_ASCRIPTION.get(iMapID, 0)`). No map ID was substituted or guessed: the key is the
constant the script itself loads.

**Cross-table corroboration (three independent tables).**

* 400 (`sceneid2name.py`, framing unchanged and independently valid) carries the row
  `1071 -> ('加洛法師師道殿', 2302, 1500, 2000)`; its key 1071 is now found in the repaired catalog, and for
  all **57/57** of 400's keys the 1301 name equals the 400 name (`0` mismatches).
* 400's `GetShidaodianClass` and 2804/4897's `GetShidaodianClass` both switch on exactly the twelve scene
  ids `[1061,1064,1067,1070]`, `[1062,1065,1068,1071]`, `[1063,1066,1069,1072]` and return
  `defines.CAREER_ZS/FS/SS`; the repaired catalog carries those same twelve ids with the
  `南遙/天寧/清嵐/加洛 × 戰士/法師/術士師道殿` names and the value `1588 × 1220` in all twelve.
* `DATA[1053]` (`兔坦卡門陵墓`, `4800 × 3600`) is the scene whose *name text* the stray key borrowed — i.e.
  the misframe also explains why the wrong key was a plausible-looking scene name.

**Remaining risk.** `candidate` only: static evidence, no native loader run. The key database still stores
the unusable `[1612, 3237, …]` for this entry and the survey used the solver's `(1615, 3239)`; both code
paths need the repaired value before this table can be trusted as CSV (§9.3 item 10).

---

## 2. Entry 400 / `script\data\sceneid2name.py` — "`DATA[1071]` has no same-key record in mapdata"

**Anomaly as delivered**: `entry_index: 400, table: DATA, issues: [{key: 1071, kind: "not_in_map_catalog"}],
count: 57, value_types: {tuple: 57}`.

**Why it fired.** `survey_csv_readiness.py` (line 189) asks whether every key of this table exists in the
*map catalog* built from entry 1301. Because 1301's decode lost key `1071` (its record appeared under the
text key, §1), 400's `1071` looked dangling. **Nothing is wrong with entry 400**: its own framing is
byte-code clean (`check → (True, 550)`), the marshal walk consumes the payload exactly (4790/4790), all
consts are valid cp950 and its 57 rows are plain 4-tuple *constants* (constant-pool objects, not built at
runtime). With 1301 repaired, `1071` *is* in the catalog.

**What the two tables are (from their own code, not from their names).**

| | 1301 `script\data\mapdata.py` | 400 `script\data\sceneid2name.py` |
|--|--|--|
| table | `DATA = {scene id -> {name, w, h}}` (104; dicts built at runtime: `BUILD_MAP` 105, `STORE_SUBSCR` 416, `LOAD_CONST` 728, `STORE_GLOBAL` 1 — pure literal) | `DATA = {scene id -> (name, related_id, w, h)}` (57; all rows are **tuple constants**: `BUILD_MAP 1`, `LOAD_CONST 114`, `DUP_TOP/ROT_TWO/STORE_SUBSCR` 57 each, `STORE_GLOBAL 1`) |
| API | `GetSceneSize(ID)→(DATA[ID]['w'],DATA[ID]['h'])`, `GetSceneName`, `GetSceneID(name)`, `GetSceneIDList()`, `GetParentMap` | `IsMiniMap(mapid) = DATA.has_key(mapid)`, `GetSceneIDByName(name)` (iterates `DATA.iteritems()`, compares `row[0]`, returns the key, default `0`), `GetShidaodianClass(iSceneID)` |
| size fields read by | `GetSceneSize` (consumers 159/215/539/2241/2931 …) | **nothing**: no entry of `script.fls` imports this module, so nothing reads `row[2]`/`row[3]` |
| importers | the name `mapdata` occurs in **21** entries' name tables (159 `mxgame\map\dlgmap.py`, 215, 290, 539, 743, 875, 891, 1023, 1227 `wrap\wrapui.py`, 1863, 2080, 2241 `mxgame\map\dlgworldmap.py`, 2341 `teamui.py`, 2512, 2931, 2965 `dlgnewguide.py`, 4059, 4144, 4676 `autofindpath.py`, 4837, 4957) + 2 as a *string* (4164, 4225) | **0** — see the note below |
| version branch inside the literal | none (only literal opcodes) | none (only literal opcodes) |

**Consumer note (honest negative result).** The identifier `sceneid2name` appears in **no** entry of
`script.fls` (checked recursively over every nested code object of all 5002 entries) and the string
`'sceneid2name'` appears in no constant either. `IsMiniMap`/`GetShidaodianClass` are *re-implemented* in
2804/4897 against their own tables, and 4676's `GetSceneIDByName` is its own local helper. So either the
module is reached by a mechanism not visible in the static configs, or it is a stale/duplicate table that the
current build no longer imports. This does **not** make its data wrong (it is internally consistent and
subset-consistent with 1301); it means the *consumer path* is the part that stays unresolved.

**Coverage / version relationship.** One shared *scene id* space: **400's 57 keys ⊂ 1301's 104 keys
(57/57)**, and the names agree for all 57. Both NPC tables use the same space as a superset: of 1301's 104
catalogued scenes, **70** also occur in 2601 and **70** in 2804; 36 of 400's ids occur in the NPC tables.
Whatever the version relationship is, 400 is not a copy of 1301 (57 ≠ 104, extra column) and not a subset in
*content* (its size pair differs for every shared scene). No file version marker or branch exists in either
module to date them; do not infer one.

**The genuinely open semantic question — 400's second column (`related_id`).**

* equals the row key for **40 / 57** rows;
* the twelve rows `1061…1072` (the 師道殿 scenes) **all** point at `2302` (a scene id that exists in the NPC
  tables but is not in the 1301 catalog);
* `1074 → 1042`, `1075 → 1047` — ids absent from the catalog; `1073 → 1041`, `1301 → 2121`,
  `1303 → 2122` — ids present in the catalog but with a **different name**
  (`1073 靈風塔一層 → 1041 靈石塔三層`, `1301 冒險家行會一層 → 2121 豪宅房屋`,
  `1303 冒險家行會二層 → 2122 豪宅二樓`);
* for the 43 rows whose `related_id` is itself a catalog key, the names agree in **40** cases.

Reading it as a *related scene / resource id* (shared by the 12 class halls; instance scenes reusing another
scene's resource) fits the shape of the data, but its exact meaning is **not established** and is left
unresolved (§9.3 item 1). It must not be renamed "scene id" and must not be used as a join key.

**Size semantics (verified, both variants).**

| comparison | identical | axis-swapped | other |
|------------|-----------|--------------|-------|
| 400 `(w,h)` vs 1301 `(h,w)` for the **row key** | 0 | **38** | 19 |
| 400 `(w,h)` vs 1301 `(h,w)` for **`related_id`** | 0 | **36** | 7 |

The 19 non-transposed rows (key-based) with their values and the row-specific ratios
(`1301_w/400_h`, `1301_h/400_w`):

```
1001 永澤城   400=(1800,2400)  1301=(2711,2020)  (1.130, 1.122)
1005 天水平原  400=(3000,4800)  1301=(4279,2800)  (0.892, 0.933)
1007/1013/1019 400=(1800,2400) 1301=(2700,2000)  (1.125, 1.111)
1025 清風村   400=(3000,4000)  1301=(3880,3280)  (0.970, 1.093)
1054 明月城   400=(6000,10000) 1301=(7300,5020)  (0.730, 0.837)
1061…1072 師道殿 (12 rows) 400=(1500,2000) 1301=(1588,1220) (0.794, 0.813)
```

So the two tables do **not** share a size semantics: for 38/57 scenes 400's pair is exactly 1301's pair with
the axes exchanged, and for 19 scenes the two pairs are different numbers (the same pair for all twelve
class halls) — a table-revision / different-quantity pattern that the byte evidence cannot decide.
**Both pairs must be carried as separate columns and no winner may be picked** (§9.3 item 2).

**Conclusion — statuses.** 400's own table: `confirmed_source_value` (57 rows, bytecode valid, walk clean,
0 invalid texts, no duplicate keys, no runtime construction). The `not_in_map_catalog` flag:
`confirmed_extraction_bug` — but **on the mapdata side** (1301's framing), not in 400; it disappears once
1301 is repaired. The second column (17 rows) and the size relation (19 rows): `legitimate_table_difference`
+ `unresolved`; the consumer path of the module: `unresolved`.

---

## 3. Entry 1799 / `script\data\npcname2realnamedata.py` — two constants that cannot encode

**Anomaly as delivered**: two `kind: encoding` issues — value row `個人心法教師`,
`bytes_hex: a4b8c646b9dc3acf`; key row `天選…`, `invalid_cp950_hex: a4d1bfefa8197c1a`; `count: 55`.

**Anomaly source (verified, plus one more symptom than reported).** The saved bounds
`[528, 1096, 1655, 2207]` put **three** boundaries 3–5 bytes late: `1096→1093`, `1655→1652`, `2207→2202`.
Each misplaced boundary corrupts exactly the constants/fields that straddle it and nothing else:

| saved slot | true slot | victim |
|-----------|-----------|--------|
| 1096 | **1093** | value constant of `個人心法教師` |
| 1655 | **1652** | key constant of the `天選…` row |
| 2207 | **2202** | the module code object's `co_name` — `b'<modu\xda\xd3\x88'` instead of `b'<module>'` |

**Original bytes.**

```
entry 1799  keys = [92(0x5c), 155(0x9b), 4(0x04), 210(0xd2), 100(0x64)]
            saved bounds = [528, 1096, 1655, 2207]      repaired bounds = [528, 1093, 1652, 2202]

const[31]  tag 's' payload 1083..1096  (value bytes 1088..1095)
  saved  : a4 b8 c6 46 b9 dc 3a cf     -> cp950 fails (0xb9dc.. is not text)
  correct: a4 b8 c6 46 b9 43 a5 50     -> 元靈遊仙
  bytes 1088..1092 need key 0x9b (5 bytes), bytes 1093..1095 need key 0x04 (3 bytes)

const[74]  tag 's' payload 1642..1655  (value bytes 1647..1654)
  saved  : a4 d1 bf ef a8 19 7c 1a     -> 天選 + invalid tail (0xa8 0x19 0x7c 0x1a)
  correct: a4 d1 bf ef a8 cf aa cc     -> 天選使者
  bytes 1647..1651 need key 0x04 (5 bytes), bytes 1652..1654 need key 0xd2 (3 bytes)

const[73] = a9 fa ab c2 = 明威  (the value of the 天選使者 row; unchanged by the repair)
co_name     saved b'<modu\xda\xd3\x88'   repaired b'<module>'
table shape DATA = {alias(bytes) -> real name(bytes)}; 55 rows; pure literal:
            BUILD_MAP 1, LOAD_CONST 110, DUP_TOP/ROT_TWO/STORE_SUBSCR 55 each, STORE_GLOBAL 1
```

**Reproduction (full sweeps, criteria 1–3).**

```
slot1 in 1089…1097 -> 1091…1096 all evaluate cleanly with 55 rows and 0 invalid texts,
                      but only 1093 yields the witness pair:
                      個人心法教師 -> 元靈遊仙 (a4 b8 c6 46 b9 43 a5 50)
                      天選使者     -> 明威     (a9 fa ab c2)
                      (1097 breaks the marshal walk: unknown tag 0xec at 1096)
slot2 in 1648…1656 -> only 1652 gives 0 invalid texts; 1648…1651/1653…1655 leave exactly one
                      invalid constant; 1656 breaks the walk (unknown tag 0xa5 at 1655)
slot3 in 2195…2211 -> 2197…2209 all evaluate; only 2202 yields co_name == b'<module>'
                      (2197 b'\x8a\xdb\xd9\xd2\xc3le>', 2198 b'<\xdb\xd9\xd2\xc3le>' …
                      2203 b'<modu\xdae>', 2205…2209 b'<modu\xda\xd3\x88', 2210 breaks)
```

The repaired `DATA` is **identical** for `slot3 = 2202` and `2207` — the third repair only un-corrupts the
code object's tail; the first two carry the payload meaning.

**Conclusion — status `candidate` (boundary repair, three slots).** Both "unencodable" constants are
boundary victims, not source errors, and they are fully explained byte-for-byte (5 bytes of one key + 3 bytes
of the next, twice). The names were **not** reconstructed from the displayed `天選…` prefix: after the repair
the key constant is byte-identical to `天選使者` (a lexeme attested by two other independent sources, see
below) and the value constant decodes to `元靈遊仙` by pure key application, not by completion.

**Cross-table corroboration (the table is heavily attested).** 1799's rows are `alias → real name`, and the
NPC tables carry exactly that pair in fields 0 and 11:

* 2601: **175** records whose field 0 is one of the 36 aliases used (of 55 rows); of the 71 records whose
  field 11 is set, **70 agree** with 1799 and **1 differs** (map 1054, npcid 1078, alias `藥店`; 1799 says
  `藥店老闆`, the record says `裝備店老闆` — that single mismatch stays, §9.3 item 8).
* 2804: 178 records / 37 aliases; 74 with field 11 set → **73 agree, same single mismatch**.
* 22 records have field 11 set for an alias 1799 does not list (e.g. `錢莊 → 錢莊老闆`), i.e. 1799 is not
  exhaustive; 19 of its aliases never occur as field 0 in the NPC tables.
* The two repaired rows are directly attested in the NPC tables: map 1032 contains
  `個人心法教師 / 元靈遊仙`, and maps 1014 + 1054 contain `天選使者 / 明威` (field 0 / field 11).

**Remaining risk.** `candidate` (no native loader). The `藥店` mismatch and the non-exhaustiveness must be
carried, not "fixed". The reader must also un-strand the table from its bounds: with the saved framing the
table *evaluates* and looks fine except for 2 unencodable constants — a mechanical check would have shipped
it with mojibake.

---

## 4. Entry 2601 / `script\data\npcposdata.py` — "rejected opcode 101 @124"

**Anomaly as delivered**: `status: not_recovered_by_this_reader`,
`error: "ValueError: unsupported opcode 101 at 124"`.

**Two independent causes, both verified.**

1. **Reader limitation.** `DATA` is assigned by one pure literal segment (`STORE_GLOBAL 'DATA'` at code
   offset 71691; 24719 instructions: `LOAD_CONST` 13831, **`LOAD_NAME` 6560**, `BUILD_TUPLE` 2606,
   `BUILD_MAP` 1, `BUILD_LIST` 430, `DUP_TOP`/`ROT_TWO`/`STORE_SUBSCR` 430 each, `STORE_GLOBAL` 1 — no call,
   no attribute access, no import, no branch). Every one of the 6560 name loads is index `co_names[10]`,
   whose value is the text `None`. The delivered reader's literal allowlist has no `LOAD_NAME`, so the very
   first "absent field" placeholder aborts recovery — the failure is a property of the *reader*, not of the
   table: the table does **not** depend on other variables, on a version condition, or on an init call.
   `permission`, `VER2MASK`/`ver2mask`, `GetData`, `InitTestData`, `DelShenHeNpc`, `IsNeedDelShenHeNpc` all
   exist in the module, but they are *other* code objects (functions), not part of the literal.
   The emitter uses the *name* `None` (not the `None` constant, which is also present in the module's const
   pool) for absent fields throughout this family; at runtime that name resolves to the `None` singleton via
   the builtins mapping — an inference from the language semantics, not an execution (no client run here).
2. **The saved bounds are wrong as well.** `[18821, 37733, 56546, 75375]` fails criterion 1 at payload
   **18821** — exactly the first byte of the misplaced boundary: raw `0xde` decodes to `0xf7` (unmapped)
   under the saved placement and to `0x8f` (`LOAD_CONST`) under the repaired one. Re-running criteria 1–4
   slot by slot (with the correct limits, `n_consts = 2035`, `n_names = 12`, `code_len = 71698`):

```
slot 0 : saved 18821 fails at 18799. In 18818…18835 **only 18827** yields a fully valid instruction
         stream (any other value fails within the misplaced window) -> 18827 (Δ +6 vs saved)
slot 1 : 37733 fails (unmapped 0x9e at 37711); 37734 and 37736…37739 break the *literal* (evaluator
         "underflow at 37711"); 37740/37741 fail (unmapped 0xea at 37717) -> **only 37735** gives
         430 maps / 1335 records / 10 unused consts -> Δ +2 vs saved
slot 2 : only 56546 keeps the whole code valid (56544/56545 leave the literal unevaluable) -> Δ 0
slot 3 : 75375 and 75377…75379 also evaluate (430 maps, 1335 records) — criterion 1–3 cannot separate
         them; criterion 4 does: 75375 makes the pair (1003, 4810) and 75377…75379 make (1003, 4810)
         as well, i.e. the join against 2804 has 663 common pairs / 655 identical, while **75376**
         yields 664 common / 656 identical. The single byte-level cause is `const[179]`:
              const[179] = 4764 with 75376   (record: 谷雨鎮商人, pos [46,40], shape gyzsr, map 1003)
              const[179] = 4810 with 75375   (a pair that exists in no other table)
         2804's DATA_POS independently records (1003, 4764) for 谷雨鎮商人 -> 75376.
```

So the delivered failure was *two* stacked defects: **`reader_limitation`** (allowlist) and a **boundary
misplacement** (`candidate`). The reader message ("opcode 101") is not evidence of the table being dynamic.

**Recovered content.** `DATA = {scene id -> [record, …]}`: **430 scenes, 1335 records**, every record a
14-field value `(display name, secondary name, npcid, type, [x,y], flag, ?, 255, shape, a, b, real name, ?,
?)`. 632 records carry `npcid == 0` (scene furniture / no NPC id); the remaining 703 records map onto **665
distinct `(scene, npcid)` pairs**, i.e. 12 pairs carry two or more records (multiplicity must be preserved:
the multiplicity histogram is `{1:653, 2:3, 4:5, 6:4}`). Type (field 3) ∈ {0,1,2}; field 7 is `255` in every
record; shape (field 8) has 378 distinct values.

**Consumers (recursive name-table scan over all 5002 entries).** `npcposdata` is imported by exactly **one**
entry: **1870** (`taiwan\npcpos_fix.py`, to rebind `DelShenHeNpc`). Every real consumer in this build calls
the *same API* on `minimapnpcpos` (2804/4897) instead: 4676 `autofindpath.py`
(`GetNpcPosByMapAndName`, `GetNpcNameByMapAndName`), 949 `char\npc.py` (`GetMapNpcNames`),
2341 `teamui.py`, 159 `dlgmap.py`, 539, 1697, 2120, 2965, 4010 … So 2601 is best read as the
`minimapnpcpos` table family's sibling (an older or alternate copy), and its data is the same kind of data:
`2601 ∩ 2804` = 664 pairs with 656 identical record-lists.

**Remaining risk.** `candidate` framing + reader rule; the `LOAD_NAME 'None' → None` rule must be an explicit,
documented reader feature; `npcid == 0` records (47 %) must not be dropped; and the multiplicities must be
kept as list-valued.

---

## 5. Entry 2804 / `script\data\minimapnpcpos.py` — "no supported literal assignment for DATA"

**Anomaly as delivered**: `status: not_recovered_by_this_reader`,
`error: "ValueError: no supported literal assignment found for DATA"`.

**Cause 1 — the variable name (extraction bug).** The module contains **no `DATA`**. Its two tables are

* **`DATA_POS`** — a pure literal assignment, `STORE_GLOBAL` at code offset **76119** (27062 instructions:
  `LOAD_CONST` 14364, `LOAD_NAME` 6600 (all `co_names[13] = 'None'`), `BUILD_TUPLE` 2624, `BUILD_MAP` 435,
  `BUILD_LIST` 434, `DUP_TOP`/`ROT_TWO`/`STORE_SUBSCR` 868 each, `STORE_GLOBAL` 1), and
* **`DATA_WENZI`** — a second pure literal, `STORE_NAME` at code offset **99135** (12020 instructions:
  `LOAD_CONST` 3916, `BUILD_MAP` 453, `DUP_TOP`/`ROT_TWO`/`STORE_SUBSCR` 2174 each, `BUILD_TUPLE` 574,
  `LOAD_NAME` 554, `STORE_NAME` 1).

So the survey asked for a name that does not exist in this module: a **`confirmed_extraction_bug` in the
target list**, not a defect of the file. The file is neither corrupt nor empty (434 + 165 scenes of data).
Init method: ordinary module-level literal assignment (at module scope `STORE_GLOBAL` and `STORE_NAME` are
the same operation) — there is no lazy init, no `import`-time hook, no version branch inside either literal
(`ver2mask`/`VER2MASK` exist in the module but are referenced only by `GetData`, not by the literals).

**Cause 2 — one constant, one byte (`const[544]`).**

```
entry 2804  keys = [65(0x41), 33(0x21), 179(0xb3), 28(0x1c), 4(0x04)]
const[544] tag 's' payload 106614..106627 (value bytes 106619..106626)
raw payload 106610..106630: 47 1c 1c 1c 6f 14 1c 1c 1c a1 b0 be aa a2 d5 b5 6d 6d 81 14 04
value bytes              : a1 b0 be aa a2 d5 b5 6d
  XOR 0x1c (saved slot3=106627): bd ac a2 b6 be c9 a9 71 = 蓮７導姒
  XOR 0x04 (slot3=106619)     : a5 b4 ba ae a6 d1 b1 69 = 打漁老張
```

**Cause 3 — one ambiguous slot (criteria cannot decide).** Slot 2 `79988` vs `79989` both survive criteria
1–3; they differ in exactly one place, the `港口` entry at position `(28,108)` of `DATA_WENZI[1022]`
(`desc 通往各國首都`, `jumpPos [25,102]`, `npcName 船夫`):

```
slot2 = 79988 -> npcID 324      slot2 = 79989 -> npcID 2008
```

The sibling entry **4897** (`minimapnpcpos_test.py`, same module shape down to the instruction profile of
`DATA_WENZI`) has the same table with the uniquely clean value `79961` (see §6.1); at 79961 its
`DATA_WENZI` is **identical to 2804's for all 165 scenes**, which selects **`79989`**. Working set:
**`[26695, 53365, 79989, 106619]`** — the only difference from the saved decode is those two records.

**Reproduction of cause 2 (sweep of slot 3, criteria 1–3 + name plausibility).**

```
slot3 = 106609…106614  marshal walk breaks (unknown tag 0x6b/0x71 at 106609/106614)
slot3 = 106615…106618  structural failure (index out of range)
slot3 = 106619         POS ok (434)  WENZI ok (165)  const[544] = 打漁老張  <-- matches 2601 + its own table
slot3 = 106620…106627  POS ok        WENZI ok        const[544] = 蓬漁老張 / 蓮漁老張 / 蓮╳老張 /
                                                      蓮７老張 / 蓮７憾張 / 蓮７導張 / 蓮７導姆 / 蓮７導姒
slot3 = 106628…106630  marshal walk breaks
```

Note that 106619…106627 **all pass criteria 1–3** (0 invalid texts, 434 + 165 rows, walk consumed): the
shifted text stays encodable, one character at a time. Only the semantic criterion (the name must be the one
the NPC tables carry) picks 106619 — and the witness is double: **both 2601 and 2804's own `DATA_POS`**
record `打漁老張` at `(scene 1020, npcid 4229)`, position `[81, 22]`, shape `dylz`.

**Recovered content.** `DATA_POS = {scene id -> {scene name -> [14-field records]}}`: 434 scenes, 1344
records (631 with `npcid == 0`; 713 records → 676 distinct pairs, 11 with multiplicity > 1).
`DATA_WENZI = {scene id -> {(x,y) -> {name, desc, jumpPos, npcID, npcName, servergrade}}}`: 165 scenes, 287
entries. The scene-name key inside `DATA_POS[scene]` is a *display name of the scene* — and it is **not**
always the same string as 1301's/400's name for that id:

```
1036 珊瑚迷宮1 vs 珊瑚迷宮      1039 靈石塔1層 vs 靈石塔一層   1040 靈石塔2層 vs 靈石塔二層
1043 古木祭壇1層 vs 古木祭壇一層   1073 靈風塔1層 vs 靈風塔一層
2151 小院子 vs 民宅庭院        2152 中院子 vs 華宅庭院      2153 大院子 vs 豪宅庭院
```

(a further reason never to join on names).

**Runtime mutation (static evidence, call site included).**

* `misc.py` (1693) ends `SetServerID` with `minimapnpcpos.InitTestData()` (its name table is
  `[… g_ServerID, LimitServerShowWarriorSelect, LimitServerCommandKey, ReplaceSeparateData_New,
  ReplaceOtherData, minimapnpcpos, InitTestData]`); 2054 `dlghongbao.py` references `InitTestData` too.
* `InitTestData` (2804, 4897 — and 2601 has its own copy) reads constants `[1054, 0, -1, 0, 戰隊使者, 0, 33,
  戰隊使者, 無雙, 5025, 1, [30,200], 0, None, 255, z, 0, 0, 無雙, None, None]` with names
  `[DATA_POS, values, enumerate, insert, None]` → it **inserts**
  `('戰隊使者','無雙',5025,1,[30,200],0,None,255,'z',0,0,'無雙',None,None)` at index 33 of one list of
  `DATA_POS[1054]`.
* `GetData(mapid)` (2601/2804/4897, names `[misc, IsFreshManServer, DATA(_POS), has_key, (values),
  DelShenHeNpc]`, constants `[-1, None, 1054, 1055, …]`) rewrites mapid **1054 → 1055** on freshman servers
  and then applies `DelShenHeNpc`; `GetMapNpcNames` applies the same rewrite.
* `DelShenHeNpc` (names `[hero, IsShenHe, IsNeedDelShenHeNpc, append]`) mutates the lists of the *returned*
  data by filtering 神合 NPCs when `hero.IsShenHe()`.
* 1870 (`taiwan\npcpos_fix.py`) rebinds `DelShenHeNpc` on both modules (see §6.2).

**Conclusion — `confirmed_extraction_bug` (wrong target name in the survey) + `reader_limitation`
(`LOAD_NAME 'None'`) + `candidate` (slots 3 and 2).** Neither literal depends on other variables, version
conditions or init calls; the mutations are consumer-side and must be documented, not baked into a CSV.

---

## 6. Entries outside the five, but part of the evidence

### 6.1 4897 `script\data\minimapnpcpos_test.py` — witness (used as `candidate` evidence only)

Same module shape as 2804 (`InitTestData`, `ver2mask`, `GetData`, `GetMapNpcNames`,
`GetNpcPosByMapAndName`, `GetNpcNameByMapAndName`, `IsNeedDelShenHeNpc`, `DelShenHeNpc`, `IsMiniMap`,
`GetShidaodianClass`, `GetMiniData`; `DATA_WENZI` has the *identical* instruction profile: 12020
instructions, `LOAD_CONST` 3916, `BUILD_MAP` 453, …). Saved bounds `[26677, 53319, 79959, 106579]`; slot 2
sweep:

```
79957/79958 unmapped 0x73 at 79936 ; 79959 -> evaluator rejects (std 63 BINARY_RSHIFT at 79937)
79960 CALL_FUNCTION_KW at 79938 ; 79962…79964 LOAD_NAME out of range ; 79965 unmapped 0xf9
79961 -> DATA_WENZI ok (165 scenes), DATA_POS ok (433 scenes)
```

At `79961` the table agrees with 2804 in full: `DATA_WENZI` **165/165 scenes identical**, `DATA_POS`
**674/674 common pairs have identical record lists** (2804 additionally has map 9908 and the pair
`(1327,5030)`; 4897 has no unique pairs). That full agreement is what pins `79989` for 2804's slot 2. Slot 0
(`26677` vs `26678`) is **not** discriminated by my probes; 4897 is therefore a witness, never a staged
table.

### 6.2 1870 `script\taiwan\npcpos_fix.py` — specimen, stays unresolved

`co_names` contains a name that cannot be an identifier (`D~ChhiIha^ehcEeNpc`, 18 bytes) beside the correct
`npcposdata`, `minimapnpcpos`, `DelShenHeNpc`, `Fix` — the same boundary-victim signature. Its `Fix()` body
holds two `STORE_ATTR DelShenHeNpc` instructions against `npcposdata` and `minimapnpcpos`, i.e. the Taiwan
build patches the 神合-filtering entry point at runtime. Because the operand of the first `STORE_ATTR` is the
corrupted name, I do **not** read 1870's binding as a semantic fact (`X.DelShenHeNpc = Y` must not be quoted);
my earlier probes could not separate two equally clean placements (`+10` and `+11` for slot 0), so 1870 stays
unrepaired and is listed as unresolved.

---

## 7. Required analysis focus

**(a) Client-side consumers (recursive scan of all 5002 entries' name tables — module-level *and* nested
code objects).**

| table / API | consumer entries |
|-------------|------------------|
| 1301 `mapdata`: `GetSceneSize` | 159 `dlgmap.py`, 215, 539, 2241 `dlgworldmap.py`, 2931 (+ 1301 itself) |
| `GetSceneName` | 159, 290, 539, 875, 1023, 1026, 1227, 2341 `teamui.py`, 2965, 3222, 4144, 4676, 4957 |
| `GetSceneID` / `GetSceneIDList` | 518, 539, 673, 1129, 1697, 1863, 1869, 2241, 2512, 2663, 4059, 4676, 4837, … (14 callers in total) / 1227, 2241 |
| `GetParentMap` (+ `MAP_ASCRIPTION`) | 2241 (`MAP_ASCRIPTION` itself is used by nothing else) |
| `mapdata` module name | 21 entries + 2 as literal string (4164, 4225) |
| 400 `sceneid2name` | **none** (see §2) |
| 1799 `npcname2realnamedata` (`GetRealName`) | 159, 2601, 2804, 4897 (+ 1456 `dlgprofession.py`, 2491, 4287 use their own `GetRealName`) |
| 2601 `npcposdata` | imported only by 1870 |
| 2804/4897 `minimapnpcpos` | 159, 450, 518, 539, 949 `char\npc.py`, 1693 `misc.py`, 1697, 1870, 2120, 2341, 2965, 4010, 4676 |
| `GetMiniData` (`DATA_WENZI`) | 159, 539 |
| `GetNpcPosByMapAndName` / `GetNpcNameByMapAndName` | 4676 |
| `GetMapNpcNames` | 949 |
| `IsMiniMap` | 159, 518, 1697 (2804/4897 implement their own on `DATA_POS`) |
| `GetShidaodianClass` | 2341 (+ 400/2804/4897 own implementations) |
| `InitTestData` | 1693 (`SetServerID`), 2054 `dlghongbao.py` |
| `DelShenHeNpc` | 1870 |

**(b) Scene id / map id / related resource id.** One *scene-id* space is used consistently by the catalog
(1301), the minimap-scene table (400) and both NPC tables (2601/2804/4897): 400 ⊂ 1301 as key sets
(57/57), NPC tables are a superset of the catalog (70 of 104 catalogued ids occur in each; 360/364 ids in
the NPC tables are not in the catalog — instance/event scenes such as 2302, 9050, 9444). The NPC tables are
keyed by exactly that scene id. 400's **second column is a different id-like value** (§2) and must not be
called a scene id until its meaning is established; `MAP_ASCRIPTION` maps child → parent *scene* id (not to a
resource id). No table in this round carries a separate "map resource id" column whose identity is proven.

**(c) Size fields in different tables are not the same quantity.** For the same scene, 1301's `(w,h)` and
400's `(w,h)` are never identical (0/57): 38 rows are exact axis transposes, 19 rows differ per-row by
scene-specific factors (table above). 1301's `(w,h)` *is* consumed in client code (`GetSceneSize`), 400's
pair is read by no script. `DATA_WENZI`'s `jumpPos` is yet another pair (jump target inside the minimap
frame), and NPC positions `[x,y]` live in a coarse third frame: comparing positions with 1301 sizes gives
median `w/max(x) ≈ 25.8`, `h/max(y) ≈ 27.3` (10th pct ≈ 22; max coordinate 332 for a 10000-wide scene) —
**no single scale factor exists**, so no conversion or clamping may be applied.

**(d) How NPC name, shape and coordinates relate.** One 14-field record carries them as independent fields:
field 0 = display name / alias (what 1799 translates and `GetMapNpcNames` returns), field 1 = secondary
name, field 2 = npcid (`0` = no NPC), field 3 = type (0/1/2), field 4 = `[x,y]`, field 7 = `255` everywhere,
field 8 = shape/sprite code (378 distinct values, e.g. `gyzsr`, `dylz`, `ntklb`), field 11 = real name
(optional; `None` in 1242 of 1335 records). Name ↔ shape ↔ coordinates are independent: no field is
derivable from another, and 1799 corroborates field 0 ↔ field 11 for 70/71 (2601) and 73/74 (2804) records.

**(e) Version filtering and runtime initialization.** **Inside** the five literals there is no branch, no
call, no import, no name reference except the `LOAD_NAME 'None'` placeholder (opcode profiles in §4/§5; for
1301/400/1799 there is not even the placeholder). Version/runtime behaviour exists only in the *consumers*:
`misc.SetServerID → minimapnpcpos.InitTestData()` (inserts `戰隊使者`), `GetData` (1054 → 1055 on freshman
servers) + `DelShenHeNpc` filtering, `GetMapNpcNames`'s same rewrite, and `taiwan\npcpos_fix.py::Fix()`
rebinding `DelShenHeNpc`. A CSV staged from these tables is the **pre-mutation** state; the transforms must
be documented as consumer behaviour, not applied to the staged rows.

---

## 8. Systemic note (what connects the items)

1. **Boundary-victim class.** Every anomaly in this round except 400's cross-check flag is caused by a
   constant/field straddling a slightly mis-placed 4-byte XOR boundary: 1301 (key constant; +1 solver, +4 DB),
   1799 (value constant, key constant, `co_name`; 3–5 bytes), 2601 (slot 0 +6, slot 1 +2, slot 3 +1), 2804
   (`const[544]`, 8 bytes; slot 2 +1), 4897 (slot 2 +2), 1870 (`co_names`). Mechanical checks (opcode
   validity, walk consumption, "valid cp950") pass on several *wrong* placements — only a semantic rebuild
   plus a cross-table witness discriminates. The key database's stored bounds and the span solver's placement
   disagree for 1301 (`[1612,3237]` vs `(1615,3239)`), so both code paths need the repaired value.
2. **`LOAD_NAME 'None'` placeholder.** 1970 of 4989 walkable entries carry `None` in the module name table;
   282 actually *load* it, and the five heaviest users are exactly the big static tables: 2804 (7154 uses,
   `co_names[13]`), 4897 (7144, index 13), 2601 (6560, index 10), 244 `newfurnituredata.py` (1050),
   3935 `charpartdata.py` (237). It is an encoding idiom of the exporter (the `None` *constant* is present in
   the pool as well; the emitter chose the name), not per-entry damage. Readers must implement it explicitly.
3. **A raw statistic, offered as a lead, not a verdict.** With the saved key/bound sets my strict
   module-level bytecode check rejects **447 of 4989** walkable entries (13 further entries fail the marshal
   walk outright: 64, 1013, 1528, 1854, 1931, 2643, 2984, 3066, 4133, 4166, 4305, 4691, 4928). **398 of the
   447 first fail within 0–8 bytes after one of that entry's saved boundaries** — the same signature as this
   round's items. I did not repair those (out of scope, and most are not map/NPC data); a per-entry check of
   the failing byte (mapped opcode? argument in range?) is work for the decoder owners.
4. **Specimen 1870** — see §6.2. Not repaired; its binding semantics must not be quoted.
5. **Family inventory (from `co_filename` of all 4989 walkable entries).** `mapdata.py` has eight namesakes
   (`fubenmapdata.py` 633, `style4resmapdata.py` 2999, `newoldcolormapdata.py` 3285,
   `yardmapdata_oldyard.py` 3381, `hanghaimapdata.py` 3393, `oceanmapdata.py` 3771, `yardmapdatamgr.py` 3938,
   `yardmapdata_room.py` 4673) and the NPC-position family has two members outside the selected entries:
   * **4532 `script\data\minimap_data.py`** — a third table of the `DATA_WENZI` shape, 163 scenes vs 2804's
     165 (2804 additionally has 1327, 9907). Its saved framing is short in **two** slots: the field *name*
     `servergrade` decodes as the smeared `s&15&1$1"'&` (slot 2 must move −10: `19591 → 19581`) and one jump
     coordinate decodes as a garbage 32-bit int `-1920103164` (slot 3 must move −3: `26083 → 26080`). After
     both repairs **161 of the 163 shared scenes are byte-identical to 2804's `DATA_WENZI`**; the surviving
     differences are map 1018's `靈石塔一層` jump key `(61,125)` vs `(58,125)` and `靈風塔一層` `jumpPos`
     `(135,40)` vs `(135,18)` — the same small coordinate deltas that separate 2601 from 2804 there. This
     makes 4532 an independent witness for the `DATA_WENZI` schema (field names included) and shows that the
     boundary-victim class is not confined to the selected entries.
   * **4516 `script\data\npcposfixdata.py`** — `DATA` is an *empty* literal (0 rows) beside a `GetData`
     helper; it is imported by 159 `dlgmap.py` and 2965 `dlgnewguide.py` (with the token
     `GetNpcDataBuyNpcName`). A "fix" table that is empty in this build is worth remembering when the join is
     built; it is not staged here.

---

## 9. Deliverables for the coordinator

### 9.1 Reliable-join proposal

1. **Join keys are `(scene id, npcid)`** — two integers, and only ever within one table pair
   (2601 ↔ 2804/4897). Never join on display names, real names, scene *names* or shapes (2804's inner scene
   names differ from 1301/400 for 8 scenes; NPC display names differ between 2601 and 2804 in 8 cases), never
   on coordinates.
2. **Records are list-valued.** 2601 has 12 duplicated `(scene, npcid)` pairs among 665 (703 records);
   2804 has 11 among 676 (713 records); a join must compare *lists* (664 common pairs: 656 identical lists,
   8 differing) — comparing only the first record hides real differences.
3. **Keep every coordinate/size frame separate**: 1301 `(w,h)`; 400 `(w,h)` (own convention, unresolved);
   NPC `[x,y]` (coarse frame); `DATA_WENZI` `jumpPos`. No derived conversion factors.
4. **Use 1799 only as a display-name translator** (`alias → real name`) applied to field 0, exactly as
   `GetMapNpcNames` does; never promote it to a join key and never overwrite field 0.
5. **Provenance on every row**: entry index, `co_filename`, boundary/key set, the reader rules needed
   (`LOAD_NAME 'None' → None`; bytecode check with per-code-object limits), and the sentence
   *"candidate framing, not yet confirmed by the native loader"*.
6. **Stage relationships, not merges**: the 2601↔2804 comparison as its own table (one row per pair, both
   sides' fields, `agreement` flag).
7. **Do not build one "complete map-NPC table"** by unioning 2601/2804/4897 or folding 1301/400 into it.

### 9.2 CSVs suggested for staging (as candidates; `server/docs/` staging area, never `server/game_data/`)

| CSV | source | rows | columns / notes |
|-----|--------|------|-----------------|
| `mapdata.scene_dictionary.csv` | 1301 `DATA`, `[1616,3239,4884,6553]` | 104 | `scene_id, name, w, h` |
| `mapdata.parent_scene.csv` | 1301 `MAP_ASCRIPTION`, same | 6 | `scene_id, parent_scene_id` |
| `sceneid2name.minimap_scenes.csv` | 400 `DATA` (saved bounds verified) | 57 | `scene_id, name, related_id, size_a, size_b`; `related_id` flagged unresolved |
| `npcname2realnamedata.alias_to_realname.csv` | 1799 `DATA`, `[528,1093,1652,2202]` | 55 | `alias, real_name` |
| `npcposdata.records.csv` | 2601 `DATA`, `[18827,37735,56546,75376]` | 430 scenes / 1335 recs | 14 raw fields + named columns; `npcid=0` kept; multiplicity kept; reader rule documented |
| `minimapnpcpos.pos_records.csv` | 2804 `DATA_POS`, `[26695,53365,79989,106619]` | 434 / 1344 | same schema family as 2601 |
| `minimapnpcpos.wenzi_entries.csv` | 2804 `DATA_WENZI`, same | 165 / 287 | `scene_id, x, y, name, desc, jump_x, jump_y, npcID, npcName, servergrade` |
| `npc_2601_vs_2804.agreement.csv` | join of the two above | 664 pairs | both sides + `agreement`; 8 rows flagged |

**Do not stage** 4897 (test sibling; witness only), 1870 (`npcpos_fix`), 4532/4516 (out-of-scope family
members), any mutation-applied view (`GetData`/`InitTestData`/`DelShenHeNpc` results), or any merged
map-NPC table. Every file should carry the provenance block and the *candidate framing* sentence.

### 9.3 Records that must stay unresolved

1. **400 `related_id` (17 rows)** — no verified meaning: `1061…1072 → 2302`, `1073 → 1041`, `1074 → 1042`,
   `1075 → 1047`, `1301 → 2121`, `1303 → 2122`; in particular the three name-mismatch rows
   (`1073 靈風塔一層/1041 靈石塔三層`, `1301 冒險家行會一層/2121 豪宅房屋`,
   `1303 冒險家行會二層/2122 豪宅二樓`) must not be normalized either way.
2. **400 vs 1301 sizes** — the **19** rows where the two pairs are not an exact axis transposition
   (1001, 1005, 1007, 1013, 1019, 1025, 1054, 1061…1072) must be carried as two separate columns; do not
   pick a winner.
3. **2601 ↔ 2804 differences (8 of the 664 shared pairs, list compare)** — no side may be dropped or "fixed":
   * display name (field 0): `(1014,5011)` `陣營任務` / `陣營功績`;
   * position (field 4): `(1018,4313)` `[131,77]`/`[128,80]`, `(1018,4326)` `[46,59]`/`[40,52]`,
     `(1018,4484)` `[135,23]`/`[135,18]`, `(1018,4975)` `[83,29]`/`[81,22]`;
   * real name (field 11): `(1025,4152)`, `(1157,4152)` — 2601 `None` vs 2804 `倉庫管理員`;
   * multiplicity: `(1010,4137)` — two identical records in 2601, one in 2804.
   Pairs present in only one table: 2601-only `(1179,5020)`; 2804-only `(1023,2013)`, `(1055,5025)`,
   `(1179,5019)`, `(1327,2014)`, `(1327,5026…5028)`, `(1327,5030)`, `(9515,1002)`, `(9907,1003)`,
   `(9907,1005)`, `(9908,3007)`. (Note: for `(1014,5011)` a *third* table, 1799, lists the alias
   `陣營功績 → 鎮魔將軍`, which is 2804's spelling — recorded as evidence, not as a licence to overwrite
   2601.)
4. **2804 slot 2** `79988` vs `79989` — settled only *through* 4897's agreement (and 4897's own slot 0
   `26677/26678` is not discriminated at all). Both entries keep the "candidate" marker.
5. **1799 ↔ NPC tables**: 19 aliases never occur in 2601 (18 in 2804); the single disagreement
   (`藥店` @ map 1054 npcid 1078, real name `裝備店老闆` vs 1799's `藥店老闆`) must stay visible.
6. **1870 `taiwan\npcpos_fix.py`**: framing unrepaired (two equally clean placements for slot 0), corrupted
   `co_names` entry; `Fix()`'s binding semantics must not be quoted as fact.
7. **400's consumer path**: no entry imports `sceneid2name`; do not assert the module is dead or live.
8. **All repaired framings are `candidate`** (1301, 1799, 2601, 2804, 4897-slot2): no native-loader run was
   possible under this round's constraints.
9. **NPC `npcid == 0` records** (632 in 2601, 631 in 2804): they cannot be joined by npcid. Keep them in the
   staged CSVs, unresolved — do not drop and do not invent ids.
10. **Decoder fixes required (not data changes)**: (i) implement `LOAD_NAME 'None' → None` in the literal
    reader; (ii) update 1301's stored bounds (`[1612,3237,…]`) and stop letting the span solver overwrite
    them with `(1615,3239)`; (iii) update 2601's (`[18821,37733,56546,75375]` → `[18827,37735,56546,75376]`),
    2804's slot 2/3 (`79988→79989`, `106627→106619`), 4897's slot 2 (`79959→79961`), 1799's
    (`1096/1655/2207` → `1093/1652/2202`); (iv) re-run the `not_in_map_catalog` cross-check for entry 400
    after the 1301 repair; (v) have the owners look at the 447/398 lead (§8.3).

---

## 10. Status summary

| item | entry | anomaly | root cause | status | residual |
|------|-------|---------|-----------|--------|----------|
| 1 | 1301 `mapdata.py` | text key `兔坦卡門陵墓` instead of the int key `1071` | boundary 1 one byte early in the solver frame (`1615`), four bytes early in the key DB (`1612`); `LOAD_CONST 1071` stranded | `candidate` — correct bounds `[1616,3239,4884,6553]`, corroborated by 400 + the class-hall logic | native confirmation; DB update |
| 2 | 400 `sceneid2name.py` | key 1071 "not in map catalog" | artifact of 1301's misframe (the record hid under the text key) | flag = `confirmed_extraction_bug` **on 1301**; 400 data = `confirmed_source_value` | `related_id` (17), size pairs (19), consumer path = `unresolved` |
| 3 | 1799 `npcname2realnamedata.py` | two constants fail cp950 | slots 1096→1093, 1655→1652, 2207→2202 (3–5 bytes late each) | `candidate` `[528,1093,1652,2202]`; names `個人心法教師→元靈遊仙`, `天選使者→明威` corroborated in 2601/2804 | native confirmation |
| 4 | 2601 `npcposdata.py` | "unsupported opcode 101 @124" | reader allowlist lacks `LOAD_NAME 'None'` (6560 uses) **and** saved bounds misframed (slot 0 +6, slot 1 +2, slot 3 +1) | `reader_limitation` + `candidate` `[18827,37735,56546,75376]` (slot 3 pinned by the `谷雨鎮商人`/const[179] join) | reader rule; native confirmation |
| 5 | 2804 `minimapnpcpos.py` | "no supported literal assignment for DATA" | the module has `DATA_POS`/`DATA_WENZI`, no `DATA`; one corrupted constant (`const[544]`) and one ambiguous slot | `confirmed_extraction_bug` (target name) + `reader_limitation` + `candidate` `[26695,53365,79989,106619]` | slot 2 settled only via 4897; joint identification with 4897 |
| witness | 4897 `minimapnpcpos_test.py` | — | slot 2 two bytes early (`79959`); slot 0 ambiguous | `candidate` (slot 2 → `79961`) | witness only |
| specimen | 1870 `taiwan\npcpos_fix.py` | corrupted `co_names` entry | same boundary-victim class | `unresolved` | framing not repaired; `Fix()` semantics not established |

---

## 11. How to reproduce

Repository root, `PYTHONDONTWRITEBYTECODE=1`, CPython 3.11:

* survey baseline: `python3 server/tools/survey_csv_readiness.py` (38/48 recovered);
* architecture tests: `python3 -m unittest discover -s server/tests/architecture -v`;
* this report's probes (scratch, `/tmp/mx`, may not persist): an independent marshal walker with interned
  `TYPE_STRINGREF` resolution, `payload → decode with (bounds, keys) → walker → module code object`, then a
  segment-based literal evaluator for `STORE_NAME`/`STORE_GLOBAL` targets, plus a per-slot boundary sweep
  over the four criteria above. Nothing in this round was run against the client or the server.
