import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { renderApp } from '../test/renderApp'
import { installFixtureFetch, installNetworkFailure, jsonResponse } from '../test/fakeApi'

const LONG = { timeout: 4000 }

describe('items page', () => {
  it('lists items from the API and shows pagination counts from the response', async () => {
    installFixtureFetch()
    renderApp('/items')

    expect(screen.getByTestId('loading-state')).toBeInTheDocument()

    const table = await screen.findByTestId('items-table', {}, LONG)
    expect(within(table).getAllByTestId('item-id')).toHaveLength(25)
    expect(screen.getByTestId('pagination').textContent).toContain('第 1 / 3 页')
    expect(screen.getByTestId('pagination').textContent).toContain('共 69 条')
  })

  it('searches by name and by id against the API', async () => {
    const { calls } = installFixtureFetch()
    const user = userEvent.setup()
    renderApp('/items')

    await screen.findByTestId('items-table', {}, LONG)

    const waitForQuery = (fragment: string) =>
      waitFor(() => expect(calls.some((url) => url.includes(fragment))).toBe(true), LONG)

    await user.type(screen.getByLabelText('搜索道具'), '鹿茸')
    await waitForQuery('q=%E9%B9%BF%E8%8C%B8')
    await waitFor(() => {
      const table = screen.getByTestId('items-table')
      expect(within(table).getAllByTestId('item-id')).toHaveLength(1)
      expect(within(table).queryByText('鹿茸')).not.toBeNull()
    }, LONG)

    await user.clear(screen.getByLabelText('搜索道具'))
    await user.type(screen.getByLabelText('搜索道具'), '41052')
    await waitForQuery('q=41052')
    await waitFor(() => {
      const table = screen.getByTestId('items-table')
      expect(within(table).getAllByTestId('item-id')).toHaveLength(1)
      expect(within(table).queryByText('時空石')).not.toBeNull()
    }, LONG)
  })

  it('paginates without re-sorting or collapsing rows', async () => {
    installFixtureFetch()
    const user = userEvent.setup()
    renderApp('/items')

    const firstPage = await screen.findByTestId('items-table', {}, LONG)
    const firstRowOfPageOne = within(firstPage).getAllByTestId('item-id')[0].textContent

    await user.click(screen.getByRole('button', { name: '下一页' }))

    const secondPage = await screen.findByTestId('items-table', {}, LONG)
    expect(screen.getByTestId('pagination').textContent).toContain('第 2 / 3 页')
    expect(within(secondPage).getAllByTestId('item-id')[0].textContent).not.toBe(firstRowOfPageOne)
  })

  it('shows an empty state for a query with no matches', async () => {
    installFixtureFetch()
    const user = userEvent.setup()
    renderApp('/items')

    await screen.findByTestId('items-table', {}, LONG)
    await user.type(screen.getByLabelText('搜索道具'), 'ZZZ-不存在')

    expect(await screen.findByTestId('empty-state', {}, LONG)).toBeInTheDocument()
    expect(screen.getByText('没有符合条件的记录。')).toBeInTheDocument()
  })

  it('renders item detail with raw description, category code and image mapping', async () => {
    installFixtureFetch()
    renderApp('/items/12')

    const detail = await screen.findByTestId('item-detail', {}, LONG)
    expect(within(detail).getByText('鹿茸')).toBeInTheDocument()
    expect(within(detail).getByText(/雄鹿額部生長出來的尚未骨化的嫩角/)).toBeInTheDocument()

    const body = detail.textContent ?? ''
    expect(body).toContain('category_code_raw')
    expect(body).toContain('原始整数，未解释为业务类别')
    expect(body).toContain('image_id = 21302')
    expect(body).toContain('显式映射')
    expect(body).toContain('本轮没有图片资源 API')

    // No fabricated image preview is rendered.
    expect(detail.querySelector('img')).toBeNull()
  })

  it('describes the fallback mapping when there is no explicit SHAPETABLE entry', async () => {
    installFixtureFetch()
    renderApp('/items/11')
    const detail = await screen.findByTestId('item-detail', {}, LONG)
    expect(within(detail).getByText('回退映射')).toBeInTheDocument()
    expect(detail.textContent).toContain('可以呼叫各種功能NPC以方便測試#r【測試專用物品】'.slice(0, 10))
  })

  it('shows an API error instead of falling back to fixtures', async () => {
    installNetworkFailure()
    renderApp('/items')

    const error = await screen.findByTestId('error-state', {}, LONG)
    expect(error.textContent).toContain('无法连接复核 API')
    expect(error.textContent).toContain('/api/v1/review/items')
    expect(screen.queryByTestId('items-table')).toBeNull()
  })

  it('surfaces a 404 for an unknown item id', async () => {
    installFixtureFetch({
      override: (url) =>
        url.startsWith('/api/v1/review/items/') && !url.includes('?')
          ? jsonResponse(404, { error: { code: 'NOT_FOUND', message: '道具 999999 不存在' } })
          : null,
    })
    renderApp('/items/999999')

    const error = await screen.findByTestId('error-state', {}, LONG)
    expect(error.textContent).toContain('道具 999999 不存在')
    expect(error.textContent).toContain('404')
  })

  it('retries the request when the retry button is pressed', async () => {
    const user = userEvent.setup()
    let attempt = 0
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: unknown) => {
        const url = String(input)
        attempt += 1
        if (attempt === 1) throw new TypeError('Failed to fetch')
        const { handleRequest, loadFixture } = await import('../../fixtures/contractHandler.mjs')
        const parsed = new URL(url, 'http://review.local')
        const { status, body } = handleRequest(loadFixture(), parsed.pathname, parsed.searchParams)
        return jsonResponse(status, body)
      }),
    )

    renderApp('/items')
    await screen.findByTestId('error-state', {}, LONG)
    await user.click(screen.getByTestId('retry-button'))

    expect(await screen.findByTestId('items-table', {}, LONG)).toBeInTheDocument()
  })
})
