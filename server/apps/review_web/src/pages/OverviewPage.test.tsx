/**
 * Batch overview against Agent H's real captured responses.
 *
 * The home page is the one that used to white-screen (`tables_summary` missing,
 * `Cannot read properties of undefined (reading 'length')`), so these tests pin
 * both the real counters and the failure behaviour.
 */
import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { captureBody, installCaptureFetch, installNetworkFailure, jsonResponse } from '../test/hApiReplay'
import { renderApp } from '../test/renderApp'

const LONG = { timeout: 4000 }

function counter(label: string): string {
  const grid = screen.getByTestId('counter-grid')
  const cells = within(grid).getAllByText(label)
  const cell = cells[0].closest('.counter') as HTMLElement
  return (within(cell).getByText(/[\d,]+|（API 未提供）/).textContent ?? '').trim()
}

describe('batch overview page', () => {
  it('renders the real counters, checks and quarantine totals', async () => {
    const { calls } = installCaptureFetch()
    renderApp('/')

    const page = await screen.findByTestId('page-overview', {}, LONG)
    await waitFor(() => expect(within(page).getByTestId('counter-grid')).toBeInTheDocument(), LONG)

    expect(counter('资质缺失数')).toBe('3')
    expect(counter('隔离记录数')).toBe('4')
    expect(counter('技能唯一 ID 数')).toBe('581')
    expect(counter('技能字典写入次数')).toBe('590')
    expect(counter('重复键覆盖次数')).toBe('9')
    expect(counter('数据集数')).toBe('17')
    expect(counter('数据集记录合计')).toBe('12,202')

    // The four source tables with their real counts.
    const tables = within(page).getByTestId('batch-tables')
    expect(tables.textContent).toContain('6,852')
    expect(tables.textContent).toContain('6,851')
    expect(tables.textContent).toContain('132')
    expect(tables.textContent).toContain('581')
    expect(within(tables).getAllByTestId('table-dataset').length).toBe(4)

    const checks = within(page).getByTestId('checks-list')
    expect(checks.textContent).toContain('csv_round_trip')
    expect(checks.textContent).toContain('pet_aptitude_foreign_keys')
    expect(within(checks).getAllByText('pass')).toHaveLength(5)

    const ambiguous = within(page).getByTestId('ambiguous-names')
    expect(ambiguous.textContent).toContain('高級命中')
    expect(ambiguous.textContent).toContain('229')
    expect(ambiguous.textContent).toContain('255')
    expect(ambiguous.textContent).toContain('329')
    expect(ambiguous.textContent).toContain('355')

    // No native verification is claimed anywhere on the page.
    expect(page.textContent).not.toContain('原生已确认')
    expect(calls).toContain('/api/v1/review/batch')
    expect(calls).toContain('/api/v1/review/health')
    expect(calls).toContain('/api/v1/review/datasets')
  })

  it('shows an interface-structure error instead of a blank page when the batch shape drifts', async () => {
    // The exact fiction the reviewer hit: batch_id / tables / counters instead of
    // batch / tables_summary / validation_summary.
    installCaptureFetch({
      override: (url) => {
        if (url.includes('/batch')) {
          return jsonResponse(200, {
            batch_id: 'batch_001',
            tables: [{ name: 'items', rows: 6851 }],
            counters: {},
            input_hashes: {},
          })
        }
        return null
      },
    })

    renderApp('/')

    const panel = await screen.findByTestId('error-state', {}, LONG)
    expect(panel.textContent).toContain('接口结构错误')
    expect(panel.textContent).toContain('response.tables_summary')
    expect(panel.textContent).toContain('不会把缺失字段补成空数组或 0')
    // The app shell is still there: no white screen.
    expect(screen.getAllByText('批次概览').length).toBeGreaterThan(0)
    expect(screen.getByTestId('review-notice')).toBeInTheDocument()
  })

  it('keeps the rest of the page alive when only one of the three calls fails', async () => {
    installCaptureFetch({
      override: (url) => (url.includes('/health') ? jsonResponse(500, { error: { code: 'BOOM', message: '健康检查失败' } }) : null),
    })

    renderApp('/')

    const page = await screen.findByTestId('page-overview', {}, LONG)
    await waitFor(() => expect(within(page).getByTestId('counter-grid')).toBeInTheDocument(), LONG)
    expect(counter('资质缺失数')).toBe('3')
    // Missing health data is reported as not provided, never as 0.
    expect(counter('数据集记录合计')).toBe('（API 未提供）')
  })

  it('shows a loud error when the API is unreachable', async () => {
    installNetworkFailure()
    renderApp('/')

    const panel = await screen.findByTestId('error-state', {}, LONG)
    expect(panel.textContent).toContain('无法连接复核 API')
    expect(screen.queryByTestId('counter-grid')).toBeNull()
  })

  it('does not fall back to the test captures when the live API breaks mid-response', async () => {
    const batch = captureBody('batch') as Record<string, unknown>
    batch.validation_summary = null
    installCaptureFetch({ override: (url) => (url.includes('/batch') ? jsonResponse(200, batch) : null) })

    renderApp('/')
    const panel = await screen.findByTestId('error-state', {}, LONG)
    expect(panel.textContent).toContain('接口结构错误')
    expect(panel.textContent).toContain('validation_summary')
  })
})
