/**
 * Map / NPC page against Agent H's real captured responses.
 *
 * Pins the two things the reviewer asked about explicitly: every dataset is
 * queried on its own endpoint (no merged "one map table"), and the two NPC
 * sources are never folded into one - including their separate zero-npcid
 * counts and their duplicate (scene_id, npcid) rows.
 */
import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { installCaptureFetch } from '../test/hApiReplay'
import { renderApp } from '../test/renderApp'

const LONG = { timeout: 4000 }

type NpcSourceTestId = 'npc-source-npcposdata_records' | 'npc-source-minimapnpcpos_pos_records'

function npcSection(testId: NpcSourceTestId): HTMLElement {
  return screen.getByTestId(testId)
}

function npcSourceInfo(testId: NpcSourceTestId): HTMLElement {
  return within(npcSection(testId)).getByTestId('npc-source-info')
}

describe('map and NPC page', () => {
  it('queries each map dataset separately and pages it', async () => {
    const { calls } = installCaptureFetch()
    renderApp('/maps')

    const table = await screen.findByTestId('map-dataset-table', {}, LONG)
    expect(screen.getByTestId('dataset-meta').textContent).toContain('全表行数 104')
    expect(within(table).getByText('永澤城')).toBeInTheDocument()
    expect(within(screen.getAllByTestId('pagination')[0]).getByText(/共 104 条/)).toBeInTheDocument()

    expect(calls.some((url) => url.includes('/datasets/mapdata_scene_dictionary/records?offset=0&limit=25'))).toBe(true)
    // All five map datasets were looked up separately, none merged.
    for (const dataset of [
      'mapdata_scene_dictionary',
      'mapdata_parent_scene',
      'sceneid2name_minimap_scenes',
      'npcname2realnamedata_alias_to_realname',
      'minimapnpcpos_wenzi_entries',
    ]) {
      expect(calls).toContain(`/api/v1/review/datasets/${dataset}`)
    }
  })

  it('switches datasets through their own endpoint without merging rows', async () => {
    const { calls } = installCaptureFetch()
    const user = userEvent.setup()
    renderApp('/maps')

    await screen.findByTestId('map-dataset-table', {}, LONG)
    await user.click(screen.getByRole('tab', { name: 'mapdata_parent_scene' }))

    await waitFor(() => {
      expect(calls.some((url) => url.includes('/datasets/mapdata_parent_scene/records?offset=0&limit=25'))).toBe(true)
    }, LONG)
    await waitFor(() => {
      expect(screen.getByTestId('dataset-meta').textContent).toContain('全表行数 6')
    }, LONG)
  })

  it('keeps both NPC sources separate, with their own totals and zero-id counts', async () => {
    installCaptureFetch()
    renderApp('/maps')

    await screen.findAllByTestId('npc-source-info', {}, LONG)
    await waitFor(() => {
      expect(npcSourceInfo('npc-source-npcposdata_records').textContent).toContain('本来源记录数 1335')
      expect(npcSourceInfo('npc-source-minimapnpcpos_pos_records').textContent).toContain('本来源记录数 1344')
    }, LONG)

    const pos2601 = npcSection('npc-source-npcposdata_records')
    const pos2804 = npcSection('npc-source-minimapnpcpos_pos_records')

    expect(npcSourceInfo('npc-source-npcposdata_records').textContent).toContain('npcid = 0 的记录 632')
    expect(npcSourceInfo('npc-source-minimapnpcpos_pos_records').textContent).toContain('npcid = 0 的记录 631')

    // The two sections render their own dataset's rows: 2601 starts with npcid
    // 1083, 2804 starts with 4992. A merged table could not look like this, and
    // 2804 is the only source whose records carry a scene display name.
    const firstIdentity = (section: HTMLElement) =>
      within(section).getAllByTestId('npc-identity')[0].textContent ?? ''
    expect(firstIdentity(pos2601)).toContain('1001 / #0')
    expect(firstIdentity(pos2804)).toContain('永澤城')

    // The zero id is shown as 0 on both sources, never hidden or renumbered.
    expect(within(pos2601).getAllByText('ID 0').length).toBe(1)
    expect(within(pos2804).getAllByText('ID 0').length).toBe(1)
  })

  it('shows duplicate keys of one scene instead of folding them', async () => {
    const { calls } = installCaptureFetch()
    const user = userEvent.setup()
    renderApp('/maps')

    await screen.findAllByTestId('npc-source-info', {}, LONG)
    const sceneInputs = screen.getAllByPlaceholderText('如 1005')
    await user.type(sceneInputs[0], '1005')

    await waitFor(() => {
      expect(calls.some((url) => url.includes('/datasets/npcposdata_records/records') && url.includes('scene_id=1005'))).toBe(
        true,
      )
    }, LONG)

    await waitFor(() => {
      const section = npcSection('npc-source-npcposdata_records')
      const table = within(section).getByTestId('npc-table')
      expect(within(table).getAllByRole('row')).toHaveLength(3) // header + 2 real rows
      expect(within(table).getAllByText('重复 ×2')).toHaveLength(2)
      // Both zero-id rows of the scene are still listed, with their own names.
      expect(within(table).getByText('月夜先生')).toBeInTheDocument()
      expect(within(table).getByText('愛蘿俠士')).toBeInTheDocument()
    }, LONG)
  })

  it('searches each source through the backend', async () => {
    const { calls } = installCaptureFetch()
    const user = userEvent.setup()
    renderApp('/maps')

    await screen.findAllByTestId('npc-source-info', {}, LONG)
    const searchInputs = screen.getAllByLabelText('搜索 NPC')
    await user.type(searchInputs[0], '車伕')

    await waitFor(() => {
      expect(calls.some((url) => url.includes('q=%E8%BB%8A%E4%BC%95') && url.includes('npcposdata_records'))).toBe(true)
    }, LONG)
    await waitFor(() => {
      const section = npcSection('npc-source-npcposdata_records')
      expect(within(section).getByTestId('pagination').textContent).toContain('共 27 条')
    }, LONG)
  })

  it('counts agreement categories over the whole dataset and filters by scene', async () => {
    const { calls } = installCaptureFetch()
    const user = userEvent.setup()
    renderApp('/maps')

    const counts = await screen.findByTestId('agreement-counts', {}, LONG)
    expect(counts.textContent).toContain('identical_sequence')
    expect(counts.textContent).toContain('647')
    expect(counts.textContent).toContain('only_in_minimapnpcpos_2804')
    expect(counts.textContent).toContain('12')
    expect(screen.getByText(/全表 677 行/)).toBeInTheDocument()

    // The full-set read follows the pages the backend has (500 then 177 rows).
    await waitFor(() => {
      expect(
        calls.some((url) => url.includes('/api/v1/review/datasets/npc_2601_vs_2804_agreement/records?offset=0&limit=500')),
      ).toBe(true)
    }, LONG)
    await waitFor(() => {
      expect(
        calls.some((url) => url.includes('/api/v1/review/datasets/npc_2601_vs_2804_agreement/records?offset=500&limit=500')),
      ).toBe(true)
    }, LONG)

    const sceneInput = screen.getAllByPlaceholderText('留空显示全部')[0]
    await user.type(sceneInput, '1001')

    await waitFor(() => {
      const table = screen.getByTestId('agreement-table')
      expect(within(table).getAllByRole('row')).toHaveLength(12) // header + 11 scene rows
    }, LONG)
    expect(
      calls.some((url) => url.includes('/datasets/npc_2601_vs_2804_agreement/records') && url.includes('scene_id=1001')),
    ).toBe(true)
  })
})
