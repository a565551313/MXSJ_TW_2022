/**
 * Contract tests for the pagination translation.
 *
 * The reviewer's report was concrete: the old frontend sent
 * `?page=1&page_size=25` while Agent H serves `?offset=0&limit=25`. These tests
 * pin the translation and the parameter vocabulary, so the two pagination
 * dialects can never be mixed again.
 */
import { describe, expect, it } from 'vitest'
import {
  API_PATHS,
  DEFAULT_PAGE_SIZE,
  MAX_LIMIT,
  clampLimit,
  buildQuery,
  offsetToPage,
  pageToOffset,
} from './contract'

describe('pagination translation', () => {
  it('turns page 1 into offset 0', () => {
    expect(pageToOffset(1, 25)).toBe(0)
  })

  it('keeps page and offset in step for later pages', () => {
    for (const pageSize of [25, 50, 100, MAX_LIMIT]) {
      for (const page of [1, 2, 3, 17]) {
        expect(offsetToPage(pageToOffset(page, pageSize), pageSize)).toBe(page)
      }
    }
  })

  it('never emits page or page_size', () => {
    const suffix = buildQuery({ offset: 0, limit: DEFAULT_PAGE_SIZE, dataset: 'items' })
    expect(suffix).not.toContain('page=')
    expect(suffix).not.toContain('page_size=')
    expect(suffix).toContain('offset=0')
    expect(suffix).toContain(`limit=${DEFAULT_PAGE_SIZE}`)
  })

  it('clamps limit into the backend range and drops empty values', () => {
    expect(clampLimit(0)).toBe(1)
    expect(clampLimit(9999)).toBe(MAX_LIMIT)
    expect(clampLimit(25)).toBe(25)
    expect(buildQuery({ q: '', offset: 0 })).toBe('?offset=0')
  })

  it('builds the real dataset paths', () => {
    expect(API_PATHS.records('items')).toBe('/api/v1/review/datasets/items/records')
    expect(API_PATHS.record('items', '12')).toBe('/api/v1/review/datasets/items/records/12')
    expect(API_PATHS.record('minimapnpcpos_pos_records', '1001:0')).toBe(
      '/api/v1/review/datasets/minimapnpcpos_pos_records/records/1001%3A0',
    )
    expect(API_PATHS.quarantine).toBe('/api/v1/review/quarantine')
    expect(API_PATHS.ambiguousSkills).toBe('/api/v1/review/ambiguous-skills')
  })
})
