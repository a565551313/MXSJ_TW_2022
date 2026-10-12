/**
 * DTO types for the review API (`/api/v1/review/...`).
 *
 * Field names deliberately mirror the batch_001 manifest column names so a DTO
 * field can be traced back to a CSV column without a second vocabulary.
 *
 * STATUS: these types describe the *expected* contract only. Agent H owns the
 * authoritative `server/docs/review_browser/API_CONTRACT.md`; until it lands in
 * this repository every type below is "pending integration" and must be
 * reconciled against that document. See `src/api/contract.ts`.
 */

export type ReviewStatus = string

/** Raw JSON value as stored in quarantine.jsonl / overwrite_evidence.jsonl. */
export type RawJson =
  | { bytes_hex: string }
  | { dict: Array<[RawJson, RawJson]> }
  | { tuple: RawJson[] }
  | { list: RawJson[] }
  | string
  | number
  | boolean
  | null
  | RawJson[]

export interface Page<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

/* ------------------------------------------------------------------ batch */

export interface BatchTableSummary {
  table_key: string
  /** Human label, when the API provides one. Never required. */
  label?: string | null
  csv_file?: string | null
  source_entry?: number | number[] | string | null
  source_table?: string | null
  source_records?: number | null
  review_csv_records?: number | null
  quarantined_records?: number | null
  missing_records?: number | null
  review_status?: ReviewStatus
}

export interface BatchOverview {
  batch_id: string
  status: ReviewStatus
  native_verified: boolean
  review_notice?: string | null
  generated_files?: number | null
  csv_files?: number | null
  tables: BatchTableSummary[]
  checks: Record<string, string>
  counters: Record<string, number>
  ambiguous_pet_skill_names?: Record<string, number[]>
  limitations?: string[]
  input_hashes?: Record<string, string>
}

/* ------------------------------------------------------------------ items */

export interface ItemRecord {
  client_shape_id: string
  name: string
  description_raw: string
  category_code_raw: string
  image_id: string
  image_mapping_explicit: string | boolean
  source_entry?: number | string
  source_table?: string
  review_status?: ReviewStatus
}

export interface ItemDetail {
  item: ItemRecord
}

/* ------------------------------------------------------------------- pets */

export interface PetRecord {
  client_shape_id: string
  name: string
  liupai_raw: string
  attack_type_raw: string
  carry_grade: string
  maxskillnum_raw: string
  address_raw: string
  source_entry?: number | string
  source_table?: string
  review_status?: ReviewStatus
}

/** Ten aptitude columns keep their original Traditional Chinese field names. */
export type PetAptitude = { client_shape_id: string } & Record<string, string | number | null | undefined>

export type AptitudeStatus = 'present' | 'missing_in_source_table' | 'quarantined' | 'unknown'

export interface AptitudeStatusInfo {
  status: AptitudeStatus
  /** e.g. `no_record_in_2954`, kept verbatim from pet_aptitude_missing.csv */
  reason?: string | null
  /** Anomaly identifier the UI can link to, e.g. `2954:2800`. */
  evidence_id?: string | null
}

export interface PetSkillNameMatch {
  skill_name_raw: string
  skill_id: string
  match_count: number
  ambiguous: boolean
}

export interface CandidateSkill {
  /** Source tuple order, starting at 0. Duplicates are preserved. */
  sequence: number
  skill_name_raw: string
  /** Every candidate ID for this exact name. Empty means unresolved. */
  matches: PetSkillNameMatch[]
}

export interface RequiredSkill {
  skill_name_raw: string
  matches: PetSkillNameMatch[]
}

export interface PetDetail {
  pet: PetRecord
  aptitude: PetAptitude | null
  aptitude_status: AptitudeStatusInfo
  required_skills: RequiredSkill[]
  candidate_skills: CandidateSkill[]
}

/** List row = pet main table plus its aptitude availability. */
export type PetListRow = PetRecord & {
  aptitude_status?: AptitudeStatusInfo | AptitudeStatus
}

/* ----------------------------------------------------------------- skills */

