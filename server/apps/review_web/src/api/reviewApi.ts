/**
 * Domain layer: composes Agent H's generic dataset endpoints into the models the
 * pages need (pet detail with aptitude status, skill detail with overwrite
 * evidence, anomaly board, per-source NPC pages).
 *
 * Rules:
 *   - every field is read through a nullable accessor; a missing field is
 *     reported as "not provided" by the UI, never defaulted to `0` / `[]`;
 *   - related queries that must be complete (candidate skills, candidate IDs,
 *     name matches, overwrite evidence) fetch **all** pages, not just the first;
 *   - sources stay separate: no endpoint here merges 2601 and 2804 records.
 */
import {
  ApiError,
  fetchAmbiguousSkills,
  fetchBatch,
  fetchDatasetMeta,
  fetchDatasets,
  fetchHealth,
  fetchMissingAptitudes,
  fetchOverwrites,
  fetchQuarantine,
  fetchRecord,
  fetchRecords,
  type RecordsQuery,
  type RequestOptions,
} from './client'
import {
  clampLimit,
  DATASET,
  MAX_FETCH_ALL_RECORDS,
  MAX_LIMIT,
  pageToOffset,
  type NpcSourceKey,
} from './contract'
import type {
  ApiRecord,
  BatchPayload,
  DatasetListPayload,
  DatasetMeta,
  Envelope,
  HealthPayload,
  OverwriteEvidenceEntry,
  QuarantineEntry,
  TableSummary,
  ValidationSummary,
} from './parsers'
import { describeValue } from './schema'

export type {
  ApiRecord,
  ApiError,
  BatchPayload,
  DatasetListPayload,
  DatasetMeta,
  Envelope,
  HealthPayload,
  OverwriteEvidenceEntry,
  QuarantineEntry,
  TableSummary,
  ValidationSummary,
}

/* ------------------------------------------------------------ accessors */

export function asText(record: ApiRecord, key: string): string | null {
  const value = record[key]
  if (value === null || value === undefined) return null
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  return describeValue(value)
}

export function asNumber(record: ApiRecord, key: string): number | null {
  const value = record[key]
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string' && value.trim() !== '' && Number.isFinite(Number(value))) {
    return Number(value)
  }
  return null
}

export function asBool(record: ApiRecord, key: string): boolean | null {
  const value = record[key]
  if (typeof value === 'boolean') return value
  if (typeof value === 'string') {
    const text = value.trim().toLowerCase()
    if (text === 'true') return true
    if (text === 'false') return false
  }
  return null
}

export function recordKey(record: ApiRecord): string {
  return asText(record, '_pk') ?? ''
}

/* ------------------------------------------------------------ utilities */

export function offsetForPage(page: number, pageSize: number): number {
  return pageToOffset(page, pageSize)
}

export interface PageInfo {
  page: number
  pageSize: number
  total: number
  pageCount: number
}

export function pageInfo(envelope: Envelope, page: number, pageSize: number): PageInfo {
  const safeSize = clampLimit(pageSize)
  return {
    page,
    pageSize: safeSize,
    total: envelope.total,
    pageCount: Math.max(1, Math.ceil(envelope.total / safeSize)),
  }
}

export function queryDatasetRecords(
  datasetId: string,
  query: RecordsQuery,
  options?: RequestOptions,
): Promise<Envelope> {
  return fetchRecords(datasetId, query, options)
}

/**
 * Fetches every page of a filtered query.
 *
 * Used where a first page is provably not the whole answer: pet candidate
 * skills, name matches and overwrite evidence. Rejects early empty pages, total
 * drift and repeated record identities instead of silently truncating. Exceeding the safety cap
 * raises an ApiError instead of returning a partial list that would look like
 * "the pet has fewer skills".
 */
