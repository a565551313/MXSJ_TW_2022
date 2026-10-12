import { afterEach, describe, expect, it, vi } from 'vitest'
import { fetchAllRecords } from './reviewApi'

function pages(responses: Array<Record<string, unknown>>) {
  const fetch = vi.fn(async (input: unknown) => {
    const offset = Number(new URL(String(input), 'http://review.test').searchParams.get('offset'))
    const value = responses.shift()
    if (!value) throw new Error('unexpected request')
    const records = value.records as Array<Record<string, unknown>>
    return new Response(JSON.stringify({ dataset: 'synthetic', offset, limit: 500,
      count: records.length, ...value }), { status: 200, headers: { 'Content-Type': 'application/json' } })
  })
  vi.stubGlobal('fetch', fetch)
  return fetch
}

afterEach(() => vi.unstubAllGlobals())

describe('fetch-all consistency (synthetic responses, never product data)', () => {
  it('rejects an empty first page when total is nonzero', async () => {
    pages([{ total: 3, records: [] }])
    await expect(fetchAllRecords('synthetic', {})).rejects.toMatchObject({ code: 'INCOMPLETE_RESULT_SET' })
  })
  it('rejects an early empty subsequent page rather than returning one of three rows', async () => {
    pages([{ total: 3, records: [{ _pk: '1' }] }, { total: 3, records: [] }])
    await expect(fetchAllRecords('synthetic', {})).rejects.toMatchObject({ code: 'INCOMPLETE_RESULT_SET' })
  })
  it('rejects total drift', async () => {
    pages([{ total: 3, records: [{ _pk: '1' }] }, { total: 2, records: [{ _pk: '2' }] }])
    await expect(fetchAllRecords('synthetic', {})).rejects.toMatchObject({ code: 'INCOMPLETE_RESULT_SET' })
  })
  it('rejects repeated identities across pages', async () => {
    pages([{ total: 2, records: [{ _pk: '1' }] }, { total: 2, records: [{ _pk: '1' }] }])
    await expect(fetchAllRecords('synthetic', {})).rejects.toMatchObject({ code: 'INCOMPLETE_RESULT_SET' })
  })
  it('rejects inconsistent returned offset', async () => {
    pages([{ total: 1, offset: 10, records: [{ _pk: '1' }] }])
    await expect(fetchAllRecords('synthetic', {})).rejects.toMatchObject({ code: 'INCOMPLETE_RESULT_SET' })
  })
  it('rejects count different from records length', async () => {
    pages([{ total: 1, count: 0, records: [{ _pk: '1' }] }])
    await expect(fetchAllRecords('synthetic', {})).rejects.toThrow()
  })
  it('rejects records beyond the declared total', async () => {
    pages([{ total: 1, records: [{ _pk: '1' }, { _pk: '2' }] }])
    await expect(fetchAllRecords('synthetic', {})).rejects.toMatchObject({ code: 'INCOMPLETE_RESULT_SET' })
  })
  it('accepts an actually empty result', async () => {
    const fetch = pages([{ total: 0, records: [] }])
    await expect(fetchAllRecords('synthetic', {})).resolves.toEqual({ records: [], total: 0, pages: 1, truncated: false })
    expect(fetch).toHaveBeenCalledTimes(1)
  })
  it('keeps ordered distinct record identities even if business fields are duplicated', async () => {
    const rows = [{ _pk: '1001:0', npcid: 0 }, { _pk: '1001:1', npcid: 0 }]
    pages(rows.map(row => ({ total: 2, records: [row] })))
    await expect(fetchAllRecords('synthetic', {})).resolves.toEqual({ records: rows, total: 2, pages: 2, truncated: false })
  })
})
