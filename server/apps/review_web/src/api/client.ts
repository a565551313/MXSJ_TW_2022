import { API_PATHS, buildQuery, type QueryValue } from './contract'
import {
  parseBatch,
  parseBareRecordArray,
  parseDatasetList,
  parseDatasetMetaResponse,
  parseEnvelope,
  parseHealth,
  parseOverwrites,
  parseQuarantine,
  parseSingleRecord,
  type ApiRecord,
  type BatchPayload,
  type DatasetListPayload,
  type DatasetMeta,
  type Envelope,
  type HealthPayload,
  type OverwriteEvidenceEntry,
  type QuarantineEntry,
} from './parsers'
import { ResponseSchemaError, isResponseSchemaError, type SchemaIssue } from './schema'

export type ApiErrorKind = 'network' | 'http' | 'invalid_json' | 'schema' | 'unknown'

export interface ApiErrorOptions {
  kind: ApiErrorKind
  url: string
  message: string
  status?: number
  code?: string
  details?: unknown
  /** Present when kind === 'schema'. */
  schemaError?: ResponseSchemaError
}

/**
 * Every failure carries the exact relative URL that failed. Nothing is swallowed
 * and nothing is replaced by fixture data: the UI shows the failure.
 */
export class ApiError extends Error {
  readonly kind: ApiErrorKind
  readonly url: string
  readonly status?: number
  readonly code?: string
  readonly details?: unknown
  readonly schemaError?: ResponseSchemaError

  constructor(options: ApiErrorOptions) {
    super(options.message)
    this.name = 'ApiError'
    this.kind = options.kind
    this.url = options.url
    this.status = options.status
    this.code = options.code
    this.details = options.details
    this.schemaError = options.schemaError
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError
}

function isAbortError(error: unknown): boolean {
  return (
    typeof error === 'object' &&
    error !== null &&
    'name' in error &&
    (error as { name?: string }).name === 'AbortError'
  )
}

/** Agent H's unified error envelope: `{error: {code, message, details}}`. */
export function extractApiErrorPayload(payload: unknown): {
  code?: string
  message?: string
  details?: unknown
} {
  if (typeof payload !== 'object' || payload === null) return {}
  const error = (payload as Record<string, unknown>).error
  if (typeof error === 'object' && error !== null) {
    const record = error as Record<string, unknown>
    return {
      code: typeof record.code === 'string' ? record.code : undefined,
      message: typeof record.message === 'string' ? record.message : undefined,
      details: record.details,
    }
  }
  if (typeof error === 'string') return { message: error }
  const record = payload as Record<string, unknown>
  if (typeof record.detail === 'object' && record.detail !== null) {
    // FastAPI's own validation errors (HTTP 422) use this shape.
    const detail = record.detail as Record<string, unknown>
    return {
      code: typeof detail.code === 'string' ? detail.code : 'REQUEST_VALIDATION_ERROR',
      message: typeof detail.message === 'string' ? detail.message : '请求参数未通过后端校验',
      details: detail,
    }
  }
  return { message: typeof record.message === 'string' ? record.message : undefined }
}

/**
 * Structural issues behind an error, from either error type:
 *   - a bare `ResponseSchemaError` (thrown by the parsers), or
 *   - the `ApiError` wrapper the client throws (`kind === 'schema'`).
 *
 * Keeping one accessor means a page-level error boundary and an inline error
 * panel report the very same JSON paths.
 */
export function schemaIssuesOf(error: unknown): SchemaIssue[] | null {
  if (isResponseSchemaError(error)) return [...error.issues]
  if (isApiError(error) && error.kind === 'schema') return error.schemaError?.issues ?? null
  return null
}

/** True when the failure means "HTTP worked, the JSON shape is wrong". */
export function isSchemaApiError(error: unknown): boolean {
  return schemaIssuesOf(error) !== null
}

export interface RequestOptions {
  signal?: AbortSignal
}

/** GET + JSON parse + structural validation, in that order. */
async function requestValidated<T>(
  path: string,
  parse: (body: unknown, url: string) => T,
  options: RequestOptions = {},
): Promise<T> {
  let response: Response
  try {
    response = await fetch(path, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      credentials: 'same-origin',
      signal: options.signal,
    })
  } catch (error) {
    if (isAbortError(error)) throw error
    throw new ApiError({
      kind: 'network',
      url: path,
      message: '无法连接复核 API（请求未发出或连接被中断）。',
      details: error instanceof Error ? error.message : String(error),
    })
  }