export async function fetchAllRecords(
  datasetId: string,
  query: Omit<RecordsQuery, 'offset' | 'limit'>,
  options: RequestOptions = {},
): Promise<{ records: ApiRecord[]; total: number; pages: number; truncated: boolean }> {
  const limit = MAX_LIMIT
  let offset = 0
  let total: number | null = null
  const records: ApiRecord[] = []
  const seen = new Set<string>()
  let pages = 0

  const incomplete = (reason: string): never => {
    throw new ApiError({
      kind: 'schema',
      url: `${datasetId}(offset=${offset})`,
      code: 'INCOMPLETE_RESULT_SET',
      message: `关联查询未能取得一致的完整结果：${reason}。不会将部分记录作为完整列表显示。`,
    })
  }

  while (true) {
    const envelope = await fetchRecords(datasetId, { ...query, offset, limit }, options)
    pages += 1
    if (total === null) total = envelope.total
    if (envelope.total !== total) incomplete('分页过程中 total 发生变化')
    if (envelope.offset !== offset) incomplete('返回的 offset 与请求不一致')
    if (envelope.count !== envelope.records.length || envelope.count > envelope.limit) {
      incomplete('count、limit 与记录数量不一致')
    }
    if (total > MAX_FETCH_ALL_RECORDS) {
      throw new ApiError({
        kind: 'unknown',
        url: `${datasetId}(offset=${offset})`,
        code: 'RESULT_SET_TOO_LARGE',
        message: `关联查询结果超过 ${MAX_FETCH_ALL_RECORDS} 条，已停止以免返回不完整列表（total=${total}）。`,
      })
    }
    if (records.length + envelope.records.length > total) incomplete('记录数量超过 total')
    for (const record of envelope.records) {
      const key = record._pk
      if (typeof key !== 'string' || key.length === 0 || seen.has(key)) {
        incomplete('记录身份缺失或分页中出现重复 _pk')
      }
      seen.add(key as string)
    }
    records.push(...envelope.records)
    if (records.length === total) break
    if (envelope.records.length === 0) incomplete('尚未达到 total 就提前返回空页')
    offset = records.length
  }

  return { records, total, pages, truncated: false }
}

/** Counts records matching a filter without downloading them. */
export async function countRecords(
  datasetId: string,
  filters: Record<string, string | number>,
  options: RequestOptions = {},
): Promise<number> {
  const envelope = await fetchRecords(datasetId, { offset: 0, limit: 1, filters }, options)
  return envelope.total
}

/* --------------------------------------------------------------- batch */

export function loadHealth(options?: RequestOptions): Promise<HealthPayload> {
  return fetchHealth(options)
}

export function loadBatch(options?: RequestOptions): Promise<BatchPayload> {
  return fetchBatch(options)
}

export function loadDatasets(options?: RequestOptions): Promise<DatasetListPayload> {
  return fetchDatasets(options)
}

export function loadDatasetMeta(datasetId: string, options?: RequestOptions): Promise<DatasetMeta> {
  return fetchDatasetMeta(datasetId, options)
}

/* --------------------------------------------------------------- items */

export interface ItemRow {
  client_shape_id: string | null
  name: string | null
  description_raw: string | null
  category_code_raw: string | null
  image_id: string | null
  image_mapping_explicit: boolean | null
  source_entry: string | null
  source_table: string | null
  review_status: string | null
  pk: string
}

export function toItemRow(record: ApiRecord): ItemRow {
  return {
    client_shape_id: asText(record, 'client_shape_id'),
    name: asText(record, 'name'),
    description_raw: asText(record, 'description_raw'),
    category_code_raw: asText(record, 'category_code_raw'),
    image_id: asText(record, 'image_id'),
    image_mapping_explicit: asBool(record, 'image_mapping_explicit'),
    source_entry: asText(record, 'source_entry'),
    source_table: asText(record, 'source_table'),
    review_status: asText(record, 'review_status'),
    pk: recordKey(record),
  }
}

export interface ItemQuery {
  page: number
  pageSize: number
  search?: string
}

export async function listItems(query: ItemQuery, options?: RequestOptions): Promise<Envelope> {
  const pageSize = clampLimit(query.pageSize)
  return fetchRecords(
    DATASET.items,
    { offset: offsetForPage(query.page, pageSize), limit: pageSize, q: query.search },
    options,
  )
}

