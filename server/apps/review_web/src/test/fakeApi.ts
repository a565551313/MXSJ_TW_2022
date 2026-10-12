/**
 * TEST-AND-FIXTURE-ONLY fetch stub.
 *
 * This module lives under `src/test/` and is imported exclusively by
 * `*.test.tsx` files and the setup helper. No production module imports it:
 * `src/test/noFixtureInProduction.test.ts` fails the build if that changes.
 *
 * It routes requests through the same fixture contract handler that the
 * explicit fixture dev server uses, so tests see the shapes the demo shows.
 */
import { vi } from 'vitest'
import { handleRequest, loadFixture } from '../../fixtures/contractHandler.mjs'

export interface FetchBehaviour {
  /** Return a custom response for a URL prefix; `null` falls through. */
  override?: (url: string) => FakeResponse | null
}

export interface FakeResponse {
  ok: boolean
  status: number
  text: () => Promise<string>
}

export function jsonResponse(status: number, body: unknown): FakeResponse {
  const text = JSON.stringify(body)
  return {
    ok: status >= 200 && status < 300,
    status,
    text: async () => text,
  }
}

export function textResponse(status: number, body: string): FakeResponse {
  return {
    ok: status >= 200 && status < 300,
    status,
    text: async () => body,
  }
}

export interface FixtureFetch {
  calls: string[]
  stub: ReturnType<typeof vi.fn>
  fixture: any
}

/** Installs a fetch stub that answers from `fixtures/batch001.sample.json`. */
export function installFixtureFetch(behaviour: FetchBehaviour = {}): FixtureFetch {
  const fixture = loadFixture()
  const calls: string[] = []

  const stub = vi.fn(async (input: unknown) => {
    const url = typeof input === 'string' ? input : String((input as { url?: string })?.url ?? input)
    calls.push(url)

    const overridden = behaviour.override?.(url)
    if (overridden) return overridden

    const parsed = new URL(url, 'http://review.local')
    const { status, body } = handleRequest(fixture, parsed.pathname, parsed.searchParams)
    return jsonResponse(status, body)
  })

  vi.stubGlobal('fetch', stub)
  return { calls, stub, fixture }
}

/** Every fetch fails at the transport layer (API down, proxy refused). */
export function installNetworkFailure(): ReturnType<typeof vi.fn> {
  const stub = vi.fn(async () => {
    throw new TypeError('Failed to fetch')
  })
  vi.stubGlobal('fetch', stub)
  return stub
}
