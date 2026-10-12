/**
 * TEST-ONLY fetch stub backed by Agent H's **real** captured responses.
 *
 * `fixtures/h_api/` holds 103 responses recorded from the running Python review
 * API (see `fixtures/capture_h_api.py`, verified with `--check`). This helper
 * replays them through the app's normal client, so tests exercise the genuine
 * shapes: `{dataset,total,offset,limit,count,records}`, `_pk` identities, raw
 * byte dictionaries for quarantined records, bare arrays for the auxiliary
 * endpoints, and the real error envelopes.
 *
 * Guarantees:
 *   - nothing is invented: records come verbatim from the captures;
 *   - an un-captured request fails with an explicit error body (the app must
 *     show it, not silently render empty data);
 *   - `mutateCapture()` exists so a test can prove that a JSON-valid but
 *     wrong-shaped response is reported as an interface-structure error.
 *
 * No production module imports this file (`architectureGuards.test.ts` fails if
 * that ever changes), and the app's default runtime mode never uses it.
 */
import { existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { vi } from 'vitest'
import { loadReplay, respond, type ReplayBundle } from '../../fixtures/h_api/replay.mjs'

/** Walks up from the working directory until the review_web app dir is found. */
function findAppDir(): string {
  let current = process.cwd()
  for (let depth = 0; depth < 6; depth += 1) {
    if (existsSync(join(current, 'package.json')) && existsSync(join(current, 'src'))) return current
    current = dirname(current)
  }
  throw new Error(`could not locate the review_web app directory from ${process.cwd()}`)
}

export const CAPTURE_DIR = join(findAppDir(), 'fixtures', 'h_api')

let bundle: ReplayBundle | null = null

/** The committed captures (loaded once per worker). */
export function captures(): ReplayBundle {
  if (bundle === null) bundle = loadReplay(CAPTURE_DIR)
  return bundle
}

/** Raw body of one capture, deep-copied so a test can modify it safely. */
export function captureBody(captureId: string): any {
  const entry = captures().captures.find((item) => item.id === captureId)
  if (!entry) throw new Error(`no capture named ${captureId}`)
  return JSON.parse(JSON.stringify(entry.body))
}

export interface FakeResponse {
  ok: boolean
  status: number
  text: () => Promise<string>
}

export function jsonResponse(status: number, body: unknown): FakeResponse {
  const text = JSON.stringify(body)
  return { ok: status >= 200 && status < 300, status, text: async () => text }
}

export function textResponse(status: number, body: string): FakeResponse {
  return { ok: status >= 200 && status < 300, status, text: async () => body }
}

export interface ReplayBehaviour {
  /** Return a custom response for a URL; `null` falls through to the capture. */
  override?: (url: string) => FakeResponse | null
  /** Body mutations applied after a capture is replayed (keyed by capture id). */
  mutations?: Map<string, (body: any) => unknown>
}

export interface ReplayFetch {
  /** Every URL the app requested, in order. */
  calls: string[]
  /** Capture ids that answered a request, in order. */
  served: string[]
  /** Requests the captures could not answer (they must surface as errors). */
  unmatched: string[]
  stub: ReturnType<typeof vi.fn>
  replay: ReplayBundle
}

/**
 * Installs a fetch stub that answers from the captures for the duration of one
 * test (`vi.unstubAllGlobals()` in `src/test/setup.ts` removes it afterwards).
 */
export function installCaptureFetch(behaviour: ReplayBehaviour = {}): ReplayFetch {
  const replay = captures()
  const calls: string[] = []
  const served: string[] = []
  const unmatched: string[] = []

  const stub = vi.fn(async (input: unknown) => {
    const url =
      typeof input === 'string' ? input : String((input as { url?: string })?.url ?? input)
    calls.push(url)

    const overridden = behaviour.override?.(url)
    if (overridden) return overridden

    const parsed = new URL(url, 'http://review.local')
    const { status, body, replay: meta } = respond(replay, {
      method: 'GET',
      pathname: parsed.pathname,
      searchParams: parsed.searchParams,
    })

    if (meta.capture_id === null) unmatched.push(url)
    else served.push(meta.capture_id)

    const mutate = meta.capture_id ? behaviour.mutations?.get(meta.capture_id) : undefined
    return jsonResponse(status, mutate ? mutate(body) : body)
  })

  vi.stubGlobal('fetch', stub)
  return { calls, served, unmatched, stub, replay }
}

/** Every fetch fails at the transport layer (API down, proxy refused). */
export function installNetworkFailure(): ReturnType<typeof vi.fn> {
  const stub = vi.fn(async () => {
    throw new TypeError('Failed to fetch')
  })
  vi.stubGlobal('fetch', stub)
  return stub
}

/** Convenience: mutations map for a single capture id. */
export function mutate(captureId: string, fn: (body: any) => unknown): Map<string, (body: any) => unknown> {
  return new Map([[captureId, fn]])
}
