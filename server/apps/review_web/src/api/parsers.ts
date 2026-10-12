/**
 * Validators for every Agent H response shape the UI consumes.
 *
 * Each parser walks the real payload with `Validator`, so a structural change on
 * the backend surfaces as a `ResponseSchemaError` with the offending JSON path
 * instead of an empty page. The returned values are newly built objects (no
 * `as SomeInterface` on an unvalidated body).
 */
import { PK_FIELD } from './contract'
import { Validator, type ApiRecord, type SchemaIssue } from './schema'

export type { ApiRecord, SchemaIssue }

export interface Envelope {
  dataset: string
  total: number
  offset: number
  limit: number
  count: number
  records: ApiRecord[]
}

export interface DatasetMeta {
  id: string
  filename: string
  rows: number
  primary_key: string[]
  notes: string
  source_entry: number | string | Array<number | string> | null
  source_table: string | null
  columns: Array<{ name: string; type: string }>
}

export interface DatasetListPayload {
  total: number
  datasets: DatasetMeta[]
}

export interface BatchPayload {
  batch: string
  native_loader_confirmed: boolean
  manifest_files_count: number
  csv_format: Record<string, string>
  tables_summary: Record<string, TableSummary>
  validation_summary: ValidationSummary
}

export interface TableSummary {
  source_records: number | null
  review_csv_records: number | null
  quarantined_records: number | null
}

export interface ValidationSummary {
  checks: Record<string, string>
  missing_aptitude_count: number | null
  pet_skill_names: number | null
  quarantined_record_count: number | null
  skill_write_count: number | null
  skill_unique_count: number | null
  skill_overwrite_count: number | null
  ambiguous_pet_skill_names: Record<string, number[]>
}

export interface HealthPayload {
  status: string
  batch: string
  loaded_files_count: number
  datasets_count: number
  total_records_count: number
}

export interface QuarantineEntry {
  entry_index: number
  table: string
  /** Text form of the backend key: it is used for identity comparisons. */
  record_key: string
  reasons: string[]
  native_verified: boolean
  value_under_applied_profile: unknown
}

export interface OverwriteEvidenceEntry {
  order: number
  code_offset: number
  entry_index: number
  table: string
  key: number
  old_value: unknown
  new_value: unknown
}

export interface CarriedIssues {
  issues: SchemaIssue[]
}

function parseRecord(validator: Validator, raw: unknown, path: string): ApiRecord | null {
  const record = validator.object(raw, path)
  if (!record) return null
  const pk = record[PK_FIELD]
  if (typeof pk !== 'string' || pk.length === 0) {
    validator.issue(`${path}.${PK_FIELD}`, 'non-empty string', pk)
    return null
  }
  return record
}

export function parseEnvelope(body: unknown, url: string): Envelope {
  const validator = new Validator(url)
  const root = validator.object(body, 'response')
  const envelope: Envelope = {
    dataset: root ? validator.requiredString(root.dataset, 'response.dataset') ?? '' : '',
    total: root ? validator.intLike(root.total, 'response.total') ?? 0 : 0,
    offset: root ? validator.intLike(root.offset, 'response.offset') ?? 0 : 0,
    limit: root ? validator.intLike(root.limit, 'response.limit') ?? 0 : 0,
    count: root ? validator.intLike(root.count, 'response.count') ?? 0 : 0,
    records: [],
  }
  if (root) {
    const records = validator.array(root.records, 'response.records')
    if (records) {
      const parsed: ApiRecord[] = []
      records.forEach((raw, index) => {
        const record = parseRecord(validator, raw, `response.records[${index}]`)
        if (record) parsed.push(record)
      })
      envelope.records = parsed
      if (parsed.length !== records.length) {
        validator.issue('response.records', '每条记录都有 _pk 且为对象', records.length - parsed.length + ' 条不合法')
      }
      if (validator.issues.length === 0 && parsed.length !== envelope.count) {
        validator.issue('response.count', `等于 records 长度 ${parsed.length}`, envelope.count)
      }
    }
  }
  validator.throwIfInvalid()
  return envelope
}

export function parseSingleRecord(body: unknown, url: string): ApiRecord {
  const validator = new Validator(url)
  const record = parseRecord(validator, body, 'response')
  validator.throwIfInvalid()
  return record as ApiRecord
}

function parseDatasetMeta(validator: Validator, raw: unknown, path: string): DatasetMeta | null {
  const root = validator.object(raw, path)
  if (!root) return null
  const columnsRaw = validator.array(root.columns, `${path}.columns`) ?? []
  const columns: Array<{ name: string; type: string }> = []
  columnsRaw.forEach((columnRaw, index) => {
    const column = validator.object(columnRaw, `${path}.columns[${index}]`)
    if (!column) return
    const name = validator.requiredString(column.name, `${path}.columns[${index}].name`)
    const type = validator.optionalString(column.type, `${path}.columns[${index}].type`)
    if (name) columns.push({ name, type: type ?? 'str' })
  })

  const primaryKeyRaw = validator.array(root.primary_key, `${path}.primary_key`) ?? []
  const primaryKey: string[] = []
  primaryKeyRaw.forEach((keyRaw, index) => {
    const key = validator.requiredString(keyRaw, `${path}.primary_key[${index}]`)
    if (key) primaryKey.push(key)
  })

  return {
    id: validator.requiredString(root.id, `${path}.id`) ?? '',
    filename: validator.requiredString(root.filename, `${path}.filename`) ?? '',
    rows: validator.intLike(root.rows, `${path}.rows`) ?? 0,
    primary_key: primaryKey,
    notes: validator.optionalString(root.notes, `${path}.notes`) ?? '',
    source_entry: (root.source_entry ?? null) as DatasetMeta['source_entry'],
    source_table: validator.optionalString(root.source_table, `${path}.source_table`),
    columns,
  }
}

