import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { installCaptureFetch } from './test/hApiReplay'
import { renderApp } from './test/renderApp'

const LONG = { timeout: 4000 }

const FORBIDDEN_BUTTON = /删除|编辑|保存|导入|发布|新增|新增记录|提交|撤回|覆盖写入/

const PAGE_PATHS: Array<[string, string]> = [
  ['/items', '道具'],
  ['/pets', '宠物'],
  ['/skills', '技能'],
  ['/maps', '地图 / NPC'],
  ['/anomalies', '异常与证据'],
]

describe('review browser shell', () => {
  it('always shows the review-candidate notice and never a "native verified" claim', async () => {
    installCaptureFetch()
    renderApp('/')

    expect(screen.getByTestId('review-notice').textContent).toContain('复核候选，非正式规则')
    expect(screen.queryByText(/原生已确认/)).toBeNull()
    // Fixture mode is off by default: the banner only appears in that explicit mode.
    expect(screen.queryByTestId('fixture-banner')).toBeNull()
  })

  it('navigates between the six review pages against the real API', async () => {
    const { calls } = installCaptureFetch()
    const user = userEvent.setup()
    renderApp('/')

    await screen.findByTestId('batch-tables', {}, LONG)

    for (const [path, label] of PAGE_PATHS) {
      await user.click(screen.getByRole('link', { name: label }))
      expect(await screen.findByTestId(`page-${path.slice(1)}`, {}, LONG)).toBeInTheDocument()
    }

    // Every call went to the review API prefix, none to the fixture server.
    expect(calls.every((url) => url.startsWith('/api/v1/review/'))).toBe(true)
    expect(calls.length).toBeGreaterThan(10)
  })

  it('opens a linked skill from a pet candidate and keeps both candidate ids reachable', async () => {
    installCaptureFetch()
    const user = userEvent.setup()
    renderApp('/pets/4011')

    const candidates = await screen.findByTestId('candidate-skills', {}, LONG)
    const links = within(candidates).getAllByRole('link')
    const ids = links.map((link) => link.textContent)
    expect(ids).toContain('329')
    expect(ids).toContain('355')

    await user.click(links[ids.indexOf('557')])
    const detail = await screen.findByTestId('skill-detail', {}, LONG)
    expect(window.location.pathname).toBe('/skills/557')
    await within(detail).findByTestId('overwrite-none', {}, LONG)
  })

  it('offers no editing, deleting, importing or publishing action anywhere', async () => {
    installCaptureFetch()
    const user = userEvent.setup()
    renderApp('/')
    await screen.findByTestId('batch-tables', {}, LONG)

    for (const [path, label] of PAGE_PATHS) {
      await user.click(screen.getByRole('link', { name: label }))
      await screen.findByTestId(`page-${path.slice(1)}`, {}, LONG)
      for (const button of screen.queryAllByRole('button')) {
        expect(button.textContent ?? '').not.toMatch(FORBIDDEN_BUTTON)
      }
      expect(screen.queryByRole('textbox', { name: FORBIDDEN_BUTTON })).toBeNull()
      // Tables only: no contenteditable inputs, file pickers or textareas.
      expect(document.querySelectorAll('textarea, input[type="file"]')).toHaveLength(0)
    }
  })

  it('keeps table cells labelled for the narrow-screen stacked layout', async () => {
    installCaptureFetch()
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

  it('falls back to the overview for an unknown path instead of rendering nothing', async () => {
    installCaptureFetch()
    renderApp('/does-not-exist')

    expect(await screen.findByTestId('page-overview', {}, LONG)).toBeInTheDocument()
  })
})
