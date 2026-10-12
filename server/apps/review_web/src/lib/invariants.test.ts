/**
 * Invariant panel against Agent H's real captured responses.
 *
 * The invariant *list* is a specification, but every verdict and every "actual"
 * string is computed from the API answer - so these tests both check the current
 * state (all pass) and prove the panel reacts when the backend stops honouring an
 * invariant.
 */
import { describe, expect, it } from 'vitest'
import type { AnomalyBoard } from '../api/reviewApi'
import { evaluateInvariants, REVIEW_INVARIANTS } from './invariants'
import { installCaptureFetch } from '../test/hApiReplay'
import { loadAnomalyBoard } from '../api/reviewApi'

async function realBoard(): Promise<AnomalyBoard> {
  installCaptureFetch()
  return loadAnomalyBoard()
}

function clone(board: AnomalyBoard): AnomalyBoard {
  return JSON.parse(JSON.stringify(board)) as AnomalyBoard
}

describe('review invariants', () => {
  it('passes on the real backend answers, with the real values shown', async () => {
    const board = await realBoard()
    const results = evaluateInvariants(board)

    expect(results).toHaveLength(REVIEW_INVARIANTS.length)
    expect(results.filter((result) => !result.ok)).toEqual([])

    const actualById = new Map(results.map((result) => [result.id, result.actual]))
    expect(actualById.get('ambiguous-229-255')).toBe('229 / 255')
    expect(actualById.get('ambiguous-329-355')).toBe('329 / 355')
    expect(actualById.get('item-72548-quarantined')).toContain('invalid_cp950_source_name_bytes_preserved')
    expect(actualById.get('aptitude-2800-quarantined')).toContain('value_exceeds_named_maximum:法力資質')
    expect(actualById.get('aptitude-missing-3010')).toBe('reason = no_record_in_2954')
  })

  it('fails loudly when the backend stops quarantining the item', async () => {
    const board = clone(await realBoard())
    board.quarantine = board.quarantine.filter((record) => record.record_key !== '72548')

    const result = evaluateInvariants(board).find((item) => item.id === 'item-72548-quarantined')
    expect(result?.ok).toBe(false)
    expect(result?.actual).toContain('隔离清单中没有')
  })

  it('fails when a candidate id is dropped from an ambiguous skill name', async () => {
    const board = clone(await realBoard())
    const group = board.ambiguous_skill_names.find((item) => item.skill_name_raw === '高級命中')
    if (group) group.ids = group.ids.filter((id) => id !== '255')

    const result = evaluateInvariants(board).find((item) => item.id === 'ambiguous-229-255')
    expect(result?.ok).toBe(false)
    expect(result?.actual).toBe('229')
  })

  it('fails when a missing aptitude turns up as a value or disappears', async () => {
    const board = clone(await realBoard())
    board.missing_aptitudes = board.missing_aptitudes.filter((row) => row.client_shape_id !== '3010')

    const result = evaluateInvariants(board).find((item) => item.id === 'aptitude-missing-3010')
    expect(result?.ok).toBe(false)
    expect(result?.actual).toContain('缺失清单中没有')
  })

  it('fails when a quarantined skill row appears in the skill dataset', async () => {
    const board = clone(await realBoard())
    board.quarantine = board.quarantine.filter((record) => record.record_key !== '4406')

    const result = evaluateInvariants(board).find((item) => item.id === 'skill-4406-quarantined')
    expect(result?.ok).toBe(false)
  })
})
