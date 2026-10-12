/**
 * Domain-layer tests: the composition the pages rely on, driven by Agent H's
 * real captured responses.
 *
 * Everything asserted here (quarantine keys, missing aptitudes, ambiguous
 * candidate ids, zero-NPC counts, agreement categories) is read back from
 * `fixtures/h_api/` - the values are the backend's, not the test's opinion. The
 * two synthetic stubs at the end only exercise *client-side* loop behaviour
 * (multi-page follow-through and the size guard); they are labelled as such.
 */
import { describe, expect, it, vi } from 'vitest'
import {
  countRecords,
  decodeCp950,
  evidenceName,
  fetchAllRecords,
  getAptitudeStatus,
  getPetDetail,
  getSkillDetail,
  groupAmbiguousSkills,
  loadAgreement,
  loadAnomalyBoard,
  loadMissingAptitudes,
  loadNpcSourcePage,
} from './reviewApi'
import { captureBody, installCaptureFetch, jsonResponse } from '../test/hApiReplay'

describe('aptitude status comes from the backend, never from a default', () => {
  it('reports pet 2800 as quarantined with its evidence id', async () => {
    installCaptureFetch()
    const status = await getAptitudeStatus('2800')
    expect(status.status).toBe('quarantined')
    expect(status.reason).toContain('value_exceeds_named_maximum:法力資質')
    expect(status.evidence_id).toBe('2954:2800')
  })

  it('reports pet 3010 as missing in the source table', async () => {
    installCaptureFetch()
    const status = await getAptitudeStatus('3010')
    expect(status.status).toBe('missing_in_source_table')
    expect(status.reason).toBe('no_record_in_2954')
  })

  it('reports pet 4011 as present (a real row exists)', async () => {
    installCaptureFetch()
    const status = await getAptitudeStatus('4011')
    expect(status.status).toBe('present')
    expect(status.evidence_id).toBeNull()
  })

  it('lists exactly the three missing aptitudes with their reasons', async () => {
    installCaptureFetch()
    const missing = await loadMissingAptitudes()
    expect(missing.map((row) => [row.client_shape_id, row.reason])).toEqual([
      ['3010', 'no_record_in_2954'],
      ['4021', 'no_record_in_2954'],
      ['4022', 'no_record_in_2954'],
    ])
  })
})