export async function getItem(clientShapeId: string, options?: RequestOptions): Promise<ItemRow> {
  return toItemRow(await fetchRecord(DATASET.items, clientShapeId, options))
}

/* ---------------------------------------------------------------- pets */

export interface PetRow {
  client_shape_id: string | null
  name: string | null
  liupai_raw: string | null
  attack_type_raw: string | null
  carry_grade: string | null
  maxskillnum_raw: string | null
  address_raw: string | null
  source_entry: string | null
  source_table: string | null
  review_status: string | null
  pk: string
}

export function toPetRow(record: ApiRecord): PetRow {
  return {
    client_shape_id: asText(record, 'client_shape_id'),
    name: asText(record, 'name'),
    liupai_raw: asText(record, 'liupai_raw'),
    attack_type_raw: asText(record, 'attack_type_raw'),
    carry_grade: asText(record, 'carry_grade'),
    maxskillnum_raw: asText(record, 'maxskillnum_raw'),
    address_raw: asText(record, 'address_raw'),
    source_entry: asText(record, 'source_entry'),
    source_table: asText(record, 'source_table'),
    review_status: asText(record, 'review_status'),
    pk: recordKey(record),
  }
}

export type AptitudeStatus = 'present' | 'missing_in_source_table' | 'quarantined' | 'unknown'

export interface AptitudeStatusInfo {
  status: AptitudeStatus
  reason: string | null
  evidence_id: string | null
}

export interface SkillNameMatch {
  skill_name_raw: string | null
  skill_id: string | null
  match_count: number | null
  ambiguous: boolean | null
}

export interface CandidateSkill {
  sequence: number | null
  skill_name_raw: string | null
  matches: SkillNameMatch[]
}

export interface RequiredSkill {
  skill_name_raw: string | null
  matches: SkillNameMatch[]
}

export interface AptitudeField {
  label: string
  value: string | null
}

export interface PetDetail {
  pet: PetRow
  aptitude: { fields: AptitudeField[]; record: ApiRecord } | null
  aptitude_status: AptitudeStatusInfo
  required_skills: RequiredSkill[]
  candidate_skills: CandidateSkill[]
  /**
   * True when the candidate/required/name-match queries were capped by
   * MAX_FETCH_ALL_RECORDS; the UI shows a warning instead of pretending the
   * list is complete.
   */
  truncated: boolean
}

export interface PetQuery {
  page: number
  pageSize: number
  search?: string
}

export async function listPets(query: PetQuery, options?: RequestOptions): Promise<Envelope> {
  const pageSize = clampLimit(query.pageSize)
  return fetchRecords(
    DATASET.pets,
    { offset: offsetForPage(query.page, pageSize), limit: pageSize, q: query.search },
    options,
  )
}

export function toSkillNameMatch(record: ApiRecord): SkillNameMatch {
  return {
    skill_name_raw: asText(record, 'skill_name_raw'),
    skill_id: asText(record, 'skill_id'),
    match_count: asNumber(record, 'match_count'),
    ambiguous: asBool(record, 'ambiguous'),
  }
}

export function toQuarantineEvidenceId(entry: QuarantineEntry): string {
  return `${entry.entry_index}:${entry.record_key}`
}

/** Pet ids whose aptitude row is quarantined, by source entry 2954. */
export async function loadQuarantinedAptitudeIds(options?: RequestOptions): Promise<Set<string>> {
  const { records } = await fetchQuarantine({ entryIndex: 2954, limit: 500 }, options)
  const ids = new Set<string>()
  for (const entry of records) ids.add(String(entry.record_key))
  return ids
}

export interface MissingAptitudeRow {
  client_shape_id: string | null
  pet_name: string | null
  reason: string | null
  source_entry: string | null
  source_table: string | null
  review_status: string | null
  pk: string
}

