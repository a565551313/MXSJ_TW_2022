/**
 * Client tests against Agent H's **real** responses.
 *
 * Every happy-path body here is a committed capture from the running Python
 * service (`fixtures/h_api/`, re-verifiable with
 * `python3 fixtures/capture_h_api.py --check`). Failure paths are produced by
 * mutating those captures or by failing the transport, never by inventing a
 * different contract.
 */
import { describe, expect, it } from 'vitest'
import {
  fetchAmbiguousSkills,
  fetchBatch,
  fetchDatasetMeta,
  fetchDatasets,
  fetchHealth,
  fetchQuarantine,
  fetchRecord,
  fetchRecords,
} from './client'
import { isApiError, isSchemaApiError } from './client'
import { isResponseSchemaError } from './schema'
import { captureBody, installCaptureFetch, installNetworkFailure, jsonResponse, textResponse } from '../test/hApiReplay'

describe('client against real backend captures', () => {
  it('parses the health envelope verbatim', async () => {
    installCaptureFetch()
    const health = await fetchHealth()
    expect(health.batch).toBe('batch_001')
    expect(health.datasets_count).toBe(17)
    expect(health.total_records_count).toBe(12202)
  })

  it('parses a list envelope with offset/limit/count and _pk identities', async () => {
    installCaptureFetch()
    const envelope = await fetchRecords('items', { offset: 0, limit: 25 })
    expect(envelope.dataset).toBe('items')
    expect(envelope.total).toBe(6851)
    expect(envelope.offset).toBe(0)
    expect(envelope.limit).toBe(25)
    expect(envelope.count).toBe(25)
    expect(envelope.records).toHaveLength(25)
    expect(envelope.records[0]._pk).toBe('11')
    expect(envelope.records[0].name).toBe('NPC呼叫器')
    expect(envelope.records[1].name).toBe('鹿茸')
  })

  it('sends the reviewer-reported query as offset/limit, never page/page_size', async () => {
    const { calls } = installCaptureFetch()
    await fetchRecords('items', { offset: 0, limit: 25, q: '鹿茸' })
    expect(calls).toHaveLength(1)
    expect(calls[0]).toContain('/api/v1/review/datasets/items/records?')
    expect(calls[0]).toContain('offset=0')
    expect(calls[0]).toContain('limit=25')
    expect(calls[0]).toContain('q=%E9%B9%BF%E8%8C%B8')
    expect(calls[0]).not.toContain('page=')
  })

  it('parses dataset metadata and the dataset list', async () => {
    installCaptureFetch()
    const list = await fetchDatasets()
    expect(list.datasets).toHaveLength(17)
    expect(list.datasets.map((dataset) => dataset.id)).toContain('pet_skill_overwrites')

    const meta = await fetchDatasetMeta('pet_aptitudes')
    expect(meta.id).toBe('pet_aptitudes')
    expect(meta.rows).toBe(131)
    expect(meta.primary_key).toEqual(['client_shape_id'])
  })

  it('parses the auxiliary endpoints, including bare arrays', async () => {
    installCaptureFetch()
    const quarantine = await fetchQuarantine({ limit: 500 })
    expect(quarantine.total).toBe(4)
    // The parser normalises the key to text; identity is compared as text.
    expect(quarantine.records.map((record) => record.record_key)).toEqual(['72548', '2800', '719', '4406'])

    const ambiguous = await fetchAmbiguousSkills()
    expect(ambiguous).toHaveLength(4)
    expect(ambiguous[0].skill_name_raw).toBe('終級命中')
  })

  it('surfaces a real backend error envelope (HTTP 404, no fallback)', async () => {
    const { calls } = installCaptureFetch()
    await expect(fetchRecord('items', '999999')).rejects.toSatisfy(
      (error: unknown) => isApiError(error) && error.kind === 'http',
    )
    await expect(fetchRecord('items', '999999')).rejects.toMatchObject({
      status: 404,
      code: 'RECORD_NOT_FOUND',
    })
    expect(calls).toHaveLength(2)
  })

  it('reports an un-captured query as a failure instead of an empty list', async () => {
    const { unmatched } = installCaptureFetch()
    let caught: unknown = null
    try {
      await fetchRecords('items', { offset: 0, limit: 25, q: '不存在的查詢' })
    } catch (error) {
      caught = error
    }
    expect(isApiError(caught)).toBe(true)
    expect((caught as { code?: string }).code).toBe('FIXTURE_CAPTURE_MISSING')
    expect(unmatched).toHaveLength(1)
    // The point of the check: the app must not receive `records: []` here.
    expect((caught as { details?: unknown }).details).toBeDefined()
  })

  it('reports a transport failure as a network error', async () => {
    installNetworkFailure()
    await expect(fetchHealth()).rejects.toMatchObject({ kind: 'network' })
  })

  it('reports invalid JSON as such (HTTP 200 is not enough)', async () => {
    installCaptureFetch({ override: () => textResponse(200, '<html>proxy error</html>') })
    let caught: unknown = null
    try {
      await fetchBatch()
    } catch (error) {
      caught = error
    }
    expect(isApiError(caught)).toBe(true)
    expect((caught as { kind: string }).kind).toBe('invalid_json')
  })

  it('reports a JSON-valid but wrongly shaped response as a schema error', async () => {
    // Exactly the shape the reviewer saw when the frontend expected the old
    // fictional contract: HTTP 200, JSON parses, keys are wrong.
    installCaptureFetch({
      override: () =>
        jsonResponse(200, {
          batch_id: 'batch_001',
          tables: [{ name: 'items', rows: 6851 }],
          counters: {},
          input_hashes: {},
        }),
    })

    let caught: unknown = null
    try {
      await fetchBatch()
    } catch (error) {
      caught = error
    }

    expect(isSchemaApiError(caught)).toBe(true)
    expect(isApiError(caught)).toBe(true)
    const error = caught as { kind: string; message: string; schemaError: { issues: Array<{ path: string }> } }
    // The wrapper carries the original structural error, so the UI can print
    // the exact JSON paths that did not match.
    expect(isResponseSchemaError(error.schemaError)).toBe(true)
    expect(error.kind).toBe('schema')
    expect(error.message).toContain('结构')
    expect(error.schemaError.issues.map((issue) => issue.path)).toContain('response.batch')
  })

  it('reports a structurally broken capture (too few keys) as a schema error', async () => {
    const broken = captureBody('batch')
    delete broken.tables_summary
    installCaptureFetch({ override: () => jsonResponse(200, broken) })

    let caught: unknown = null
    try {
      await fetchBatch()
    } catch (error) {
      caught = error
    }
    expect(isSchemaApiError(caught)).toBe(true)
    const issues = (caught as { schemaError: { issues: Array<{ path: string }> } }).schemaError.issues
    expect(issues.some((issue) => issue.path.includes('tables_summary'))).toBe(true)
  })

  it('refuses a list envelope whose count disagrees with its records', async () => {
    const envelope = captureBody('records_pets_limit500') as { count: number }
    const tampered = { ...envelope, count: 999 }
    installCaptureFetch({ override: () => jsonResponse(200, tampered) })

    let caught: unknown = null
    try {
      await fetchRecords('pets', { offset: 0, limit: 25 })
    } catch (error) {
      caught = error
    }
    expect(isSchemaApiError(caught)).toBe(true)
  })
})
