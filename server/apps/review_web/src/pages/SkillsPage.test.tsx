import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { renderApp } from '../test/renderApp'
import { installFixtureFetch } from '../test/fakeApi'

const LONG = { timeout: 4000 }

describe('skills page', () => {
  it('searches skills and shows the source type code', async () => {
    installFixtureFetch()
    renderApp('/skills')

    const table = await screen.findByTestId('skills-table', {}, LONG)
    expect(within(table).getAllByTestId('skill-id').length).toBeGreaterThan(0)
    expect(screen.getByTestId('pagination').textContent).toContain('共 28 条')
  })

  it('displays descriptions and formulas as text without evaluating them', async () => {
    installFixtureFetch()
    renderApp('/skills/229')

    const detail = await screen.findByTestId('skill-detail', {}, LONG)
    const nameCell = detail.querySelector('.keyvalue__row dd [data-testid="safe-text"]')
    expect(nameCell?.textContent).toBe('高級命中')
    expect(detail.textContent).toContain('使用物理攻擊時，命中率提高10%')

    const formulas = within(detail).getAllByTestId('safe-formula')
    expect(formulas).toHaveLength(3)
    expect(formulas.map((node) => node.textContent)).toEqual(['0', '0', '0'])
    expect(detail.textContent).toContain('仅展示，不计算')
    expect(detail.querySelector('script')).toBeNull()
  })

  it('shows both IDs of an ambiguous name instead of picking one', async () => {
    installFixtureFetch()
    renderApp('/skills/229')

    const matches = await screen.findByTestId('skill-name-matches', {}, LONG)
    expect(matches.textContent).toContain('高級命中')
    expect(matches.textContent).toContain('ID 229')
    expect(matches.textContent).toContain('match_count 2')
    expect(within(matches).getByText(/同名多 ID（2 个候选）/)).toBeInTheDocument()
  })

  it('shows the overwrite summary and preserves the old value', async () => {
    installFixtureFetch()
    renderApp('/skills/4573')

    const panel = await screen.findByTestId('overwrite-panel', {}, LONG)
    expect(panel.textContent).toContain('天魔返生術')
    expect(panel.textContent).toContain('地魔返生術')
    expect(panel.textContent).toContain('值已改变')
    expect(panel.textContent).toContain('22409')
    expect(panel.textContent).toContain('352')
  })

  it('marks identical-value overwrites as evidence that is still kept', async () => {
    installFixtureFetch()
    renderApp('/skills/4574')

    const panel = await screen.findByTestId('overwrite-panel', {}, LONG)
    expect(panel.textContent).toContain('identical_values = true')
    expect(panel.textContent).toContain('不因值相同而删除证据')
  })

  it('states that a skill id outside the overwrite list has no overwrite entry', async () => {
    installFixtureFetch()
    renderApp('/skills/101')

    const detail = await screen.findByTestId('skill-detail', {}, LONG)
    expect(detail.textContent).toContain('不在 9 次重复键写入的覆盖清单中')
  })
})