export function toMissingAptitudeRow(record: ApiRecord): MissingAptitudeRow {
  return {
    client_shape_id: asText(record, 'client_shape_id'),
    pet_name: asText(record, 'pet_name'),
    reason: asText(record, 'reason'),
    source_entry: asText(record, 'source_entry'),
    source_table: asText(record, 'source_table'),
    review_status: asText(record, 'review_status'),
    pk: recordKey(record),
  }
}

export function loadMissingAptitudes(options?: RequestOptions): Promise<MissingAptitudeRow[]> {
  return fetchMissingAptitudes(options).then((records) => records.map(toMissingAptitudeRow))
}

export interface AptitudeStatusIndex {
  /** Resolves a pet id exactly like `getAptitudeStatus`, from bulk requests. */
  statusOf: (petId: string) => AptitudeStatusInfo
  counts: { quarantined: number; missing: number; present: number }
}

/**
 * Builds the aptitude status of *every* pet with three bulk requests instead of
 * three requests per row (a 25-row page would otherwise fire 75 calls).
 *
 * Sources, in the same precedence as the single-pet resolver:
 *   - `/quarantine?entry_index=2954`      -> quarantined (values withheld)
 *   - `pet_aptitudes` rows (all pages)    -> present
 *   - `/missing-aptitudes`                -> missing_in_source_table
 *   - none of the above                   -> unknown
 *
 * Nothing is guessed: a pet is only "present" when a real aptitude row came
 * back, and an id absent from all three sources stays "unknown".
 */
export async function loadAptitudeStatusIndex(
  options: RequestOptions = {},
): Promise<AptitudeStatusIndex> {
  const [quarantine, missing, aptitudes] = await Promise.all([
    fetchQuarantine({ entryIndex: 2954, limit: MAX_LIMIT }, options),
    loadMissingAptitudes(options),
    fetchAllRecords(DATASET.petAptitudes, {}, options),
  ])

  const quarantined = new Map<string, AptitudeStatusInfo>()
  for (const entry of quarantine.records) {
    const id = String(entry.record_key)
    quarantined.set(id, {
      status: 'quarantined',
      reason: entry.reasons.join(', '),
      evidence_id: toQuarantineEvidenceId(entry),
    })
  }

  const missingById = new Map<string, AptitudeStatusInfo>()
  for (const row of missing) {
    const id = row.client_shape_id
    if (!id) continue
    missingById.set(id, {
      status: 'missing_in_source_table',
      reason: row.reason,
      evidence_id: null,
    })
  }

  const present = new Set<string>()
  for (const record of aptitudes.records) {
    const id = asText(record, 'client_shape_id')
    if (id) present.add(id)
  }

  return {
    statusOf: (petId: string) =>
      quarantined.get(petId) ??
      (present.has(petId)
        ? { status: 'present', reason: null, evidence_id: null }
        : missingById.get(petId) ?? { status: 'unknown', reason: null, evidence_id: null }),
    counts: { quarantined: quarantined.size, missing: missingById.size, present: present.size },
  }
}

/**
 * Resolves a pet's aptitude state without ever inventing a value:
 *   - a quarantine entry for (2954, petId)  -> 'quarantined' (values withheld)
 *   - an aptitude row                       -> 'present'
 *   - a pet_aptitude_missing row            -> 'missing_in_source_table'
 *   - otherwise                             -> 'unknown'
 */
export async function getAptitudeStatus(
  petId: string,
  options: RequestOptions = {},
): Promise<AptitudeStatusInfo> {
  const [quarantine, aptitude, missing] = await Promise.all([
    fetchQuarantine({ entryIndex: 2954, recordKey: petId, limit: 1 }, options),
    fetchRecords(DATASET.petAptitudes, { offset: 0, limit: 1, filters: { client_shape_id: petId } }, options),
    fetchRecords(
      DATASET.petAptitudeMissing,
      { offset: 0, limit: 1, filters: { client_shape_id: petId } },
      options,
    ),
  ])

  const quarantineEntry = quarantine.records[0]
  if (quarantineEntry) {
    return {
      status: 'quarantined',
      reason: quarantineEntry.reasons.join(', '),
      evidence_id: toQuarantineEvidenceId(quarantineEntry),
    }
  }
  if (aptitude.records.length > 0) {
    return { status: 'present', reason: null, evidence_id: null }
  }
  const missingRecord = missing.records[0]
  if (missingRecord) {
    return {
      status: 'missing_in_source_table',
      reason: asText(missingRecord, 'reason'),
      evidence_id: null,
    }
  }
  return { status: 'unknown', reason: null, evidence_id: null }
}