export function parseDatasetList(body: unknown, url: string): DatasetListPayload {
  const validator = new Validator(url)
  const root = validator.object(body, 'response')
  let datasets: DatasetMeta[] = []
  if (root) {
    const list = validator.array(root.datasets, 'response.datasets') ?? []
    datasets = list
      .map((raw, index) => parseDatasetMeta(validator, raw, `response.datasets[${index}]`))
      .filter((entry): entry is DatasetMeta => entry !== null)
  }
  validator.throwIfInvalid()
  return { total: root ? validatorTolerantInt(root.total) ?? datasets.length : datasets.length, datasets }
}

/** `total` is informational here; datasets.length is the authoritative count. */
function validatorTolerantInt(value: unknown): number | null {
  if (typeof value === 'number' && Number.isInteger(value)) return value
  if (typeof value === 'string' && /^-?\d+$/.test(value.trim())) return Number(value.trim())
  return null
}

export function parseDatasetMetaResponse(body: unknown, url: string): DatasetMeta {
  const validator = new Validator(url)
  const meta = parseDatasetMeta(validator, body, 'response')
  validator.throwIfInvalid()
  return meta as DatasetMeta
}

export function parseTableSummary(validator: Validator, raw: unknown, path: string): TableSummary {
  const table = validator.object(raw, path)
  return {
    source_records: table ? validator.intLike(table.source_records, `${path}.source_records`) : null,
    review_csv_records: table ? validator.intLike(table.review_csv_records, `${path}.review_csv_records`) : null,
    quarantined_records: table
      ? validator.intLike(table.quarantined_records, `${path}.quarantined_records`)
      : null,
  }
}

export function parseBatch(body: unknown, url: string): BatchPayload {
  const validator = new Validator(url)
  const root = validator.object(body, 'response')
  const tablesSummary: Record<string, TableSummary> = {}
  const csvFormat: Record<string, string> = {}
  let validationSummary: ValidationSummary = {
    checks: {},
    missing_aptitude_count: null,
    pet_skill_names: null,
    quarantined_record_count: null,
    skill_write_count: null,
    skill_unique_count: null,
    skill_overwrite_count: null,
    ambiguous_pet_skill_names: {},
  }

  if (root) {
    const formatRaw = validator.object(root.csv_format, 'response.csv_format')
    if (formatRaw) {
      for (const [key, value] of Object.entries(formatRaw)) {
        csvFormat[key] = validator.stringOrNumberAsText(value, `response.csv_format.${key}`) ?? ''
      }
    }

    const tablesRaw = validator.object(root.tables_summary, 'response.tables_summary')
    if (tablesRaw) {
      for (const [entry, value] of Object.entries(tablesRaw)) {
        tablesSummary[entry] = parseTableSummary(validator, value, `response.tables_summary.${entry}`)
      }
    }

    const validationRaw = validator.object(root.validation_summary, 'response.validation_summary')
    if (validationRaw) {
      const checks: Record<string, string> = {}
      const checksRaw = validator.object(validationRaw.checks, 'response.validation_summary.checks')
      if (checksRaw) {
        for (const [key, value] of Object.entries(checksRaw)) {
          checks[key] = validator.stringOrNumberAsText(value, `response.validation_summary.checks.${key}`) ?? ''
        }
      }

      const ambiguous: Record<string, number[]> = {}
      const ambiguousRaw = validator.object(
        validationRaw.ambiguous_pet_skill_names,
        'response.validation_summary.ambiguous_pet_skill_names',
      )
      if (ambiguousRaw) {
        for (const [name, idsRaw] of Object.entries(ambiguousRaw)) {
          const path = `response.validation_summary.ambiguous_pet_skill_names.${name}`
          const ids = validator.array(idsRaw, path) ?? []
          ambiguous[name] = ids.map((id, index) => validator.intLike(id, `${path}[${index}]`) ?? Number.NaN)
        }
      }

      validationSummary = {
        checks,
        missing_aptitude_count: nullableMetric(validator, validationRaw, 'missing_aptitude_count'),
        pet_skill_names: nullableMetric(validator, validationRaw, 'pet_skill_names'),
        quarantined_record_count: nullableMetric(validator, validationRaw, 'quarantined_record_count'),
        skill_write_count: nullableMetric(validator, validationRaw, 'skill_write_count'),
        skill_unique_count: nullableMetric(validator, validationRaw, 'skill_unique_count'),
        skill_overwrite_count: nullableMetric(validator, validationRaw, 'skill_overwrite_count'),
        ambiguous_pet_skill_names: ambiguous,
      }
    }
  }

  // Everything is read before `throwIfInvalid()`: a body missing several keys
  // must report all of them, not just the first ones.
  const batch = root ? validator.requiredString(root.batch, 'response.batch') ?? '' : ''
  const nativeLoaderConfirmed = root
    ? validator.bool(root.native_loader_confirmed, 'response.native_loader_confirmed') ?? false
    : false
  const manifestFilesCount = root
    ? validator.intLike(root.manifest_files_count, 'response.manifest_files_count') ?? 0
    : 0

  validator.throwIfInvalid()
  return {
    batch,
    native_loader_confirmed: nativeLoaderConfirmed,
    manifest_files_count: manifestFilesCount,
    csv_format: csvFormat,
    tables_summary: tablesSummary,
    validation_summary: validationSummary,
  }
}