describe('pet detail', () => {
  it('composes candidates, required skills and name matches for a quarantined pet', async () => {
    installCaptureFetch()
    const detail = await getPetDetail('2800')

    expect(detail.pet.name).toBe('機甲少女')
    expect(detail.pet.review_status).toBe('review_candidate_not_native_verified')
    // Quarantined: the UI gets no aptitude values at all (no zero fill, no 1700).
    expect(detail.aptitude).toBeNull()
    expect(detail.aptitude_status.status).toBe('quarantined')

    expect(detail.candidate_skills.map((skill) => [skill.sequence, skill.skill_name_raw])).toEqual([
      [0, '英勇對決'],
      [1, '強壯'],
      [2, '神跡'],
    ])
    expect(detail.candidate_skills[0].matches.map((match) => match.skill_id)).toEqual(['562'])
    expect(detail.candidate_skills[2].matches.map((match) => match.skill_id)).toEqual(['108'])
    expect(detail.required_skills).toEqual([])
  })

  it('keeps both candidate ids of an ambiguous name', async () => {
    installCaptureFetch()
    const detail = await getPetDetail('4011')

    expect(detail.pet.name).toBe('仙獸吉祥虎')
    expect(detail.aptitude_status.status).toBe('present')
    expect(detail.aptitude?.fields.map((field) => field.label)).toContain('法力資質')
    expect(detail.aptitude?.fields.find((field) => field.label === '法力資質')?.value).toBe('1900')

    const terminal = detail.candidate_skills.find((skill) => skill.skill_name_raw === '終級命中')
    expect(terminal?.matches.map((match) => match.skill_id)).toEqual(['329', '355'])
    expect(terminal?.matches.every((match) => match.ambiguous === true)).toBe(true)
  })

  it('follows every page of a candidate list instead of trusting page 1', async () => {
    // Synthetic stub: real capture rows, but the first page only holds one row.
    const candidates = captureBody('candidates_4011')
    const rows = candidates.records
    const stub = vi.fn(async (input: unknown) => {
      const url = String(input)
      if (url.includes('/pet_skill_candidates/records')) {
        const parsed = new URL(url, 'http://review.local')
        const offset = Number(parsed.searchParams.get('offset') ?? '0')
        const slice = rows.slice(offset, offset + 1)
        return jsonResponse(200, { ...candidates, offset, limit: 1, count: slice.length, records: slice })
      }
      return jsonResponse(404, { error: { code: 'TEST_STUB', message: `unexpected ${url}` } })
    })
    vi.stubGlobal('fetch', stub)

    const { records, pages } = await fetchAllRecords(
      'pet_skill_candidates',
      { filters: { client_shape_id: '4011' }, sortBy: 'sequence', order: 'asc' },
    )

    expect(pages).toBeGreaterThan(1)
    expect(records.map((record) => record.skill_name_raw)).toEqual([
      '新月獠牙',
      '終級命中',
      '終級神跡',
      '終級強力',
    ])
    const offsets = stub.mock.calls.map(
      (call) => Number(new URL(String(call[0]), 'http://review.local').searchParams.get('offset')),
    )
    expect(offsets).toEqual([0, 1, 2, 3])
  })

  it('refuses to return a truncated list when the result set exceeds the cap', async () => {
    // Synthetic stub: an endless 500-row page, so the safety valve must fire.
    const stub = vi.fn(async (input: unknown) => {
      const parsed = new URL(String(input), 'http://review.local')
      const offset = Number(parsed.searchParams.get('offset') ?? '0')
      const records = Array.from({ length: 500 }, (_, index) => ({ _pk: `${offset + index}` }))
      return jsonResponse(200, {
        dataset: 'synthetic',
        total: 999999,
        offset,
        limit: 500,
        count: records.length,
        records,
      })
    })
    vi.stubGlobal('fetch', stub)

    await expect(fetchAllRecords('synthetic', {})).rejects.toMatchObject({
      code: 'RESULT_SET_TOO_LARGE',
    })
  })
})

describe('skill detail and overwrite evidence', () => {
  it('decodes the old/new name from the raw byte evidence', async () => {
    installCaptureFetch()
    const detail = await getSkillDetail('4573')

    expect(detail.skill.name).toBe('地魔返生術')
    expect(detail.skill.description_raw).toBe('對隊友使用，使其起死回生，並恢復大量氣血')
    expect(detail.overwrites).toHaveLength(1)

    const overwrite = detail.overwrites[0]
    expect(overwrite.write_order).toBe(352)
    expect(overwrite.code_offset).toBe(22409)
    // The evidence records the write itself: 天魔返生術 -> 地魔返生術, and the
    // dataset row already carries the new value (no old value lost).
    expect(overwrite.old_name).toBe('天魔返生術')
    expect(overwrite.new_name).toBe('地魔返生術')
    expect(overwrite.identical_values).toBe(false)
    // The raw evidence is kept as it arrived, for the "raw bytes" panel.
    expect(JSON.stringify(overwrite.old_value)).toContain('bytes_hex')
    expect(detail.name_matches).toEqual([])
  })

  it('decodes CP950 bytes strictly and never invents a name', () => {
    expect(decodeCp950('a4d1c55daaf0a5cdb34e')).toBe('天魔返生術')
    // An odd byte run is not a name: the UI falls back to showing raw hex.
    expect(decodeCp950('a4d1c')).toBeNull()
    expect(decodeCp950('zz')).toBeNull()
    expect(evidenceName({ dict: [[{ bytes_hex: '6e616d65' }, { bytes_hex: 'a4d1c55daaf0a5cdb34e' }]] })).toBe(
      '天魔返生術',
    )
    expect(evidenceName({ dict: [[{ bytes_hex: '6e616d65' }, 1]] })).toBeNull()
  })
})

