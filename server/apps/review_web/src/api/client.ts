import { API_PATHS, buildQuery, listQueryString, type ListQuery } from './contract'
import type {
  AgreementPage,
  AnomaliesPayload,
  BatchOverview,
  ItemDetail,
  ItemRecord,
  MapDatasetList,
  MapDatasetPage,
  NpcPage,
  NpcSourceKey,
  Page,
  PetDetail,
  PetRecord,
  SkillDetail,
  SkillRecord,
} from './types'

export type ApiErrorKind = 'network' | 'http' | 'invalid_payload' | 'unknown'

export interface ApiErrorOptions {
  kind: ApiErrorKind
  url: string
  message: string
  status?: number
  code?: string
  detail?: string
}

/**
 * Every failure carries the exact relative URL that failed, so a contract
 * mismatch (404) or a dead proxy is visible in the UI instead of being
 * swallowed or replaced by fixture data.
 */
export class ApiError extends Error {
  readonly kind: ApiErrorKind
  readonly url: string
  readonly status?: number
  readonly code?: string
  readonly detail?: string

  constructor(options: ApiErrorOptions) {
    super(options.message)
    this.name = 'ApiError'
    this.kind = options.kind
    this.url = options.url
    this.status = options.status
    this.code = options.code
    this.detail = options.detail
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

function extractMessage(payload: unknown): { message?: string; code?: string } {
  if (typeof payload !== 'object' || payload === null) return {}
  const record = payload as Record<string, unknown>
  const error = record.error
  if (typeof error === 'string') return { message: error }
  if (typeof error === 'object' && error !== null) {
    const err = error as Record<string, unknown>
    return {
      message: typeof err.message === 'string' ? err.message : undefined,
      code: typeof err.code === 'string' ? err.code : undefined,
    }
  }
  return {
    message: typeof record.message === 'string' ? record.message : undefined,
    code: typeof record.code === 'string' ? record.code : undefined,
  }
}

export interface RequestOptions {
  signal?: AbortSignal
}

/**
 * Performs a GET against a relative `/api/...` path.
 * The browser never talks to a sandbox-local absolute URL: everything is
 * same-origin and forwarded by the Vite dev proxy (or a reverse proxy in
 * production) to the Python review API.
 */
export async function getJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
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
      detail: error instanceof Error ? error.message : String(error),
    })
  }

  const body = await response.text()
  let payload: unknown = null
  let parsed = false
  if (body.length > 0) {
    try {
      payload = JSON.parse(body)
      parsed = true
    } catch {
      parsed = false
    }
  }

  if (!response.ok) {
    const extracted = extractMessage(payload)
    throw new ApiError({
      kind: 'http',
      url: path,
      status: response.status,
      code: extracted.code,
      message:
        extracted.message ??
        (parsed
          ? `复核 API 响应 HTTP ${response.status}。`
          : `复核 API 响应 HTTP ${response.status}，且内容不是 JSON（可能是 Vite 代理无法连接到 Python 后端）。`),
      detail: parsed ? undefined : body.slice(0, 400),
    })
  }

  if (!parsed) {
    throw new ApiError({
      kind: 'invalid_payload',
      url: path,
      status: response.status,
      message: '复核 API 响应不是有效的 JSON，无法显示。',
      detail: body.slice(0, 400),
    })
  }

  return payload as T
}

/* ------------------------------------------------------------ endpoints */

export function fetchBatchOverview(options?: RequestOptions): Promise<BatchOverview> {
  return getJson<BatchOverview>(API_PATHS.batch, options)
}

export function fetchItems(query: ListQuery, options?: RequestOptions): Promise<Page<ItemRecord>> {
  return getJson<Page<ItemRecord>>(`${API_PATHS.items}${listQueryString(query)}`, options)
}

export function fetchItem(clientShapeId: string, options?: RequestOptions): Promise<ItemDetail> {
  return getJson<ItemDetail>(API_PATHS.item(clientShapeId), options)
}

export function fetchPets(query: ListQuery, options?: RequestOptions): Promise<Page<PetRecord>> {
  return getJson<Page<PetRecord>>(`${API_PATHS.pets}${listQueryString(query)}`, options)
}

export function fetchPet(clientShapeId: string, options?: RequestOptions): Promise<PetDetail> {
  return getJson<PetDetail>(API_PATHS.pet(clientShapeId), options)
}

export function fetchSkills(query: ListQuery, options?: RequestOptions): Promise<Page<SkillRecord>> {
  return getJson<Page<SkillRecord>>(`${API_PATHS.skills}${listQueryString(query)}`, options)
}

export function fetchSkill(skillId: string, options?: RequestOptions): Promise<SkillDetail> {
  return getJson<SkillDetail>(API_PATHS.skill(skillId), options)
}

export function fetchMapDatasets(options?: RequestOptions): Promise<MapDatasetList> {
  return getJson<MapDatasetList>(API_PATHS.mapDatasets, options)
}

export interface MapDatasetQuery extends ListQuery {
  scene_id?: string
}

export function fetchMapDataset(
  datasetKey: string,
  query: MapDatasetQuery,
  options?: RequestOptions,
): Promise<MapDatasetPage> {
  const suffix = buildQuery({
    q: query.q?.trim() ? query.q.trim() : undefined,
    scene_id: query.scene_id?.trim() ? query.scene_id.trim() : undefined,
    page: query.page ?? 1,
    page_size: query.page_size,
  })
  return getJson<MapDatasetPage>(`${API_PATHS.mapDataset(datasetKey)}${suffix}`, options)
}

export interface NpcQuery extends ListQuery {
  source: NpcSourceKey
  scene_id?: string
}

export function fetchNpcs(query: NpcQuery, options?: RequestOptions): Promise<NpcPage> {
  const suffix = buildQuery({
    source: query.source,
    q: query.q?.trim() ? query.q.trim() : undefined,
    scene_id: query.scene_id?.trim() ? query.scene_id.trim() : undefined,
    page: query.page ?? 1,
    page_size: query.page_size,
  })
  return getJson<NpcPage>(`${API_PATHS.npcs}${suffix}`, options)
}

export interface AgreementQuery extends ListQuery {
  scene_id?: string
}

export function fetchNpcAgreement(query: AgreementQuery, options?: RequestOptions): Promise<AgreementPage> {
  const suffix = buildQuery({
    scene_id: query.scene_id?.trim() ? query.scene_id.trim() : undefined,
    q: query.q?.trim() ? query.q.trim() : undefined,
    page: query.page ?? 1,
    page_size: query.page_size,
  })
  return getJson<AgreementPage>(`${API_PATHS.npcAgreement}${suffix}`, options)
}

export function fetchAnomalies(options?: RequestOptions): Promise<AnomaliesPayload> {
  return getJson<AnomaliesPayload>(API_PATHS.anomalies, options)
}
