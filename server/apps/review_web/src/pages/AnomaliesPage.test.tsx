import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { loadFixture } from '../../fixtures/contractHandler.mjs'
import { renderApp } from '../test/renderApp'
import { installFixtureFetch, jsonResponse } from '../test/fakeApi'

const LONG = { timeout: 4000 }

describe('anomalies page', () => {
  it('lists the four quarantine records with their source entries', async () => {
    installFixtureFetch()
    renderApp('/anomalies')

    const cards = await screen.findAllByTestId('quarantine-card', {}, LONG)
    expect(cards).toHaveLength(4)
    expect(cards.map((card) => card.getAttribute('data-anomaly-id'))).toEqual([
      '1945:72548',
      '2954:2800',
      '3205:719',
      '3205:4406',
    ])
    for (const card of cards) {
      expect(card.textContent).toContain('已隔离')
      expect(card.textContent).toContain('native_verified = false')
    }
  })

  it('renders the invalid CP950 name bytes of 72548 as hex, not as a fake name', async () => {
    installFixtureFetch()
    renderApp('/anomalies')

    await screen.findAllByTestId('quarantine-card', {}, LONG)
    const container = document.querySelector('[data-anomaly-id="1945:72548"]') as HTMLElement
    expect(container).not.toBeNull()
    const body = container.textContent ?? ''

    expect(body).toContain('invalid_cp950_source_name_bytes_preserved')
    expect(body).toContain('c2 f9 a4 48 a7 a4 c3 4d c5 e9 c5 e7 84')
    expect(body).toContain('十六进制，未解码')
    // No replacement characters, no invented name, no lossy truncation.
    expect(body).not.toContain('\uFFFD')
    expect(body).not.toContain('時空石')
    expect(within(container).getAllByTestId('byte-hex').length).toBeGreaterThan(0)
  })

  it('never decodes byte-encoded structure keys that are not printable ASCII', async () => {
    installFixtureFetch()
    renderApp('/anomalies')

    await screen.findAllByTestId('quarantine-card', {}, LONG)
    const container = document.querySelector('[data-anomaly-id="1945:72548"]') as HTMLElement
    expect(container).not.toBeNull()
    // The 2954/3205 records carry ASCII keys (name/desc), but no byte run of the
    // 72548 record may be turned into a decoded string.
    const hints = container.querySelectorAll('.byte-hex__hint')
    for (const hint of Array.from(hints)) {
      expect(hint.textContent).toMatch(/^[\x20-\x7e]+$/)
    }
  })

  it('shows quarantine evidence values with byte hex for the aptitude conflict', async () => {
    installFixtureFetch()
    renderApp('/anomalies?focus=2954%3A2800')

    await screen.findAllByTestId('quarantine-card', {}, LONG)
    const container = document.querySelector('[data-anomaly-id="2954:2800"]') as HTMLElement
    expect(container).not.toBeNull()
    const body = container.textContent ?? ''

    expect(body).toContain('aptitude_value_exceeds_named_maximum_unresolved')
    expect(body).toContain('法力資質')
    expect(body).toContain('2130')
    expect(body).toContain('1989')
    expect(container.className).toContain('is-focused')
  })

  it('lists the three pets whose aptitude rows are missing, without zero filling', async () => {
    installFixtureFetch()
    renderApp('/anomalies')

    const table = await screen.findByTestId('missing-aptitude-table', {}, LONG)
    const reasons = within(table).getAllByTestId('missing-reason')
    expect(reasons.map((node) => node.textContent)).toEqual([
      'no_record_in_2954',
      'no_record_in_2954',
      'no_record_in_2954',
    ])
    expect(table.textContent).toContain('未定')
    expect(table.textContent).toContain('年獸')
    expect(table.textContent).toContain('爆竹')
  })

  it('lists the ambiguous skill names with every candidate id', async () => {
    installFixtureFetch()
    renderApp('/anomalies')

    const list = await screen.findByTestId('ambiguous-list', {}, LONG)
    const items = within(list).getAllByRole('listitem')
    expect(items).toHaveLength(2)

    const byName = (name: string) =>
      items.find((item) => item.textContent?.startsWith(name)) as HTMLElement

    expect(within(byName('高級命中')).getAllByRole('link').map((link) => link.textContent)).toEqual([
      'ID 229',
      'ID 255',
    ])
    expect(within(byName('終級命中')).getAllByRole('link').map((link) => link.textContent)).toEqual([
      'ID 329',
      'ID 355',
    ])
  })

  it('lists all nine overwrite writes including the unchanged ones', async () => {
    installFixtureFetch()
    renderApp('/anomalies')

    const table = await screen.findByTestId('overwrite-table', {}, LONG)
    expect(within(table).getAllByTestId('overwrite-skill-link')).toHaveLength(9)
    expect(table.textContent).toContain('天魔返生術')
    expect(table.textContent).toContain('地魔返生術')
    expect(within(table).getAllByText('true（值相同，仍是写入）')).toHaveLength(8)
    expect(within(table).getAllByText('false（值已改变）')).toHaveLength(1)
  })
})

describe('anomalies page invariant self-check', () => {
  it('verifies the preserved batch_001 semantics against API data', async () => {
    installFixtureFetch()
    renderApp('/anomalies')

    const panel = await screen.findByTestId('invariant-panel', {}, LONG)
    const verdicts = within(panel).getAllByTestId('invariant-verdict')
    expect(verdicts).toHaveLength(9)
    expect(verdicts.map((node) => node.textContent)).toEqual(Array(9).fill('通过'))
    expect(panel.textContent).toContain('全部 9 项不变量在本接口返回值下成立')
    expect(panel.textContent).toContain('接口实际值：229 / 255')
    expect(panel.textContent).toContain('接口实际值：329 / 355')
  })

  it('flags a backend that stops quarantining item 72548', async () => {
    installFixtureFetch({
      override: (url) => {
        if (url !== '/api/v1/review/anomalies') return null
        const payload = JSON.parse(JSON.stringify(loadFixture().anomalies))
        payload.quarantine = payload.quarantine.filter(
          (record: { record_key: number }) => record.record_key !== 72548,
        )
        return jsonResponse(200, payload)
      },
    })
    renderApp('/anomalies')

    const panel = await screen.findByTestId('invariant-panel', {}, LONG)
    expect(panel.textContent).toContain('未通过')
    expect(panel.textContent).toContain('隔离清单中没有 1945 / 72548')
    expect(panel.textContent).toContain('有 1 项不变量未通过')
  })
})
