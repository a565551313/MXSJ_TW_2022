# Staging area — map/NPC candidate CSVs (review material only)

**Status of every file in this directory: `candidate`; NOT approved game
data.** The boundary placements used to produce them are static
reproductions of the handover findings (`../AGENT_E.md`), never confirmed by
the native client loader. Do not copy any file here into `server/game_data/`.

Generated deterministically by:

```
python3 server/tools/map_npc_reproduction.py \
    --csv-dir server/docs/csv_checks/staging
```

(`server/tests/architecture/test_agent_e_map_npc.py` regenerates all files
and fails if regeneration differs from what is committed here.)

## Files

| file | source (script.fls zero-based index, candidate bounds) | rows (excl. header) |
|------|---------------------------------------------------------|---------------------|
| `mapdata_scene_dictionary.csv` | 1301 `DATA`, `[1616,3239,4884,6553]` | 104 |
| `mapdata_parent_scene.csv` | 1301 `MAP_ASCRIPTION`, same | 6 |
| `sceneid2name_minimap_scenes.csv` | 400 `DATA`, saved bounds (already correct) | 57 |
| `npcname2realnamedata_alias_to_realname.csv` | 1799 `DATA`, `[528,1093,1652,2202]` | 55 |
| `npcposdata_records.csv` | 2601 `DATA`, `[18827,37735,56546,75376]` | 1335 |
| `minimapnpcpos_pos_records.csv` | 2804 `DATA_POS`, `[26695,53365,79989,106619]` | 1344 |
| `minimapnpcpos_wenzi_entries.csv` | 2804 `DATA_WENZI`, same | 287 |
| `npc_2601_vs_2804_agreement.csv` | join of the two record tables on `(scene_id, npcid)` | 677 |
| `provenance.json` | machine-readable provenance block | — |

## Reading rules (binding, same as AGENT_E.md §9.1/§9.2)

- Joins between the two NPC tables use only `(scene_id, npcid)`; never names,
  shapes or coordinates. The agreement CSV distinguishes
  `identical_sequence`, `identical_multiset_different_order` (9 pairs),
  `content_difference` (8 pairs), and single-sided pairs.
- `npcid = 0` records (632 in `npcposdata_records.csv`, 631 in
  `minimapnpcpos_pos_records.csv`) are kept; they cannot be joined by npcid
  and must not be dropped or assigned invented ids.
- `field5`, `field6`, `field9`, `field10`, `field12`, `field13` in the record
  CSVs are deliberately neutral raw columns: their meanings are not
  established. `field7_const255` is 255 in every staged record.
- `related_id_unresolved` in `sceneid2name_minimap_scenes.csv` is an
  id-like second column whose meaning is unresolved; it must not be used as
  a join key.
- Coordinate/size frames are not interchangeable: map width/height
  (1301), scene pair A/B (400), NPC `x,y`, and WENZI `jump_x/jump_y` are
  four separate frames with no verified conversion. Do not scale.
- No Simplified/Traditional conversion was or may be applied; text is the
  client's own cp950 content rendered as UTF-8.
- What is NOT staged here and must not be staged: 4897
  (`minimapnpcpos_test.py`, witness only), 1870 (`taiwan\npcpos_fix.py`,
  unresolved framing), 4532/4516 (out-of-scope family members), any
  mutation-applied view produced by `GetData` / `InitTestData` /
  `DelShenHeNpc` / `taiwan\npcpos_fix.Fix`, and any merged "complete
  map+NPC" table.