/** Aptitude columns keep their original source names, in record order. */
export function aptitudeFields(record: ApiRecord): AptitudeField[] {
  const ignored = new Set(['_pk', 'source_entry', 'source_table', 'review_status', 'client_shape_id'])
  return Object.entries(record)
    .filter(([key]) => !ignored.has(key))
    .map(([key, value]) => ({
      label: key,
      value: value === null || value === undefined ? null : String(value),
    }))
}

export async function getPetDetail(petId: string, options?: RequestOptions): Promise<PetDetail> {
  const queue: Promise<unknown>[] = []
  const track = <T>(promise: Promise<T>): Promise<T> => {
    queue.push(promise)
    return promise
  }

  const pet = await toPetRow(await fetchRecord(DATASET.pets, petId, options))

  // Candidates and name matches are read in full (all pages), never just page 1.
  const [candidatesResult, requiredResult, matchesResult, aptitudeResult, statusResult] = await Promise.all([
    track(fetchAllRecords(DATASET.petSkillCandidates, { filters: { client_shape_id: petId }, sortBy: 'sequence', order: 'asc' }, options)),
    track(fetchAllRecords(DATASET.petRequiredSkills, { filters: { client_shape_id: petId } }, options)),
    track(fetchAllRecords(DATASET.petSkillNameMatches, {}, options)),
    track(
      fetchRecords(DATASET.petAptitudes, { offset: 0, limit: 1, filters: { client_shape_id: petId } }, options),
    ),
    track(getAptitudeStatus(petId, options)),
  ])

  const matchesByName = new Map<string, SkillNameMatch[]>()
  for (const record of matchesResult.records) {
    const match = toSkillNameMatch(record)
    const name = match.skill_name_raw ?? ''
    const bucket = matchesByName.get(name)
    if (bucket) bucket.push(match)
    else matchesByName.set(name, [match])
  }

  const candidateSkills: CandidateSkill[] = candidatesResult.records
    .filter((record) => asText(record, 'client_shape_id') === petId)
    .map((record) => {
      const name = asText(record, 'skill_name_raw')
      return {
        sequence: asNumber(record, 'sequence'),
        skill_name_raw: name,
        matches: (name ? matchesByName.get(name) : undefined) ?? [],
      }
    })
    .sort((a, b) => (a.sequence ?? Number.MAX_SAFE_INTEGER) - (b.sequence ?? Number.MAX_SAFE_INTEGER))

  const requiredSkills: RequiredSkill[] = requiredResult.records
    .filter((record) => asText(record, 'client_shape_id') === petId)
    .map((record) => {
      const name = asText(record, 'skill_name_raw')
      return {
        skill_name_raw: name,
        matches: (name ? matchesByName.get(name) : undefined) ?? [],
      }
    })

  const aptitudeRecord = aptitudeResult.records[0] ?? null

  return {
    pet,
    aptitude: aptitudeRecord ? { fields: aptitudeFields(aptitudeRecord), record: aptitudeRecord } : null,
    aptitude_status: statusResult,
    required_skills: requiredSkills,
    candidate_skills: candidateSkills,
    truncated: false,
  }
}

/* -------------------------------------------------------------- skills */

export interface SkillRow {
  skill_id: string | null
  type_code_raw: string | null
  name: string | null
  description_raw: string | null
  fpneed_raw: string | null
  mpneed_raw: string | null
  hpneed_raw: string | null
  source_entry: string | null
  source_table: string | null
  review_status: string | null
  pk: string
}