export interface SkillRecord {
  skill_id: string
  type_code_raw: string
  name: string
  description_raw: string
  fpneed_raw: string
  mpneed_raw: string
  hpneed_raw: string
  source_entry?: number | string
  source_table?: string
  review_status?: ReviewStatus
}

export interface SkillOverwriteRecord {
  write_order: string | number
  code_offset: string | number
  skill_id: string | number
  old_name: string
  new_name: string
  identical_values: string | boolean
  source_entry?: number | string
  source_table?: string
  review_status?: ReviewStatus
}

export interface SkillDetail {
  skill: SkillRecord
  /** Present only for the IDs whose write history is a duplicate-key overwrite. */
  overwrite?: SkillOverwriteRecord | null
  /** Pet candidate names that resolve to this skill ID (exact match only). */
  name_matches?: PetSkillNameMatch[]
}

/* -------------------------------------------------------------- maps/npcs */

export interface MapColumn {
  name: string
  type?: string
}

export interface MapDatasetSummary {
  dataset_key: string
  csv_file?: string | null
  source_entry?: number | number[] | string | null
  source_table?: string | null
  rows?: number | null
  primary_key?: string[]
  columns?: MapColumn[]
  notes?: string | null
  review_status?: ReviewStatus
}

export interface MapDatasetList {
  datasets: MapDatasetSummary[]
}

export type MapRow = Record<string, string | number | null | undefined>

export interface MapDatasetPage extends Page<MapRow> {
  dataset: MapDatasetSummary
}

export type NpcSourceKey = 'npcposdata_2601' | 'minimapnpcpos_2804'

/** 2601 records: key is (scene_id, record_index). */
export interface NpcRecord2601 {
  scene_id: string | number | null
  record_index: string | number | null
  display_name?: string | null
  secondary_name?: string | null
  npcid: string | number | null
  type?: string | number | null
  x?: string | number | null
  y?: string | number | null
  field5?: string | number | null
  field6?: string | number | null
  field7_const255?: string | number | null
  shape?: string | null
  field9?: string | number | null
  field10?: string | number | null
  real_name?: string | null
  field12?: string | number | null
  field13?: string | number | null
}

/** 2804 POS records: key is (scene_id, scene_display_name, record_index). */
export interface NpcRecord2804 extends NpcRecord2601 {
  scene_display_name: string | null
}

export type NpcRecord = NpcRecord2601 | NpcRecord2804

export interface NpcSourceInfo {
  source: NpcSourceKey
  source_entry: number | number[]
  source_table: string
  csv_file: string
  /** Composite record identity, never (scene_id, npcid). */
  primary_key: string[]
  total: number
  /** Rows whose npcid is 0 - never hidden, never renumbered. */
  zero_npcid_records: number | null
  review_status?: ReviewStatus
}

export interface NpcPage extends Page<NpcRecord> {
  source_info: NpcSourceInfo
}

export interface AgreementRow {
  scene_id: string | number
  npcid: string | number
  records_2601: string | number
  records_2804: string | number
  agreement: string
}

export interface AgreementPage extends Page<AgreementRow> {
  agreement_counts: Record<string, number>
}

/* -------------------------------------------------------------- anomalies */

export interface QuarantineRecord {
  anomaly_id: string
  entry_index: number | string
  table: string
  record_key: string | number
  reasons: string[]
  native_verified: boolean
  value_under_applied_profile: RawJson
}

export interface MissingAptitudeRecord {
  client_shape_id: string
  pet_name: string
  reason: string
  source_entry?: number | string
  source_table?: string
  review_status?: ReviewStatus
}

export interface AmbiguousSkillName {
  skill_name_raw: string
  skill_id: string | number
  match_count: number
  ambiguous: boolean
}

export interface AnomaliesPayload {
  batch_id: string
  status: ReviewStatus
  native_verified: boolean
  quarantine: QuarantineRecord[]
  missing_aptitudes: MissingAptitudeRecord[]
  ambiguous_skill_names: AmbiguousSkillName[]
  skill_overwrites: SkillOverwriteRecord[]
}
