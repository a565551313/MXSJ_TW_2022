import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { renderApp } from './test/renderApp'
import { installFixtureFetch } from './test/fakeApi'

const LONG = { timeout: 4000 }

const FORBIDDEN_BUTTON = /删除|编辑|保存|导入|发布|新增|新增记录|提交|撤回|覆盖写入/

describe('review browser shell', () => {
  it('always shows the review-candidate notice and never a "native verified" claim', async () => {
    installFixtureFetch()
    renderApp('/')

    expect(screen.getByTestId('review-notice').textContent).toContain('复核候选，非正式规则')
    expect(screen.queryByText(/原生已确认/)).toBeNull()
    expect(screen.queryByTestId('fixture-banner')).toBeNull()
  })

  it('navigates between the six review pages', async () => {
    installFixtureFetch()
    const user = userEvent.setup()
    renderApp('/')

    await screen.findByTestId('batch-tables', {}, LONG)

    await user.click(screen.getByRole('link', { name: '道具' }))
    expect(await screen.findByTestId('page-items', {}, LONG)).toBeInTheDocument()

    await user.click(screen.getByRole('link', { name: '宠物' }))
    expect(await screen.findByTestId('page-pets', {}, LONG)).toBeInTheDocument()

    await user.click(screen.getByRole('link', { name: '技能' }))
    expect(await screen.findByTestId('page-skills', {}, LONG)).toBeInTheDocument()

    await user.click(screen.getByRole('link', { name: '地图 / NPC' }))
    expect(await screen.findByTestId('page-maps', {}, LONG)).toBeInTheDocument()

    await user.click(screen.getByRole('link', { name: '异常与证据' }))
    expect(await screen.findByTestId('page-anomalies', {}, LONG)).toBeInTheDocument()
  })

  it('opens a linked skill from a pet candidate and keeps both candidate ids reachable', async () => {
    installFixtureFetch()
    const user = userEvent.setup()
    renderApp('/pets/2790')

    const candidates = await screen.findByTestId('candidate-skills', {}, LONG)
    const links = within(candidates).getAllByRole('link', { name: '255' })
    await user.click(links[0])

    const detail = await screen.findByTestId('skill-detail', {}, LONG)
    expect(detail.textContent).toContain('高級命中')
    expect(window.location.pathname).toBe('/skills/255')
  })

  it('offers no editing, deleting, importing or publishing action anywhere', async () => {
    installFixtureFetch()
    const user = userEvent.setup()
    renderApp('/')
    await screen.findByTestId('batch-tables', {}, LONG)

    const paths = ['/items', '/pets', '/skills', '/maps', '/anomalies']
    for (const path of paths) {
      await user.click(screen.getByRole('link', { name: navLabelFor(path) }))
      await screen.findByTestId('page-' + path.slice(1), {}, LONG)
      for (const button of screen.queryAllByRole('button')) {
        expect(button.textContent ?? '').not.toMatch(FORBIDDEN_BUTTON)
      }
      expect(screen.queryByRole('textbox', { name: FORBIDDEN_BUTTON })).toBeNull()
    }
  })

  it('keeps table cells labelled for the narrow-screen stacked layout', async () => {
    installFixtureFetch()
    renderApp('/items')

    const table = await screen.findByTestId('items-table', {}, LONG)
    const headerCells = within(table).getAllByRole('columnheader').map((cell) => cell.textContent)
    const bodyCells = within(table).getAllByRole('cell')
    expect(bodyCells.length).toBeGreaterThan(0)
    for (const cell of bodyCells) {
      expect(cell.getAttribute('data-label')).toBeTruthy()
      expect(headerCells).toContain(cell.getAttribute('data-label'))
    }
  })
})

function navLabelFor(path: string): string {
  switch (path) {
    case '/items':
      return '道具'
    case '/pets':
      return '宠物'
    case '/skills':
      return '技能'
    case '/maps':
      return '地图 / NPC'
    default:
      return '异常与证据'
  }
}
