/**
 * Live integration checks against the running Python review API.
 *
 * These do real HTTP: the browser-side client uses relative `/api/...` URLs, so
 * the test prepends the backend base URL - exactly what the Vite proxy does in
 * the browser - and everything after that is a genuine request/response cycle
 * with the real server (no fetch stub, no captured body).
 *
 * The live part is opt-in, because `npm test` must not depend on a running
 * backend:
 *
 *     REVIEW_API_BASE=http://127.0.0.1:8000 npx vitest run src/api/liveBackend.test.ts
 *
 * The wrong-shape check at the end starts its own tiny HTTP server and needs no
 * backend: it proves that an HTTP 200 with a JSON body of the wrong structure is
 * reported as an interface-structure error, not rendered as empty data.
 */
import http from 'node:http'
import type { AddressInfo } from 'node:net'
import { afterAll, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest'
import { fetchBatch, fetchHealth, fetchRecord, fetchRecords, isApiError, isSchemaApiError } from './client'
import {
  getAptitudeStatus,
  getPetDetail,
  getSkillDetail,
  loadAgreement,
  loadAnomalyBoard,
  loadNpcSourcePage,
} from './reviewApi'

const BASE = process.env.REVIEW_API_BASE ?? ''
const live = BASE.length > 0

/** Points the client's relative URLs at the live backend (the proxy's job). */
function routeFetchTo(base: string): void {
  const realFetch = globalThis.fetch
  vi.stubGlobal('fetch', (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === 'string' ? new URL(input, base) : input
    return realFetch(url as RequestInfo, init)
  })
}

describe.runIf(live)('live review API integration', () => {
  // Re-installed per test: the global test setup clears stubs after each test.
  beforeEach(() => {
    routeFetchTo(BASE)
  })

  it('reads the batch summary with real counts', async () => {
    const [health, batch] = await Promise.all([fetchHealth(), fetchBatch()])
    expect(health.status).toBe('ready')
    expect(health.datasets_count).toBe(17)
    expect(batch.batch).toBe('batch_001')
    expect(batch.native_loader_confirmed).toBe(false)
    expect(batch.tables_summary['1945']).toEqual({
      source_records: 6852,
      review_csv_records: 6851,
      quarantined_records: 1,
    })
    expect(batch.validation_summary.missing_aptitude_count).toBe(3)
    expect(batch.validation_summary.quarantined_record_count).toBe(4)
    expect(batch.validation_summary.skill_unique_count).toBe(581)
    expect(batch.validation_summary.skill_write_count).toBe(590)
    expect(batch.validation_summary.skill_overwrite_count).toBe(9)
    expect(batch.validation_summary.ambiguous_pet_skill_names).toEqual({
      終級命中: [329, 355],
      高級命中: [229, 255],
    })
  })

  it('pages and searches the item dataset with offset/limit', async () => {
    const page1 = await fetchRecords('items', { offset: 0, limit: 25 })
    expect(page1.total).toBe(6851)
    expect(page1.count).toBe(25)
    expect(page1.records[0]._pk).toBe('11')

    const search = await fetchRecords('items', { offset: 0, limit: 25, q: '鹿茸' })
    expect(search.total).toBe(2)
    expect(search.records.map((record) => String(record.client_shape_id))).toEqual(['12', '21302'])

    const detail = await fetchRecord('items', '12')
    expect(detail.name).toBe('鹿茸')
  })

  it('keeps quarantined, missing and present aptitudes apart', async () => {
    const [quarantined, missing, present] = await Promise.all([
      getAptitudeStatus('2800'),
      getAptitudeStatus('3010'),
      getAptitudeStatus('4011'),
    ])
    expect(quarantined.status).toBe('quarantined')
    expect(quarantined.evidence_id).toBe('2954:2800')
    expect(missing.status).toBe('missing_in_source_table')
    expect(missing.reason).toBe('no_record_in_2954')
    expect(present.status).toBe('present')
  })

  it('composes a pet detail from the real related endpoints', async () => {
    const detail = await getPetDetail('4011')
    expect(detail.pet.name).toBe('仙獸吉祥虎')
    expect(detail.candidate_skills.map((skill) => [skill.sequence, skill.skill_name_raw])).toEqual([
      [0, '新月獠牙'],
      [1, '終級命中'],
      [2, '終級神跡'],
      [3, '終級強力'],
    ])
    const terminal = detail.candidate_skills.find((skill) => skill.skill_name_raw === '終級命中')
    expect(terminal?.matches.map((match) => match.skill_id)).toEqual(['329', '355'])
    expect(detail.required_skills).toEqual([])
    expect(detail.aptitude?.fields.find((field) => field.label === '法力資質')?.value).toBe('1900')
  })

  it('decodes skill overwrite evidence from the real byte dictionaries', async () => {
    const detail = await getSkillDetail('4573')
    expect(detail.skill.name).toBe('地魔返生術')
    expect(detail.overwrites).toHaveLength(1)
    expect(detail.overwrites[0]).toMatchObject({
      write_order: 352,
      code_offset: 22409,
      old_name: '天魔返生術',
      new_name: '地魔返生術',
      identical_values: false,
    })
  })

  it('collects the anomaly board from the auxiliary endpoints', async () => {
    const board = await loadAnomalyBoard()
    expect(board.quarantine_total).toBe(4)
    expect(board.quarantine.map((entry) => entry.record_key)).toEqual(['72548', '2800', '719', '4406'])
    expect(board.missing_aptitudes.map((row) => row.client_shape_id)).toEqual(['3010', '4021', '4022'])
    expect(board.ambiguous_skill_names.map((group) => [group.skill_name_raw, group.ids])).toEqual([
      ['終級命中', ['329', '355']],
      ['高級命中', ['229', '255']],
    ])
    expect(board.overwrites_total).toBe(9)
  })

  it('reads both NPC sources separately, including their zero-id counts', async () => {
    const [pos2601, pos2804] = await Promise.all([
      loadNpcSourcePage('npcposdata_records', { page: 1, pageSize: 25 }),
      loadNpcSourcePage('minimapnpcpos_pos_records', { page: 1, pageSize: 25 }),
    ])
    expect(pos2601.envelope.total).toBe(1335)
    expect(pos2601.zeroNpcIdTotal).toBe(632)
    expect(pos2804.envelope.total).toBe(1344)
    expect(pos2804.zeroNpcIdTotal).toBe(631)
    expect(Object.keys(pos2601.envelope.records[0])).not.toContain('scene_display_name')
    expect(Object.keys(pos2804.envelope.records[0])).toContain('scene_display_name')
  })

  it('counts agreement categories over every page of the dataset', async () => {
    const view = await loadAgreement({ page: 1, pageSize: 25 })
    expect(view.total).toBe(677)
    expect(view.counts.identical_sequence).toBe(647)
    expect(Object.values(view.counts).reduce((total, value) => total + value, 0)).toBe(677)
  })

  it('surfaces real backend error envelopes (404 / 400 / 405)', async () => {
    await expect(fetchRecord('items', '999999')).rejects.toMatchObject({
      kind: 'http',
      status: 404,
      code: 'RECORD_NOT_FOUND',
    })
    await expect(fetchRecords('items', { offset: 0, limit: 0 })).rejects.toMatchObject({
      kind: 'http',
      status: 400,
      code: 'INVALID_PARAMETER',
    })
    await expect(fetchRecords('unknown_dataset', { offset: 0, limit: 1 })).rejects.toMatchObject({
      status: 404,
      code: 'DATASET_NOT_FOUND',
    })

    // A POST (the UI never sends one) is rejected by the backend as well.
    const realFetch = globalThis.fetch
    const response = await realFetch(new URL('/api/v1/review/batch', BASE), { method: 'POST' })
    expect(response.status).toBe(405)
  })
})

describe('HTTP 200 with the wrong JSON structure', () => {
  let server: http.Server
  let base = ''

  beforeAll(async () => {
    server = http.createServer((request, response) => {
      const url = request.url ?? '/'
      const send = (body: unknown) => {
        const payload = JSON.stringify(body)
        response.writeHead(200, { 'content-type': 'application/json; charset=utf-8' })
        response.end(payload)
      }
      if (url.startsWith('/api/v1/review/batch')) {
        // The fictional shape the old frontend expected.
        return send({ batch_id: 'batch_001', tables: [{ name: 'items', rows: 6851 }], counters: {} })
      }
      if (url.startsWith('/api/v1/review/datasets/items/records')) {
        // A list endpoint without records/count at all.
        return send({ dataset: 'items', total: 6851 })
      }
      if (url.startsWith('/api/v1/review/health')) {
        // HTTP 200 with a body that is not JSON at all.
        response.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
        return response.end('<html>proxy error</html>')
      }
      response.writeHead(500, { 'content-type': 'application/json' })
      response.end(JSON.stringify({ error: { code: 'TEST', message: 'unexpected request' } }))
    })
    await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve))
    base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`
  })

  beforeEach(() => {
    routeFetchTo(base)
  })

  afterAll(async () => {
    await new Promise<void>((resolve) => server.close(() => resolve()))
  })

  it('reports the batch shape mismatch with the offending JSON paths', async () => {
    let caught: unknown = null
    try {
      await fetchBatch()
    } catch (error) {
      caught = error
    }
    expect(isSchemaApiError(caught)).toBe(true)
    expect(isApiError(caught)).toBe(true)
    const error = caught as { kind: string; schemaError: { issues: Array<{ path: string }> } }
    expect(error.kind).toBe('schema')
    const paths = error.schemaError.issues.map((issue) => issue.path)
    expect(paths).toContain('response.tables_summary')
    expect(paths).toContain('response.validation_summary')
    expect(paths).toContain('response.batch')
  })

  it('never turns a missing records array into an empty list', async () => {
    let caught: unknown = null
    try {
      await fetchRecords('items', { offset: 0, limit: 25 })
    } catch (error) {
      caught = error
    }
    expect(isSchemaApiError(caught)).toBe(true)
    expect((caught as { schemaError: { issues: Array<{ path: string }> } }).schemaError.issues).toContainEqual(
      expect.objectContaining({ path: 'response.records' }),
    )
  })

  it('reports a 200 whose body is not JSON as an invalid-JSON error', async () => {
    await expect(fetchHealth()).rejects.toMatchObject({ kind: 'invalid_json', status: 200 })
  })
})
