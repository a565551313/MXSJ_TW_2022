/**
 * Replay of the committed Agent H captures (`fixtures/h_api/*.json`).
 *
 * Used by two callers, both explicitly non-integration:
 *   - `src/test/hApiReplay.ts` (vitest) so tests parse/renders *real* backend
 *     responses instead of a frontend-invented contract;
 *   - `fixtures/serve-fixture-api.mjs` (`npm run dev:fixture`) so the UI can be
 *     walked through without a Python backend.
 *
 * Rules, deliberately strict so a replay can never pass itself off as a live,
 * complete data source:
 *   1. A request is answered only if a capture exists for the *same* path and the
 *      same non-paging query parameters (`offset`/`limit` are ignored when
 *      matching, because paging stays inside one captured window).
 *   2. Records come verbatim from the capture. `total` stays the real dataset
 *      total returned by the backend, never a locally recomputed number.
 *   3. `offset`/`limit` in the answer are the requested ones, so the pager in
 *      the UI keeps working while records stay genuine.
 *   4. A paging request that leaves the captured window, or any un-captured
 *      filter combination, is answered with an explicit
 *      `FIXTURE_CAPTURE_MISSING` error - never with invented rows, an empty
 *      list, or a different page's rows.
 *   5. No filtering, sorting, or value rewriting is done locally: the backend is
 *      the only thing allowed to decide which rows match a filter.
 */
import { readFileSync } from 'node:fs'
import { join } from 'node:path'

export const REVIEW_PREFIX = '/api/v1/review'

const PAGING_KEYS = new Set(['offset', 'limit'])

/** Loads every capture plus the manifest that describes it. */
export function loadReplay(dir) {
  const manifest = JSON.parse(readFileSync(join(dir, 'manifest.json'), 'utf-8'))
  const captures = manifest.captures.map((entry) => ({
    ...entry,
    body: JSON.parse(readFileSync(join(dir, entry.file), 'utf-8')),
  }))
  return { dir, manifest, captures }
}

export function describeReplay(replay) {
  return `${replay.captures.length} captures from ${replay.manifest._capture.provenance}`
}

function normalisePath(pathname) {
  const trimmed = pathname.replace(/\/+$/, '')
  return trimmed.length === 0 ? '/' : trimmed
}

function filterKey(searchParams) {
  const pairs = []
  for (const [key, value] of searchParams) {
    if (PAGING_KEYS.has(key)) continue
    if (value === '') continue
    pairs.push([key, value])
  }
  pairs.sort((a, b) => (a[0] === b[0] ? (a[1] < b[1] ? -1 : 1) : a[0] < b[0] ? -1 : 1))
  return pairs.map(([key, value]) => `${key}=${value}`).join('&')
}

function captureFilterKey(entry) {
  return filterKey(new URLSearchParams(entry.query ?? ''))
}

function pagingParams(searchParams) {
  const offset = searchParams.get('offset')
  const limit = searchParams.get('limit')
  return {
    offset: offset === null ? 0 : Number(offset),
    limit: limit === null ? null : Number(limit),
  }
}

/**
 * Describes the captured page: where it starts, how many rows it holds and
 * whether it contains the *whole* filtered result set.
 *
 * `reachesEnd` matters: when the captured page runs up to (or past) the end of
 * the filtered set, a request may be answered with fewer rows than it asked for,
 * or with an empty list for an offset beyond the data - exactly like the
 * backend. When the page was cut off in the middle of the set, an out-of-window
 * offset must fail instead of looking like the end of the data.
 */
function windowOf(entry) {
  const params = new URLSearchParams(entry.query ?? '')
  const base = Number(params.get('offset') ?? '0')
  const body = entry.body && typeof entry.body === 'object' ? entry.body : {}
  const records = Array.isArray(body.records) ? body.records : []
  const totalRaw = typeof body.total === 'number' ? body.total : null
  const total = totalRaw === null ? base + records.length : totalRaw
  return { base, count: records.length, total, reachesEnd: base + records.length >= total }
}