export function toSkillRow(record: ApiRecord): SkillRow {
  return {
    skill_id: asText(record, 'skill_id'),
    type_code_raw: asText(record, 'type_code_raw'),
    name: asText(record, 'name'),
    description_raw: asText(record, 'description_raw'),
    fpneed_raw: asText(record, 'fpneed_raw'),
    mpneed_raw: asText(record, 'mpneed_raw'),
    hpneed_raw: asText(record, 'hpneed_raw'),
    source_entry: asText(record, 'source_entry'),
    source_table: asText(record, 'source_table'),
    review_status: asText(record, 'review_status'),
    pk: recordKey(record),
  }
}

export interface SkillQuery {
  page: number
  pageSize: number
  search?: string
}

export async function listSkills(query: SkillQuery, options?: RequestOptions): Promise<Envelope> {
  const pageSize = clampLimit(query.pageSize)
  return fetchRecords(
    DATASET.petSkills,
    { offset: offsetForPage(query.page, pageSize), limit: pageSize, q: query.search },
    options,
  )
}

export interface SkillOverwriteSummary {
  write_order: number
  code_offset: number
  skill_id: number
  entry_index: number
  table: string
  /** Names are derived from the evidence byte dicts, not from the CSV summary. */
  old_name: string | null
  new_name: string | null
  identical_values: boolean | null
  old_value: unknown
  new_value: unknown
  pk: string
}

/** Source key names inside overwrite evidence dicts, e.g. `name` from bytes 6e616d65. */
export const OVERWRITE_EVIDENCE_KEY_ASCII = { 0x74_79_70_65: 'type', 0x6e_61_6d_65: 'name', 0x64_65_73_63: 'desc' } as const

/** Decodes an ASCII JSON structure key from bytes; returns null when not printable ASCII. */
export function asciiKeyFromHex(hex: unknown): string | null {
  if (typeof hex !== 'string') return null
  const clean = hex.replace(/[^0-9a-fA-F]/g, '')
  if (clean.length === 0 || clean.length % 2 !== 0) return null
  let out = ''
  for (let i = 0; i < clean.length; i += 2) {
    const code = Number.parseInt(clean.slice(i, i + 2), 16)
    if (!Number.isFinite(code) || code < 0x20 || code > 0x7e) return null
    out += String.fromCharCode(code)
  }
  return out
}

interface BytesHex {
  bytes_hex: string
}

function isBytesHex(value: unknown): value is BytesHex {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof (value as { bytes_hex?: unknown }).bytes_hex === 'string'
  )
}

function isDictValue(value: unknown): value is { dict: Array<[unknown, unknown]> } {
  return typeof value === 'object' && value !== null && Array.isArray((value as { dict?: unknown }).dict)
}

/**
 * Reads the `name` entry out of an overwrite evidence dict.
 * Only a CP950-decodable byte run is turned into text; anything else returns
 * null so the UI shows the byte hex instead of a mojibake placeholder.
 */
export function evidenceName(value: unknown): string | null {
  if (!isDictValue(value)) return null
  for (const pair of value.dict) {
    if (!Array.isArray(pair) || pair.length !== 2) continue
    const [key, entryValue] = pair
    if (!isBytesHex(key) || !isBytesHex(entryValue)) continue
    if (asciiKeyFromHex(key.bytes_hex) !== 'name') continue
    return decodeCp950(entryValue.bytes_hex)
  }
  return null
}

/** Strict CP950 decode via TextDecoder; returns null if the byte run is invalid. */
export function decodeCp950(hex: string): string | null {
  const clean = hex.replace(/[^0-9a-fA-F]/g, '')
  if (clean.length === 0 || clean.length % 2 !== 0) return null
  const bytes = new Uint8Array(clean.length / 2)
  for (let i = 0; i < clean.length; i += 2) {
    bytes[i / 2] = Number.parseInt(clean.slice(i, i + 2), 16)
  }
  try {
    const decoder = new TextDecoder('big5', { fatal: true })
    return decoder.decode(bytes)
  } catch {
    return null
  }
}

