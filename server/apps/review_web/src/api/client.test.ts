import { describe, expect, it, vi } from 'vitest'
import { ApiError, fetchBatchOverview, fetchItem, fetchItems, getJson } from './client'
import { REVIEW_API_PREFIX } from './contract'
import { installFixtureFetch, installNetworkFailure, jsonResponse, textResponse } from '../test/fakeApi'

describe('review API client', () => {
  it('always requests a same-origin relative /api/v1/review path', async () => {
    const { calls } = installFixtureFetch()
    await fetchBatchOverview()
    await fetchItems({ q: '鹿茸', page: 2, page_size: 25 })
    await fetchItem('12')

    expect(calls).toHaveLength(3)
    for (const url of calls) {
      expect(url.startsWith(REVIEW_API_PREFIX)).toBe(true)
      expect(url.startsWith('/')).toBe(true)
      expect(url).not.toMatch(/^https?:/i)
      expect(url).not.toContain('localhost')
      expect(url).not.toContain('127.0.0.1')
      expect(url).not.toContain('0.0.0.0')
    }
    expect(calls[1]).toBe('/api/v1/review/items?q=%E9%B9%BF%E8%8C%B8&page=2&page_size=25')
  })

  it('omits empty search parameters instead of sending placeholders', async () => {
    const { calls } = installFixtureFetch()
    await fetchItems({ q: '   ', page: 1, page_size: 25 })
    expect(calls[0]).toBe('/api/v1/review/items?page=1&page_size=25')
  })

  it('surfaces HTTP errors with the failing URL and status', async () => {
    installFixtureFetch({
      override: (url) =>
        url.includes('/items') ? jsonResponse(404, { error: { code: 'NOT_FOUND', message: '不存在' } }) : null,
    })

    const error = await fetchItems({ page: 1, page_size: 25 }).catch((caught: unknown) => caught)
    expect(error).toBeInstanceOf(ApiError)
    const apiError = error as ApiError
    expect(apiError.kind).toBe('http')
    expect(apiError.status).toBe(404)
    expect(apiError.code).toBe('NOT_FOUND')
    expect(apiError.url).toBe('/api/v1/review/items?page=1&page_size=25')
  })

  it('explains a non-JSON response (dead proxy) instead of pretending the data is empty', async () => {
    installFixtureFetch({
      override: (url) => (url.includes('/batch') ? textResponse(500, '<html>proxy error</html>') : null),
    })
    const error = (await fetchBatchOverview().catch((caught: unknown) => caught)) as ApiError
    expect(error.kind).toBe('http')
    expect(error.status).toBe(500)
    expect(error.message).toContain('不是 JSON')
  })

  it('reports a transport failure as a network error', async () => {
    installNetworkFailure()
    const error = (await fetchBatchOverview().catch((caught: unknown) => caught)) as ApiError
    expect(error).toBeInstanceOf(ApiError)
    expect(error.kind).toBe('network')
    expect(error.message).toContain('无法连接复核 API')
  })

  it('rejects a 200 response whose body is not JSON', async () => {
    installFixtureFetch({ override: () => textResponse(200, 'not json') })
    const error = (await getJson('/api/v1/review/batch').catch((caught: unknown) => caught)) as ApiError
    expect(error.kind).toBe('invalid_payload')
  })

  it('does not fall back to fixture data when the API fails', async () => {
    const stub = installNetworkFailure()
    const result = await fetchBatchOverview().catch((caught: unknown) => caught)
    expect(result).toBeInstanceOf(ApiError)
    expect(stub).toHaveBeenCalledTimes(1)
    // A fixture fallback would have returned the sample batch instead of throwing.
    expect(result).not.toHaveProperty('batch_id')
  })

  it('propagates aborts instead of converting them into API errors', async () => {
    const controller = new AbortController()
    const abortError = Object.assign(new Error('aborted'), { name: 'AbortError' })
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        controller.abort()
        throw abortError
      }),
    )
    const caught = await getJson('/api/v1/review/batch', { signal: controller.signal }).catch(
      (error: unknown) => error,
    )
    expect(caught).toBe(abortError)
    expect(caught).not.toBeInstanceOf(ApiError)
  })
})
