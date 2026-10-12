/**
 * Anomaly / evidence page against Agent H's real captured responses.
 *
 * Pins the four anomaly sources separately (never merged into one story), the
 * raw byte evidence for the quarantined item name, and the invariant panel that
 * re-derives every verdict from the API answer.
 */
import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { captureBody, installCaptureFetch, jsonResponse } from '../test/hApiReplay'
import { renderApp } from '../test/renderApp'

const LONG = { timeout: 4000 }

describe('anomalies page', () => {
  it('lists all four quarantined records with their reasons and evidence ids', async () => {
    const { calls } = installCaptureFetch()
    renderApp('/anomalies')

    const page = await screen.findByTestId('page-anomalies', {}, LONG)
    const cards = within(page).getAllByTestId('quarantine-card')
    expect(cards).toHaveLength(4)

    const index = within(page).getByTestId('quarantine-index')
    expect(within(index).getAllByRole('link').map((link) => link.textContent)).toEqual([
      '1945:72548',
      '2954:2800',
      '3205:719',
      '3205:4406',
    ])

    const item = cards[0]
    expect(item.textContent).toContain('72548')
    expect(item.textContent).toContain('invalid_cp950_source_name_bytes_preserved')
    // The illegal source name bytes are preserved as hex.
    expect(within(item).getByTestId('raw-evidence').textContent).toContain('c2 f9 a4 48 a7 a4 c3 4d')

    expect(cards[1].textContent).toContain('2800')
    expect(cards[1].textContent).toContain('value_exceeds_named_maximum:法力資質')
    expect(cards[2].textContent).toContain('719')
    expect(cards[3].textContent).toContain('4406')

    expect(calls).toContain('/api/v1/review/quarantine?offset=0&limit=500')
    expect(calls).toContain('/api/v1/review/missing-aptitudes')
    expect(calls).toContain('/api/v1/review/ambiguous-skills')
    expect(calls).toContain('/api/v1/review/overwrites?offset=0&limit=500')
  })

  it('lists the missing aptitudes with reasons and links to the pets page', async () => {
    installCaptureFetch()
    renderApp('/anomalies')

    const page = await screen.findByTestId('page-anomalies', {}, LONG)
    const table = within(page).getByTestId('missing-aptitude-table')
    const rows = within(table).getAllByRole('row')
    expect(rows).toHaveLength(4) // header + 3
    expect(table.textContent).toContain('3010')
    expect(table.textContent).toContain('4021')
    expect(table.textContent).toContain('4022')
    expect(within(table).getAllByTestId('missing-reason').map((cell) => cell.textContent)).toEqual([
      'no_record_in_2954',
      'no_record_in_2954',
      'no_record_in_2954',
    ])
  })

  it('keeps every candidate id of an ambiguous skill name', async () => {
    installCaptureFetch()
    renderApp('/anomalies')

    const page = await screen.findByTestId('page-anomalies', {}, LONG)
    const list = within(page).getByTestId('ambiguous-list')
    const entries = within(list).getAllByRole('listitem')
    expect(entries.map((entry) => entry.textContent?.replace(/\s+/g, ''))).toEqual([
      '終級命中ID329ID355match_count2同名多ID（2个候选）',
      '高級命中ID229ID255match_count2同名多ID（2个候选）',
    ])
  })

  it('shows the overwrite evidence with names decoded from the raw bytes', async () => {
    installCaptureFetch()
    renderApp('/anomalies')

    const page = await screen.findByTestId('page-anomalies', {}, LONG)
    const table = within(page).getByTestId('overwrite-table')
    expect(within(table).getAllByRole('row')).toHaveLength(10) // header + 9

    // 4573 is the real write 天魔返生術 -> 地魔返生術.
    const row = within(table).getAllByRole('row')[1]
    expect(row.textContent).toContain('352')
    expect(row.textContent).toContain('22409')
    await waitFor(() => {
      const names = within(within(page).getByTestId('overwrite-table')).getAllByTestId('overwrite-names')[0]
      expect(names.textContent).toContain('天魔返生術')
      expect(names.textContent).toContain('地魔返生術')
    }, LONG)

    expect(page.textContent).toContain('接口 total 9 次写入')
  })

  it('re-derives every review invariant from the API answer', async () => {
    installCaptureFetch()
    renderApp('/anomalies')

    const page = await screen.findByTestId('page-anomalies', {}, LONG)
    const panel = within(page).getByTestId('invariant-panel')
    const verdicts = within(panel).getAllByTestId('invariant-verdict')
    expect(verdicts.length).toBeGreaterThanOrEqual(9)
    expect(verdicts.map((verdict) => verdict.textContent)).toEqual(
      verdicts.map(() => '通过'),
    )
    expect(panel.textContent).toContain('高級命中 保留全部候选 229 / 255')
    expect(panel.textContent).toContain('接口实际值：229 / 255')
    expect(panel.textContent).toContain('接口实际值：329 / 355')
  })

  it('reports a failed invariant instead of repeating the old story', async () => {
    const quarantine = captureBody('quarantine_all') as { records: Array<{ record_key: string }> }
    quarantine.records = quarantine.records.filter((record) => String(record.record_key) !== '72548')
    installCaptureFetch({
      override: (url) =>
        url.includes('/quarantine') ? jsonResponse(200, { total: 3, records: quarantine.records }) : null,
    })

    renderApp('/anomalies')

    const page = await screen.findByTestId('page-anomalies', {}, LONG)
    const panel = within(page).getByTestId('invariant-panel')
    await waitFor(() => {
      expect(within(panel).getAllByTestId('invariant-verdict').map((v) => v.textContent)).toContain('未通过')
    }, LONG)
    expect(panel.textContent).toContain('隔离清单中没有 1945 / 72548')
  })

  it('focuses the quarantine card named in the URL', async () => {
    installCaptureFetch()
    renderApp('/anomalies?focus=2954:2800')

    const page = await screen.findByTestId('page-anomalies', {}, LONG)
    const cards = within(page).getAllByTestId('quarantine-card')
    const focused = cards.filter((card) => card.className.includes('is-focused'))
    expect(focused).toHaveLength(1)
    expect(focused[0].getAttribute('data-anomaly-id')).toBe('2954:2800')
    expect(focused[0].textContent).toContain('2800')
  })
})