function nullableMetric(validator: Validator, source: Record<string, unknown>, key: string): number | null {
  const value = source[key]
  if (value === undefined || value === null) return null
  return validator.intLike(value, `response.validation_summary.${key}`)
}

export function parseHealth(body: unknown, url: string): HealthPayload {
  const validator = new Validator(url)
  const root = validator.object(body, 'response')
  const health: HealthPayload = {
    status: root ? validator.requiredString(root.status, 'response.status') ?? '' : '',
    batch: root ? validator.requiredString(root.batch, 'response.batch') ?? '' : '',
    loaded_files_count: root ? validator.intLike(root.loaded_files_count, 'response.loaded_files_count') ?? 0 : 0,
    datasets_count: root ? validator.intLike(root.datasets_count, 'response.datasets_count') ?? 0 : 0,
    total_records_count: root
      ? validator.intLike(root.total_records_count, 'response.total_records_count') ?? 0
      : 0,
  }
  validator.throwIfInvalid()
  return health
}

export function parseQuarantine(body: unknown, url: string): { total: number; records: QuarantineEntry[] } {
  const validator = new Validator(url)
  const root = validator.object(body, 'response')
  let records: QuarantineEntry[] = []
  let total = 0
  if (root) {
    total = validator.intLike(root.total, 'response.total') ?? 0
    const list = validator.array(root.records, 'response.records') ?? []
    records = list
      .map((raw, index) => {
        const path = `response.records[${index}]`
        const entry = validator.object(raw, path)
        if (!entry) return null
        const reasonsRaw = validator.array(entry.reasons, `${path}.reasons`) ?? []
        const reasons: string[] = []
        reasonsRaw.forEach((reason, reasonIndex) => {
          const text = validator.requiredString(reason, `${path}.reasons[${reasonIndex}]`)
          if (text !== null) reasons.push(text)
        })
        return {
          entry_index: validator.intLike(entry.entry_index, `${path}.entry_index`) ?? 0,
          table: validator.requiredString(entry.table, `${path}.table`) ?? '',
          record_key: validator.stringOrNumberAsText(entry.record_key, `${path}.record_key`) ?? '',
          reasons,
          native_verified: validator.bool(entry.native_verified, `${path}.native_verified`) ?? false,
          value_under_applied_profile: entry.value_under_applied_profile,
        }
      })
      .filter((entry): entry is QuarantineEntry => entry !== null)
  }
  validator.throwIfInvalid()
  return { total, records }
}

export function parseOverwrites(
  body: unknown,
  url: string,
): { total: number; records: OverwriteEvidenceEntry[] } {
  const validator = new Validator(url)
  const root = validator.object(body, 'response')
  let records: OverwriteEvidenceEntry[] = []
  let total = 0
  if (root) {
    total = validator.intLike(root.total, 'response.total') ?? 0
    const list = validator.array(root.records, 'response.records') ?? []
    records = list
      .map((raw, index) => {
        const path = `response.records[${index}]`
        const entry = validator.object(raw, path)
        if (!entry) return null
        return {
          order: validator.intLike(entry.order, `${path}.order`) ?? 0,
          code_offset: validator.intLike(entry.code_offset, `${path}.code_offset`) ?? 0,
          entry_index: validator.intLike(entry.entry_index, `${path}.entry_index`) ?? 0,
          table: validator.requiredString(entry.table, `${path}.table`) ?? '',
          key: validator.intLike(entry.key, `${path}.key`) ?? 0,
          old_value: entry.old_value,
          new_value: entry.new_value,
        }
      })
      .filter((entry): entry is OverwriteEvidenceEntry => entry !== null)
  }
  validator.throwIfInvalid()
  return { total, records }
}

/** `/missing-aptitudes` and `/ambiguous-skills` return bare arrays. */
export function parseBareRecordArray(body: unknown, url: string): ApiRecord[] {
  const validator = new Validator(url)
  const list = validator.array(body, 'response') ?? []
  const records: ApiRecord[] = []
  list.forEach((raw, index) => {
    const record = parseRecord(validator, raw, `response[${index}]`)
    if (record) records.push(record)
  })
  validator.throwIfInvalid()
  return records
}
