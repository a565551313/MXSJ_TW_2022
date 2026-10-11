# AGENT_C — pet detail / aptitude / graph / monster-description extraction check

Scope: entries **2027** (`script\data\petdata.py`), **1115** (`script\data\mxpetdata.py`),
**2954** (`script\data\petaptitudedata.py`), **1761** (`script\data\petgraphdata.py`),
**3526** (`script\data\monsterdata.py`). Zero-based `script.fls` entry indices, not game ids.
Read-only review: the client archive, the shared key database and the production
`server/game_data/` were **not** modified; nothing was written into any key database or
CSV release. No recovered script was executed (all probes are static: XOR decode → marshal
walk → literal extraction, plus a private Py2.5 bytecode disassembler).

## 1. Inputs and reproducibility

| material | sha256 |
|---|---|
| `data/script.fls` (24,454,082 B) | `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72` |
| `tools/decompiler/script_fls_keys.json` | `43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb` |
| entry 2027 payload (zlib-decompressed, XOR payload) | `e979fc6b22d39f3b86ef04dcfeb7aff105f51741e308975861856a6d12f6aa9e` |
| entry 1115 payload | `a9482d7da48a2ac17eb01001e455639a2fba33a9e055a6c42dfddf95356e325b` |
| entry 2954 payload | `e697e53ddb71219030c8d9a609ae9a21362255ea173e123af13af1f59ca59b55` |
| entry 1761 payload | `b4a1cfbd8394340685eb0a49d301047c0da75cdf98470773aa31ee3665056f0a` |
| entry 3526 payload | `1fdd20719349d4d3ecd1556ea09ccf27336970a672b230d81cdf0a03dbd8d5ff` |

Entry metadata (keys, saved bounds, rows; all verified this round):

| idx | file | keys | saved bounds | DATA rows |
|---|---|---|---|---|
| 2027 | `script\data\petdata.py` | [220, 251, 132, 12, 100] | [5383, 10831, 16277, 21755] | 135 (+`SHAPE2ICON` 1) |
| 1115 | `script\data\mxpetdata.py` | [122, 243, 64, 127, 196] | [825, 1699, 2546, 3375] | 137 |
| 2954 | `script\data\petaptitudedata.py` | [113, 215, 173, 43, 182] | [3973, 7978, 11868, 15798] | 132 |
| 1761 | `script\data\petgraphdata.py` | [135, 162, 221, 100, 139] | [6574, 13324, 19838, 26338] | 134 |
| 3526 | `script\data\monsterdata.py` | [239, 118, 48, 73, 171] | [17980, 35980, 54089, 71945] | 143 |

Reproduction hook (read-only, no repo file is written):

```python
import importlib.util; from pathlib import Path
ROOT = Path('/home/user/MXSJ_TW_2022')
spec = importlib.util.spec_from_file_location('rcdb', ROOT/'server/tools/review_client_data_boundaries.py')
rcdb = importlib.util.module_from_spec(spec); spec.loader.exec_module(rcdb)
REV = rcdb.Review()
co  = REV.load(2027, [5383,10831,16264,21751], use_solver=False)   # candidate bounds
tbl = rcdb.extract_table(co, b'DATA')
rcdb.text_errors(co)                                               # CP950 check (module-level helper)
```

`use_solver=False` is mandatory for any boundary statement: the heuristic
`solve_py25_co_span` repair silently normalises co_code bytes and hides the differences
under test (see §3.3). All conclusions below were produced with `use_solver=False` except
where explicitly noted.

Candidate bound sets used in this report (local hypotheses only, not installed):

```
2027: [5383, 10831, 16264, 21751]
1115: [ 828,  1699,  2546,  3375]
2954: [3973,  7979, 11868, 15798]   # evidence-level only; values deliberately NOT applied
1761: [6574, 13203, 19731, 26330]
3526: [17980, 35954, 53933, 71908]
```

Global effect of the candidate bounds (whole-payload marshal string walk, raw decode):

| entry | strings | strings failing strict CP950 (saved) | (candidate) |
|---|---|---|---|
| 2027 | 843 | 2 — spans (16241,16277), (21747,21755) | 0 |
| 1761 | 208 | 3 — spans (13149,13324), (19693,19838), (26267,26338) | 0 |
| 3526 | 767 | 3 — spans (35894,35980), (53873,54089), (71861,71945) | 0 |
| 1115 | 134 | 0 | 0 |
| 2954 | 49 | 0 | 0 |

