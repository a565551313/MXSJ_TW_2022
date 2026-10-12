/**
 * Pets page against Agent H's real captured responses.
 *
 * Key semantics pinned here: a quarantined aptitude row shows *no* values (and
 * certainly not an unapproved 1700), a pet missing from the aptitude table is
 * shown as missing rather than 0, and an ambiguous skill name keeps every
 * candidate id.
 */
import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { installCaptureFetch } from '../test/hApiReplay'
import { renderApp } from '../test/renderApp'

const LONG = { timeout: 4000 }

async function jumpToPage(user: ReturnType<typeof userEvent.setup>, page: number) {
  await user.clear(screen.getByLabelText('跳至'))
  await user.type(screen.getByLabelText('跳至'), String(page))
  await user.click(screen.getByRole('button', { name: '跳转' }))
}

describe('pets page', () => {
  it('lists the real pet main table with paging totals', async () => {
    const { calls } = installCaptureFetch()
    renderApp('/pets')

    const table = await screen.findByTestId('pets-table', {}, LONG)
    const ids = within(table)
      .getAllByTestId('pet-id')
      .map((cell) => cell.textContent)
    expect(ids).toHaveLength(25)
    expect(ids[0]).toBe('2010')
    expect(within(table).getByText('毛草團')).toBeInTheDocument()

    expect(screen.getByTestId('pagination').textContent).toContain('第 1 / 6 页')
    expect(screen.getByTestId('pagination').textContent).toContain('共 135 条')

    expect(calls).toContain('/api/v1/review/datasets/pets/records?offset=0&limit=25')
    // The status column comes from three bulk requests, never 3 x 25 calls.
    expect(calls).toContain('/api/v1/review/quarantine?entry_index=2954&offset=0&limit=500')
    expect(calls).toContain('/api/v1/review/missing-aptitudes')
    expect(calls.filter((url) => url.includes('/pet_aptitudes/records')).length).toBeLessThanOrEqual(2)
    expect(calls).toHaveLength(4)
  })

  it('marks the quarantined and the missing pet on the page they appear', async () => {
    installCaptureFetch()
    const user = userEvent.setup()
    renderApp('/pets')

    await screen.findByTestId('pets-table', {}, LONG)
    await jumpToPage(user, 4)

    await waitFor(() => {
      const ids = within(screen.getByTestId('pets-table'))
        .getAllByTestId('pet-id')
        .map((cell) => cell.textContent)
      expect(ids).toContain('2800')
      expect(ids).toContain('3010')
    }, LONG)

    const row2800 = screen.getByText('2800').closest('tr') as HTMLElement
    const row3010 = screen.getByText('3010').closest('tr') as HTMLElement
    expect(within(row2800).getByText('资质隔离')).toBeInTheDocument()
    expect(within(row3010).getByText('资质缺失')).toBeInTheDocument()
    expect(within(row2800).queryByText('资质存在')).toBeNull()
    expect(within(row3010).queryByText('资质存在')).toBeNull()
  })

  it('hides the values of a quarantined aptitude row instead of showing candidates', async () => {
    installCaptureFetch()
    renderApp('/pets/2800')

    const detail = await screen.findByTestId('pet-detail', {}, LONG)
    const quarantine = await within(detail).findByTestId('aptitude-quarantined', {}, LONG)
    expect(quarantine.textContent).toContain('value_exceeds_named_maximum:法力資質')
    expect(quarantine.textContent).toContain('不展示尚未批准的候选值')

    expect(within(detail).queryByTestId('aptitude-table')).toBeNull()
    expect(detail.textContent).not.toContain('1700')
    expect(within(detail).queryByText('法力資質')).toBeNull()
  })

  it('shows a missing aptitude record as missing, never as zero', async () => {
    installCaptureFetch()
    renderApp('/pets/3010')

    const detail = await screen.findByTestId('pet-detail', {}, LONG)
    const missing = await within(detail).findByTestId('aptitude-missing', {}, LONG)
    expect(missing.textContent).toContain('no_record_in_2954')
    expect(missing.textContent).toContain('本页不会把它显示为 0')
    expect(within(detail).queryByTestId('aptitude-table')).toBeNull()
  })

  it('lists candidates in sequence order and keeps both ids of an ambiguous name', async () => {
    installCaptureFetch()
    renderApp('/pets/4011')

    const detail = await screen.findByTestId('pet-detail', {}, LONG)
    await within(detail).findByTestId('aptitude-table', {}, LONG)

    const candidates = within(detail).getByTestId('candidate-skills')
    const items = within(candidates).getAllByRole('listitem')
    expect(items.map((item) => item.textContent?.replace(/\s+/g, ''))).toEqual([
      'sequence0新月獠牙候选技能ID：557',
      'sequence1終級命中候选技能ID：329355同名多ID（2个候选）全部候选都保留（match_count=2），未默认选择第一个。',
      'sequence2終級神跡候选技能ID：308',
      'sequence3終級強力候选技能ID：319',
    ])

    // The aptitude row for this pet is real and shows source column names.
    const aptitude = within(detail).getByTestId('aptitude-table')
    expect(within(aptitude).getByText('法力資質')).toBeInTheDocument()
    expect(aptitude.textContent).toContain('1900')

    const required = within(detail).getByTestId('required-skills-empty')
    expect(required.textContent).toContain('返回 0 条')
  })

  it('asks the backend for the whole related set, ordered, not just page 1', async () => {
    const { calls } = installCaptureFetch()
    renderApp('/pets/4011')

    await screen.findByTestId('pet-detail', {}, LONG)
    await waitFor(() => {
      expect(
        calls.some((url) =>
          url.includes(
            '/pet_skill_candidates/records?offset=0&limit=500&sort_by=sequence&order=asc&client_shape_id=4011',
          ),
        ),
      ).toBe(true)
    }, LONG)
    expect(
      calls.some((url) => url.includes('/pet_required_skills/records?offset=0&limit=500&client_shape_id=4011')),
    ).toBe(true)
    expect(calls.some((url) => url.includes('/pets/records/4011'))).toBe(true)
  })
})
