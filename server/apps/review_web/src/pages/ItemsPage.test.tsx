/**
 * Items page against Agent H's real captured responses.
 *
 * The numbers asserted here (total 6851, 鹿茸 twice, row order 11/12/9003) come
 * from the backend capture; nothing is read from the repository CSV.
 */
import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { captureBody, installCaptureFetch, installNetworkFailure, jsonResponse } from '../test/hApiReplay'
import { renderApp } from '../test/renderApp'

const LONG = { timeout: 4000 }

describe('items page', () => {
  it('lists real rows and paging information from the list envelope', async () => {
    const { calls } = installCaptureFetch()
    renderApp('/items')

    const table = await screen.findByTestId('items-table', {}, LONG)
    expect(within(table).getAllByTestId('item-id')).toHaveLength(25)
    expect(within(table).getByText('NPC呼叫器')).toBeInTheDocument()
    expect(within(table).getByText('鹿茸')).toBeInTheDocument()

    expect(screen.getByTestId('pagination').textContent).toContain('第 1 / 275 页')
    expect(screen.getByTestId('pagination').textContent).toContain('共 6,851 条')

    expect(calls[0]).toContain('/api/v1/review/datasets/items/records?offset=0&limit=25')
    expect(calls[0]).not.toContain('page=')
  })

  it('searches through the backend and shows both 鹿茸 rows', async () => {
    const { calls } = installCaptureFetch()
    const user = userEvent.setup()
    renderApp('/items')

    await screen.findByTestId('items-table', {}, LONG)
    await user.type(screen.getByLabelText('搜索道具'), '鹿茸')

    await waitFor(
      () => expect(calls.some((url) => url.includes('q=%E9%B9%BF%E8%8C%B8'))).toBe(true),
      LONG,
    )

    await waitFor(() => {
      const rows = within(screen.getByTestId('items-table')).getAllByTestId('item-id')
      expect(rows.map((row) => row.textContent)).toEqual(['12', '21302'])
    }, LONG)

    // The search request keeps offset/limit pagination and adds q only.
    const searchCall = calls.find((url) => url.includes('q=%E9%B9%BF%E8%8C%B8')) as string
    expect(searchCall).toContain('offset=0')
    expect(searchCall).toContain('limit=25')
  })

  it('pages through the real rows without collapsing or reordering them', async () => {
    const { calls } = installCaptureFetch()
    const user = userEvent.setup()
    renderApp('/items')

    const firstPage = await screen.findByTestId('items-table', {}, LONG)
    const firstIds = within(firstPage)
      .getAllByTestId('item-id')
      .map((cell) => cell.textContent)
    expect(firstIds[0]).toBe('11')
    expect(firstIds[24]).toBe('10010')

    await user.click(screen.getByRole('button', { name: '下一页' }))

    await waitFor(() => {
      expect(calls.some((url) => url.includes('offset=25&limit=25'))).toBe(true)
    }, LONG)
    await waitFor(() => {
      const ids = within(screen.getByTestId('items-table'))
        .getAllByTestId('item-id')
        .map((cell) => cell.textContent)
      expect(ids[0]).toBe('10011')
      expect(ids).not.toContain('11')
    }, LONG)
  })

  it('shows a row detail with the raw description text and the mapping id, not a fake image', async () => {
    installCaptureFetch()
    renderApp('/items/12')

    const detail = await screen.findByTestId('item-detail', {}, LONG)
    expect(within(detail).getByText('鹿茸')).toBeInTheDocument()
    // Source text stays raw: markers are displayed, never interpreted.
    expect(detail.textContent).toContain('#r【類型】藥品')
    expect(detail.textContent).toContain('21302')
    expect(detail.querySelector('img')).toBeNull()
  })

  it('reports a backend failure loudly instead of showing an empty table', async () => {
    installNetworkFailure()
    renderApp('/items')

    const panel = await screen.findByTestId('error-state', {}, LONG)
    expect(panel.textContent).toContain('无法连接复核 API')
    expect(screen.queryByTestId('items-table')).toBeNull()
    // No fallback to test data, and no "0 rows" story.
    expect(screen.queryByTestId('empty-state')).toBeNull()
  })

  it('reports a wrong-shaped 200 response as an interface-structure error', async () => {
    const envelope = captureBody('records_items_limit500') as Record<string, unknown>
    delete envelope.records
    delete envelope.count
    installCaptureFetch({ override: () => jsonResponse(200, envelope) })

    renderApp('/items')

    const panel = await screen.findByTestId('error-state', {}, LONG)
    expect(panel.textContent).toContain('接口结构错误')
    expect(screen.queryByTestId('items-table')).toBeNull()
    expect(panel.textContent).toContain('response.records')
  })
})