Every saved-boundary string that fails strict CP950 is one of the assigned items, and the
candidate bounds remove **all** failures in the three text entries without changing row
counts (135/134/143) or any other string.

## 2. Status vocabulary used

`confirmed_extraction_bug` · `confirmed_source_value` · `legitimate_table_difference` ·
`reader_limitation` · `candidate` · `unresolved` (as defined by the coordinator).

## 3. Item findings

### 3.1 Item 1a — 2027 `DATA[2600]['address']` (出現地點 of 亡靈力士)

* payload span **(16241, 16277)**, 36 bytes; table path `DATA[2600][b'address']`.
* saved bytes `a558b27ba661c249a1472372a8dfafabb7b5bff2a77d23fa205721d22dec22713b26315b`
  — strict CP950 **fails** (invalid trailing 13 bytes).
* candidate bytes `a558b27ba661c249a1472372a8dfafabb7b5bff2a77d2372a8dfa95aa564aaf9b3aeb9d3`
  → `出現地點：#r兔神殿遺址#r兔坦卡門陵墓`.
* byte-level basis: the saved and candidate decodings differ exactly on string bytes
  [23,35] and the XOR delta over that run is constant **0x88 = 132 ^ 12 = keys[2] ^ keys[3]**
  — i.e. those bytes were decoded with the neighbouring segment's key. The first byte of
  the damaged run is payload **16264**, so the correct third boundary is 16264, not 16277.
* independent twin: `monsterdata.py` (entry 3526, saved bounds, clean) `DATA[2600]['address']`
  is byte-identical to the candidate value. `petgraphdata.py` `DATA[2600]['adress']`
  contains the same text without the `出現地點：#r` prefix.
* status: **confirmed_extraction_bug** (recovery uniquely determined; twin + constant key delta).
* unexcluded explanations: none for the byte damage; the residual assumption is that the
  same text is legitimately duplicated in `monsterdata` (verified byte-identical).

### 3.2 Item 1b — 2027 `DATA[4011]['maySkillLst'][3]` (仙獸吉祥虎, 4th candidate skill name)

* payload span **(21747, 21755)**, 8 bytes.
* saved bytes `b2d7afc5d902cc27` (decodes to `終級` + invalid bytes);
  candidate bytes `b2d7afc5b16aa44f` → **`終級強力`**.
* byte-level basis: saved/candidate differ on bytes [4,7] with constant delta
  **0x68 = 12 ^ 100 = keys[3] ^ keys[4]**; first damaged byte = payload 21751 → correct
  fourth boundary 21751 (not 21755).
* independent twins: (a) the identical byte string `b2d7afc5b16aa44f` occurs intact under
  **saved** bounds elsewhere in the same table — records 2470 `maySkillLst[1]`,
  4009 `maySkillLst[1]`, 4018 `maySkillLst[3]`; (b) `monsterdata.py` `DATA[4011]['lock3']`
  possible-skill list is `新月獠牙、終級命中、終級神跡、終級強力`, matching the candidate
  `maySkillLst` (`新月獠牙`, `終級命中`, `終級神跡`, `終級強力`) name-for-name.
* status: **confirmed_extraction_bug**.
* skill-ID note (Agent D interface): this report only certifies the **name** `終級強力`
  (CP950 bytes `b2 d7 af c5 b1 6a a4 4f`). No `skill_id` is generated here. Pet identifier:
  data key **4011**. Cross-reference: `monsterdata` key 4011 lock3.

### 3.3 Item 2 — 1115 `DATA[2910]` (mxpetdata name for 混沌騎士)

* saved bounds `[825,1699,2546,3375]` are **not raw-decodable at all**
  (`Review.load(1115, use_solver=False)` → `IndexError: tuple index out of range`);
  the solver-repaired path returns `DATA[2910] = 2280` (int) — the **only** non-bytes
  value among the 137 rows (`value_types {bytes:136, int:1}`), i.e. a schema violation.
* isolated sweep of boundary 0 (813…840): only `t=828` gives a fully bytes-valued table
  (137 rows, `2910 = 混沌騎士`); `t=829` gives `2910 = 2280`; everything else fails to build.
  With `[828,1699,2546,3375]` the *only* row that differs from the saved/solver table is 2910.