export interface SkillDetail {
  skill: SkillRow
  overwrites: SkillOverwriteSummary[]
  name_matches: SkillNameMatch[]
}

export async function getSkillDetail(skillId: string, options?: RequestOptions): Promise<SkillDetail> {
  const [skill, overwrites, matches] = await Promise.all([
    fetchRecord(DATASET.petSkills, skillId, options).then(toSkillRow),
    fetchOverwrites({ key: Number(skillId), limit: 500 }, options),
    fetchAllRecords(DATASET.petSkillNameMatches, { filters: { skill_id: skillId } }, options),
  ])

  const summaries: SkillOverwriteSummary[] = overwrites.records.map((entry) => {
    const oldName = evidenceName(entry.old_value)
    const newName = evidenceName(entry.new_value)
    return {
      write_order: entry.order,
      code_offset: entry.code_offset,
      skill_id: entry.key,
      entry_index: entry.entry_index,
      table: entry.table,
      old_name: oldName,
      new_name: newName,
      identical_values: oldName !== null && newName !== null ? oldName === newName : null,
      old_value: entry.old_value,
      new_value: entry.new_value,
      pk: `${entry.order}`,
    }
  })

  return {
    skill,
    overwrites: summaries,
    name_matches: matches.records.map(toSkillNameMatch),
  }
}

/* ------------------------------------------------------------ anomalies */

export interface AmbiguousSkillGroup {
  skill_name_raw: string
  ids: string[]
  match_count: number | null
  ambiguous: boolean | null
}

export interface AnomalyBoard {
  batch: BatchPayload
  quarantine: QuarantineEntry[]
  quarantine_total: number
  missing_aptitudes: MissingAptitudeRow[]
  ambiguous_skill_names: AmbiguousSkillGroup[]
  skill_overwrites: OverwriteEvidenceEntry[]
  overwrites_total: number
  /** Set when an auxiliary endpoint had to be capped; the UI surfaces it. */
  notes: string[]
}

/** Groups every candidate ID of one name together: no ID can be dropped. */
export function groupAmbiguousSkills(records: ApiRecord[]): AmbiguousSkillGroup[] {
  const groups = new Map<string, AmbiguousSkillGroup>()
  for (const record of records) {
    const name = asText(record, 'skill_name_raw') ?? ''
    if (name === '') continue
    const ids = (asText(record, 'skill_id') ?? '')
      .split(/[,、\s]+/)
      .map((piece) => piece.trim())
      .filter((piece) => piece.length > 0)
    const existing = groups.get(name)
    if (existing) {
      for (const id of ids) if (!existing.ids.includes(id)) existing.ids.push(id)
      existing.match_count = Math.max(existing.match_count ?? 0, asNumber(record, 'match_count') ?? 0) || null
      existing.ambiguous = existing.ambiguous || asBool(record, 'ambiguous')
    } else {
      groups.set(name, {
        skill_name_raw: name,
        ids,
        match_count: asNumber(record, 'match_count'),
        ambiguous: asBool(record, 'ambiguous'),
      })
    }
  }
  return Array.from(groups.values())
}

export async function loadAnomalyBoard(options?: RequestOptions): Promise<AnomalyBoard> {
  const [batch, quarantine, missing, ambiguous, overwrites] = await Promise.all([
    fetchBatch(options),
    fetchQuarantine({ limit: 500 }, options),
    loadMissingAptitudes(options),
    fetchAmbiguousSkills(options),
    fetchOverwrites({ limit: 500 }, options),
  ])

  return {
    batch,
    quarantine: quarantine.records,
    quarantine_total: quarantine.total,
    missing_aptitudes: missing,
    ambiguous_skill_names: groupAmbiguousSkills(ambiguous),
    skill_overwrites: overwrites.records,
    overwrites_total: overwrites.total,
    notes: [],
  }
}

/* --------------------------------------------------------------- maps */