describe('anomaly board', () => {
  it('collects quarantine, missing aptitudes, ambiguous names and overwrites', async () => {
    installCaptureFetch()
    const board = await loadAnomalyBoard()

    expect(board.batch.batch).toBe('batch_001')
    expect(board.batch.native_loader_confirmed).toBe(false)

    expect(board.quarantine_total).toBe(4)
    expect(board.quarantine.map((entry) => entry.record_key)).toEqual(['72548', '2800', '719', '4406'])
    const itemQuarantine = board.quarantine.find((entry) => entry.record_key === '72548')
    expect(itemQuarantine?.entry_index).toBe(1945)
    expect(itemQuarantine?.reasons).toContain('invalid_cp950_source_name_bytes_preserved')
    expect(JSON.stringify(itemQuarantine?.value_under_applied_profile)).toContain('c2f9a448a7a4c34dc5e9c5e784')

    expect(board.missing_aptitudes.map((row) => row.client_shape_id)).toEqual(['3010', '4021', '4022'])
    expect(board.ambiguous_skill_names.map((group) => [group.skill_name_raw, group.ids])).toEqual([
      ['終級命中', ['329', '355']],
      ['高級命中', ['229', '255']],
    ])
    expect(board.overwrites_total).toBe(9)
    expect(board.skill_overwrites).toHaveLength(9)
    expect(board.skill_overwrites[0].key).toBe(4573)
  })

  it('groups every candidate id of a name without dropping one', () => {
    const groups = groupAmbiguousSkills(captureBody('ambiguous_skills'))
    const byName = new Map(groups.map((group) => [group.skill_name_raw, group.ids]))
    expect(byName.get('高級命中')).toEqual(['229', '255'])
    expect(byName.get('終級命中')).toEqual(['329', '355'])
    expect(byName.get('高級命中')).toHaveLength(2)
  })
})

describe('map / NPC sources stay separate and complete', () => {
  it('reports per-source totals and zero-NPC counts from the backend itself', async () => {
    installCaptureFetch()
    const pos2601 = await loadNpcSourcePage('npcposdata_records', { page: 1, pageSize: 25 })
    expect(pos2601.envelope.total).toBe(1335)
    expect(pos2601.envelope.records).toHaveLength(25)
    expect(pos2601.zeroNpcIdTotal).toBe(632)
    expect(pos2601.meta?.source_entry).toBe(2601)

    const pos2804 = await loadNpcSourcePage('minimapnpcpos_pos_records', { page: 1, pageSize: 25 })
    expect(pos2804.envelope.total).toBe(1344)
    expect(pos2804.zeroNpcIdTotal).toBe(631)
    expect(pos2804.meta?.source_entry).toBe(2804)

    // The two sources have different columns: nothing was merged.
    expect(Object.keys(pos2601.envelope.records[0])).not.toContain('scene_display_name')
    expect(Object.keys(pos2804.envelope.records[0])).toContain('scene_display_name')
  })

  it('counts agreement categories over the whole dataset, not one page', async () => {
    installCaptureFetch()
    const view = await loadAgreement({ page: 1, pageSize: 25 })

    expect(view.envelope.records).toHaveLength(25)
    expect(view.total).toBe(677)
    expect(view.counts).toEqual({
      identical_sequence: 647,
      only_in_minimapnpcpos_2804: 12,
      identical_multiset_different_order: 9,
      content_difference: 8,
      only_in_npcposdata_2601: 1,
    })
    const sum = Object.values(view.counts).reduce((total, value) => total + value, 0)
    expect(sum).toBe(view.total)
  })

  it('counts a filtered set through the backend total, not by downloading rows', async () => {
    installCaptureFetch()
    await expect(countRecords('npcposdata_records', { npcid: 0 })).resolves.toBe(632)
  })
})