* byte-level basis (structural, no CP950 involved): raw payload bytes [815,845) are
  `7a7f4af5d47a20f5d57a7f4af543f3a97c42f3f6c37c41f3a97c40f3f6c3`.
  * saved decode: `0005308fae005a8faf00 8cb906 b0005a8fb10005308fb2005a8fb3000530` → breaks the record pattern at 825–827.
  * candidate decode: `0005308fae005a8faf00 0530 8fb0005a8fb10005308fb2005a8fb3000530` → restores the strictly periodic
    `<05 30 8f k>` / `<5a 8f k+1>` sequence for k = ae, af, b0, b1, b2, b3.
  Three bytes (825–827) were decoded with key[1]=243 instead of key[0]=122; the correct
  first boundary is therefore **828**, not 825.
* independent cross-table check: `petdata.py` (entry 2027, saved bounds, clean)
  `DATA[2910]['name']` = `混沌騎士`; `mxpetdata` is a parallel flat id→name map, so the
  candidate value restores agreement with the detail table.
* status: **confirmed_extraction_bug** (recovery candidate `828`; the saved bounds for this
  entry are unusable in raw mode and must be treated as broken by Agent A's pipeline).
* collaboration request (Agent A): ratify the corrected first bound for entry 1115 in the
  key database; until then no production change is made here.

### 3.4 Item 3 — 2954 `DATA[2800]` (機甲少女: 法力資質 2130 vs 法力資質最大值 1989)

Facts (raw decode, `use_solver=False`):

* saved bounds `[3973,7978,…]` → `法力資質 2130`, `法力資質最大值 1989`
  (plus 防禦 1760/2059, 攻擊 2120/2480, 速度 1850/2164, 體力 1850/2164).
* candidate `[…,7979,…]` → `法力資質 1700`, everything else identical. The two settings
  differ in exactly **one field slot table-wide**; the 4 `text_errors` entries are identical
  in both (they are the binary `code` blobs of the module, not table text).
* all four other pairs of record 2800 satisfy `max = floor(base*1.17)` exactly; the 法力 pair
  does not (2130 → 2492 ≠ 1989). Under the candidate it does: `1700*117//100 = 1989`.
* record 2800 is the **only** row in all 132 aptitude records whose stored maximum is smaller
  than its base (verified over the whole saved table); `2130` is otherwise used only as a
  maximum (2570 水晶女妖 體力資質最大值).
* `1700` is not an unusual value in its own right: it is the stored base of 28 other
  attribute slots, so the candidate reading is consistent with the table's own value domain.
* displacement direction: the saved boundary 7978 puts the last byte of key[1]'s segment into
  key[2]'s segment; the candidate moves the boundary one byte later to 7979. The difference
  of the two decoded bytes is `0x7A = keys[1] ^ keys[2]` (215 ^ 173), the same constant
  key-pair delta pattern as the tail-law cases in §3.1/§3.5/§3.6, with shift +1.
* mechanism: payload byte **7978** (raw `0xE0`) is the low byte of the imm16 operand of the
  custom-format `LOAD_CONST` whose opcode sits at co_code offset **7955**; the operand byte
  itself is co_code offset **7956**. Saved key[2]=173 decodes it to `0x4D` (77 → const 2130);
  candidate key[1]=215 decodes it to `0x37` (55 → const 1700). Both parses are structurally
  valid bytecode, so the decision is content-based, not structural.
* whole-object diff between the two alignments (raw, `use_solver=False`):
  co_code byte 7956 is the **only** byte that differs in the transpiled code object;
  `consts` and `names` are identical; `text_errors` are the same 4 entries in both (they are
  the binary `code` blobs of the module and its three const-code children, not table text).
  Table-side, the only differing cell is `(2800, 法力資質)`: 2130 vs 1700. The boundary shift
  is therefore surgical, exactly one integer field.
* solver masking: `use_solver=True` returns 2130 for **both** bounds (the repair normalises
  the byte), so the standard pipeline cannot see this question; batch-decode artefacts also
  record entry 2954 as `status=fail` (no independent second decode exists in the repo).

Conclusion: **not field semantics** (both readings are the same named field; `最大值` stays
1989) and **not a provable source value** — the evidence favours an off-by-one boundary
artifact that would make the row obey the client's own 1.17 relation, but there is no twin
and no authoritative independent boundary source. Status: **candidate**. Per assignment the
numbers are **not** swapped or rewritten; the row must be quarantined in any review CSV and
exported only with the flagged status. Residual alternatives kept on record: (i) original
source data really stores 2130 with a stale maximum; (ii) the true boundary is correct at
7978 and some other explanation applies to the 2130/1989 pair.

### 3.5 Item 4 — 1761 `desc[0]` of records 2190, 2600, 4015

All three are single-key-delta damages of the same kind; each candidate boundary equals the
first damaged byte of the string, and each candidate text equals the corresponding
`monsterdata` `lock1` text preceded by the standard prefix `未知的怪物，暫時無法獲知任何信息,`.

| record | payload span | saved delta run | delta | candidate text |
|---|---|---|---|---|
| 2190 | (13149,13324) | bytes 54…174 (121 B) | 0x7F = 162^221 | `未知的怪物，暫時無法獲知任何信息,穿著鎧甲拿著大刀和盾牌的兔子…` |
| 2600 | (19693,19838) | bytes 38…144 (107 B) | 0xB9 = 221^100 | `未知的怪物，暫時無法獲知任何信息,亡靈力士同樣來自埃及…` |
| 4015 | (26267,26338) | bytes 63…70 (8 B)  | 0xEF = 100^139 | `未知的怪物，暫時無法獲知任何信息,充滿靈氣的梅花鹿，外表柔弱，卻法力高強` |

Raw bytes (saved/candidate pairs) are reproduced verbatim in Appendix A; the three
candidate texts are byte-identical to `monsterdata` `lock1` with the 33-byte prefix, which
is the cross-table identity `petgraph.desc[0] == prefix + monsterdata.lock1[2:]` verified for
**134/134** records under the candidate bounds (130/134 under saved bounds — the four
exceptions are exactly the three flagged records plus record 2490 whose *monster* side is
flagged). Candidate bounds: `[6574,13203,19731,26330]`.
Status: **confirmed_extraction_bug** for all three.

### 3.6 Item 5 — 3526 `lock1`/`lock2`/`lock3` of records 2490, 2650, 2740

| record/field | payload span | delta run | delta | recovered text | twin |
|---|---|---|---|---|---|
| 2490 `lock1` | (35894,35980), 86 B | bytes 60…85 (26 B) | 0x46 = 118^48 | `  比霜月狼更大更酷的狼，前肢有雲紋裝飾，下身隱藏在煙霧中，長長的獠牙使它看起來十分凶悍` | `petgraph DATA[2490]['desc'][0][...]` (byte-identical after the 33-byte prefix, incl. the two leading spaces) |
| 2650 `lock2` | (53873,54089), 216 B | bytes 60…215 (156 B) | 0x79 = 48^73 | `#c3300CC生活習性：#n  #r  在「初雲峽谷和初雲平原」來回遊蕩的燈神最近交到了一個好朋友，除卻脾氣過於火爆之外炎魔同他相處的相當不錯，不過得當心他珍貴的寶石項鏈及手環，一不小心興奮過頭的炎魔所爆發出的高溫極有可能融化它們` | none in archive (searched `寶石項鏈`, `融化它們`, `最近交到了一個好朋友` → 0 hits) |
| 2740 `lock3` | (71861,71945), 84 B | bytes 47…83 (37 B) | 0xE2 = 73^171 | `#c3300CC必然攜帶技能：#n  無#r#c3300CC可能攜帶技能：#n  靈通術、智慧、神跡、魔法反擊` | canonical skill-block template, byte-identical prefix/separator bytes to the 100+ clean `lock3` values in the same table |

* 2490: recovery pinned by the petgraph twin (and `monC[2490].lock1[2:] == pgC[2490].desc0[33:]`).
  Status **confirmed_extraction_bug**.
* 2650: strict-CP950 valid texts exist for boundary shifts 53929–53934 (six possibilities).
  The minimal-damage choice 53933 is the first byte of the damaged run and restores the text
  that names this row's own monster `燈神` and its neighbour `炎魔` (record 2660, whose own
  `lock2` text is the sibling narrative). No byte twin exists, therefore status **candidate**;
  do not install. See the counter-example in §4.