function missing(replay, method, pathname, search) {
  return {
    status: 404,
    body: {
      error: {
        code: 'FIXTURE_CAPTURE_MISSING',
        message:
          `复核夹具没有捕获这个请求：${method} ${pathname}${search ? `?${search}` : ''}。` +
          `夹具模式只回放 fixtures/h_api/ 中已捕获的响应，不会用别的页面、空列表或编造的数据来代替。`,
        details: { captures: replay.captures.length, dir: 'fixtures/h_api' },
      },
    },
    replay: { capture_id: null, mode: 'missing' },
  }
}

/**
 * Rows the backend would return for [offset, offset+limit) within this captured
 * page, or `null` when the capture cannot answer that window truthfully.
 */
function sliceRecords(window, offset, limit) {
  const start = offset - window.base
  if (start < 0) return null
  if (start > window.count) return window.reachesEnd ? [] : null
  if (limit === null) return window.records.slice(start)
  const end = start + limit
  if (end <= window.count) return window.records.slice(start, end)
  // The requested page reaches past the captured rows: only allowed when the
  // captured page already runs to the end of the filtered set, in which case the
  // backend itself would return a short page.
  return window.reachesEnd ? window.records.slice(start, window.count) : null
}

/**
 * Answers one request from the captures.
 *
 * @returns {{status: number, body: unknown, replay: {capture_id: string|null, mode: string}}}
 */
export function respond(replay, request) {
  const method = (request.method ?? 'GET').toUpperCase()
  const pathname = normalisePath(request.pathname ?? '/')
  const searchParams =
    request.searchParams instanceof URLSearchParams
      ? request.searchParams
      : new URLSearchParams(request.searchParams ?? '')

  if (method !== 'GET' && method !== 'HEAD') {
    return {
      status: 405,
      body: {
        error: {
          code: 'METHOD_NOT_ALLOWED',
          message: '复核界面是只读的：夹具服务同样只接受 GET。',
        },
      },
      replay: { capture_id: null, mode: 'method' },
    }
  }

  if (!pathname.startsWith(REVIEW_PREFIX)) {
    return {
      status: 404,
      body: {
        error: {
          code: 'NOT_FOUND',
          message: `夹具服务只提供 ${REVIEW_PREFIX} 下的路径。`,
        },
      },
      replay: { capture_id: null, mode: 'unknown-prefix' },
    }
  }

  const wanted = filterKey(searchParams)
  const candidates = replay.captures.filter(
    (entry) => entry.method === method && normalisePath(entry.path) === pathname && captureFilterKey(entry) === wanted,
  )

  if (candidates.length === 0) {
    return missing(replay, method, pathname, searchParams.toString())
  }

  const { offset, limit } = pagingParams(searchParams)
  const body = candidates[0].body

  // Endpoints whose body is a list envelope: page inside the captured window.
  if (body && typeof body === 'object' && Array.isArray(body.records)) {
    for (const entry of candidates) {
      const window = windowOf(entry)
      window.records = entry.body.records
      const sliced = sliceRecords(window, offset, limit)
      if (sliced === null) continue
      return {
        status: entry.status,
        body: {
          ...entry.body,
          offset,
          limit: limit === null ? sliced.length : limit,
          count: sliced.length,
          records: sliced,
        },
        replay: { capture_id: entry.id, mode: 'paged' },
      }
    }
    return missing(replay, method, pathname, searchParams.toString())
  }

  // Bare arrays (missing-aptitudes / ambiguous-skills): returned verbatim.
  if (Array.isArray(body)) {
    return {
      status: candidates[0].status,
      body,
      replay: { capture_id: candidates[0].id, mode: 'verbatim' },
    }
  }

  return {
    status: candidates[0].status,
    body,
    replay: { capture_id: candidates[0].id, mode: 'verbatim' },
  }
}
