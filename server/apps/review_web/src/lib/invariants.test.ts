import { describe, expect, it } from 'vitest'
import type { AnomaliesPayload } from '../api/types'
import { evaluateInvariants, REVIEW_INVARIANTS } from './invariants'
import { loadFixture } from '../../fixtures/contractHandler.mjs'

const fixturePayload = (loadFixture().anomalies as unknown) as AnomaliesPayload

function clone(): AnomaliesPayload {
  return JSON.parse(JSON.stringify(fixturePayload)) as AnomaliesPayload
}

describe('review invariants', () => {
  it('passes for the frozen batch_001 sample', () => {
    const results = evaluateInvariants(fixturePayload)
    expect(results).toHaveLength(REVIEW_INVARIANTS.length)
    expect(results.filter((result) => !result.ok)).toEqual([])
  })

  it('reports the actual candidate ids from the API payload', () => {
    const results = evaluateInvariants(fixturePayload)
    const ambiguous = results.find((result) => result.id === 'ambiguous-229-255')
    expect(ambiguous?.actual).toBe('229 / 255')
    const terminal = results.find((result) => result.id === 'ambiguous-329-355')
    expect(terminal?.actual).toBe('329 / 355')
  })

  it('fails loudly when the backend stops quarantining a record', () => {
    const payload = clone()
    payload.quarantine = payload.quarantine.filter((record) => record.record_key !== 72548)
    const result = evaluateInvariants(payload).find((item) => item.id === 'item-72548-quarantined')
    expect(result?.ok).toBe(false)
    expect(result?.actual).toContain('隔离清单中没有')
  })

  it('fails when a candidate id is dropped from an ambiguous skill name', () => {
    const payload = clone()
    payload.ambiguous_skill_names = payload.ambiguous_skill_names.filter(
      (row) => !(row.skill_name_raw === '高級命中' && String(row.skill_id) === '255'),
    )
    const result = evaluateInvariants(payload).find((item) => item.id === 'ambiguous-229-255')
    expect(result?.ok).toBe(false)
    expect(result?.actual).toBe('229')
  })

  it('fails when a missing aptitude becomes zero-filled or disappears', () => {
    const payload = clone()
    payload.missing_aptitudes = payload.missing_aptitudes.filter((row) => row.client_shape_id !== '3010')
    const result = evaluateInvariants(payload).find((item) => item.id === 'aptitude-missing-3010')
    expect(result?.ok).toBe(false)
  })
})