* 2740: shift 71908 restores the exact template bytes used by every other clean `lock3`
  (e.g. record 2010's `#c3300CC必然攜帶技能：#n  無#r#c3300CC可能攜帶技能：#n  ` prefix is
  byte-identical) and the tail tokens (`靈通術`, `智慧`, `神跡`, `魔法反擊`) are all known
  skill **names** elsewhere in `petdata.maySkillLst` (occurrence counts 3/10/10/2 resp.).
  Status **confirmed_extraction_bug** (name-level only; Agent D owns the name→id mapping).

## 4. Required counter-example: decodable but wrong value

Strict CP950 success alone is **not** sufficient evidence, and the probes contain the
counter-example required by the assignment:

* 3526 boundary 2 (`lock2` of 2650): shifts 53929–53934 all produce strictly CP950-decodable
  text. 53933 yields `…來回遊蕩的燈神…`, but 53934 yields `…來回遊蕩的鷺神…` — fully
  decodable, wrong character. The recovery therefore relies on the damaged-run start /
  narrative cross-reference, not on "the text reads".
* 2027 boundary 2 (`address` of 2600): shifts 16259–16264 all decode; 16262/16263 yield
  `…兔神殿遺李咬兔坦卡門陵墓` / `…遺址咬兔坦卡門陵墓` — valid CP950, wrong bytes. Only
  16264 reproduces the byte-identical twin from `monsterdata`.
