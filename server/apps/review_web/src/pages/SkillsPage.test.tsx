/**
 * Skills page against Agent H's real captured responses.
 *
 * Pins: raw description text is shown verbatim (never interpreted), formulas are
 * displayed but not computed, and overwrite evidence names come from the raw
 * CP950 byte dicts (a byte run that does not decode stays raw hex).
 */
import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { installCaptureFetch } from '../test/hApiReplay'
import { renderApp } from '../test/renderApp'

const LONG = { timeout: 4000 }

describe('skills page', () => {
  it('lists the real skill rows with the dataset total', async () => {
    const { calls } = installCaptureFetch()
    renderApp('/skills')

    const table = await screen.findByTestId('skills-table', {}, LONG)
    const ids = within(table)
      .getAllByTestId('skill-id')
      .map((cell) => cell.textContent)
    expect(ids).toHaveLength(25)
    expect(ids[0]).toBe('101')
    expect(within(table).getByText('反擊')).toBeInTheDocument()
    expect(screen.getByTestId('pagination').textContent).toContain('共 579 条')
    expect(calls[0]).toContain('/api/v1/review/datasets/pet_skills/records?offset=0&limit=25')
  })

  it('searches an ambiguous name and keeps both rows', async () => {
    const { calls } = installCaptureFetch()
    const user = userEvent.setup()
    renderApp('/skills')

    await screen.findByTestId('skills-table', {}, LONG)
    await user.type(screen.getByLabelText('搜索技能'), '高級命中')

    await waitFor(() => {
      const ids = within(screen.getByTestId('skills-table'))
        .getAllByTestId('skill-id')
        .map((cell) => cell.textContent)
      expect(ids).toEqual(['229', '255'])
    }, LONG)
    expect(calls.some((url) => url.includes('q=%E9%AB%98%E7%B4%9A%E5%91%BD%E4%B8%AD'))).toBe(true)
  })

  it('shows description, non-computed formulas and overwrite evidence for a skill', async () => {
    installCaptureFetch()
    renderApp('/skills/4573')

    const detail = await screen.findByTestId('skill-detail', {}, LONG)

    // Raw source text, markers and all - no rich-text interpretation.
    expect(detail.textContent).toContain('對隊友使用，使其起死回生，並恢復大量氣血')
    // The dataset row name and the overwrite's new value both read 地魔返生術.
    expect(within(detail).getAllByText('地魔返生術').length).toBeGreaterThanOrEqual(2)

    // Formulas are shown as text; 0 stays 0 and is never evaluated.
    expect(detail.textContent).toContain('fpneed_raw')
    expect(within(detail).getAllByText('0').length).toBeGreaterThanOrEqual(3)

    const overwrite = within(detail).getByTestId('overwrite-panel')
    expect(overwrite.textContent).toContain('天魔返生術')
    expect(overwrite.textContent).toContain('地魔返生術')
    expect(within(overwrite).getByText('值已改变')).toBeInTheDocument()
    expect(overwrite.textContent).toContain('352')
    expect(overwrite.textContent).toContain('22409')

    // The raw byte evidence stays available verbatim.
    // Byte evidence is rendered byte by byte, so the old name stays readable as hex.
    expect(within(overwrite).getByTestId('overwrite-raw').textContent).toContain('a4 d1 c5 5d aa f0 a5 cd b3 4e')

    expect(within(detail).getByTestId('skill-name-matches-empty')).toBeInTheDocument()
  })

  it('shows a skill without overwrite evidence as such (not as an empty table)', async () => {
    installCaptureFetch()
    renderApp('/skills/101')

    const detail = await screen.findByTestId('skill-detail', {}, LONG)
    expect(within(detail).getByTestId('overwrite-none')).toBeInTheDocument()
  })

  it('lists the pets that reference a skill through the name-match dataset', async () => {
    installCaptureFetch()
    renderApp('/skills/229')

    const detail = await screen.findByTestId('skill-detail', {}, LONG)
    const matches = await within(detail).findByTestId('skill-name-matches', {}, LONG)
    expect(matches.textContent).toContain('高級命中')
    expect(matches.textContent).toContain('229')
  })
})