  const rawBody = await response.text()
  let payload: unknown = null
  let parsed = false
  if (rawBody.length > 0) {
    try {
      payload = JSON.parse(rawBody)
      parsed = true
    } catch {
      parsed = false
    }
  }

  if (!response.ok) {
    const extracted = parsed ? extractApiErrorPayload(payload) : {}
    throw new ApiError({
      kind: 'http',
      url: path,
      status: response.status,
      code: extracted.code,
      details: extracted.details,
      message:
        extracted.message ??
        (parsed
          ? `复核 API 响应 HTTP ${response.status}。`
          : `复核 API 响应 HTTP ${response.status}，且内容不是 JSON（可能是代理无法连接到后端）。`),
    })
  }

  if (!parsed) {
    throw new ApiError({
      kind: 'invalid_json',
      url: path,
      status: response.status,
      message: '复核 API 响应不是有效的 JSON，无法显示。',
      details: rawBody.slice(0, 400),
    })
  }

  try {
    return parse(payload, path)
  } catch (error) {
    if (error instanceof ResponseSchemaError) {
      throw new ApiError({
        kind: 'schema',
        url: path,
        status: response.status,
        code: 'RESPONSE_SCHEMA_MISMATCH',
        message: error.message,
        details: error.issues,
        schemaError: error,
      })
    }
    throw error
  }
}

/* ------------------------------------------------------------ endpoints */

export function fetchHealth(options?: RequestOptions): Promise<HealthPayload> {
  return requestValidated(API_PATHS.health, parseHealth, options)
}

export function fetchBatch(options?: RequestOptions): Promise<BatchPayload> {
  return requestValidated(API_PATHS.batch, parseBatch, options)
}

export function fetchDatasets(options?: RequestOptions): Promise<DatasetListPayload> {
  return requestValidated(API_PATHS.datasets, parseDatasetList, options)
}

export function fetchDatasetMeta(datasetId: string, options?: RequestOptions): Promise<DatasetMeta> {
  return requestValidated(API_PATHS.dataset(datasetId), parseDatasetMetaResponse, options)
}

export interface RecordsQuery {
  offset: number
  limit: number
  /** Free-text search (`q`) applied by the backend. */
  q?: string
  sortBy?: string
  order?: 'asc' | 'desc'
  /** Exact-match column filters; keys must be real dataset column names. */
  filters?: Record<string, QueryValue>
}

export function fetchRecords(
  datasetId: string,
  query: RecordsQuery,
  options?: RequestOptions,
): Promise<Envelope> {
  const suffix = buildQuery({
    offset: query.offset,
    limit: query.limit,
    q: query.q?.trim() ? query.q.trim() : undefined,
    sort_by: query.sortBy,
    order: query.order,
    ...(query.filters ?? {}),
  })
  return requestValidated(`${API_PATHS.records(datasetId)}${suffix}`, parseEnvelope, options)
}

export function fetchRecord(
  datasetId: string,
  recordId: string,
  options?: RequestOptions,
): Promise<ApiRecord> {
  return requestValidated(API_PATHS.record(datasetId, recordId), parseSingleRecord, options)
}

export interface QuarantineQuery {
  entryIndex?: number
  recordKey?: string | number
  offset?: number
  limit?: number
}

export function fetchQuarantine(
  query: QuarantineQuery = {},
  options?: RequestOptions,
): Promise<{ total: number; records: QuarantineEntry[] }> {
  const suffix = buildQuery({
    entry_index: query.entryIndex,
    record_key: query.recordKey,
    offset: query.offset ?? 0,
    limit: query.limit ?? 50,
  })
  return requestValidated(`${API_PATHS.quarantine}${suffix}`, parseQuarantine, options)
}

export function fetchOverwrites(
  query: { key?: number; offset?: number; limit?: number } = {},
  options?: RequestOptions,
): Promise<{ total: number; records: OverwriteEvidenceEntry[] }> {
  const suffix = buildQuery({
    key: query.key,
    offset: query.offset ?? 0,
    limit: query.limit ?? 50,
  })
  return requestValidated(`${API_PATHS.overwrites}${suffix}`, parseOverwrites, options)
}

export function fetchMissingAptitudes(options?: RequestOptions): Promise<ApiRecord[]> {
  return requestValidated(API_PATHS.missingAptitudes, parseBareRecordArray, options)
}

export function fetchAmbiguousSkills(options?: RequestOptions): Promise<ApiRecord[]> {
  return requestValidated(API_PATHS.ambiguousSkills, parseBareRecordArray, options)
}