* 2954: the solver-repaired value 2130 is fully "legal" (valid bytecode, valid integer) and
  nevertheless is the value under suspicion; legality is not proof of correctness.

Consequently every declared recovery in this report is anchored on a byte-level twin,
byte-identical template, or constant key-delta run — never on readability.

## 5. Mandatory table-relation checks

1. **135 pet-detail rows vs 137 mxpetdata rows** — `petdata` id set is a strict subset of
   `mxpetdata`; the extras are ids **5106, 5107** (both 御靈少女 entries). `mxpetdata` is a
   flat `id → name bytes` map (not a per-record dict), names agree with `petdata` on all
   shared ids except the 2910 artifact (§3.3) and 4024 (§5.2). Status:
   **legitimate_table_difference**.
2. **id 4024 naming** — `petdata` says `仙獸雷吉斯`; `mxpetdata` and `monsterdata` both say
   `神獸雷吉斯`; the client-side predicate `IsShenShou()` in entry 2027 lists 4024 among the
   神獸 ids. The petguide name is the outlier. Status: **unresolved** (extraction of all three
   strings is clean; the difference is content). Names are **not** unified.
3. **aptitude coverage** — all 132 aptitude records map into `petdata`; detail ids **3010**
   (未定, carry_grade 0), **4021** (年獸), **4022** (爆竹) have no aptitude record. Status:
   **legitimate_table_difference** (placeholder records); missing aptitude is **not**
   zero-filled.
4. **`mxpetdata` readers / aliases** — literal scan of all 5,002 entries: `mxpetdata` occurs
   only in entry 1115 itself; alias spellings `mxPet`, `MXPet`, `mx_pet`, `MXpetdata`,
   `MXPetData` occur nowhere; `mxpet` occurs only in 1115. Repo-wide text search finds
   `mxpet` only in docs/artefacts. By contrast `petdata` is referenced by 93 entries,
   `petaptitudedata` by 8 `{1249,2300,2363,2655,2954,3813,4048,4920}`, `petgraphdata` by
   `{1761,4920}`, `monsterdata` by 15. Status: **reader_limitation** — a literal scan cannot
   prove absence (dynamic/attribute access, renamed imports, native-side use). The two pet
   tables must **not** be merged.

Additional relations established (useful for joins):

* `petgraphdata` ids (134) are a subset of `monsterdata` ids (143). Shared ids:
  pet∩pg = 120, pet∩monster = 129, pet∩pg∩monster = 120.
* `monsterdata` has 14 ids not in `petdata` (3101–3102, 4041–4046, 4103, 4108, 4111, 4112,
  4114, 4115 — all of which are also in `petgraphdata`) and 9 ids not in `petgraphdata`
  (2990, 4025, 4027, 4028, 5100, 5101, 5103, 5104, 5105 — all of which are in `petdata`).
* `petgraphdata.desc[0] == prefix + monsterdata.lock1[2:]` holds for 130/134 records under
  saved bounds and 134/134 under the candidate bounds (§3.5).
* `petdata.address` vs `monsterdata.address`: after the 2600 fix 13 of 129 shared records
  differ in content (both sides valid CP950, e.g. 2081, 2160, 2190, 2200, 2640, 2650, 2660,
  2670, 2680, 2690, 2700, 2720, 2940) — table-content differences, not extraction damage.
