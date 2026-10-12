/**
 * The one and only place where review API paths and query parameters are built.
 *
 * ============================ 待接口联调 (PENDING) ============================
 * As of baseline commit 5f23690 the authoritative contract file
 * `server/docs/review_browser/API_CONTRACT.md` (owned by Agent H) does **not**
 * exist in this repository, and no Python review backend is present under
 * `server/`. The surface below is the frontend's *request* to Agent H: it is
 * derived strictly from the batch_001 data model (manifest columns, validation
 * counters, quarantine/overwrite evidence files) and from the page requirements.
 *
 * Consequences, stated plainly:
 *   - Real API integration has NOT been verified. Nothing here is evidence that
 *     the backend exists or agrees with these paths.
 *   - When `API_CONTRACT.md` lands, this file is the single adaptation point:
 *     change the paths/params here, and the callers keep working unchanged.
 *   - If the backend answers 404 for a path, the UI shows that exact path in its
 *     error state instead of pretending the data is missing.
 * ============================================================================
 */

export const REVIEW_API_PREFIX = '/api/v1/review'

export const API_PATHS = {
  batch: `${REVIEW_API_PREFIX}/batch`,
  items: `${REVIEW_API_PREFIX}/items`,
  item: (clientShapeId: string) => `${REVIEW_API_PREFIX}/items/${encodeURIComponent(clientShapeId)}`,
  pets: `${REVIEW_API_PREFIX}/pets`,
  pet: (clientShapeId: string) => `${REVIEW_API_PREFIX}/pets/${encodeURIComponent(clientShapeId)}`,
  skills: `${REVIEW_API_PREFIX}/skills`,
  skill: (skillId: string) => `${REVIEW_API_PREFIX}/skills/${encodeURIComponent(skillId)}`,
  mapDatasets: `${REVIEW_API_PREFIX}/maps/datasets`,
  mapDataset: (datasetKey: string) =>
    `${REVIEW_API_PREFIX}/maps/datasets/${encodeURIComponent(datasetKey)}`,
  npcs: `${REVIEW_API_PREFIX}/npcs`,
  npcAgreement: `${REVIEW_API_PREFIX}/npcs/agreement`,
  anomalies: `${REVIEW_API_PREFIX}/anomalies`,
} as const

export type QueryValue = string | number | boolean | null | undefined

/** Drops empty/undefined params so the URL only carries what the user asked for. */
export function buildQuery(params: Record<string, QueryValue>): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === null || value === undefined) continue
    const text = String(value)
    if (text.length === 0) continue
    search.set(key, text)
  }
  const query = search.toString()
  return query.length > 0 ? `?${query}` : ''
}

export const DEFAULT_PAGE_SIZE = 25
export const PAGE_SIZE_OPTIONS = [25, 50, 100] as const

export interface ListQuery {
  q?: string
  page?: number
  page_size?: number
}

export function listQueryString(query: ListQuery): string {
  return buildQuery({
    q: query.q?.trim() ? query.q.trim() : undefined,
    page: query.page ?? 1,
    page_size: query.page_size ?? DEFAULT_PAGE_SIZE,
  })
}
