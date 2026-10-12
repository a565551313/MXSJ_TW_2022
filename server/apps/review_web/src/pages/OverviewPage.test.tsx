import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { renderApp } from '../test/renderApp'
import { installFixtureFetch, installNetworkFailure, jsonResponse } from '../test/fakeApi'

const LONG = { timeout: 4000 }

describe('batch overview page', () => {
  it('shows the review-candidate notice on every page', async () => {
    installFixtureFetch()
    renderApp('/')

    const notice = screen.getByTestId('review-notice')
    expect(notice.textContent).toContain('复核候选，非正式规则')
    expect(notice.textContent).toContain('不是')
    expect(await screen.findByTestId('batch-tables', {}, LONG)).toBeInTheDocument()
  })

  it('takes table counts, checks and quarantine figures from the API', async () => {
    installFixtureFetch()
    renderApp('/')

    const table = await screen.findByTestId('batch-tables', {}, LONG)
    const rows = within(table).getAllByRole('row')
    // header + 4 source tables
    expect(rows).toHaveLength(5)
    expect(table.textContent).toContain('6,851')
    expect(table.textContent).toContain('6,852')

    const checks = screen.getByTestId('checks-list')
    expect(checks.textContent).toContain('csv_round_trip')
    expect(within(checks).getAllByText('pass')).toHaveLength(5)

    const counters = screen.getByTestId('counter-grid')
    expect(counters.textContent).toContain('隔离记录数')
    expect(counters.textContent).toContain('资质缺失数')
    expect(counters.textContent).toContain('quarantined_record_count')

    const ambiguous = screen.getByTestId('ambiguous-names')
    expect(ambiguous.textContent).toContain('高級命中')
    expect(ambiguous.textContent).toContain('ID 229')
    expect(ambiguous.textContent).toContain('ID 255')
  })

  it('does not hardcode a counter that the API omits', async () => {
    installFixtureFetch({
      override: (url) =>
        url === '/api/v1/review/batch'
          ? jsonResponse(200, {
              batch_id: 'batch_001',
              status: 'review_candidate_not_native_verified',
              native_verified: false,
              tables: [],
              checks: {},
              counters: { items: 6851, newly_added_api_counter: 7 },
            })
          : null,
    })
    renderApp('/')

    const counters = await screen.findByTestId('counter-grid', {}, LONG)
    expect(counters.textContent).toContain('6,851')
    expect(counters.textContent).toContain('newly_added_api_counter')
    // No label was invented for the unknown counter.
    expect(counters.textContent).not.toContain('隔离记录数')
  })

  it('renders an error state when the batch endpoint fails', async () => {
    installNetworkFailure()
    renderApp('/')

    const error = await screen.findByTestId('error-state', {}, LONG)
    expect(error.textContent).toContain('/api/v1/review/batch')
    expect(screen.queryByTestId('batch-tables')).toBeNull()
  })
})