* `petdata.maySkillLst` vs `monsterdata.lock3` possible-skill list: exactly equal (same order)
  for 69/125 shared records; the rest are order/token differences to be resolved by Agent D.
  Note `petdata` also has an optional `mustSkillName` field: present in 26/135 records.

## 6. CSV recommendations

Proposed review-CSV columns (one row per field):

`entry_index, table, record_key, field_path, value_text_utf8, value_hex,
payload_offset_span, bounds_used, status, candidate_text, candidate_bounds, twin_source, notes`

**May enter the review CSV as-is** (extraction and encoding clean; no boundary dependence
found): all other fields of the five tables, including the `mustSkillName`/`maySkillLst`
skill-name fields of all records except those listed below, `SHAPE2ICON` (2027), and all
`petdata`/`petgraphdata`/`monsterdata` fields outside the flagged spans.

**Must be quarantined** (export only with status + candidate annotation, never as trusted):

| entry | record | field | reason | candidate |
|---|---|---|---|---|
| 2027 | 2600 | `address` | saved bytes invalid CP950; twin-proven boundary damage | `出現地點：#r兔神殿遺址#r兔坦卡門陵墓` |
| 2027 | 4011 | `maySkillLst[3]` | invalid bytes; twin-proven | `終級強力` |
| 1115 | 2910 | row value | saved bounds unusable raw; int 2280 schema violation | `混沌騎士` |
| 2954 | 2800 | `法力資質` | off-by-one boundary suspicion; max<base unique inversion | `1700` (not applied) |
| 1761 | 2190 / 2600 / 4015 | `desc[0]` | invalid bytes; twin-proven | see §3.5 |
| 3526 | 2490 | `lock1` | invalid bytes; twin-proven | see §3.6 |
| 3526 | 2650 | `lock2` | invalid bytes; recovery ambiguous within 53929–53934 | minimal-damage 53933 text |
| 3526 | 2740 | `lock3` | invalid bytes; template-proven | see §3.6 |

Also excluded from text export (not table fields, but they appear in the payload walk and
would trip naive text pipelines): module-level binary string constants with control bytes —
e.g. 2954 span (16526,19436) 2,910 B, 1115 span (3529,3803) 274 B, 2027 span (24630,26874),
3526 span (85592,89602), 1761 span (30043,32591). They are not part of the DATA tables and
should be classified as binary, not text.

## 7. How to join the tables reliably

* Join key = the marshal dict key (`record_key`), i.e. the pet/shape id. It is present in all
  four pet-side tables; `mxpetdata` is `id → name`.
* Coverage: `aptitude ⊂ petdata ⊂ mxpetdata` (for ids), `petgraphdata ⊂ monsterdata`.
  Left-join `petdata → aptitude` leaves 3010/4021/4022 without aptitude (keep NULL, do not
  zero-fill). Left-join `petdata → monsterdata` leaves 2750/2760/3010/4016/4021/4022 without a
  monster row.
* Never join on **name text** (4024, 4110/4113, 5104/5105 suffix variants, and the 2910
  artifact show names are not a reliable key). Use the numeric key.
* Address-like fields: `petdata.address` and `monsterdata.address` share the
  `出現地點：#r` prefix style; `petgraphdata` spells the field `adress` (sic) and stores the
  raw location list only. `monsterdata.lock1` and `petgraphdata.desc[0]` are the same text
  with a standard 33-byte prefix on the graph side (see §5); join on id, then compare bytes.
* Skill-name linkage for Agent D: `petdata.maySkillLst` / `mustSkillName` (names) and
  `monsterdata.lock3` possible-skill list. Provide names + pet identifier only; no skill id
  may be generated by this report.

## 8. Tests executed / regression baselines (not data certification)

* `python3 -m unittest discover -s server/tests/architecture -v` → **31 tests OK**
  (`test_contracts`, `test_csv_readiness`, `test_inventory`, `test_client_data_review`).
* `python3 -m unittest discover -s server/tests/architecture -p "test_client_data_review.py" -v`
  → 8 tests OK (includes `test_candidates_stay_unapproved_and_local`,
  `test_source_files_not_changed`).
* Probe failures recorded: the first `robust.py` run and the written-but-unrun `diff2954.py`
  raised `SyntaxError` (non-ASCII inside bytes literals) — fixed/superseded by building byte
  keys with `.encode('cp950')` (the 2954 alignment diff was then reproduced inline); `1115`
  saved-bounds raw decode raises `IndexError`; `solve_py25_co_span` masks the in-co_code
  boundary question (documented in §3.3/§3.4).

