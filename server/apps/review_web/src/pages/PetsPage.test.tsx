import { screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { renderApp } from '../test/renderApp'
import { installFixtureFetch, installNetworkFailure } from '../test/fakeApi'

const LONG = { timeout: 4000 }

describe('pets page', () => {
  it('marks missing aptitudes in the list and explains them in detail without showing 0', async () => {
    installFixtureFetch()
    renderApp('/pets')

    const table = await screen.findByTestId('pets-table', {}, LONG)
    const row = within(table).getByText('未定').closest('tr') as HTMLElement
    expect(within(row).getByText('资质缺失')).toBeInTheDocument()

    renderApp('/pets/3010')
    const missing = await screen.findByTestId('aptitude-missing', {}, LONG)
    expect(missing.textContent).toContain('no_record_in_2954')
    expect(missing.textContent).toContain('本页不会把它显示为 0')
    expect(screen.queryByTestId('aptitude-table')).toBeNull()
  })

  it('keeps the quarantined aptitude of pet 2800 out of the normal value grid', async () => {
    installFixtureFetch()
    renderApp('/pets/2800')

    const quarantined = await screen.findByTestId('aptitude-quarantined', {}, LONG)
    expect(quarantined.textContent).toContain('隔离')
    expect(quarantined.textContent).toContain('不展示尚未批准的候选值')
    expect(quarantined.textContent).not.toContain('1700')
    expect(screen.queryByTestId('aptitude-table')).toBeNull()

    const link = within(quarantined).getByRole('link', { name: /查看隔离记录与原始字节/ })
    expect(link).toHaveAttribute('href', '/anomalies?focus=2954%3A2800')
  })

  it('shows the aptitude grid verbatim for pets that do have a record', async () => {
    installFixtureFetch()
    renderApp('/pets/2010')

    const grid = await screen.findByTestId('aptitude-table', {}, LONG)
    const cells = Array.from(grid.querySelectorAll('.aptitude-grid__cell'))
    const cellValue = (label: string) =>
      cells.find((cell) => cell.querySelector('dt')?.textContent === label)?.querySelector('dd')
        ?.textContent

    expect(cellValue('法力資質')).toBe('1610')
    expect(cellValue('法力資質最大值')).toBe('1883')
    expect(grid.textContent).toContain('防禦資質')
  })

  it('keeps every candidate ID for an ambiguous skill name and selects none by default', async () => {
    installFixtureFetch()
    renderApp('/pets/2790')

    const candidates = await screen.findByTestId('candidate-skills', {}, LONG)
    const items = within(candidates).getAllByRole('listitem')
    const hitRow = items.find((item) => item.textContent?.includes('高級命中')) as HTMLElement
    expect(hitRow).toBeDefined()

    const links = within(hitRow).getAllByRole('link')
    const hrefs = links.map((link) => link.getAttribute('href'))
    expect(hrefs).toEqual(['/skills/229', '/skills/255'])
    expect(within(hitRow).getByText(/同名多 ID（2 个候选）/)).toBeInTheDocument()
    expect(within(hitRow).getByText(/未默认选择第一个/)).toBeInTheDocument()
    expect(within(hitRow).queryByText(/首选|推荐|primary/i)).toBeNull()
  })

  it('preserves source sequence order and duplicates in candidate skills', async () => {
    installFixtureFetch()
    renderApp('/pets/2010')

    const candidates = await screen.findByTestId('candidate-skills', {}, LONG)
    const items = within(candidates).getAllByRole('listitem')
    expect(items).toHaveLength(4)
    expect(items[0].textContent).toContain('sequence 0')
    expect(items[0].textContent).toContain('連擊')
    expect(items[3].textContent).toContain('sequence 3')
    expect(items[3].textContent).toContain('幸運')
  })

  it('keeps the 329/355 pair for 終級命中', async () => {
    installFixtureFetch()
    renderApp('/pets/4011')

    const candidates = await screen.findByTestId('candidate-skills', {}, LONG)
    const items = within(candidates).getAllByRole('listitem')
    const hitRow = items.find((item) => item.textContent?.includes('終級命中')) as HTMLElement
    expect(within(hitRow).getAllByRole('link').map((link) => link.getAttribute('href'))).toEqual([
      '/skills/329',
      '/skills/355',
    ])
  })

  it('lists required skills with their candidate ids', async () => {
    installFixtureFetch()
    renderApp('/pets/2030')

    const required = await screen.findByTestId('required-skills', {}, LONG)
    expect(required.textContent).toContain('飛行')
    expect(within(required).getAllByRole('link').map((link) => link.getAttribute('href'))).toEqual(['/skills/123'])
  })

  it('does not invent a required skill when the source record has no field', async () => {
    installFixtureFetch()
    renderApp('/pets/2010')

    await screen.findByTestId('pet-detail', {}, LONG)
    expect(await screen.findByText(/不补一个空技能，也不补 ID 0/)).toBeInTheDocument()
  })

  it('reports an API failure rather than showing fixture pets', async () => {
    installNetworkFailure()
    renderApp('/pets')

    const error = await screen.findByTestId('error-state', {}, LONG)
    expect(error.textContent).toContain('无法连接复核 API')
    expect(screen.queryByTestId('pets-table')).toBeNull()
  })
})
