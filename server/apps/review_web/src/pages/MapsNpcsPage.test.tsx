import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { renderApp } from '../test/renderApp'
import { installFixtureFetch } from '../test/fakeApi'

const LONG = { timeout: 4000 }

describe('map / npc page', () => {
  it('lists each map dataset with its own source entry and does not merge them', async () => {
    installFixtureFetch()
    renderApp('/maps')

    await screen.findByTestId('dataset-meta', {}, LONG)
    const datasetSection = screen
      .getByRole('heading', { name: '地图 / 场景 / 别名数据集' })
      .closest('.panel') as HTMLElement
    const npcSection = screen
      .getByRole('heading', { name: 'NPC 位置记录（按来源分开）' })
      .closest('.panel') as HTMLElement

    expect(within(datasetSection).getAllByRole('tab').map((tab) => tab.textContent)).toEqual([
      'mapdata_scene_dictionary',
      'mapdata_parent_scene',
      'sceneid2name_minimap_scenes',
      'npcname2realnamedata_alias_to_realname',
    ])
    expect(within(npcSection).getAllByRole('tab').map((tab) => tab.textContent)).toEqual([
      '条目 2601 · npcposdata_records',
      '条目 2804 · minimapnpcpos_pos_records',
    ])
    expect(datasetSection).not.toBe(npcSection)

    const meta = await screen.findByTestId('dataset-meta', {}, LONG)
    expect(meta.textContent).toContain('条目 1301')
    expect(meta.textContent).toContain('DATA')
    expect(meta.textContent).toContain('FIXTURE')
  })

  it('keeps NPC sources separate and states the composite record identity', async () => {
    installFixtureFetch()
    renderApp('/maps')

    const table = await screen.findByTestId('npc-table', {}, LONG)
    expect(table.textContent).toBeTruthy()

    const info = screen.getByTestId('npc-source-info')
    expect(info.textContent).toContain('2601')
    expect(info.textContent).toContain('scene_id + record_index')
    expect(info.textContent).toContain('npcid = 0 的记录 632（全部保留）')

    const user = userEvent.setup()
    await user.click(screen.getByRole('tab', { name: /2804/ }))

    const info2804 = await screen.findByTestId('npc-source-info', {}, LONG)
    expect(info2804.textContent).toContain('scene_id + scene_display_name + record_index')
    expect(info2804.textContent).toContain('631')
  })

  it('renders zero NPC ids instead of hiding them', async () => {
    installFixtureFetch()
    renderApp('/maps')

    const table = await screen.findByTestId('npc-table', {}, LONG)
    const zeroBadges = within(table).getAllByText('ID 0')
    expect(zeroBadges.length).toBeGreaterThan(0)
    const rows = within(table).getAllByTestId('npc-identity')
    expect(rows.length).toBeGreaterThan(0)
  })

  it('does not collapse same scene + same npcid records', async () => {
    installFixtureFetch()
    renderApp('/maps')

    const table = await screen.findByTestId('npc-table', {}, LONG)
    const identities = within(table)
      .getAllByTestId('npc-identity')
      .map((node) => node.textContent)
    // scene 1005 contains two npcid=0 records with distinct record_index values.
    const scene1005 = identities.filter((text) => text?.startsWith('1005'))
    expect(scene1005.length).toBeGreaterThanOrEqual(2)
    expect(new Set(scene1005).size).toBe(scene1005.length)
    expect(within(table).getAllByText(/重复 ×\d/).length).toBeGreaterThan(0)
  })

  it('filters NPC rows by scene id through the API', async () => {
    const { calls } = installFixtureFetch()
    const user = userEvent.setup()
    renderApp('/maps')

    await screen.findByTestId('npc-table', {}, LONG)
    await user.type(screen.getByPlaceholderText('如 1005'), '1005')

    await waitFor(() =>
      expect(calls.some((url) => url.includes('/npcs?') && url.includes('scene_id=1005'))).toBe(true),
    )
  })

  it('shows the agreement table with per-category counts', async () => {
    installFixtureFetch()
    renderApp('/maps')

    const counts = await screen.findByTestId('agreement-counts', {}, LONG)
    expect(counts.textContent).toContain('identical_sequence')
    expect(counts.textContent).toContain('647')
    expect(counts.textContent).toContain('content_difference')
    expect(counts.textContent).toContain('only_in_npcposdata_2601')

    const table = await screen.findByTestId('agreement-table', {}, LONG)
    expect(within(table).getByText('identical_multiset_different_order')).toBeInTheDocument()
  })
})