## 9. Residual uncertainty

* 2954/2800 remains a **candidate**; no independent decode of entry 2954 exists in the repo
  (batch-decode artefacts: all runs `status=fail`), and the solver output is not usable as
  evidence because it normalises the disputed byte for both bound settings.
* 3526/2650 `lock2` remains a **candidate**; five other boundary shifts also produce
  CP950-valid text (see §4), and no archive twin exists.
* 1115 and 2954 need Agent A's ratification of any key-database change; nothing was changed
  in this round. The two pet tables must not be merged; the 4024 name difference is left
  unresolved per instructions.
* All texts are reported in Traditional Chinese exactly as decoded; no Traditional↔Simplified
  conversion was performed this round.

## Appendix A — raw bytes per flagged field (saved vs candidate)

`2027 / 2600 / address` · payload span (16241,16277) · 36 B

```
saved a558b27ba661c249a1472372a8dfafabb7b5bff2a77d23fa205721d22dec22713b26315b
cand  a558b27ba661c249a1472372a8dfafabb7b5bff2a77d2372a8dfa95aa564aaf9b3aeb9d3
```

`2027 / 4011 / maySkillLst[3]` · (21747,21755) · 8 B

```
saved b2d7afc5d902cc27
cand  b2d7afc5b16aa44f
```

`1761 / 2190 / desc[0]` · (13149,13324) · 175 B

```
saved a5bcaabeaabaa9c7aaaba141bcc8aec9b54caa6bc0f2aabea5f4a6f3ab48aea72cacefb5dbf15aa5d2aeb3b5dba46aa44da94dacdeb52fd5c5d7a0db13de3ebf26db28bfc6caa4dac4cea5ce2dd48bd5c5c6b0bbb4de3ed7bccbbece99caa4d9ccdb3fdbaed9a4db09db22d09fc1a9d9ccd92fc6b0bbb4db3fc3b4c39bdaaada3dd587d5c5db15db85de27de27c1a5c4decc10d330dad9d2b3d09fd820dbb6bdc1d5c5d2d4d211c3afc8b8dbd8db3f
cand  a5bcaabeaabaa9c7aaaba141bcc8aec9b54caa6bc0f2aabea5f4a6f3ab48aea72cacefb5dbf15aa5d2aeb3b5dba46aa44da94dacdeb550aabaa8dfa46ca141c059a457c0b9b5dba5bbb1dab152abf4aabab9cfc4cba141a8c3b4c1b1e6b5dba6b3a440a4d1a6dba476a45dafe0bed6a6b3a650b9cfc4cba440bccbbce4a5d5a542aaf8aabaa46aa4faa158a158bedabba1b36fac4fa5a6adccafe0a75fa4c9c2beaabaadabad6ebcd0b7c7a4a7a440
```

`1761 / 2600 / desc[0]` · (19693,19838) · 145 B

```
saved a5bcaabeaabaa9c7aaaba141bcc8aec9b54caa6bc0f2aabea5f4a6f3ab48aea72ca460c646a4f61dd11fe90572116a1f6217f31d7718f81f441c1f156409e6116a1df97bf01de41d1a000a1dd97fff1e4a000a1df91ccc1dd30ff1181e0ad61d1a15f61e631303064018cf1c1f021818cc1de40ae515f61e631d6a1e1e1dff18f110770ae51e63016a0d570d57137718cf
cand  a5bcaabeaabaa9c7aaaba141bcc8aec9b54caa6bc0f2aabea5f4a6f3ab48aea72ca460c646a44fa468a650bccba8d3a6dbae4aa4cea141a6fda5a6acddb05fa8d3a440c249a45da4a3b9b3a460c646a7f3b9b3a440a575a46ab648a1a7b36fa4a3ac4fa7daaababff9a176a5a6bba1a175a45db35cac4fa7daa4d3a7a7a446a148a9ceb35ca7dab8d3b4eeb4eeaacea176
```

`1761 / 4015 / desc[0]` · (26267,26338) · 71 B

```
saved a5bcaabeaabaa9c7aaaba141bcc8aec9b54caa6bc0f2aabea5f4a6f3ab48aea72ca552baa1c646aef0aabab1f6aae1b3c0a141a57eaaedac58ae7aa141ab6f45844ba05f455e85
cand  a5bcaabeaabaa9c7aaaba141bcc8aec9b54caa6bc0f2aabea5f4a6f3ab48aea72ca552baa1c646aef0aabab1f6aae1b3c0a141a57eaaedac58ae7aa141ab6faa6ba44fb0aab16a
```