export interface MapDatasetView {
  key: string
  meta: DatasetMeta | null
  rows: ApiRecord[]
  total: number
  page: number
  pageSize: number
  /** True when the dataset is larger than the returned page. */
  hasMore: boolean
}

export interface DatasetPageResult {
  datasets: DatasetMeta[]
  /** Non-fatal problems (e.g. one dataset's rows failed) reported to the UI. */
  errors: Array<{ dataset: string; error: unknown }>
}

export async function loadMapDatasets(
  keys: readonly string[],
  options?: RequestOptions,
): Promise<DatasetPageResult> {
  const [list, ...metas] = await Promise.all([
    fetchDatasets(options),
    ...keys.map((key) => fetchDatasetMeta(key, options)),
  ])

  const byId = new Map(list.datasets.map((dataset) => [dataset.id, dataset]))
  const errors: Array<{ dataset: string; error: unknown }> = []
  const datasets: DatasetMeta[] = []

  metas.forEach((meta, index) => {
    const key = keys[index]
    if (meta) datasets.push(meta)
    else errors.push({ dataset: key, error: new ApiError({ kind: 'unknown', url: key, message: '元数据缺失' }) })
  })

  // Keep the list endpoint's order as a fallback for datasets without metadata.
  for (const key of keys) {
    if (!datasets.some((dataset) => dataset.id === key) && byId.has(key)) {
      datasets.push(byId.get(key) as DatasetMeta)
    }
  }

  return { datasets, errors }
}

export interface NpcSourcePage {
  source: NpcSourceKey
  envelope: Envelope
  meta: DatasetMeta | null
  zeroNpcIdTotal: number | null
  metaError: unknown | null
}

/**
 * One NPC source, queried on its own. 2601 and 2804 are never merged, and the
 * zero-npcid count comes from the backend's own filtered total.
 */
export async function loadNpcSourcePage(
  source: NpcSourceKey,
  query: { page: number; pageSize: number; search?: string; sceneId?: string },
  options?: RequestOptions,
): Promise<NpcSourcePage> {
  const pageSize = clampLimit(query.pageSize)
  const filters: Record<string, string | number> = {}
  if (query.sceneId && query.sceneId.trim() !== '') filters.scene_id = query.sceneId.trim()

  const [envelope, metaResult, zeroCount] = await Promise.all([
    fetchRecords(
      source,
      { offset: offsetForPage(query.page, pageSize), limit: pageSize, q: query.search, filters },
      options,
    ),
    fetchDatasetMeta(source, options).then(
      (meta) => ({ meta, error: null as unknown }),
      (error: unknown) => ({ meta: null as DatasetMeta | null, error }),
    ),
    countRecords(source, { npcid: 0 }, options).catch(() => null),
  ])

  return {
    source,
    envelope,
    meta: metaResult.meta,
    metaError: metaResult.error,
    zeroNpcIdTotal: zeroCount,
  }
}

export interface AgreementView {
  envelope: Envelope
  counts: Record<string, number>
  total: number
}

/**
 * Agreement rows plus per-category counts.
 *
 * Counts are computed over the *whole* dataset (every page), not just the
 * current page, so the numbers next to the filters are complete.
 */
export async function loadAgreement(
  query: { page: number; pageSize: number; sceneId?: string },
  options?: RequestOptions,
): Promise<AgreementView> {
  const pageSize = clampLimit(query.pageSize)
  const filters: Record<string, string | number> = {}
  if (query.sceneId && query.sceneId.trim() !== '') filters.scene_id = query.sceneId.trim()

  const [envelope, all] = await Promise.all([
    fetchRecords(
      DATASET.npcAgreement,
      { offset: offsetForPage(query.page, pageSize), limit: pageSize, filters },
      options,
    ),
    fetchAllRecords(DATASET.npcAgreement, {}, options),
  ])

  const counts: Record<string, number> = {}
  for (const record of all.records) {
    const key = asText(record, 'agreement') ?? 'unknown'
    counts[key] = (counts[key] ?? 0) + 1
  }

  return { envelope, counts, total: all.total }
}