`3526 / 2490 / lock1` · (35894,35980) · 86 B

```
saved 2020a4f1c1f7a4ebaf54a7f3a46aa7f3bbc5aabaaf54a141ab65aacfa6b3b6b3afbeb8cbb9a2a141a455a8adc1f4c2c3a662b7cfc3faa4a4a141aaf8ecbeecfca03fe2bcee89e3e0ea9bf619ee95e217e286e2f9e8ed
cand  2020a4f1c1f7a4ebaf54a7f3a46aa7f3bbc5aabaaf54a141ab65aacfa6b3b6b3afbeb8cbb9a2a141a455a8adc1f4c2c3a662b7cfc3faa4a4a141aaf8aaf8aabae679a4faa8cfa5a6acddb05fa8d3a451a4c0a4bfaeab
```

`3526 / 2650 / lock2` · (53873,54089) · 216 B

```
saved 2363333330304343a5cdaca1b2dfa9caa147236e202023722020a662a175aaecb6b3ae6ca8a6a94daaecb6b3a5adadeca176a8d3a65eb943bfbaaabac636d6d2cab5d388dc9fd195dd3fdd39d4aadf17d33bddb4d838c9dad216ccb3d789c035d08add8cba03dddedc07d3dbbc24df29dc35d5a2ca3bd3c3d5a2ce94dddac680d838dddac035c816ce94dda6dc35d5bacf28d3c3bd26dca2cfccba95ddb7dd9bb98dd838dd39dddadd09dda6c6cac7bdc035b920d3c3d3dbbc24d0abba03cc16dc21d3c3c9d3cebccedcdfcadc10d699c6bdddbfdcdfd4b5
cand  2363333330304343a5cdaca1b2dfa9caa147236e202023722020a662a175aaecb6b3ae6ca8a6a94daaecb6b3a5adadeca176a8d3a65eb943bfbaaababf4fafabb3ccaaf1a5e6a8eca446a440add3a66eaa42a4cda141b0a3ab6fb5caaef0b94ca9f3a4f5c37aa4a7a57eaaa2c55da650a54cacdbb342aabaacdbb7eda4a3bff9a141a4a3b94cb16fb7eda4dfa54cacc3b651aabac45fa5dbb6b5c3eca4cea4e2c0f4a141a440a4a3a470a4dfbfb3bec4b94cc059aabaaaa2c55da9d2c37ab56fa558aabab0aab7c5b7a5a6b3a569afe0bfc4a4c6a5a6adcc
```

`3526 / 2740 / lock3` · (71861,71945) · 84 B

```
saved 2363333330304343a5b2b54dc4e2b161a7deafe0a147236e2020b54c23722363333330304343a569afe0c4e2b161a73c4d0243a5c18cc2c224a4519351ac43a0565e5e9843a04d495a1343a027bf4889462d2259
cand  2363333330304343a5b2b54dc4e2b161a7deafe0a147236e2020b54c23722363333330304343a569afe0c4e2b161a7deafe0a147236e2020c646b371b34ea142b4bcbc7aa142afabb8f1a142c55daa6ba4cfc0bb
```

`1115 / DATA[2910]` · raw payload [815,845) = `7a7f4af5d47a20f5d57a7f4af543f3a97c42f3f6c37c41f3a97c40f3f6c3`

```
saved dec 0005308fae005a8faf008cb906b0005a8fb10005308fb2005a8fb3000530   (pattern break at 825–827; DATA[2910] = int 2280)
cand  dec 0005308fae005a8faf0005308fb0005a8fb10005308fb2005a8fb3000530   (periodic; DATA[2910] = 混沌騎士)
```

`2954 / DATA[2800]` · raw payload [7970,7990) = `d7d2e76cd7d7e758e0adf722a9ada89d2295adf7`

```
saved dec 000530bb0000308f4d005a8f040005308f38005a   (payload 7978 → 0x4d, const idx 77 → 2130)
cand  dec 000530bb0000308f37005a8f040005308f38005a   (payload 7978 → 0x37, const idx 55 → 1700)
transpiled py2.5 co_code [7952:7968] saved 000004644d00026404003c0464380002 / cand 000004643700026404003c0464380002
```
